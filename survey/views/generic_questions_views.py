from django.shortcuts import render, redirect
from survey.utils.progress import get_progress_context
from survey.utils.session_utils import validate_session_size
from survey.models import SurveyResponse
import logging
import json

logger = logging.getLogger(__name__)

def get_generic_questions_context():
    """Return standardized context for generic questions form options."""
    matrix_options = [
        ('very_positive', 'Very Positive'), ('positive', 'Positive'), ('neutral', 'Neutral'),
        ('negative', 'Negative'), ('very_negative', 'Very Negative'), ('na', 'N/A'), ('dont_know', 'Don’t Know')
    ]
    g3_options = [
        ('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'),
        ('rarely', 'Rarely'), ('never', 'Never'), ('dont_know', 'Don’t Know')
    ]
    g4_options = [
        ('very_significantly', 'Very significantly'), ('significantly', 'Significantly'),
        ('minimally', 'Minimally'), ('not_at_all', 'Not at all')
    ]
    g5_options = [
        ('very_significantly', 'Very significantly'), ('significantly', 'Significantly'), ('neutral', 'Neutral'),
        ('minimally', 'Minimally'), ('not_at_all', 'Not at all'), ('dont_know', 'Don’t Know')
    ]
    g1_aspects = [
        ('service_delivery', 'Service delivery efficiency'),
        ('client_numbers', 'Client numbers'),
        ('revenue_fees', 'Revenue/fees'),
        ('compliance_burden', 'Compliance burden')
    ]
    g2_aspects = [
        ('workflow_efficiency', 'Workflow efficiency'),
        ('service_delivery', 'Service delivery'),
        ('client_numbers', 'Client numbers')
    ]
    
    return {
        'g1_matrix_options': matrix_options,
        'g2_matrix_options': matrix_options,
        'g3_options': g3_options,
        'g4_options': g4_options,
        'g5_options': g5_options,
        'g1_aspects': g1_aspects,
        'g2_aspects': g2_aspects,
        'g3_values_requiring_g4': ['daily', 'weekly', 'monthly', 'rarely'],
        'valid_options': {
            'g1': [opt[0] for opt in matrix_options],
            'g2': [opt[0] for opt in matrix_options],
            'g3_technical_issues': [opt[0] for opt in g3_options],
            'g4_disruption': [opt[0] for opt in g4_options],
            'g5_digital_literacy': [opt[0] for opt in g5_options]
        }
    }

def validate_matrix_fields(request, aspects, prefix, valid_options, errors, answers):
    """Validate matrix fields (G1 or G2) and populate answers."""
    for aspect in aspects:
        value = request.POST.get(f'{prefix}_{aspect}', '').strip()
        if not value:
            errors.append(f"Please select an option for {prefix.upper()} {aspect.replace('_', ' ').title()}")
        elif value not in valid_options:
            errors.append(f"Invalid value for {prefix.upper()} {aspect.replace('_', ' ').title()}")
        answers[prefix][aspect] = value

def validate_generic_questions_form(request, context_data):
    """Validate generic questions form data."""
    errors = []
    generic_answers = {'g1': {}, 'g2': {}}

    try:
        # Validate G1: Policy Impact Matrix
        for aspect, _ in context_data['g1_aspects']:
            value = request.POST.get(f'g1_{aspect}', '').strip()  # Get string value
            if isinstance(value, (tuple, list)):
                value = value[0] if value else ''  # Take first value if tuple/list
            if not value:
                errors.append(f"Please select an option for G1 {aspect.replace('_', ' ').title()}")
            elif value not in context_data['valid_options']['g1']:
                errors.append(f"Invalid value for G1 {aspect.replace('_', ' ').title()}")
            generic_answers['g1'][aspect] = value

        # Validate G2: System Impact Matrix
        for aspect, _ in context_data['g2_aspects']:
            value = request.POST.get(f'g2_{aspect}', '').strip()
            if isinstance(value, (tuple, list)):
                value = value[0] if value else ''
            if not value:
                errors.append(f"Please select an option for G2 {aspect.replace('_', ' ').title()}")
            elif value not in context_data['valid_options']['g2']:
                errors.append(f"Invalid value for G2 {aspect.replace('_', ' ').title()}")
            generic_answers['g2'][aspect] = value

        # Validate G3: Technical Issues
        g3_value = request.POST.get('g3_technical_issues', '').strip()
        if isinstance(g3_value, (tuple, list)):
            g3_value = g3_value[0] if g3_value else ''
        if not g3_value:
            errors.append("Please select an option for G3 Technical Issues")
        elif g3_value not in context_data['valid_options']['g3_technical_issues']:
            errors.append("Invalid value for G3 Technical Issues")
        generic_answers['g3_technical_issues'] = g3_value

        # Validate G4: Disruption (conditional)
        g4_value = request.POST.get('g4_disruption', '').strip()
        if isinstance(g4_value, (tuple, list)):
            g4_value = g4_value[0] if g4_value else ''
        if g3_value in context_data['g3_values_requiring_g4']:
            if not g4_value:
                errors.append("Please select an option for G4 Disruption")
            elif g4_value not in context_data['valid_options']['g4_disruption']:
                errors.append("Invalid value for G4 Disruption")
        generic_answers['g4_disruption'] = g4_value if g3_value in context_data['g3_values_requiring_g4'] else ''

        # Validate G5: Digital Literacy
        g5_value = request.POST.get('g5_digital_literacy', '').strip()
        if isinstance(g5_value, (tuple, list)):
            g5_value = g5_value[0] if g5_value else ''
        if not g5_value:
            errors.append("Please select an option for G5 Digital Literacy")
        elif g5_value not in context_data['valid_options']['g5_digital_literacy']:
            errors.append("Invalid value for G5 Digital Literacy")
        generic_answers['g5_digital_literacy'] = g5_value

        return generic_answers, errors, len(errors) == 0

    except Exception as e:
        logger.error(f"Error in validate_generic_questions_form: {str(e)}")
        errors.append("An unexpected error occurred during validation")
        return {}, errors, False


def generic_questions_view(request):
    """Render the generic questions page (step 3) and handle form submission."""
    # Check session prerequisites
    if not request.session.get('survey_started'):
        logger.warning("Survey not started, redirecting to welcome")
        return redirect('survey:welcome')
        
    if not request.session.get('respondent_info'):
        logger.warning("Respondent info missing, redirecting to respondent info")
        return redirect('survey:respondent_info')

    logger.debug(f"Generic questions view accessed - method: {request.method}")
    context_data = get_generic_questions_context()
    
    try:
        if request.method == 'POST':
            generic_answers, errors, is_valid = validate_generic_questions_form(request, context_data)
            
            if not is_valid:
                logger.warning(f"Validation errors in generic_questions: {errors}")
                context = get_progress_context(current_step=3, total_steps=6)
                context.update(context_data)
                context.update({
                    'generic_answers': generic_answers,
                    'generic_answers_json': json.dumps(generic_answers),
                    'error': "Please correct the following errors:\n" + "\n".join(errors)
                })
                return render(request, 'survey/generic_questions.html', context)

            # Save to session
            validate_session_size(request)
            request.session['generic_answers'] = generic_answers
            request.session.modified = True

            # Save to database
            respondent_id = request.session.get('respondent_info', {}).get('id')
            if respondent_id:
                survey_response = SurveyResponse.objects.get(id=respondent_id)
                survey_response.g1_policy_impact = generic_answers['g1']
                survey_response.g2_system_impact = generic_answers['g2']
                survey_response.g3_technical_issues = generic_answers['g3_technical_issues']
                survey_response.g4_disruption = generic_answers['g4_disruption']
                survey_response.g5_digital_literacy = generic_answers['g5_digital_literacy']
                survey_response.save()

            logger.info("Generic questions saved successfully, redirecting to legal practitioner section")
            return redirect('survey:role_specific_questions')
        
        # Handle GET request
        context = get_progress_context(current_step=3, total_steps=6)
        context.update(context_data)
        context.update({
            'respondent_id': request.session.get('respondent_info', {}).get('id', ''),
            'generic_answers': request.session.get('generic_answers', {'g1': {}, 'g2': {}}),
        })
        context['generic_answers_json'] = json.dumps(context['generic_answers'])
        logger.debug(f"Final context prepared for template with progress: {context}")
        return render(request, 'survey/generic_questions.html', context)
            
    except Exception as e:
        logger.error(f"Unexpected error in generic_questions_view: {e}")
        context = get_progress_context(current_step=3, total_steps=6)
        context.update(context_data)
        context.update({
            'generic_answers': request.session.get('generic_answers', {'g1': {}, 'g2': {}}),
            'generic_answers_json': json.dumps(request.session.get('generic_answers', {'g1': {}, 'g2': {}})),
            'error': "An unexpected error occurred. Please try again."
        })
        return render(request, 'survey/generic_questions.html', context)