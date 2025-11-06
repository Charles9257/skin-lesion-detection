from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .models import Feedback
import json

@method_decorator(csrf_exempt, name='dispatch')
class FeedbackListCreateView(View):
    """Simple feedback view that works without REST Framework"""
    
    def get(self, request):
        """List all feedback"""
        try:
            feedback_list = []
            for feedback in Feedback.objects.all():
                feedback_list.append({
                    'id': feedback.id,
                    'rating': feedback.rating,
                    'comments': feedback.comments,
                    'created_at': feedback.created_at.isoformat() if feedback.created_at else None
                })
            return JsonResponse({'results': feedback_list})
        except Exception as e:
            return JsonResponse({'error': f'Error retrieving feedback: {str(e)}'}, status=500)
    
    def post(self, request):
        """Create new feedback"""
        try:
            data = json.loads(request.body)
            
            feedback = Feedback.objects.create(
                rating=data.get('rating'),
                comments=data.get('comments', '')
            )
            
            return JsonResponse({
                'id': feedback.id,
                'rating': feedback.rating,
                'comments': feedback.comments,
                'created_at': feedback.created_at.isoformat()
            }, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Error creating feedback: {str(e)}'}, status=500)
