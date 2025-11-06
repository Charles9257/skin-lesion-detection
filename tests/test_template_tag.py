#!/usr/bin/env python3
"""
Test the analytics template tag to make sure it works correctly
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.templatetags.admin_tags import get_analytics_data

def test_template_tag():
    """Test the analytics template tag"""
    
    print("🧪 Testing Analytics Template Tag...")
    print("="*50)
    
    try:
        # Get analytics data using the template tag
        analytics = get_analytics_data()
        
        print("📊 Template Tag Results:")
        for key, value in analytics.items():
            print(f"   {key}: {value}")
        
        print(f"\n✅ Template tag working correctly!")
        print(f"📈 Key Metrics:")
        print(f"   🎯 Total Predictions: {analytics['total_predictions']}")
        print(f"   🔴 Malignant: {analytics['malignant_predictions']}")
        print(f"   🟢 Benign: {analytics['benign_predictions']}")
        print(f"   📊 Avg Confidence: {analytics['avg_confidence']:.1f}%")
        print(f"   ⏱️ Avg Processing: {analytics['avg_processing_time']:.2f}s")
        
        if analytics['false_positive_case']:
            case = analytics['false_positive_case']
            print(f"   🚨 False Positive: {case.filename} ({case.prediction}, {case.confidence_pct:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"❌ Template tag error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_template_tag()
    
    if success:
        print(f"\n🎉 Template tag is working! The admin dashboard should now show real data.")
        print(f"🌐 Refresh your admin page at: http://localhost:8000/admin/")
    else:
        print(f"\n❌ Template tag failed. Check the errors above.")