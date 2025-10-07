// static/js/generic_questions_script.js
function handleBackNavigation(url) {
    window.location.href = url;
}

document.addEventListener('DOMContentLoaded', function () {
    // Error box scrolling
    const errorBox = document.getElementById('error-box');
    if (errorBox) {
        setTimeout(() => errorBox.scrollIntoView({ behavior: 'smooth', block: 'center' }), 100);
    }

    // G3: Show/hide G3a based on G3 selection
    const g3Yes = document.getElementById('g3_yes');
    const g3No = document.getElementById('g3_no');
    const g3aSection = document.getElementById('g3a_section');

    function toggleG3a() {
        if (g3Yes && g3Yes.checked) {
            g3aSection.style.display = 'block';
            document.querySelector('textarea[name="g2a_weaknesses_details"]').required = true;
        } else {
            g3aSection.style.display = 'none';
            document.querySelector('textarea[name="g2a_weaknesses_details"]').required = false;
            document.querySelector('textarea[name="g2a_weaknesses_details"]').value = '';
        }
    }

    if (g3Yes && g3No && g3aSection) {
        g3Yes.addEventListener('change', toggleG3a);
        g3No.addEventListener('change', toggleG3a);
        toggleG3a(); // Initialize on load
    }

    // G8: Show/hide G8 details based on G8 selection
    const g8YesSignificantly = document.getElementById('g8_yes_significantly');
    const g8YesSomewhat = document.getElementById('g8_yes_somewhat');
    const g8Details = document.getElementById('g8_details');

    function toggleG8Details() {
        if (g8YesSignificantly && g8YesSomewhat && g8Details) {
            g8Details.style.display = (g8YesSignificantly.checked || g8YesSomewhat.checked) ? 'block' : 'none';
            document.querySelector('textarea[name="g8_regional_differences_text"]').required = (g8YesSignificantly.checked || g8YesSomewhat.checked);
            if (!(g8YesSignificantly.checked || g8YesSomewhat.checked)) {
                document.querySelector('textarea[name="g8_regional_differences_text"]').value = '';
            }
        }
    }

    if (g8YesSignificantly && g8YesSomewhat && g8Details) {
        g8YesSignificantly.addEventListener('change', toggleG8Details);
        g8YesSomewhat.addEventListener('change', toggleG8Details);
        document.getElementById('g8_no_similar')?.addEventListener('change', toggleG8Details);
        document.getElementById('g8_dont_know')?.addEventListener('change', toggleG8Details);
        toggleG8Details(); // Initialize on load
    }

    // G4: Other field toggle
    window.toggleG4Other = function(checkbox) {
        const g4OtherSpecify = document.getElementById('g4_other_specify');
        const g4OtherText = document.getElementById('g4_other_text');

        if (checkbox.checked && checkbox.value === 'others') {
            g4OtherSpecify.style.display = 'block';
            g4OtherText.required = true;
        } else {
            g4OtherSpecify.style.display = 'none';
            g4OtherText.required = false;
            g4OtherText.value = '';
        }
    };

    // Form validation
    const form = document.getElementById('genericQuestionsForm');
    if (form) {
        form.addEventListener('submit', function (e) {
            let isValid = true;
            const errorMessages = [];

            // Validate radio groups (G1, G3, G5, G6, G7, G8)
            const radioGroups = [
                'g1_iris_rating', 'g2_system_weaknesses', 'g5_clients_change',
                'g6_fee_change', 'g7_digital_literacy_impact', 'g8_regional_differences'
            ];
            radioGroups.forEach(groupName => {
                const selected = document.querySelector(`input[name="${groupName}"]:checked`);
                const errorDiv = document.getElementById(`${groupName}_error_inline`);
                if (!selected) {
                    if (errorDiv) {
                        errorDiv.style.display = 'block';
                        errorDiv.setAttribute('aria-live', 'polite');
                    }
                    document.querySelector(`input[name="${groupName}"]`).setAttribute('aria-invalid', 'true');
                    document.querySelector(`input[name="${groupName}"]`).setAttribute('aria-describedby', `${groupName}_error_inline`);
                    isValid = false;
                    errorMessages.push(`Please select an option for ${groupName.replace('_', ' ').replace('g', 'G').replace('iris rating', 'platform usability')}`);
                } else {
                    if (errorDiv) {
                        errorDiv.style.display = 'none';
                    }
                    document.querySelectorAll(`input[name="${groupName}"]`).forEach(radio => {
                        radio.setAttribute('aria-invalid', 'false');
                        radio.removeAttribute('aria-describedby');
                    });
                }
            });

            // Validate G4 checkboxes
            const g4Checkboxes = document.querySelectorAll('input[name="g4_challenged_groups"]');
            const g4Selected = document.querySelectorAll('input[name="g4_challenged_groups"]:checked').length;
            const g4Error = document.getElementById('g4_challenged_groups_error_inline');
            if (g4Selected === 0) {
                if (g4Error) {
                    g4Error.style.display = 'block';
                    g4Error.setAttribute('aria-live', 'polite');
                }
                g4Checkboxes.forEach(cb => {
                    cb.setAttribute('aria-invalid', 'true');
                    cb.setAttribute('aria-describedby', 'g4_challenged_groups_error_inline');
                });
                isValid = false;
                errorMessages.push("Please select at least one challenged group in G4");
            } else {
                if (g4Error) {
                    g4Error.style.display = 'none';
                }
                g4Checkboxes.forEach(cb => {
                    cb.setAttribute('aria-invalid', 'false');
                    cb.removeAttribute('aria-describedby');
                });
            }

            // Validate G4 other text
            const g4OtherCheckbox = document.getElementById('g4_others');
            const g4OtherText = document.getElementById('g4_other_text');
            const g4OtherError = document.getElementById('g4_other_text_error_inline');
            if (g4OtherCheckbox && g4OtherCheckbox.checked && g4OtherText && !g4OtherText.value.trim()) {
                if (g4OtherError) {
                    g4OtherError.style.display = 'block';
                    g4OtherError.setAttribute('aria-live', 'polite');
                }
                g4OtherText.setAttribute('aria-invalid', 'true');
                g4OtherText.setAttribute('aria-describedby', 'g4_other_text_error_inline');
                isValid = false;
                errorMessages.push("Please specify details for 'Others' in G4");
            } else if (g4OtherError) {
                g4OtherError.style.display = 'none';
                if (g4OtherText) {
                    g4OtherText.setAttribute('aria-invalid', 'false');
                    g4OtherText.removeAttribute('aria-describedby');
                }
            }

            // Validate G8 details text
            const g8DetailsText = document.querySelector('textarea[name="g8_regional_differences_text"]');
            const g8DetailsError = document.getElementById('g8_details_error_inline');
            if ((g8YesSignificantly?.checked || g8YesSomewhat?.checked) && g8DetailsText && !g8DetailsText.value.trim()) {
                if (g8DetailsError) {
                    g8DetailsError.style.display = 'block';
                    g8DetailsError.setAttribute('aria-live', 'polite');
                }
                g8DetailsText.setAttribute('aria-invalid', 'true');
                g8DetailsText.setAttribute('aria-describedby', 'g8_details_error_inline');
                isValid = false;
                errorMessages.push("Please provide details for regional differences in G8");
            } else if (g8DetailsError) {
                g8DetailsError.style.display = 'none';
                if (g8DetailsText) {
                    g8DetailsText.setAttribute('aria-invalid', 'false');
                    g8DetailsText.removeAttribute('aria-describedby');
                }
            }

            if (!isValid) {
                e.preventDefault();
                const firstError = document.querySelector('.validation-error-inline[style*="display: block"]');
                if (firstError) {
                    setTimeout(() => firstError.scrollIntoView({ behavior: 'smooth', block: 'center' }), 100);
                    const firstInvalidInput = document.querySelector('[aria-invalid="true"]');
                    if (firstInvalidInput) {
                        firstInvalidInput.focus();
                    }
                }
                const errorBox = document.querySelector('.error-box');
                if (errorBox) {
                    errorBox.style.display = 'block';
                    errorBox.innerHTML = errorMessages.join('<br>');
                    errorBox.setAttribute('aria-live', 'assertive');
                }
            }
        });
    }
});