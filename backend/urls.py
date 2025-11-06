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

class RootIndexView(View):
    """Root index view showing all available app endpoints"""
    def get(self, request):
        return JsonResponse({
            'message': 'Skin Lesion Detection Project API',
            'version': '1.0.0',
            'available_apps': {
                '/admin/': 'Django admin interface',
                '/api/': 'Main API endpoints for image analysis',
                '/feedback/': 'User feedback collection endpoints',
                '/users/': 'User management endpoints',
                '/test/': 'Testing interface for image uploads',
                '/study/': 'User study interface for research participation'
            },
            'main_endpoints': {
                '/api/upload/': 'POST - Upload skin lesion image for AI analysis',
                '/api/study/': 'GET - Access user study interface',
                '/api/study/submit/': 'POST - Submit user study data',
                '/feedback/': 'GET/POST - Collect user feedback',
                '/users/register/': 'POST - Register new user',
                '/test/': 'GET - Test interface for image analysis'
            },
            'research_endpoints': {
                '/study/': 'GET - Main user study interface',
                '/api/study/statistics/': 'GET - Study participation statistics',
                '/api/study/export/': 'POST - Export study data for analysis'
            },
            'status': 'running',
            'django_version': '5.2.3'
        })

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
    """Main dashboard interface - handled by users app authentication"""
    # Redirect to users app dashboard which handles authentication
    from django.shortcuts import redirect
    return redirect('/users/dashboard/')

urlpatterns = [
    path("", RootIndexView.as_view(), name="root-index"),
    path("test/", test_upload_view, name="test-upload"),
    path("study/", user_study_view, name="user-study"),
    path("auth/", auth_view, name="auth"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path("feedback/", include("feedback.urls")),
    path("users/", include("users.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
