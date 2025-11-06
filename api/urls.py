from django.urls import path
from .views import ImageUploadView, ApiIndexView, AnalysisHistoryView
from .user_study_views import (
    UserStudyView, 
    submit_study_data, 
    validate_consent, 
    get_study_statistics,
    export_study_data
)

urlpatterns = [
    path("", ApiIndexView.as_view(), name="api-index"),
    path("upload/", ImageUploadView.as_view(), name="image-upload"),
    path("history/", AnalysisHistoryView.as_view(), name="analysis-history"),
    
    # User Study endpoints
    path("study/", UserStudyView.as_view(), name="user-study"),
    path("study/submit/", submit_study_data, name="submit-study-data"),
    path("study/consent/", validate_consent, name="validate-consent"),
    path("study/statistics/", get_study_statistics, name="study-statistics"),
    path("study/export/", export_study_data, name="export-study-data"),
]
