#!/usr/bin/env python3
"""
Quick training script with limited samples for MSc development
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_model.train import train_model

if __name__ == "__main__":
    print("🎓 MSc Project - Quick Training with Limited Samples")
    print("=" * 60)
    
    try:
        # Train with limited samples for development
        model, history, results = train_model(
            model_type='custom',  # Faster custom CNN
            use_processed_data=True,
            max_samples=1000  # 1000 samples per class for quick training
        )
        
        print("\n🎉 Quick training completed!")
        print(f"✅ Test Accuracy: {results['test_accuracy']:.4f}")
        print(f"✅ Test F1-Score: {results['test_f1_score']:.4f}")
        print("\n📝 Model saved and ready for use in your application!")
        
    except Exception as e:
        print(f"❌ Training failed: {e}")
        import traceback
        traceback.print_exc()