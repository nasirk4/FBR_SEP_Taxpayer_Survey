from django.shortcuts import render, redirect
from survey.utils.progress import get_progress_context
from survey.utils.session_utils import sanitize_input, validate_session_size
from survey.models import SurveyResponse
import logging
import json
import re

logger = logging.getLogger(__name__)

# --- Constants (Module Level) ---
PROVINCES = [
    ('ajk', 'Azad Jammu and Kashmir'),
    ('balochistan', 'Balochistan'),
    ('gb', 'Gilgit-Baltistan'),
    ('ict', 'ICT'),
    ('kpk', 'Khyber Pakhtunkhwa'),
    ('punjab', 'Punjab'),
    ('sindh', 'Sindh'),
]

DISTRICTS = [
    # AJK
    ('Bagh', 'ajk'), ('Bhimber', 'ajk'), ('Haveli', 'ajk'), ('Jhelum Valley (Hattian)', 'ajk'),
    ('Kotli', 'ajk'), ('Mirpur', 'ajk'), ('Muzaffarabad', 'ajk'), ('Neelum Valley', 'ajk'),
    ('Poonch (Rawalakot)', 'ajk'), ('Sudhanoti (Pallandri)', 'ajk'),
    # Gilgit-Baltistan
    ('Astore', 'gb'), ('Darel', 'gb'), ('Diamer', 'gb'), ('Ghanche', 'gb'), ('Ghizer', 'gb'),
    ('Gilgit', 'gb'), ('Gupis-Yasin', 'gb'), ('Hunza', 'gb'), ('Kharmang', 'gb'), ('Nagar', 'gb'),
    ('Roundu', 'gb'), ('Shigar', 'gb'), ('Skardu', 'gb'), ('Tangir', 'gb'),
    # Punjab
    ('Attock', 'punjab'), ('Bahawalnagar', 'punjab'), ('Bahawalpur', 'punjab'), ('Bhakkar', 'punjab'),
    ('Chakwal', 'punjab'), ('Chiniot', 'punjab'), ('Dera Ghazi Khan', 'punjab'), ('Faisalabad', 'punjab'),
    ('Gujranwala', 'punjab'), ('Gujrat', 'punjab'), ('Hafizabad', 'punjab'), ('Jhelum', 'punjab'),
    ('Jhang', 'punjab'), ('Kasur', 'punjab'), ('Khanewal', 'punjab'), ('Khushab', 'punjab'),
    ('Kot Addu', 'punjab'), ('Lahore', 'punjab'), ('Layyah', 'punjab'), ('Lodhran', 'punjab'),
    ('Mandi Bahauddin', 'punjab'), ('Mianwali', 'punjab'), ('Multan', 'punjab'), ('Murree', 'punjab'),
    ('Muzaffargarh', 'punjab'), ('Nankana Sahib', 'punjab'), ('Narowal', 'punjab'), ('Okara', 'punjab'),
    ('Pakpattan', 'punjab'), ('Rahim Yar Khan', 'punjab'), ('Rajanpur', 'punjab'), ('Rawalpindi', 'punjab'),
    ('Sahiwal', 'punjab'), ('Sargodha', 'punjab'), ('Sheikhupura', 'punjab'), ('Sialkot', 'punjab'),
    ('Toba Tek Singh', 'punjab'), ('Vehari', 'punjab'), ('Wazirabad', 'punjab'), ('Rajanpur (Taunsa)', 'punjab'),
    ('Talagang', 'punjab'),
    # Sindh
    ('Badin', 'sindh'), ('Dadu', 'sindh'), ('Ghotki', 'sindh'), ('Hyderabad', 'sindh'), ('Jacobabad', 'sindh'),
    ('Jamshoro', 'sindh'), ('Kambar Shahdadkot', 'sindh'), ('Karachi Central', 'sindh'), ('Karachi East', 'sindh'),
    ('Karachi South', 'sindh'), ('Karachi West', 'sindh'), ('Kashmore', 'sindh'), ('Keamari', 'sindh'),
    ('Khairpur', 'sindh'), ('Korangi', 'sindh'), ('Larkana', 'sindh'), ('Malir', 'sindh'), ('Matiari', 'sindh'),
    ('Mirpur Khas', 'sindh'), ('Naushahro Feroze', 'sindh'), ('Qambar Shahdadkot', 'sindh'), ('Sanghar', 'sindh'),
    ('Shaheed Benazirabad', 'sindh'), ('Shikarpur', 'sindh'), ('Sujawal', 'sindh'), ('Sukkur', 'sindh'),
    ('Tando Allahyar', 'sindh'), ('Tando Muhammad Khan', 'sindh'), ('Tharparkar', 'sindh'), ('Thatta', 'sindh'),
    ('Umerkot', 'sindh'),
    # Khyber Pakhtunkhwa
    ('Abbottabad', 'kpk'), ('Allai', 'kpk'), ('Bajaur', 'kpk'), ('Bannu', 'kpk'), ('Batagram', 'kpk'),
    ('Buner', 'kpk'), ('Charsadda', 'kpk'), ('Chitral Lower', 'kpk'), ('Chitral Upper', 'kpk'),
    ('Dera Ismail Khan', 'kpk'), ('Dir Lower', 'kpk'), ('Dir Upper', 'kpk'), ('Hangu', 'kpk'),
    ('Haripur', 'kpk'), ('Karak', 'kpk'), ('Kolai-Palas', 'kpk'), ('Kohat', 'kpk'), ('Kurram', 'kpk'),
    ('Lakki Marwat', 'kpk'), ('Lower Kohistan', 'kpk'), ('Malakand', 'kpk'), ('Mansehra', 'kpk'),
    ('Mardan', 'kpk'), ('Mohmand', 'kpk'), ('North Waziristan', 'kpk'), ('Nowshera', 'kpk'),
    ('Orakzai', 'kpk'), ('Paharpur', 'kpk'), ('Peshawar', 'kpk'), ('Shangla', 'kpk'), ('Swabi', 'kpk'),
    ('Swat', 'kpk'), ('Tank', 'kpk'), ('Torghar', 'kpk'), ('Upper Kohistan', 'kpk'), ('South Waziristan', 'kpk'),
    # Balochistan
    ('Awaran', 'balochistan'), ('Barkhan', 'balochistan'), ('Bolan', 'balochistan'), ('Chagai', 'balochistan'),
    ('Chaman', 'balochistan'), ('Dera Bugti', 'balochistan'), ('Duki', 'balochistan'), ('Gwadar', 'balochistan'),
    ('Harnai', 'balochistan'), ('Hub', 'balochistan'), ('Jaffarabad', 'balochistan'), ('Jhal Magsi', 'balochistan'),
    ('Kalat', 'balochistan'), ('Kech (Turbat)', 'balochistan'), ('Kharan', 'balochistan'), ('Khuzdar', 'balochistan'),
    ('Killa Abdullah', 'balochistan'), ('Killa Saifullah', 'balochistan'), ('Kohlu', 'balochistan'),
    ('Lehri', 'balochistan'), ('Loralai', 'balochistan'), ('Mastung', 'balochistan'), ('Musakhel', 'balochistan'),
    ('Nasirabad', 'balochistan'), ('Nushki', 'balochistan'), ('Panjgur', 'balochistan'), ('Pishin', 'balochistan'),
    ('Quetta', 'balochistan'), ('Sherani', 'balochistan'), ('Sibi', 'balochistan'), ('Sohbatpur', 'balochistan'),
    ('Surab', 'balochistan'), ('Washuk', 'balochistan'), ('Zhob', 'balochistan'), ('Ziarat', 'balochistan'),
    ('Usta Muhammad', 'balochistan'), ('Kachhi', 'balochistan'),
    # ICT
    ('ICT', 'ict')
]

EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

# --- Pre-calculated Maps (Module Level for DRY) ---
PROVINCE_DISPLAY_MAP = {value: display for value, display in PROVINCES}
PROVINCE_DISTRICT_MAP = {d[0]: d[1] for d in DISTRICTS}

# --- Respondent Info Views ---

def get_respondent_info_context():
    """Return standardized context for respondent info form."""
    return {
        'provinces': PROVINCES,
        'districts': DISTRICTS,
        'province_display_map': PROVINCE_DISPLAY_MAP,
        'province_district_map': PROVINCE_DISTRICT_MAP
    }

def prepare_respondent_data(request):
    """Prepare respondent data for form display with province display name."""
    if request.method == 'POST':
        respondent_data = request.POST.copy()
    else:
        respondent_data = request.session.get('respondent_info', {}).copy()
    
    # Add province display name for form rendering using pre-calculated map
    selected_province_code = respondent_data.get('province')
    if selected_province_code:
        respondent_data['province_display'] = PROVINCE_DISPLAY_MAP.get(selected_province_code, selected_province_code)
    else:
        respondent_data['province_display'] = ''
    
    return respondent_data

def validate_respondent_info_form(request):
    """Validate respondent info form data."""
    errors = []
    
    # Extract form data
    full_name = request.POST.get('full_name', '').strip()
    email = request.POST.get('email', '').strip()
    mobile = request.POST.get('mobile', '').strip()
    province = request.POST.get('province', '').strip()
    district = request.POST.get('district', '').strip()
    custom_district = request.POST.get('custom_district', '').strip()
    professional_roles_list = request.POST.getlist('professional_role')
    practice_areas = request.POST.getlist('practice_areas')
    experience_legal = request.POST.get('experience_legal', '').strip()
    experience_customs = request.POST.get('experience_customs', '').strip()
    kii_consent = request.POST.get('kii_consent', '').strip()

    # Validation
    if not full_name or len(full_name) > 255:
        errors.append("Full name is required and must be 255 characters or less")
    if not email or not re.match(EMAIL_REGEX, email):
        errors.append("Valid email is required")
    if not province:
        errors.append("Province is required")
    if not district and not custom_district:
        errors.append("District is required")
    if mobile and len(mobile) > 20:
        errors.append("Mobile number must be 20 characters or less")
    if not professional_roles_list:
        errors.append("Please select at least one professional role.")
    if 'legal' in professional_roles_list and not experience_legal:
        errors.append("Legal practitioner experience is required")
    if 'customs' in professional_roles_list and not experience_customs:
        errors.append("Customs agent experience is required")
    if experience_legal and len(experience_legal) > 50:
        errors.append("Legal experience must be 50 characters or less")
    if experience_customs and len(experience_customs) > 50:
        errors.append("Customs experience must be 50 characters or less")

    # Province-district consistency validation using pre-calculated map
    final_district = custom_district if custom_district else district
    if final_district and final_district in PROVINCE_DISTRICT_MAP and province:
        if PROVINCE_DISTRICT_MAP[final_district] != province:
            errors.append(f"Selected district ({final_district}) does not belong to selected province ({province})")
    if final_district and final_district not in PROVINCE_DISTRICT_MAP:
        logger.info(f"Custom district provided: {final_district}")

    # Prepare validated data
    respondent_data = {
        'full_name': sanitize_input(full_name),
        'email': email,
        'mobile': sanitize_input(mobile),
        'province': sanitize_input(province),
        'district': sanitize_input(final_district),
        'professional_roles': professional_roles_list,
        'practice_areas': practice_areas,
        'experience_legal': sanitize_input(experience_legal),
        'experience_customs': sanitize_input(experience_customs),
        'kii_consent': kii_consent,
    }

    is_valid = len(errors) == 0
    return respondent_data, errors, is_valid

def handle_respondent_info_post(request):
    logger.debug("Processing respondent info POST request")
    
    respondent_data, errors, is_valid = validate_respondent_info_form(request)
    
    if not is_valid:
        logger.warning(f"Validation errors in respondent_info: {errors}")
        context = get_progress_context(current_step=2, total_steps=6)
        context.update(get_respondent_info_context())
        context.update({
            'error': "Please correct the following errors:\n" + "\n".join(errors),
            'respondent_info': prepare_respondent_data(request)
        })
        return render(request, 'survey/respondent_info.html', context)

    try:
        # Save to session for data persistence
        validate_session_size(request)
        request.session['respondent_info'] = respondent_data
        request.session.modified = True

        # Convert lists to comma-separated strings for database
        professional_role_str = ",".join(respondent_data.get('professional_roles', [])) if respondent_data.get('professional_roles') else ''
        practice_areas_str = ",".join(respondent_data.get('practice_areas', [])) if respondent_data.get('practice_areas') else ''

        # Save to database
        survey_response = SurveyResponse(
            full_name=respondent_data['full_name'],
            email=respondent_data['email'],
            mobile=respondent_data['mobile'],
            province=respondent_data['province'],
            district=respondent_data['district'],
            professional_role=professional_role_str,  # Corrected field name and converted to string
            practice_areas=practice_areas_str,        # Corrected field name and converted to string
            experience_legal=respondent_data['experience_legal'],
            experience_customs=respondent_data['experience_customs'],
            kii_consent=respondent_data['kii_consent'],
        )
        survey_response.save()
        
        # Store the ID in session for future updates
        request.session['respondent_info']['id'] = survey_response.id
        request.session.modified = True

        logger.info("Respondent info saved successfully, redirecting to generic questions")
        return redirect('survey:generic_questions')
        
    except Exception as e:
        logger.error(f"Error saving respondent info: {str(e)}")
        context = get_progress_context(current_step=2, total_steps=6)
        context.update(get_respondent_info_context())
        context.update({
            'error': "An error occurred while saving your information. Please try again.",
            'respondent_info': prepare_respondent_data(request)
        })
        return render(request, 'survey/respondent_info.html', context)


def handle_respondent_info_get(request):
    """Handle GET request for respondent info form."""
    logger.debug("Rendering respondent info GET request")
    
    progress_context = get_progress_context(current_step=2, total_steps=6)
    context = progress_context
    context.update(get_respondent_info_context())
    context['respondent_info'] = prepare_respondent_data(request)
    
    logger.debug(f"Final context prepared for template with progress: {progress_context}")
    return render(request, 'survey/respondent_info.html', context)

def respondent_info_view(request):
    """Render the respondent information page (step 2) and handle submission."""
    if not request.session.get('survey_started'):
        logger.warning("Survey not started, redirecting to welcome")
        return redirect('survey:welcome')

    logger.debug(f"Respondent info view accessed - method: {request.method}")
    
    try:
        if request.method == 'POST':
            return handle_respondent_info_post(request)
        else:
            return handle_respondent_info_get(request)
            
    except Exception as e:
        logger.error(f"Unexpected error in respondent_info_view: {e}")
        context = get_progress_context(current_step=2, total_steps=6)
        context.update(get_respondent_info_context())
        context['respondent_info'] = prepare_respondent_data(request)
        context['error'] = "An unexpected error occurred. Please try again."
        return render(request, 'survey/respondent_info.html', context)