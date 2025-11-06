import tensorflow as tf
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import matplotlib.pyplot as plt
import seaborn as sns
from .data_loader import load_dataset
from aif360.metrics import BinaryLabelDatasetMetric, ClassificationMetric
from aif360.datasets import BinaryLabelDataset
import cv2
import os
from typing import Dict, List, Tuple, Optional


class SkinToneClassifier:
    """Classify skin tone using the Fitzpatrick scale or simplified categories"""
    
    @staticmethod
    def classify_skin_tone_simple(image_path: str) -> str:
        """
        Simple skin tone classification based on average skin color
        Returns: 'light', 'medium', 'dark'
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                return 'unknown'
            
            # Convert to HSV for better skin detection
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Define skin color range in HSV
            lower_skin = np.array([0, 20, 70], dtype=np.uint8)
            upper_skin = np.array([20, 255, 255], dtype=np.uint8)
            
            # Create mask for skin pixels
            skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
            
            # Get skin pixels
            skin_pixels = image[skin_mask > 0]
            
            if len(skin_pixels) == 0:
                return 'unknown'
            
            # Calculate average brightness of skin pixels
            avg_brightness = np.mean(cv2.cvtColor(skin_pixels.reshape(-1, 1, 3), cv2.COLOR_BGR2GRAY))
            
            # Classify based on brightness thresholds
            if avg_brightness > 180:
                return 'light'
            elif avg_brightness > 120:
                return 'medium'
            else:
                return 'dark'
                
        except Exception as e:
            print(f"Error classifying skin tone for {image_path}: {e}")
            return 'unknown'


class FairnessEvaluator:
    """Comprehensive fairness evaluation for skin lesion detection"""
    
    def __init__(self, model_path: str):
        """
        Initialize fairness evaluator
        
        Args:
            model_path: Path to trained model
        """
        self.model = tf.keras.models.load_model(model_path)
        self.skin_classifier = SkinToneClassifier()
        
    def evaluate_model_fairness(self, 
                              test_data_path: str,
                              image_metadata: Optional[pd.DataFrame] = None) -> Dict:
        """
        Comprehensive fairness evaluation
        
        Args:
            test_data_path: Path to test dataset
            image_metadata: Optional metadata with demographic information
            
        Returns:
            Dictionary containing fairness metrics
        """
        # Load test data
        _, X_test, _, y_test, class_map = load_dataset(test_data_path)
        
        # Get predictions
        y_pred = self.model.predict(X_test)
        y_pred_classes = np.argmax(y_pred, axis=1)
        y_true_classes = np.argmax(y_test, axis=1)
        
        # If no metadata provided, classify skin tones from images
        if image_metadata is None:
            skin_tones = self._classify_skin_tones_from_dataset(test_data_path)
        else:
            skin_tones = image_metadata['skin_tone'].values
        
        # Overall performance metrics
        overall_metrics = self._calculate_overall_metrics(y_true_classes, y_pred_classes)
        
        # Group-wise performance
        group_metrics = self._calculate_group_metrics(
            y_true_classes, y_pred_classes, skin_tones
        )
        
        # Fairness metrics
        fairness_metrics = self._calculate_fairness_metrics(
            y_true_classes, y_pred_classes, skin_tones
        )
        
        # Bias analysis
        bias_analysis = self._analyze_bias_patterns(
            y_true_classes, y_pred_classes, skin_tones, y_pred
        )
        
        return {
            'overall_metrics': overall_metrics,
            'group_metrics': group_metrics,
            'fairness_metrics': fairness_metrics,
            'bias_analysis': bias_analysis
        }
    
    def _classify_skin_tones_from_dataset(self, dataset_path: str) -> List[str]:
        """Classify skin tones for all images in dataset"""
        skin_tones = []
        
        for class_name in os.listdir(dataset_path):
            class_dir = os.path.join(dataset_path, class_name)
            if not os.path.isdir(class_dir):
                continue
                
            for img_file in os.listdir(class_dir):
                img_path = os.path.join(class_dir, img_file)
                skin_tone = self.skin_classifier.classify_skin_tone_simple(img_path)
                skin_tones.append(skin_tone)
        
        return skin_tones
    
    def _calculate_overall_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
        """Calculate overall performance metrics"""
        return {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, average='weighted'),
            'recall': recall_score(y_true, y_pred, average='weighted'),
            'f1_score': f1_score(y_true, y_pred, average='weighted'),
            'confusion_matrix': confusion_matrix(y_true, y_pred).tolist()
        }
    
    def _calculate_group_metrics(self, 
                               y_true: np.ndarray, 
                               y_pred: np.ndarray, 
                               groups: List[str]) -> Dict:
        """Calculate performance metrics for each group"""
        group_metrics = {}
        unique_groups = list(set(groups))
        
        for group in unique_groups:
            if group == 'unknown':
                continue
                
            group_mask = np.array(groups) == group
            
            if np.sum(group_mask) == 0:
                continue
                
            group_y_true = y_true[group_mask]
            group_y_pred = y_pred[group_mask]
            
            group_metrics[group] = {
                'sample_size': int(np.sum(group_mask)),
                'accuracy': accuracy_score(group_y_true, group_y_pred),
                'precision': precision_score(group_y_true, group_y_pred, average='weighted', zero_division=0),
                'recall': recall_score(group_y_true, group_y_pred, average='weighted', zero_division=0),
                'f1_score': f1_score(group_y_true, group_y_pred, average='weighted', zero_division=0)
            }
        
        return group_metrics
    
    def _calculate_fairness_metrics(self, 
                                  y_true: np.ndarray, 
                                  y_pred: np.ndarray, 
                                  groups: List[str]) -> Dict:
        """Calculate fairness-specific metrics"""
        fairness_metrics = {}
        unique_groups = [g for g in set(groups) if g != 'unknown']
        
        if len(unique_groups) < 2:
            return {'error': 'Need at least 2 groups for fairness evaluation'}
        
        # Calculate demographic parity difference
        group_positive_rates = {}
        for group in unique_groups:
            group_mask = np.array(groups) == group
            if np.sum(group_mask) > 0:
                group_positive_rates[group] = np.mean(y_pred[group_mask])
        
        if len(group_positive_rates) >= 2:
            rates = list(group_positive_rates.values())
            fairness_metrics['demographic_parity_difference'] = max(rates) - min(rates)
        
        # Calculate equal opportunity difference
        group_tpr = {}  # True Positive Rate
        for group in unique_groups:
            group_mask = np.array(groups) == group
            group_y_true = y_true[group_mask]
            group_y_pred = y_pred[group_mask]
            
            if np.sum(group_mask) > 0 and np.sum(group_y_true) > 0:
                # TPR = TP / (TP + FN)
                tp = np.sum((group_y_true == 1) & (group_y_pred == 1))
                fn = np.sum((group_y_true == 1) & (group_y_pred == 0))
                tpr = tp / (tp + fn) if (tp + fn) > 0 else 0
                group_tpr[group] = tpr
        
        if len(group_tpr) >= 2:
            tpr_values = list(group_tpr.values())
            fairness_metrics['equal_opportunity_difference'] = max(tpr_values) - min(tpr_values)
        
        # Calculate equalized odds difference  
        group_fpr = {}  # False Positive Rate
        for group in unique_groups:
            group_mask = np.array(groups) == group
            group_y_true = y_true[group_mask]
            group_y_pred = y_pred[group_mask]
            
            if np.sum(group_mask) > 0 and np.sum(group_y_true == 0) > 0:
                # FPR = FP / (FP + TN)
                fp = np.sum((group_y_true == 0) & (group_y_pred == 1))
                tn = np.sum((group_y_true == 0) & (group_y_pred == 0))
                fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
                group_fpr[group] = fpr
        
        if len(group_tpr) >= 2 and len(group_fpr) >= 2:
            tpr_diff = max(group_tpr.values()) - min(group_tpr.values())
            fpr_diff = max(group_fpr.values()) - min(group_fpr.values())
            fairness_metrics['equalized_odds_difference'] = max(tpr_diff, fpr_diff)
        
        return fairness_metrics
    
    def _analyze_bias_patterns(self, 
                              y_true: np.ndarray, 
                              y_pred: np.ndarray, 
                              groups: List[str],
                              y_pred_proba: np.ndarray) -> Dict:
        """Analyze bias patterns in predictions"""
        bias_analysis = {}
        unique_groups = [g for g in set(groups) if g != 'unknown']
        
        # Confidence distribution by group
        confidence_by_group = {}
        for group in unique_groups:
            group_mask = np.array(groups) == group
            if np.sum(group_mask) > 0:
                group_confidences = np.max(y_pred_proba[group_mask], axis=1)
                confidence_by_group[group] = {
                    'mean_confidence': float(np.mean(group_confidences)),
                    'std_confidence': float(np.std(group_confidences)),
                    'min_confidence': float(np.min(group_confidences)),
                    'max_confidence': float(np.max(group_confidences))
                }
        
        bias_analysis['confidence_by_group'] = confidence_by_group
        
        # Error rate by group
        error_rates = {}
        for group in unique_groups:
            group_mask = np.array(groups) == group
            if np.sum(group_mask) > 0:
                group_y_true = y_true[group_mask]
                group_y_pred = y_pred[group_mask]
                error_rate = np.mean(group_y_true != group_y_pred)
                error_rates[group] = float(error_rate)
        
        bias_analysis['error_rates_by_group'] = error_rates
        
        return bias_analysis
    
    def generate_fairness_report(self, evaluation_results: Dict, output_path: str = None):
        """Generate comprehensive fairness report"""
        report = []
        report.append("=" * 80)
        report.append("FAIRNESS EVALUATION REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Overall metrics
        report.append("OVERALL MODEL PERFORMANCE:")
        report.append("-" * 40)
        overall = evaluation_results['overall_metrics']
        report.append(f"Accuracy: {overall['accuracy']:.4f}")
        report.append(f"Precision: {overall['precision']:.4f}")
        report.append(f"Recall: {overall['recall']:.4f}")
        report.append(f"F1 Score: {overall['f1_score']:.4f}")
        report.append("")
        
        # Group metrics
        report.append("GROUP-WISE PERFORMANCE:")
        report.append("-" * 40)
        for group, metrics in evaluation_results['group_metrics'].items():
            report.append(f"\n{group.upper()} SKIN TONE:")
            report.append(f"  Sample Size: {metrics['sample_size']}")
            report.append(f"  Accuracy: {metrics['accuracy']:.4f}")
            report.append(f"  Precision: {metrics['precision']:.4f}")
            report.append(f"  Recall: {metrics['recall']:.4f}")
            report.append(f"  F1 Score: {metrics['f1_score']:.4f}")
        report.append("")
        
        # Fairness metrics
        report.append("FAIRNESS METRICS:")
        report.append("-" * 40)
        fairness = evaluation_results['fairness_metrics']
        
        if 'demographic_parity_difference' in fairness:
            dpd = fairness['demographic_parity_difference']
            report.append(f"Demographic Parity Difference: {dpd:.4f}")
            report.append(f"  Interpretation: {'FAIR' if dpd < 0.1 else 'UNFAIR'} (threshold: 0.1)")
        
        if 'equal_opportunity_difference' in fairness:
            eod = fairness['equal_opportunity_difference']
            report.append(f"Equal Opportunity Difference: {eod:.4f}")
            report.append(f"  Interpretation: {'FAIR' if eod < 0.1 else 'UNFAIR'} (threshold: 0.1)")
        
        if 'equalized_odds_difference' in fairness:
            eqod = fairness['equalized_odds_difference']
            report.append(f"Equalized Odds Difference: {eqod:.4f}")
            report.append(f"  Interpretation: {'FAIR' if eqod < 0.1 else 'UNFAIR'} (threshold: 0.1)")
        
        report.append("")
        
        # Bias analysis
        report.append("BIAS ANALYSIS:")
        report.append("-" * 40)
        bias = evaluation_results['bias_analysis']
        
        if 'error_rates_by_group' in bias:
            report.append("Error Rates by Group:")
            for group, error_rate in bias['error_rates_by_group'].items():
                report.append(f"  {group}: {error_rate:.4f}")
        
        if 'confidence_by_group' in bias:
            report.append("\nConfidence Statistics by Group:")
            for group, stats in bias['confidence_by_group'].items():
                report.append(f"  {group}:")
                report.append(f"    Mean Confidence: {stats['mean_confidence']:.4f}")
                report.append(f"    Std Confidence: {stats['std_confidence']:.4f}")
        
        report_text = "\n".join(report)
        
        if output_path:
            with open(output_path, 'w') as f:
                f.write(report_text)
        
        return report_text


if __name__ == "__main__":
    # Example usage
    model_path = "ai_model/saved_models/skin_lesion_cnn.h5"
    
    if os.path.exists(model_path):
        evaluator = FairnessEvaluator(model_path)
        
        dataset_path = "dataset/processed"
        results = evaluator.evaluate_model_fairness(dataset_path)
        
        # Generate report
        report = evaluator.generate_fairness_report(results)
        print(report)
        
        # Save report
        evaluator.generate_fairness_report(results, "fairness_report.txt")
        print("\nFairness report saved to fairness_report.txt")
    else:
        print(f"Model not found at {model_path}. Please train a model first.")
