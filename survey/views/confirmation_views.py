# survey/views/confirmation_views.py
from django.shortcuts import render
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

def confirmation_view(request):
    """Display survey submission confirmation with reference number"""
    reference_number = request.session.get('reference_number')
    
    if not reference_number:
        logger.warning(f"Confirmation accessed without reference number, session_id={request.session.session_key}")
        messages.error(request, "No survey submission found. Please complete the survey.")
    
    context = {
        'reference_number': reference_number,
    }
    
    logger.info(f"Confirmation displayed, reference_number={reference_number}, session_id={request.session.session_key}")
    return render(request, 'survey/confirmation.html', context)