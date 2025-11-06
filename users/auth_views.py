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
    """Main authentication page with login/register forms"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    return render(request, 'auth.html', {
        'title': 'AI Skin Lesion Detection - Login',
        'demo_accounts': [
            {'email': 'doctor@demo.com', 'password': 'demo123', 'role': 'Doctor'},
            {'email': 'researcher@demo.com', 'password': 'demo123', 'role': 'Researcher'},
            {'email': 'student@demo.com', 'password': 'demo123', 'role': 'Student'},
        ]
    })

@csrf_exempt
@require_http_methods(["POST"])
def login_api(request):
    """API endpoint for user login"""
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return JsonResponse({
                'success': False,
                'error': 'Email and password are required'
            }, status=400)
        
        # Check demo accounts first
        demo_accounts = {
            'doctor@demo.com': 'demo123',
            'researcher@demo.com': 'demo123',
            'student@demo.com': 'demo123'
        }
        
        if email in demo_accounts and demo_accounts[email] == password:
            # Create demo user session
            user_data = {
                'email': email,
                'name': get_demo_name(email),
                'role': get_demo_role(email),
                'is_demo': True
            }
            
            return JsonResponse({
                'success': True,
                'user': user_data,
                'message': 'Demo login successful'
            })
        
        # Try to authenticate with Django user system
        try:
            user = User.objects.get(email=email)
            auth_user = authenticate(request, username=user.username, password=password)
            
            if auth_user:
                login(request, auth_user)
                return JsonResponse({
                    'success': True,
                    'user': {
                        'email': auth_user.email,
                        'name': auth_user.get_full_name() or auth_user.username,
                        'role': 'User',
                        'is_demo': False
                    },
                    'message': 'Login successful'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid password'
                }, status=401)
                
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'User account not found'
            }, status=404)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Login failed. Please try again.'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def register_api(request):
    """API endpoint for user registration"""
    try:
        data = json.loads(request.body)
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        # Validation
        if not all([name, email, password, confirm_password]):
            return JsonResponse({
                'success': False,
                'error': 'All fields are required'
            }, status=400)
        
        if password != confirm_password:
            return JsonResponse({
                'success': False,
                'error': 'Passwords do not match'
            }, status=400)
        
        if len(password) < 6:
            return JsonResponse({
                'success': False,
                'error': 'Password must be at least 6 characters long'
            }, status=400)
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                'success': False,
                'error': 'User with this email already exists'
            }, status=409)
        
        # Create new user
        username = email.split('@')[0]  # Use email prefix as username
        counter = 1
        original_username = username
        
        # Ensure unique username
        while User.objects.filter(username=username).exists():
            username = f"{original_username}{counter}"
            counter += 1
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=name.split()[0] if name.split() else name,
            last_name=' '.join(name.split()[1:]) if len(name.split()) > 1 else ''
        )
        
        logger.info(f"New user registered: {email}")
        
        return JsonResponse({
            'success': True,
            'message': 'Account created successfully. Please log in.'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Registration failed. Please try again.'
        }, status=500)

@login_required
def dashboard_view(request):
    """Main dashboard view for authenticated users - requires login"""
    
    user_data = {
        'name': request.user.get_full_name() or request.user.username,
        'email': request.user.email,
        'role': 'User'
    }
    
    return render(request, 'dashboard.html', {
        'user': user_data,
        'title': 'AI Skin Lesion Detection - Dashboard'
    })

def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('auth')

def get_demo_name(email):
    """Get demo user display name"""
    names = {
        'doctor@demo.com': 'Dr. Sarah Johnson',
        'researcher@demo.com': 'Prof. Michael Chen',
        'student@demo.com': 'Alex Thompson'
    }
    return names.get(email, email.split('@')[0].title())

def get_demo_role(email):
    """Get demo user role"""
    if 'doctor' in email:
        return 'Doctor'
    elif 'researcher' in email:
        return 'Researcher'
    elif 'student' in email:
        return 'Student'
    return 'User'

@csrf_exempt
def check_session(request):
    """API endpoint to check user session status"""
    if request.user.is_authenticated:
        return JsonResponse({
            'authenticated': True,
            'user': {
                'name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
                'role': 'User'
            }
        })
    else:
        return JsonResponse({'authenticated': False})

@csrf_exempt
def demo_data_api(request):
    """API endpoint to get demo data for dashboard"""
    demo_stats = {
        'total_uploads': 247,
        'avg_accuracy': 94.2,
        'fairness_score': 87.5,
        'avg_processing_time': 2.3,
        'recent_analyses': [
            {
                'date': '2025-01-04 14:30:22',
                'filename': 'melanoma_sample_001.jpg',
                'prediction': 'malignant',
                'confidence': 92,
                'processing_time': '2.1s',
                'status': 'completed'
            },
            {
                'date': '2025-01-04 14:25:15',
                'filename': 'benign_mole_003.jpg',
                'prediction': 'benign',
                'confidence': 87,
                'processing_time': '1.9s',
                'status': 'completed'
            },
            {
                'date': '2025-01-04 14:18:09',
                'filename': 'suspicious_lesion_002.jpg',
                'prediction': 'malignant',
                'confidence': 89,
                'processing_time': '2.4s',
                'status': 'completed'
            }
        ],
        'fairness_metrics': {
            'disparate_impact': 0.85,
            'equalised_odds': 0.92,
            'demographic_parity': 0.89,
            'individual_fairness': 0.94
        }
    }
    
    return JsonResponse(demo_stats)