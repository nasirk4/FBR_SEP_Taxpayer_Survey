from django import forms
from .models import SurveyResponse

class SurveyResponseForm(forms.ModelForm):
    class Meta:
        model = SurveyResponse
        fields = '__all__'
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required': True}),
            'district': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'professional_role': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'province': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'experience_legal': forms.Select(attrs={'class': 'form-control'}),
            'experience_customs': forms.Select(attrs={'class': 'form-control'}),
        }