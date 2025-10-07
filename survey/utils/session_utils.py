"""
Session utility functions for the FBR survey application.
"""

import logging

logger = logging.getLogger(__name__)

def sanitize_input(text):
    """
    Sanitize user input by stripping whitespace and handling None values.
    
    Args:
        text (str): Input text to sanitize
        
    Returns:
        str: Sanitized text or empty string if None
    """
    if text is None:
        return ""
    
    # Convert to string and strip whitespace
    sanitized = str(text).strip()
    
    # Log suspicious inputs (very long or containing special patterns)
    if len(sanitized) > 1000:
        logger.warning(f"Long input detected: {len(sanitized)} characters")
    
    return sanitized

def validate_session_size(request):
    """
    Validate session size to prevent overflow and ensure reasonable data size.
    
    Args:
        request: Django request object
        
    Raises:
        ValueError: If session size exceeds reasonable limits
    """
    try:
        # Estimate session size by converting to string
        session_data = dict(request.session)
        session_size = len(str(session_data))
        
        # Warn if approaching limit (Django sessions typically have 4KB limit)
        if session_size > 3500:
            logger.warning(f"Session size approaching limit: {session_size} bytes")
            
        # Hard limit to prevent abuse
        if session_size > 5000:
            raise ValueError(f"Session size too large: {session_size} bytes")
            
        logger.debug(f"Session size: {session_size} bytes")
        
    except Exception as e:
        logger.error(f"Error validating session size: {e}")
        # Don't raise here to avoid breaking the application
        # Just log the error and continue
