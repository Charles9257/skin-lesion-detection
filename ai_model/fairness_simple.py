"""
Simplified Fairness Evaluation System for Skin Lesion Detection
Focus on practical bias analysis without complex dependencies
"""

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import cv2
from typing import Dict, List, Tuple, Optional
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime
import json

class SimpleFairnessEvaluator:
    """Practical fairness evaluation for skin lesion detection"""
    
    def __init__(self):
        self.results_dir = "fairness_evaluation_results"
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Skin tone detection based on brightness
        self.skin_tone_thresholds = {
            'very_light': (0.7, 1.0),
            'light': (0.5, 0.7),
            'medium': (0.3, 0.5),
            'dark': (0.15, 0.3),
            'very_dark': (0.0, 0.15)
        }
    
    def detect_skin_tone_simple(self, image_path: str) -> str:
        """Simple skin tone detection based on image brightness"""
        try:
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if image is None:
                return 'unknown'
            
            brightness = np.mean(image) / 255.0
            
            for tone, (min_val, max_val) in self.skin_tone_thresholds.items():
                if min_val <= brightness < max_val:
                    return tone
            
            return 'unknown'
            
        except Exception as e:
            print(f"Error detecting skin tone: {e}")
            return 'unknown'
    
    def create_synthetic_dataset(self, n_samples: int = 1000) -> pd.DataFrame:
        """Create synthetic dataset with bias patterns"""
        np.random.seed(42)
        
        # Generate synthetic demographics
        skin_tones = ['very_light', 'light', 'medium', 'dark', 'very_dark']
        age_groups = ['young', 'middle_aged', 'elderly']
        genders = ['male', 'female']
        
        data = {
            'patient_id': range(n_samples),
            'skin_tone': np.random.choice(skin_tones, n_samples, p=[0.3, 0.25, 0.2, 0.15, 0.1]),
            'age_group': np.random.choice(age_groups, n_samples, p=[0.3, 0.4, 0.3]),
            'gender': np.random.choice(genders, n_samples, p=[0.48, 0.52]),
            'image_quality': np.random.choice(['high', 'medium', 'low'], n_samples, p=[0.4, 0.5, 0.1]),
            'true_label': np.random.choice([0, 1], n_samples, p=[0.7, 0.3])  # 30% malignant
        }
        
        # Simulate biased predictions based on skin tone
        predicted_labels = []
        confidences = []
        
        for i in range(n_samples):
            true_label = data['true_label'][i]
            skin_tone = data['skin_tone'][i]
            
            # Model performance varies by skin tone (simulating bias)
            if skin_tone in ['very_light', 'light']:
                base_accuracy = 0.92
                base_confidence = 0.88
            elif skin_tone == 'medium':
                base_accuracy = 0.87
                base_confidence = 0.83
            elif skin_tone == 'dark':
                base_accuracy = 0.81
                base_confidence = 0.78
            else:  # very_dark
                base_accuracy = 0.75
                base_confidence = 0.72
            
            # Generate prediction with bias
            if np.random.random() < base_accuracy:
                predicted_labels.append(true_label)
                confidence = base_confidence + np.random.normal(0, 0.05)
            else:
                # Bias: darker skin tends to have more false positives
                if skin_tone in ['dark', 'very_dark'] and true_label == 0:
                    predicted_labels.append(1)  # False positive
                    confidence = base_confidence - 0.1 + np.random.normal(0, 0.1)
                else:
                    predicted_labels.append(1 - true_label)
                    confidence = base_confidence - 0.15 + np.random.normal(0, 0.1)
            
            confidences.append(max(0.5, min(0.99, confidence)))
        
        data['predicted_label'] = predicted_labels
        data['confidence'] = confidences
        
        return pd.DataFrame(data)
    
    def compute_group_metrics(self, df: pd.DataFrame, group_col: str) -> Dict:
        """Compute detailed metrics for each group"""
        results = {}
        
        for group in df[group_col].unique():
            group_data = df[df[group_col] == group]
            
            if len(group_data) == 0:
                continue
            
            y_true = group_data['true_label']
            y_pred = group_data['predicted_label']
            
            # Basic metrics
            tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
            
            results[group] = {
                'sample_size': len(group_data),
                'accuracy': accuracy_score(y_true, y_pred),
                'precision': precision_score(y_true, y_pred, zero_division=0),
                'recall': recall_score(y_true, y_pred, zero_division=0),
                'f1_score': f1_score(y_true, y_pred, zero_division=0),
                'specificity': tn / (tn + fp) if (tn + fp) > 0 else 0,
                'sensitivity': tp / (tp + fn) if (tp + fn) > 0 else 0,
                'positive_rate': np.mean(y_pred),
                'false_positive_rate': fp / (fp + tn) if (fp + tn) > 0 else 0,
                'false_negative_rate': fn / (fn + tp) if (fn + tp) > 0 else 0,
                'avg_confidence': np.mean(group_data['confidence']),
                'true_positives': tp,
                'false_positives': fp,
                'true_negatives': tn,
                'false_negatives': fn
            }
        
        return results
    
    def compute_fairness_metrics(self, df: pd.DataFrame, group_col: str, privileged_groups: List[str]) -> Dict:
        """Compute fairness metrics manually"""
        
        # Split into privileged and unprivileged groups
        privileged_data = df[df[group_col].isin(privileged_groups)]
        unprivileged_data = df[~df[group_col].isin(privileged_groups)]
        
        if len(privileged_data) == 0 or len(unprivileged_data) == 0:
            return {}
        
        # Compute rates for each group
        priv_pos_rate = np.mean(privileged_data['predicted_label'])
        unpriv_pos_rate = np.mean(unprivileged_data['predicted_label'])
        
        # True positive rates (sensitivity)
        priv_tpr = recall_score(privileged_data['true_label'], privileged_data['predicted_label'], zero_division=0)
        unpriv_tpr = recall_score(unprivileged_data['true_label'], unprivileged_data['predicted_label'], zero_division=0)
        
        # False positive rates
        priv_fpr = np.mean(privileged_data[privileged_data['true_label'] == 0]['predicted_label']) if len(privileged_data[privileged_data['true_label'] == 0]) > 0 else 0
        unpriv_fpr = np.mean(unprivileged_data[unprivileged_data['true_label'] == 0]['predicted_label']) if len(unprivileged_data[unprivileged_data['true_label'] == 0]) > 0 else 0
        
        fairness_metrics = {
            'demographic_parity_difference': unpriv_pos_rate - priv_pos_rate,
            'disparate_impact': unpriv_pos_rate / priv_pos_rate if priv_pos_rate > 0 else 0,
            'equalized_odds_difference': abs(unpriv_tpr - priv_tpr) + abs(unpriv_fpr - priv_fpr),
            'equal_opportunity_difference': unpriv_tpr - priv_tpr,
            'privileged_group_size': len(privileged_data),
            'unprivileged_group_size': len(unprivileged_data),
            'privileged_positive_rate': priv_pos_rate,
            'unprivileged_positive_rate': unpriv_pos_rate
        }
        
        return fairness_metrics
    
    def identify_bias_indicators(self, group_metrics: Dict, fairness_metrics: Dict, attr: str) -> List[Dict]:
        """Identify potential bias issues"""
        indicators = []
        
        # Check accuracy disparities
        accuracies = [metrics['accuracy'] for metrics in group_metrics.values()]
        if len(accuracies) > 1:
            accuracy_gap = max(accuracies) - min(accuracies)
            if accuracy_gap > 0.1:
                indicators.append({
                    'type': 'accuracy_disparity',
                    'attribute': attr,
                    'severity': 'high' if accuracy_gap > 0.2 else 'medium',
                    'value': accuracy_gap,
                    'description': f"Accuracy varies by {accuracy_gap:.3f} across {attr} groups"
                })
        
        # Check disparate impact
        if 'disparate_impact' in fairness_metrics:
            di = fairness_metrics['disparate_impact']
            if di > 0 and (di < 0.8 or di > 1.25):  # 80% rule with tolerance
                indicators.append({
                    'type': 'disparate_impact',
                    'attribute': attr,
                    'severity': 'high' if di < 0.7 or di > 1.43 else 'medium',
                    'value': di,
                    'description': f"Disparate impact ratio: {di:.3f} (should be 0.8-1.25)"
                })
        
        # Check false positive rate disparities
        fpr_rates = [metrics['false_positive_rate'] for metrics in group_metrics.values()]
        if len(fpr_rates) > 1:
            fpr_gap = max(fpr_rates) - min(fpr_rates)
            if fpr_gap > 0.1:
                indicators.append({
                    'type': 'false_positive_disparity',
                    'attribute': attr,
                    'severity': 'high' if fpr_gap > 0.2 else 'medium',
                    'value': fpr_gap,
                    'description': f"False positive rate varies by {fpr_gap:.3f} across {attr} groups"
                })
        
        return indicators
    
    def create_comprehensive_visualizations(self, df: pd.DataFrame, analysis_results: Dict) -> str:
        """Create comprehensive bias analysis visualizations"""
        
        # Create figure with subplots
        fig = plt.figure(figsize=(20, 16))
        
        # 1. Performance metrics by skin tone
        ax1 = plt.subplot(3, 3, 1)
        if 'skin_tone' in analysis_results['group_analysis']:
            skin_metrics = analysis_results['group_analysis']['skin_tone']
            skin_tones = list(skin_metrics.keys())
            accuracies = [skin_metrics[tone]['accuracy'] for tone in skin_tones]
            
            bars = ax1.bar(skin_tones, accuracies, color='lightblue', alpha=0.8)
            ax1.set_title('Model Accuracy by Skin Tone', fontweight='bold')
            ax1.set_ylabel('Accuracy')
            ax1.set_ylim(0, 1)
            ax1.tick_params(axis='x', rotation=45)
            
            # Add value labels on bars
            for bar, acc in zip(bars, accuracies):
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                        f'{acc:.3f}', ha='center', va='bottom', fontweight='bold')
            
            # Add threshold line
            ax1.axhline(y=0.8, color='red', linestyle='--', alpha=0.7, label='Minimum Acceptable')
            ax1.legend()
        
        # 2. False Positive Rates
        ax2 = plt.subplot(3, 3, 2)
        if 'skin_tone' in analysis_results['group_analysis']:
            fpr_rates = [skin_metrics[tone]['false_positive_rate'] for tone in skin_tones]
            
            bars = ax2.bar(skin_tones, fpr_rates, color='salmon', alpha=0.8)
            ax2.set_title('False Positive Rate by Skin Tone', fontweight='bold')
            ax2.set_ylabel('False Positive Rate')
            ax2.tick_params(axis='x', rotation=45)
            
            for bar, fpr in zip(bars, fpr_rates):
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005, 
                        f'{fpr:.3f}', ha='center', va='bottom', fontweight='bold')
        
        # 3. Sample size distribution
        ax3 = plt.subplot(3, 3, 3)
        if 'skin_tone' in analysis_results['group_analysis']:
            sample_sizes = [skin_metrics[tone]['sample_size'] for tone in skin_tones]
            
            colors = plt.cm.Set3(np.linspace(0, 1, len(skin_tones)))
            wedges, texts, autotexts = ax3.pie(sample_sizes, labels=skin_tones, autopct='%1.1f%%', 
                                              colors=colors, startangle=90)
            ax3.set_title('Sample Distribution by Skin Tone', fontweight='bold')
        
        # 4. Precision and Recall by skin tone
        ax4 = plt.subplot(3, 3, 4)
        if 'skin_tone' in analysis_results['group_analysis']:
            precisions = [skin_metrics[tone]['precision'] for tone in skin_tones]
            recalls = [skin_metrics[tone]['recall'] for tone in skin_tones]
            
            x = np.arange(len(skin_tones))
            width = 0.35
            
            ax4.bar(x - width/2, precisions, width, label='Precision', color='lightgreen', alpha=0.8)
            ax4.bar(x + width/2, recalls, width, label='Recall', color='lightcoral', alpha=0.8)
            
            ax4.set_title('Precision and Recall by Skin Tone', fontweight='bold')
            ax4.set_ylabel('Score')
            ax4.set_xticks(x)
            ax4.set_xticklabels(skin_tones, rotation=45)
            ax4.legend()
            ax4.set_ylim(0, 1)
        
        # 5. Confidence distribution
        ax5 = plt.subplot(3, 3, 5)
        for tone in df['skin_tone'].unique():
            tone_data = df[df['skin_tone'] == tone]
            ax5.hist(tone_data['confidence'], alpha=0.6, label=tone, bins=20)
        
        ax5.set_title('Confidence Distribution by Skin Tone', fontweight='bold')
        ax5.set_xlabel('Confidence Score')
        ax5.set_ylabel('Frequency')
        ax5.legend()
        
        # 6. Bias indicators summary
        ax6 = plt.subplot(3, 3, 6)
        bias_types = {}
        for indicator in analysis_results['bias_indicators']:
            bias_type = indicator['type']
            severity = indicator['severity']
            if bias_type not in bias_types:
                bias_types[bias_type] = {'high': 0, 'medium': 0, 'low': 0}
            bias_types[bias_type][severity] += 1
        
        if bias_types:
            types = list(bias_types.keys())
            high_counts = [bias_types[t]['high'] for t in types]
            medium_counts = [bias_types[t]['medium'] for t in types]
            
            x = np.arange(len(types))
            ax6.bar(x, high_counts, label='High Severity', color='red', alpha=0.8)
            ax6.bar(x, medium_counts, bottom=high_counts, label='Medium Severity', color='orange', alpha=0.8)
            
            ax6.set_title('Bias Indicators by Type', fontweight='bold')
            ax6.set_ylabel('Count')
            ax6.set_xticks(x)
            ax6.set_xticklabels([t.replace('_', ' ').title() for t in types], rotation=45)
            ax6.legend()
        else:
            ax6.text(0.5, 0.5, 'No Significant Bias Detected!', ha='center', va='center', 
                    fontsize=14, fontweight='bold', color='green')
            ax6.set_title('Bias Assessment', fontweight='bold')
        
        # 7. Performance by age group
        ax7 = plt.subplot(3, 3, 7)
        if 'age_group' in analysis_results['group_analysis']:
            age_metrics = analysis_results['group_analysis']['age_group']
            age_groups = list(age_metrics.keys())
            age_accuracies = [age_metrics[age]['accuracy'] for age in age_groups]
            
            bars = ax7.bar(age_groups, age_accuracies, color='lightsteelblue', alpha=0.8)
            ax7.set_title('Accuracy by Age Group', fontweight='bold')
            ax7.set_ylabel('Accuracy')
            ax7.set_ylim(0, 1)
            
            for bar, acc in zip(bars, age_accuracies):
                ax7.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                        f'{acc:.3f}', ha='center', va='bottom', fontweight='bold')
        
        # 8. Performance by gender
        ax8 = plt.subplot(3, 3, 8)
        if 'gender' in analysis_results['group_analysis']:
            gender_metrics = analysis_results['group_analysis']['gender']
            genders = list(gender_metrics.keys())
            gender_accuracies = [gender_metrics[gender]['accuracy'] for gender in genders]
            
            bars = ax8.bar(genders, gender_accuracies, color='plum', alpha=0.8)
            ax8.set_title('Accuracy by Gender', fontweight='bold')
            ax8.set_ylabel('Accuracy')
            ax8.set_ylim(0, 1)
            
            for bar, acc in zip(bars, gender_accuracies):
                ax8.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                        f'{acc:.3f}', ha='center', va='bottom', fontweight='bold')
        
        # 9. Overall fairness score
        ax9 = plt.subplot(3, 3, 9)
        
        # Calculate overall fairness score
        total_indicators = len(analysis_results['bias_indicators'])
        high_severity = sum(1 for i in analysis_results['bias_indicators'] if i['severity'] == 'high')
        medium_severity = sum(1 for i in analysis_results['bias_indicators'] if i['severity'] == 'medium')
        
        fairness_score = max(0, 100 - (high_severity * 30 + medium_severity * 15))
        
        # Create gauge-like visualization
        theta = np.linspace(0, np.pi, 100)
        colors = ['red' if fairness_score < 60 else 'orange' if fairness_score < 80 else 'green']
        
        ax9.fill_between(theta, 0, 1, color=colors[0], alpha=0.3)
        
        # Add score arc
        score_theta = (fairness_score / 100) * np.pi
        ax9.plot([score_theta, score_theta], [0, 1], color='black', linewidth=4)
        
        ax9.set_xlim(0, np.pi)
        ax9.set_ylim(0, 1)
        ax9.set_title(f'Overall Fairness Score: {fairness_score:.0f}/100', fontweight='bold')
        ax9.text(np.pi/2, 0.5, f'{fairness_score:.0f}', ha='center', va='center', 
                fontsize=20, fontweight='bold')
        ax9.set_xticks([])
        ax9.set_yticks([])
        
        plt.tight_layout()
        
        # Save the comprehensive plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plot_path = os.path.join(self.results_dir, f'comprehensive_fairness_analysis_{timestamp}.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return plot_path
    
    def run_complete_evaluation(self, df: Optional[pd.DataFrame] = None) -> Tuple[Dict, str]:
        """Run complete fairness evaluation"""
        print("🔍 Starting Comprehensive Fairness Evaluation for Skin Lesion AI")
        print("="*70)
        
        # Create or use provided dataset
        if df is None:
            print("📊 Creating synthetic dataset with realistic bias patterns...")
            df = self.create_synthetic_dataset(1000)
        
        print(f"📈 Analyzing {len(df):,} patient records...")
        
        # Initialize results
        analysis_results = {
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
        
        # Define privileged groups for fairness analysis
        privileged_groups_map = {
            'skin_tone': ['very_light', 'light'],
            'age_group': ['middle_aged'],
            'gender': ['male']
        }
        
        # Analyze each demographic attribute
        for attr in ['skin_tone', 'age_group', 'gender']:
            if attr in df.columns:
                print(f"  🔍 Analyzing {attr.replace('_', ' ')}...")
                
                # Group metrics
                group_metrics = self.compute_group_metrics(df, attr)
                analysis_results['group_analysis'][attr] = group_metrics
                
                # Fairness metrics
                if attr in privileged_groups_map:
                    fairness_metrics = self.compute_fairness_metrics(
                        df, attr, privileged_groups_map[attr]
                    )
                    analysis_results['fairness_metrics'][attr] = fairness_metrics
                    
                    # Identify bias indicators
                    bias_indicators = self.identify_bias_indicators(
                        group_metrics, fairness_metrics, attr
                    )
                    analysis_results['bias_indicators'].extend(bias_indicators)
        
        # Create visualizations
        print("📊 Creating comprehensive visualizations...")
        plot_path = self.create_comprehensive_visualizations(df, analysis_results)
        
        # Save detailed report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(self.results_dir, f'fairness_report_{timestamp}.json')
        
        with open(report_path, 'w') as f:
            json.dump(analysis_results, f, indent=2, default=str)
        
        # Print summary
        self._print_detailed_summary(analysis_results)
        
        print(f"\n📄 Detailed report saved: {report_path}")
        print(f"📊 Visualizations saved: {plot_path}")
        print("✅ Fairness evaluation complete!")
        
        return analysis_results, report_path
    
    def _print_detailed_summary(self, results: Dict):
        """Print comprehensive fairness evaluation summary"""
        print("\n" + "="*70)
        print("🎯 FAIRNESS EVALUATION SUMMARY")
        print("="*70)
        
        print(f"📊 Dataset: {results['dataset_size']:,} patient records")
        print(f"🎯 Overall Performance:")
        for metric, value in results['overall_metrics'].items():
            print(f"   • {metric.replace('_', ' ').title()}: {value:.3f}")
        
        print(f"\n🚨 Bias Assessment: {len(results['bias_indicators'])} issues found")
        
        if results['bias_indicators']:
            high_severity = [i for i in results['bias_indicators'] if i['severity'] == 'high']
            medium_severity = [i for i in results['bias_indicators'] if i['severity'] == 'medium']
            
            if high_severity:
                print(f"   🔴 HIGH SEVERITY ({len(high_severity)} issues):")
                for indicator in high_severity:
                    print(f"      • {indicator['description']}")
            
            if medium_severity:
                print(f"   🟡 MEDIUM SEVERITY ({len(medium_severity)} issues):")
                for indicator in medium_severity:
                    print(f"      • {indicator['description']}")
        else:
            print("   ✅ No significant bias detected!")
        
        print(f"\n📈 Performance by Demographic Groups:")
        
        for attr, groups in results['group_analysis'].items():
            print(f"\n  📊 {attr.replace('_', ' ').title()}:")
            print(f"     {'Group':<12} {'Size':<6} {'Accuracy':<9} {'Precision':<10} {'Recall':<8} {'FPR':<6}")
            print(f"     {'-'*12} {'-'*6} {'-'*9} {'-'*10} {'-'*8} {'-'*6}")
            
            for group, metrics in groups.items():
                print(f"     {group:<12} {metrics['sample_size']:<6} "
                     f"{metrics['accuracy']:<9.3f} {metrics['precision']:<10.3f} "
                     f"{metrics['recall']:<8.3f} {metrics['false_positive_rate']:<6.3f}")
        
        print(f"\n⚖️ Fairness Metrics:")
        for attr, fairness in results['fairness_metrics'].items():
            if fairness:
                print(f"\n  📊 {attr.replace('_', ' ').title()}:")
                for metric, value in fairness.items():
                    if 'size' not in metric and 'rate' not in metric:
                        print(f"     • {metric.replace('_', ' ').title()}: {value:.3f}")

def main():
    """Run the fairness evaluation demonstration"""
    evaluator = SimpleFairnessEvaluator()
    results, report_path = evaluator.run_complete_evaluation()
    
    return evaluator, results

if __name__ == "__main__":
    main()