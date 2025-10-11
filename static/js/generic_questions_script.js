// static/js/generic_questions_script.js
function handleBackNavigation(url) {
    window.location.href = url;
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
                const value = genericAnswers.g1[aspect];
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
                const value = genericAnswers.g2[aspect];
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

    document.querySelectorAll('input[name="g3_technical_issues"]').forEach(input => {
        input.addEventListener('change', toggleG4Section);
    });
    toggleG4Section(); // Initialize on load

    // Detect Bootstrap version
    const bootstrapVersion = typeof bootstrap !== 'undefined' && bootstrap.Modal && bootstrap.Modal.VERSION ? bootstrap.Modal.VERSION : '4';
    const isBootstrap5 = bootstrapVersion.startsWith('5');

    // Create Bootstrap confirmation modal
    const modalHtml = isBootstrap5 ? `
        <div class="modal fade" id="confirmSubmitModal" tabindex="-1" aria-labelledby="confirmSubmitModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="confirmSubmitModalLabel">Confirm Submission</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        Are you sure you want to submit your responses?
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-back" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-next" id="confirmSubmitBtn">Submit</button>
                    </div>
                </div>
            </div>
        </div>
    ` : `
        <div class="modal fade" id="confirmSubmitModal" tabindex="-1" role="dialog" aria-labelledby="confirmSubmitModalLabel" aria-hidden="true">
            <div class="modal-dialog" role="document">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="confirmSubmitModalLabel">Confirm Submission</h5>
                        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                    <div class="modal-body">
                        Are you sure you want to submit your responses?
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-back" data-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-next" id="confirmSubmitBtn">Submit</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', modalHtml);

    // Form validation
    const form = document.getElementById('genericQuestionsForm');
    if (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault(); // Prevent default submission
            let isValid = true;
            const errorMessages = [];

            // Validate G1 matrix
            const g1Aspects = ['service_delivery', 'client_numbers', 'revenue_fees', 'compliance_burden'];
            g1Aspects.forEach(aspect => {
                const selected = document.querySelector(`input[name="g1_${aspect}"]:checked`);
                const errorDiv = document.getElementById('g1_error_inline');
                if (!selected) {
                    if (errorDiv) {
                        errorDiv.style.display = 'block';
                        errorDiv.setAttribute('aria-live', 'polite');
                    }
                    document.querySelectorAll(`input[name="g1_${aspect}"]`).forEach(radio => {
                        radio.setAttribute('aria-invalid', 'true');
                        radio.setAttribute('aria-describedby', 'g1_error_inline');
                    });
                    isValid = false;
                    errorMessages.push(`Please select an option for G1 ${aspect.replace('_', ' ').title()}`);
                } else {
                    if (errorDiv) {
                        errorDiv.style.display = 'none';
                    }
                    document.querySelectorAll(`input[name="g1_${aspect}"]`).forEach(radio => {
                        radio.setAttribute('aria-invalid', 'false');
                        radio.removeAttribute('aria-describedby');
                    });
                }
            });

            // Validate G2 matrix
            const g2Aspects = ['workflow_efficiency', 'service_delivery', 'client_numbers'];
            g2Aspects.forEach(aspect => {
                const selected = document.querySelector(`input[name="g2_${aspect}"]:checked`);
                const errorDiv = document.getElementById('g2_error_inline');
                if (!selected) {
                    if (errorDiv) {
                        errorDiv.style.display = 'block';
                        errorDiv.setAttribute('aria-live', 'polite');
                    }
                    document.querySelectorAll(`input[name="g2_${aspect}"]`).forEach(radio => {
                        radio.setAttribute('aria-invalid', 'true');
                        radio.setAttribute('aria-describedby', 'g2_error_inline');
                    });
                    isValid = false;
                    errorMessages.push(`Please select an option for G2 ${aspect.replace('_', ' ').title()}`);
                } else {
                    if (errorDiv) {
                        errorDiv.style.display = 'none';
                    }
                    document.querySelectorAll(`input[name="g2_${aspect}"]`).forEach(radio => {
                        radio.setAttribute('aria-invalid', 'false');
                        radio.removeAttribute('aria-describedby');
                    });
                }
            });

            // Validate G3
            const g3Selected = document.querySelector('input[name="g3_technical_issues"]:checked');
            const g3Error = document.getElementById('g3_technical_issues_error_inline');
            if (!g3Selected) {
                if (g3Error) {
                    g3Error.style.display = 'block';
                    g3Error.setAttribute('aria-live', 'polite');
                }
                document.querySelectorAll('input[name="g3_technical_issues"]').forEach(radio => {
                    radio.setAttribute('aria-invalid', 'true');
                    radio.setAttribute('aria-describedby', 'g3_technical_issues_error_inline');
                });
                isValid = false;
                errorMessages.push('Please select an option for G3 Technical Issues');
            } else {
                if (g3Error) {
                    g3Error.style.display = 'none';
                }
                document.querySelectorAll('input[name="g3_technical_issues"]').forEach(radio => {
                    radio.setAttribute('aria-invalid', 'false');
                    radio.removeAttribute('aria-describedby');
                });
            }

            // Validate G4 (conditional)
            const g3Value = g3Selected?.value;
            const g4Selected = document.querySelector('input[name="g4_disruption"]:checked');
            const g4Error = document.getElementById('g4_disruption_error_inline');
            if (['daily', 'weekly', 'monthly', 'rarely'].includes(g3Value) && !g4Selected) {
                if (g4Error) {
                    g4Error.style.display = 'block';
                    g4Error.setAttribute('aria-live', 'polite');
                }
                document.querySelectorAll('input[name="g4_disruption"]').forEach(radio => {
                    radio.setAttribute('aria-invalid', 'true');
                    radio.setAttribute('aria-describedby', 'g4_disruption_error_inline');
                });
                isValid = false;
                errorMessages.push('Please select an option for G4 Disruption');
            } else {
                if (g4Error) {
                    g4Error.style.display = 'none';
                }
                document.querySelectorAll('input[name="g4_disruption"]').forEach(radio => {
                    radio.setAttribute('aria-invalid', 'false');
                    radio.removeAttribute('aria-describedby');
                });
            }

            // Validate G5
            const g5Selected = document.querySelector('input[name="g5_digital_literacy"]:checked');
            const g5Error = document.getElementById('g5_digital_literacy_error_inline');
            if (!g5Selected) {
                if (g5Error) {
                    g5Error.style.display = 'block';
                    g5Error.setAttribute('aria-live', 'polite');
                }
                document.querySelectorAll('input[name="g5_digital_literacy"]').forEach(radio => {
                    radio.setAttribute('aria-invalid', 'true');
                    radio.setAttribute('aria-describedby', 'g5_digital_literacy_error_inline');
                });
                isValid = false;
                errorMessages.push('Please select an option for G5 Digital Literacy');
            } else {
                if (g5Error) {
                    g5Error.style.display = 'none';
                }
                document.querySelectorAll('input[name="g5_digital_literacy"]').forEach(radio => {
                    radio.setAttribute('aria-invalid', 'false');
                    radio.removeAttribute('aria-describedby');
                });
            }

            if (!isValid) {
                const firstError = document.querySelector('.validation-error-inline[style*="display: block"]');
                if (firstError) {
                    setTimeout(() => firstError.scrollIntoView({ behavior: 'smooth', block: 'center' }), 100);
                    const firstInvalidInput = document.querySelector('[aria-invalid="true"]');
                    if (firstInvalidInput) {
                        firstInvalidInput.focus();
                    }
                }
                if (errorBox) {
                    errorBox.style.display = 'block';
                    errorBox.querySelector('.error-message').innerHTML = errorMessages.join('<br>');
                    errorBox.setAttribute('aria-live', 'assertive');
                }
            } else {
                // Show Bootstrap modal
                const modal = document.getElementById('confirmSubmitModal');
                const bootstrapModal = new bootstrap.Modal(modal);
                bootstrapModal.show();

                // Handle modal submit
                document.getElementById('confirmSubmitBtn').onclick = function () {
                    bootstrapModal.hide();
                    form.submit(); // Proceed with form submission
                };
            }
        });
    }
});