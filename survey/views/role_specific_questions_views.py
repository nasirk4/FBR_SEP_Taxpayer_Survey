from django.shortcuts import render, redirect
from survey.utils.progress import get_progress_context
from survey.utils.session_utils import sanitize_input, validate_session_size
import logging

logger = logging.getLogger(__name__)

def get_role_specific_context(professional_role):
    """Return context for role-specific questions based on professional role"""
    context = {}
    if professional_role in ['legal', 'both']:
        context.update({
            'lp1_options': [
                ('very_frequently', 'Very frequently'),
                ('frequently', 'Frequently'),
                ('occasionally', 'Occasionally'),
                ('rarely', 'Rarely'),
                ('never', 'Never'),
            ],
            'lp2_options': [
                ('system_downtime', 'System downtime or slow performance'),
                ('login_failures', 'Login failures or session timeouts'),
                ('document_upload_errors', 'Document upload errors'),
                ('access_issues', 'Inability to access case records or notices'),
                ('data_mismatches', 'Data mismatches in client records'),
                ('audit_trail_issues', 'Lack of audit trail for actions taken'),
                ('vague_notices', 'Vague or inconsistent system-generated notices'),
                ('client_management', 'Limited functionality for managing multiple clients'),
                ('other', 'Other (please specify)'),
            ],
            'lp3_options': [
                ('system_stability', 'System stability and uptime'),
                ('user_interface', 'User interface for legal filings'),
                ('document_management', 'Document management and submission'),
                ('case_tracking', 'Case status tracking and updates'),
                ('appellate_integration', 'Integration with appellate tribunal systems'),
                ('legal_research', 'Legal research and database access'),
                ('notification_system', 'Notification and alert system'),
                ('other', 'Other (please specify)'),
            ],
            'lp4_procedures': [
                ('Registration', 'registration', ''),
                ('Return Filing', 'return_filing', ''),
                ('Refund Claims', 'refund_claims', ''),
                ('Audit Compliance', 'audit_compliance', ''),
                ('Appeals', 'appeals', ''),
                ('Correspondence', 'correspondence', ''),
            ],
            'lp5_options': [
                ('commissioner_appeals', 'Appeal filings before Commissioner (Appeals)'),
                ('appellate_tribunal', 'Appellate Tribunal representations'),
                ('high_court', 'High Court/Supreme Court references'),
                ('audit_response', 'Audit response proceedings'),
                ('show_cause', 'Show cause notice responses'),
                ('refund_processing', 'Refund claim processing'),
                ('settlement', 'Settlement applications'),
                ('adr', 'Alternate Dispute Resolution (ADR)'),
                ('other', 'Other (please specify)'),
            ],
            'lp6_options': [
                ('very_efficient', 'Very efficient'),
                ('efficient', 'Efficient'),
                ('moderately_efficient', 'Moderately efficient'),
                ('inefficient', 'Inefficient'),
                ('very_inefficient', 'Very inefficient'),
            ],
            'lp7_options': [
                ('very_effective', 'Very effective - real-time updates'),
                ('effective', 'Effective - adequate information'),
                ('moderately_effective', 'Moderately effective - basic information'),
                ('ineffective', 'Ineffective - limited access'),
                ('very_ineffective', 'Very ineffective - no reliable tracking'),
            ],
            'lp8_options': [
                ('very_effective', 'Very effective - timely and clear'),
                ('effective', 'Effective - adequate with minor issues'),
                ('moderately_effective', 'Moderately effective - some delays'),
                ('inefficient', 'Ineffective - frequent delays'),
                ('very_ineffective', 'Very ineffective - unreliable'),
            ],
            'lp9_options': [
                ('very_accessible', 'Very accessible - comprehensive database'),
                ('accessible', 'Accessible - adequate resources'),
                ('moderately_accessible', 'Moderately accessible - basic access'),
                ('not_very_accessible', 'Not very accessible - limited resources'),
                ('not_accessible', 'Not accessible at all'),
            ],
            'lp10_options': [
                ('significant_negative', 'Significant negative impact'),
                ('moderate_negative', 'Moderate negative impact'),
                ('minor_impact', 'Minor impact'),
                ('no_impact', 'No impact'),
                ('positive_impact', 'Positive impact'),
            ],
            'lp11_options': [
                ('very_effective', 'Very effective'),
                ('effective', 'Effective'),
                ('moderately_effective', 'Moderately effective'),
                ('inefficient', 'Ineffective'),
                ('very_inefficient', 'Very inefficient'),
            ],
            'lp12_options': [
                ('highly_transparent', 'Highly transparent and predictable'),
                ('mostly_transparent', 'Mostly transparent and predictable'),
                ('somewhat_transparent', 'Somewhat transparent but unpredictable'),
                ('often_opaque', 'Often opaque and unpredictable'),
                ('completely_unpredictable', 'Completely unpredictable'),
            ],
            'lp13_options': [
                ('very_satisfied', 'Very satisfied'),
                ('satisfied', 'Satisfied'),
                ('neutral', 'Neutral'),
                ('dissatisfied', 'Dissatisfied'),
                ('very_dissatisfied', 'Very dissatisfied'),
            ],
            'valid_options': {
                'lp1_technical_issues': ['very_frequently', 'frequently', 'occasionally', 'rarely', 'never'],
                'lp6_filing_efficiency': ['very_efficient', 'efficient', 'moderately_efficient', 'inefficient', 'very_inefficient'],
                'lp7_case_tracking': ['very_effective', 'effective', 'moderately_effective', 'ineffective', 'very_ineffective'],
                'lp8_notice_communication': ['very_effective', 'effective', 'moderately_effective', 'inefficient', 'very_ineffective'],
                'lp9_law_accessibility': ['very_accessible', 'accessible', 'moderately_accessible', 'not_very_accessible', 'not_accessible'],
                'lp10_law_change_impact': ['significant_negative', 'moderate_negative', 'minor_impact', 'no_impact', 'positive_impact'],
                'lp11_adr_effectiveness': ['very_effective', 'effective', 'moderately_effective', 'inefficient', 'very_inefficient'],
                'lp12_dispute_transparency': ['highly_transparent', 'mostly_transparent', 'somewhat_transparent', 'often_opaque', 'completely_unpredictable'],
                'lp13_overall_satisfaction': ['very_satisfied', 'satisfied', 'neutral', 'dissatisfied', 'very_dissatisfied'],
            }
        })

    if professional_role in ['customs', 'both']:
        context.update({
            # CA1: Training
            'ca1_options': [
                ('both_training', 'Yes - for both WeBOC and PSW'),
                ('weboc_only', 'Yes - only for WeBOC'),
                ('psw_only', 'Yes - only for PSW'),
                ('no_training', 'No training received'),
            ],
            'ca1a_options': [
                ('very_useful', 'Very useful'),
                ('moderately_useful', 'Moderately useful'),
                ('slightly_useful', 'Slightly useful'),
                ('not_useful', 'Not useful'),
                ('not_at_all_useful', 'Not at all useful'),
            ],
            'ca2_options': [
                ('very_well_integrated', 'Very well integrated - seamless data flow'),
                ('well_integrated', 'Well integrated - minor gaps'),
                ('moderately_integrated', 'Moderately integrated - some duplication/delays'),
                ('poorly_integrated', 'Poorly integrated - frequent disruptions'),
                ('not_integrated', 'Not integrated - systems operate independently'),
            ],
            'ca3_options': [
                ('psw_significantly_better', 'PSW is significantly more efficient'),
                ('psw_moderately_better', 'PSW is moderately better but evolving'),
                ('comparable', 'Both systems have comparable strengths'),
                ('weboc_reliable', 'WeBOC remains more reliable for core processes'),
                ('not_sure', 'Not sure/No direct PSW experience'),
            ],
            'ca4_options': [
                ('goods_declaration', 'Goods declaration filing'),
                ('classification', 'Classification under PCT codes'),
                ('customs_valuation', 'Customs valuation of goods'),
                ('duty_calculation', 'Duty and tax calculation'),
                ('document_submission', 'Document submission and verification'),
                ('cargo_examination', 'Cargo examination coordination'),
                ('client_registration', 'Client registration/management'),
                ('refund_processing', 'Refund/drawback processing'),
                ('no_challenges', 'No significant challenges'),
                ('other', 'Other (please specify)'),
            ],
            'ca5_options': [
                ('highly_transparent', 'Highly transparent and predictable'),
                ('mostly_transparent', 'Mostly transparent with minor issues'),
                ('somewhat_transparent', 'Somewhat transparent but inconsistent'),
                ('often_unpredictable', 'Often unpredictable'),
                ('completely_unpredictable', 'Completely unpredictable'),
            ],
            'ca6_options': [
                ('very_efficient', 'Very efficient - minimal delays'),
                ('efficient', 'Efficient - acceptable timelines'),
                ('moderately_efficient', 'Moderate - occasional delays'),
                ('inefficient', 'Inefficient - frequent delays'),
                ('very_inefficient', 'Very inefficient - major bottlenecks'),
            ],
            'ca7_options': [
                ('very_efficient', 'Very efficient - quick verification'),
                ('efficient', 'Efficient - reasonable timelines'),
                ('moderately_efficient', 'Moderate - some delays'),
                ('inefficient', 'Inefficient - frequent verification delays'),
                ('very_inefficient', 'Very inefficient - major document processing issues'),
            ],
            'ca8_options': [
                ('very_effective', 'Very effective - seamless multi-agency processing'),
                ('effective', 'Effective - minor coordination issues'),
                ('moderately_effective', 'Moderate - some coordination challenges'),
                ('ineffective', 'Ineffective - frequent coordination problems'),
                ('very_ineffective', 'Very ineffective - major inter-agency bottlenecks'),
            ],
            'ca9_options': [
                ('very_reliable', 'Very reliable - minimal downtime'),
                ('reliable', 'Reliable - occasional slowdowns'),
                ('moderately_reliable', 'Moderate - frequent performance issues'),
                ('unreliable', 'Unreliable - regular system crashes'),
                ('very_unreliable', 'Very unreliable - unusable during peaks'),
            ],
            'ca10_options': [
                ('significant_negative', 'Significant negative impact - major operational disruptions'),
                ('moderate_negative', 'Moderate negative impact - manageable but challenging'),
                ('minor_impact', 'Minor impact - easily adaptable'),
                ('no_impact', 'No significant impact'),
                ('positive_impact', 'Positive impact - improvements in processes'),
            ],
            'ca11_options': [
                ('very_effective', 'Very effective - can fully represent client interests'),
                ('effective', 'Effective - minor representation limitations'),
                ('moderately_effective', 'Moderate - some representation challenges'),
                ('ineffective', 'Ineffective - significant representation barriers'),
                ('very_ineffective', 'Very ineffective - cannot adequately represent clients'),
            ],
            'ca12_options': [
                ('system_reliability', 'System reliability and uptime'),
                ('frequent_policy_changes', 'Frequent policy changes'),
                ('unpredictable_assessments', 'Unpredictable duty assessments'),
                ('cargo_examination_delays', 'Cargo examination delays'),
                ('document_processing_bottlenecks', 'Document processing bottlenecks'),
                ('client_management_challenges', 'Client management challenges'),
                ('inter_agency_coordination', 'Inter-agency coordination'),
                ('training_knowledge_gaps', 'Training and knowledge gaps'),
                ('other', 'Other (please specify)'),
            ],
            'ca13_options': [
                ('system_reliability', 'System reliability and uptime'),
                ('frequent_policy_changes', 'Frequent policy changes'),
                ('unpredictable_assessments', 'Unpredictable duty assessments'),
                ('cargo_examination_delays', 'Cargo examination delays'),
                ('document_processing_bottlenecks', 'Document processing bottlenecks'),
                ('client_management_challenges', 'Client management challenges'),
                ('inter_agency_coordination', 'Inter-agency coordination'),
                ('training_knowledge_gaps', 'Training and knowledge gaps'),
                ('other', 'Other'),
            ],
            'valid_options': {
                'ca1_training_received': ['both_training', 'weboc_only', 'psw_only', 'no_training'],
                'ca1a_training_usefulness': ['very_useful', 'moderately_useful', 'slightly_useful', 'not_useful', 'not_at_all_useful'],
                'ca2_psw_weboc_integration': ['very_well_integrated', 'well_integrated', 'moderately_integrated', 'poorly_integrated', 'not_integrated'],
                'ca3_psw_comparison': ['psw_significantly_better', 'psw_moderately_better', 'comparable', 'weboc_reliable', 'not_sure'],
                'ca5_duty_assessment': ['highly_transparent', 'mostly_transparent', 'somewhat_transparent', 'often_unpredictable', 'completely_unpredictable'],
                'ca6_cargo_efficiency': ['very_efficient', 'efficient', 'moderately_efficient', 'inefficient', 'very_inefficient'],
                'ca7_document_verification': ['very_efficient', 'efficient', 'moderately_efficient', 'inefficient', 'very_inefficient'],
                'ca8_agency_coordination': ['very_effective', 'effective', 'moderately_effective', 'ineffective', 'very_ineffective'],
                'ca9_system_reliability': ['very_reliable', 'reliable', 'moderately_reliable', 'unreliable', 'very_unreliable'],
                'ca10_policy_impact': ['significant_negative', 'moderate_negative', 'minor_impact', 'no_impact', 'positive_impact'],
                'ca11_client_representation': ['very_effective', 'effective', 'moderately_effective', 'ineffective', 'very_ineffective'],
                'ca13_biggest_challenge': ['system_reliability', 'frequent_policy_changes', 'unpredictable_assessments', 'cargo_examination_delays', 'document_processing_bottlenecks', 'client_management_challenges', 'inter_agency_coordination', 'training_knowledge_gaps', 'other'],
            }
        })
    return context

def role_specific_questions_view(request):
    """Render the role-specific questions page (step 4)"""
    if not request.session.get('survey_started') or not request.session.get('respondent_info') or not request.session.get('generic_answers'):
        return redirect('survey:welcome')

    respondent_info = request.session.get('respondent_info', {})

    # Determine professional role based on respondent_info
    professional_roles = respondent_info.get('professional_roles', [])
    if 'legal' in professional_roles and 'customs' in professional_roles:
        professional_role = 'both'
    elif 'legal' in professional_roles:
        professional_role = 'legal'
    elif 'customs' in professional_roles:
        professional_role = 'customs'
    else:
        professional_role = ''

    context_data = get_role_specific_context(professional_role)

    # Preprocess lp4_procedures to include comments
    if professional_role in ['legal', 'both']:
        role_answers = request.session.get('role_specific_answers', {})
        comments = role_answers.get('lp4_procedures', {}).get('comments', {})
        lp4_procedures = context_data['lp4_procedures']
        context_data['lp4_procedures'] = [
            (procedure, value, comments.get(value, '')) for procedure, value, _ in lp4_procedures
        ]

    if request.method == 'POST':
        errors = []
        role_answers = request.session.get('role_specific_answers', {})

        if professional_role in ['legal', 'both']:
            required_legal_fields = [
                'lp1_technical_issues', 'lp6_filing_efficiency', 'lp7_case_tracking',
                'lp8_notice_communication', 'lp9_law_accessibility', 'lp10_law_change_impact',
                'lp11_adr_effectiveness', 'lp12_dispute_transparency', 'lp13_overall_satisfaction'
            ]
            for field in required_legal_fields:
                value = request.POST.get(field, '').strip()
                if not value:
                    errors.append(f"Missing required field: {field.replace('_', ' ').title()} (LP{field[2]})")
                elif field in context_data.get('valid_options', {}) and value not in context_data['valid_options'][field]:
                    errors.append(f"Invalid value for {field.replace('_', ' ').title()} (LP{field[2]})")
                role_answers[field] = value

            # LP1 and LP2: Technical issues and common problems
            lp1_value = request.POST.get('lp1_technical_issues', '')
            lp2_problems = request.POST.getlist('lp2_common_problems', [])
            lp2_required = lp1_value in ['very_frequently', 'frequently']
            if lp2_required and not lp2_problems:
                errors.append("Please select at least one technical issue for LP2")
            if 'other' in lp2_problems and not request.POST.get('lp2_other_text', '').strip():
                errors.append("Please specify details for 'Other' in LP2")
            role_answers['lp2_common_problems'] = lp2_problems
            role_answers['lp2_other_text'] = sanitize_input(request.POST.get('lp2_other_text', ''))

            # LP3: Improvement areas
            lp3_improvements = request.POST.getlist('lp3_improvement_areas', [])
            if not lp3_improvements:
                errors.append("Please select at least one improvement area for LP3")
            elif len(lp3_improvements) > 3:
                errors.append("Please select no more than 3 options for LP3")
            if 'other' in lp3_improvements and not request.POST.get('lp3_other_text', '').strip():
                errors.append("Please specify details for 'Other' in LP3")
            role_answers['lp3_improvement_areas'] = lp3_improvements
            role_answers['lp3_other_text'] = sanitize_input(request.POST.get('lp3_other_text', ''))

            # LP4: Procedures matrix
            lp4_procedures = ['registration', 'return_filing', 'refund_claims', 'audit_compliance', 'appeals', 'correspondence']
            lp4_data = {'sales': [], 'income': [], 'comments': {}}
            lp4_has_selection = False
            for procedure in lp4_procedures:
                if request.POST.get(f'lp4_{procedure}_sales'):
                    lp4_data['sales'].append(procedure)
                    lp4_has_selection = True
                if request.POST.get(f'lp4_{procedure}_income'):
                    lp4_data['income'].append(procedure)
                    lp4_has_selection = True
                comment = sanitize_input(request.POST.get(f'lp4_{procedure}_comment', ''))
                if comment:
                    lp4_data['comments'][procedure] = comment
            lp4_other_procedure = sanitize_input(request.POST.get('lp4_other_procedure', ''))
            lp4_other_sales = bool(request.POST.get('lp4_other_sales'))
            lp4_other_income = bool(request.POST.get('lp4_other_income'))
            if lp4_other_procedure and not (lp4_other_sales or lp4_other_income):
                errors.append("Please select at least one tax type for the 'Other' procedure in LP4")
            if lp4_other_procedure or lp4_other_sales or lp4_other_income:
                lp4_has_selection = True
            role_answers['lp4_procedures'] = lp4_data
            role_answers['lp4_other_procedure'] = lp4_other_procedure
            role_answers['lp4_other_sales'] = lp4_other_sales
            role_answers['lp4_other_income'] = lp4_other_income
            role_answers['lp4_other_comment'] = sanitize_input(request.POST.get('lp4_other_comment', ''))
            if not lp4_has_selection:
                errors.append("Please select at least one procedure or tax type in LP4")

            # LP5: Representation challenges
            lp5_challenges = request.POST.getlist('lp5_representation_challenges', [])
            if not lp5_challenges:
                errors.append("Please select at least one challenge for LP5")
            elif len(lp5_challenges) > 3:
                errors.append("Please select no more than 3 options for LP5")
            if 'other' in lp5_challenges and not request.POST.get('lp5_other_text', '').strip():
                errors.append("Please specify details for 'Other' in LP5")
            role_answers['lp5_representation_challenges'] = lp5_challenges
            role_answers['lp5_other_text'] = sanitize_input(request.POST.get('lp5_other_text', ''))

            # LP6: Qualitative validation
            lp6_visible = request.POST.get('lp6_qualitative_visible', '0') == '1'
            lp6_text = request.POST.get('lp6_qualitative_text', '').strip()
            if lp6_visible and not lp6_text:
                errors.append("Please provide details for the filing challenges in LP6")
            role_answers['lp6_qualitative_text'] = sanitize_input(lp6_text)
            role_answers['lp6_qualitative_visible'] = lp6_visible

            # LP8: Qualitative validation
            lp8_visible = request.POST.get('lp8_qualitative_visible', '0') == '1'
            lp8_text = request.POST.get('lp8_qualitative_text', '').strip()
            if lp8_visible and not lp8_text:
                errors.append("Please provide details for the communication challenges in LP8")
            role_answers['lp8_qualitative_text'] = sanitize_input(lp8_text)
            role_answers['lp8_qualitative_visible'] = lp8_visible

            # LP10: Qualitative validation
            lp10_visible = request.POST.get('lp10_qualitative_visible', '0') == '1'
            lp10_text = request.POST.get('lp10_qualitative_text', '').strip()
            if lp10_visible and not lp10_text:
                errors.append("Please provide details for the impact of tax law changes in LP10")
            role_answers['lp10_qualitative_text'] = sanitize_input(lp10_text)
            role_answers['lp10_qualitative_visible'] = lp10_visible

            # Final Feedback (optional)
            role_answers['final_feedback'] = sanitize_input(request.POST.get('final_feedback', ''))

        if professional_role in ['customs', 'both']:
            # Required radio fields
            required_customs_fields = [
                'ca1_training_received', 'ca2_psw_weboc_integration', 'ca3_psw_comparison',
                'ca5_duty_assessment', 'ca6_cargo_efficiency', 'ca7_document_verification',
                'ca8_agency_coordination', 'ca9_system_reliability', 'ca10_policy_impact',
                'ca11_client_representation', 'ca13_biggest_challenge'
            ]
            for field in required_customs_fields:
                value = request.POST.get(field, '').strip()
                if not value:
                    errors.append(f"Missing required field: {field.replace('_', ' ').title()} (CA{field[2] if field[2].isdigit() else field[2:4]})")
                elif field in context_data.get('valid_options', {}) and value not in context_data['valid_options'][field]:
                    errors.append(f"Invalid value for {field.replace('_', ' ').title()} (CA{field[2] if field[2].isdigit() else field[2:4]})")
                role_answers[field] = value

            # CA1a: Conditional validation
            ca1_training = request.POST.get('ca1_training_received', '')
            ca1a_visible = request.POST.get('ca1a_visible', '0') == '1'
            ca1a_value = request.POST.get('ca1a_training_usefulness', '').strip()
            if ca1_training != 'no_training' and ca1a_visible and not ca1a_value:
                errors.append("Please select an option for CA1a")
            elif ca1a_value and ca1a_value not in context_data['valid_options']['ca1a_training_usefulness']:
                errors.append("Invalid value for CA1a")
            role_answers['ca1a_training_usefulness'] = ca1a_value if ca1_training != 'no_training' else ''

            # CA4: Procedure challenges (multiple selection)
            ca4_challenges = request.POST.getlist('ca4_procedure_challenges', [])
            if not ca4_challenges:
                errors.append("Please select at least one option for CA4")
            elif 'no_challenges' in ca4_challenges and len(ca4_challenges) > 1:
                errors.append("Cannot select 'No significant challenges' with other options in CA4")
            elif len(ca4_challenges) > 3 and 'no_challenges' not in ca4_challenges:
                errors.append("Please select no more than 3 options for CA4")
            if 'other' in ca4_challenges and not request.POST.get('ca4_other_text', '').strip():
                errors.append("Please specify details for 'Other' in CA4")
            role_answers['ca4_procedure_challenges'] = ca4_challenges
            role_answers['ca4_other_text'] = sanitize_input(request.POST.get('ca4_other_text', ''))

            # CA12: Operational challenges (multiple selection)
            ca12_challenges = request.POST.getlist('ca12_operational_challenges', [])
            if not ca12_challenges:
                errors.append("Please select at least one operational challenge for CA12")
            if 'other' in ca12_challenges and not request.POST.get('ca12_other_text', '').strip():
                errors.append("Please specify details for 'Other' in CA12")
            role_answers['ca12_operational_challenges'] = ca12_challenges
            role_answers['ca12_other_text'] = sanitize_input(request.POST.get('ca12_other_text', ''))

            # CA13: Biggest challenge (single selection with optional textarea)
            ca13_biggest_challenge = request.POST.get('ca13_biggest_challenge', '').strip()
            ca13_other_text = request.POST.get('ca13_other_text', '').strip()
            if ca13_biggest_challenge == 'other' and not ca13_other_text:
                errors.append("Please specify details for 'Other' in CA13")
            role_answers['ca13_biggest_challenge'] = ca13_biggest_challenge
            role_answers['ca13_other_text'] = sanitize_input(ca13_other_text)

        if errors:
            logger.warning(f"Validation errors in role_specific_questions: {errors}")
            context = get_progress_context(current_step=4)
            context.update({
                'professional_role': professional_role,
                'is_legal': professional_role in ['legal', 'both'],
                'is_customs': professional_role in ['customs', 'both'],
                'role_specific_answers': role_answers,
                'submitted_ca1': role_answers.get('ca1_training_received', ''),
                'error': "Please correct the following errors:\n" + "\n".join(errors)
            })
            context.update(context_data)
            return render(request, 'survey/role_specific.html', context)

        validate_session_size(request)
        request.session['role_specific_answers'] = role_answers
        request.session.modified = True
        return redirect('survey:cross_system_perspectives')

    context = get_progress_context(current_step=4, total_steps=6)
    context.update({
        'professional_role': professional_role,
        'is_legal': professional_role in ['legal', 'both'],
        'is_customs': professional_role in ['customs', 'both'],
        'role_specific_answers': request.session.get('role_specific_answers', {}),
        'submitted_ca1': request.session.get('role_specific_answers', {}).get('ca1_training_received', '')
    })
    context.update(context_data)
    return render(request, 'survey/role_specific.html', context)