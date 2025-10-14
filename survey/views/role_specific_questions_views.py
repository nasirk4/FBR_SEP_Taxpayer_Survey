# survey/views/role_specific_questions_views.py

from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from survey.models import SurveyResponse
from survey.utils.progress import get_progress_context
from survey.utils.session_utils import sanitize_input, validate_session_size
import logging
import json

logger = logging.getLogger(__name__)

def get_role_specific_context(professional_role):
    """Return context for role-specific questions based on professional role"""
    context = {'valid_options': {}}
    if professional_role in ['legal', 'both']:
        context.update({
            'lp1_options': [
                ('great_extent', 'To a great extent'),
                ('considerable_extent', 'To a considerable extent'),
                ('moderate_extent', 'To a moderate extent'),
                ('slight_extent', 'To a slight extent'),
                ('not_at_all', 'Not at all'),
            ],
            'lp2_functions': [
                ('Appeal filings before Commissioner', 'S.127', 'appeals_commissioner'),
                ('Appellate Tribunal representations', 'S.132', 'appellate_tribunal'),
                ('High Court/Supreme Court references', '', 'high_court'),
                ('Audit responses & compliance', 'S.177', 'audit_responses'),
                ('Show cause notice responses', 'S.122', 'show_cause'),
            ],
            'lp3_functions': [
                ('Return filing & compliance', 'S.114', 'return_filing'),
                ('Return amendments & rectifications', '', 'amendments'),
                ('Withholding statements & compliance', '', 'withholding'),
                ('Risk assessment procedures', 'S.122A', 'risk_assessment'),
                ('Tax planning advisory services', '', 'tax_planning'),
            ],
            'lp4_functions': [
                ('Alternate Dispute Resolution', 'S.134A', 'adr'),
                ('Settlement procedures', '', 'settlement'),
                ('e-Payments & refund processing', '', 'epayments'),
                ('CPR corrections', '', 'cpr_corrections'),
                ('FBR correspondence management', '', 'correspondence'),
            ],
            'valid_options': {
                'lp1_digital_support': ['great_extent', 'considerable_extent', 'moderate_extent', 'slight_extent', 'not_at_all'],
                'lp2_challenge_levels': ['no_challenge', 'minor_challenge', 'moderate_challenge', 'major_challenge', 'dont_perform'],
                'lp3_challenge_levels': ['no_challenge', 'minor_challenge', 'moderate_challenge', 'major_challenge', 'dont_perform'],
                'lp4_challenge_levels': ['no_challenge', 'minor_challenge', 'moderate_challenge', 'major_challenge', 'dont_perform'],
            }
        })

    if professional_role in ['customs', 'both']:
        context.update({
            'ca1_options': [
                ('effective_both', 'Yes, effective training on both WeBOC and PSW'),
                ('needs_improvement', 'Yes, but training needs improvement'),
                ('no_training', 'No formal training received'),
                ('not_applicable', 'Not applicable'),
            ],
            'ca2_options': [
                ('very_well', 'Very well integrated'),
                ('well', 'Well integrated'),
                ('moderately', 'Moderately integrated'),
                ('poorly', 'Poorly integrated'),
                ('not_integrated', 'Not integrated'),
            ],
            'ca3_functions': [
                ('Goods Declaration', 'S.79', 'goods_declaration'),
                ('Duty Assessment', 'S.81', 'duty_assessment'),
                ('Cargo Examination', 'S.26', 'cargo_examination'),
                ('Document Processing', 'S.79(2)', 'document_processing'),
                ('Transit/Warehousing', 'S.13, S.15', 'transit_warehousing'),
                ('Record Keeping', 'S.155(6)', 'record_keeping'),
                ('Audit Compliance', 'S.26A', 'audit_compliance'),
                ('License Compliance', 'S.155(4)', 'license_compliance'),
            ],
            'ca4_processes': [
                ('Duty assessment', 'duty_assessment'),
                ('Cargo examination', 'cargo_examination'),
                ('System reliability', 'system_reliability'),
                ('Client representation', 'client_representation'),
            ],
            'ca5_options': [
                ('very_positively', 'Very positively'),
                ('positively', 'Positively'),
                ('neutral', 'Neutral'),
                ('negatively', 'Negatively'),
                ('very_negatively', 'Very negatively'),
            ],
            'ca6_challenge_options': [
                ('system_issues', 'System reliability and performance issues'),
                ('policy_changes', 'Frequent policy or procedural changes'),
                ('assessment_unpredictability', 'Unpredictable assessment outcomes'),
                ('documentation_delays', 'Documentation processing delays'),
                ('cargo_bottlenecks', 'Cargo examination bottlenecks'),
                ('compliance_burden', 'Compliance and record-keeping burden'),
                ('coordination_issues', 'Inter-agency coordination challenges'),
                ('training_gaps', 'Training and knowledge gaps'),
            ],
            'valid_options': {
                **context['valid_options'],  # Merge with existing valid_options
                'ca1_training': ['effective_both', 'needs_improvement', 'no_training', 'not_applicable'],
                'ca2_system_integration': ['very_well', 'well', 'moderately', 'poorly', 'not_integrated'],
                'ca3_challenge_levels': ['no_challenge', 'minor_challenge', 'moderate_challenge', 'major_challenge', 'not_applicable'],
                'ca4_effectiveness_levels': ['very_effective', 'effective', 'neutral', 'ineffective', 'very_ineffective'],
                'ca5_policy_impact': ['very_positively', 'positively', 'neutral', 'negatively', 'very_negatively'],
                'ca6_biggest_challenge': ['system_issues', 'policy_changes', 'assessment_unpredictability', 'documentation_delays', 'cargo_bottlenecks', 'compliance_burden', 'coordination_issues', 'training_gaps'],
            }
        })
    return context

def preprocess_grid_data(professional_role, role_answers, context_data):
    """Preprocess grid data for template rendering"""
    if professional_role in ['legal', 'both']:
        lp2_functions_with_data = []
        lp3_functions_with_data = []
        lp4_functions_with_data = []
        
        for function, statute, value in context_data.get('lp2_functions', []):
            challenge_value = role_answers.get('lp2_challenges', {}).get(value, '')
            lp2_functions_with_data.append((function, statute, value, challenge_value))
        
        for function, statute, value in context_data.get('lp3_functions', []):
            challenge_value = role_answers.get('lp3_challenges', {}).get(value, '')
            lp3_functions_with_data.append((function, statute, value, challenge_value))
            
        for function, statute, value in context_data.get('lp4_functions', []):
            challenge_value = role_answers.get('lp4_challenges', {}).get(value, '')
            lp4_functions_with_data.append((function, statute, value, challenge_value))
        
        context_data['lp2_functions_with_data'] = lp2_functions_with_data
        context_data['lp3_functions_with_data'] = lp3_functions_with_data
        context_data['lp4_functions_with_data'] = lp4_functions_with_data

    if professional_role in ['customs', 'both']:
        ca3_functions_with_data = []
        ca4_processes_with_data = []
        
        for function, statute, value in context_data.get('ca3_functions', []):
            challenge_value = role_answers.get('ca3_challenges', {}).get(value, '')
            ca3_functions_with_data.append((function, statute, value, challenge_value))
            
        for process, value in context_data.get('ca4_processes', []):
            effectiveness_value = role_answers.get('ca4_effectiveness', {}).get(value, '')
            ca4_processes_with_data.append((process, value, effectiveness_value))
        
        context_data['ca3_functions_with_data'] = ca3_functions_with_data
        context_data['ca4_processes_with_data'] = ca4_processes_with_data
    
    return context_data

def role_specific_questions_view(request):
    """Render the role-specific questions page (step 4)"""
    if not request.session.get('survey_started') or not request.session.get('respondent_info') or not request.session.get('generic_answers'):
        logger.warning("Invalid session data, redirecting to welcome page")
        return redirect('survey:welcome')

    respondent_info = request.session.get('respondent_info', {})
    professional_roles = respondent_info.get('professional_roles', [])
    professional_role = 'both' if 'legal' in professional_roles and 'customs' in professional_roles else professional_roles[0] if professional_roles else ''
    
    logger.debug(f"Professional role: {professional_role}, Roles: {professional_roles}")

    if not professional_role:
        logger.error("No valid professional role found in session")
        return render(request, 'survey/role_specific.html', {
            'error': "No professional role specified. Please start the survey again.",
            **get_progress_context(current_step=4)
        })

    context_data = get_role_specific_context(professional_role)
    role_answers = request.session.get('role_specific_answers', {})

    # Validate and clean lp5_tax_types in session to prevent invalid JSON
    if 'lp5_tax_types' in role_answers:
        try:
            if isinstance(role_answers['lp5_tax_types'], str):
                json.loads(role_answers['lp5_tax_types'])
                role_answers['lp5_tax_types'] = json.loads(role_answers['lp5_tax_types'])
            elif not isinstance(role_answers['lp5_tax_types'], dict):
                logger.warning(f"Invalid lp5_tax_types in session: {role_answers['lp5_tax_types']}, resetting to an empty dict")
                role_answers['lp5_tax_types'] = {}
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON in lp5_tax_types: {role_answers['lp5_tax_types']}, resetting to an empty dict")
            role_answers['lp5_tax_types'] = {}
    else:
        role_answers['lp5_tax_types'] = {}

    # Convert Python dict to proper JSON string for the template
    try:
        lp5_tax_types_json = json.dumps(role_answers['lp5_tax_types'])
        logger.debug(f"LP5 tax types JSON: {lp5_tax_types_json}")
    except Exception as e:
        logger.error(f"Error serializing LP5 tax types: {e}")
        lp5_tax_types_json = "{}"
    
    context_data = preprocess_grid_data(professional_role, role_answers, context_data)

    if request.method == 'POST':
        errors = []
        role_answers = request.session.get('role_specific_answers', {})

        # Retrieve or create SurveyResponse instance
        email = respondent_info.get('email', '')
        survey_response = SurveyResponse.objects.filter(email=email).first()
        if not survey_response:
            survey_response = SurveyResponse(
                full_name=respondent_info.get('full_name', ''),
                email=email,
                mobile=respondent_info.get('mobile', ''),
                province=respondent_info.get('province', ''),
                district=respondent_info.get('district', ''),
                professional_role=','.join(professional_roles),
                experience_legal=respondent_info.get('experience_legal', ''),
                experience_customs=respondent_info.get('experience_customs', ''),
                practice_areas=','.join(respondent_info.get('practice_areas', [])),
                kii_consent=respondent_info.get('kii_consent', ''),
                g1_policy_impact={},
                g2_system_impact={},
                g3_technical_issues='',
                g4_disruption=None,
                g5_digital_literacy='',
                lp1_digital_support='',
                lp2_challenges={},
                lp3_challenges={},
                lp4_challenges={},
                lp5_tax_types={},
                lp5_visible=False,
                lp6_priority_improvement='',
                ca1_training='',
                ca2_system_integration='',
                ca3_challenges={},
                ca4_effectiveness={},
                ca5_policy_impact='',
                ca6_biggest_challenge='',
                ca6_improvement='',
                cross_system_answers={},
                final_remarks='',
                submission_date=None
            )
        logger.debug(f"SurveyResponse for {email}: lp6={survey_response.lp6_priority_improvement}, ca6_improvement={survey_response.ca6_improvement}")

        if professional_role in ['legal', 'both']:
            # LP1: Overall Digital Support
            lp1_value = request.POST.get('lp1_digital_support', '').strip()
            if 'lp1_digital_support' in context_data['valid_options']:
                if not lp1_value:
                    errors.append("Please select an option for LP1 (Overall Digital Support)")
                elif lp1_value not in context_data['valid_options']['lp1_digital_support']:
                    errors.append("Invalid value for LP1")
                else:
                    role_answers['lp1_digital_support'] = lp1_value
                    survey_response.lp1_digital_support = lp1_value
            else:
                logger.warning("LP1 validation skipped: lp1_digital_support not in valid_options")

            # LP2: Representation & Appeals Grid
            lp2_challenges = {}
            for function_data in context_data.get('lp2_functions', []):
                function_value = function_data[2]
                challenge_value = request.POST.get(f'lp2_{function_value}', '').strip()
                if not challenge_value:
                    errors.append("Please complete all rows in LP2 (Representation & Appeals)")
                    break
                elif challenge_value not in context_data['valid_options'].get('lp2_challenge_levels', []):
                    errors.append(f"Invalid value for {function_data[0]} in LP2")
                    break
                lp2_challenges[function_value] = challenge_value
            role_answers['lp2_challenges'] = lp2_challenges
            survey_response.lp2_challenges = lp2_challenges

            # LP3: Compliance & Advisory Grid
            lp3_challenges = {}
            for function_data in context_data.get('lp3_functions', []):
                function_value = function_data[2]
                challenge_value = request.POST.get(f'lp3_{function_value}', '').strip()
                if not challenge_value:
                    errors.append("Please complete all rows in LP3 (Compliance & Advisory)")
                    break
                elif challenge_value not in context_data['valid_options'].get('lp3_challenge_levels', []):
                    errors.append(f"Invalid value for {function_data[0]} in LP3")
                    break
                lp3_challenges[function_value] = challenge_value
            role_answers['lp3_challenges'] = lp3_challenges
            survey_response.lp3_challenges = lp3_challenges

            # LP4: Dispute Resolution & Documentation Grid
            lp4_challenges = {}
            for function_data in context_data.get('lp4_functions', []):
                function_value = function_data[2]
                challenge_value = request.POST.get(f'lp4_{function_value}', '').strip()
                if not challenge_value:
                    errors.append("Please complete all rows in LP4 (Dispute Resolution & Documentation)")
                    break
                elif challenge_value not in context_data['valid_options'].get('lp4_challenge_levels', []):
                    errors.append(f"Invalid value for {function_data[0]} in LP4")
                    break
                lp4_challenges[function_value] = challenge_value
            role_answers['lp4_challenges'] = lp4_challenges
            survey_response.lp4_challenges = lp4_challenges

            # LP5: Tax-Type Impact (conditional)
            lp5_visible = request.POST.get('lp5_visible', '0') == '1'
            lp5_tax_types = {}
            if lp5_visible:
                all_challenges = {**lp2_challenges, **lp3_challenges, **lp4_challenges}
                challenging_functions = [
                    func for func, level in all_challenges.items()
                    if level in ['moderate_challenge', 'major_challenge']
                ]
                for function in challenging_functions:
                    income_tax = bool(request.POST.get(f'lp5_{function}_income', ''))
                    sales_tax = bool(request.POST.get(f'lp5_{function}_sales', ''))
                    if not income_tax and not sales_tax:
                        errors.append(f"Please indicate tax types for {function} in LP5")
                        break
                    lp5_tax_types[function] = {
                        'income_tax': income_tax,
                        'sales_tax': sales_tax
                    }
            role_answers['lp5_tax_types'] = lp5_tax_types
            survey_response.lp5_tax_types = lp5_tax_types
            role_answers['lp5_visible'] = lp5_visible
            survey_response.lp5_visible = lp5_visible

            # LP6: Priority Improvement (optional)
            lp6_improvement = sanitize_input(request.POST.get('lp6_priority_improvement', '')).strip()
            logger.debug(f"LP6 value: {lp6_improvement}")
            role_answers['lp6_priority_improvement'] = lp6_improvement
            survey_response.lp6_priority_improvement = lp6_improvement

        if professional_role in ['customs', 'both']:
            # CA1: Training
            ca1_value = request.POST.get('ca1_training', '').strip()
            if 'ca1_training' in context_data['valid_options']:
                if not ca1_value:
                    errors.append("Please select an option for CA1 (Training)")
                elif ca1_value not in context_data['valid_options']['ca1_training']:
                    errors.append("Invalid value for CA1")
                else:
                    role_answers['ca1_training'] = ca1_value
                    survey_response.ca1_training = ca1_value
            else:
                logger.warning("CA1 validation skipped: ca1_training not in valid_options")

            # CA2: System Integration
            ca2_value = request.POST.get('ca2_system_integration', '').strip()
            if 'ca2_system_integration' in context_data['valid_options']:
                if not ca2_value:
                    errors.append("Please select an option for CA2 (System Integration)")
                elif ca2_value not in context_data['valid_options']['ca2_system_integration']:
                    errors.append("Invalid value for CA2")
                else:
                    role_answers['ca2_system_integration'] = ca2_value
                    survey_response.ca2_system_integration = ca2_value
            else:
                logger.warning("CA2 validation skipped: ca2_system_integration not in valid_options")

            # CA3: Customs Function Challenges Grid
            ca3_challenges = {}
            ca3_has_errors = False
            for function_data in context_data.get('ca3_functions', []):
                function_value = function_data[2]
                challenge_value = request.POST.get(f'ca3_{function_value}', '').strip()
                if not challenge_value:
                    if not ca3_has_errors:
                        errors.append("Please complete all rows in CA3 (Customs Function Challenges)")
                        ca3_has_errors = True
                elif challenge_value not in context_data['valid_options'].get('ca3_challenge_levels', []):
                    if not ca3_has_errors:
                        errors.append(f"Invalid value for {function_data[0]} in CA3")
                        ca3_has_errors = True
                ca3_challenges[function_value] = challenge_value
            role_answers['ca3_challenges'] = ca3_challenges
            survey_response.ca3_challenges = ca3_challenges

            # CA4: Process Effectiveness Grid
            ca4_effectiveness = {}
            for process_data in context_data.get('ca4_processes', []):
                process_value = process_data[1]
                effectiveness_value = request.POST.get(f'ca4_{process_value}', '').strip()
                if not effectiveness_value:
                    errors.append("Please complete all rows in CA4 (Process Effectiveness)")
                    break
                elif effectiveness_value not in context_data['valid_options'].get('ca4_effectiveness_levels', []):
                    errors.append(f"Invalid value for {process_data[0]} in CA4")
                    break
                ca4_effectiveness[process_value] = effectiveness_value
            role_answers['ca4_effectiveness'] = ca4_effectiveness
            survey_response.ca4_effectiveness = ca4_effectiveness

            # CA5: Policy Impact
            ca5_value = request.POST.get('ca5_policy_impact', '').strip()
            if 'ca5_policy_impact' in context_data['valid_options']:
                if not ca5_value:
                    errors.append("Please select an option for CA5 (Policy Impact)")
                elif ca5_value not in context_data['valid_options']['ca5_policy_impact']:
                    errors.append("Invalid value for CA5")
                else:
                    role_answers['ca5_policy_impact'] = ca5_value
                    survey_response.ca5_policy_impact = ca5_value
            else:
                logger.warning("CA5 validation skipped: ca5_policy_impact not in valid_options")

            # CA6: Combined Challenge & Improvement
            ca6_challenge = request.POST.get('ca6_biggest_challenge', '').strip()
            ca6_improvement = sanitize_input(request.POST.get('ca6_improvement', '')).strip()
            if 'ca6_biggest_challenge' in context_data['valid_options']:
                if not ca6_challenge:
                    errors.append("Please select your biggest challenge in CA6")
                elif ca6_challenge not in context_data['valid_options']['ca6_biggest_challenge']:
                    errors.append("Invalid value for CA6 challenge")
            else:
                logger.warning("CA6 validation skipped: ca6_biggest_challenge not in valid_options")
            logger.debug(f"CA6 improvement value: {ca6_improvement}")
            role_answers['ca6_biggest_challenge'] = ca6_challenge
            role_answers['ca6_improvement'] = ca6_improvement
            survey_response.ca6_biggest_challenge = ca6_challenge
            survey_response.ca6_improvement = ca6_improvement

        if errors:
            logger.warning(f"Validation errors in role_specific_questions: {errors}")
            context_data = preprocess_grid_data(professional_role, role_answers, context_data)
            context = get_progress_context(current_step=4)
            context.update({
                'professional_role': professional_role,
                'is_legal': professional_role in ['legal', 'both'],
                'is_customs': professional_role in ['customs', 'both'],
                'role_specific_answers': role_answers,
                'lp5_tax_types_json': json.dumps(role_answers['lp5_tax_types']),
                'error': "Please correct the following errors:\n" + "\n".join(errors)
            })
            context.update(context_data)
            return render(request, 'survey/role_specific.html', context)

        try:
            logger.debug(f"Before saving session: role_specific_answers={role_answers}")
            survey_response.save()
            logger.debug(f"Saved role-specific answers for {email}: lp6={survey_response.lp6_priority_improvement}, ca6_improvement={survey_response.ca6_improvement}")
            request.session['role_specific_answers'] = role_answers
            request.session.modified = True
            logger.debug(f"After saving session: role_specific_answers={request.session['role_specific_answers']}")
            validate_session_size(request)
            return redirect('survey:cross_system_perspectives')
        except Exception as e:
            logger.error(f"Error saving role-specific answers: {str(e)}", exc_info=True)
            context_data = preprocess_grid_data(professional_role, role_answers, context_data)
            context = get_progress_context(current_step=4)
            context.update({
                'professional_role': professional_role,
                'is_legal': professional_role in ['legal', 'both'],
                'is_customs': professional_role in ['customs', 'both'],
                'role_specific_answers': role_answers,
                'lp5_tax_types_json': json.dumps(role_answers['lp5_tax_types']),
                'error': f"Error saving data: {str(e)}"
            })
            context.update(context_data)
            return render(request, 'survey/role_specific.html', context)

    context = get_progress_context(current_step=4, total_steps=6)
    context.update({
        'professional_role': professional_role,
        'is_legal': professional_role in ['legal', 'both'],
        'is_customs': professional_role in ['customs', 'both'],
        'role_specific_answers': role_answers,
        'lp5_tax_types_json': lp5_tax_types_json
    })
    context.update(context_data)
    return render(request, 'survey/role_specific.html', context)