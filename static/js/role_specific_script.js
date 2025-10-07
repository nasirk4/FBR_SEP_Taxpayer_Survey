// static/js/role_specific_script.js
function handleBackNavigation(url) {
    window.location.href = url;
}

// Centralized error management
function showError(fieldId, message) {
    const errorElement = document.getElementById(`${fieldId}_error_inline`);
    if (errorElement) {
        errorElement.textContent = `⚠️ ${message}`;
        errorElement.style.display = 'block';
        errorElement.classList.add('highlight-error');
    }
    console.log(`Validation Error - ${fieldId}: ${message}`);
}

function hideError(fieldId) {
    const errorElement = document.getElementById(`${fieldId}_error_inline`);
    if (errorElement) {
        errorElement.style.display = 'none';
        errorElement.classList.remove('highlight-error');
    }
}

document.addEventListener('DOMContentLoaded', function () {
    console.log('Role-specific form loaded - starting initialization');

    // Error box scrolling
    const errorBox = document.getElementById('error-box');
    if (errorBox) {
        setTimeout(() => errorBox.scrollIntoView({ behavior: 'smooth', block: 'center' }), 100);
    }

    // Initialize error elements object for reference
    const errorElements = {
        lp1: document.getElementById('lp1_error_inline'),
        lp2: document.getElementById('lp2_error_inline'),
        lp2_other: document.getElementById('lp2_other_error_inline'),
        lp3: document.getElementById('lp3_error_inline'),
        lp3_other: document.getElementById('lp3_other_error_inline'),
        lp4: document.getElementById('lp4_error_inline'),
        lp5: document.getElementById('lp5_error_inline'),
        lp5_other: document.getElementById('lp5_other_error_inline'),
        lp6: document.getElementById('lp6_error_inline'),
        lp7: document.getElementById('lp7_error_inline'),
        lp8: document.getElementById('lp8_error_inline'),
        lp9: document.getElementById('lp9_error_inline'),
        lp10: document.getElementById('lp10_error_inline'),
        lp11: document.getElementById('lp11_error_inline'),
        lp12: document.getElementById('lp12_error_inline'),
        lp13: document.getElementById('lp13_error_inline'),
        ca1: document.getElementById('ca1_error_inline'),
        ca1a: document.getElementById('ca1a_error_inline'),
        ca2: document.getElementById('ca2_error_inline'),
        ca3: document.getElementById('ca3_error_inline'),
        ca3_other: document.getElementById('ca3_other_error_inline'),
        ca4: document.getElementById('ca4_error_inline'),
        ca5: document.getElementById('ca5_error_inline'),
        ca6: document.getElementById('ca6_error_inline'),
        ca7: document.getElementById('ca7_error_inline'),
        ca8: document.getElementById('ca8_error_inline'),
        ca9: document.getElementById('ca9_error_inline'),
        ca9_other: document.getElementById('ca9_other_error_inline')
    };

    // --- Legal Practitioner Logic ---

    // LP1: Toggle LP2 visibility
    function toggleLP2Section() {
        const lp1Radios = document.querySelectorAll('input[name="lp1_technical_issues"]:checked');
        const lp2Section = document.getElementById('lp2_section');
        const showLP2 = lp1Radios.length > 0 && ['very_frequently', 'frequently'].includes(lp1Radios[0].value);

        if (lp2Section) {
            lp2Section.style.display = showLP2 ? 'block' : 'none';
            if (!showLP2) {
                document.querySelectorAll('input[name="lp2_common_problems"]').forEach(cb => cb.checked = false);
                const lp2OtherText = document.getElementById('lp2_other_text');
                if (lp2OtherText) lp2OtherText.value = '';
                hideError('lp2');
                hideError('lp2_other');
            }
        }
    }

    // LP2 Other field toggle
    window.toggleLP2Other = function() {
        const checkbox = document.getElementById('lp2_other');
        const specifyDiv = document.getElementById('lp2_other_specify');
        const textarea = document.getElementById('lp2_other_text');

        if (checkbox && checkbox.checked) {
            specifyDiv.style.display = 'block';
        } else {
            specifyDiv.style.display = 'none';
            if (textarea) textarea.value = '';
            hideError('lp2_other');
        }
    };

    // LP3 Selection counter
    function setupLP3Counter() {
        const checkboxes = document.querySelectorAll('input[name="lp3_improvement_areas"]');
        const counter = document.getElementById('lp3_counter');

        function updateLP3Counter() {
            const selected = document.querySelectorAll('input[name="lp3_improvement_areas"]:checked');
            const maxSelections = 3;

            if (counter) {
                counter.textContent = selected.length;
                counter.style.color = selected.length >= maxSelections ? '#dc3545' : '#666';
            }

            checkboxes.forEach(cb => {
                if (selected.length >= maxSelections && !cb.checked) {
                    cb.disabled = true;
                    cb.parentElement.classList.add('disabled-input');
                } else {
                    cb.disabled = false;
                    cb.parentElement.classList.remove('disabled-input');
                }
            });
        }

        if (checkboxes.length > 0) {
            checkboxes.forEach(checkbox => {
                checkbox.addEventListener('change', function(e) {
                    updateLP3Counter();
                    if (e.target.value === 'other') toggleLP3Other();
                });
            });
            updateLP3Counter();
        }
    }

    window.toggleLP3Other = function() {
        const checkbox = document.getElementById('lp3_other');
        const specifyDiv = document.getElementById('lp3_other_specify');
        const textarea = document.getElementById('lp3_other_text');

        if (checkbox && checkbox.checked) {
            specifyDiv.style.display = 'block';
        } else {
            specifyDiv.style.display = 'none';
            if (textarea) textarea.value = '';
            hideError('lp3_other');
        }
    };

    // LP5 Selection counter
    function setupLP5Counter() {
        const checkboxes = document.querySelectorAll('input[name="lp5_representation_challenges"]');
        const counter = document.getElementById('lp5_counter');

        function updateLP5Counter() {
            const selected = document.querySelectorAll('input[name="lp5_representation_challenges"]:checked');
            const maxSelections = 3;

            if (counter) {
                counter.textContent = selected.length;
                counter.style.color = selected.length >= maxSelections ? '#dc3545' : '#666';
            }

            checkboxes.forEach(cb => {
                if (selected.length >= maxSelections && !cb.checked) {
                    cb.disabled = true;
                    cb.parentElement.classList.add('disabled-input');
                } else {
                    cb.disabled = false;
                    cb.parentElement.classList.remove('disabled-input');
                }
            });
        }

        if (checkboxes.length > 0) {
            checkboxes.forEach(checkbox => {
                checkbox.addEventListener('change', function(e) {
                    updateLP5Counter();
                    if (e.target.value === 'other') toggleLP5Other();
                });
            });
            updateLP5Counter();
        }
    }

    window.toggleLP5Other = function() {
        const checkbox = document.getElementById('lp5_other');
        const specifyDiv = document.getElementById('lp5_other_specify');
        const textarea = document.getElementById('lp5_other_text');

        if (checkbox && checkbox.checked) {
            specifyDiv.style.display = 'block';
        } else {
            specifyDiv.style.display = 'none';
            if (textarea) textarea.value = '';
            hideError('lp5_other');
        }
    };

    // --- Customs Agent Logic ---

    // CA1: Toggle CA1a visibility
    function toggleCA1a() {
        const selectedValue = document.querySelector('input[name="ca1_training_received"]:checked');
        const ca1aSection = document.getElementById('ca1a_section');
        const ca1aVisibleInput = document.getElementById('ca1a_visible');
        const showCA1a = selectedValue && selectedValue.value !== 'no_training';

        if (ca1aSection) {
            ca1aSection.style.display = showCA1a ? 'block' : 'none';
            ca1aVisibleInput.value = showCA1a ? '1' : '0';
            if (!showCA1a) {
                document.querySelectorAll('input[name="ca1a_training_usefulness"]').forEach(radio => radio.checked = false);
                hideError('ca1a');
            }
        }
    }

    // FIXED: CA1a validation - only validate when section is visible and required
    function validateCA1a() {
        const ca1aRadios = document.querySelectorAll('input[name="ca1a_training_usefulness"]:checked');
        const ca1aSection = document.getElementById('ca1a_section');
        const ca1Training = document.querySelector('input[name="ca1_training_received"]:checked');
        
        // Only validate if CA1a section is visible AND user received training
        const shouldValidate = ca1aSection && 
                              ca1aSection.style.display === 'block' && 
                              ca1Training && 
                              ca1Training.value !== 'no_training';

        if (shouldValidate && ca1aRadios.length === 0) {
            showError('ca1a', 'Please select an option for CA1a.');
            return false;
        } else {
            hideError('ca1a');
            return true;
        }
    }

    // CA3 Selection counter
    function setupCA3Counter() {
        const checkboxes = document.querySelectorAll('input[name="ca3_procedure_challenges"]');
        const counter = document.getElementById('ca3_counter');

        function updateCA3Counter() {
            const selected = document.querySelectorAll('input[name="ca3_procedure_challenges"]:checked');
            const maxSelections = 3;
            const noChallengesChecked = document.getElementById('ca3_no_challenges')?.checked;

            if (counter) {
                counter.textContent = selected.length;
                counter.style.color = (selected.length >= maxSelections && !noChallengesChecked) ? '#dc3545' : '#666';
            }

            checkboxes.forEach(cb => {
                if (selected.length >= maxSelections && !cb.checked && cb.value !== 'no_challenges' && !noChallengesChecked) {
                    cb.disabled = true;
                    cb.parentElement.classList.add('disabled-input');
                } else {
                    cb.disabled = false;
                    cb.parentElement.classList.remove('disabled-input');
                }
            });

            updateCA3State();
        }

        if (checkboxes.length > 0) {
            checkboxes.forEach(checkbox => {
                checkbox.addEventListener('change', function(e) {
                    updateCA3Counter();
                    if (e.target.value === 'other') toggleCA3Other();
                });
            });
            updateCA3Counter();
        }
    }

    window.toggleCA3Other = function() {
        const checkbox = document.getElementById('ca3_other');
        const specifyDiv = document.getElementById('ca3_other_specify');
        const textarea = document.getElementById('ca3_other_text');

        if (checkbox && checkbox.checked) {
            specifyDiv.style.display = 'block';
        } else {
            specifyDiv.style.display = 'none';
            if (textarea) textarea.value = '';
            hideError('ca3_other');
        }
        updateCA3State();
    };

    window.updateCA3State = function() {
        const checkboxes = document.querySelectorAll('input[name="ca3_procedure_challenges"]:checked');
        const noChallenges = document.getElementById('ca3_no_challenges');
        const otherCheckbox = document.getElementById('ca3_other');
        const textarea = document.getElementById('ca3_other_text');
        
        const textEntered = textarea && textarea.value.trim().length > 0;
        const hasSelections = checkboxes.length > 0;

        // Clear errors when conditions are fixed
        if (noChallenges && noChallenges.checked && checkboxes.length === 1) {
            hideError('ca3');
        }
        if (otherCheckbox && otherCheckbox.checked && textEntered) {
            hideError('ca3_other');
        }
        
        // Disable other checkboxes when "No challenges" is selected
        const allCheckboxes = document.querySelectorAll('input[name="ca3_procedure_challenges"]');
        if (noChallenges && noChallenges.checked) {
            allCheckboxes.forEach(cb => {
                if (cb.value !== 'no_challenges') {
                    cb.disabled = true;
                    cb.parentElement.classList.add('disabled-input');
                }
            });
        } else {
            allCheckboxes.forEach(cb => {
                cb.disabled = false;
                cb.parentElement.classList.remove('disabled-input');
            });
        }
    };

    // CA9 Other field toggle
    window.toggleCA9Other = function() {
        const checkbox = document.getElementById('ca9_other');
        const specifyDiv = document.getElementById('ca9_other_specify');
        const textarea = document.getElementById('ca9_other_text');

        if (checkbox && checkbox.checked) {
            specifyDiv.style.display = 'block';
        } else {
            specifyDiv.style.display = 'none';
            if (textarea) textarea.value = '';
            hideError('ca9_other');
        }
    };

    // LP4 Validation
    function validateLP4() {
        const checkboxes = document.querySelectorAll('input[name*="lp4_"][type="checkbox"]');
        const otherProcedure = document.getElementById('lp4_other_procedure');
        const otherSales = document.getElementById('lp4_other_sales');
        const otherIncome = document.getElementById('lp4_other_income');

        const hasSelection = Array.from(checkboxes).some(cb => cb.checked);
        const otherTextEntered = otherProcedure && otherProcedure.value.trim().length > 0;
        const otherChecked = (otherSales && otherSales.checked) || (otherIncome && otherIncome.checked);

        if (!hasSelection && (!otherTextEntered || !otherChecked)) {
            showError('lp4', 'Please select at least one procedure or specify an "Other" procedure with a selection.');
            return false;
        } else if (otherChecked && !otherTextEntered) {
            showError('lp4', 'Please specify the "Other" procedure name.');
            return false;
        } else {
            hideError('lp4');
            return true;
        }
    }

    // PHASE 1 FIX: Direct field validation without fake events
    function validateAllFields() {
        console.log('Starting comprehensive form validation...');
        let isValid = true;

        // Only validate Legal Practitioner section if it exists
        const legalSectionExists = document.querySelector('.section h2')?.textContent.includes('Legal Practitioner');
        if (legalSectionExists) {
            console.log('Validating Legal Practitioner questions...');
            isValid = validateLegalSection() && isValid;
        }

        // Only validate Customs Agent section if it exists  
        const customsSectionExists = document.querySelector('.section h2')?.textContent.includes('Customs Agent');
        if (customsSectionExists) {
            console.log('Validating Customs Agent questions...');
            isValid = validateCustomsSection() && isValid;
        }

        console.log(`Form validation result: ${isValid ? 'VALID' : 'INVALID'}`);
        return isValid;
    }

    function validateLegalSection() {
        let isValid = true;

        // Required radio groups for Legal Practitioner
        const requiredLegalRadios = [
            { name: 'lp1_technical_issues', field: 'lp1' },
            { name: 'lp6_filing_efficiency', field: 'lp6' },
            { name: 'lp7_case_tracking', field: 'lp7' },
            { name: 'lp8_notice_communication', field: 'lp8' },
            { name: 'lp9_law_accessibility', field: 'lp9' },
            { name: 'lp10_law_change_impact', field: 'lp10' },
            { name: 'lp11_adr_effectiveness', field: 'lp11' },
            { name: 'lp12_dispute_transparency', field: 'lp12' },
            { name: 'lp13_overall_satisfaction', field: 'lp13' }
        ];

        requiredLegalRadios.forEach(radio => {
            const selected = document.querySelector(`input[name="${radio.name}"]:checked`);
            if (!selected) {
                showError(radio.field, `Please select an option for ${radio.name.replace('_', ' ').toUpperCase()}.`);
                isValid = false;
            } else {
                hideError(radio.field);
            }
        });

        // LP2: Conditional validation
        const lp1Selected = document.querySelector('input[name="lp1_technical_issues"]:checked');
        const lp2Section = document.getElementById('lp2_section');
        if (lp1Selected && lp2Section && lp2Section.style.display === 'block') {
            const lp2Checkboxes = document.querySelectorAll('input[name="lp2_common_problems"]:checked');
            if (lp2Checkboxes.length === 0) {
                showError('lp2', 'Please select at least one technical issue for LP2.');
                isValid = false;
            } else {
                hideError('lp2');
                // Check "Other" text if needed
                if (document.getElementById('lp2_other')?.checked) {
                    const otherText = document.getElementById('lp2_other_text')?.value.trim();
                    if (!otherText) {
                        showError('lp2_other', 'Please specify details for the "Other" option in LP2.');
                        isValid = false;
                    } else {
                        hideError('lp2_other');
                    }
                }
            }
        }

        // LP3: Improvement areas
        const lp3Checkboxes = document.querySelectorAll('input[name="lp3_improvement_areas"]:checked');
        if (lp3Checkboxes.length === 0) {
            showError('lp3', 'Please select at least one improvement area for LP3.');
            isValid = false;
        } else if (lp3Checkboxes.length > 3) {
            showError('lp3', 'Please select no more than 3 options for LP3.');
            isValid = false;
        } else {
            hideError('lp3');
            // Check "Other" text if needed
            if (document.getElementById('lp3_other')?.checked) {
                const otherText = document.getElementById('lp3_other_text')?.value.trim();
                if (!otherText) {
                    showError('lp3_other', 'Please specify details for the "Other" option in LP3.');
                    isValid = false;
                } else {
                    hideError('lp3_other');
                }
            }
        }

        // LP4: Procedures matrix
        if (!validateLP4()) {
            isValid = false;
        }

        // LP5: Representation challenges
        const lp5Checkboxes = document.querySelectorAll('input[name="lp5_representation_challenges"]:checked');
        if (lp5Checkboxes.length === 0) {
            showError('lp5', 'Please select at least one challenge for LP5.');
            isValid = false;
        } else if (lp5Checkboxes.length > 3) {
            showError('lp5', 'Please select no more than 3 options for LP5.');
            isValid = false;
        } else {
            hideError('lp5');
            // Check "Other" text if needed
            if (document.getElementById('lp5_other')?.checked) {
                const otherText = document.getElementById('lp5_other_text')?.value.trim();
                if (!otherText) {
                    showError('lp5_other', 'Please specify details for the "Other" option in LP5.');
                    isValid = false;
                } else {
                    hideError('lp5_other');
                }
            }
        }

        return isValid;
    }

    function validateCustomsSection() {
        let isValid = true;

        // Required radio groups for Customs Agent
        const requiredCustomsRadios = [
            { name: 'ca1_training_received', field: 'ca1' },
            { name: 'ca2_psw_weboc_integration', field: 'ca2' },
            { name: 'ca4_duty_assessment', field: 'ca4' },
            { name: 'ca5_psw_vs_weboc', field: 'ca5' },
            { name: 'ca6_cargo_efficiency', field: 'ca6' },
            { name: 'ca7_system_reliability', field: 'ca7' },
            { name: 'ca8_policy_impact', field: 'ca8' }
        ];

        requiredCustomsRadios.forEach(radio => {
            const selected = document.querySelector(`input[name="${radio.name}"]:checked`);
            if (!selected) {
                showError(radio.field, `Please select an option for ${radio.name.replace('_', ' ').toUpperCase()}.`);
                isValid = false;
            } else {
                hideError(radio.field);
            }
        });

        // CA1a: Conditional validation
        if (!validateCA1a()) {
            isValid = false;
        }

        // CA3: Procedure challenges
        const ca3Checkboxes = document.querySelectorAll('input[name="ca3_procedure_challenges"]:checked');
        const noChallengesChecked = document.getElementById('ca3_no_challenges')?.checked;
        
        if (ca3Checkboxes.length === 0) {
            showError('ca3', 'Please select at least one option for CA3.');
            isValid = false;
        } else if (noChallengesChecked && ca3Checkboxes.length > 1) {
            showError('ca3', 'If you select "No significant challenges", you cannot select other options.');
            isValid = false;
        } else if (ca3Checkboxes.length > 3 && !noChallengesChecked) {
            showError('ca3', 'Please select no more than 3 options for CA3.');
            isValid = false;
        } else {
            hideError('ca3');
        }
        
        // CA3 "Other" text validation
        if (document.getElementById('ca3_other')?.checked) {
            const otherText = document.getElementById('ca3_other_text')?.value.trim();
            if (!otherText) {
                showError('ca3_other', 'Please specify details for the "Other" option in CA3.');
                isValid = false;
            } else {
                hideError('ca3_other');
            }
        }

        // CA9: Operational challenges
        const ca9Checkboxes = document.querySelectorAll('input[name="ca9_operational_challenges"]:checked');
        if (ca9Checkboxes.length === 0) {
            showError('ca9', 'Please select at least one operational challenge for CA9.');
            isValid = false;
        } else {
            hideError('ca9');
            // Check "Other" text if needed
            if (document.getElementById('ca9_other')?.checked) {
                const otherText = document.getElementById('ca9_other_text')?.value.trim();
                if (!otherText) {
                    showError('ca9_other', 'Please specify details for the "Other" option in CA9.');
                    isValid = false;
                } else {
                    hideError('ca9_other');
                }
            }
        }

        return isValid;
    }

    // Clear validation errors when user interacts
    function clearValidationErrorsOnInteraction() {
        // Clear radio errors
        const allRadios = document.querySelectorAll('input[type="radio"]');
        allRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                const fieldName = this.name.split('_')[0];
                hideError(fieldName);
            });
        });

        // Clear checkbox errors  
        const allCheckboxes = document.querySelectorAll('input[type="checkbox"]');
        allCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                const fieldName = this.name.split('_')[0];
                hideError(fieldName);
                
                // Clear "Other" errors when checkbox is unchecked
                if (this.value === 'other' && !this.checked) {
                    hideError(`${fieldName}_other`);
                }
            });
        });

        // Clear textarea errors when typing
        const allTextareas = document.querySelectorAll('textarea');
        allTextareas.forEach(textarea => {
            textarea.addEventListener('input', function() {
                // Find associated error field
                const fieldId = this.id.replace('_text', '');
                if (fieldId && this.value.trim().length > 0) {
                    hideError(fieldId);
                }
            });
        });
    }

    // Initialize conditional sections based on current form state
    function initializeConditionalSections() {
        console.log('Initializing conditional sections...');

        // Set up event listeners for main conditional triggers
        const lp1Radios = document.querySelectorAll('input[name="lp1_technical_issues"]');
        lp1Radios.forEach(radio => {
            radio.addEventListener('change', toggleLP2Section);
        });

        const ca1Radios = document.querySelectorAll('input[name="ca1_training_received"]');
        ca1Radios.forEach(radio => {
            radio.addEventListener('change', toggleCA1a);
        });

        // Initialize sections based on current selections
        toggleLP2Section();
        toggleCA1a();
        
        // Initialize "Other" sections
        if (document.getElementById('lp2_other')?.checked) toggleLP2Other();
        if (document.getElementById('lp3_other')?.checked) toggleLP3Other();
        if (document.getElementById('lp5_other')?.checked) toggleLP5Other();
        if (document.getElementById('ca3_other')?.checked) toggleCA3Other();
        if (document.getElementById('ca9_other')?.checked) toggleCA9Other();

        // Initialize counters
        setupLP3Counter();
        setupLP5Counter();
        setupCA3Counter();

        // Initialize error clearing
        clearValidationErrorsOnInteraction();

        console.log('Conditional sections initialized successfully');
    }

    // PHASE 1 FIX: Simplified form submission handler
    document.getElementById('roleSpecificForm').addEventListener('submit', function (e) {
        console.log('Form submission initiated...');
        
        const isValid = validateAllFields();
        
        if (!isValid) {
            console.log('Form validation failed - preventing submission');
            e.preventDefault();
            
            // Scroll to first error
            const firstError = document.querySelector('.validation-error-inline[style*="display: block"]');
            if (firstError) {
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        } else {
            console.log('Form validation passed - allowing submission to cross-system-perspectives');
        }
    });

    // Real-time validation with event delegation
    const form = document.getElementById('roleSpecificForm');
    form.addEventListener('change', function(e) {
        // Real-time validation for better UX
        if (e.target.type === 'radio' || e.target.type === 'checkbox') {
            validateAllFields();
        }
    });

    // Initialize everything when page loads
    initializeConditionalSections();
    console.log('Role-specific form initialization complete');
});