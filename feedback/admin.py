from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Avg, Count
from .models import (
    Feedback, DemographicProfile, UserStudySession,
    ImageFeedback, SystemFeedback, ResearchConsent
)


class FeedbackAdmin(admin.ModelAdmin):
    """Admin for Legacy Feedback"""
    
    list_display = ['id', 'display_rating', 'display_comments_preview', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['comments']
    
    def display_rating(self, obj):
        stars = '⭐' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span title="{}/5 stars">{}</span>', obj.rating, stars)
    display_rating.short_description = '⭐ Rating'
    
    def display_comments_preview(self, obj):
        if obj.comments:
            preview = obj.comments[:50] + '...' if len(obj.comments) > 50 else obj.comments
            return preview
        return 'No comments'
    display_comments_preview.short_description = '💬 Comments'


class DemographicProfileAdmin(admin.ModelAdmin):
    """Admin for Demographic Profiles"""
    
    list_display = [
        'user', 'fitzpatrick_skin_type', 'age_group', 'gender',
        'education_level', 'has_skin_condition', 'previous_ai_experience'
    ]
    
    list_filter = [
        'fitzpatrick_skin_type', 'age_group', 'gender', 'education_level',
        'has_skin_condition', 'previous_ai_experience', 'consent_for_research'
    ]
    
    search_fields = ['user__username', 'user__email']


class UserStudySessionAdmin(admin.ModelAdmin):
    """Admin for User Study Sessions"""
    
    list_display = [
        'session_id', 'user', 'display_status', 'started_at', 'display_duration'
    ]
    
    list_filter = ['is_completed', 'started_at']
    search_fields = ['session_id', 'user__username']
    
    readonly_fields = ['display_session_analytics']
    
    def display_status(self, obj):
        if obj.is_completed:
            return format_html('<span style="color: #28a745;">✅ Completed</span>')
        return format_html('<span style="color: #ffc107;">⏳ Active</span>')
    display_status.short_description = '🔄 Status'
    
    def display_duration(self, obj):
        if obj.completed_at and obj.started_at:
            duration = obj.completed_at - obj.started_at
            return f"{duration.total_seconds() / 60:.1f} min"
        return 'Ongoing'
    display_duration.short_description = '⏱️ Duration'
    
    def display_session_analytics(self, obj):
        feedback_count = obj.image_feedback.count()
        system_feedback_count = obj.system_feedback.count()
        
        return format_html(
            '<div style="background: #f0f8ff; padding: 15px; border-radius: 8px;">' +
            '<h4>📊 Session Analytics</h4>' +
            '<p><strong>💬 Image Feedback Count:</strong> {}</p>' +
            '<p><strong>🔧 System Feedback Count:</strong> {}</p>' +
            '<p><strong>⏱️ Session Duration:</strong> {}</p>' +
            '</div>',
            feedback_count, system_feedback_count, self.display_duration(obj)
        )
    display_session_analytics.short_description = '📊 Session Analytics'


class ImageFeedbackAdmin(admin.ModelAdmin):
    """Admin for Image-specific Feedback"""
    
    list_display = [
        'user', 'display_image_upload', 'trust_in_prediction', 'confidence_in_system',
        'would_act_on_result', 'noticed_bias', 'created_at'
    ]
    
    list_filter = [
        'trust_in_prediction', 'confidence_in_system', 'would_act_on_result',
        'noticed_bias', 'perceived_accuracy', 'created_at'
    ]
    
    search_fields = ['user__username', 'image_upload__filename']
    
    def display_image_upload(self, obj):
        if obj.image_upload:
            return f"{obj.image_upload.filename} ({obj.image_upload.prediction})"
        return '-'
    display_image_upload.short_description = '🖼️ Image & Prediction'


class SystemFeedbackAdmin(admin.ModelAdmin):
    """Admin for System-wide Feedback"""
    
    list_display = [
        'user', 'system_is_reliable', 'system_is_fair', 'would_recommend',
        'trust_in_ai_diagnosis', 'created_at'
    ]
    
    list_filter = [
        'system_is_reliable', 'system_is_fair', 'system_respects_diversity',
        'would_recommend', 'trust_in_ai_diagnosis', 'created_at'
    ]
    
    search_fields = ['user__username']
    
    readonly_fields = ['display_feedback_summary']
    
    def display_feedback_summary(self, obj):
        return format_html(
            '<div style="background: #fff3cd; padding: 15px; border-radius: 8px;">' +
            '<h4>💬 Feedback Summary</h4>' +
            '<p><strong>🔧 Reliability:</strong> {}/5</p>' +
            '<p><strong>⚖️ Fairness:</strong> {}/5</p>' +
            '<p><strong>🌍 Diversity Respect:</strong> {}/5</p>' +
            '<p><strong>👍 Would Recommend:</strong> {}/5</p>' +
            '</div>',
            obj.system_is_reliable, obj.system_is_fair,
            obj.system_respects_diversity, obj.would_recommend
        )
    display_feedback_summary.short_description = '💬 Feedback Summary'


class ResearchConsentAdmin(admin.ModelAdmin):
    """Admin for Research Consent Tracking"""
    
    list_display = [
        'user', 'display_consent_status', 'consented_at', 'data_retention_years'
    ]
    
    list_filter = [
        'consent_to_participate', 'consent_data_collection',
        'consent_image_analysis', 'consented_at'
    ]
    
    search_fields = ['user__username']
    
    def display_consent_status(self, obj):
        if obj.consent_to_participate:
            return format_html('<span style="color: #28a745;">✅ Consented</span>')
        return format_html('<span style="color: #dc3545;">❌ Not Consented</span>')
    display_consent_status.short_description = '✅ Consent Status'


# Register models manually to avoid conflicts
try:
    admin.site.register(Feedback, FeedbackAdmin)
except admin.sites.AlreadyRegistered:
    pass

try:
    admin.site.register(DemographicProfile, DemographicProfileAdmin)
except admin.sites.AlreadyRegistered:
    pass

try:
    admin.site.register(UserStudySession, UserStudySessionAdmin)
except admin.sites.AlreadyRegistered:
    pass

try:
    admin.site.register(ImageFeedback, ImageFeedbackAdmin)
except admin.sites.AlreadyRegistered:
    pass

try:
    admin.site.register(SystemFeedback, SystemFeedbackAdmin)
except admin.sites.AlreadyRegistered:
    pass

try:
    admin.site.register(ResearchConsent, ResearchConsentAdmin)
except admin.sites.AlreadyRegistered:
    pass

# Custom admin site configuration
admin.site.site_header = '🩺 Skin Lesion AI - Admin Dashboard'
admin.site.site_title = 'Skin Lesion AI Admin'
admin.site.index_title = '📊 Analytics & Management Dashboard'
