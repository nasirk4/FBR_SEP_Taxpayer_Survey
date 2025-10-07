# survey/views/save_progress_views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from .utils import sanitize_input, validate_session_size
import json
import logging

logger = logging.getLogger(__name__)

@csrf_protect
def save_progress_view(request):
    """Save survey progress via AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            allowed_keys = [
                'respondent_info', 'generic_answers', 'role_specific_answers',
                'cross_system_answers'  # Exclude final_remarks to avoid overwrite
            ]
            sanitized_data = {}
            for key, value in data.items():
                if key in allowed_keys:
                    if isinstance(value, str):
                        sanitized_data[key] = sanitize_input(value)
                    elif isinstance(value, (list, dict)):
                        sanitized_data[key] = value
                    else:
                        sanitized_data[key] = value
            validate_session_size(request)
            request.session.update(sanitized_data)
            logger.info(f"Progress saved: keys={list(sanitized_data.keys())}, session_id={request.session.session_key}")
            return JsonResponse({'status': 'success'})
        except Exception as e:
            logger.error(f"Error in save_progress: {e}, session_id={request.session.session_key}")
            return JsonResponse({'status': 'error', 'message': f"Failed to save progress: {str(e)}"}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)