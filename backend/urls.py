"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.views import View
from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static


# Landing page view
def landing_view(request):
    return render(request, 'landing.html')

def test_upload_view(request):
    """Test interface for image upload and analysis"""
    return render(request, 'test_upload.html')

def user_study_view(request):
    """User study interface for research participation"""
    return render(request, 'user_study.html')

def auth_view(request):
    """Authentication interface for login/register"""
    return render(request, 'auth.html')

def dashboard_view(request):
    """Main dashboard interface - redirect to authenticated dashboard"""
    from django.shortcuts import redirect
    return redirect('/users/dashboard/')

def upload_view(request):
    """Upload interface for skin lesion images"""
    return render(request, 'upload.html')

def results_view(request):
    """Results interface for analysis results"""
    return render(request, 'results.html')

def feedback_view(request):
    """Feedback interface for user feedback"""
    return render(request, 'feedback.html')

urlpatterns = [
    path("", landing_view, name="root-index"),
    path("test/", test_upload_view, name="test-upload"),
    path("study/", user_study_view, name="user-study"),
    path("auth/", auth_view, name="auth"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("upload/", upload_view, name="upload"),
    path("results/", results_view, name="results"),
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path("feedback/", include("feedback.urls")),
    path("users/", include("users.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
