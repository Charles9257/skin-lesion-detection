from django import template
from django.db.models import Avg, Count
from api.models import ImageUpload
from datetime import datetime

register = template.Library()

@register.simple_tag
def get_analytics_data():
    """Get real-time analytics data from the database"""
    
    # Calculate real-time analytics
    total_images = ImageUpload.objects.count()
    total_predictions = ImageUpload.objects.exclude(prediction='').count()
    malignant_predictions = ImageUpload.objects.filter(prediction__icontains='malignant').count()
    benign_predictions = ImageUpload.objects.filter(prediction__icontains='benign').count()
    
    avg_metrics = ImageUpload.objects.aggregate(
        avg_confidence=Avg('confidence'),
        avg_processing_time=Avg('processing_time')
    )
    
    # Calculate malignant rate
    malignant_rate = (malignant_predictions / total_predictions * 100) if total_predictions > 0 else 0
    
    # Find the false positive case
    false_positive_case = ImageUpload.objects.filter(filename='ISIC_0000008.jpg').first()
    if false_positive_case:
        false_positive_case.confidence_pct = false_positive_case.confidence * 100 if false_positive_case.confidence else 0
    
    return {
        'total_images': total_images,
        'total_predictions': total_predictions,
        'malignant_predictions': malignant_predictions,
        'benign_predictions': benign_predictions,
        'avg_confidence': (avg_metrics['avg_confidence'] or 0) * 100,
        'avg_processing_time': avg_metrics['avg_processing_time'] or 0,
        'malignant_rate': malignant_rate,
        'false_positive_case': false_positive_case,
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }