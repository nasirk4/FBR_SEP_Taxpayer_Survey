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
    
    // --- District Dropdown Elements ---
    const searchInput = document.getElementById('district_search');
    const dropdown = document.getElementById('district_dropdown');
    const customInput = document.getElementById('custom_district');
    const finalDistrict = document.getElementById('final_district');
    const dropdownOptions = dropdown.querySelectorAll('.dropdown-option');
    const districtOptions = dropdown.querySelectorAll('.dropdown-option');

    // --- Professional Role Elements ---
    const legalCheckbox = document.getElementById('legalPractitioner');
    const customsCheckbox = document.getElementById('customsAgent');
    const roleField = document.getElementById('professional_role_combined');
    const legalExpSection = document.getElementById('legalExperience');
    const customsExpSection = document.getElementById('customsExperience');
    const legalExpRadios = document.querySelectorAll('input[name="experience_legal"]');
    const customsExpRadios = document.querySelectorAll('input[name="experience_customs"]');

    // Track dropdown state to prevent immediate closing
    let isDropdownInteraction = false;

    /**
     * Toggles the visibility and 'required' status for experience sections.
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
    
    // --- Improved Dropdown Functions ---
    
    /**
     * Show dropdown on click (not just focus)
     */
    function showDropdown(dropdownElement, searchElement) {
        dropdownElement.style.display = 'block';
        if (isMobile) document.body.classList.add('dropdown-open');
        
        // Mark as dropdown interaction to prevent immediate closing
        isDropdownInteraction = true;
        setTimeout(() => { isDropdownInteraction = false; }, 100);
    }

    /**
     * Hide dropdown
     */
    function hideDropdown(dropdownElement) {
        dropdownElement.style.display = 'none';
        if (isMobile) document.body.classList.remove('dropdown-open');
    }

    // --- Province Dropdown Logic ---
    
    // Show dropdown on click (not just focus)
    provinceSearch.addEventListener('click', function (e) {
        e.stopPropagation();
        showDropdown(provinceDropdown, provinceSearch);
        showAllProvinces();
    });

    provinceSearch.addEventListener('focus', function () {
        showDropdown(provinceDropdown, provinceSearch);
        showAllProvinces();
    });

    provinceSearch.addEventListener('input', function () {
        filterProvinces();
        showDropdown(provinceDropdown, provinceSearch);
    });

    provinceOptions.forEach(option => {
        option.addEventListener('mousedown', function (e) {
            e.preventDefault(); // Prevent input blur
        });
        
        option.addEventListener('click', function () {
            const selectedText = this.textContent;
            const selectedValue = this.dataset.value;
            
            provinceSearch.value = selectedText;
            finalProvince.value = selectedValue;
            
            // Update selected state
            provinceOptions.forEach(opt => opt.classList.remove('selected'));
            this.classList.add('selected');
            
            hideDropdown(provinceDropdown);
            
            // Reset and filter districts based on new province
            searchInput.value = '';
            finalDistrict.value = '';
            customInput.style.display = 'none';
            customInput.required = false;
            filterDistricts();
        });
    });

    // Show all provinces (reset filtering)
    function showAllProvinces() {
        provinceOptions.forEach(option => {
            option.style.display = 'block';
        });
    }

    function filterProvinces() {
        const query = provinceSearch.value.toLowerCase();
        provinceOptions.forEach(option => {
            const text = option.textContent.toLowerCase();
            option.style.display = text.includes(query) ? 'block' : 'none';
        });
    }

    // --- District Dropdown Logic ---
    
    // Show dropdown on click (not just focus)
    searchInput.addEventListener('click', function(e) {
        e.stopPropagation();
        showDropdown(dropdown, searchInput);
        filterDistricts();
    });

    searchInput.addEventListener('focus', function() {
        showDropdown(dropdown, searchInput);
        filterDistricts();
    });

    searchInput.addEventListener('input', function() {
        filterDistricts();
        showDropdown(dropdown, searchInput);
        customInput.style.display = 'none';
        customInput.required = false;
    });

    // Handle selection from dropdown
    dropdownOptions.forEach(option => {
        option.addEventListener('mousedown', function (e) {
            e.preventDefault(); // Prevent input blur
        });
        
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
            hideDropdown(dropdown);
        });
    });

    // Handle custom district input
    customInput.addEventListener('input', function() {
        finalDistrict.value = this.value;
        searchInput.value = this.value;
    });

    // --- Improved Click Outside Handler ---
    document.addEventListener('click', function(e) {
        // Don't close if it's a dropdown interaction
        if (isDropdownInteraction) return;
        
        // Check for province dropdown
        const isProvinceRelated = 
            provinceSearch.contains(e.target) || 
            provinceDropdown.contains(e.target);
        
        if (!isProvinceRelated) {
            hideDropdown(provinceDropdown);
        }
        
        // Check for district dropdown
        const isDistrictRelated = 
            searchInput.contains(e.target) || 
            dropdown.contains(e.target) || 
            customInput.contains(e.target);
        
        if (!isDistrictRelated) {
            hideDropdown(dropdown);
        }
    });

    // --- District Filtering Function ---
    function filterDistricts() {
        const query = searchInput.value.toLowerCase();
        const selectedProvince = finalProvince.value;
        
        console.log('Filtering districts - Province:', selectedProvince, 'Query:', query);

        districtOptions.forEach(option => {
            const text = option.textContent.toLowerCase();
            const isCustomOption = option.classList.contains('custom-option');
            const optionProvince = option.dataset.province;

            // Skip custom option for now
            if (isCustomOption) {
                return;
            }

            let shouldShow = true;

            // Filter by province if one is selected
            if (selectedProvince && optionProvince !== selectedProvince) {
                shouldShow = false;
            }
            
            // Filter by search query if there is one
            if (shouldShow && query && !text.includes(query)) {
                shouldShow = false;
            }

            option.style.display = shouldShow ? 'block' : 'none';
        });

        // Handle custom option visibility
        const customOption = dropdown.querySelector('.custom-option');
        if (selectedProvince) {
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

    // --- Improved Form Submission Validation ---
    form.addEventListener('submit', function(e) {
        let isValid = true;
        const errorMessages = [];

        // Validate professional role
        if (!validateProfessionalRole()) {
            isValid = false;
            errorMessages.push('Please select at least one professional role');
        }

        // Validate province
        if (!finalProvince.value) {
            isValid = false;
            provinceSearch.style.borderColor = 'var(--fbr-red, #dc3545)';
            errorMessages.push('Province is required');
        }

        // Validate district
        if (!finalDistrict.value) {
            isValid = false;
            searchInput.style.borderColor = 'var(--fbr-red, #dc3545)';
            errorMessages.push('District is required');
        }

        // Validate required fields
        const requiredFields = Array.from(form.querySelectorAll('[required]'));
        const invalidFields = requiredFields.filter(field => {
            if (field.id === 'province_search' || field.id === 'district_search') {
                // These are handled separately above
                return false;
            }
            if (!field.value.trim()) return true;
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
            errorMessages.push('Please fill in all required fields');
        }

        // Handle practice areas
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
            
            // Show error notification
            if (errorMessages.length > 0) {
                showMobileNotification(errorMessages.join(', '));
            }
            
            // Scroll to first error
            const firstErrorField = document.querySelector('[aria-invalid="true"]');
            if (firstErrorField) {
                firstErrorField.scrollIntoView({ behavior: 'smooth', block: 'center' });
            } else if (roleError.classList.contains('show')) {
                roleError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
            
            return false;
        }
        
        // If valid, allow form submission to proceed
        console.log('Form validation passed, submitting...');
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
        
        // Reset province/district borders
        if (field.id === 'province_search' || field === provinceSearch) {
            provinceSearch.style.borderColor = '#ccc';
        }
        if (field.id === 'district_search' || field === searchInput) {
            searchInput.style.borderColor = '#ccc';
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