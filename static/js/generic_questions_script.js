// static/js/generic_questions_script.js
function handleBackNavigation(url) {
    window.location.href = url;
}

function toggleG4Section() {
    const g3Value = document.querySelector('input[name="g3_technical_issues"]:checked')?.value;
    const g4Section = document.getElementById('g4_section');
    const g4Inputs = document.querySelectorAll('input[name="g4_disruption"]');
    if (g4Section) {
        g4Section.style.display = ['daily', 'weekly', 'monthly', 'rarely'].includes(g3Value) ? 'block' : 'none';
        g4Inputs.forEach(input => {
            input.required = ['daily', 'weekly', 'monthly', 'rarely'].includes(g3Value);
            if (g4Section.style.display !== 'block') {
                input.checked = false;
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', function () {
    // Set checked states for G1 and G2 from generic_answers_json
    const genericAnswersInput = document.getElementById('generic_answers');
    if (genericAnswersInput) {
        try {
            const genericAnswers = JSON.parse(genericAnswersInput.value);
            
            // Set G1 checked states
            const g1Aspects = ['service_delivery', 'client_numbers', 'revenue_fees', 'compliance_burden'];
            g1Aspects.forEach(aspect => {
                const value = genericAnswers.g1 && genericAnswers.g1[aspect];
                if (value) {
                    const input = document.getElementById(`g1_${aspect}_${value}`);
                    if (input) {
                        input.checked = true;
                    }
                }
            });

            // Set G2 checked states
            const g2Aspects = ['workflow_efficiency', 'service_delivery', 'client_numbers'];
            g2Aspects.forEach(aspect => {
                const value = genericAnswers.g2 && genericAnswers.g2[aspect];
                if (value) {
                    const input = document.getElementById(`g2_${aspect}_${value}`);
                    if (input) {
                        input.checked = true;
                    }
                }
            });
        } catch (e) {
            console.error('Error parsing generic_answers_json:', e);
        }
    }

    // Error box scrolling
    const errorBox = document.getElementById('error-box');
    if (errorBox) {
        setTimeout(() => errorBox.scrollIntoView({ behavior: 'smooth', block: 'center' }), 100);
    }

    // G3: Show/hide G4 based on G3 selection
    document.querySelectorAll('input[name="g3_technical_issues"]').forEach(input => {
        input.addEventListener('change', toggleG4Section);
    });
    toggleG4Section(); // Initialize on load

    // Form validation and submission
    const form = document.getElementById('genericQuestionsForm');
    if (form) {
        form.addEventListener('submit', function (e) {
            // Don't prevent default submission - let it submit normally after validation
            let isValid = true;
            const errorMessages = [];

            // Clear previous errors
            document.querySelectorAll('.validation-error-inline').forEach(error => {
                error.style.display = 'none';
            });
            document.querySelectorAll('[aria-invalid="true"]').forEach(input => {
                input.setAttribute('aria-invalid', 'false');
                input.removeAttribute('aria-describedby');
            });

            // Validate G1 matrix
            const g1Aspects = ['service_delivery', 'client_numbers', 'revenue_fees', 'compliance_burden'];
            let g1HasError = false;
            g1Aspects.forEach(aspect => {
                const selected = document.querySelector(`input[name="g1_${aspect}"]:checked`);
                if (!selected) {
                    isValid = false;
                    g1HasError = true;
                    errorMessages.push(`Please select an option for G1 ${aspect.replace('_', ' ').title()}`);
                    
                    document.querySelectorAll(`input[name="g1_${aspect}"]`).forEach(radio => {
                        radio.setAttribute('aria-invalid', 'true');
                        radio.setAttribute('aria-describedby', 'g1_error_inline');
                    });
                }
            });
            
            // Show G1 error if any aspect is missing
            const g1ErrorDiv = document.getElementById('g1_error_inline');
            if (g1HasError && g1ErrorDiv) {
                g1ErrorDiv.style.display = 'block';
                g1ErrorDiv.setAttribute('aria-live', 'polite');
            }

            // Validate G2 matrix
            const g2Aspects = ['workflow_efficiency', 'service_delivery', 'client_numbers'];
            let g2HasError = false;
            g2Aspects.forEach(aspect => {
                const selected = document.querySelector(`input[name="g2_${aspect}"]:checked`);
                if (!selected) {
                    isValid = false;
                    g2HasError = true;
                    errorMessages.push(`Please select an option for G2 ${aspect.replace('_', ' ').title()}`);
                    
                    document.querySelectorAll(`input[name="g2_${aspect}"]`).forEach(radio => {
                        radio.setAttribute('aria-invalid', 'true');
                        radio.setAttribute('aria-describedby', 'g2_error_inline');
                    });
                }
            });
            
            // Show G2 error if any aspect is missing
            const g2ErrorDiv = document.getElementById('g2_error_inline');
            if (g2HasError && g2ErrorDiv) {
                g2ErrorDiv.style.display = 'block';
                g2ErrorDiv.setAttribute('aria-live', 'polite');
            }

            // Validate G3
            const g3Selected = document.querySelector('input[name="g3_technical_issues"]:checked');
            if (!g3Selected) {
                isValid = false;
                errorMessages.push('Please select an option for G3 Technical Issues');
                
                const g3Error = document.getElementById('g3_technical_issues_error_inline');
                if (g3Error) {
                    g3Error.style.display = 'block';
                    g3Error.setAttribute('aria-live', 'polite');
                }
                
                document.querySelectorAll('input[name="g3_technical_issues"]').forEach(radio => {
                    radio.setAttribute('aria-invalid', 'true');
                    radio.setAttribute('aria-describedby', 'g3_technical_issues_error_inline');
                });
            }

            // Validate G4 (conditional)
            const g3Value = g3Selected?.value;
            const g4Selected = document.querySelector('input[name="g4_disruption"]:checked');
            if (['daily', 'weekly', 'monthly', 'rarely'].includes(g3Value) && !g4Selected) {
                isValid = false;
                errorMessages.push('Please select an option for G4 Disruption');
                
                const g4Error = document.getElementById('g4_disruption_error_inline');
                if (g4Error) {
                    g4Error.style.display = 'block';
                    g4Error.setAttribute('aria-live', 'polite');
                }
                
                document.querySelectorAll('input[name="g4_disruption"]').forEach(radio => {
                    radio.setAttribute('aria-invalid', 'true');
                    radio.setAttribute('aria-describedby', 'g4_disruption_error_inline');
                });
            }

            // Validate G5
            const g5Selected = document.querySelector('input[name="g5_digital_literacy"]:checked');
            if (!g5Selected) {
                isValid = false;
                errorMessages.push('Please select an option for G5 Digital Literacy');
                
                const g5Error = document.getElementById('g5_digital_literacy_error_inline');
                if (g5Error) {
                    g5Error.style.display = 'block';
                    g5Error.setAttribute('aria-live', 'polite');
                }
                
                document.querySelectorAll('input[name="g5_digital_literacy"]').forEach(radio => {
                    radio.setAttribute('aria-invalid', 'true');
                    radio.setAttribute('aria-describedby', 'g5_digital_literacy_error_inline');
                });
            }

            if (!isValid) {
                // Prevent form submission and show errors
                e.preventDefault();
                
                // Show errors and scroll to first error
                const firstError = document.querySelector('.validation-error-inline[style*="display: block"]');
                if (firstError) {
                    setTimeout(() => firstError.scrollIntoView({ behavior: 'smooth', block: 'center' }), 100);
                    const firstInvalidInput = document.querySelector('[aria-invalid="true"]');
                    if (firstInvalidInput) {
                        firstInvalidInput.focus();
                    }
                }
                
                // Update error box if it exists
                if (errorBox) {
                    errorBox.style.display = 'block';
                    errorBox.querySelector('.error-message').innerHTML = errorMessages.join('<br>');
                    errorBox.setAttribute('aria-live', 'assertive');
                    setTimeout(() => errorBox.scrollIntoView({ behavior: 'smooth', block: 'center' }), 100);
                }
            }
            // If valid, let the form submit normally - no modal interruption
        });
    }
});