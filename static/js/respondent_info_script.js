function handleBackNavigation(url) {
    window.location.href = url;
}

document.addEventListener('DOMContentLoaded', function () {
    console.log('respondent_info_script.js loaded successfully');
    const form = document.getElementById('respondent-form');
    const roleError = document.getElementById('roleError');
    const isMobile = window.innerWidth <= 767;

    // --- Province Dropdown Elements ---
    const provinceSearch = document.getElementById('province_search');
    const provinceDropdown = document.getElementById('province_dropdown');
    const finalProvince = document.getElementById('final_province');
    const provinceOptions = provinceDropdown.querySelectorAll('.dropdown-option');
    const provinceSelect = document.getElementById('province');
    
    // --- District Dropdown Elements ---
    const searchInput = document.getElementById('district_search');
    const dropdown = document.getElementById('district_dropdown');
    const customInput = document.getElementById('custom_district');
    const finalDistrict = document.getElementById('final_district');
    const dropdownOptions = dropdown.querySelectorAll('.dropdown-option');
    
    // ADD THE MISSING VARIABLE - This was causing the issue
    const districtOptions = dropdown.querySelectorAll('.dropdown-option');

    // --- Professional Role Elements ---
    const legalCheckbox = document.getElementById('legalPractitioner');
    const customsCheckbox = document.getElementById('customsAgent');
    const roleField = document.getElementById('professional_role_combined');
    const legalExpSection = document.getElementById('legalExperience');
    const customsExpSection = document.getElementById('customsExperience');
    const legalExpRadios = document.querySelectorAll('input[name="experience_legal"]');
    const customsExpRadios = document.querySelectorAll('input[name="experience_customs"]');

    /**
     * Toggles the visibility and 'required' status for experience sections.
     * @param {HTMLElement} section The experience section div.
     * @param {boolean} isVisible Whether the section should be visible/required.
     */
    function toggleExperienceSection(section, isVisible) {
        if (!section) return;
        section.style.display = isVisible ? 'block' : 'none';
        section.setAttribute('aria-hidden', !isVisible);
        const radios = section.querySelectorAll('input[type="radio"]');
        radios.forEach(radio => {
            radio.required = isVisible;
            if (!isVisible) radio.checked = false;
        });
    }

    /**
     * Updates the hidden 'professional_role_combined' field based on selected checkboxes.
     * Hides/shows the corresponding experience sections.
     */
    function updateRoleSelection() {
        const legalChecked = legalCheckbox.checked;
        const customsChecked = customsCheckbox.checked;
        roleField.value = legalChecked && customsChecked ? 'both'
            : legalChecked ? 'legal'
            : customsChecked ? 'customs'
            : '';
        toggleExperienceSection(legalExpSection, legalChecked);
        toggleExperienceSection(customsExpSection, customsChecked);
    }

    /**
     * Validates that at least one professional role is selected.
     * @returns {boolean} True if validation passes.
     */
    function validateProfessionalRole() {
        if (!legalCheckbox.checked && !customsCheckbox.checked) {
            roleError.classList.add('show');
            return false;
        } else {
            roleError.classList.remove('show');
            return true;
        }
    }

    // --- Event Listeners for Professional Roles ---
    legalCheckbox.addEventListener('change', function() {
        updateRoleSelection();
        validateProfessionalRole();
    });

    customsCheckbox.addEventListener('change', function() {
        updateRoleSelection();
        validateProfessionalRole();
    });

    // Initial setup for experience sections
    updateRoleSelection();

    // Province Dropdown Logic
    provinceSearch.addEventListener('focus', function () {
        filterProvinces();
        provinceDropdown.style.display = 'block';
        if (isMobile) document.body.classList.add('dropdown-open');
    })

    provinceSearch.addEventListener('input', function () {
        filterProvinces();
        provinceDropdown.style.display = 'block';
    });
    provinceOptions.forEach(option => {
        option.addEventListener('click', function () {
            provinceSearch.value = this.textContent;
            finalProvince.value = this.dataset.value;
            provinceOptions.forEach(opt => opt.classList.remove('selected'));
            this.classList.add('selected');
            provinceDropdown.style.display = 'none';
            if (isMobile) document.body.classList.remove('dropdown-open');
            // Reset district fields and filter
            districtSearch.value = '';
            finalDistrict.value = '';
            customInput.style.display = 'none';
            customInput.required = false;
            filterDistricts();
        });
    });
    function filterProvinces() {
        const query = provinceSearch.value.toLowerCase();
        provinceOptions.forEach(option => {
            const text = option.textContent.toLowerCase();
            option.style.display = text.includes(query) ? 'block' : 'none';
        });
    }


    // -- District Dropdown Logic ---
    // Show dropdown when search input is focused or has value
    searchInput.addEventListener('focus', function() {
        filterDistricts();
        dropdown.style.display = 'block';
        if (isMobile) document.body.classList.add('dropdown-open');
    });

    // Filter districts based on search input and province
    searchInput.addEventListener('input', function() {
        filterDistricts();
        dropdown.style.display = 'block';
        customInput.style.display = 'none';
        customInput.required = false;
    });

    // Reset district when province changes
    provinceSelect.addEventListener('change', function() {
        searchInput.value = '';
        finalDistrict.value = '';
        customInput.value = '';
        customInput.style.display = 'none';
        customInput.required = false;
        filterDistricts();
        dropdown.style.display = 'block';
    });

    // Handle selection from dropdown
    dropdownOptions.forEach(option => {
        option.addEventListener('click', function() {
            const value = this.dataset.value;
            dropdownOptions.forEach(opt => opt.classList.remove('selected'));
            this.classList.add('selected');
            if (value === '__custom__') {
                customInput.style.display = 'block';
                customInput.required = true;
                customInput.value = '';
                searchInput.value = '';
                finalDistrict.value = '';
                if (isMobile) customInput.focus();
            } else {
                searchInput.value = this.textContent;
                finalDistrict.value = value;
                customInput.style.display = 'none';
                customInput.required = false;
            }
            dropdown.style.display = 'none';
            if (isMobile) document.body.classList.remove('dropdown-open');
        });
    });

    // Handle custom district input
    customInput.addEventListener('input', function() {
        finalDistrict.value = this.value;
        searchInput.value = this.value;
    });

    // Close dropdown when clicking outside - IMPROVED VERSION
    document.addEventListener('click', function(e) {
        const isDistrictRelated = 
            searchInput.contains(e.target) || 
            dropdown.contains(e.target) || 
            customInput.contains(e.target) ||
            (e.target.classList && e.target.classList.contains('dropdown-option')) ||
            (e.target.parentElement && e.target.parentElement.classList && 
             e.target.parentElement.classList.contains('dropdown-option'));
        
        if (!isDistrictRelated) {
            dropdown.style.display = 'none';
            if (isMobile) document.body.classList.remove('dropdown-open');
        }
    });

    // Filter function - NOW USING districtOptions VARIABLE
    function filterDistricts() {
        const query = searchInput.value.toLowerCase();
        const selectedProvince = finalProvince.value;
        let hasVisibleOptions = false;

        districtOptions.forEach(option => {
            const text = option.textContent.toLowerCase();
            const isCustomOption = option.classList.contains('custom-option');
            const optionProvince = option.dataset.province;

            if (isCustomOption && selectedProvince) {
                option.style.display = 'block';
            } else if (selectedProvince && optionProvince !== selectedProvince) {
                option.style.display = 'none';
            } else if (text.includes(query)) {
                option.style.display = 'block';
                hasVisibleOptions = true;
            } else {
                option.style.display = 'none';
            }
        });

        const customOption = dropdown.querySelector('.custom-option');
        if (query && !hasVisibleOptions && selectedProvince) {
            customOption.style.display = 'block';
        } else if (query && hasVisibleOptions && selectedProvince) {
            customOption.style.display = 'block';
        } else if (!query && selectedProvince) {
            customOption.style.display = 'block';
        } else {
            customOption.style.display = 'none';
        }
    }

    // Initialize state for district field
    (function initializeDistrict() {
        const existingValue = finalDistrict.value;
        if (existingValue) {
            const matchingOption = Array.from(dropdownOptions).find(
                option => option.dataset.value === existingValue
            );
            if (matchingOption) {
                searchInput.value = matchingOption.textContent;
                matchingOption.classList.add('selected');
            } else {
                customInput.style.display = 'block';
                customInput.value = existingValue;
                customInput.required = true;
                searchInput.value = existingValue;
            }
        }
    })();

    // --- Form Submission Validation ---
    form.addEventListener('submit', function(e) {
        let isValid = true;

        if (!validateProfessionalRole()) {
            isValid = false;
            roleError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }

        const requiredFields = Array.from(form.querySelectorAll('[required]'));
        const invalidFields = requiredFields.filter(field => {
            if (!field.value.trim()) return true;
            if (field.id === 'district_search' && !finalDistrict.value) return true;
            if (field.type === 'radio' && field.required) {
                const radioName = field.name;
                const radiosInGroup = form.querySelectorAll(`input[name="${radioName}"]`);
                const isChecked = Array.from(radiosInGroup).some(radio => radio.checked);
                return !isChecked && field.offsetParent !== null;
            }
            return false;
        });

        if (invalidFields.length > 0) {
            isValid = false;
            invalidFields.forEach(field => {
                field.setAttribute('aria-invalid', 'true');
                if (field.type !== 'radio') {
                    field.style.borderColor = 'var(--fbr-red, #dc3545)';
                } else {
                    const container = field.closest('.experience-section');
                    if (container) container.style.borderColor = 'var(--fbr-red, #dc3545)';
                }
            });
            if (invalidFields[0]) {
                invalidFields[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
            if (isMobile) showMobileNotification('Please fill in all required fields');
        }

        const practiceAreaCheckboxes = form.querySelectorAll('input[name="practice_areas"]:checked');
        const practiceAreaValues = Array.from(practiceAreaCheckboxes).map(cb => cb.value);
        let hiddenPracticeAreaField = document.getElementById('hidden_practice_areas');
        if (!hiddenPracticeAreaField) {
            hiddenPracticeAreaField = document.createElement('input');
            hiddenPracticeAreaField.type = 'hidden';
            hiddenPracticeAreaField.name = 'practice_areas';
            hiddenPracticeAreaField.id = 'hidden_practice_areas';
            form.appendChild(hiddenPracticeAreaField);
        }
        hiddenPracticeAreaField.value = practiceAreaValues.join(',');

        if (!isValid) {
            e.preventDefault();
            return false;
        }
    });

    // Reset invalid state on input
    form.addEventListener('input', function(e) {
        const field = e.target;
        if (field.hasAttribute('aria-invalid')) {
            field.removeAttribute('aria-invalid');
            field.style.borderColor = '#ccc';
            if (field.type === 'radio') {
                const container = field.closest('.experience-section');
                if (container) container.style.borderColor = '#eee';
            }
        }
    });

    // Mobile-friendly notification function
    function showMobileNotification(message) {
        const existingNotification = document.getElementById('mobile-notification');
        if (existingNotification) existingNotification.remove();
        const notification = document.createElement('div');
        notification.id = 'mobile-notification';
        notification.style.cssText = `
            position: fixed; top: 20px; left: 50%; transform: translateX(-50%);
            background: var(--fbr-blue, #007bff); color: white; padding: 12px 20px;
            border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.2); z-index: 10000;
            font-size: 14px; max-width: 90%; text-align: center; transition: opacity 0.3s ease;
        `;
        notification.textContent = message;
        document.body.appendChild(notification);
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
});