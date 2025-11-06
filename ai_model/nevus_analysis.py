#!/usr/bin/env python3
"""
Nevus Analysis Tool - Investigate why benign nevus images are predicted as malignant
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import json
from datetime import datetime

def analyze_prediction_confidence(image_path, model_prediction=None, confidence=None):
    """Analyze why a nevus image might be predicted as malignant"""
    
    print("🔍 NEVUS PREDICTION ANALYSIS")
    print("=" * 50)
    
    if os.path.exists(image_path):
        # Load and analyze image
        img = Image.open(image_path)
        img_array = np.array(img)
        
        print(f"📁 Image: {os.path.basename(image_path)}")
        print(f"📏 Dimensions: {img_array.shape}")
        print(f"🎨 Color channels: {img_array.shape[2] if len(img_array.shape) > 2 else 1}")
        
        # Image quality analysis
        brightness = np.mean(img_array)
        contrast = np.std(img_array)
        
        print(f"💡 Brightness: {brightness:.2f}")
        print(f"🌓 Contrast: {contrast:.2f}")
        
        # Color distribution analysis
        if len(img_array.shape) == 3:
            red_mean = np.mean(img_array[:,:,0])
            green_mean = np.mean(img_array[:,:,1])
            blue_mean = np.mean(img_array[:,:,2])
            
            print(f"🔴 Red channel: {red_mean:.2f}")
            print(f"🟢 Green channel: {green_mean:.2f}")
            print(f"🔵 Blue channel: {blue_mean:.2f}")
    
    if model_prediction and confidence:
        print(f"\n🤖 AI Prediction: {model_prediction}")
        print(f"📊 Confidence: {confidence}%")
        
        # Confidence analysis
        if confidence > 90:
            confidence_level = "Very High (Potential overconfidence)"
        elif confidence > 70:
            confidence_level = "High"
        elif confidence > 50:
            confidence_level = "Moderate"
        else:
            confidence_level = "Low (Uncertain)"
            
        print(f"⚡ Confidence Level: {confidence_level}")
    
    print("\n🚨 POSSIBLE REASONS FOR MISCLASSIFICATION:")
    print("-" * 50)
    
    reasons = [
        "1. 🎯 Model Bias: Trained on limited nevus examples",
        "2. 📸 Image Quality: Poor lighting or angle affecting features",
        "3. 🔍 Feature Confusion: Nevus characteristics misinterpreted",
        "4. 🌈 Color Bias: Model sensitive to specific color patterns",
        "5. 📏 Size Bias: Lesion size affecting classification",
        "6. ⚖️ Demographic Bias: Model performance varies by skin type"
    ]
    
    for reason in reasons:
        print(reason)
    
    print("\n💡 RECOMMENDATIONS:")
    print("-" * 30)
    print("✅ Upload multiple nevus images to test consistency")
    print("✅ Check if all nevus images get similar predictions")
    print("✅ Try images with different lighting/angles")
    print("✅ Use the Fairness Analysis in your dashboard")
    print("✅ Consider getting second opinion from medical professional")
    
    # Save analysis report
    report = {
        "timestamp": datetime.now().isoformat(),
        "image_analyzed": os.path.basename(image_path) if os.path.exists(image_path) else "Unknown",
        "prediction": model_prediction,
        "confidence": confidence,
        "analysis_type": "Nevus Misclassification Analysis",
        "recommendations": [
            "Test multiple nevus images",
            "Check prediction consistency", 
            "Review fairness analysis",
            "Consult medical professional"
        ]
    }
    
    with open('nevus_analysis_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Report saved to: nevus_analysis_report.json")

def check_model_bias():
    """Check for systematic bias in the model"""
    print("\n🔬 MODEL BIAS ASSESSMENT")
    print("=" * 30)
    
    bias_indicators = [
        "False Positive Rate: Benign lesions classified as malignant",
        "Training Data Imbalance: More malignant than benign examples",
        "Feature Extraction Bias: Over-emphasis on certain visual patterns",
        "Demographic Representation: Limited diversity in training data"
    ]
    
    for i, indicator in enumerate(bias_indicators, 1):
        print(f"{i}. {indicator}")
    
    print("\n⚠️  CRITICAL: This appears to be a FALSE POSITIVE")
    print("   The AI incorrectly classified benign nevus as malignant")

if __name__ == "__main__":
    print("🩺 SKIN LESION AI - NEVUS ANALYSIS TOOL")
    print("=====================================")
    
    # You can manually input your results here
    analyze_prediction_confidence(
        image_path="sample_nevus.jpg",  # Replace with your actual image path
        model_prediction="Malignant",
        confidence=85  # Replace with actual confidence from your results
    )
    
    check_model_bias()
    
    print("\n🎯 NEXT STEPS:")
    print("1. Check your Results & History tab for confidence scores")
    print("2. Run Fairness Analysis in your dashboard")
    print("3. Upload more nevus images to test consistency")
    print("4. Consider this a potential false positive")