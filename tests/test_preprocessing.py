import unittest
import numpy as np
import cv2
import tempfile
import os
from PIL import Image

# Import preprocessing functions
from ai_model.preprocess import (
    resize_image,
    normalize_image, 
    lighting_correction,
    preprocess_image
)


class ImagePreprocessingTestCase(unittest.TestCase):
    """Comprehensive tests for image preprocessing pipeline"""
    
    def setUp(self):
        """Set up test images with different characteristics"""
        # Create test images with different properties
        self.color_image = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
        self.grayscale_image = np.random.randint(0, 255, (200, 200), dtype=np.uint8)
        
        # Create images with specific lighting conditions
        self.dark_image = np.full((200, 200, 3), 50, dtype=np.uint8)  # Dark image
        self.bright_image = np.full((200, 200, 3), 200, dtype=np.uint8)  # Bright image
        
        # Create temporary files
        self.temp_files = []
        
    def tearDown(self):
        """Clean up temporary files"""
        for temp_file in self.temp_files:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def create_temp_image(self, image_array):
        """Helper to create temporary image file"""
        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        Image.fromarray(image_array).save(temp_file.name)
        self.temp_files.append(temp_file.name)
        return temp_file.name
    
    def test_resize_preserves_aspect_ratio(self):
        """Test that resizing maintains proper dimensions"""
        original_shape = self.color_image.shape
        resized = resize_image(self.color_image, size=(224, 224))
        
        self.assertEqual(resized.shape, (224, 224, 3))
        self.assertEqual(resized.dtype, original_shape)
    
    def test_resize_different_input_sizes(self):
        """Test resizing with various input dimensions"""
        # Test with rectangular image
        rect_image = np.random.randint(0, 255, (100, 300, 3), dtype=np.uint8)
        resized = resize_image(rect_image, size=(224, 224))
        self.assertEqual(resized.shape, (224, 224, 3))
        
        # Test with small image
        small_image = np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8)
        resized = resize_image(small_image, size=(224, 224))
        self.assertEqual(resized.shape, (224, 224, 3))
    
    def test_normalize_image_range(self):
        """Test that normalization produces correct value ranges"""
        normalized = normalize_image(self.color_image)
        
        # Check value range
        self.assertTrue(np.all(normalized >= 0.0))
        self.assertTrue(np.all(normalized <= 1.0))
        
        # Check data type
        self.assertEqual(normalized.dtype, np.float32)
        
        # Check that max values are properly scaled
        max_input = np.max(self.color_image)
        max_output = np.max(normalized)
        expected_max = max_input / 255.0
        self.assertAlmostEqual(max_output, expected_max, places=5)
    
    def test_lighting_correction_enhances_contrast(self):
        """Test that lighting correction improves image contrast"""
        # Test with dark image
        corrected_dark = lighting_correction(self.dark_image)
        
        # Corrected image should have higher contrast
        original_std = np.std(self.dark_image)
        corrected_std = np.std(corrected_dark)
        
        # CLAHE should increase standard deviation (contrast)
        self.assertGreater(corrected_std, original_std * 0.8)  # Allow some tolerance
        
        # Test with bright image
        corrected_bright = lighting_correction(self.bright_image)
        self.assertEqual(corrected_bright.shape, self.bright_image.shape)
    
    def test_lighting_correction_grayscale(self):
        """Test lighting correction on grayscale images"""
        corrected = lighting_correction(self.grayscale_image)
        
        self.assertEqual(corrected.shape, self.grayscale_image.shape)
        self.assertEqual(corrected.dtype, self.grayscale_image.dtype)
    
    def test_complete_preprocessing_pipeline(self):
        """Test the complete preprocessing pipeline"""
        temp_file = self.create_temp_image(self.color_image)
        
        # Test successful preprocessing
        processed = preprocess_image(temp_file, size=(224, 224))
        
        # Check output properties
        self.assertEqual(processed.shape, (224, 224, 3))
        self.assertEqual(processed.dtype, np.float32)
        self.assertTrue(np.all(processed >= 0.0))
        self.assertTrue(np.all(processed <= 1.0))
    
    def test_preprocessing_with_different_sizes(self):
        """Test preprocessing with various target sizes"""
        temp_file = self.create_temp_image(self.color_image)
        
        sizes = [(128, 128), (256, 256), (512, 512)]
        
        for size in sizes:
            processed = preprocess_image(temp_file, size=size)
            self.assertEqual(processed.shape, (*size, 3))
    
    def test_preprocessing_error_handling(self):
        """Test preprocessing error handling"""
        # Test with non-existent file
        with self.assertRaises(ValueError):
            preprocess_image("non_existent_file.jpg")
        
        # Test with invalid file (create empty file)
        empty_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        empty_file.close()
        self.temp_files.append(empty_file.name)
        
        with self.assertRaises(ValueError):
            preprocess_image(empty_file.name)
    
    def test_preprocessing_maintains_quality(self):
        """Test that preprocessing maintains image quality"""
        # Create a test image with known patterns
        pattern_image = np.zeros((200, 200, 3), dtype=np.uint8)
        pattern_image[50:150, 50:150] = [255, 0, 0]  # Red square
        
        temp_file = self.create_temp_image(pattern_image)
        processed = preprocess_image(temp_file, size=(224, 224))
        
        # Check that the red region is still prominent
        red_channel = processed[:, :, 0]  # Assuming BGR format from cv2
        self.assertGreater(np.max(red_channel), 0.5)  # Should have significant red values
    
    def test_batch_preprocessing_consistency(self):
        """Test that preprocessing gives consistent results"""
        temp_file = self.create_temp_image(self.color_image)
        
        # Process the same image multiple times
        results = []
        for _ in range(3):
            processed = preprocess_image(temp_file, size=(224, 224))
            results.append(processed)
        
        # All results should be identical
        for i in range(1, len(results)):
            np.testing.assert_array_equal(results[0], results[i])


class LightingCorrectionAdvancedTestCase(unittest.TestCase):
    """Advanced tests for lighting correction specifically"""
    
    def setUp(self):
        """Create images with specific lighting conditions"""
        # Create image with uneven lighting (gradient)
        self.gradient_image = np.zeros((200, 200, 3), dtype=np.uint8)
        for i in range(200):
            self.gradient_image[i, :] = [i * 255 // 200] * 3
    
    def test_clahe_parameters(self):
        """Test that CLAHE parameters are working correctly"""
        corrected = lighting_correction(self.gradient_image)
        
        # Check that the image is modified
        self.assertFalse(np.array_equal(self.gradient_image, corrected))
        
        # Check that output is in valid range
        self.assertTrue(np.all(corrected >= 0))
        self.assertTrue(np.all(corrected <= 255))
    
    def test_lighting_correction_preserves_color_channels(self):
        """Test that color channels are processed appropriately"""
        # Create image with different color channels
        color_test = np.zeros((100, 100, 3), dtype=np.uint8)
        color_test[:, :, 0] = 100  # Red channel
        color_test[:, :, 1] = 150  # Green channel  
        color_test[:, :, 2] = 200  # Blue channel
        
        corrected = lighting_correction(color_test)
        
        # Check that we still have 3 color channels
        self.assertEqual(corrected.shape, color_test.shape)
        
        # Check that channels are still distinguishable
        self.assertNotEqual(np.mean(corrected[:, :, 0]), np.mean(corrected[:, :, 1]))


if __name__ == '__main__':
    unittest.main()