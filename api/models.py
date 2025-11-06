from django.db import models
from django.conf import settings
import uuid
import time

class ImageUpload(models.Model):
    """Model for storing uploaded skin lesion images and AI predictions"""
    
    # Image information
    image = models.ImageField(upload_to='uploads/', null=True, blank=True)
    filename = models.CharField(max_length=255, blank=True)
    file_size = models.IntegerField(null=True, blank=True)
    upload_timestamp = models.DateTimeField(auto_now_add=True)
    
    # AI prediction results
    prediction = models.CharField(max_length=50, blank=True)  # 'malignant' or 'benign'
    confidence = models.FloatField(null=True, blank=True)  # 0.0 to 1.0
    
    # Model information
    model_used = models.CharField(max_length=100, blank=True)
    model_version = models.CharField(max_length=50, blank=True)
    
    # Processing metadata
    processing_time = models.FloatField(null=True, blank=True)  # seconds
    error_message = models.TextField(blank=True)
    
    # User context (optional)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['-upload_timestamp']
    
    def __str__(self):
        return f"{self.filename} - {self.prediction} ({self.confidence:.2f})" if self.prediction else self.filename

class UserStudyParticipant(models.Model):
    """Model for storing user study participant data"""
    
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
    
    def save(self, *args, **kwargs):
        if not self.participant_id:
            # Generate unique participant ID
            self.participant_id = f"P{int(time.time())}{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Participant {self.participant_id} - {'Completed' if self.is_completed else 'In Progress'}"

class UserStudyFeedback(models.Model):
    """Model for storing user study feedback and ratings"""
    
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
    
    # Bias perception
    bias_perception = models.CharField(max_length=20, blank=True, choices=[
        ('yes', 'Yes, definitely'),
        ('maybe', 'Possibly'),
        ('unsure', 'Unsure'),
        ('no', 'No, unlikely'),
    ])
    
    # Open-ended feedback
    improvements = models.TextField(blank=True)
    additional_comments = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Feedback for {self.participant.participant_id}"

class UserStudyAnalysis(models.Model):
    """Model for storing AI analysis results during user study"""
    
    participant = models.ForeignKey(UserStudyParticipant, on_delete=models.CASCADE, related_name='analyses')
    
    # Image information
    image_filename = models.CharField(max_length=255, blank=True)
    image_size = models.IntegerField(null=True, blank=True)
    image_type = models.CharField(max_length=20, blank=True)  # 'uploaded' or 'test'
    
    # AI prediction results
    prediction = models.CharField(max_length=50, blank=True)
    confidence = models.FloatField(null=True, blank=True)
    model_used = models.CharField(max_length=100, blank=True)
    
    # Analysis metadata
    analysis_timestamp = models.DateTimeField(auto_now_add=True)
    processing_time = models.FloatField(null=True, blank=True)
    
    # Study context
    analysis_order = models.IntegerField(default=1)  # In case multiple analyses per participant
    
    class Meta:
        ordering = ['participant', 'analysis_order']
    
    def __str__(self):
        return f"Analysis {self.analysis_order} for {self.participant.participant_id}: {self.prediction}"
