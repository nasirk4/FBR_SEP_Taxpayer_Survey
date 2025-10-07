# survey/views/utils.py
import bleach
import json
import logging

logger = logging.getLogger(__name__)

def calculate_progress(current_step, total_steps=6):
    """Calculate progress percentage for the progress bar"""
    return ((current_step - 1) / (total_steps - 1)) * 100

def get_progress_context(current_step, total_steps=6):
    """Return standardized progress context for templates"""
    return {
        'current_step': current_step,
        'progress_width': f'{calculate_progress(current_step, total_steps)}%',
        'total_steps': total_steps,
    }

def sanitize_input(text):
    """Sanitize text inputs to prevent XSS"""
    return bleach.clean(text, tags=[], strip=True).strip() if text else ''

def validate_session_size(request):
    """Check session size to prevent bloat"""
    session_data = json.dumps(dict(request.session))
    if len(session_data) > 1024 * 1024:  # 1MB limit
        logger.warning("Session size exceeds 1MB, clearing non-critical data")
        for key in list(request.session.keys()):
            if key not in ['reference_number']:
                del request.session[key]
        raise ValueError("Session data too large, please start over")