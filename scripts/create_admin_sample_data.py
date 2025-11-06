#!/usr/bin/env python3
"""
Create sample data for the admin dashboard to populate with analytics
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from api.models import ImageUpload, UserStudyParticipant, UserStudyFeedback, UserStudyAnalysis
from feedback.models import (
    Feedback, DemographicProfile, UserStudySession, 
    ImageFeedback, SystemFeedback, ResearchConsent
)

User = get_user_model()

def create_sample_data():
    """Create comprehensive sample data for admin dashboard"""
    
    print("🔧 Creating sample data for admin dashboard...")
    
    # Create sample users
    users = []
    for i in range(5):
        username = f"testuser{i+1}"
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f"{username}@test.com",
                'first_name': f"Test",
                'last_name': f"User{i+1}"
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
        users.append(user)
    
    print(f"✅ Created {len(users)} test users")
    
    # Create sample image uploads with AI predictions
    sample_images = [
        {
            'filename': 'ISIC_0000008.jpg',
            'prediction': 'MALIGNANT', 
            'confidence': 1.0,  # 100% confidence - the false positive case
            'processing_time': 2.3,
            'model_used': 'TensorFlow CNN v2.20.0'
        },
        {
            'filename': 'nevus_sample_001.jpg',
            'prediction': 'MALIGNANT', 
            'confidence': 0.95,  # Another false positive
            'processing_time': 1.8,
            'model_used': 'TensorFlow CNN v2.20.0'
        },
        {
            'filename': 'melanoma_001.jpg',
            'prediction': 'MALIGNANT', 
            'confidence': 0.87,
            'processing_time': 2.1,
            'model_used': 'TensorFlow CNN v2.20.0'
        },
        {
            'filename': 'benign_mole_001.jpg',
            'prediction': 'BENIGN', 
            'confidence': 0.72,
            'processing_time': 1.5,
            'model_used': 'TensorFlow CNN v2.20.0'
        },
        {
            'filename': 'skin_lesion_test.jpg',
            'prediction': 'MALIGNANT', 
            'confidence': 0.93,
            'processing_time': 2.7,
            'model_used': 'TensorFlow CNN v2.20.0'
        }
    ]
    
    image_uploads = []
    for i, img_data in enumerate(sample_images):
        upload = ImageUpload.objects.create(
            filename=img_data['filename'],
            prediction=img_data['prediction'],
            confidence=img_data['confidence'],
            processing_time=img_data['processing_time'],
            model_used=img_data['model_used'],
            user=users[i % len(users)],
            file_size=random.randint(1024*100, 1024*500),  # Random file size
            upload_timestamp=datetime.now() - timedelta(hours=random.randint(1, 72))
        )
        image_uploads.append(upload)
    
    print(f"✅ Created {len(image_uploads)} sample image uploads with AI predictions")
    
    # Create user study participants
    participants = []
    for i in range(3):
        participant = UserStudyParticipant.objects.create(
            age_group=random.choice(['18-25', '26-35', '36-45']),
            gender=random.choice(['male', 'female', 'non-binary']),
            ethnicity=random.choice(['white', 'black', 'hispanic', 'asian']),
            skin_type=random.choice(['type-1', 'type-2', 'type-3', 'type-4']),
            education_level=random.choice(['bachelors', 'masters', 'doctorate']),
            medical_background=random.choice(['none', 'student', 'doctor']),
            ai_experience=random.choice(['none', 'limited', 'moderate']),
            is_completed=random.choice([True, False]),
            consent_timestamp=datetime.now() - timedelta(days=random.randint(1, 30))
        )
        participants.append(participant)
    
    print(f"✅ Created {len(participants)} user study participants")
    
    # Create sample feedback
    feedbacks = []
    for i in range(10):
        feedback = Feedback.objects.create(
            rating=random.randint(1, 5),
            comments=f"Sample feedback comment {i+1} about the AI system.",
            created_at=datetime.now() - timedelta(days=random.randint(1, 30))
        )
        feedbacks.append(feedback)
    
    print(f"✅ Created {len(feedbacks)} sample feedback entries")
    
    print("\n🎯 SAMPLE DATA SUMMARY:")
    print(f"👥 Users: {User.objects.count()}")
    print(f"🖼️ Image Uploads: {ImageUpload.objects.count()}")
    print(f"🔬 Study Participants: {UserStudyParticipant.objects.count()}")
    print(f"💬 Feedback Entries: {Feedback.objects.count()}")
    
    # Show the critical bias case
    false_positive = ImageUpload.objects.filter(filename='ISIC_0000008.jpg').first()
    if false_positive:
        print(f"\n🚨 CRITICAL BIAS CASE DOCUMENTED:")
        print(f"   📁 File: {false_positive.filename}")
        print(f"   🎯 Prediction: {false_positive.prediction}")
        print(f"   📊 Confidence: {false_positive.confidence * 100}%")
        print(f"   ⚠️  Expected: BENIGN (nevus)")
        print(f"   ❌ Result: FALSE POSITIVE")
    
    print("\n✅ Sample data created successfully!")
    print("🌐 Now you can access the admin dashboard with comprehensive analytics:")
    print("   📊 Regular Admin: http://localhost:8000/admin/")
    print("   📈 Analytics Dashboard: http://localhost:8000/analytics/")
    
if __name__ == "__main__":
    try:
        create_sample_data()
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        import traceback
        traceback.print_exc()