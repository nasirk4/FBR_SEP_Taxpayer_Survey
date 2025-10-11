from django.shortcuts import render, redirect
from httpcore import request
from survey.utils.progress import get_progress_context
from survey.utils.session_utils import sanitize_input, validate_session_size
import re
import logging

logger = logging.getLogger(__name__)

def respondent_info_view(request):
    """Render the respondent information page (step 2) and handle submission."""
    if not request.session.get('survey_started'):
        return redirect('survey:welcome')

    # --- Province and District Data Definitions (CORRECT PLACEMENT) ---
    provinces = [
        ('ajk', 'Azad Jammu and Kashmir'),
        ('balochistan', 'Balochistan'),
        ('gb', 'Gilgit-Baltistan'),
        ('ict', 'ICT'),
        ('kpk', 'Khyber Pakhtunkhwa'),
        ('punjab', 'Punjab'),
        ('sindh', 'Sindh'),
    ]
    
    # Province-district list
    districts = [
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
    
    province_district_map = {d[0]: d[1] for d in districts}
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    # Initial context definition for GET request
    # This must be defined *after* 'provinces' and 'districts'
    context = { 
        'provinces': provinces, 
        'districts': districts, 
        'respondent_info': request.session.get('respondent_info', {}) 
    }

    if request.method == 'POST':
        errors = []

        # --- Extraction ---
        # ... (POST extraction code remains the same)
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

        # --- Validation ---
        # ... (Validation code remains the same)
        if not full_name or len(full_name) > 255:
            errors.append("Full name is required and must be 255 characters or less")
        if not email or not re.match(email_regex, email):
            errors.append("Valid email is required")
        if not province:
            errors.append("Province is required")
        if not district:
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

        # Province-district consistency validation
        final_district = custom_district if custom_district else district
        if final_district and final_district in province_district_map and province:
            if province_district_map[final_district] != province:
                errors.append(f"Selected district ({final_district}) does not belong to selected province ({province})")
        if final_district and final_district not in province_district_map:
            logger.info(f"Custom district provided: {final_district}")

        if errors:
            logger.warning(f"Validation errors in respondent_info: {errors}")
            # Context for error case needs to be re-built
            context = get_progress_context(current_step=2)
            context.update({
                'provinces': provinces, # Ensure provinces is still available
                'districts': districts,
                'error': "Please correct the following errors:\n" + "\n".join(errors),
                'respondent_info': request.POST
            })
            return render(request, 'survey/respondent_info.html', context)

        # --- Saving to Session ---
        # ... (Session saving code remains the same)
        validate_session_size(request)
        request.session['respondent_info'] = {
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
        request.session.modified = True
        return redirect('survey:generic_questions')

    # --- GET Request ---
    # The context built at the top is sufficient for a GET request
    context.update(get_progress_context(current_step=2, total_steps=6))
    logger.debug(f"DEBUG: get_progress_context returned: {context}")
    # The 'districts' and 'respondent_info' are already in the context from the top definition
    return render(request, 'survey/respondent_info.html', context)