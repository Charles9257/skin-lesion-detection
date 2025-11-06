import os
import pandas as pd
import numpy as np
import cv2
from pathlib import Path
import shutil
from collections import defaultdict
import json

class DatasetProcessor:
    """
    Comprehensive processor for Fitzpatrick17k, HAM10000, and ISIC datasets
    Handles different formats and creates unified training structure
    """
    
    def __init__(self, raw_data_dir, processed_data_dir):
        self.raw_data_dir = Path(raw_data_dir)
        self.processed_data_dir = Path(processed_data_dir)
        self.class_mapping = {
            # Malignant classes
            'melanoma': 'malignant',
            'squamous cell carcinoma': 'malignant', 
            'basal cell carcinoma': 'malignant',
            'actinic keratosis': 'malignant',  # Pre-cancerous/high-risk
            'kaposi sarcoma': 'malignant',
            'mel': 'malignant',  # HAM10000 melanoma
            'bcc': 'malignant',  # HAM10000 basal cell carcinoma
            'akiec': 'malignant',  # HAM10000 actinic keratoses
            
            # Benign classes
            'nevus': 'benign',
            'dermatofibroma': 'benign',
            'pigmented benign keratosis': 'benign',
            'seborrheic keratosis': 'benign',
            'vascular lesion': 'benign',
            'nv': 'benign',  # HAM10000 melanocytic nevi
            'df': 'benign',  # HAM10000 dermatofibroma
            'bkl': 'benign',  # HAM10000 benign keratosis-like lesions
            'vasc': 'benign',  # HAM10000 vascular lesions
            'sk': 'benign',  # HAM10000 seborrheic keratoses
            
            # Fitzpatrick classes - mostly benign unless specifically malignant
            'malignant dermal': 'malignant',
            'malignant epidermal': 'malignant',
            'malignant melanoma': 'malignant',
            'benign dermal': 'benign',
            'benign epidermal': 'benign',
            'benign melanocyte': 'benign',
            'non-neoplastic': 'benign',  # inflammatory conditions
        }
        
    def process_all_datasets(self):
        """Process all three datasets and create unified structure"""
        print("🔄 Processing all datasets...")
        
        # Create processed directory structure
        self.processed_data_dir.mkdir(exist_ok=True)
        (self.processed_data_dir / 'benign').mkdir(exist_ok=True)
        (self.processed_data_dir / 'malignant').mkdir(exist_ok=True)
        
        stats = defaultdict(int)
        
        # Process each dataset
        stats.update(self.process_isic_dataset())
        stats.update(self.process_ham10000_dataset()) 
        stats.update(self.process_fitzpatrick_dataset())
        
        # Save processing statistics
        self.save_processing_stats(stats)
        
        return stats
    
    def process_isic_dataset(self):
        """Process ISIC skin cancer dataset"""
        print("📁 Processing ISIC dataset...")
        stats = defaultdict(int)
        
        isic_train_dir = self.raw_data_dir / 'Skin cancer ISIC' / 'Train'
        
        if not isic_train_dir.exists():
            print(f"❌ ISIC train directory not found: {isic_train_dir}")
            return stats
            
        for class_dir in isic_train_dir.iterdir():
            if not class_dir.is_dir():
                continue
                
            class_name = class_dir.name.lower()
            target_class = self.class_mapping.get(class_name, 'benign')  # Default to benign
            
            print(f"  📂 Processing {class_name} → {target_class}")
            
            target_dir = self.processed_data_dir / target_class
            
            for img_path in class_dir.glob('*.jpg'):
                try:
                    # Copy image to target directory with ISIC prefix
                    new_name = f"ISIC_{class_name.replace(' ', '_')}_{img_path.name}"
                    target_path = target_dir / new_name
                    
                    if not target_path.exists():
                        shutil.copy2(img_path, target_path)
                        stats[f'isic_{target_class}'] += 1
                        stats['total_isic'] += 1
                        
                except Exception as e:
                    print(f"    ❌ Error processing {img_path.name}: {e}")
                    
        return stats
    
    def process_ham10000_dataset(self):
        """Process HAM10000 dataset using metadata"""
        print("📁 Processing HAM10000 dataset...")
        stats = defaultdict(int)
        
        metadata_path = self.raw_data_dir / 'HAM10000' / 'HAM10000_metadata.csv'
        img_dir1 = self.raw_data_dir / 'HAM10000' / 'HAM10000_images_part_1'
        img_dir2 = self.raw_data_dir / 'HAM10000' / 'HAM10000_images_part_2'
        
        if not metadata_path.exists():
            print(f"❌ HAM10000 metadata not found: {metadata_path}")
            return stats
            
        try:
            df = pd.read_csv(metadata_path)
            print(f"  📊 Found {len(df)} HAM10000 entries")
            
            for _, row in df.iterrows():
                image_id = row['image_id']
                dx = row['dx']  # diagnosis
                
                target_class = self.class_mapping.get(dx, 'benign')
                
                # Find image file
                img_path = None
                for img_dir in [img_dir1, img_dir2]:
                    potential_path = img_dir / f"{image_id}.jpg"
                    if potential_path.exists():
                        img_path = potential_path
                        break
                
                if img_path and img_path.exists():
                    try:
                        target_dir = self.processed_data_dir / target_class
                        new_name = f"HAM_{dx}_{image_id}.jpg"
                        target_path = target_dir / new_name
                        
                        if not target_path.exists():
                            shutil.copy2(img_path, target_path)
                            stats[f'ham_{target_class}'] += 1
                            stats['total_ham'] += 1
                            
                    except Exception as e:
                        print(f"    ❌ Error processing {image_id}: {e}")
                else:
                    stats['ham_missing'] += 1
                    
        except Exception as e:
            print(f"❌ Error processing HAM10000: {e}")
            
        return stats
    
    def process_fitzpatrick_dataset(self):
        """Process Fitzpatrick17k dataset using metadata"""
        print("📁 Processing Fitzpatrick17k dataset...")
        stats = defaultdict(int)
        
        metadata_path = self.raw_data_dir / 'Fitzpatrick17k' / 'fitzpatrick17k (1).csv'
        img_dir = self.raw_data_dir / 'Fitzpatrick17k' / 'background removed'
        
        if not metadata_path.exists():
            print(f"❌ Fitzpatrick metadata not found: {metadata_path}")
            return stats
            
        if not img_dir.exists():
            print(f"❌ Fitzpatrick images not found: {img_dir}")
            return stats
            
        try:
            df = pd.read_csv(metadata_path)
            print(f"  📊 Found {len(df)} Fitzpatrick17k entries")
            
            for _, row in df.iterrows():
                md5hash = row['md5hash']
                label = row['label']
                three_partition_label = row['three_partition_label']
                
                # Use three_partition_label for classification
                target_class = self.class_mapping.get(three_partition_label, 'benign')
                
                # Find image file by md5 hash
                img_files = list(img_dir.glob(f"{md5hash}*"))
                
                if img_files:
                    img_path = img_files[0]
                    try:
                        target_dir = self.processed_data_dir / target_class
                        new_name = f"FITZ_{label.replace(' ', '_')}_{md5hash}{img_path.suffix}"
                        target_path = target_dir / new_name
                        
                        if not target_path.exists():
                            shutil.copy2(img_path, target_path)
                            stats[f'fitz_{target_class}'] += 1
                            stats['total_fitz'] += 1
                            
                    except Exception as e:
                        print(f"    ❌ Error processing {md5hash}: {e}")
                else:
                    stats['fitz_missing'] += 1
                    
        except Exception as e:
            print(f"❌ Error processing Fitzpatrick17k: {e}")
            
        return stats
    
    def save_processing_stats(self, stats):
        """Save processing statistics"""
        stats_file = self.processed_data_dir / 'processing_stats.json'
        
        # Count final images
        benign_count = len(list((self.processed_data_dir / 'benign').glob('*')))
        malignant_count = len(list((self.processed_data_dir / 'malignant').glob('*')))
        
        final_stats = {
            'processing_stats': dict(stats),
            'final_counts': {
                'benign': benign_count,
                'malignant': malignant_count,
                'total': benign_count + malignant_count
            },
            'class_balance': {
                'benign_percentage': (benign_count / (benign_count + malignant_count)) * 100 if (benign_count + malignant_count) > 0 else 0,
                'malignant_percentage': (malignant_count / (benign_count + malignant_count)) * 100 if (benign_count + malignant_count) > 0 else 0
            }
        }
        
        with open(stats_file, 'w') as f:
            json.dump(final_stats, f, indent=2)
            
        print(f"\n📊 DATASET PROCESSING COMPLETE")
        print(f"📁 Benign images: {benign_count}")
        print(f"🔴 Malignant images: {malignant_count}")
        print(f"📈 Total images: {benign_count + malignant_count}")
        print(f"⚖️ Balance: {final_stats['class_balance']['benign_percentage']:.1f}% benign, {final_stats['class_balance']['malignant_percentage']:.1f}% malignant")
        print(f"💾 Stats saved to: {stats_file}")

if __name__ == "__main__":
    # Run dataset processing
    processor = DatasetProcessor(
        raw_data_dir="dataset/raw",
        processed_data_dir="dataset/processed"
    )
    
    stats = processor.process_all_datasets()
    print("\n✅ Dataset processing completed!")