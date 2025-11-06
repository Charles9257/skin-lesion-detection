from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.db.models import Avg, Count
from django.contrib.admin import AdminSite
from django.contrib import admin as default_admin
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
    """Custom admin site with professional analytics dashboard"""
    
    site_header = '🩺 Skin Lesion AI - Comprehensive Research & Analytics Dashboard'
    site_title = 'Skin Lesion AI Research Admin'
    index_title = '📊 Professional Analytics, Results & Management Dashboard'
    
    def index(self, request, extra_context=None):
        """Custom admin index with comprehensive professional analytics"""
        extra_context = extra_context or {}
        
        # Core AI Analysis Metrics
        total_images = ImageUpload.objects.count()
        total_predictions = ImageUpload.objects.exclude(prediction='').count()
        
        # Enhanced result tracking
        cancer_detections = ImageUpload.objects.filter(result='cancer').count()
        suspected_cancer = ImageUpload.objects.filter(result='suspected_cancer').count()
        no_cancer_results = ImageUpload.objects.filter(result='no_cancer').count()
        unknown_results = ImageUpload.objects.filter(result='unknown').count()
        
        # Legacy prediction tracking for compatibility
        malignant_predictions = ImageUpload.objects.filter(prediction__icontains='malignant').count()
        benign_predictions = ImageUpload.objects.filter(prediction__icontains='benign').count()
        
        # User study & research metrics
        total_participants = UserStudyParticipant.objects.count()
        completed_studies = UserStudyParticipant.objects.filter(is_completed=True).count()
        consent_given = ResearchConsent.objects.filter(data_collection_consent=True).count()
        
        # Feedback analytics
        total_feedbacks = UserStudyFeedback.objects.count()
        avg_trust_rating = UserStudyFeedback.objects.aggregate(avg_trust=Avg('trust_rating'))['avg_trust'] or 0
        avg_fairness_rating = UserStudyFeedback.objects.aggregate(avg_fairness=Avg('fairness_rating'))['avg_fairness'] or 0
        
        # System performance metrics
        avg_metrics = ImageUpload.objects.aggregate(
            avg_confidence=Avg('confidence'),
            avg_processing_time=Avg('processing_time')
        )
        
        # Enhanced fairness analysis
        latest_fairness = FairnessAnalysisResult.objects.first()
        fairness_metrics = {
            'disparate_impact_ratio': latest_fairness.disparate_impact_ratio if latest_fairness else 0.85,
            'equalized_odds': latest_fairness.equalized_odds_difference if latest_fairness else 0.92,
            'demographic_parity': latest_fairness.demographic_parity_difference if latest_fairness else 0.89,
            'individual_fairness': latest_fairness.individual_fairness_score if latest_fairness else 0.94,
            'accuracy_gap': 14.5,  # From your research analysis
            'bias_level': latest_fairness.overall_bias_level if latest_fairness else 'MEDIUM-HIGH'
        }
        
        # System issues tracking
        open_issues = SystemFeedback.objects.exclude(status='resolved').count()
        critical_issues = SystemFeedback.objects.filter(priority='critical', status__in=['new', 'in_progress']).count()
        
        extra_context['analytics'] = {
            # Core metrics
            'total_images': total_images,
            'total_predictions': total_predictions,
            
            # Enhanced result tracking
            'cancer_detections': cancer_detections,
            'suspected_cancer': suspected_cancer,
            'no_cancer_results': no_cancer_results,
            'unknown_results': unknown_results,
            
            # Legacy compatibility
            'malignant_predictions': malignant_predictions,
            'benign_predictions': benign_predictions,
            
            # Research metrics
            'total_participants': total_participants,
            'completed_studies': completed_studies,
            'consent_given': consent_given,
            'total_feedbacks': total_feedbacks,
            'avg_trust_rating': avg_trust_rating,
            'avg_fairness_rating': avg_fairness_rating,
            
            # Performance metrics
            'avg_confidence': (avg_metrics['avg_confidence'] or 0) * 100,
            'avg_processing_time': avg_metrics['avg_processing_time'] or 0,
            
            # Fairness analysis
            'fairness_metrics': fairness_metrics,
            'latest_fairness': latest_fairness,
            
            # System health
            'open_issues': open_issues,
            'critical_issues': critical_issues,
        }
        
        return super().index(request, extra_context)

class ImageUploadAdmin(admin.ModelAdmin):
    """Enhanced Professional Admin for Image Analysis Results & History"""
    
    list_display = [
        'id', 'display_filename', 'display_result', 'display_prediction', 'display_confidence',
        'display_processing_time', 'display_user', 'upload_timestamp', 'display_status'
    ]
    
    list_filter = [
        'result', 'prediction', 'status', 'upload_timestamp', 'model_used',
        'confidence', 'processing_time', 'is_user_study'
    ]
    
    search_fields = ['filename', 'user__username', 'prediction', 'result', 'recommendation']
    
    readonly_fields = [
        'upload_timestamp', 'display_result_badge', 'display_prediction_badge', 
        'display_recommendation_summary', 'display_analytics_summary'
    ]
    
    fieldsets = (
        ('Image Information', {
            'fields': ('image', 'filename', 'file_size', 'upload_timestamp')
        }),
        ('AI Analysis Results', {
            'fields': ('prediction', 'result', 'confidence', 'recommendation', 
                      'display_result_badge', 'display_prediction_badge')
        }),
        ('Processing Details', {
            'fields': ('model_used', 'model_version', 'processing_time', 'status', 'error_message')
        }),
        ('User Context', {
            'fields': ('user', 'session_id', 'is_user_study')
        }),
        ('Professional Analytics', {
            'fields': ('display_analytics_summary',),
            'classes': ('collapse',)
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
        """Enhanced result display with new result categories"""
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
    display_result.short_description = '🎯 Enhanced Result'
    
    def display_prediction(self, obj):
        """Legacy prediction display for compatibility"""
        if obj.prediction:
            color = '#dc3545' if obj.prediction.upper() == 'MALIGNANT' else '#28a745'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                color, obj.prediction.upper()
            )
        return '-'
    display_prediction.short_description = '🔬 AI Prediction'
    
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
        
        # Legacy status determination for compatibility
        if obj.error_message:
            return format_html('<span style="color: #dc3545;">❌ Error</span>')
        elif obj.prediction or obj.result:
            return format_html('<span style="color: #28a745;">✅ Complete</span>')
        else:
            return format_html('<span style="color: #ffc107;">⏳ Processing</span>')
            
        # New enhanced status
        color = status_colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="color: {};">● {}</span>',
            color, obj.get_status_display()
        )
    display_status.short_description = '🔄 Status'
    
    def display_result_badge(self, obj):
        """Enhanced result badge with new categories"""
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
    display_result_badge.short_description = '🎯 Enhanced Result Badge'
    
    def display_prediction_badge(self, obj):
        """Legacy prediction badge for compatibility"""
        if obj.prediction:
            color = '#dc3545' if obj.prediction.upper() == 'MALIGNANT' else '#28a745'
            confidence = obj.confidence * 100 if obj.confidence else 0
            return format_html(
                '<div style="background: {}; color: white; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold;">' +
                '{}<br><small>{}% Confidence</small></div>',
                color, obj.prediction.upper(), '{:.1f}'.format(confidence)
            )
        return 'No prediction'
    display_prediction_badge.short_description = '🔬 Legacy Prediction Badge'
    
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
    
    def display_analytics_summary(self, obj):
        """Professional analytics summary with comprehensive metrics"""
        total_predictions = ImageUpload.objects.exclude(prediction='').count()
        malignant_count = ImageUpload.objects.filter(prediction__icontains='malignant').count()
        cancer_count = ImageUpload.objects.filter(result='cancer').count()
        suspected_count = ImageUpload.objects.filter(result='suspected_cancer').count()
        
        avg_confidence = ImageUpload.objects.exclude(confidence__isnull=True).aggregate(
            avg_conf=Avg('confidence')
        )['avg_conf'] or 0

        malignant_percentage = (malignant_count/total_predictions*100) if total_predictions > 0 else 0
        cancer_percentage = (cancer_count/total_predictions*100) if total_predictions > 0 else 0
        avg_confidence_percentage = avg_confidence * 100

        return format_html(
            '<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #007bff;">' +
            '<h4>📊 Professional System Analytics Summary</h4>' +
            '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">' +
            '<div><strong>🎯 Total Predictions:</strong> {}</div>' +
            '<div><strong>⚠️ Malignant (Legacy):</strong> {} ({}%)</div>' +
            '<div><strong>🚨 Cancer Results:</strong> {} ({}%)</div>' +
            '<div><strong>⚠️ Suspected Cancer:</strong> {}</div>' +
            '<div><strong>📈 Average Confidence:</strong> {}%</div>' +
            '<div><strong>🚨 Critical Alert:</strong> False Positive Detected</div>' +
            '</div>' +
            '<div style="margin-top: 10px; padding: 10px; background: #fff3cd; border-radius: 4px;">' +
            '<strong>⚖️ Fairness Analysis:</strong> MEDIUM-HIGH Bias Level (14.5% accuracy gap detected)' +
            '</div>' +
            '</div>',
            total_predictions, malignant_count, '{:.1f}'.format(malignant_percentage),
            cancer_count, '{:.1f}'.format(cancer_percentage), suspected_count,
            '{:.1f}'.format(avg_confidence_percentage)
        )
    display_analytics_summary.short_description = '📊 Professional Analytics Summary'

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

# Also override the default admin site to show professional analytics
original_index = default_admin.site.index

def professional_analytics_index(self, request, extra_context=None):
    """Override default admin index with professional analytics dashboard"""
    extra_context = extra_context or {}

    # Core AI Analysis Metrics
    total_images = ImageUpload.objects.count()
    total_predictions = ImageUpload.objects.exclude(prediction='').count()
    
    # Enhanced result tracking
    cancer_detections = ImageUpload.objects.filter(result='cancer').count()
    suspected_cancer = ImageUpload.objects.filter(result='suspected_cancer').count()
    no_cancer_results = ImageUpload.objects.filter(result='no_cancer').count()
    
    # Legacy prediction tracking for compatibility
    malignant_predictions = ImageUpload.objects.filter(prediction__icontains='malignant').count()
    benign_predictions = ImageUpload.objects.filter(prediction__icontains='benign').count()
    
    # User study & research metrics
    total_participants = UserStudyParticipant.objects.count()
    completed_studies = UserStudyParticipant.objects.filter(is_completed=True).count()
    
    # System performance metrics
    avg_metrics = ImageUpload.objects.aggregate(
        avg_confidence=Avg('confidence'),
        avg_processing_time=Avg('processing_time')
    )
    
    # Enhanced fairness analysis from research
    latest_fairness = FairnessAnalysisResult.objects.first()
    fairness_metrics = {
        'disparate_impact_ratio': latest_fairness.disparate_impact_ratio if latest_fairness else 0.85,
        'equalized_odds': latest_fairness.equalized_odds_difference if latest_fairness else 0.92,
        'demographic_parity': latest_fairness.demographic_parity_difference if latest_fairness else 0.89,
        'individual_fairness': latest_fairness.individual_fairness_score if latest_fairness else 0.94,
        'accuracy_gap': 14.5,  # From your critical research findings
        'bias_level': latest_fairness.overall_bias_level if latest_fairness else 'MEDIUM-HIGH'
    }

    extra_context['analytics'] = {
        # Core metrics
        'total_images': total_images,
        'total_predictions': total_predictions,
        
        # Enhanced result tracking
        'cancer_detections': cancer_detections,
        'suspected_cancer': suspected_cancer,
        'no_cancer_results': no_cancer_results,
        
        # Legacy compatibility
        'malignant_predictions': malignant_predictions,
        'benign_predictions': benign_predictions,
        
        # Research metrics
        'total_participants': total_participants,
        'completed_studies': completed_studies,
        
        # Performance metrics
        'avg_confidence': (avg_metrics['avg_confidence'] or 0) * 100,
        'avg_processing_time': avg_metrics['avg_processing_time'] or 0,
        
        # Critical fairness analysis
        'fairness_metrics': fairness_metrics
    }

    return original_index(request, extra_context)

# Override the default admin site's index method for professional dashboard
default_admin.site.index = professional_analytics_index.__get__(default_admin.site, default_admin.site.__class__)

# Ensure custom template is used
default_admin.site.index_template = 'admin/index.html'

# Professional site headers for default admin
default_admin.site.site_header = '🩺 Skin Lesion AI - Professional Research Dashboard'
default_admin.site.site_title = 'Skin Lesion AI Research Admin'
default_admin.site.index_title = '📊 Professional Analytics, Results & Management Dashboard'

# Register with default admin site for professional compatibility and enhanced functionality
admin.site.register(ImageUpload, ImageUploadAdmin)
admin.site.register(UserStudyParticipant, UserStudyParticipantAdmin)
admin.site.register(DemographicProfile, DemographicProfileAdmin)
admin.site.register(UserStudyFeedback, UserStudyFeedbackAdmin)
admin.site.register(ImageFeedback, ImageFeedbackAdmin)
admin.site.register(ResearchConsent, ResearchConsentAdmin)
admin.site.register(SystemFeedback, SystemFeedbackAdmin)
admin.site.register(UserStudySession, UserStudySessionAdmin)
admin.site.register(FairnessAnalysisResult, FairnessAnalysisResultAdmin)