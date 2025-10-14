# survey/views/cross_system_perspectives_views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from survey.utils.progress import get_progress_context
from survey.utils.session_utils import sanitize_input, validate_session_size
import logging

logger = logging.getLogger(__name__)

def cross_system_perspectives_view(request):
    """Render the cross-system perspectives page (step 5)"""
    if not request.session.get('survey_started') or not request.session.get('respondent_info') or not request.session.get('generic_answers') or not request.session.get('role_specific_answers'):
        return redirect('survey:welcome')

    if request.method == 'POST':
        try:
            # Check if user wants to skip this section
            if request.POST.get('skip_section') == 'true':
                # Store empty answers to indicate section was visited but skipped
                request.session['cross_system_answers'] = {
                    'skipped': True,
                    'timestamp': timezone.now().isoformat()
                }
                request.session.modified = True

                # Return JSON response for AJAX requests, redirect for normal form submissions
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'success'})
                else:
                    return redirect('survey:final_remarks')

            # Handle save_draft for auto-save and back navigation
            if request.POST.get('save_draft') == 'true':
                # *** Updated field names to match HTML: xs1_data_discrepancy and xs2_policy_consistency ***
                cross_system_answers = {
                    'xs1_data_discrepancy': sanitize_input(request.POST.get('xs1_data_discrepancy', '')),
                    'xs2_policy_consistency': sanitize_input(request.POST.get('xs2_policy_consistency', '')),
                    'saved_as_draft': True,
                    'draft_saved_at': timezone.now().isoformat()
                }

                validate_session_size(request)
                request.session['cross_system_answers'] = cross_system_answers
                request.session.modified = True

                # Return JSON response for AJAX requests
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'success'})
                else:
                    return redirect('survey:cross_system_perspectives')

            # Process normal form submission (Next button)
            # *** Updated field names to match HTML: xs1_data_discrepancy and xs2_policy_consistency ***
            cross_system_answers = {
                'xs1_data_discrepancy': sanitize_input(request.POST.get('xs1_data_discrepancy', '')),
                'xs2_policy_consistency': sanitize_input(request.POST.get('xs2_policy_consistency', '')),
                'completed_at': timezone.now().isoformat()
            }

            validate_session_size(request)
            request.session['cross_system_answers'] = cross_system_answers
            request.session.modified = True

            return redirect('survey:final_remarks')

        except Exception as e:
            logger.error(f"Error in cross_system_perspectives: {str(e)}")
            error_message = 'An error occurred while saving your responses. Please try again.'

            # Return JSON error for AJAX, render for normal requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': error_message}, status=400)
            else:
                return render(request, 'survey/cross_system_perspectives.html', {
                    'error': error_message
                })

    # GET request - load existing data if any
    cross_system_answers = request.session.get('cross_system_answers', {})
    
    # Define options for the radio buttons (must be compatible with both XS1 and XS2)
    xs_options = [
        ('always', 'Always / Almost Always'),
        ('often', 'Often'),
        ('sometimes', 'Sometimes'),
        ('rarely', 'Rarely'),
        ('never', 'Never / Almost Never'),
        ('not_applicable', 'Not Applicable / Don\'t know')
    ]

    context = get_progress_context(current_step=5, total_steps=6)
    context['cross_system_answers'] = cross_system_answers
    context['xs1_options'] = xs_options # Using the same options for both questions
    context['xs2_options'] = xs_options
    
    # Note: If XS2 options were different, they would be defined separately here.
    
    return render(request, 'survey/cross_system_perspectives.html', context)