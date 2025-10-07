# survey/views/welcome_views.py 
from django.shortcuts import render, redirect
# Use direct import to bypass any cached import issues
from survey.utils.progress import get_progress_context
from survey.utils.session_utils import validate_session_size

def welcome_view(request):
    """Render the welcome page (step 1)"""
    if request.method == 'POST':
        if request.POST.get('start_new_survey'):
            validate_session_size(request)
            request.session.flush()
        request.session['survey_started'] = True
        return redirect('survey:respondent_info')

    # FORCE CORRECT PROGRESS WITH DEBUG
    try:
        context = get_progress_context(current_step=1, total_steps=6)
        print(f"DEBUG Welcome View - Progress Context: {context}")
    except Exception as e:
        print(f"DEBUG Welcome View - Error: {e}")
        # Fallback to manual calculation
        context = {
            'current_step': 1,
            'progress_width': '0%',
            'progress_percentage': 0,
            'total_steps': 6
        }
    
    return render(request, 'survey/welcome.html', context)