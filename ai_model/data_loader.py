import os
import numpy as np
import json
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from tensorflow.keras.utils import to_categorical
import cv2

# Import with error handling for both relative and absolute imports
try:
    from .preprocess import preprocess_image, augment_image
except ImportError:
    from ai_model.preprocess import preprocess_image, augment_image

def load_dataset(data_dir, img_size=(224, 224), test_size=0.2, validation_size=0.2, augment=True, max_samples_per_class=None):
    """
    Load dataset from directory structured as:
    data_dir/
        benign/
            img1.jpg
            img2.jpg
        malignant/
            img3.jpg
            ...
    
    Args:
        data_dir: Path to processed dataset
        img_size: Target image size
        test_size: Fraction for test set
        validation_size: Fraction of training set for validation
        augment: Whether to apply data augmentation
        max_samples_per_class: Maximum samples per class (for development)
    
    Returns: (X_train, X_val, X_test, y_train, y_val, y_test, class_map, class_weights)
    """
    print(f"🔄 Loading dataset from {data_dir}")
    
    data_dir = Path(data_dir)
    if not data_dir.exists():
        raise ValueError(f"Dataset directory not found: {data_dir}")
    
    X, y, filenames = [], [], []
    classes = ['benign', 'malignant']  # Binary classification
    class_map = {cls: idx for idx, cls in enumerate(classes)}
    
    print(f"📁 Classes: {class_map}")
    
    for cls in classes:
        class_dir = data_dir / cls
        if not class_dir.exists():
            print(f"⚠️ Class directory not found: {class_dir}")
            continue
            
        # Get all image files
        image_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
            image_files.extend(list(class_dir.glob(ext)))
        
        print(f"  📂 {cls}: Found {len(image_files)} images")
        
        # Limit samples if specified (for development)
        if max_samples_per_class and len(image_files) > max_samples_per_class:
            image_files = image_files[:max_samples_per_class]
            print(f"    🔢 Limited to {len(image_files)} samples")
        
        loaded_count = 0
        for img_path in image_files:
            try:
                image = preprocess_image(str(img_path), size=img_size)
                X.append(image)
                y.append(class_map[cls])
                filenames.append(img_path.name)
                loaded_count += 1
                
                # Data augmentation for training data
                if augment and cls == 'malignant':  # Augment minority class more
                    aug_image = augment_image(image)
                    X.append(aug_image)
                    y.append(class_map[cls])
                    filenames.append(f"aug_{img_path.name}")
                    loaded_count += 1
                    
            except Exception as e:
                print(f"    ❌ Skipping {img_path.name}: {e}")
        
        print(f"    ✅ Loaded {loaded_count} images for {cls}")
    
    if len(X) == 0:
        raise ValueError("No images loaded! Check dataset structure.")
    
    X = np.array(X, dtype="float32")
    y = np.array(y, dtype="int")
    
    print(f"\n📊 Dataset Statistics:")
    print(f"  Total images: {len(X)}")
    print(f"  Benign: {np.sum(y == 0)} ({np.sum(y == 0)/len(y)*100:.1f}%)")
    print(f"  Malignant: {np.sum(y == 1)} ({np.sum(y == 1)/len(y)*100:.1f}%)")
    print(f"  Image shape: {X[0].shape}")
    
    # First split: separate test set
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=test_size, stratify=y, random_state=42
    )
    
    # Second split: separate train and validation
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=validation_size, stratify=y_temp, random_state=42
    )
    
    print(f"\n📈 Data Splits:")
    print(f"  Training: {len(X_train)} images")
    print(f"  Validation: {len(X_val)} images") 
    print(f"  Test: {len(X_test)} images")
    
    # Calculate class weights for imbalanced data
    class_weights = compute_class_weight(
        'balanced',
        classes=np.unique(y_train),
        y=y_train
    )
    class_weight_dict = {i: class_weights[i] for i in range(len(class_weights))}
    
    print(f"⚖️ Class weights: {class_weight_dict}")
    
    # One-hot encode labels
    y_train = to_categorical(y_train, num_classes=len(classes))
    y_val = to_categorical(y_val, num_classes=len(classes))
    y_test = to_categorical(y_test, num_classes=len(classes))
    
    return X_train, X_val, X_test, y_train, y_val, y_test, class_map, class_weight_dict

if __name__ == "__main__":
    dataset_path = "dataset/processed"  # Example
    X_train, X_test, y_train, y_test, class_map = load_dataset(dataset_path)
    print(f"Train: {X_train.shape}, Test: {X_test.shape}")
    print(f"Classes: {class_map}")
