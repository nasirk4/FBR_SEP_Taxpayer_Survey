from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from survey.utils.progress import get_progress_context
from survey.utils.session_utils import sanitize_input, validate_session_size
from survey.models import SurveyResponse
import logging
import json

logger = logging.getLogger(__name__)

def final_remarks_view(request):
    """Render the final remarks page (step 6)"""
    if not request.session.get('survey_started'):
        logger.warning(f"Redirecting to welcome: missing survey_started, session_id={request.session.session_key}")
        return redirect('survey:welcome')

    respondent_info = request.session.get('respondent_info', {})
    professional_roles = respondent_info.get('professional_roles', [])
    professional_role = 'both' if 'legal' in professional_roles and 'customs' in professional_roles else professional_roles[0] if professional_roles else ''

    if not professional_role:
        logger.error(f"No valid professional role found, session_id={request.session.session_key}")
        context = get_progress_context(current_step=6)
        context['error'] = "No professional role specified. Please start the survey again."
        return render(request, 'survey/final_remarks.html', context)

    if request.method == 'POST':
        # --- START NEW/UPDATED LOGIC ---
        final_remarks = sanitize_input(request.POST.get('final_remarks', '').strip())
        survey_feedback = sanitize_input(request.POST.get('survey_feedback', '').strip()) # NEW FIELD
        # --- END NEW/UPDATED LOGIC ---
        
        draft_save_attempt = request.POST.get('draft_save_attempt') == 'true' or 'save_draft' in request.POST
        confirm_submit = request.POST.get('confirm_submit') == 'true'

        logger.debug(f"POST received: final_remarks='{final_remarks[:50]}{'...' if len(final_remarks) > 50 else ''}', draft_save_attempt={draft_save_attempt}, confirm_submit={confirm_submit}, session_id={request.session.session_key}")

        # Handle draft saving
        if draft_save_attempt:
            try:
                request.session['final_remarks'] = final_remarks
                request.session['survey_feedback'] = survey_feedback # NEW: Save survey feedback to session
                request.session['final_remarks_timestamp'] = timezone.now().isoformat()
                request.session.modified = True
                logger.info(f"Draft saved: final_remarks='{final_remarks[:50]}{'...' if len(final_remarks) > 50 else ''}', timestamp={request.session['final_remarks_timestamp']}, session_id={request.session.session_key}")
                validate_session_size(request)
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Draft saved',
                        'final_remarks': final_remarks,
                        'survey_feedback': survey_feedback, # NEW: Include in response
                        'timestamp': request.session['final_remarks_timestamp']
                    })
                context = get_progress_context(current_step=6)
                context['success'] = 'Draft saved successfully'
                context['final_remarks'] = final_remarks
                context['survey_feedback'] = survey_feedback # NEW: Include in context
                context['professional_role'] = professional_role
                return render(request, 'survey/final_remarks.html', context)
            except Exception as e:
                logger.error(f"Error saving draft: {str(e)}, session_id={request.session.session_key}")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'error',
                        'message': f"Error saving draft: {str(e)}"
                    }, status=400)
                context = get_progress_context(current_step=6)
                context['error'] = f"Error saving draft: {str(e)}"
                context['final_remarks'] = final_remarks
                context['survey_feedback'] = survey_feedback # NEW: Include in context
                context['professional_role'] = professional_role
                return render(request, 'survey/final_remarks.html', context, status=400)

        # Handle final submission
        if confirm_submit:
            errors = []
            respondent_info = request.session.get('respondent_info', {})
            generic_answers = request.session.get('generic_answers', {})
            role_answers = request.session.get('role_specific_answers', {})
            cross_system_answers = request.session.get('cross_system_answers', {})
            email = respondent_info.get('email', '')

            # Define valid SurveyResponse fields
            valid_fields = {
                'full_name', 'email', 'mobile', 'province', 'district', 'professional_role',
                'experience_legal', 'experience_customs', 'practice_areas', 'kii_consent',
                'g1_policy_impact', 'g2_system_impact', 'g3_technical_issues', 'g4_disruption',
                'g5_digital_literacy', 'lp1_digital_support', 'lp2_challenges', 'lp3_challenges',
                'lp4_challenges', 'lp5_tax_types', 'lp5_visible', 'lp6_priority_improvement',
                'ca1_training', 'ca2_system_integration', 'ca3_challenges', 'ca4_effectiveness',
                'ca5_policy_impact', 'ca6_biggest_challenge', 'ca6_improvement',
                'cross_system_answers', 'final_remarks', 'survey_feedback', 'submission_date', 'reference_number' # ADDED: 'survey_feedback'
            }

            # Check required fields (survey_feedback is optional, final_remarks is required)
            required_role_fields = []
            if professional_role in ['legal', 'both']:
                required_role_fields.extend([
                    'lp1_digital_support', 'lp2_challenges', 'lp3_challenges', 'lp4_challenges'
                ])
            if professional_role in ['customs', 'both']:
                required_role_fields.extend([
                    'ca1_training', 'ca2_system_integration', 'ca3_challenges', 'ca4_effectiveness',
                    'ca5_policy_impact', 'ca6_biggest_challenge'
                ])

            for field in required_role_fields:
                value = role_answers.get(field)
                if not value or (isinstance(value, dict) and not value):
                    errors.append(f"Missing required field: {field.replace('_', ' ').title()}")

            if not final_remarks:
                errors.append("Please provide your final remarks before submitting")

            if errors:
                logger.warning(f"Validation errors in final_remarks: {errors}, session_id={request.session.session_key}")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'error',
                        'message': "Please complete all required sections:\n" + "\n".join(errors)
                    }, status=400)
                context = get_progress_context(current_step=6)
                context['error'] = "Please complete all required sections:\n" + "\n".join(errors)
                context['final_remarks'] = final_remarks
                context['survey_feedback'] = survey_feedback # NEW: Include in context
                context['professional_role'] = professional_role
                return render(request, 'survey/final_remarks.html', context, status=400)

            try:
                # Retrieve or create SurveyResponse
                survey_response = SurveyResponse.objects.filter(email=email).first()
                if not survey_response:
                    # Initializing a new instance with session data
                    survey_response = SurveyResponse(
                        full_name=sanitize_input(respondent_info.get('full_name', '')),
                        email=email,
                        mobile=sanitize_input(respondent_info.get('mobile', '')),
                        province=sanitize_input(respondent_info.get('province', '')),
                        district=sanitize_input(respondent_info.get('district', '')),
                        professional_role=','.join(professional_roles),
                        experience_legal=sanitize_input(respondent_info.get('experience_legal', '')),
                        experience_customs=sanitize_input(respondent_info.get('experience_customs', '')),
                        practice_areas=','.join(respondent_info.get('practice_areas', [])),
                        kii_consent=respondent_info.get('kii_consent', ''),
                        # Initialize fields to prevent DB errors on first save
                        g1_policy_impact={}, g2_system_impact={}, g3_technical_issues='', g4_disruption=None, g5_digital_literacy='',
                        lp1_digital_support='', lp2_challenges={}, lp3_challenges={}, lp4_challenges={}, lp5_tax_types={},
                        lp5_visible=False, lp6_priority_improvement='', ca1_training='', ca2_system_integration='',
                        ca3_challenges={}, ca4_effectiveness={}, ca5_policy_impact='', ca6_biggest_challenge='',
                        ca6_improvement='', cross_system_answers={}, final_remarks='', survey_feedback='', submission_date=None # ADDED: survey_feedback
                    )

                # Update SurveyResponse with session data
                for field in valid_fields:
                    if field == 'submission_date' or field == 'reference_number':
                        continue
                    
                    if field == 'final_remarks':
                        setattr(survey_response, field, final_remarks)
                        continue
                        
                    # --- NEW LOGIC: Handle survey_feedback separately ---
                    if field == 'survey_feedback':
                        setattr(survey_response, field, survey_feedback)
                        continue
                    # ----------------------------------------------------

                    if field in respondent_info:
                        value = respondent_info[field]
                        if field == 'practice_areas' and isinstance(value, list):
                            value = ','.join(value)
                        setattr(survey_response, field, value)
                    elif field in generic_answers:
                        value = generic_answers[field]
                        if isinstance(getattr(survey_response, field, None), dict) and isinstance(value, str):
                            try:
                                value = json.loads(value)
                            except json.JSONDecodeError:
                                logger.warning(f"Invalid JSON for {field}: {value}, resetting to empty dict, session_id={request.session.session_key}")
                                value = {}
                        setattr(survey_response, field, value)
                    elif field in role_answers:
                        value = role_answers[field]
                        if isinstance(getattr(survey_response, field, None), dict) and isinstance(value, str):
                            try:
                                value = json.loads(value)
                            except json.JSONDecodeError:
                                logger.warning(f"Invalid JSON for {field}: {value}, resetting to empty dict, session_id={request.session.session_key}")
                                value = {}
                        setattr(survey_response, field, value)
                    elif field == 'cross_system_answers': 
                        # Correctly assigns the entire dictionary stored in the session key to the model's JSONField
                        setattr(survey_response, field, cross_system_answers)

                survey_response.submission_date = timezone.now()

                # Log ignored session fields
                all_session_fields = {**respondent_info, **generic_answers, **role_answers, **cross_system_answers, 'survey_feedback': survey_feedback} # Added survey_feedback to check
                ignored_fields = [key for key in all_session_fields if key not in valid_fields and key not in ['final_remarks']]
                if ignored_fields:
                    logger.warning(f"Ignored unexpected session fields: {ignored_fields}, session_id={request.session.session_key}")

                survey_response.save()
                request.session['reference_number'] = survey_response.reference_number

                # Clear session data except reference_number
                for key in list(request.session.keys()):
                    if key != 'reference_number':
                        del request.session[key]

                logger.info(f"Survey submitted successfully, reference_number={survey_response.reference_number}, session_id={request.session.session_key}")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Survey submitted successfully',
                        'redirect_url': '/confirmation/'
                    })
                return redirect('survey:confirmation')

            except Exception as e:
                logger.error(f"Error saving survey: {str(e)}, session_id={request.session.session_key}")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'error',
                        'message': f"Error submitting survey: {str(e)}"
                    }, status=400)
                context = get_progress_context(current_step=6)
                context['error'] = "Error submitting survey. Please try again or contact support."
                context['final_remarks'] = final_remarks
                context['survey_feedback'] = survey_feedback # NEW: Include in context
                context['professional_role'] = professional_role
                return render(request, 'survey/final_remarks.html', context, status=400)

    # GET request - load existing data if any
    context = get_progress_context(current_step=6, total_steps=6)
    context['final_remarks'] = request.session.get('final_remarks', '')
    context['survey_feedback'] = request.session.get('survey_feedback', '') # NEW: Load survey feedback from session
    context['final_remarks_timestamp'] = request.session.get('final_remarks_timestamp', '')
    context['professional_role'] = professional_role
    logger.debug(f"Rendering final_remarks, session final_remarks='{context['final_remarks'][:50]}{'...' if len(context['final_remarks']) > 50 else ''}', timestamp={context['final_remarks_timestamp']}, session_id={request.session.session_key}")
    return render(request, 'survey/final_remarks.html', context)