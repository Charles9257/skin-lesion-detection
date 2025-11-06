from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Avg, Count
from django.contrib.admin import AdminSite
from .models import ImageUpload, UserStudyParticipant, UserStudyFeedback, UserStudyAnalysis


class AnalyticsAdminSite(AdminSite):
    """Custom admin site with analytics dashboard"""
    
    site_header = '🩺 Skin Lesion AI - Comprehensive Admin Dashboard'
    site_title = 'Skin Lesion AI Admin'
    index_title = '📊 Analytics, Results & Management Dashboard'
    
    def index(self, request, extra_context=None):
        """Custom admin index with comprehensive analytics"""
        extra_context = extra_context or {}
        
        # Calculate analytics
        total_images = ImageUpload.objects.count()
        total_predictions = ImageUpload.objects.exclude(prediction='').count()
        malignant_predictions = ImageUpload.objects.filter(prediction__icontains='malignant').count()
        benign_predictions = ImageUpload.objects.filter(prediction__icontains='benign').count()
        
        avg_metrics = ImageUpload.objects.aggregate(
            avg_confidence=Avg('confidence'),
            avg_processing_time=Avg('processing_time')
        )
        
        # Critical bias metrics from your analysis
        fairness_metrics = {
            'disparate_impact_ratio': 0.85,
            'equalized_odds': 0.92,
            'demographic_parity': 0.89,
            'individual_fairness': 0.94,
            'accuracy_gap': 14.5,
            'bias_level': 'MEDIUM-HIGH'
        }
        
        extra_context['analytics'] = {
            'total_images': total_images,
            'total_predictions': total_predictions,
            'malignant_predictions': malignant_predictions,
            'benign_predictions': benign_predictions,
            'avg_confidence': (avg_metrics['avg_confidence'] or 0) * 100,
            'avg_processing_time': avg_metrics['avg_processing_time'] or 0,
            'fairness_metrics': fairness_metrics
        }
        
        return super().index(request, extra_context)


class ImageUploadAdmin(admin.ModelAdmin):
    """Comprehensive admin for AI Analysis Results"""
    
    list_display = [
        'id', 'display_filename', 'display_prediction', 'display_confidence',
        'display_processing_time', 'display_user', 'upload_timestamp', 'display_status'
    ]
    
    list_filter = [
        'prediction', 'upload_timestamp', 'model_used',
        'confidence', 'processing_time'
    ]
    
    search_fields = ['filename', 'user__username', 'prediction', 'model_used']
    
    readonly_fields = [
        'upload_timestamp', 'display_prediction_badge', 'display_analytics_summary'
    ]
    
    def display_filename(self, obj):
        return obj.filename[:30] + '...' if len(obj.filename) > 30 else obj.filename
    display_filename.short_description = '📁 Filename'
    
    def display_prediction(self, obj):
        if obj.prediction:
            color = '#dc3545' if obj.prediction.upper() == 'MALIGNANT' else '#28a745'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                color, obj.prediction.upper()
            )
        return '-'
    display_prediction.short_description = '🎯 Prediction'
    
    def display_confidence(self, obj):
        if obj.confidence is not None:
            percentage = obj.confidence * 100
            color = '#dc3545' if percentage > 90 else '#ffc107' if percentage > 70 else '#28a745'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                color, '{:.1f}%'.format(percentage)
            )
        return '-'
    display_confidence.short_description = '📊 Confidence'
    
    def display_processing_time(self, obj):
        if obj.processing_time:
            return "{:.2f}s".format(obj.processing_time)
        return '-'
    display_processing_time.short_description = '⏱️ Process Time'
    
    def display_user(self, obj):
        if obj.user:
            return obj.user.username
        return 'Anonymous'
    display_user.short_description = '👤 User'
    
    def display_status(self, obj):
        if obj.error_message:
            return format_html('<span style="color: #dc3545;">❌ Error</span>')
        elif obj.prediction:
            return format_html('<span style="color: #28a745;">✅ Complete</span>')
        else:
            return format_html('<span style="color: #ffc107;">⏳ Processing</span>')
    display_status.short_description = '🔄 Status'
    
    def display_prediction_badge(self, obj):
        if obj.prediction:
            color = '#dc3545' if obj.prediction.upper() == 'MALIGNANT' else '#28a745'
            confidence = obj.confidence * 100 if obj.confidence else 0
            return format_html(
                '<div style="background: {}; color: white; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold;">' +
                '{}<br><small>{}% Confidence</small></div>',
                color, obj.prediction.upper(), '{:.1f}'.format(confidence)
            )
        return 'No prediction'
    display_prediction_badge.short_description = '🎯 Prediction Badge'
    
    def display_analytics_summary(self, obj):
        total_predictions = ImageUpload.objects.exclude(prediction='').count()
        malignant_count = ImageUpload.objects.filter(prediction__icontains='malignant').count()
        avg_confidence = ImageUpload.objects.exclude(confidence__isnull=True).aggregate(
            avg_conf=Avg('confidence')
        )['avg_conf'] or 0
        
    def display_analytics_summary(self, obj):
        total_predictions = ImageUpload.objects.exclude(prediction='').count()
        malignant_count = ImageUpload.objects.filter(prediction__icontains='malignant').count()
        avg_confidence = ImageUpload.objects.exclude(confidence__isnull=True).aggregate(
            avg_conf=Avg('confidence')
        )['avg_conf'] or 0
        
        malignant_percentage = (malignant_count/total_predictions*100) if total_predictions > 0 else 0
        avg_confidence_percentage = avg_confidence * 100
        
        return format_html(
            '<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #007bff;">' +
            '<h4>📊 System Analytics Summary</h4>' +
            '<p><strong>🎯 Total Predictions:</strong> {}</p>' +
            '<p><strong>⚠️ Malignant Predictions:</strong> {} ({}%)</p>' +
            '<p><strong>📈 Average Confidence:</strong> {}%</p>' +
            '<p><strong>🚨 Critical: False Positive Detected</strong> (ISIC_0000008.jpg)</p>' +
            '<p><strong>⚖️ Bias Level:</strong> MEDIUM-HIGH (14.5% accuracy gap)</p>' +
            '</div>',
            total_predictions, malignant_count, 
            '{:.1f}'.format(malignant_percentage),
            '{:.1f}'.format(avg_confidence_percentage)
        )
    display_analytics_summary.short_description = '📊 Analytics Summary'


class UserStudyParticipantAdmin(admin.ModelAdmin):
    """Admin for User Study Participants"""
    
    list_display = [
        'participant_id', 'display_completion_status', 'age_group', 'gender',
        'skin_type', 'medical_background', 'created_at'
    ]
    
    list_filter = [
        'is_completed', 'age_group', 'gender', 'ethnicity', 'skin_type',
        'medical_background', 'ai_experience', 'created_at'
    ]
    
    search_fields = ['participant_id', 'session_id']
    readonly_fields = ['participant_id', 'session_id', 'created_at']
    
    def display_completion_status(self, obj):
        if obj.is_completed:
            return format_html('<span style="color: #28a745;">✅ Completed</span>')
        return format_html('<span style="color: #ffc107;">⏳ In Progress</span>')
    display_completion_status.short_description = '🔄 Status'


# Create custom admin site
analytics_admin = AnalyticsAdminSite(name='analytics_admin')

# Register models with custom admin site
analytics_admin.register(ImageUpload, ImageUploadAdmin)
analytics_admin.register(UserStudyParticipant, UserStudyParticipantAdmin)

# Also override the default admin site to show analytics
from django.contrib.admin import AdminSite
from django.contrib import admin as default_admin

# Override the default admin site index method
original_index = default_admin.site.index

def analytics_index(self, request, extra_context=None):
    """Override default admin index with analytics"""
    extra_context = extra_context or {}
    
    # Calculate analytics
    total_images = ImageUpload.objects.count()
    total_predictions = ImageUpload.objects.exclude(prediction='').count()
    malignant_predictions = ImageUpload.objects.filter(prediction__icontains='malignant').count()
    benign_predictions = ImageUpload.objects.filter(prediction__icontains='benign').count()
    
    avg_metrics = ImageUpload.objects.aggregate(
        avg_confidence=Avg('confidence'),
        avg_processing_time=Avg('processing_time')
    )
    
    # Critical bias metrics from your analysis
    fairness_metrics = {
        'disparate_impact_ratio': 0.85,
        'equalized_odds': 0.92,
        'demographic_parity': 0.89,
        'individual_fairness': 0.94,
        'accuracy_gap': 14.5,
        'bias_level': 'MEDIUM-HIGH'
    }
    
    extra_context['analytics'] = {
        'total_images': total_images,
        'total_predictions': total_predictions,
        'malignant_predictions': malignant_predictions,
        'benign_predictions': benign_predictions,
        'avg_confidence': (avg_metrics['avg_confidence'] or 0) * 100,
        'avg_processing_time': avg_metrics['avg_processing_time'] or 0,
        'fairness_metrics': fairness_metrics
    }
    
    return original_index(request, extra_context)

# Override the default admin site's index method
default_admin.site.index = analytics_index.__get__(default_admin.site, default_admin.site.__class__)

# Also register with default admin for backward compatibility
admin.site.register(ImageUpload, ImageUploadAdmin)
admin.site.register(UserStudyParticipant, UserStudyParticipantAdmin)