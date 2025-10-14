# survey/forms.py
from django import forms
from .models import SurveyResponse

class SurveyResponseForm(forms.ModelForm):
    class Meta:
        model = SurveyResponse
        # Explicitly define fields to control ordering and requirements
        fields = [
            # Basic Information (R = Required, O = Optional)
            'full_name', 'email', 'district', 'mobile', 'professional_role', 
            'province', 'practice_areas', 'kii_consent',
            
            # Experience (O)
            'experience_legal', 'experience_customs',
            
            # Generic Questions (R)
            'g1_policy_impact', 'g2_system_impact', 'g3_technical_issues', 
            'g4_disruption', 'g5_digital_literacy',
            
            # Legal Practitioner Questions (R for legal/both)
            'lp1_digital_support', 'lp2_challenges', 'lp3_challenges', 
            'lp4_challenges', 'lp5_tax_types', 'lp5_visible', 'lp6_priority_improvement',
            
            # Customs Agent Questions (R for customs/both)  
            'ca1_training', 'ca2_system_integration', 'ca3_challenges', 
            'ca4_effectiveness', 'ca5_policy_impact', 'ca6_biggest_challenge', 'ca6_improvement',
            
            # Cross-System & Feedback (O)
            'cross_system_answers', 'final_remarks', 'survey_feedback'
        ]
        
        widgets = {
            # Required fields with stronger styling
            'full_name': forms.TextInput(attrs={
                'class': 'form-control required-field', 
                'required': True,
                'placeholder': 'Enter full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control required-field', 
                'required': True,
                'placeholder': 'Enter email address'
            }),
            'district': forms.TextInput(attrs={
                'class': 'form-control required-field', 
                'required': True,
                'placeholder': 'Enter district'
            }),
            
            # Optional fields with different styling
            'mobile': forms.TextInput(attrs={
                'class': 'form-control optional-field',
                'placeholder': 'Optional mobile number'
            }),
            'practice_areas': forms.TextInput(attrs={
                'class': 'form-control optional-field',
                'placeholder': 'e.g., income_tax,sales_tax (optional)'
            }),
            
            # Required select fields
            'professional_role': forms.Select(attrs={
                'class': 'form-control required-field', 
                'required': True
            }),
            'province': forms.Select(attrs={
                'class': 'form-control required-field', 
                'required': True
            }),
            
            # Optional select fields
            'experience_legal': forms.Select(attrs={
                'class': 'form-control optional-field'
            }),
            'experience_customs': forms.Select(attrs={
                'class': 'form-control optional-field'
            }),
            'kii_consent': forms.Select(attrs={
                'class': 'form-control optional-field'
            }),
            
            # Text areas
            'final_remarks': forms.Textarea(attrs={
                'class': 'form-control optional-field',
                'rows': 3,
                'placeholder': 'Optional final remarks...'
            }),
            'survey_feedback': forms.Textarea(attrs={
                'class': 'form-control optional-field', 
                'rows': 3,
                'placeholder': 'Optional feedback about this survey...'
            }),
            'lp6_priority_improvement': forms.Textarea(attrs={
                'class': 'form-control optional-field',
                'rows': 3,
                'placeholder': 'What ONE improvement would most enhance your legal practice?'
            }),
            'ca6_improvement': forms.Textarea(attrs={
                'class': 'form-control optional-field',
                'rows': 3, 
                'placeholder': 'What specific improvement would help most?'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_field_requirements()
        self._add_field_labels()

    def _apply_field_requirements(self):
        """Apply proper required/optional field attributes based on our model."""
        required_fields = [
            'full_name', 'email', 'district', 'professional_role', 'province',
            'g1_policy_impact', 'g2_system_impact', 'g3_technical_issues', 'g5_digital_literacy'
        ]
        
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True
                # Add CSS class for frontend styling
                current_classes = self.fields[field_name].widget.attrs.get('class', '')
                self.fields[field_name].widget.attrs['class'] = f'{current_classes} required-field'.strip()

    def _add_field_labels(self):
        """Add helpful labels and help text to fields."""
        field_labels = {
            'professional_role': 'Professional Role *',
            'province': 'Province *', 
            'mobile': 'Mobile Number (Optional)',
            'practice_areas': 'Practice Areas (Optional)',
            'kii_consent': 'Consent for Follow-up Interview (Optional)',
            'g4_disruption': 'Significance of Disruptions (Optional)',
            'lp6_priority_improvement': 'Priority Improvement Suggestion (Optional)',
            'ca6_improvement': 'Specific Improvement Needed (Optional)',
            'final_remarks': 'Final Remarks (Optional)',
            'survey_feedback': 'Survey Feedback (Optional)'
        }
        
        for field_name, label in field_labels.items():
            if field_name in self.fields:
                self.fields[field_name].label = label

    def clean(self):
        """Custom validation for role-specific field requirements."""
        cleaned_data = super().clean()
        professional_role = cleaned_data.get('professional_role')
        
        # Validate role-specific required fields
        if professional_role in ['legal', 'both']:
            legal_fields = ['lp1_digital_support', 'lp2_challenges', 'lp3_challenges', 'lp4_challenges']
            for field in legal_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, 'This field is required for Legal Practitioners')
                    
        if professional_role in ['customs', 'both']:
            customs_fields = ['ca1_training', 'ca2_system_integration', 'ca3_challenges', 'ca4_effectiveness', 'ca5_policy_impact', 'ca6_biggest_challenge']
            for field in customs_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, 'This field is required for Customs Agents')
        
        return cleaned_data