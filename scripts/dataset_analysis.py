"""
Dataset Analysis Tools for Skin Lesion Detection Research

This module provides comprehensive analysis tools for evaluating dataset diversity,
bias, and characteristics in the context of fairness-aware machine learning.
"""

import os
import pandas as pd
import numpy as np
import cv2
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json
from sklearn.cluster import KMeans
from collections import defaultdict, Counter
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


class DatasetAnalyzer:
    """Comprehensive dataset analysis for skin lesion detection"""
    
    def __init__(self, dataset_path: str):
        """
        Initialize dataset analyzer
        
        Args:
            dataset_path: Path to the raw dataset folder
        """
        self.dataset_path = Path(dataset_path)
        self.analysis_results = {}
        
    def analyze_dataset_structure(self) -> Dict:
        """Analyze the basic structure of the dataset"""
        structure = {
            'total_images': 0,
            'classes': {},
            'file_formats': Counter(),
            'directory_structure': []
        }
        
        if not self.dataset_path.exists():
            print(f"Dataset path {self.dataset_path} does not exist")
            return structure
        
        for root, dirs, files in os.walk(self.dataset_path):
            level = root.replace(str(self.dataset_path), '').count(os.sep)
            indent = ' ' * 2 * level
            structure['directory_structure'].append(f"{indent}{os.path.basename(root)}/")
            
            # Analyze images in current directory
            image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]
            
            if image_files:
                class_name = os.path.basename(root)
                structure['classes'][class_name] = {
                    'count': len(image_files),
                    'files': image_files[:5]  # Store first 5 for reference
                }
                structure['total_images'] += len(image_files)
                
                # Count file formats
                for img_file in image_files:
                    ext = os.path.splitext(img_file)[1].lower()
                    structure['file_formats'][ext] += 1
        
        self.analysis_results['structure'] = structure
        return structure
    
    def analyze_image_properties(self, sample_size: int = 100) -> Dict:
        """Analyze image properties (dimensions, color distributions, etc.)"""
        properties = {
            'dimensions': [],
            'aspect_ratios': [],
            'file_sizes': [],
            'color_stats': {
                'brightness': [],
                'contrast': [],
                'saturation': []
            },
            'skin_tone_distribution': Counter()
        }
        
        sample_count = 0
        
        for root, dirs, files in os.walk(self.dataset_path):
            image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]
            
            for img_file in image_files:
                if sample_count >= sample_size:
                    break
                    
                img_path = os.path.join(root, img_file)
                
                try:
                    # Basic file properties
                    file_size = os.path.getsize(img_path)
                    properties['file_sizes'].append(file_size)
                    
                    # Load and analyze image
                    image = cv2.imread(img_path)
                    if image is None:
                        continue
                        
                    h, w = image.shape[:2]
                    properties['dimensions'].append((w, h))
                    properties['aspect_ratios'].append(w / h)
                    
                    # Color analysis
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    properties['color_stats']['brightness'].append(np.mean(gray))
                    properties['color_stats']['contrast'].append(np.std(gray))
                    
                    # HSV analysis for saturation
                    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
                    properties['color_stats']['saturation'].append(np.mean(hsv[:, :, 1]))
                    
                    # Simple skin tone classification
                    skin_tone = self._classify_skin_tone(image)
                    properties['skin_tone_distribution'][skin_tone] += 1
                    
                    sample_count += 1
                    
                except Exception as e:
                    print(f"Error analyzing {img_path}: {e}")
                    continue
        
        # Calculate statistics
        properties['dimension_stats'] = self._calculate_dimension_stats(properties['dimensions'])
        properties['aspect_ratio_stats'] = self._calculate_stats(properties['aspect_ratios'])
        properties['file_size_stats'] = self._calculate_stats(properties['file_sizes'])
        
        for stat_type in properties['color_stats']:
            properties[f'{stat_type}_stats'] = self._calculate_stats(properties['color_stats'][stat_type])
        
        self.analysis_results['properties'] = properties
        return properties
    
    def _classify_skin_tone(self, image: np.ndarray) -> str:
        """Simple skin tone classification"""
        try:
            # Convert to HSV for better skin detection
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Define skin color range
            lower_skin = np.array([0, 20, 70], dtype=np.uint8)
            upper_skin = np.array([20, 255, 255], dtype=np.uint8)
            
            # Create mask for skin pixels
            skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
            skin_pixels = image[skin_mask > 0]
            
            if len(skin_pixels) == 0:
                return 'unknown'
            
            # Calculate average brightness
            avg_brightness = np.mean(cv2.cvtColor(skin_pixels.reshape(-1, 1, 3), cv2.COLOR_BGR2GRAY))
            
            if avg_brightness > 180:
                return 'light'
            elif avg_brightness > 120:
                return 'medium'
            else:
                return 'dark'
        except:
            return 'unknown'
    
    def _calculate_stats(self, data: List) -> Dict:
        """Calculate basic statistics for a list of values"""
        if not data:
            return {}
        
        return {
            'mean': np.mean(data),
            'median': np.median(data),
            'std': np.std(data),
            'min': np.min(data),
            'max': np.max(data),
            'q25': np.percentile(data, 25),
            'q75': np.percentile(data, 75)
        }
    
    def _calculate_dimension_stats(self, dimensions: List[Tuple]) -> Dict:
        """Calculate statistics for image dimensions"""
        if not dimensions:
            return {}
        
        widths = [d[0] for d in dimensions]
        heights = [d[1] for d in dimensions]
        
        return {
            'width_stats': self._calculate_stats(widths),
            'height_stats': self._calculate_stats(heights),
            'common_resolutions': Counter(dimensions).most_common(10)
        }
    
    def analyze_class_balance(self) -> Dict:
        """Analyze class balance and distribution"""
        if 'structure' not in self.analysis_results:
            self.analyze_dataset_structure()
        
        classes = self.analysis_results['structure']['classes']
        
        balance_analysis = {
            'class_counts': {k: v['count'] for k, v in classes.items()},
            'total_samples': sum(v['count'] for v in classes.values()),
            'num_classes': len(classes),
            'balance_metrics': {}
        }
        
        if balance_analysis['num_classes'] > 1:
            counts = list(balance_analysis['class_counts'].values())
            
            balance_analysis['balance_metrics'] = {
                'imbalance_ratio': max(counts) / min(counts) if min(counts) > 0 else float('inf'),
                'entropy': self._calculate_entropy(counts),
                'coefficient_of_variation': np.std(counts) / np.mean(counts) if np.mean(counts) > 0 else 0
            }
        
        self.analysis_results['class_balance'] = balance_analysis
        return balance_analysis
    
    def _calculate_entropy(self, counts: List[int]) -> float:
        """Calculate entropy for class distribution"""
        total = sum(counts)
        if total == 0:
            return 0
        
        probabilities = [c / total for c in counts]
        entropy = -sum(p * np.log2(p) for p in probabilities if p > 0)
        return entropy
    
    def analyze_diversity_metrics(self) -> Dict:
        """Calculate comprehensive diversity metrics"""
        diversity = {
            'skin_tone_diversity': {},
            'demographic_diversity': {},
            'image_diversity': {}
        }
        
        # Skin tone diversity
        if 'properties' in self.analysis_results:
            skin_tone_dist = self.analysis_results['properties']['skin_tone_distribution']
            total_samples = sum(skin_tone_dist.values())
            
            diversity['skin_tone_diversity'] = {
                'distribution': dict(skin_tone_dist),
                'entropy': self._calculate_entropy(list(skin_tone_dist.values())),
                'representation_ratios': {
                    tone: count / total_samples 
                    for tone, count in skin_tone_dist.items()
                } if total_samples > 0 else {}
            }
        
        # Image diversity (based on visual features)
        if 'properties' in self.analysis_results:
            props = self.analysis_results['properties']
            
            diversity['image_diversity'] = {
                'brightness_range': {
                    'min': min(props['color_stats']['brightness']) if props['color_stats']['brightness'] else 0,
                    'max': max(props['color_stats']['brightness']) if props['color_stats']['brightness'] else 0,
                    'std': np.std(props['color_stats']['brightness']) if props['color_stats']['brightness'] else 0
                },
                'dimension_variety': len(set(props['dimensions'])),
                'aspect_ratio_variety': len(set(np.round(props['aspect_ratios'], 2))) if props['aspect_ratios'] else 0
            }
        
        self.analysis_results['diversity'] = diversity
        return diversity
    
    def generate_visualizations(self, output_dir: str = "dataset_analysis_plots"):
        """Generate comprehensive visualizations of the dataset analysis"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Set style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # 1. Class distribution plot
        if 'class_balance' in self.analysis_results:
            self._plot_class_distribution(output_path)
        
        # 2. Image properties plots
        if 'properties' in self.analysis_results:
            self._plot_image_properties(output_path)
        
        # 3. Skin tone distribution
        if 'properties' in self.analysis_results:
            self._plot_skin_tone_distribution(output_path)
        
        # 4. Diversity metrics
        if 'diversity' in self.analysis_results:
            self._plot_diversity_metrics(output_path)
        
        print(f"Visualizations saved to {output_path}")
    
    def _plot_class_distribution(self, output_path: Path):
        """Plot class distribution"""
        class_data = self.analysis_results['class_balance']['class_counts']
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Bar plot
        classes = list(class_data.keys())
        counts = list(class_data.values())
        
        ax1.bar(classes, counts, color=sns.color_palette("husl", len(classes)))
        ax1.set_title('Class Distribution')
        ax1.set_xlabel('Class')
        ax1.set_ylabel('Number of Images')
        ax1.tick_params(axis='x', rotation=45)
        
        # Pie chart
        ax2.pie(counts, labels=classes, autopct='%1.1f%%', startangle=90)
        ax2.set_title('Class Distribution (Proportional)')
        
        plt.tight_layout()
        plt.savefig(output_path / 'class_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_image_properties(self, output_path: Path):
        """Plot image properties"""
        props = self.analysis_results['properties']
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        
        # Dimensions scatter plot
        if props['dimensions']:
            widths, heights = zip(*props['dimensions'])
            axes[0, 0].scatter(widths, heights, alpha=0.6)
            axes[0, 0].set_title('Image Dimensions')
            axes[0, 0].set_xlabel('Width')
            axes[0, 0].set_ylabel('Height')
        
        # Aspect ratios histogram
        if props['aspect_ratios']:
            axes[0, 1].hist(props['aspect_ratios'], bins=30, alpha=0.7)
            axes[0, 1].set_title('Aspect Ratio Distribution')
            axes[0, 1].set_xlabel('Aspect Ratio')
            axes[0, 1].set_ylabel('Frequency')
        
        # File sizes histogram
        if props['file_sizes']:
            file_sizes_mb = [size / (1024 * 1024) for size in props['file_sizes']]
            axes[0, 2].hist(file_sizes_mb, bins=30, alpha=0.7)
            axes[0, 2].set_title('File Size Distribution')
            axes[0, 2].set_xlabel('File Size (MB)')
            axes[0, 2].set_ylabel('Frequency')
        
        # Color properties
        color_stats = props['color_stats']
        for i, (stat_name, values) in enumerate(color_stats.items()):
            if values and i < 3:
                axes[1, i].hist(values, bins=30, alpha=0.7)
                axes[1, i].set_title(f'{stat_name.capitalize()} Distribution')
                axes[1, i].set_xlabel(stat_name.capitalize())
                axes[1, i].set_ylabel('Frequency')
        
        plt.tight_layout()
        plt.savefig(output_path / 'image_properties.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_skin_tone_distribution(self, output_path: Path):
        """Plot skin tone distribution"""
        skin_tone_dist = self.analysis_results['properties']['skin_tone_distribution']
        
        if not skin_tone_dist:
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        tones = list(skin_tone_dist.keys())
        counts = list(skin_tone_dist.values())
        
        # Bar plot
        colors = {'light': '#F5DEB3', 'medium': '#DEB887', 'dark': '#8B4513', 'unknown': '#808080'}
        bar_colors = [colors.get(tone, '#808080') for tone in tones]
        
        ax1.bar(tones, counts, color=bar_colors)
        ax1.set_title('Skin Tone Distribution')
        ax1.set_xlabel('Skin Tone Category')
        ax1.set_ylabel('Number of Images')
        
        # Pie chart
        ax2.pie(counts, labels=tones, autopct='%1.1f%%', colors=bar_colors, startangle=90)
        ax2.set_title('Skin Tone Distribution (Proportional)')
        
        plt.tight_layout()
        plt.savefig(output_path / 'skin_tone_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_diversity_metrics(self, output_path: Path):
        """Plot diversity metrics"""
        diversity = self.analysis_results['diversity']
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Skin tone representation
        if 'skin_tone_diversity' in diversity:
            skin_repr = diversity['skin_tone_diversity'].get('representation_ratios', {})
            if skin_repr:
                tones = list(skin_repr.keys())
                ratios = list(skin_repr.values())
                
                axes[0, 0].bar(tones, ratios)
                axes[0, 0].set_title('Skin Tone Representation Ratios')
                axes[0, 0].set_xlabel('Skin Tone')
                axes[0, 0].set_ylabel('Proportion')
                axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Image diversity metrics
        if 'image_diversity' in diversity:
            img_div = diversity['image_diversity']
            
            # Brightness range
            if 'brightness_range' in img_div:
                br = img_div['brightness_range']
                axes[0, 1].bar(['Min', 'Max', 'Std'], [br['min'], br['max'], br['std']])
                axes[0, 1].set_title('Brightness Diversity')
                axes[0, 1].set_ylabel('Brightness Value')
            
            # Dimension and aspect ratio variety
            variety_metrics = ['dimension_variety', 'aspect_ratio_variety']
            variety_values = [img_div.get(metric, 0) for metric in variety_metrics]
            
            axes[1, 0].bar(['Dimension\nVariety', 'Aspect Ratio\nVariety'], variety_values)
            axes[1, 0].set_title('Visual Diversity Metrics')
            axes[1, 0].set_ylabel('Number of Unique Values')
        
        # Summary metrics
        summary_data = []
        if 'skin_tone_diversity' in diversity:
            entropy = diversity['skin_tone_diversity'].get('entropy', 0)
            summary_data.append(('Skin Tone Entropy', entropy))
        
        if 'class_balance' in self.analysis_results:
            balance_metrics = self.analysis_results['class_balance']['balance_metrics']
            if 'entropy' in balance_metrics:
                summary_data.append(('Class Entropy', balance_metrics['entropy']))
            if 'imbalance_ratio' in balance_metrics:
                ratio = min(balance_metrics['imbalance_ratio'], 10)  # Cap for visualization
                summary_data.append(('Imbalance Ratio', ratio))
        
        if summary_data:
            metrics, values = zip(*summary_data)
            axes[1, 1].bar(metrics, values)
            axes[1, 1].set_title('Dataset Quality Metrics')
            axes[1, 1].set_ylabel('Value')
            axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(output_path / 'diversity_metrics.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_report(self, output_file: str = "dataset_analysis_report.json"):
        """Generate comprehensive analysis report"""
        
        # Run all analyses if not already done
        if 'structure' not in self.analysis_results:
            self.analyze_dataset_structure()
        if 'properties' not in self.analysis_results:
            self.analyze_image_properties()
        if 'class_balance' not in self.analysis_results:
            self.analyze_class_balance()
        if 'diversity' not in self.analysis_results:
            self.analyze_diversity_metrics()
        
        # Add summary
        self.analysis_results['summary'] = {
            'dataset_path': str(self.dataset_path),
            'analysis_timestamp': pd.Timestamp.now().isoformat(),
            'total_images': self.analysis_results['structure']['total_images'],
            'num_classes': self.analysis_results['structure'].get('total_images', 0),
            'key_findings': self._generate_key_findings()
        }
        
        # Save report
        with open(output_file, 'w') as f:
            # Convert numpy types for JSON serialization
            serializable_results = self._make_json_serializable(self.analysis_results)
            json.dump(serializable_results, f, indent=2)
        
        print(f"Analysis report saved to {output_file}")
        return self.analysis_results
    
    def _make_json_serializable(self, obj):
        """Convert numpy types to Python types for JSON serialization"""
        if isinstance(obj, dict):
            return {key: self._make_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, Counter):
            return dict(obj)
        else:
            return obj
    
    def _generate_key_findings(self) -> List[str]:
        """Generate key findings from the analysis"""
        findings = []
        
        # Class balance findings
        if 'class_balance' in self.analysis_results:
            balance = self.analysis_results['class_balance']['balance_metrics']
            if 'imbalance_ratio' in balance:
                ratio = balance['imbalance_ratio']
                if ratio > 10:
                    findings.append(f"Severe class imbalance detected (ratio: {ratio:.2f})")
                elif ratio > 3:
                    findings.append(f"Moderate class imbalance detected (ratio: {ratio:.2f})")
                else:
                    findings.append("Classes are relatively balanced")
        
        # Skin tone diversity findings
        if 'diversity' in self.analysis_results:
            skin_diversity = self.analysis_results['diversity']['skin_tone_diversity']
            if 'representation_ratios' in skin_diversity:
                ratios = skin_diversity['representation_ratios']
                if 'unknown' in ratios and ratios['unknown'] > 0.3:
                    findings.append("High proportion of images with unclassifiable skin tone")
                
                known_ratios = {k: v for k, v in ratios.items() if k != 'unknown'}
                if known_ratios:
                    min_repr = min(known_ratios.values())
                    max_repr = max(known_ratios.values())
                    if max_repr / min_repr > 3:
                        findings.append("Uneven skin tone representation across categories")
        
        # Image quality findings
        if 'properties' in self.analysis_results:
            props = self.analysis_results['properties']
            
            # Check dimension variety
            if 'dimension_stats' in props:
                common_res = props['dimension_stats'].get('common_resolutions', [])
                if len(common_res) > 0:
                    most_common_count = common_res[0][1]
                    total_analyzed = sum(count for _, count in common_res)
                    if most_common_count / total_analyzed > 0.8:
                        findings.append("Low resolution diversity - most images have same dimensions")
        
        return findings


if __name__ == "__main__":
    # Example usage
    dataset_path = "dataset/raw"
    
    if os.path.exists(dataset_path):
        analyzer = DatasetAnalyzer(dataset_path)
        
        print("Analyzing dataset structure...")
        structure = analyzer.analyze_dataset_structure()
        print(f"Found {structure['total_images']} images across {len(structure['classes'])} classes")
        
        print("Analyzing image properties...")
        properties = analyzer.analyze_image_properties(sample_size=200)
        
        print("Analyzing class balance...")
        balance = analyzer.analyze_class_balance()
        
        print("Analyzing diversity metrics...")
        diversity = analyzer.analyze_diversity_metrics()
        
        print("Generating visualizations...")
        analyzer.generate_visualizations()
        
        print("Generating comprehensive report...")
        report = analyzer.generate_report()
        
        print("Analysis complete! Check the generated files for detailed results.")
    else:
        print(f"Dataset path '{dataset_path}' not found. Please ensure your dataset is in the correct location.")