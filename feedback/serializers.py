from rest_framework import serializers
from .models import (
    DemographicProfile, 
    UserStudySession, 
    ImageFeedback, 
    SystemFeedback, 
    ResearchConsent,
    Feedback  # Keep the old model for backward compatibility
)


class FeedbackSerializer(serializers.ModelSerializer):
    """Legacy feedback serializer - kept for backward compatibility"""
    class Meta:
        model = Feedback
        fields = "__all__"


class DemographicProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemographicProfile
        fields = [
            'fitzpatrick_skin_type', 'age_group', 'gender', 'education_level',
            'has_skin_condition', 'previous_ai_experience', 'consent_for_research'
        ]


class UserStudySessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStudySession
        fields = ['session_id', 'started_at', 'completed_at', 'is_completed']
        read_only_fields = ['session_id', 'started_at']


class ImageFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageFeedback
        fields = [
            'image_upload', 'trust_in_prediction', 'confidence_in_system',
            'would_act_on_result', 'perceived_accuracy', 'noticed_bias',
            'bias_description', 'ease_of_use', 'interface_clarity',
            'additional_comments'
        ]


class SystemFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemFeedback
        fields = [
            'system_is_reliable', 'system_is_fair', 'system_respects_diversity',
            'would_recommend', 'works_equally_all_skin_tones', 'free_from_discrimination',
            'inclusive_design', 'trust_in_ai_diagnosis', 'trust_compared_to_doctor',
            'most_concerning_aspect', 'improvement_suggestions', 'overall_experience'
        ]


class ResearchConsentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearchConsent
        fields = [
            'consent_to_participate', 'consent_data_collection', 'consent_image_analysis',
            'consent_demographic_data', 'consent_feedback_publication',
            'data_retention_years', 'can_withdraw_consent'
        ]
