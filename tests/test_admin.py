#!/usr/bin/env python3
"""
Test script to verify admin interface configuration
"""

import os
import sys
import django

# Add project directory to Python path
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_dir)

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import ImageUpload
from api.admin import ImageUploadAdmin
from django.contrib.admin.sites import AdminSite

def test_admin_methods():
    """Test that all admin display methods work correctly"""
    print("🧪 Testing Admin Interface Methods...")
    
    # Create a mock admin site and admin instance
    site = AdminSite()
    admin_instance = ImageUploadAdmin(ImageUpload, site)
    
    # Create a test ImageUpload object
    test_upload = ImageUpload(
        filename="test_image.jpg",
        prediction="malignant",
        confidence=0.85,
        processing_time=2.5,
        file_size=150000
    )
    
    try:
        # Test each display method
        print("📁 Testing display_filename...")
        filename_result = admin_instance.display_filename(test_upload)
        print(f"   Result: {filename_result}")
        
        print("🎯 Testing display_prediction...")
        prediction_result = admin_instance.display_prediction(test_upload)
        print(f"   Result: {prediction_result}")
        
        print("📊 Testing display_confidence...")
        confidence_result = admin_instance.display_confidence(test_upload)
        print(f"   Result: {confidence_result}")
        
        print("⏱️ Testing display_processing_time...")
        time_result = admin_instance.display_processing_time(test_upload)
        print(f"   Result: {time_result}")
        
        print("🔄 Testing display_status...")
        status_result = admin_instance.display_status(test_upload)
        print(f"   Result: {status_result}")
        
        print("🎯 Testing display_prediction_badge...")
        badge_result = admin_instance.display_prediction_badge(test_upload)
        print(f"   Result: {badge_result[:100]}...")
        
        print("\n✅ All admin display methods work correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing admin methods: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_list_display():
    """Test that list_display fields are all valid"""
    print("\n🧪 Testing list_display configuration...")
    
    site = AdminSite()
    admin_instance = ImageUploadAdmin(ImageUpload, site)
    
    print("📋 Checking list_display fields:")
    for field in admin_instance.list_display:
        print(f"   - {field}")
        
        # Check if it's a model field or admin method
        if hasattr(admin_instance, field):
            print(f"     ✅ Admin method exists")
        elif hasattr(ImageUpload, field):
            print(f"     ✅ Model field exists")
        else:
            print(f"     ❌ Field/method not found!")
            return False
    
    print("✅ All list_display fields are valid!")
    return True

if __name__ == "__main__":
    print("🩺 Testing Skin Lesion Admin Interface")
    print("=" * 50)
    
    # Test admin methods
    methods_ok = test_admin_methods()
    
    # Test list display configuration
    display_ok = test_list_display()
    
    print("\n" + "=" * 50)
    print("📋 Test Results:")
    print(f"   Admin Methods: {'✅ PASS' if methods_ok else '❌ FAIL'}")
    print(f"   List Display: {'✅ PASS' if display_ok else '❌ FAIL'}")
    
    if methods_ok and display_ok:
        print("\n🎉 Admin interface is working correctly!")
        print("You can now access /admin/api/imageupload/ without errors.")
        sys.exit(0)
    else:
        print("\n❌ Some admin tests failed. Check the configuration.")
        sys.exit(1)