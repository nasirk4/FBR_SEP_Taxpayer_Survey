// static/js/respondent_info_script.js
function handleBackNavigation(url) {
    window.location.href = url;
}

document.addEventListener('DOMContentLoaded', function () {
    console.log('respondent_info_script.js loaded successfully');
    const form = document.getElementById('respondent-form');
    const roleError = document.getElementById('roleError');
    const isMobile = window.innerWidth <= 767;

    // --- District Dropdown Elements ---
    const searchInput = document.getElementById('district_search');
    const dropdown = document.getElementById('district_dropdown');
    const customInput = document.getElementById('custom_district');
    const finalDistrict = document.getElementById('final_district');
    const dropdownOptions = dropdown.querySelectorAll('.dropdown-option');

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

        // Toggle visibility
        section.style.display = isVisible ? 'block' : 'none';
        section.setAttribute('aria-hidden', !isVisible);

        // Find all radio inputs in the section and set 'required'
        const radios = section.querySelectorAll('input[type="radio"]');
        radios.forEach(radio => {
            radio.required = isVisible;
        });

        // Clear selection if hidden
        if (!isVisible) {
            radios.forEach(radio => radio.checked = false);
        }
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

        // Toggle visibility of experience sections and update required status
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

    // Initial setup for experience sections based on loaded session data
    updateRoleSelection();

    // --- Form Submission Validation ---
    form.addEventListener('submit', function(e) {
        let isValid = true;

        // 1. Validate professional role (required custom logic)
        if (!validateProfessionalRole()) {
            isValid = false;
            // Scroll to the error message for visibility
            roleError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }

        // 2. Standard HTML5 required validation
        const requiredFields = Array.from(form.querySelectorAll('[required]'));
        const invalidFields = requiredFields.filter(field => {
            // Check for empty string values
            if (!field.value.trim()) return true;

            // Specific check for district which uses a hidden input
            if (field.id === 'district_search' && !finalDistrict.value) return true;

            // Check if radio groups are required but unchecked
            if (field.type === 'radio' && field.required) {
                const radioName = field.name;
                const radiosInGroup = form.querySelectorAll(`input[name="${radioName}"]`);
                const isChecked = Array.from(radiosInGroup).some(radio => radio.checked);
                return !isChecked && field.offsetParent !== null; // Only count if visible and not checked
            }
            return false;
        });

        if (invalidFields.length > 0) {
            isValid = false;
            invalidFields.forEach(field => {
                field.setAttribute('aria-invalid', 'true');
                // Add visual error styling
                if (field.type !== 'radio') {
                    field.style.borderColor = 'var(--fbr-red)';
                } else {
                    // For radio groups, highlight the container
                    const container = field.closest('.experience-section');
                    if (container) {
                        container.style.borderColor = 'var(--fbr-red)';
                    }
                }
            });

            // Scroll to first invalid field
            if (invalidFields[0]) {
                invalidFields[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
            }

            // Show a general notification on mobile if fields are missing
            if (isMobile) showMobileNotification('Please fill in all required fields');
        }

        // 3. Process practice areas into a single hidden field
        const practiceAreaCheckboxes = form.querySelectorAll('input[name="practice_areas"]:checked');
        const practiceAreaValues = Array.from(practiceAreaCheckboxes).map(cb => cb.value);

        // Create or update hidden field for practice areas
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

            // Also reset container borders for radio groups
            if (field.type === 'radio') {
                const container = field.closest('.experience-section');
                if (container) {
                    container.style.borderColor = '#eee';
                }
            }
        }
    });

    // --- District Dropdown Logic ---
    // Show dropdown when search input is focused or has value
    searchInput.addEventListener('focus', function() {
        filterDistricts();
        dropdown.style.display = 'block';
        if (isMobile) document.body.classList.add('dropdown-open');
    });

    // Filter districts based on search input
    searchInput.addEventListener('input', function() {
        filterDistricts();
        dropdown.style.display = 'block';
        // Clear custom input if user starts typing a search
        customInput.style.display = 'none';
        customInput.required = false;
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
                customInput.value = ''; // Clear custom input on selection
                searchInput.value = ''; // Clear search input visually
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

    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !dropdown.contains(e.target) && !customInput.contains(e.target)) {
            dropdown.style.display = 'none';
            if (isMobile) document.body.classList.remove('dropdown-open');
        }
    });

    // Filter function
    function filterDistricts() {
        const query = searchInput.value.toLowerCase();
        let hasVisibleOptions = false;

        dropdownOptions.forEach(option => {
            const text = option.textContent.toLowerCase();
            const isCustomOption = option.classList.contains('custom-option');

            if (isCustomOption) {
                 // Custom option always shows when dropdown is open, unless a perfect match is found
                option.style.display = 'block';
            } else if (text.includes(query)) {
                option.style.display = 'block';
                hasVisibleOptions = true;
            } else {
                option.style.display = 'none';
            }
        });

        // Hide the "My district is not in the list" if many options are showing on a clear query.
        const customOption = dropdown.querySelector('.custom-option');
        if (query && !hasVisibleOptions) {
             customOption.style.display = 'block';
        } else if (query && hasVisibleOptions) {
             customOption.style.display = 'block';
        } else if (!query) {
             customOption.style.display = 'block';
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
                // It's a custom district not in the list
                customInput.style.display = 'block';
                customInput.value = existingValue;
                customInput.required = true;
                searchInput.value = existingValue;
            }
        }
    })();

    // Mobile-friendly notification function
    function showMobileNotification(message) {
        const existingNotification = document.getElementById('mobile-notification');
        if (existingNotification) existingNotification.remove();

        const notification = document.createElement('div');
        notification.id = 'mobile-notification';
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: var(--fbr-red);
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            z-index: 10000;
            font-size: 14px;
            max-width: 90%;
            text-align: center;
            transition: opacity 0.3s ease;
        `;
        notification.textContent = message;
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
});