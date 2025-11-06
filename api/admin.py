from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.db.models import Avg, Count
from django.contrib.admin import AdminSite
from .models import (
    ImageUpload, UserStudyParticipant, DemographicProfile, UserStudyFeedback,
    ImageFeedback, ResearchConsent, SystemFeedback, UserStudySession,
    FairnessAnalysisResult
)

# Custom User Admin to enhance user management
class CustomUserAdmin(UserAdmin):
    """Enhanced User Admin for managing users"""
    
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined', 'last_login']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined', 'last_login']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('last_login', 'date_joined'),
        }),
    )
    
    readonly_fields = ['last_login', 'date_joined']

# Safely unregister and register User admin
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass
admin.site.register(User, CustomUserAdmin)

class AnalyticsAdminSite(AdminSite):
    """Custom admin site with analytics dashboard"""
    
    site_header = '🩺 Skin Lesion AI - Research & Analytics Dashboard'
    site_title = 'Skin Lesion AI Research Admin'
    index_title = '📊 Research Analytics, User Studies & System Management'
    
    def index(self, request, extra_context=None):
        """Custom admin index with comprehensive analytics"""
        extra_context = extra_context or {}
        
        # Calculate analytics
        total_images = ImageUpload.objects.count()
        total_predictions = ImageUpload.objects.exclude(prediction='').count()
        cancer_detections = ImageUpload.objects.filter(result='cancer').count()
        suspected_cancer = ImageUpload.objects.filter(result='suspected_cancer').count()
        
        # User study metrics
        total_participants = UserStudyParticipant.objects.count()
        completed_studies = UserStudyParticipant.objects.filter(is_completed=True).count()
        
        # Fairness analysis
        latest_fairness = FairnessAnalysisResult.objects.first()
        
        avg_metrics = ImageUpload.objects.aggregate(
            avg_confidence=Avg('confidence'),
            avg_processing_time=Avg('processing_time')
        )
        
        extra_context['analytics'] = {
            'total_images': total_images,
            'total_predictions': total_predictions,
            'cancer_detections': cancer_detections,
            'suspected_cancer': suspected_cancer,
            'total_participants': total_participants,
            'completed_studies': completed_studies,
            'avg_confidence': (avg_metrics['avg_confidence'] or 0) * 100,
            'avg_processing_time': avg_metrics['avg_processing_time'] or 0,
            'latest_fairness': latest_fairness,
        }
        
        return super().index(request, extra_context)

class ImageUploadAdmin(admin.ModelAdmin):
    """Enhanced admin for Image Analysis Results & History"""
    
    list_display = [
        'id', 'display_filename', 'display_result', 'display_confidence',
        'display_processing_time', 'display_user', 'upload_timestamp', 'display_status'
    ]
    
    list_filter = [
        'result', 'prediction', 'status', 'upload_timestamp', 'model_used',
        'confidence', 'processing_time', 'is_user_study'
    ]
    
    search_fields = ['filename', 'user__username', 'prediction', 'result', 'recommendation']
    
    readonly_fields = [
        'upload_timestamp', 'display_result_badge', 'display_recommendation_summary'
    ]
    
    fieldsets = (
        ('Image Information', {
            'fields': ('image', 'filename', 'file_size', 'upload_timestamp')
        }),
        ('Analysis Results', {
            'fields': ('prediction', 'result', 'confidence', 'recommendation', 'display_result_badge')
        }),
        ('Processing Details', {
            'fields': ('model_used', 'model_version', 'processing_time', 'status', 'error_message')
        }),
        ('User Context', {
            'fields': ('user', 'session_id', 'is_user_study')
        }),
        ('Research Notes', {
            'fields': ('research_notes', 'display_recommendation_summary'),
            'classes': ('collapse',)
        }),
    )
    
    def display_filename(self, obj):
        return obj.filename[:30] + '...' if len(obj.filename) > 30 else obj.filename
    display_filename.short_description = '📁 Filename'
    
    def display_result(self, obj):
        colors = {
            'cancer': '#dc3545',
            'suspected_cancer': '#fd7e14',
            'no_cancer': '#28a745',
            'unknown': '#6c757d'
        }
        if obj.result:
            color = colors.get(obj.result, '#6c757d')
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                color, obj.get_result_display()
            )
        return obj.prediction.upper() if obj.prediction else '-'
    display_result.short_description = '🎯 Result'
    
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
        status_colors = {
            'completed': '#28a745',
            'error': '#dc3545',
            'processing': '#ffc107',
            'pending': '#6c757d',
            'reviewed': '#17a2b8'
        }
        color = status_colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="color: {};">● {}</span>',
            color, obj.get_status_display()
        )
    display_status.short_description = '🔄 Status'
    
    def display_result_badge(self, obj):
        if obj.result:
            colors = {
                'cancer': '#dc3545',
                'suspected_cancer': '#fd7e14',
                'no_cancer': '#28a745',
                'unknown': '#6c757d'
            }
            color = colors.get(obj.result, '#6c757d')
            confidence = obj.confidence * 100 if obj.confidence else 0
            return format_html(
                '<div style="background: {}; color: white; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold;">' +
                '{}<br><small>{}% Confidence</small></div>',
                color, obj.get_result_display(), '{:.1f}'.format(confidence)
            )
        return 'No result'
    display_result_badge.short_description = '🎯 Result Badge'
    
    def display_recommendation_summary(self, obj):
        if obj.recommendation:
            return format_html(
                '<div style="background: #e3f2fd; padding: 15px; border-radius: 8px; border-left: 4px solid #2196f3;">' +
                '<h4>🤖 AI Recommendation</h4>' +
                '<p>{}</p>' +
                '</div>',
                obj.recommendation[:200] + '...' if len(obj.recommendation) > 200 else obj.recommendation
            )
        return 'No recommendation provided'
    display_recommendation_summary.short_description = '💡 AI Recommendation'

class UserStudyParticipantAdmin(admin.ModelAdmin):
    """Admin for User Study Participants"""
    
    list_display = [
        'participant_id', 'display_completion_status', 'age_group', 'gender',
        'skin_type', 'medical_background', 'created_at', 'display_consent_status'
    ]
    
    list_filter = [
        'is_completed', 'age_group', 'gender', 'ethnicity', 'skin_type',
        'medical_background', 'ai_experience', 'created_at', 'research_consent_given'
    ]
    
    search_fields = ['participant_id', 'session_id']
    readonly_fields = ['participant_id', 'session_id', 'created_at']
    
    fieldsets = (
        ('Participant Information', {
            'fields': ('participant_id', 'session_id', 'created_at', 'completed_at', 'is_completed')
        }),
        ('Demographics', {
            'fields': ('age_group', 'gender', 'ethnicity', 'skin_type', 'education_level')
        }),
        ('Background', {
            'fields': ('medical_background', 'ai_experience')
        }),
        ('Consent & Ethics', {
            'fields': ('research_consent_given', 'consent_timestamp', 'consent_version', 'ethics_approval')
        }),
        ('Technical Details', {
            'fields': ('user_agent', 'ip_address', 'phases_completed'),
            'classes': ('collapse',)
        }),
    )
    
    def display_completion_status(self, obj):
        if obj.is_completed:
            return format_html('<span style="color: #28a745;">✅ Completed</span>')
        return format_html('<span style="color: #ffc107;">⏳ In Progress</span>')
    display_completion_status.short_description = '🔄 Status'
    
    def display_consent_status(self, obj):
        if obj.research_consent_given:
            return format_html('<span style="color: #28a745;">✅ Given</span>')
        return format_html('<span style="color: #dc3545;">❌ Pending</span>')
    display_consent_status.short_description = '📝 Consent'

class DemographicProfileAdmin(admin.ModelAdmin):
    """Admin for Demographic Profiles"""
    
    list_display = ['participant', 'occupation', 'location_country', 'has_skin_condition', 'smartphone_usage']
    list_filter = ['has_skin_condition', 'family_history_skin_cancer', 'smartphone_usage', 'health_app_usage']
    search_fields = ['participant__participant_id', 'occupation', 'location_country']

class UserStudyFeedbackAdmin(admin.ModelAdmin):
    """Admin for User Study Feedback"""
    
    list_display = [
        'participant', 'trust_rating', 'usability_rating', 'accuracy_perception',
        'fairness_rating', 'bias_perception', 'created_at'
    ]
    
    list_filter = [
        'trust_rating', 'usability_rating', 'accuracy_perception',
        'fairness_rating', 'bias_perception', 'created_at'
    ]
    
    search_fields = ['participant__participant_id', 'improvements', 'additional_comments']
    readonly_fields = ['created_at', 'updated_at']

class ImageFeedbackAdmin(admin.ModelAdmin):
    """Admin for Image-specific Feedback"""
    
    list_display = [
        'image_upload', 'participant', 'prediction_agreement',
        'confidence_rating', 'helpfulness_rating', 'timestamp'
    ]
    
    list_filter = [
        'prediction_agreement', 'confidence_rating', 'helpfulness_rating', 'timestamp'
    ]
    
    search_fields = ['image_upload__filename', 'participant__participant_id', 'specific_feedback']

class ResearchConsentAdmin(admin.ModelAdmin):
    """Admin for Research Consent tracking"""
    
    list_display = [
        'participant', 'consent_form_version', 'data_collection_consent',
        'data_analysis_consent', 'publication_consent', 'display_status'
    ]
    
    list_filter = [
        'data_collection_consent', 'data_analysis_consent', 'publication_consent',
        'consent_withdrawn', 'consent_given_at'
    ]
    
    search_fields = ['participant__participant_id', 'ethics_approval_number']
    
    def display_status(self, obj):
        if obj.consent_withdrawn:
            return format_html('<span style="color: #dc3545;">❌ Withdrawn</span>')
        return format_html('<span style="color: #28a745;">✅ Active</span>')
    display_status.short_description = '📋 Status'

class SystemFeedbackAdmin(admin.ModelAdmin):
    """Admin for System Feedback"""
    
    list_display = [
        'title', 'feedback_type', 'priority', 'user', 'status', 'created_at'
    ]
    
    list_filter = [
        'feedback_type', 'priority', 'status', 'created_at'
    ]
    
    search_fields = ['title', 'description', 'user__username']
    
    fieldsets = (
        ('Feedback Details', {
            'fields': ('title', 'feedback_type', 'priority', 'description')
        }),
        ('Technical Details', {
            'fields': ('steps_to_reproduce', 'expected_behavior', 'actual_behavior')
        }),
        ('System Information', {
            'fields': ('browser_info', 'device_info')
        }),
        ('Status Tracking', {
            'fields': ('status', 'admin_notes', 'resolved_at')
        }),
        ('Metadata', {
            'fields': ('user', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']

class UserStudySessionAdmin(admin.ModelAdmin):
    """Admin for User Study Sessions"""
    
    list_display = [
        'participant', 'session_type', 'session_start', 'duration_minutes',
        'images_analyzed', 'display_completion'
    ]
    
    list_filter = ['session_type', 'session_start']
    search_fields = ['participant__participant_id', 'notes']
    
    def display_completion(self, obj):
        if obj.session_end:
            return format_html('<span style="color: #28a745;">✅ Completed</span>')
        return format_html('<span style="color: #ffc107;">⏳ In Progress</span>')
    display_completion.short_description = '🔄 Status'

class FairnessAnalysisResultAdmin(admin.ModelAdmin):
    """Admin for Fairness Analysis Results"""
    
    list_display = [
        'analysis_date', 'dataset_used', 'overall_bias_level',
        'disparate_impact_ratio', 'equalized_odds_difference'
    ]
    
    list_filter = ['overall_bias_level', 'analysis_date', 'dataset_used']
    search_fields = ['dataset_used', 'mitigation_recommendations', 'analysis_notes']
    
    fieldsets = (
        ('Analysis Information', {
            'fields': ('analysis_date', 'dataset_used', 'model_version', 'overall_bias_level')
        }),
        ('Fairness Metrics', {
            'fields': ('disparate_impact_ratio', 'equalized_odds_difference', 
                      'demographic_parity_difference', 'individual_fairness_score')
        }),
        ('Detailed Results', {
            'fields': ('accuracy_by_skin_type', 'confidence_by_demographic', 'prediction_distribution')
        }),
        ('Recommendations', {
            'fields': ('mitigation_recommendations', 'analysis_notes')
        }),
        ('Raw Data', {
            'fields': ('raw_results',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['analysis_date']

# Create custom admin site
analytics_admin = AnalyticsAdminSite(name='analytics_admin')

# Register models with custom admin site
analytics_admin.register(ImageUpload, ImageUploadAdmin)
analytics_admin.register(UserStudyParticipant, UserStudyParticipantAdmin)
analytics_admin.register(DemographicProfile, DemographicProfileAdmin)
analytics_admin.register(UserStudyFeedback, UserStudyFeedbackAdmin)
analytics_admin.register(ImageFeedback, ImageFeedbackAdmin)
analytics_admin.register(ResearchConsent, ResearchConsentAdmin)
analytics_admin.register(SystemFeedback, SystemFeedbackAdmin)
analytics_admin.register(UserStudySession, UserStudySessionAdmin)
analytics_admin.register(FairnessAnalysisResult, FairnessAnalysisResultAdmin)
analytics_admin.register(User, CustomUserAdmin)

# Register with default admin site for compatibility
admin.site.register(ImageUpload, ImageUploadAdmin)
admin.site.register(UserStudyParticipant, UserStudyParticipantAdmin)
admin.site.register(DemographicProfile, DemographicProfileAdmin)
admin.site.register(UserStudyFeedback, UserStudyFeedbackAdmin)
admin.site.register(ImageFeedback, ImageFeedbackAdmin)
admin.site.register(ResearchConsent, ResearchConsentAdmin)
admin.site.register(SystemFeedback, SystemFeedbackAdmin)
admin.site.register(UserStudySession, UserStudySessionAdmin)
admin.site.register(FairnessAnalysisResult, FairnessAnalysisResultAdmin)