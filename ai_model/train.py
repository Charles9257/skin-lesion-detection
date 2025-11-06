import sys
import os
import tensorflow as tf
import numpy as np
from tensorflow.keras import layers, models, callbacks, optimizers
from tensorflow.keras.applications import EfficientNetB0, ResNet50V2
import matplotlib.pyplot as plt
import json
from pathlib import Path

# Add the project root to the path so we can import from ai_model
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import with error handling for both relative and absolute imports
try:
    from .data_loader import load_dataset
    from .dataset_processor import DatasetProcessor
except ImportError:
    from ai_model.data_loader import load_dataset
    from ai_model.dataset_processor import DatasetProcessor

def build_efficientnet_model(input_shape=(224, 224, 3), num_classes=2, trainable_layers=20):
    """
    Build EfficientNet-based model for skin lesion classification.
    """
    # Load pre-trained EfficientNetB0
    base_model = EfficientNetB0(
        weights='imagenet',
        include_top=False,
        input_shape=input_shape
    )
    
    # Freeze early layers, fine-tune later layers
    base_model.trainable = True
    for layer in base_model.layers[:-trainable_layers]:
        layer.trainable = False
    
    # Add custom classification head
    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(512, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        layers.Dense(256, activation='relu'),
        layers.Dropout(0.2),
        layers.Dense(num_classes, activation='softmax')
    ])
    
    return model

def build_resnet_model(input_shape=(224, 224, 3), num_classes=2):
    """
    Build ResNet50V2-based model for comparison.
    """
    base_model = ResNet50V2(
        weights='imagenet',
        include_top=False,
        input_shape=input_shape
    )
    
    # Fine-tune last few layers
    base_model.trainable = True
    for layer in base_model.layers[:-30]:
        layer.trainable = False
    
    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        layers.Dense(num_classes, activation='softmax')
    ])
    
    return model

def build_custom_cnn(input_shape=(224, 224, 3), num_classes=2):
    """
    Build custom CNN architecture optimized for skin lesions.
    """
    model = models.Sequential([
        # First conv block
        layers.Conv2D(32, (3,3), activation='relu', input_shape=input_shape, padding='same'),
        layers.BatchNormalization(),
        layers.Conv2D(32, (3,3), activation='relu', padding='same'),
        layers.MaxPooling2D(2,2),
        layers.Dropout(0.25),
        
        # Second conv block
        layers.Conv2D(64, (3,3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.Conv2D(64, (3,3), activation='relu', padding='same'),
        layers.MaxPooling2D(2,2),
        layers.Dropout(0.25),
        
        # Third conv block
        layers.Conv2D(128, (3,3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.Conv2D(128, (3,3), activation='relu', padding='same'),
        layers.MaxPooling2D(2,2),
        layers.Dropout(0.25),
        
        # Fourth conv block
        layers.Conv2D(256, (3,3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.Conv2D(256, (3,3), activation='relu', padding='same'),
        layers.MaxPooling2D(2,2),
        layers.Dropout(0.25),
        
        # Classification head
        layers.GlobalAveragePooling2D(),
        layers.BatchNormalization(),
        layers.Dense(512, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(256, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(num_classes, activation='softmax')
    ])
    
    return model

def create_callbacks(model_name):
    """Create training callbacks"""
    os.makedirs("ai_model/saved_models", exist_ok=True)
    os.makedirs("ai_model/logs", exist_ok=True)
    
    return [
        callbacks.ModelCheckpoint(
            f"ai_model/saved_models/{model_name}_best.h5",
            monitor='val_accuracy',
            save_best_only=True,
            mode='max',
            verbose=1
        ),
        callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-7,
            verbose=1
        ),
        callbacks.EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True,
            verbose=1
        ),
        callbacks.TensorBoard(
            log_dir=f"ai_model/logs/{model_name}",
            histogram_freq=1
        )
    ]

def train_model(model_type='efficientnet', use_processed_data=True, max_samples=None):
    """
    Train skin lesion classification model.
    
    Args:
        model_type: 'efficientnet', 'resnet', or 'custom'
        use_processed_data: Whether to use processed dataset
        max_samples: Maximum samples per class (for development)
    """
    print(f"🚀 Training {model_type.upper()} model...")
    
    # Process datasets if needed
    if use_processed_data:
        processed_dir = Path("dataset/processed")
        if not processed_dir.exists() or len(list(processed_dir.glob("*/*.jpg"))) < 100:
            print("📊 Processing datasets...")
            processor = DatasetProcessor("dataset/raw", "dataset/processed")
            stats = processor.process_all_datasets()
    
    # Load dataset
    dataset_path = "dataset/processed" if use_processed_data else "dataset/raw"
    
    try:
        X_train, X_val, X_test, y_train, y_val, y_test, class_map, class_weights = load_dataset(
            dataset_path, 
            img_size=(224, 224),
            test_size=0.15,
            validation_size=0.15,
            augment=True,
            max_samples_per_class=max_samples
        )
        
        print(f"✅ Dataset loaded successfully!")
        print(f"   Training: {X_train.shape}")
        print(f"   Validation: {X_val.shape}")
        print(f"   Test: {X_test.shape}")
        
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        print("Creating dummy model for development...")
        return create_dummy_model()
    
    # Build model
    input_shape = X_train.shape[1:]
    num_classes = y_train.shape[1]
    
    if model_type == 'efficientnet':
        model = build_efficientnet_model(input_shape, num_classes)
        learning_rate = 0.0001
    elif model_type == 'resnet':
        model = build_resnet_model(input_shape, num_classes)
        learning_rate = 0.0001
    else:  # custom
        model = build_custom_cnn(input_shape, num_classes)
        learning_rate = 0.001
    
    # Compile model
    model.compile(
        optimizer=optimizers.Adam(learning_rate=learning_rate),
        loss='categorical_crossentropy',
        metrics=['accuracy', 'precision', 'recall']
    )
    
    print(f"📊 Model Summary:")
    model.summary()
    
    # Create callbacks
    model_callbacks = create_callbacks(f"skin_lesion_{model_type}")
    
    # Train model
    print(f"🎯 Starting training...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=50,
        batch_size=32,
        class_weight=class_weights,
        callbacks=model_callbacks,
        verbose=1
    )
    
    # Evaluate on test set
    print(f"🧪 Evaluating on test set...")
    test_loss, test_acc, test_precision, test_recall = model.evaluate(X_test, y_test, verbose=0)
    test_f1 = 2 * (test_precision * test_recall) / (test_precision + test_recall) if (test_precision + test_recall) > 0 else 0
    
    print(f"\n📈 FINAL TEST RESULTS:")
    print(f"   Test Accuracy: {test_acc:.4f}")
    print(f"   Test Precision: {test_precision:.4f}")
    print(f"   Test Recall: {test_recall:.4f}")
    print(f"   Test F1-Score: {test_f1:.4f}")
    
    # Save final model
    final_model_path = f"ai_model/saved_models/skin_lesion_cnn.h5"
    model.save(final_model_path)
    print(f"💾 Model saved to {final_model_path}")
    
    # Save training results
    results = {
        'model_type': model_type,
        'test_accuracy': float(test_acc),
        'test_precision': float(test_precision),
        'test_recall': float(test_recall),
        'test_f1_score': float(test_f1),
        'class_map': class_map,
        'class_weights': class_weights,
        'training_history': {
            'loss': [float(x) for x in history.history['loss']],
            'accuracy': [float(x) for x in history.history['accuracy']],
            'val_loss': [float(x) for x in history.history['val_loss']],
            'val_accuracy': [float(x) for x in history.history['val_accuracy']]
        }
    }
    
    with open(f"ai_model/saved_models/training_results_{model_type}.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    return model, history, results

def create_dummy_model():
    """Create a dummy model for development when no dataset is available"""
    print("🔧 Creating dummy model for development...")
    model = build_custom_cnn(input_shape=(224, 224, 3), num_classes=2)
    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
    
    # Create dummy data
    dummy_X = tf.random.normal((10, 224, 224, 3))
    dummy_y = tf.keras.utils.to_categorical([0, 1, 0, 1, 0, 1, 0, 1, 0, 1], num_classes=2)
    
    # Train for 1 epoch on dummy data
    model.fit(dummy_X, dummy_y, epochs=1, verbose=0)
    
    # Save the dummy model
    os.makedirs("ai_model/saved_models", exist_ok=True)
    model.save("ai_model/saved_models/skin_lesion_cnn.h5")
    print("✅ Dummy model saved to ai_model/saved_models/skin_lesion_cnn.h5")
    return model

if __name__ == "__main__":
    # Check for GPU
    print(f"🔍 TensorFlow version: {tf.__version__}")
    print(f"🖥️ GPU Available: {tf.config.list_physical_devices('GPU')}")
    
    # Train the model
    try:
        # Start with EfficientNet for best performance
        model, history, results = train_model(
            model_type='efficientnet',
            use_processed_data=True,
            max_samples=None  # Use all data
        )
        print("🎉 Training completed successfully!")
        
    except Exception as e:
        print(f"❌ Training failed: {e}")
        import traceback
        traceback.print_exc()
        
        # Fallback to dummy model
        create_dummy_model()
