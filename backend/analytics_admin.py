from django.contrib import admin
from django.contrib.admin import AdminSite
from django.shortcuts import render
from django.db.models import Avg, Count, Q
from django.utils.html import format_html
from api.models import ImageUpload, UserStudyParticipant, UserStudyFeedback, UserStudyAnalysis
from feedback.models import (
    Feedback, DemographicProfile, UserStudySession, 
    ImageFeedback, SystemFeedback, ResearchConsent
)


class AnalyticsAdminSite(AdminSite):
    """Custom admin site with analytics dashboard"""
    
    site_header = '🩺 Skin Lesion AI - Analytics Dashboard'
    site_title = 'Skin Lesion AI Admin'
    index_title = '📊 Comprehensive Analytics & Management Dashboard'
    
    def index(self, request, extra_context=None):
        """Custom admin index with comprehensive analytics"""
        extra_context = extra_context or {}
        
        # AI Analysis Results Analytics
        total_images = ImageUpload.objects.count()
        total_predictions = ImageUpload.objects.exclude(prediction='').count()
        malignant_predictions = ImageUpload.objects.filter(prediction__icontains='malignant').count()
        benign_predictions = ImageUpload.objects.filter(prediction__icontains='benign').count()
        
        # Average metrics
        avg_metrics = ImageUpload.objects.aggregate(
            avg_confidence=Avg('confidence'),
            avg_processing_time=Avg('processing_time')
        )
        
        # User Study Analytics
        total_participants = UserStudyParticipant.objects.count()
        completed_studies = UserStudyParticipant.objects.filter(is_completed=True).count()
        total_feedback = SystemFeedback.objects.count()
        total_image_feedback = ImageFeedback.objects.count()
        
        # Research Consent Analytics
        consented_users = ResearchConsent.objects.filter(consent_to_participate=True).count()
        
        # Demographic Analytics
        demographic_breakdown = DemographicProfile.objects.values('fitzpatrick_skin_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Critical Bias Metrics (from your analysis)
        fairness_metrics = {
            'disparate_impact_ratio': 0.85,
            'equalized_odds': 0.92,
            'demographic_parity': 0.89,
            'individual_fairness': 0.94,
            'accuracy_gap': 14.5,
            'bias_level': 'MEDIUM-HIGH'
        }
        
        # False Positive Analysis
        false_positive_analysis = {
            'nevus_misclassified': 'ISIC_0000008.jpg',
            'confidence_overconfidence': 100.0,
            'expected_prediction': 'BENIGN',
            'actual_prediction': 'MALIGNANT',
            'clinical_impact': 'HIGH RISK'
        }
        
        extra_context.update({
            'analytics': {
                'total_images': total_images,
                'total_predictions': total_predictions,
                'malignant_predictions': malignant_predictions,
                'benign_predictions': benign_predictions,
                'avg_confidence': (avg_metrics['avg_confidence'] or 0) * 100,
                'avg_processing_time': avg_metrics['avg_processing_time'] or 0,
                'fairness_metrics': fairness_metrics,
                'false_positive_analysis': false_positive_analysis
            },
            'user_study_analytics': {
                'total_participants': total_participants,
                'completed_studies': completed_studies,
                'completion_rate': (completed_studies / total_participants * 100) if total_participants > 0 else 0,
                'total_feedback': total_feedback,
                'total_image_feedback': total_image_feedback,
                'consented_users': consented_users
            },
            'demographic_breakdown': demographic_breakdown,
            'bias_alert': {
                'level': 'CRITICAL',
                'accuracy_gap': 14.5,
                'false_positive_detected': True,
                'action_required': True
            }
        })
        
        return super().index(request, extra_context)


# Create custom admin site instance
analytics_admin_site = AnalyticsAdminSite(name='analytics_admin')

# Register all models with the custom admin site
from api.admin import (
    ImageUploadAdmin, UserStudyParticipantAdmin
)
from feedback.admin import (
    FeedbackAdmin, DemographicProfileAdmin, ImageFeedbackAdmin,
    SystemFeedbackAdmin, UserStudySessionAdmin, ResearchConsentAdmin
)

# Register models with the custom admin site
analytics_admin_site.register(ImageUpload, ImageUploadAdmin)
analytics_admin_site.register(UserStudyParticipant, UserStudyParticipantAdmin)
analytics_admin_site.register(DemographicProfile, DemographicProfileAdmin)
analytics_admin_site.register(ImageFeedback, ImageFeedbackAdmin)
analytics_admin_site.register(SystemFeedback, SystemFeedbackAdmin)
analytics_admin_site.register(UserStudySession, UserStudySessionAdmin)
analytics_admin_site.register(ResearchConsent, ResearchConsentAdmin)
analytics_admin_site.register(Feedback, FeedbackAdmin)

# Also register with default admin site for compatibility
admin.site.register(ImageUpload, ImageUploadAdmin)
admin.site.register(UserStudyParticipant, UserStudyParticipantAdmin)