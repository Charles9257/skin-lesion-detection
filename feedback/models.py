from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


# New model for System Usability and Trust Survey (2025)
class UsabilityTrustSurvey(models.Model):
    """Detailed system usability and trust survey for qualitative analytics."""
    LIKERT_CHOICES = [
        (1, 'Strongly Disagree'),
        (2, 'Disagree'),
        (3, 'Neutral'),
        (4, 'Agree'),
        (5, 'Strongly Agree'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='usability_trust_surveys')
    submitted_at = models.DateTimeField(auto_now_add=True)

    # Likert-scale questions (1-11)
    q1_interface_intuitive = models.IntegerField(choices=LIKERT_CHOICES)
    q2_layout_design_clear = models.IntegerField(choices=LIKERT_CHOICES)
    q3_response_time_satisfactory = models.IntegerField(choices=LIKERT_CHOICES)
    q4_steps_understandable = models.IntegerField(choices=LIKERT_CHOICES)
    q5_results_clear = models.IntegerField(choices=LIKERT_CHOICES)
    q6_visual_explanations_helpful = models.IntegerField(choices=LIKERT_CHOICES)
    q7_fairness_metrics_understandable = models.IntegerField(choices=LIKERT_CHOICES)
    q8_fair_predictions = models.IntegerField(choices=LIKERT_CHOICES)
    q9_info_and_control_sufficient = models.IntegerField(choices=LIKERT_CHOICES)
    q10_overall_satisfaction = models.IntegerField(choices=LIKERT_CHOICES)
    q11_recommend_system = models.IntegerField(choices=LIKERT_CHOICES)

    # Optional short answer questions
    most_helpful_feature = models.TextField(blank=True)
    improvement_suggestion = models.TextField(blank=True)
    noticed_limitations = models.TextField(blank=True)

    def __str__(self):
        return f"UsabilityTrustSurvey by {self.user.username} at {self.submitted_at}"  


class Feedback(models.Model):
    """Legacy feedback model - kept for backward compatibility"""
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback {self.id} - Rating: {self.rating}"


class DemographicProfile(models.Model):
    """User demographic information for research purposes"""
    
    SKIN_TONE_CHOICES = [
        ('I', 'Type I - Very fair (always burns, never tans)'),
        ('II', 'Type II - Fair (usually burns, tans minimally)'),
        ('III', 'Type III - Medium (sometimes burns, tans gradually)'),
        ('IV', 'Type IV - Olive (rarely burns, tans well)'),
        ('V', 'Type V - Brown (very rarely burns, tans very easily)'),
        ('VI', 'Type VI - Dark brown/Black (never burns, tans very easily)'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ]
    
    AGE_GROUPS = [
        ('18-25', '18-25'),
        ('26-35', '26-35'),
        ('36-45', '36-45'),
        ('46-55', '46-55'),
        ('56-65', '56-65'),
        ('65+', '65+'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ]
    
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('non_binary', 'Non-binary'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ]
    
    EDUCATION_CHOICES = [
        ('high_school', 'High school or equivalent'),
        ('bachelors', "Bachelor's degree"),
        ('masters', "Master's degree"),
        ('phd', 'PhD or equivalent'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='demographic_profile')
    fitzpatrick_skin_type = models.CharField(max_length=20, choices=SKIN_TONE_CHOICES, blank=True)
    age_group = models.CharField(max_length=20, choices=AGE_GROUPS, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True)
    education_level = models.CharField(max_length=20, choices=EDUCATION_CHOICES, blank=True)
    has_skin_condition = models.BooleanField(default=False, help_text="Do you have any known skin conditions?")
    previous_ai_experience = models.BooleanField(default=False, help_text="Have you used AI-based diagnostic tools before?")
    consent_for_research = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Demographics for {self.user.username}"


class UserStudySession(models.Model):
    """Track user study sessions for research"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_sessions')
    session_id = models.CharField(max_length=100, unique=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Study session {self.session_id} for {self.user.username}"


class ImageFeedback(models.Model):
    """Feedback specific to image uploads and predictions"""
    
    TRUST_LEVELS = [
        (1, 'Not at all trustworthy'),
        (2, 'Slightly trustworthy'),
        (3, 'Moderately trustworthy'),
        (4, 'Very trustworthy'),
        (5, 'Extremely trustworthy'),
    ]
    
    CONFIDENCE_LEVELS = [
        (1, 'Not confident at all'),
        (2, 'Slightly confident'),
        (3, 'Moderately confident'),
        (4, 'Very confident'),
        (5, 'Extremely confident'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='image_feedback')
    study_session = models.ForeignKey(UserStudySession, on_delete=models.CASCADE, related_name='image_feedback')
    image_upload = models.ForeignKey('api.ImageUpload', on_delete=models.CASCADE, related_name='feedback')
    
    # Trust and confidence ratings
    trust_in_prediction = models.IntegerField(choices=TRUST_LEVELS)
    confidence_in_system = models.IntegerField(choices=CONFIDENCE_LEVELS)
    would_act_on_result = models.BooleanField(help_text="Would you act on this prediction?")
    
    # Perceived accuracy and bias
    perceived_accuracy = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rate the perceived accuracy (1-5)"
    )
    noticed_bias = models.BooleanField(default=False, help_text="Did you notice any bias in the result?")
    bias_description = models.TextField(blank=True, help_text="Describe any bias you noticed")
    
    # User experience
    ease_of_use = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="How easy was it to use the system? (1-5)"
    )
    interface_clarity = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="How clear was the interface? (1-5)"
    )
    
    # Additional comments
    additional_comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Image feedback from {self.user.username}"


class SystemFeedback(models.Model):
    """Overall system feedback and evaluation"""
    
    LIKERT_CHOICES = [
        (1, 'Strongly disagree'),
        (2, 'Disagree'),
        (3, 'Neutral'),
        (4, 'Agree'),
        (5, 'Strongly agree'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='system_feedback')
    study_session = models.ForeignKey(UserStudySession, on_delete=models.CASCADE, related_name='system_feedback')
    
    # System trust and reliability
    system_is_reliable = models.IntegerField(choices=LIKERT_CHOICES)
    system_is_fair = models.IntegerField(choices=LIKERT_CHOICES)
    system_respects_diversity = models.IntegerField(choices=LIKERT_CHOICES)
    would_recommend = models.IntegerField(choices=LIKERT_CHOICES)
    
    # Bias perception questions
    works_equally_all_skin_tones = models.IntegerField(
        choices=LIKERT_CHOICES,
        help_text="The system works equally well for all skin tones"
    )
    free_from_discrimination = models.IntegerField(
        choices=LIKERT_CHOICES,
        help_text="The system is free from discrimination"
    )
    inclusive_design = models.IntegerField(
        choices=LIKERT_CHOICES,
        help_text="The system has an inclusive design"
    )
    
    # Trust factors
    trust_in_ai_diagnosis = models.IntegerField(
        choices=LIKERT_CHOICES,
        help_text="I trust AI-based diagnosis tools"
    )
    trust_compared_to_doctor = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Trust level compared to human doctor (1=much less, 5=much more)"
    )
    
    # Open-ended questions
    most_concerning_aspect = models.TextField(
        blank=True,
        help_text="What concerns you most about AI-based skin diagnosis?"
    )
    improvement_suggestions = models.TextField(
        blank=True,
        help_text="How could this system be improved?"
    )
    overall_experience = models.TextField(
        blank=True,
        help_text="Describe your overall experience"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"System feedback from {self.user.username}"


class ResearchConsent(models.Model):
    """Track research consent and data usage permissions"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='research_consent')
    
    # Consent items
    consent_to_participate = models.BooleanField(default=False)
    consent_data_collection = models.BooleanField(default=False)
    consent_image_analysis = models.BooleanField(default=False)
    consent_demographic_data = models.BooleanField(default=False)
    consent_feedback_publication = models.BooleanField(default=False)
    
    # Data retention
    data_retention_years = models.IntegerField(default=5)
    can_withdraw_consent = models.BooleanField(default=True)
    
    # Timestamps
    consented_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    withdrawn_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Research consent for {self.user.username}"
