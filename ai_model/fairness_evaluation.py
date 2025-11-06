"""
Fairness Evaluation System for Skin Lesion Detection
Analyzes bias across different demographic groups and skin tones
"""

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from aif360.datasets import BinaryLabelDataset
from aif360.metrics import BinaryLabelDatasetMetric, ClassificationMetric
import cv2
from typing import Dict, List, Tuple, Optional
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

class SkinToneDetector:
    """Detect skin tone from medical images using computer vision"""
    
    def __init__(self):
        self.skin_tone_ranges = {
            'very_light': [(0, 50, 50), (25, 255, 255)],    # Very light skin (Type I-II)
            'light': [(15, 30, 80), (35, 255, 255)],        # Light skin (Type III)
            'medium': [(10, 40, 60), (25, 200, 200)],       # Medium skin (Type IV)
            'dark': [(5, 30, 30), (20, 255, 150)],          # Dark skin (Type V)
            'very_dark': [(0, 10, 10), (15, 200, 100)]      # Very dark skin (Type VI)
        }
    
    def detect_skin_tone(self, image_path: str) -> str:
        """
        Detect predominant skin tone in the image
        Returns: skin tone category as string
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                return 'unknown'
            
            # Convert to HSV for better skin detection
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Create masks for different skin tones
            tone_pixels = {}
            
            for tone, (lower, upper) in self.skin_tone_ranges.items():
                lower = np.array(lower)
                upper = np.array(upper)
                mask = cv2.inRange(hsv, lower, upper)
                tone_pixels[tone] = np.sum(mask > 0)
            
            # Return the tone with most pixels
            if sum(tone_pixels.values()) == 0:
                return 'unknown'
            
            return max(tone_pixels, key=tone_pixels.get)
            
        except Exception as e:
            print(f"Error detecting skin tone: {e}")
            return 'unknown'
    
    def analyze_brightness(self, image_path: str) -> float:
        """
        Analyze overall brightness of the image
        Returns: brightness score (0-1)
        """
        try:
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if image is None:
                return 0.5
            
            return np.mean(image) / 255.0
            
        except Exception:
            return 0.5

class FairnessEvaluator:
    """Comprehensive fairness evaluation for skin lesion detection"""
    
    def __init__(self, model_predictions_file: Optional[str] = None):
        self.skin_detector = SkinToneDetector()
        self.results_dir = "fairness_evaluation_results"
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Protected attributes for fairness analysis
        self.protected_attributes = [
            'skin_tone', 'age_group', 'gender', 'image_quality'
        ]
        
        # Fairness metrics to compute
        self.fairness_metrics = [
            'demographic_parity',
            'equalized_odds',
            'statistical_parity',
            'disparate_impact'
        ]
    
    def create_synthetic_demographics(self, n_samples: int = 1000) -> pd.DataFrame:
        """
        Create synthetic demographic data for testing
        """
        np.random.seed(42)
        
        # Generate synthetic data
        data = {
            'patient_id': range(n_samples),
            'skin_tone': np.random.choice(
                ['very_light', 'light', 'medium', 'dark', 'very_dark'], 
                n_samples, 
                p=[0.3, 0.25, 0.2, 0.15, 0.1]  # Realistic distribution
            ),
            'age_group': np.random.choice(
                ['young', 'middle_aged', 'elderly'], 
                n_samples, 
                p=[0.3, 0.4, 0.3]
            ),
            'gender': np.random.choice(['male', 'female'], n_samples, p=[0.48, 0.52]),
            'image_quality': np.random.choice(
                ['high', 'medium', 'low'], 
                n_samples, 
                p=[0.4, 0.5, 0.1]
            ),
            'true_label': np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),  # 30% malignant
        }
        
        # Add bias: darker skin tones have higher false positive rates
        predicted_labels = []
        for i in range(n_samples):
            true_label = data['true_label'][i]
            skin_tone = data['skin_tone'][i]
            
            # Base accuracy varies by skin tone (simulating bias)
            if skin_tone in ['very_light', 'light']:
                accuracy = 0.92
            elif skin_tone == 'medium':
                accuracy = 0.88
            elif skin_tone == 'dark':
                accuracy = 0.82
            else:  # very_dark
                accuracy = 0.76
            
            # Simulate prediction with bias
            if np.random.random() < accuracy:
                predicted_labels.append(true_label)
            else:
                # Add bias: more false positives for darker skin
                if skin_tone in ['dark', 'very_dark'] and true_label == 0:
                    predicted_labels.append(1)  # False positive
                else:
                    predicted_labels.append(1 - true_label)
        
        data['predicted_label'] = predicted_labels
        data['confidence'] = np.random.uniform(0.6, 0.99, n_samples)
        
        return pd.DataFrame(data)
    
    def compute_group_metrics(self, df: pd.DataFrame, group_col: str) -> Dict:
        """
        Compute performance metrics for each group
        """
        results = {}
        
        for group in df[group_col].unique():
            group_data = df[df[group_col] == group]
            
            if len(group_data) == 0:
                continue
            
            y_true = group_data['true_label']
            y_pred = group_data['predicted_label']
            
            results[group] = {
                'sample_size': len(group_data),
                'accuracy': accuracy_score(y_true, y_pred),
                'precision': precision_score(y_true, y_pred, zero_division=0),
                'recall': recall_score(y_true, y_pred, zero_division=0),
                'f1_score': f1_score(y_true, y_pred, zero_division=0),
                'positive_rate': np.mean(y_pred),
                'true_positive_rate': recall_score(y_true, y_pred, zero_division=0),
                'false_positive_rate': np.mean(y_pred[y_true == 0]) if np.sum(y_true == 0) > 0 else 0
            }
        
        return results
    
    def compute_fairness_metrics(self, df: pd.DataFrame, protected_attr: str) -> Dict:
        """
        Compute fairness metrics using AIF360
        """
        try:
            # Prepare data for AIF360
            favorable_label = 1
            unfavorable_label = 0
            
            # Create privileged and unprivileged groups
            # For skin tone: light tones are privileged
            if protected_attr == 'skin_tone':
                privileged_groups = [{'skin_tone': 'very_light'}, {'skin_tone': 'light'}]
                unprivileged_groups = [{'skin_tone': 'dark'}, {'skin_tone': 'very_dark'}]
            elif protected_attr == 'age_group':
                privileged_groups = [{'age_group': 'middle_aged'}]
                unprivileged_groups = [{'age_group': 'elderly'}]
            elif protected_attr == 'gender':
                privileged_groups = [{'gender': 'male'}]
                unprivileged_groups = [{'gender': 'female'}]
            else:
                return {}
            
            # Create AIF360 datasets
            dataset = BinaryLabelDataset(
                df=df,
                label_names=['true_label'],
                protected_attribute_names=[protected_attr],
                favorable_label=favorable_label,
                unfavorable_label=unfavorable_label
            )
            
            # Compute dataset metrics
            dataset_metric = BinaryLabelDatasetMetric(
                dataset, 
                unprivileged_groups=unprivileged_groups,
                privileged_groups=privileged_groups
            )
            
            # Create prediction dataset
            pred_dataset = dataset.copy()
            pred_dataset.labels = df['predicted_label'].values.reshape(-1, 1)
            
            # Compute classification metrics
            classified_metric = ClassificationMetric(
                dataset, pred_dataset,
                unprivileged_groups=unprivileged_groups,
                privileged_groups=privileged_groups
            )
            
            fairness_results = {
                'statistical_parity_difference': dataset_metric.statistical_parity_difference(),
                'disparate_impact': classified_metric.disparate_impact(),
                'equalized_odds_difference': classified_metric.equalized_odds_difference(),
                'demographic_parity_difference': classified_metric.statistical_parity_difference(),
                'average_odds_difference': classified_metric.average_odds_difference()
            }
            
            return fairness_results
            
        except Exception as e:
            print(f"Error computing fairness metrics for {protected_attr}: {e}")
            return {}
    
    def generate_bias_report(self, df: pd.DataFrame) -> Dict:
        """
        Generate comprehensive bias analysis report
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'dataset_size': len(df),
            'overall_metrics': {
                'accuracy': accuracy_score(df['true_label'], df['predicted_label']),
                'precision': precision_score(df['true_label'], df['predicted_label']),
                'recall': recall_score(df['true_label'], df['predicted_label']),
                'f1_score': f1_score(df['true_label'], df['predicted_label'])
            },
            'group_analysis': {},
            'fairness_metrics': {},
            'bias_indicators': []
        }
        
        # Analyze each protected attribute
        for attr in ['skin_tone', 'age_group', 'gender']:
            if attr in df.columns:
                # Group metrics
                group_metrics = self.compute_group_metrics(df, attr)
                report['group_analysis'][attr] = group_metrics
                
                # Fairness metrics
                fairness_metrics = self.compute_fairness_metrics(df, attr)
                report['fairness_metrics'][attr] = fairness_metrics
                
                # Check for bias indicators
                self._identify_bias_indicators(report, attr, group_metrics, fairness_metrics)
        
        return report
    
    def _identify_bias_indicators(self, report: Dict, attr: str, group_metrics: Dict, fairness_metrics: Dict):
        """
        Identify potential bias indicators
        """
        # Check for significant accuracy differences
        accuracies = [metrics['accuracy'] for metrics in group_metrics.values()]
        if max(accuracies) - min(accuracies) > 0.1:  # 10% difference threshold
            report['bias_indicators'].append({
                'type': 'accuracy_disparity',
                'attribute': attr,
                'severity': 'high' if max(accuracies) - min(accuracies) > 0.2 else 'medium',
                'details': f"Accuracy varies by {(max(accuracies) - min(accuracies)):.3f} across {attr} groups"
            })
        
        # Check disparate impact
        if 'disparate_impact' in fairness_metrics:
            di = fairness_metrics['disparate_impact']
            if di < 0.8 or di > 1.2:  # 80% rule
                report['bias_indicators'].append({
                    'type': 'disparate_impact',
                    'attribute': attr,
                    'severity': 'high' if di < 0.7 or di > 1.3 else 'medium',
                    'details': f"Disparate impact ratio: {di:.3f} (should be close to 1.0)"
                })
    
    def create_visualizations(self, df: pd.DataFrame, report: Dict):
        """
        Create bias analysis visualizations
        """
        # Set up the plotting style
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Skin Lesion AI Fairness Analysis', fontsize=16, fontweight='bold')
        
        # 1. Accuracy by skin tone
        if 'skin_tone' in report['group_analysis']:
            skin_metrics = report['group_analysis']['skin_tone']
            skin_tones = list(skin_metrics.keys())
            accuracies = [skin_metrics[tone]['accuracy'] for tone in skin_tones]
            
            axes[0, 0].bar(skin_tones, accuracies, color='skyblue', alpha=0.7)
            axes[0, 0].set_title('Model Accuracy by Skin Tone')
            axes[0, 0].set_ylabel('Accuracy')
            axes[0, 0].set_ylim(0, 1)
            axes[0, 0].tick_params(axis='x', rotation=45)
            
            # Add threshold line
            axes[0, 0].axhline(y=0.8, color='red', linestyle='--', alpha=0.7, label='Acceptable Threshold')
            axes[0, 0].legend()
        
        # 2. False Positive Rate by skin tone
        if 'skin_tone' in report['group_analysis']:
            skin_metrics = report['group_analysis']['skin_tone']
            fpr_rates = [skin_metrics[tone]['false_positive_rate'] for tone in skin_tones]
            
            axes[0, 1].bar(skin_tones, fpr_rates, color='salmon', alpha=0.7)
            axes[0, 1].set_title('False Positive Rate by Skin Tone')
            axes[0, 1].set_ylabel('False Positive Rate')
            axes[0, 1].tick_params(axis='x', rotation=45)
        
        # 3. Sample distribution
        skin_tone_counts = df['skin_tone'].value_counts()
        axes[1, 0].pie(skin_tone_counts.values, labels=skin_tone_counts.index, autopct='%1.1f%%')
        axes[1, 0].set_title('Dataset Distribution by Skin Tone')
        
        # 4. Fairness metrics heatmap
        fairness_data = []
        for attr, metrics in report['fairness_metrics'].items():
            for metric, value in metrics.items():
                fairness_data.append([attr, metric, value])
        
        if fairness_data:
            fairness_df = pd.DataFrame(fairness_data, columns=['Attribute', 'Metric', 'Value'])
            fairness_pivot = fairness_df.pivot(index='Attribute', columns='Metric', values='Value')
            
            sns.heatmap(fairness_pivot, annot=True, cmap='RdYlBu_r', center=0, 
                       ax=axes[1, 1], cbar_kws={'label': 'Bias Score'})
            axes[1, 1].set_title('Fairness Metrics Heatmap')
        
        plt.tight_layout()
        
        # Save the plot
        plot_path = os.path.join(self.results_dir, f'fairness_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return plot_path
    
    def run_fairness_evaluation(self, df: Optional[pd.DataFrame] = None) -> Tuple[Dict, str]:
        """
        Run complete fairness evaluation
        """
        print("🔍 Starting comprehensive fairness evaluation...")
        
        # Use provided data or create synthetic data
        if df is None:
            print("📊 Creating synthetic dataset for demonstration...")
            df = self.create_synthetic_demographics(1000)
        
        # Generate bias report
        print("📈 Analyzing bias patterns...")
        report = self.generate_bias_report(df)
        
        # Create visualizations
        print("📊 Creating bias visualizations...")
        plot_path = self.create_visualizations(df, report)
        
        # Save detailed report
        report_path = os.path.join(self.results_dir, f'bias_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        
        import json
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"✅ Fairness evaluation complete!")
        print(f"📄 Report saved: {report_path}")
        print(f"📊 Visualizations saved: {plot_path}")
        
        # Print summary
        self._print_summary(report)
        
        return report, report_path
    
    def _print_summary(self, report: Dict):
        """Print fairness evaluation summary"""
        print("\n" + "="*60)
        print("🎯 FAIRNESS EVALUATION SUMMARY")
        print("="*60)
        
        print(f"📊 Dataset Size: {report['dataset_size']:,} samples")
        print(f"🎯 Overall Accuracy: {report['overall_metrics']['accuracy']:.3f}")
        
        print(f"\n🚨 Bias Indicators Found: {len(report['bias_indicators'])}")
        for indicator in report['bias_indicators']:
            severity_emoji = "🔴" if indicator['severity'] == 'high' else "🟡"
            print(f"  {severity_emoji} {indicator['type']} in {indicator['attribute']}: {indicator['details']}")
        
        if len(report['bias_indicators']) == 0:
            print("  ✅ No significant bias detected!")
        
        print("\n📈 Performance by Group:")
        for attr, groups in report['group_analysis'].items():
            print(f"\n  {attr.replace('_', ' ').title()}:")
            for group, metrics in groups.items():
                print(f"    {group}: Accuracy={metrics['accuracy']:.3f}, FPR={metrics['false_positive_rate']:.3f}")

def main():
    """Run fairness evaluation demonstration"""
    evaluator = FairnessEvaluator()
    report, report_path = evaluator.run_fairness_evaluation()
    return evaluator, report

if __name__ == "__main__":
    main()