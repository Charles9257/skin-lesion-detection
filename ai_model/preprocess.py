import cv2
import numpy as np
from PIL import Image, ImageEnhance
import random

def resize_image(image, size=(224, 224)):
    """
    Resize image to target size with proper aspect ratio handling.
    """
    return cv2.resize(image, size, interpolation=cv2.INTER_LANCZOS4)

def normalize_image(image):
    """
    Normalize image to range [0, 1].
    """
    return image.astype("float32") / 255.0

def lighting_correction(image):
    """
    Apply lighting normalization using CLAHE (Contrast Limited Adaptive Histogram Equalization).
    Works well for uneven smartphone image lighting.
    """
    if len(image.shape) == 3 and image.shape[2] == 3:  # color image
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl, a, b))
        corrected = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        return corrected
    else:  # grayscale
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        return clahe.apply(image)

def remove_hair_artifacts(image):
    """
    Remove hair artifacts using morphological operations.
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Create kernel for hair removal
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
    
    # Black hat operation to detect hair
    blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)
    
    # Threshold to create hair mask
    _, hair_mask = cv2.threshold(blackhat, 10, 255, cv2.THRESH_BINARY)
    
    # Inpaint to remove hair
    if len(image.shape) == 3:
        result = cv2.inpaint(image, hair_mask, 1, cv2.INPAINT_TELEA)
    else:
        result = cv2.inpaint(image, hair_mask, 1, cv2.INPAINT_TELEA)
    
    return result

def augment_image(image, strong=False):
    """
    Apply data augmentation to image.
    
    Args:
        image: Input image (0-1 normalized)
        strong: Whether to apply stronger augmentations
    """
    # Convert to PIL for augmentation
    img_pil = Image.fromarray((image * 255).astype(np.uint8))
    
    # Random rotation
    if random.random() > 0.5:
        angle = random.uniform(-15, 15) if not strong else random.uniform(-30, 30)
        img_pil = img_pil.rotate(angle, fillcolor=(128, 128, 128))
    
    # Random flip
    if random.random() > 0.5:
        img_pil = img_pil.transpose(Image.FLIP_LEFT_RIGHT)
    
    if random.random() > 0.7:
        img_pil = img_pil.transpose(Image.FLIP_TOP_BOTTOM)
    
    # Color augmentations
    if random.random() > 0.3:
        # Brightness
        enhancer = ImageEnhance.Brightness(img_pil)
        factor = random.uniform(0.8, 1.2) if not strong else random.uniform(0.6, 1.4)
        img_pil = enhancer.enhance(factor)
        
        # Contrast
        enhancer = ImageEnhance.Contrast(img_pil)
        factor = random.uniform(0.8, 1.2) if not strong else random.uniform(0.6, 1.4)
        img_pil = enhancer.enhance(factor)
        
        # Saturation
        enhancer = ImageEnhance.Color(img_pil)
        factor = random.uniform(0.8, 1.2) if not strong else random.uniform(0.5, 1.5)
        img_pil = enhancer.enhance(factor)
    
    # Convert back to numpy and normalize
    augmented = np.array(img_pil)
    return augmented.astype("float32") / 255.0

def preprocess_image(image_path, size=(224, 224), remove_hair=True):
    """
    Full preprocessing pipeline:
    1. Load image
    2. Hair artifact removal (optional)
    3. Lighting normalization
    4. Resize
    5. Normalize
    """
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Unable to load image: {image_path}")
    
    # Convert BGR to RGB for consistency
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Remove hair artifacts
    if remove_hair:
        image = remove_hair_artifacts(image)
    
    # Apply lighting correction
    image = lighting_correction(image)
    
    # Resize to target size
    image = resize_image(image, size)
    
    # Normalize to [0, 1]
    image = normalize_image(image)
    
    return image

def preprocess_batch(image_paths, size=(224, 224), remove_hair=True):
    """
    Preprocess a batch of images efficiently.
    """
    images = []
    failed = []
    
    for img_path in image_paths:
        try:
            image = preprocess_image(img_path, size=size, remove_hair=remove_hair)
            images.append(image)
        except Exception as e:
            failed.append((img_path, str(e)))
    
    return np.array(images), failed
