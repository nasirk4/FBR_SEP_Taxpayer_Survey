# /home/nasirk4/FBR_SEP_Taxpayer_Survey/survey/utils/progress.py
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

# Configuration constants
DEFAULT_TOTAL_STEPS = 6
MIN_STEPS = 2
MAX_PROGRESS = 100
MIN_PROGRESS = 0

def validate_progress_inputs(current_step, total_steps):
    """
    Validate and convert progress calculation inputs.

    Args:
        current_step: The current step number
        total_steps: Total number of steps

    Returns:
        tuple: (current_step_int, total_steps_int)

    Raises:
        ValueError: If inputs cannot be converted to valid integers
    """
    try:
        # Convert to integers (no string stripping needed for typical use)
        current_step_int = int(float(current_step)) if isinstance(current_step, (str, float)) else int(current_step)
        total_steps_int = int(float(total_steps)) if isinstance(total_steps, (str, float)) else int(total_steps)

        # Validate inputs
        if total_steps_int < MIN_STEPS:
            raise ValueError(f"total_steps must be at least {MIN_STEPS}, got {total_steps_int}")
        if current_step_int < 0:
            raise ValueError(f"current_step must be non-negative, got {current_step_int}")

        return current_step_int, total_steps_int

    except (TypeError, ValueError) as e:
        logger.error(f"Invalid progress inputs: current_step={current_step}, total_steps={total_steps}, error={e}")
        raise ValueError(f"Progress inputs must be valid integers: {e}")

def calculate_progress(current_step, total_steps=DEFAULT_TOTAL_STEPS):
    """
    Calculate progress percentage for the survey progress bar.

    Args:
        current_step (int, str, float): The current step number (1-based indexing).
        total_steps (int, str, float, optional): Total number of steps in the survey. Defaults to 6.

    Returns:
        int: Progress percentage (0-100), rounded to the nearest integer.
    """
    try:
        # Validate and convert inputs
        current_step, total_steps = validate_progress_inputs(current_step, total_steps)

        # Handle edge cases
        if current_step <= 0:
            logger.warning(f"Invalid current_step ({current_step}): returning {MIN_PROGRESS}%")
            return MIN_PROGRESS
        if current_step > total_steps:
            logger.info(f"current_step ({current_step}) exceeds total_steps ({total_steps}), capping at {MAX_PROGRESS}%")
            return MAX_PROGRESS

        # Calculate percentage - FIXED: Use integer calculation to avoid floating point issues
        progress = ((current_step - 1) * 100) // (total_steps - 1)
        bounded_progress = max(MIN_PROGRESS, min(MAX_PROGRESS, progress))

        logger.info(f"Progress calculated: step={current_step}/{total_steps}, progress={bounded_progress}%")
        return bounded_progress

    except (ValueError, ZeroDivisionError) as e:
        logger.error(f"Error in calculate_progress: {e}, current_step={current_step}, total_steps={total_steps}, returning {MIN_PROGRESS}")
        return MIN_PROGRESS

@lru_cache(maxsize=128)
def calculate_progress_cached(current_step, total_steps=DEFAULT_TOTAL_STEPS):
    """
    Cached version of calculate_progress for repeated calls with same parameters.

    Args:
        current_step (int, str, float): The current step number
        total_steps (int, str, float, optional): Total number of steps

    Returns:
        int: Progress percentage (0-100)
    """
    # Normalize inputs to integers for consistent cache keys
    try:
        current_step, total_steps = validate_progress_inputs(current_step, total_steps)
        return calculate_progress(current_step, total_steps)
    except ValueError:
        return MIN_PROGRESS

def get_progress_context(current_step, total_steps=DEFAULT_TOTAL_STEPS, use_cache=False):
    """
    Return standardized context for survey progress in templates.

    Args:
        current_step (int, str, float): The current step number (1-based indexing).
        total_steps (int, str, float, optional): Total number of steps in the survey. Defaults to 6.
        use_cache (bool, optional): Whether to use cached progress calculation. Defaults to False.

    Returns:
        dict: Context with current_step, progress_width, progress_percentage, and total_steps.
    """
    try:
        # Choose calculation method
        progress_calc = calculate_progress_cached if use_cache else calculate_progress

        # Validate current_step for template FIRST
        current_step_int, total_steps_int = validate_progress_inputs(current_step, total_steps)
        if current_step_int <= 0 or current_step_int > total_steps_int:
            original_step = current_step_int
            current_step_int = min(max(1, current_step_int), total_steps_int)
            logger.warning(f"Adjusted current_step from {original_step} to {current_step_int} (valid range: 1-{total_steps_int})")

        # Calculate progress percentage ONCE with validated inputs
        progress_percentage = progress_calc(current_step_int, total_steps_int)
        
        context = {
            'current_step': current_step_int,
            'progress_width': f'{progress_percentage}%',
            'progress_percentage': progress_percentage,
            'total_steps': total_steps_int,
        }

        logger.debug(f"Progress context generated: {context}")
        return context

    except Exception as e:
        logger.error(f"Unexpected error in get_progress_context: {e}, current_step={current_step}, total_steps={total_steps}, returning fallback")
        return get_fallback_context(total_steps)

def get_fallback_context(total_steps=DEFAULT_TOTAL_STEPS):
    """
    Return fallback progress context when errors occur.

    Args:
        total_steps (int, str, float): Total number of steps

    Returns:
        dict: Safe fallback context
    """
    try:
        total_steps_int = int(float(total_steps)) if isinstance(total_steps, (str, float)) else int(total_steps)
        if total_steps_int < MIN_STEPS:
            logger.error(f"Invalid total_steps ({total_steps}) in fallback, using {DEFAULT_TOTAL_STEPS}")
            total_steps_int = DEFAULT_TOTAL_STEPS
    except (TypeError, ValueError):
        logger.error(f"Invalid total_steps ({total_steps}) in fallback, using {DEFAULT_TOTAL_STEPS}")
        total_steps_int = DEFAULT_TOTAL_STEPS

    return {
        'current_step': 1,
        'progress_width': f'{MIN_PROGRESS}%',
        'progress_percentage': MIN_PROGRESS,
        'total_steps': total_steps_int,
    }

def get_step_progress_mapping(total_steps=DEFAULT_TOTAL_STEPS):
    """
    Generate a mapping of step numbers to their progress percentages.

    Args:
        total_steps (int, str, float): Total number of steps

    Returns:
        dict: Mapping of step_number -> progress_percentage
    """
    try:
        total_steps_int = int(float(total_steps)) if isinstance(total_steps, (str, float)) else int(total_steps)
        if total_steps_int < MIN_STEPS:
            logger.error(f"Invalid total_steps ({total_steps_int}) in step_progress_mapping, returning fallback")
            return {1: MIN_PROGRESS}
        return {
            step: calculate_progress_cached(step, total_steps_int)
            for step in range(1, total_steps_int + 1)
        }
    except (TypeError, ValueError) as e:
        logger.error(f"Error generating step progress mapping: {e}, total_steps={total_steps}, returning fallback")
        return {1: MIN_PROGRESS}

# Example usage and testing
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(level=logging.DEBUG)

    # Test cases
    test_cases = [
        (1, 6),        # 0%
        (2, 6),        # 20%
        (3, 6),        # 40%
        (4, 6),        # 60%
        (5, 6),        # 80%
        (6, 6),        # 100%
        (0, 6),        # 0% (invalid)
        (7, 6),        # 100% (exceeds)
        ("3", "6"),    # 40% (strings)
        (1, 1),        # 0% (invalid total_steps)
        (None, 6),     # 0% (None input)
        ("abc", 6),    # 0% (non-numeric)
        (3.5, 6),      # 40% (float)
    ]

    print("Progress Calculation Tests:")
    print("-" * 40)
    for current_step, total_steps in test_cases:
        progress = calculate_progress(current_step, total_steps)
        context = get_progress_context(current_step, total_steps)
        print(f"Step {current_step}/{total_steps}: {progress}% -> Context: {context}")

    print("\nStep Progress Mapping (6 steps):")
    print(get_step_progress_mapping(6))