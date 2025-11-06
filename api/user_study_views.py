"""
User Study Views for AI Fairness Research
Handles participant consent, demographics collection, and study data management
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import json
import logging
import uuid
from datetime import datetime
import os

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class UserStudyView(TemplateView):
    """Main user study interface view"""
    template_name = 'user_study.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'study_title': 'AI Skin Lesion Detection Research Study',
            'institution': 'Bolton University',
            'ethics_approval': 'BUIRB-2025-001',
            'contact_email': 'medical-ai-research@bolton.ac.uk'
        })
        return context

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def submit_study_data(request):
    """
    Submit complete user study data including consent, demographics, and feedback
    """
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['consent', 'participantId', 'completedAt']
        for field in required_fields:
            if field not in data:
                return Response({
                    'error': f'Missing required field: {field}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate unique study session ID
        session_id = str(uuid.uuid4())
        
        # Structure the study data
        study_record = {
            'session_id': session_id,
            'participant_id': data['participantId'],
            'submitted_at': datetime.now().isoformat(),
            'consent': data.get('consent', {}),
            'demographics': data.get('demographics', {}),
            'analysis_data': data.get('analysis', {}),
            'feedback': data.get('feedback', {}),
            'completion_time': data.get('completedAt'),
            'metadata': {
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'ip_address': get_client_ip(request),
                'study_version': '1.0'
            }
        }
        
        # Save to file (in production, save to database)
        save_study_data(study_record)
        
        logger.info(f"Study data submitted successfully for participant {data['participantId']}")
        
        return Response({
            'success': True,
            'session_id': session_id,
            'participant_id': data['participantId'],
            'message': 'Study data saved successfully'
        }, status=status.HTTP_201_CREATED)
        
    except json.JSONDecodeError:
        return Response({
            'error': 'Invalid JSON data'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error submitting study data: {str(e)}")
        return Response({
            'error': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def validate_consent(request):
    """
    Validate consent form completion
    """
    try:
        data = json.loads(request.body)
        
        required_consents = ['consentRead', 'consentParticipate', 'consentData', 'consentAge']
        missing_consents = []
        
        for consent in required_consents:
            if not data.get(consent, False):
                missing_consents.append(consent)
        
        if missing_consents:
            return Response({
                'valid': False,
                'missing_consents': missing_consents,
                'message': 'Please complete all required consent items'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'valid': True,
            'message': 'Consent validation successful'
        })
        
    except Exception as e:
        logger.error(f"Error validating consent: {str(e)}")
        return Response({
            'error': 'Consent validation failed'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def get_study_statistics(request):
    """
    Get anonymized study participation statistics
    """
    try:
        stats = calculate_study_statistics()
        
        return Response({
            'total_participants': stats.get('total_participants', 0),
            'completion_rate': stats.get('completion_rate', 0.0),
            'demographics_summary': stats.get('demographics', {}),
            'feedback_summary': stats.get('feedback', {}),
            'last_updated': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating study statistics: {str(e)}")
        return Response({
            'error': 'Failed to generate statistics'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def export_study_data(request):
    """
    Export anonymized study data for analysis
    """
    try:
        # In production, implement proper authorization
        export_format = request.data.get('format', 'json')
        include_raw_data = request.data.get('include_raw', False)
        
        if export_format not in ['json', 'csv']:
            return Response({
                'error': 'Unsupported export format'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate export
        export_data = generate_study_export(export_format, include_raw_data)
        
        return Response({
            'export_ready': True,
            'download_url': export_data.get('url'),
            'file_size': export_data.get('size'),
            'format': export_format,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error exporting study data: {str(e)}")
        return Response({
            'error': 'Export generation failed'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def get_client_ip(request):
    """Extract client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def save_study_data(study_record):
    """
    Save study data to file system (in production, use database)
    """
    try:
        # Create study data directory
        study_dir = os.path.join('study_data')
        os.makedirs(study_dir, exist_ok=True)
        
        # Save individual participant data
        filename = f"participant_{study_record['participant_id']}.json"
        filepath = os.path.join(study_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(study_record, f, indent=2)
        
        # Append to master log
        log_filepath = os.path.join(study_dir, 'study_log.jsonl')
        with open(log_filepath, 'a') as f:
            f.write(json.dumps(study_record) + '\n')
        
        logger.info(f"Study data saved to {filepath}")
        
    except Exception as e:
        logger.error(f"Error saving study data: {str(e)}")
        raise

def calculate_study_statistics():
    """
    Calculate anonymized study statistics
    """
    try:
        study_dir = os.path.join('study_data')
        if not os.path.exists(study_dir):
            return {
                'total_participants': 0,
                'completion_rate': 0.0,
                'demographics': {},
                'feedback': {}
            }
        
        # Read all participant files
        participants = []
        for filename in os.listdir(study_dir):
            if filename.startswith('participant_') and filename.endswith('.json'):
                filepath = os.path.join(study_dir, filename)
                with open(filepath, 'r') as f:
                    participants.append(json.load(f))
        
        # Calculate statistics
        total_participants = len(participants)
        completed_participants = len([p for p in participants if p.get('feedback')])
        completion_rate = completed_participants / total_participants if total_participants > 0 else 0.0
        
        # Demographics summary
        demographics = {}
        for category in ['age', 'gender', 'ethnicity', 'skinType', 'education']:
            demographics[category] = {}
            for participant in participants:
                value = participant.get('demographics', {}).get(category)
                if value:
                    demographics[category][value] = demographics[category].get(value, 0) + 1
        
        # Feedback summary
        feedback = {}
        for rating in ['trustRating', 'usabilityRating', 'biasPerception']:
            feedback[rating] = {}
            for participant in participants:
                value = participant.get('feedback', {}).get(rating)
                if value:
                    feedback[rating][value] = feedback[rating].get(value, 0) + 1
        
        return {
            'total_participants': total_participants,
            'completion_rate': completion_rate,
            'demographics': demographics,
            'feedback': feedback
        }
        
    except Exception as e:
        logger.error(f"Error calculating statistics: {str(e)}")
        return {
            'total_participants': 0,
            'completion_rate': 0.0,
            'demographics': {},
            'feedback': {}
        }

def generate_study_export(export_format, include_raw_data=False):
    """
    Generate study data export in specified format
    """
    try:
        study_dir = os.path.join('study_data')
        export_dir = os.path.join('study_exports')
        os.makedirs(export_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if export_format == 'json':
            # Read all participant data
            all_data = []
            for filename in os.listdir(study_dir):
                if filename.startswith('participant_') and filename.endswith('.json'):
                    filepath = os.path.join(study_dir, filename)
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        if not include_raw_data:
                            # Remove sensitive information
                            data.pop('metadata', None)
                        all_data.append(data)
            
            export_filename = f'study_export_{timestamp}.json'
            export_filepath = os.path.join(export_dir, export_filename)
            
            with open(export_filepath, 'w') as f:
                json.dump(all_data, f, indent=2)
        
        elif export_format == 'csv':
            import csv
            
            export_filename = f'study_export_{timestamp}.csv'
            export_filepath = os.path.join(export_dir, export_filename)
            
            # Create CSV with flattened data
            with open(export_filepath, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                headers = [
                    'participant_id', 'submitted_at', 'completion_time',
                    'age', 'gender', 'ethnicity', 'skin_type', 'education', 'medical_background',
                    'trust_rating', 'usability_rating', 'bias_perception',
                    'ai_prediction', 'ai_confidence'
                ]
                writer.writerow(headers)
                
                # Write data rows
                for filename in os.listdir(study_dir):
                    if filename.startswith('participant_') and filename.endswith('.json'):
                        filepath = os.path.join(study_dir, filename)
                        with open(filepath, 'r') as f:
                            data = json.load(f)
                            
                            demographics = data.get('demographics', {})
                            feedback = data.get('feedback', {})
                            analysis = data.get('analysis_data', {})
                            
                            row = [
                                data.get('participant_id', ''),
                                data.get('submitted_at', ''),
                                data.get('completion_time', ''),
                                demographics.get('age', ''),
                                demographics.get('gender', ''),
                                demographics.get('ethnicity', ''),
                                demographics.get('skinType', ''),
                                demographics.get('education', ''),
                                demographics.get('medicalBackground', ''),
                                feedback.get('trustRating', ''),
                                feedback.get('usabilityRating', ''),
                                feedback.get('biasPerception', ''),
                                analysis.get('prediction', ''),
                                analysis.get('confidence', '')
                            ]
                            writer.writerow(row)
        
        file_size = os.path.getsize(export_filepath)
        
        return {
            'url': f'/study_exports/{export_filename}',
            'size': file_size,
            'filepath': export_filepath
        }
        
    except Exception as e:
        logger.error(f"Error generating export: {str(e)}")
        raise