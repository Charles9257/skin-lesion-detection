from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .models import Feedback, UsabilityTrustSurvey
from .forms import UsabilityTrustSurveyForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
@login_required
def usability_trust_survey_view(request):
    """Display and process the System Usability and Trust Survey form."""
    if request.method == 'POST':
        form = UsabilityTrustSurveyForm(request.POST)
        if form.is_valid():
            survey = form.save(commit=False)
            survey.user = request.user
            survey.save()
            return render(request, 'survey_thankyou.html')
    else:
        form = UsabilityTrustSurveyForm()
    return render(request, 'usability_trust_survey.html', {'form': form})
import json


# Render feedback.html for /feedback/ page
def feedback_page_view(request):
    return render(request, 'feedback.html')
