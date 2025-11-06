from django.urls import path
from .views import RegisterView
from .auth_views import (
    auth_view, 
    login_api, 
    register_api, 
    dashboard_view, 
    logout_view, 
    check_session,
    demo_data_api,
    profile_view
)

app_name = 'users'

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    
    # Authentication endpoints
    path("auth/", auth_view, name="user-auth"),
    path("profile/", profile_view, name="user-profile"),
    path("login/", login_api, name="login-api"),
    path("register-api/", register_api, name="register-api"),
    path("logout/", logout_view, name="logout"),
    path("dashboard/", dashboard_view, name="user-dashboard"),
    path("session/", check_session, name="check-session"),
    path("demo-data/", demo_data_api, name="demo-data"),
    
    # JWT token views - uncomment when rest_framework_simplejwt is installed
    # path("login/", TokenObtainPairView.as_view(), name="login"),
    # path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    # path("logout/", TokenBlacklistView.as_view(), name="logout"),
]
