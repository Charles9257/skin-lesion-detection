from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth import authenticate
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
