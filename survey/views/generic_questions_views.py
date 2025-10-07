# survey/views/generic_questions_views.py
from django.shortcuts import render, redirect
from survey.utils.progress import get_progress_context
from survey.utils.session_utils import sanitize_input, validate_session_size
import logging

logger = logging.getLogger(__name__)

def get_generic_questions_context():
    """
    Return standardized context for generic questions form options.
    
    Returns:
        dict: Context with all question options and validation rules
    """
    challenged_groups = [
        ('limited_tax_understanding', 'People with limited tax understanding'),
        ('business_community', 'Business community'),
        ('salaried_class', 'Salaried class'),
        ('women_taxpayers', 'Women taxpayers'),
        ('differently_abled', 'Differently-abled taxpayers'),
        ('low_it_literacy', 'People with low IT literacy'),
        ('senior_citizens', 'Senior Citizens'),
        ('others', 'Others (please specify)'),
    ]
    
    g1_iris_rating_options = [
        ('1', 'Very user-friendly'),
        ('2', 'User-friendly'),
        ('3', 'Neutral'),
        ('4', 'Not user-friendly'),
        ('5', 'Not at all user-friendly'),
    ]
    
    g2_system_weaknesses_options = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]
    
    g5_options = [
        ('significantly_increased', 'Significantly increased'),
        ('slightly_increased', 'Slightly increased'),
        ('no_change', 'No change'),
        ('slightly_decreased', 'Slightly decreased'),
        ('significantly_decreased', 'Significantly decreased'),
    ]
    
    g6_options = [
        ('significantly_increased', 'Significantly increased'),
        ('slightly_increased', 'Slightly increased'),
        ('no_change', 'No change'),
        ('slightly_decreased', 'Slightly decreased'),
        ('significantly_decreased', 'Significantly decreased'),
    ]
    
    g7_options = [
        ('major_impact', 'Major impact'),
        ('moderate_impact', 'Moderate impact'),
        ('minor_impact', 'Minor impact'),
        ('no_impact', 'No impact'),
    ]
    
    g8_options = [
        ('yes_significantly', 'Yes, significantly'),
        ('yes_somewhat', 'Yes, somewhat'),
        ('no_similar', 'No, they are similar'),
        ('dont_know', 'I don\'t have enough information'),
    ]

    context = {
        'challenged_groups': challenged_groups,
        'g1_iris_rating_options': g1_iris_rating_options,
        'g2_system_weaknesses_options': g2_system_weaknesses_options,
        'g5_options': g5_options,
        'g6_options': g6_options,
        'g7_options': g7_options,
        'g8_options': g8_options,
        'valid_options': {
            'g1_iris_rating': [opt[0] for opt in g1_iris_rating_options],
            'g2_system_weaknesses': [opt[0] for opt in g2_system_weaknesses_options],
            'g5_clients_change': [opt[0] for opt in g5_options],
            'g6_fee_change': [opt[0] for opt in g6_options],
            'g7_digital_literacy_impact': [opt[0] for opt in g7_options],
            'g8_regional_differences': [opt[0] for opt in g8_options],
        }
    }
    return context

def validate_generic_questions_form(request, context_data):
    """
    Validate generic questions form data.
    
    Args:
        request: Django request object
        context_data: Context with validation rules
        
    Returns:
        tuple: (generic_answers, errors, is_valid)
    """
    errors = []
    generic_answers = {}

    try:
        # Required radio fields validation
        required_fields = [
            'g1_iris_rating', 'g2_system_weaknesses', 'g5_clients_change',
            'g6_fee_change', 'g7_digital_literacy_impact', 'g8_regional_differences'
        ]
        
        for field in required_fields:
            value = request.POST.get(field, '').strip()
            if not value:
                errors.append(f"Missing required field: {field.replace('_', ' ').title()} (G{field[1]})")
            elif value not in context_data['valid_options'][field]:
                errors.append(f"Invalid value for {field.replace('_', ' ').title()} (G{field[1]})")
            generic_answers[field] = value

        # G2: Platform limitations (optional)
        generic_answers['g2_platform_limitations'] = sanitize_input(
            request.POST.get('g2_platform_limitations', '')
        )

        # G3a: Conditional validation for system weaknesses details
        g2a_details = sanitize_input(request.POST.get('g2a_weaknesses_details', ''))
        if generic_answers.get('g2_system_weaknesses') == 'yes' and not g2a_details:
            errors.append("Please provide details for system weaknesses in G3a")
        generic_answers['g2a_weaknesses_details'] = g2a_details if generic_answers.get('g2_system_weaknesses') == 'yes' else ''

        # G4: Challenged groups (multiple selection with validation)
        g4_groups = request.POST.getlist('g4_challenged_groups', [])
        if not g4_groups:
            errors.append("Please select at least one challenged group in G4")
        if 'others' in g4_groups and not request.POST.get('g4_other_text', '').strip():
            errors.append("Please specify details for 'Others' in G4")
        generic_answers['g4_challenged_groups'] = g4_groups
        generic_answers['g4_other_text'] = sanitize_input(request.POST.get('g4_other_text', ''))

        # G8: Conditional validation for regional differences
        g8_details = sanitize_input(request.POST.get('g8_regional_differences_text', ''))
        if generic_answers.get('g8_regional_differences') in ['yes_significantly', 'yes_somewhat'] and not g8_details:
            errors.append("Please provide details for regional differences in G8")
        generic_answers['g8_regional_differences_text'] = g8_details if generic_answers.get('g8_regional_differences') in ['yes_significantly', 'yes_somewhat'] else ''

        is_valid = len(errors) == 0
        return generic_answers, errors, is_valid

    except Exception as e:
        logger.error(f"Error in validate_generic_questions_form: {e}")
        errors.append("An unexpected error occurred during validation")
        return {}, errors, False

def handle_generic_questions_post(request, context_data):
    """
    Handle POST request for generic questions form.
    
    Args:
        request: Django request object
        context_data: Context with form options
        
    Returns:
        HttpResponse: Redirect or render response
    """
    logger.debug("Processing generic questions POST request")
    
    generic_answers, errors, is_valid = validate_generic_questions_form(request, context_data)
    
    if not is_valid:
        logger.warning(f"Validation errors in generic_questions: {errors}")
        context = get_progress_context(current_step=3, total_steps=6)
        context.update(context_data)
        context['generic_answers'] = generic_answers
        context['error'] = "Please correct the following errors:\n" + "\n".join(errors)
        return render(request, 'survey/generic_questions.html', context)

    try:
        # Save to session
        validate_session_size(request)
        request.session['generic_answers'] = generic_answers
        request.session.modified = True
        
        logger.info("Generic questions saved successfully, redirecting to role-specific questions")
        return redirect('survey:role_specific_questions')
        
    except Exception as e:
        logger.error(f"Error saving generic answers: {e}")
        context = get_progress_context(current_step=3, total_steps=6)
        context.update(context_data)
        context['generic_answers'] = generic_answers
        context['error'] = "An error occurred while saving your responses. Please try again."
        return render(request, 'survey/generic_questions.html', context)

def handle_generic_questions_get(request, context_data):
    """
    Handle GET request for generic questions form.
    
    Args:
        request: Django request object
        context_data: Context with form options
        
    Returns:
        HttpResponse: Render response with form
    """
    logger.debug("Rendering generic questions GET request")
    
    # Get progress context with detailed logging
    logger.debug("Calling get_progress_context for step 3")
    progress_context = get_progress_context(current_step=3, total_steps=6)
    logger.debug(f"Progress context received: {progress_context}")
    
    # Build final context
    context = progress_context
    context.update(context_data)
    context['generic_answers'] = request.session.get('generic_answers', {})
    
    logger.debug(f"Final context prepared for template with progress: {progress_context}")
    return render(request, 'survey/generic_questions.html', context)

def generic_questions_view(request):
    """
    Render the generic questions page (step 3) and handle form submission.
    
    This view:
    - Validates session prerequisites
    - Handles both GET and POST requests
    - Manages form validation and error handling
    - Maintains progress tracking
    """
    # Session validation
    if not request.session.get('survey_started'):
        logger.warning("Survey not started, redirecting to welcome")
        return redirect('survey:welcome')
        
    if not request.session.get('respondent_info'):
        logger.warning("Respondent info missing, redirecting to respondent info")
        return redirect('survey:respondent_info')

    logger.debug(f"Generic questions view accessed - method: {request.method}")
    
    # Get form options context
    context_data = get_generic_questions_context()

    try:
        if request.method == 'POST':
            return handle_generic_questions_post(request, context_data)
        else:
            return handle_generic_questions_get(request, context_data)
            
    except Exception as e:
        logger.error(f"Unexpected error in generic_questions_view: {e}")
        context = get_progress_context(current_step=3, total_steps=6)
        context.update(context_data)
        context['error'] = "An unexpected error occurred. Please try again."
        return render(request, 'survey/generic_questions.html', context)

# Utility function for template debugging (optional)
def debug_progress_context():
    """
    Utility function to debug progress context calculation.
    Useful for testing in Django shell.
    """
    from .utils import get_progress_context
    context = get_progress_context(current_step=3, total_steps=6)
    print("Progress Context Debug:")
    print(f"  Step: {context.get('current_step')}")
    print(f"  Progress: {context.get('progress_percentage')}%")
    print(f"  Width: {context.get('progress_width')}")
    print(f"  Total Steps: {context.get('total_steps')}")
    return context