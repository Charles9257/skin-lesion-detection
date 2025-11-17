from django.urls import path
from .views import feedback_page_view, usability_trust_survey_view

urlpatterns = [
    path("", feedback_page_view, name="feedback"),
    path("usability-survey/", usability_trust_survey_view, name="usability_trust_survey"),
]
