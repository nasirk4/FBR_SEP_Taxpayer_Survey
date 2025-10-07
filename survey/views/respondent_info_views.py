# survey/views/respondent_info_views.py

from django.shortcuts import render, redirect
# Assuming .utils contains get_progress_context, sanitize_input, validate_session_size
from survey.utils.progress import get_progress_context
from survey.utils.session_utils import sanitize_input, validate_session_size
import re
import logging

logger = logging.getLogger(__name__)

def respondent_info_view(request):
    """Render the respondent information page (step 2) and handle submission."""
    if not request.session.get('survey_started'):
        return redirect('survey:welcome')

    districts = sorted([
        "Abbottabad", "Astore", "Attock", "Awaran", "Badin", "Bagh", "Bahawalnagar", "Bahawalpur", "Bajaur", "Bannu",
        "Barkhan", "Batagram", "Bhakkar", "Bhimber", "Buner", "Chagai", "Chakwal", "Chaman", "Charsadda", "Chiniot",
        "Dadu", "Darel", "Dera Bugti", "Dera Ghazi Khan", "Dera Ismail Khan", "Diamer", "Duki", "Faisalabad", "Ghanche",
        "Ghizer", "Ghotki", "Gilgit", "Gujranwala", "Gujrat", "Gupis-Yasin", "Gwadar", "Hafizabad", "Hangu", "Haripur",
        "Harnai", "Hattian", "Haveli", "Hub", "Hunza", "Hyderabad", "Islamabad", "Jacobabad", "Jafarabad", "Jamshoro",
        "Jhal Magsi", "Jhang", "Jhelum", "Kachhi", "Kalat", "Kambar/Shahdad Kot", "Karak", "Karachi Central",
        "Karachi East", "Karachi Malir", "Karachi South", "Karachi West", "Kashmore", "Kasur", "Kech", "Khairpur",
        "Khanewal", "Kharan", "Kharmang", "Khushab", "Khuzdar", "Khyber", "Killa Abdullah", "Killa Saifullah", "Kohat",
        "Kohistan", "Kohlu", "Kolai Pallas", "Korangi", "Kot Adu", "Kotli", "Kurram", "Lahore", "Lakki Marwat",
        "Larkana", "Lasbela", "Layyah", "Lehri", "Levies", "Lodhran", "Lower Chitral", "Lower Dir", "Lower Kohistan",
        "Loralai", "Lyari", "Malakand", "Malir", "Mandi Bahauddin", "Mansehra", "Mardan", "Mastung", "Matiari",
        "Mianwali", "Mirpur", "Mirpur Khas", "Mohmand", "Multan", "Murree", "Musakhel", "Muzaffarabad", "Muzaffargarh",
        "Nagar", "Nankana Sahib", "Narowal", "Naseerabad", "Naushahro Feroze", "Neelum", "North Waziristan", "Nowshera",
        "Nushki", "Okara", "Orakzai", "Pakpattan", "Panjgur", "Peshawar", "Pishin", "Poonch", "Qambar/Shahdad Kot",
        "Qila Saifullah", "Quetta", "Rahim Yar Khan", "Rajanpur", "Rawalpindi", "Roundu", "Sahiwal", "Sanghar",
        "Sargodha", "Shaheed Benazirabad", "Shaheed Sikandarabad", "Shangla", "Sheikhupura", "Sherani", "Shigar",
        "Shikarpur", "Sialkot", "Sibi", "Skardu", "Sohbatpur", "South Waziristan", "Sudhnoti", "Sujawal", "Sukkur",
        "Swabi", "Swat", "Tando Allahyar", "Tando Muhammad Khan", "Tangir", "Tank", "Taunsa", "Tharparkar", "Thatta",
        "Toba Tek Singh", "Torghar", "Umerkot", "Upper Chitral", "Upper Dir", "Upper Kohistan", "Vehari", "Washuk",
        "Wazirabad", "Zhob", "Ziarat"
    ])

    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if request.method == 'POST':
        errors = []

        # --- Extraction: Using getlist for multi-select fields ---
        district = request.POST.get('district', '').strip()
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()

        # 1. Professional Roles (Multi-select)
        professional_roles_list = request.POST.getlist('professional_role')

        mobile = request.POST.get('mobile', '').strip()
        province = request.POST.get('province', '').strip()
        experience_legal = request.POST.get('experience_legal', '').strip()
        experience_customs = request.POST.get('experience_customs', '').strip()

        # 2. Practice Areas (Multi-select, Optional)
        practice_areas = request.POST.getlist('practice_areas')

        # 3. KII Consent (Radio, Optional)
        kii_consent = request.POST.get('kii_consent', '').strip()

        # --- Validation ---

        if not full_name or len(full_name) > 255:
            errors.append("Full name is required and must be 255 characters or less")
        if not email or not re.match(email_regex, email):
            errors.append("Valid email is required")
        if not district or district not in districts:
            errors.append("Valid district is required")


        if not professional_roles_list:
            errors.append("Please select at least one professional role.")


        if mobile and len(mobile) > 20:
            errors.append("Mobile number must be 20 characters or less")
        if province and len(province) > 100:
            errors.append("Province must be 100 characters or less")

        # Experience validation (remains the same)
        if experience_legal and len(experience_legal) > 50:
            errors.append("Legal experience must be 50 characters or less")
        if experience_customs and len(experience_customs) > 50:
            errors.append("Customs experience must be 50 characters or less")

        if errors:
            logger.warning(f"Validation errors in respondent_info: {errors}")
            context = get_progress_context(current_step=2)
            context.update({
                'districts': districts,
                'error': "Please correct the following errors:\n" + "\n".join(errors),
                # request.POST is correctly used here to repopulate fields on error
                'respondent_info': request.POST
            })
            return render(request, 'survey/respondent_info.html', context)

        # --- Saving to Session (All persistence issues fixed here) ---
        validate_session_size(request)
        request.session['respondent_info'] = {
            'full_name': sanitize_input(full_name),
            'email': email,
            'district': district,
            'mobile': sanitize_input(mobile),

            # Save the list under the correct session key name
            'professional_roles': professional_roles_list,

            'province': sanitize_input(province),
            'experience_legal': sanitize_input(experience_legal),
            'experience_customs': sanitize_input(experience_customs),

            # Practice Areas saved as a list
            'practice_areas': practice_areas,

            # KII Consent saved as a string
            'kii_consent': kii_consent,
        }
        request.session.modified = True
        return redirect('survey:generic_questions')

    # --- GET Request (Page Load) ---
    context = get_progress_context(current_step=2, total_steps=6)
    # DEBUG: Log what get_progress_context returned
    logger.debug(f"DEBUG: get_progress_context returned: {context}")
    context['districts'] = districts
    context['respondent_info'] = request.session.get('respondent_info', {})
    return render(request, 'survey/respondent_info.html', context)