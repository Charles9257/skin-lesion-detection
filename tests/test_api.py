#!/usr/bin/env python3
"""
Quick test script to verify the AI prediction API is working correctly
"""

import requests
import json
import sys
from io import BytesIO
from PIL import Image

def create_test_image():
    """Create a simple test image"""
    # Create a 224x224 RGB image (standard input size)
    img = Image.new('RGB', (224, 224), color='red')
    
    # Save to BytesIO
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    return img_bytes

def test_api_endpoint():
    """Test the /api/upload/ endpoint"""
    print("🧪 Testing AI Prediction API...")
    
    try:
        # Create test image
        test_image = create_test_image()
        
        # Prepare the request
        files = {
            'image': ('test_nevus.jpg', test_image, 'image/jpeg')
        }
        
        # Make the request
        response = requests.post('http://127.0.0.1:8000/api/upload/', files=files, timeout=10)
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API Response:")
            print(json.dumps(data, indent=2))
            
            # Check required fields
            required_fields = ['success', 'prediction', 'confidence', 'confidence_raw']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"⚠️  Missing required fields: {missing_fields}")
            else:
                print("✅ All required fields present")
            
            # Check prediction value
            if 'prediction' in data and data['prediction']:
                print(f"🎯 Prediction: {data['prediction']}")
                print(f"📊 Confidence: {data.get('confidence', 'N/A')}")
                print(f"⚡ Processing Time: {data.get('processing_time', 'N/A')}")
                return True
            else:
                print("❌ Prediction field is missing or empty")
                return False
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - is the server running on http://127.0.0.1:8000/?")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_api_index():
    """Test the /api/ index endpoint"""
    print("\n🧪 Testing API Index...")
    
    try:
        response = requests.get('http://127.0.0.1:8000/api/', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API Index Response:")
            print(json.dumps(data, indent=2))
            return True
        else:
            print(f"❌ API index failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API index test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔬 Starting API Tests...")
    print("=" * 50)
    
    # Test API index
    index_success = test_api_index()
    
    # Test upload endpoint
    upload_success = test_api_endpoint()
    
    print("\n" + "=" * 50)
    print("📋 Test Results:")
    print(f"   API Index: {'✅ PASS' if index_success else '❌ FAIL'}")
    print(f"   Image Upload: {'✅ PASS' if upload_success else '❌ FAIL'}")
    
    if index_success and upload_success:
        print("\n🎉 All tests passed! API is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Check the API implementation.")
        sys.exit(1)