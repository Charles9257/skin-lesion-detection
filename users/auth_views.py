"""
Authentication Views for User Login/Register System
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
import json
import logging

logger = logging.getLogger(__name__)

def auth_view(request):
    """Combined authentication view"""
    if request.user.is_authenticated:
        return redirect('users:user-dashboard')
    return render(request, 'users/auth.html')

@csrf_exempt
@require_http_methods(["POST"])
def login_api(request):
    """API endpoint for user login"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({
                'success': False,
                'message': 'Username and password are required'
            }, status=400)
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({
                'success': True,
                'message': 'Login successful',
                'redirect_url': '/users/dashboard/' if not user.is_staff else '/admin/',
                'user': {
                    'username': user.username,
                    'email': user.email,
                    'is_staff': user.is_staff
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Invalid username or password'
            }, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Login error: {e}")
        return JsonResponse({
            'success': False,
            'message': 'An error occurred during login'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def register_api(request):
    """API endpoint for user registration"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        
        # Validation
        if not all([username, email, password]):
            return JsonResponse({
                'success': False,
                'message': 'Username, email, and password are required'
            }, status=400)
        
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                'success': False,
                'message': 'Username already exists'
            }, status=400)
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                'success': False,
                'message': 'Email already exists'
            }, status=400)
        
        if len(password) < 8:
            return JsonResponse({
                'success': False,
                'message': 'Password must be at least 8 characters long'
            }, status=400)
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Auto-login after registration
        login(request, user)
        
        return JsonResponse({
            'success': True,
            'message': 'Registration successful',
            'redirect_url': '/users/dashboard/',
            'user': {
                'username': user.username,
                'email': user.email,
                'is_staff': user.is_staff
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return JsonResponse({
            'success': False,
            'message': 'An error occurred during registration'
        }, status=500)

@login_required
def profile_view(request):
    """Enhanced profile view with update functionality"""
    from django.contrib.auth import update_session_auth_hash
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'change_password':
            # Handle password change
            current_password = request.POST.get('current_password')
            new_password1 = request.POST.get('new_password1')
            new_password2 = request.POST.get('new_password2')
            
            if not request.user.check_password(current_password):
                messages.error(request, 'Current password is incorrect.')
            elif new_password1 != new_password2:
                messages.error(request, 'New passwords do not match.')
            elif len(new_password1) < 8:
                messages.error(request, 'Password must be at least 8 characters long.')
            else:
                request.user.set_password(new_password1)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Password changed successfully!')
                return redirect('users:user-profile')
        else:
            # Handle profile update
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            email = request.POST.get('email', '').strip()
            
            # Validate email uniqueness
            if email and email != request.user.email:
                if User.objects.filter(email=email).exists():
                    messages.error(request, 'This email is already in use.')
                    return redirect('users:user-profile')
            
            # Update user information
            request.user.first_name = first_name
            request.user.last_name = last_name
            if email:
                request.user.email = email
            request.user.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:user-profile')
    
    # Calculate user statistics
    from django.utils import timezone
    days_active = (timezone.now() - request.user.date_joined).days
    
    context = {
        'user': request.user,
        'uploads_count': 0,  # TODO: Get actual count from API app
        'analyses_count': 0,  # TODO: Get actual count from API app
        'feedback_count': 0,  # TODO: Get actual count from feedback app
        'days_active': days_active,
    }
    
    return render(request, 'users/profile.html', context)

@login_required
def dashboard_view(request):
    """Enhanced dashboard view with analytics data"""
    from django.utils import timezone
    
    try:
        # Get user statistics
        context = {
            'user': request.user,
            'total_users': User.objects.count(),
            'recent_users': User.objects.order_by('-date_joined')[:5],
            'admin_users': User.objects.filter(is_staff=True).count(),
            'active_sessions': 1,  # Simplified for now
            'system_health': 'Good',
            'last_backup': timezone.now(),
        }
        return render(request, 'users/dashboard.html', context)
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        messages.error(request, "Error loading dashboard")
        return render(request, 'users/dashboard.html', {'user': request.user})

def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('users:user-auth')

def check_session(request):
    """Check if user session is active"""
    return JsonResponse({
        'authenticated': request.user.is_authenticated,
        'user': {
            'username': request.user.username,
            'email': request.user.email,
            'is_staff': request.user.is_staff
        } if request.user.is_authenticated else None
    })

def demo_data_api(request):
    """Provide demo data for testing"""
    return JsonResponse({
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'admin_users': User.objects.filter(is_staff=True).count(),
        'recent_registrations': [
            {
                'username': user.username,
                'date_joined': user.date_joined.isoformat(),
                'is_active': user.is_active
            }
            for user in User.objects.order_by('-date_joined')[:5]
        ]
    })