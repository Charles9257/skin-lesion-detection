from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .models import CustomUser
import json

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
    """Simple registration view that works without REST Framework"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            
            if not all([username, email, password]):
                return JsonResponse({'error': 'Username, email, and password are required'}, status=400)
            
            # Check if user already exists
            if CustomUser.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already exists'}, status=400)
            
            if CustomUser.objects.filter(email=email).exists():
                return JsonResponse({'error': 'Email already exists'}, status=400)
            
            # Create user
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            return JsonResponse({
                'message': 'User created successfully',
                'user_id': user.id,
                'username': user.username,
                'email': user.email
            }, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Error creating user: {str(e)}'}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    """User login view for regular users (not admin)"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            email = data.get('email')
            password = data.get('password')
            
            if not email or not password:
                return JsonResponse({'error': 'Email and password are required'}, status=400)
            
            # Try to find user by email
            try:
                user = CustomUser.objects.get(email=email)
                username = user.username
            except CustomUser.DoesNotExist:
                return JsonResponse({'error': 'Invalid email or password'}, status=401)
            
            # Authenticate user
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({
                    'success': True,
                    'message': 'Login successful',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'name': f"{user.first_name} {user.last_name}".strip() or user.username
                    },
                    'redirect_url': '/dashboard/'
                })
            else:
                return JsonResponse({'error': 'Invalid email or password'}, status=401)
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Login error: {str(e)}'}, status=500)

class LogoutView(View):
    """User logout view"""
    
    def post(self, request):
        logout(request)
        return JsonResponse({
            'success': True,
            'message': 'Logout successful',
            'redirect_url': '/auth/'
        })
    
    def get(self, request):
        logout(request)
        return redirect('/auth/')

@login_required
def check_auth_status(request):
    """Check if user is authenticated"""
    if request.user.is_authenticated:
        return JsonResponse({
            'authenticated': True,
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
            }
        })
    else:
        return JsonResponse({'authenticated': False})
