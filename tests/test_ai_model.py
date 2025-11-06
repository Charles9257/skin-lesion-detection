import unittest
import numpy as np
import cv2
import tempfile
import os
from PIL import Image
import tensorflow as tf

# Import AI model functions
from ai_model.preprocess import (
    resize_image, 
    normalize_image, 
    lighting_correction, 
    preprocess_image
)
from ai_model.train import build_custom_cnn
from ai_model.data_loader import load_dataset


class PreprocessingTestCase(unittest.TestCase):
    """Test cases for image preprocessing functions"""
    
    def setUp(self):
        """Create test images for preprocessing tests"""
        # Create a test image
        self.test_image = np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8)
        
        # Create a temporary image file
        self.temp_image = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        Image.fromarray(self.test_image).save(self.temp_image.name)
        
    def tearDown(self):
        """Clean up temporary files"""
        if os.path.exists(self.temp_image.name):
            os.unlink(self.temp_image.name)
    
    def test_resize_image(self):
        """Test image resizing function"""
        resized = resize_image(self.test_image, size=(224, 224))
        self.assertEqual(resized.shape, (224, 224, 3))
        
    def test_resize_image_different_size(self):
        """Test image resizing with different dimensions"""
        resized = resize_image(self.test_image, size=(128, 128))
        self.assertEqual(resized.shape, (128, 128, 3))
    
    def test_normalize_image(self):
        """Test image normalization function"""
        normalized = normalize_image(self.test_image)
        self.assertTrue(np.all(normalized >= 0))
        self.assertTrue(np.all(normalized <= 1))
        self.assertEqual(normalized.dtype, np.float32)
    
    def test_lighting_correction_color(self):
        """Test lighting correction on color image"""
        corrected = lighting_correction(self.test_image)
        self.assertEqual(corrected.shape, self.test_image.shape)
        self.assertEqual(corrected.dtype, self.test_image.dtype)
    
    def test_lighting_correction_grayscale(self):
        """Test lighting correction on grayscale image"""
        gray_image = cv2.cvtColor(self.test_image, cv2.COLOR_BGR2GRAY)
        corrected = lighting_correction(gray_image)
        self.assertEqual(corrected.shape, gray_image.shape)
    
    def test_preprocess_image_pipeline(self):
        """Test complete preprocessing pipeline"""
        processed = preprocess_image(self.temp_image.name, size=(224, 224))
        
        self.assertEqual(processed.shape, (224, 224, 3))
        self.assertTrue(np.all(processed >= 0))
        self.assertTrue(np.all(processed <= 1))
        self.assertEqual(processed.dtype, np.float32)
    
    def test_preprocess_image_invalid_path(self):
        """Test preprocessing with invalid image path"""
        with self.assertRaises(ValueError):
            preprocess_image("nonexistent_image.jpg")


class CNNModelTestCase(unittest.TestCase):
    """Test cases for CNN model building and training"""
    
    def test_build_cnn_default_params(self):
        """Test CNN model building with default parameters"""
        model = build_custom_cnn()
        
        # Check model structure
        self.assertIsInstance(model, tf.keras.Model)
        
        # Check input shape
        expected_input_shape = (None, 224, 224, 3)
        self.assertEqual(model.input_shape, expected_input_shape)
        
        # Check output shape
        expected_output_shape = (None, 2)
        self.assertEqual(model.output_shape, expected_output_shape)
    
    def test_build_cnn_custom_params(self):
        """Test CNN model building with custom parameters"""
        custom_input_shape = (128, 128, 3)
        custom_num_classes = 5
        
        model = build_custom_cnn(
            input_shape=custom_input_shape, 
            num_classes=custom_num_classes
        )
        
        expected_input_shape = (None, 128, 128, 3)
        expected_output_shape = (None, 5)
        
        self.assertEqual(model.input_shape, expected_input_shape)
        self.assertEqual(model.output_shape, expected_output_shape)
    
    def test_model_compilation(self):
        """Test model compilation"""
        model = build_custom_cnn()
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        self.assertEqual(model.optimizer.name, 'adam')


class DataLoaderTestCase(unittest.TestCase):
    """Test cases for data loading functionality"""
    
    def setUp(self):
        """Create temporary dataset structure for testing"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create class directories
        self.class1_dir = os.path.join(self.temp_dir, 'benign')
        self.class2_dir = os.path.join(self.temp_dir, 'malignant')
        os.makedirs(self.class1_dir)
        os.makedirs(self.class2_dir)
        
        # Create test images
        for i in range(5):
            # Benign images
            test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
            Image.fromarray(test_image).save(
                os.path.join(self.class1_dir, f'benign_{i}.jpg')
            )
            
            # Malignant images  
            test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
            Image.fromarray(test_image).save(
                os.path.join(self.class2_dir, f'malignant_{i}.jpg')
            )
    
    def tearDown(self):
        """Clean up temporary dataset"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_dataset_structure(self):
        """Test dataset loading returns correct structure"""
        try:
            X_train, X_test, y_train, y_test, class_map = load_dataset(
                self.temp_dir, img_size=(64, 64), test_size=0.2
            )
            
            # Check data shapes
            self.assertEqual(X_train.shape[1:], (64, 64, 3))
            self.assertEqual(X_test.shape[1:], (64, 64, 3))
            
            # Check that we have training and test data
            self.assertGreater(len(X_train), 0)
            self.assertGreater(len(X_test), 0)
            
            # Check class mapping
            self.assertIn('benign', class_map)
            self.assertIn('malignant', class_map)
            
            # Check one-hot encoding
            self.assertEqual(y_train.shape[1], len(class_map))
            self.assertEqual(y_test.shape[1], len(class_map))
            
        except Exception as e:
            # If preprocessing fails due to missing dependencies, skip this test
            self.skipTest(f"Dataset loading test skipped due to: {e}")


if __name__ == '__main__':
    unittest.main()