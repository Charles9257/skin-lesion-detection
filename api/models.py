from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
import uuid
import time
from django.utils import timezone

class ImageUpload(models.Model):
    """Enhanced model for storing uploaded skin lesion images and AI predictions"""
    
    # Image information
    image = models.ImageField(upload_to='uploads/', null=True, blank=True)
    filename = models.CharField(max_length=255, blank=True)
    file_size = models.IntegerField(null=True, blank=True)
    upload_timestamp = models.DateTimeField(auto_now_add=True)
    
    # Enhanced AI prediction results
    prediction = models.CharField(max_length=50, blank=True)  # 'malignant' or 'benign'
    confidence = models.FloatField(null=True, blank=True)  # 0.0 to 1.0
    
    # New result classification
    RESULT_CHOICES = [
        ('cancer', 'Cancer Detected'),
        ('no_cancer', 'No Cancer'),
        ('suspected_cancer', 'Suspected Cancer'),
        ('unknown', 'Unknown/Unclear'),
    ]
    result = models.CharField(max_length=20, choices=RESULT_CHOICES, blank=True)
    
    # AI recommendation
    recommendation = models.TextField(blank=True, help_text="AI-generated recommendation for user")
    
    # Model information
    model_used = models.CharField(max_length=100, blank=True)
    model_version = models.CharField(max_length=50, blank=True)
    
    # Processing metadata
    processing_time = models.FloatField(null=True, blank=True)  # seconds
    error_message = models.TextField(blank=True)
    
    # Enhanced status tracking
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('error', 'Error'),
        ('reviewed', 'Reviewed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # User context (optional)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    
    # Research tracking
    is_user_study = models.BooleanField(default=False)
    research_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-upload_timestamp']
        verbose_name = "Image Analysis Result"
        verbose_name_plural = "Image Analysis Results & History"
    
    def __str__(self):
        return f"{self.filename} - {self.result or self.prediction} ({self.confidence:.2f})" if self.confidence else self.filename

class UserStudyParticipant(models.Model):
    """Enhanced model for storing user study participant data"""
    
    # Unique identifiers
    participant_id = models.CharField(max_length=50, unique=True)
    session_id = models.UUIDField(default=uuid.uuid4, unique=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Consent information
    consent_timestamp = models.DateTimeField(null=True, blank=True)
    consent_version = models.CharField(max_length=20, default='1.0')
    ethics_approval = models.CharField(max_length=50, default='BUIRB-2025-001')
    research_consent_given = models.BooleanField(default=False)
    
    # Demographics
    age_group = models.CharField(max_length=20, blank=True, choices=[
        ('18-25', '18-25 years'),
        ('26-35', '26-35 years'),
        ('36-45', '36-45 years'),
        ('46-55', '46-55 years'),
        ('56-65', '56-65 years'),
        ('65+', '65+ years'),
        ('prefer-not-to-say', 'Prefer not to say'),
    ])
    
    gender = models.CharField(max_length=20, blank=True, choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('non-binary', 'Non-binary'),
        ('other', 'Other'),
        ('prefer-not-to-say', 'Prefer not to say'),
    ])
    
    ethnicity = models.CharField(max_length=30, blank=True, choices=[
        ('white', 'White/Caucasian'),
        ('black', 'Black/African American'),
        ('hispanic', 'Hispanic/Latino'),
        ('asian', 'Asian'),
        ('native-american', 'Native American'),
        ('middle-eastern', 'Middle Eastern'),
        ('mixed', 'Mixed/Multiracial'),
        ('other', 'Other'),
        ('prefer-not-to-say', 'Prefer not to say'),
    ])
    
    skin_type = models.CharField(max_length=20, blank=True, choices=[
        ('type-1', 'Type I - Very fair, always burns'),
        ('type-2', 'Type II - Fair, usually burns'),
        ('type-3', 'Type III - Medium, sometimes burns'),
        ('type-4', 'Type IV - Olive, rarely burns'),
        ('type-5', 'Type V - Brown, very rarely burns'),
        ('type-6', 'Type VI - Dark brown/black, never burns'),
        ('unsure', 'Unsure'),
    ])
    
    education_level = models.CharField(max_length=20, blank=True, choices=[
        ('high-school', 'High school or equivalent'),
        ('some-college', 'Some college'),
        ('bachelors', 'Bachelor\'s degree'),
        ('masters', 'Master\'s degree'),
        ('doctorate', 'Doctorate/PhD'),
        ('professional', 'Professional degree'),
        ('other', 'Other'),
    ])
    
    medical_background = models.CharField(max_length=20, blank=True, choices=[
        ('none', 'No medical background'),
        ('student', 'Medical student'),
        ('nurse', 'Nurse/Nursing'),
        ('doctor', 'Physician/Doctor'),
        ('dermatologist', 'Dermatologist'),
        ('researcher', 'Medical researcher'),
        ('other-medical', 'Other medical professional'),
    ])
    
    ai_experience = models.CharField(max_length=20, blank=True, choices=[
        ('none', 'No experience'),
        ('limited', 'Limited experience'),
        ('moderate', 'Moderate experience'),
        ('extensive', 'Extensive experience'),
    ])
    
    # Study completion status
    is_completed = models.BooleanField(default=False)
    phases_completed = models.JSONField(default=list)  # Track which phases were completed
    
    # Metadata
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "User Study Participant"
        verbose_name_plural = "User Study Participants"
    
    def save(self, *args, **kwargs):
        if not self.participant_id:
            # Generate unique participant ID
            self.participant_id = f"P{int(time.time())}{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Participant {self.participant_id} - {'Completed' if self.is_completed else 'In Progress'}"

class DemographicProfile(models.Model):
    """Detailed demographic information for research analysis"""
    
    participant = models.OneToOneField(UserStudyParticipant, on_delete=models.CASCADE, related_name='demographic_profile')
    
    # Additional demographic details
    occupation = models.CharField(max_length=100, blank=True)
    location_country = models.CharField(max_length=50, blank=True)
    location_region = models.CharField(max_length=50, blank=True)
    
    # Medical history (for research purposes)
    has_skin_condition = models.BooleanField(default=False)
    skin_condition_details = models.TextField(blank=True)
    family_history_skin_cancer = models.BooleanField(default=False)
    previous_skin_screening = models.BooleanField(default=False)
    
    # Technology usage
    smartphone_usage = models.CharField(max_length=20, choices=[
        ('never', 'Never'),
        ('rarely', 'Rarely'),
        ('occasionally', 'Occasionally'),
        ('frequently', 'Frequently'),
        ('daily', 'Daily'),
    ], blank=True)
    
    health_app_usage = models.CharField(max_length=20, choices=[
        ('never', 'Never used'),
        ('tried', 'Tried once'),
        ('occasional', 'Occasional user'),
        ('regular', 'Regular user'),
    ], blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Demographic Profile"
        verbose_name_plural = "Demographic Profiles"
    
    def __str__(self):
        return f"Demographics for {self.participant.participant_id}"

class UserStudyFeedback(models.Model):
    """Enhanced model for storing user study feedback and ratings"""
    
    participant = models.OneToOneField(UserStudyParticipant, on_delete=models.CASCADE, related_name='feedback')
    
    # Trust and usability ratings (1-5 scale)
    trust_rating = models.IntegerField(null=True, blank=True, choices=[
        (1, '1 - Not at all'),
        (2, '2 - Slightly'),
        (3, '3 - Moderately'),
        (4, '4 - Very much'),
        (5, '5 - Completely'),
    ])
    
    usability_rating = models.IntegerField(null=True, blank=True, choices=[
        (1, '1 - Very difficult'),
        (2, '2 - Difficult'),
        (3, '3 - Neutral'),
        (4, '4 - Easy'),
        (5, '5 - Very easy'),
    ])
    
    accuracy_perception = models.IntegerField(null=True, blank=True, choices=[
        (1, '1 - Very inaccurate'),
        (2, '2 - Inaccurate'),
        (3, '3 - Neutral'),
        (4, '4 - Accurate'),
        (5, '5 - Very accurate'),
    ])
    
    # Bias perception
    bias_perception = models.CharField(max_length=20, blank=True, choices=[
        ('yes', 'Yes, definitely'),
        ('maybe', 'Possibly'),
        ('unsure', 'Unsure'),
        ('no', 'No, unlikely'),
    ])
    
    fairness_rating = models.IntegerField(null=True, blank=True, choices=[
        (1, '1 - Very unfair'),
        (2, '2 - Unfair'),
        (3, '3 - Neutral'),
        (4, '4 - Fair'),
        (5, '5 - Very fair'),
    ])
    
    # Open-ended feedback
    improvements = models.TextField(blank=True)
    additional_comments = models.TextField(blank=True)
    concerns = models.TextField(blank=True)
    positive_aspects = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Study Feedback"
        verbose_name_plural = "User Study Feedbacks"
    
    def __str__(self):
        return f"Feedback for {self.participant.participant_id}"

class ImageFeedback(models.Model):
    """Feedback on specific image analysis results"""
    
    image_upload = models.ForeignKey(ImageUpload, on_delete=models.CASCADE, related_name='image_feedbacks')
    participant = models.ForeignKey(UserStudyParticipant, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    
    # Image-specific feedback
    prediction_agreement = models.CharField(max_length=20, choices=[
        ('strongly_agree', 'Strongly Agree'),
        ('agree', 'Agree'),
        ('neutral', 'Neutral'),
        ('disagree', 'Disagree'),
        ('strongly_disagree', 'Strongly Disagree'),
    ], blank=True)
    
    confidence_rating = models.IntegerField(null=True, blank=True, choices=[
        (1, '1 - Very low confidence'),
        (2, '2 - Low confidence'),
        (3, '3 - Medium confidence'),
        (4, '4 - High confidence'),
        (5, '5 - Very high confidence'),
    ])
    
    helpfulness_rating = models.IntegerField(null=True, blank=True, choices=[
        (1, '1 - Not helpful'),
        (2, '2 - Slightly helpful'),
        (3, '3 - Moderately helpful'),
        (4, '4 - Very helpful'),
        (5, '5 - Extremely helpful'),
    ])
    
    specific_feedback = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Image Feedback"
        verbose_name_plural = "Image Feedbacks"
    
    def __str__(self):
        return f"Feedback on {self.image_upload.filename}"

class ResearchConsent(models.Model):
    """Research consent tracking for compliance"""
    
    participant = models.OneToOneField(UserStudyParticipant, on_delete=models.CASCADE, related_name='research_consent')
    
    # Consent details
    consent_form_version = models.CharField(max_length=20, default='v1.0')
    ethics_approval_number = models.CharField(max_length=50, default='BUIRB-2025-001')
    
    # Consent permissions
    data_collection_consent = models.BooleanField(default=False)
    data_analysis_consent = models.BooleanField(default=False)
    publication_consent = models.BooleanField(default=False)
    future_contact_consent = models.BooleanField(default=False)
    
    # Timestamps
    consent_given_at = models.DateTimeField(auto_now_add=True)
    consent_ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Withdrawal tracking
    consent_withdrawn = models.BooleanField(default=False)
    withdrawal_date = models.DateTimeField(null=True, blank=True)
    withdrawal_reason = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Research Consent"
        verbose_name_plural = "Research Consents"
    
    def __str__(self):
        status = "Withdrawn" if self.consent_withdrawn else "Active"
        return f"Consent for {self.participant.participant_id} - {status}"

class SystemFeedback(models.Model):
    """General system feedback from users"""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    
    # Feedback categories
    FEEDBACK_TYPE_CHOICES = [
        ('bug', 'Bug Report'),
        ('feature', 'Feature Request'),
        ('usability', 'Usability Issue'),
        ('performance', 'Performance Issue'),
        ('accuracy', 'Accuracy Concern'),
        ('general', 'General Feedback'),
    ]
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPE_CHOICES)
    
    # Priority levels
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Feedback content
    title = models.CharField(max_length=200)
    description = models.TextField()
    steps_to_reproduce = models.TextField(blank=True)
    expected_behavior = models.TextField(blank=True)
    actual_behavior = models.TextField(blank=True)
    
    # System information
    browser_info = models.TextField(blank=True)
    device_info = models.TextField(blank=True)
    
    # Status tracking
    STATUS_CHOICES = [
        ('new', 'New'),
        ('acknowledged', 'Acknowledged'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Admin notes
    admin_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "System Feedback"
        verbose_name_plural = "System Feedbacks"
    
    def __str__(self):
        return f"{self.feedback_type.title()}: {self.title}"

class UserStudySession(models.Model):
    """Track individual study sessions"""
    
    participant = models.ForeignKey(UserStudyParticipant, on_delete=models.CASCADE, related_name='study_sessions')
    
    # Session details
    session_start = models.DateTimeField(auto_now_add=True)
    session_end = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(null=True, blank=True)
    
    # Session type
    SESSION_TYPE_CHOICES = [
        ('onboarding', 'Onboarding'),
        ('image_analysis', 'Image Analysis'),
        ('feedback', 'Feedback Collection'),
        ('follow_up', 'Follow-up'),
    ]
    session_type = models.CharField(max_length=20, choices=SESSION_TYPE_CHOICES)
    
    # Activities completed
    activities_completed = models.JSONField(default=list)
    images_analyzed = models.IntegerField(default=0)
    
    # Session notes
    notes = models.TextField(blank=True)
    issues_encountered = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-session_start']
        verbose_name = "User Study Session"
        verbose_name_plural = "User Study Sessions"
    
    def save(self, *args, **kwargs):
        if self.session_end and self.session_start:
            duration = self.session_end - self.session_start
            self.duration_minutes = int(duration.total_seconds() / 60)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.participant.participant_id} - {self.session_type} ({self.session_start.date()})"

class FairnessAnalysisResult(models.Model):
    """Store fairness analysis results for research"""
    
    # Analysis metadata
    analysis_date = models.DateTimeField(auto_now_add=True)
    dataset_used = models.CharField(max_length=100, blank=True)
    model_version = models.CharField(max_length=50, blank=True)
    
    # Fairness metrics
    disparate_impact_ratio = models.FloatField(null=True, blank=True)
    equalized_odds_difference = models.FloatField(null=True, blank=True)
    demographic_parity_difference = models.FloatField(null=True, blank=True)
    individual_fairness_score = models.FloatField(null=True, blank=True)
    
    # Group-specific metrics
    accuracy_by_skin_type = models.JSONField(default=dict)
    confidence_by_demographic = models.JSONField(default=dict)
    prediction_distribution = models.JSONField(default=dict)
    
    # Overall assessment
    BIAS_LEVEL_CHOICES = [
        ('low', 'Low Bias'),
        ('medium', 'Medium Bias'),
        ('high', 'High Bias'),
        ('critical', 'Critical Bias'),
    ]
    overall_bias_level = models.CharField(max_length=10, choices=BIAS_LEVEL_CHOICES, blank=True)
    
    # Recommendations
    mitigation_recommendations = models.TextField(blank=True)
    
    # Analysis details
    analysis_notes = models.TextField(blank=True)
    raw_results = models.JSONField(default=dict)
    
    class Meta:
        ordering = ['-analysis_date']
        verbose_name = "Fairness Analysis Result"
        verbose_name_plural = "Fairness Analysis Results"
    
    def __str__(self):
        return f"Fairness Analysis - {self.analysis_date.date()} ({self.overall_bias_level})"
