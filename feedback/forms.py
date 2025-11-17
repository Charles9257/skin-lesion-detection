from django import forms
from .models import UsabilityTrustSurvey

class UsabilityTrustSurveyForm(forms.ModelForm):
    class Meta:
        model = UsabilityTrustSurvey
        fields = [
            'q1_interface_intuitive',
            'q2_layout_design_clear',
            'q3_response_time_satisfactory',
            'q4_steps_understandable',
            'q5_results_clear',
            'q6_visual_explanations_helpful',
            'q7_fairness_metrics_understandable',
            'q8_fair_predictions',
            'q9_info_and_control_sufficient',
            'q10_overall_satisfaction',
            'q11_recommend_system',
            'most_helpful_feature',
            'improvement_suggestion',
            'noticed_limitations',
        ]
        widgets = {
            'most_helpful_feature': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Optional: What feature did you find most helpful?'}),
            'improvement_suggestion': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Optional: What could be improved?'}),
            'noticed_limitations': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Optional: Any limitations or errors noticed?'}),
        }
        labels = {
            'q1_interface_intuitive': 'The system interface was intuitive and easy to navigate.',
            'q2_layout_design_clear': 'The layout and colour design of the dashboard made information easy to interpret.',
            'q3_response_time_satisfactory': 'The system’s response time and performance were satisfactory.',
            'q4_steps_understandable': 'It was easy to understand the steps required to perform a diagnostic test using the system.',
            'q5_results_clear': 'The diagnostic results were presented clearly and understandably.',
            'q6_visual_explanations_helpful': 'The visual explanations (e.g., Grad-CAM or SHAP) helped me understand why the AI made specific predictions.',
            'q7_fairness_metrics_understandable': 'The fairness metrics (e.g., DPD, EOD, DIR) were easy to understand and meaningful for evaluating ethical accountability.',
            'q8_fair_predictions': 'I felt confident that the system treated all skin tones fairly when making predictions.',
            'q9_info_and_control_sufficient': 'The system provided enough information and control for me to question or review its outputs.',
            'q10_overall_satisfaction': 'Overall, I am satisfied with the system’s usability, fairness, and explainability.',
            'q11_recommend_system': 'I would recommend this system for future use or testing in dermatology and AI fairness studies.',
            'most_helpful_feature': 'Which feature of the system did you find most helpful or impressive?',
            'improvement_suggestion': 'What part of the system interface could be improved for better usability or fairness explanation?',
            'noticed_limitations': 'Did you notice any limitations or errors in predictions? If yes, please describe briefly.',
        }
