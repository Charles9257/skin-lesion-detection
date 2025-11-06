#!/usr/bin/env python3
"""
Test the fairness tables template tag
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.templatetags.admin_tags import get_fairness_tables

def test_fairness_tables():
    """Test the fairness tables template tag"""
    
    print("🧪 Testing Fairness Tables Template Tag...")
    
    try:
        # Get fairness tables data
        tables_data = get_fairness_tables()
        
        if tables_data:
            print("✅ Fairness tables data loaded successfully!")
            print(f"📊 Dataset Size: {tables_data.get('dataset_size', 'N/A')}")
            print(f"🎯 Overall Accuracy: {tables_data.get('overall_accuracy', 'N/A')}%")
            
            # Check skin tone table
            skin_tone_table = tables_data.get('skin_tone_table', [])
            print(f"\n📊 Skin Tone Groups: {len(skin_tone_table)}")
            for row in skin_tone_table[:3]:  # Show first 3
                print(f"   {row['group']}: {row['size']} patients, {row['accuracy']}% accuracy, {row['fpr']}% FPR")
            
            # Check age table
            age_table = tables_data.get('age_table', [])
            print(f"\n📊 Age Groups: {len(age_table)}")
            for row in age_table:
                print(f"   {row['group']}: {row['size']} patients, {row['accuracy']}% accuracy")
            
            # Check gender table
            gender_table = tables_data.get('gender_table', [])
            print(f"\n📊 Gender Groups: {len(gender_table)}")
            for row in gender_table:
                print(f"   {row['group']}: {row['size']} patients, {row['accuracy']}% accuracy")
            
            # Check fairness metrics
            fairness_table = tables_data.get('fairness_table', [])
            print(f"\n⚖️ Fairness Metrics: {len(fairness_table)} demographics")
            for row in fairness_table:
                print(f"   {row['demographic']}: DI={row['disparate_impact']}, DP={row['demographic_parity']}")
            
            # Check bias summary
            bias_summary = tables_data.get('bias_summary', [])
            print(f"\n🚨 Bias Issues: {len(bias_summary)}")
            for issue in bias_summary:
                print(f"   {issue['type']}: {issue['severity']} ({issue['value']})")
            
            return True
        else:
            print("❌ No fairness tables data available")
            print("   Make sure the fairness evaluation has been run and reports exist")
            return False
            
    except Exception as e:
        print(f"❌ Error testing fairness tables: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_fairness_tables()
    
    if success:
        print(f"\n🎉 Fairness tables template tag is working!")
        print(f"📊 The admin dashboard will now show detailed tabular results")
        print(f"🌐 Access: http://localhost:8000/admin/")
    else:
        print(f"\n❌ Fairness tables template tag needs debugging")
        print(f"🔧 Check that fairness evaluation reports exist in fairness_evaluation_results/")