# survey/views/final_remarks_views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from survey.utils.progress import get_progress_context
from survey.utils.session_utils import sanitize_input, validate_session_size
from ..models import SurveyResponse
import logging

logger = logging.getLogger(__name__)

def final_remarks_view(request):
    """Render the final remarks page (step 6)"""
    if not request.session.get('survey_started'):
        logger.warning(f"Redirecting to welcome: missing survey_started, session_id={request.session.session_key}")
        return redirect('survey:welcome')

    if request.method == 'POST':
        final_remarks = sanitize_input(request.POST.get('final_remarks', '').strip())
        logger.debug(f"POST received: final_remarks='{final_remarks[:50]}{'...' if len(final_remarks) > 50 else ''}', draft_save_attempt={request.POST.get('draft_save_attempt')}, confirm_submit={request.POST.get('confirm_submit')}, session_id={request.session.session_key}")

        # Handle draft saving
        if 'save_draft' in request.POST or 'draft_save_attempt' in request.POST:
            try:
                request.session['final_remarks'] = final_remarks
                request.session['final_remarks_timestamp'] = timezone.now().isoformat()
                request.session.modified = True
                logger.info(f"Draft saved: final_remarks='{final_remarks[:50]}{'...' if len(final_remarks) > 50 else ''}', timestamp={request.session['final_remarks_timestamp']}, session_id={request.session.session_key}")
                validate_session_size(request)
                return JsonResponse({
                    'status': 'success',
                    'message': 'Draft saved',
                    'final_remarks': final_remarks,
                    'timestamp': request.session['final_remarks_timestamp']
                })
            except Exception as e:
                logger.error(f"Error saving draft: {str(e)}, session_id={request.session.session_key}")
                return JsonResponse({
                    'status': 'error',
                    'message': f"Error saving draft: {str(e)}"
                }, status=400)

        # Handle final submission
        if 'confirm_submit' in request.POST:
            errors = []
            respondent_info = request.session.get('respondent_info', {})
            generic_answers = request.session.get('generic_answers', {})
            role_answers = request.session.get('role_specific_answers', {})
            cross_system_answers = request.session.get('cross_system_answers', {})

            professional_role = respondent_info.get('professional_role', '')
            required_role_fields = []
            if professional_role in ['legal', 'both']:
                required_role_fields.extend([
                    'lp1_technical_issues', 'lp6_filing_efficiency', 'lp7_case_tracking',
                    'lp8_notice_communication', 'lp9_law_accessibility', 'lp10_law_change_impact',
                    'lp11_adr_effectiveness', 'lp12_dispute_transparency', 'lp13_overall_satisfaction'
                ])
            if professional_role in ['customs', 'both']:
                required_role_fields.extend([
                    'ca1_training_received', 'ca2_psw_weboc_integration', 'ca5_duty_assessment',
                    'ca6_cargo_efficiency', 'ca9_system_reliability', 'ca10_policy_impact'
                ])

            # Check required fields
            for field in required_role_fields:
                if not role_answers.get(field):
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
                return render(request, 'survey/final_remarks.html', context)

            try:
                # Map outdated session keys to current model fields
                role_answers_mapped = role_answers.copy()
                # Map old CA fields to new ones
                field_mappings = {
                    'ca3_procedure_challenges': 'ca4_procedure_challenges',
                    'ca3_other_text': 'ca4_other_text',
                    'ca4_duty_assessment': 'ca5_duty_assessment',
                    'ca5_psw_vs_weboc': 'ca3_psw_comparison',
                    'ca7_system_reliability': 'ca9_system_reliability',
                    'ca8_policy_impact': 'ca10_policy_impact',
                    'ca9_operational_challenges': 'ca12_operational_challenges',
                    'ca9_other_text': 'ca12_other_text',
                    'ca9_feedback': 'ca13_other_text',
                    'lp13_feedback': 'final_feedback',  # Map lp13_feedback to final_feedback
                }
                for old_key, new_key in field_mappings.items():
                    if old_key in role_answers_mapped:
                        role_answers_mapped[new_key] = role_answers_mapped.pop(old_key)

                # Create survey response
                survey_response = SurveyResponse(
                    # Respondent Information
                    full_name=sanitize_input(respondent_info.get('full_name', '')),
                    email=respondent_info.get('email', ''),
                    district=respondent_info.get('district', ''),
                    mobile=sanitize_input(respondent_info.get('mobile', '')),
                    professional_role=professional_role,
                    province=sanitize_input(respondent_info.get('province', '')),
                    experience_legal=sanitize_input(respondent_info.get('experience_legal', '')),
                    experience_customs=sanitize_input(respondent_info.get('experience_customs', '')),

                    # General Questions
                    g1_iris_rating=generic_answers.get('g1_iris_rating', ''),
                    g2_system_weaknesses=generic_answers.get('g2_system_weaknesses', ''),
                    g2a_weaknesses_details=sanitize_input(generic_answers.get('g2a_weaknesses_details', '')),
                    g3_iris_limitations=sanitize_input(generic_answers.get('g3_iris_limitations', '')),
                    g4_challenged_groups=generic_answers.get('g4_challenged_groups', []),
                    g4_other_text=sanitize_input(generic_answers.get('g4_other_text', '')),
                    g5_clients_change=generic_answers.get('g5_clients_change', ''),
                    g6_fee_change=generic_answers.get('g6_fee_change', ''),
                    g7_digital_literacy_impact=generic_answers.get('g7_digital_literacy_impact', ''),
                    g8_regional_differences=generic_answers.get('g8_regional_differences', ''),
                    g8_regional_differences_text=sanitize_input(generic_answers.get('g8_regional_differences_text', '')),

                    # Legal Practitioner Questions
                    lp1_technical_issues=role_answers_mapped.get('lp1_technical_issues', ''),
                    lp2_common_problems=role_answers_mapped.get('lp2_common_problems', []),
                    lp2_other_text=sanitize_input(role_answers_mapped.get('lp2_other_text', '')),
                    lp3_improvement_areas=role_answers_mapped.get('lp3_improvement_areas', []),
                    lp3_other_text=sanitize_input(role_answers_mapped.get('lp3_other_text', '')),
                    lp4_procedures=role_answers_mapped.get('lp4_procedures', {}),
                    lp4_other_procedure=role_answers_mapped.get('lp4_other_procedure', ''),
                    lp4_other_sales=role_answers_mapped.get('lp4_other_sales', False),
                    lp4_other_income=role_answers_mapped.get('lp4_other_income', False),
                    lp4_other_comment=sanitize_input(role_answers_mapped.get('lp4_other_comment', '')),
                    lp5_representation_challenges=role_answers_mapped.get('lp5_representation_challenges', []),
                    lp5_other_text=sanitize_input(role_answers_mapped.get('lp5_other_text', '')),
                    lp6_filing_efficiency=role_answers_mapped.get('lp6_filing_efficiency', ''),
                    lp6_qualitative_text=sanitize_input(role_answers_mapped.get('lp6_qualitative_text', '')),
                    lp6_qualitative_visible=role_answers_mapped.get('lp6_qualitative_visible', False),
                    lp7_case_tracking=role_answers_mapped.get('lp7_case_tracking', ''),
                    lp8_notice_communication=role_answers_mapped.get('lp8_notice_communication', ''),
                    lp8_qualitative_text=sanitize_input(role_answers_mapped.get('lp8_qualitative_text', '')),
                    lp8_qualitative_visible=role_answers_mapped.get('lp8_qualitative_visible', False),
                    lp9_law_accessibility=role_answers_mapped.get('lp9_law_accessibility', ''),
                    lp10_law_change_impact=role_answers_mapped.get('lp10_law_change_impact', ''),
                    lp10_qualitative_text=sanitize_input(role_answers_mapped.get('lp10_qualitative_text', '')),
                    lp10_qualitative_visible=role_answers_mapped.get('lp10_qualitative_visible', False),
                    lp11_adr_effectiveness=role_answers_mapped.get('lp11_adr_effectiveness', ''),
                    lp12_dispute_transparency=role_answers_mapped.get('lp12_dispute_transparency', ''),
                    lp13_overall_satisfaction=role_answers_mapped.get('lp13_overall_satisfaction', ''),
                    final_feedback=sanitize_input(role_answers_mapped.get('final_feedback', '')),

                    # Customs Agent Questions
                    ca1_training_received=role_answers_mapped.get('ca1_training_received', ''),
                    ca1a_training_usefulness=role_answers_mapped.get('ca1a_training_usefulness', ''),
                    ca2_psw_weboc_integration=role_answers_mapped.get('ca2_psw_weboc_integration', ''),
                    ca3_psw_comparison=role_answers_mapped.get('ca3_psw_comparison', ''),
                    ca4_procedure_challenges=role_answers_mapped.get('ca4_procedure_challenges', []),
                    ca4_other_text=sanitize_input(role_answers_mapped.get('ca4_other_text', '')),
                    ca5_duty_assessment=role_answers_mapped.get('ca5_duty_assessment', ''),
                    ca6_cargo_efficiency=role_answers_mapped.get('ca6_cargo_efficiency', ''),
                    ca7_document_verification=role_answers_mapped.get('ca7_document_verification', ''),
                    ca8_agency_coordination=role_answers_mapped.get('ca8_agency_coordination', ''),
                    ca9_system_reliability=role_answers_mapped.get('ca9_system_reliability', ''),
                    ca10_policy_impact=role_answers_mapped.get('ca10_policy_impact', ''),
                    ca11_client_representation=role_answers_mapped.get('ca11_client_representation', ''),
                    ca12_operational_challenges=role_answers_mapped.get('ca12_operational_challenges', []),
                    ca12_other_text=sanitize_input(role_answers_mapped.get('ca12_other_text', '')),
                    ca13_biggest_challenge=role_answers_mapped.get('ca13_biggest_challenge', ''),
                    ca13_other_text=sanitize_input(role_answers_mapped.get('ca13_other_text', '')),

                    # Cross-System Perspectives
                    cross_system_answers=cross_system_answers,

                    # Final Remarks
                    final_remarks=final_remarks
                )

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
                return render(request, 'survey/final_remarks.html', context)

    # GET request - load existing data if any
    context = get_progress_context(current_step=6, total_steps=6)
    context['final_remarks'] = request.session.get('final_remarks', '')
    context['final_remarks_timestamp'] = request.session.get('final_remarks_timestamp', '')
    logger.debug(f"Rendering final_remarks, session final_remarks='{context['final_remarks'][:50]}{'...' if len(context['final_remarks']) > 50 else ''}', timestamp={context['final_remarks_timestamp']}, session_id={request.session.session_key}")
    return render(request, 'survey/final_remarks.html', context)