// static/js/final_remarks_script.js
document.addEventListener('DOMContentLoaded', function () {
    // Configuration - get from data attributes
    const form = document.getElementById('finalForm');
    if (!form) {
        console.error('finalForm not found');
        return;
    }

    const config = {
        saveUrl: form.dataset.saveUrl || '/final-remarks/',
        confirmationUrl: form.dataset.confirmationUrl || '/confirmation/',
        backUrl: form.dataset.backUrl || '/cross-system-perspectives/',
        csrfSelector: '[name=csrfmiddlewaretoken]'
    };

    console.log('Final Remarks Config:', config);

    /* Debounce with cancel support */
    function debounce(func, wait) {
        let timeout;
        const debounced = function (...args) {
            const ctx = this;
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(ctx, args), wait);
        };
        debounced.cancel = () => clearTimeout(timeout);
        return debounced;
    }

    /* Utility: create or return existing error box */
    function createErrorBox() {
        let errorBox = document.getElementById('error-box');
        if (errorBox) return errorBox;

        const section = document.querySelector('.section') || document.body;
        errorBox = document.createElement('div');
        errorBox.className = 'error-box';
        errorBox.id = 'error-box';
        errorBox.style.display = 'none';
        section.prepend(errorBox);
        return errorBox;
    }

    /* Read CSRF token safely */
    function getCsrfToken() {
        const tokenEl = document.querySelector(config.csrfSelector);
        return tokenEl ? tokenEl.value : null;
    }

    /* Show saving indicator */
    function showSaveIndicator() {
        let indicator = document.querySelector('.save-indicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.className = 'save-indicator';
            indicator.style.cssText = 'position: fixed; top: 10px; right: 10px; padding: 10px; background: #28a745; color: white; border-radius: 5px; z-index: 1000; font-size: 14px;';
            document.body.appendChild(indicator);
        }
        indicator.textContent = 'Saving...';
        indicator.style.display = 'block';
        return indicator;
    }

    /* Hide saving indicator */
    function hideSaveIndicator(indicator, success = true) {
        if (indicator) {
            indicator.textContent = success ? 'Saved!' : 'Save Failed';
            indicator.style.background = success ? '#28a745' : '#dc3545';
            setTimeout(() => {
                if (indicator.parentNode) {
                    indicator.parentNode.removeChild(indicator);
                }
            }, 2000);
        }
    }

    /* Save draft with retries */
    async function saveDraft(retries = 2, delay = 1000) {
        const finalRemarksEl = document.getElementById('final_remarks');
        const surveyFeedbackEl = document.getElementById('survey_feedback'); // NEW
        
        const finalRemarks = finalRemarksEl ? finalRemarksEl.value.trim() : '';
        const surveyFeedback = surveyFeedbackEl ? surveyFeedbackEl.value.trim() : ''; // NEW

        // Only proceed if at least one field has content
        if (!finalRemarks && !surveyFeedback) {
            console.log('No remarks or feedback to save');
            return true;
        }

        const formData = new FormData();
        formData.append('final_remarks', finalRemarks);
        formData.append('survey_feedback', surveyFeedback); // NEW: Append feedback
        formData.append('save_draft', 'true');
        formData.append('draft_save_attempt', 'true');

        // Store in localStorage as backup
        try {
            localStorage.setItem('final_remarks_backup', finalRemarks);
            localStorage.setItem('survey_feedback_backup', surveyFeedback); // NEW: Backup feedback
            console.log('Backed up to localStorage. Final Remarks:', finalRemarks.length, 'Feedback:', surveyFeedback.length);
        } catch (e) {
            console.warn('Cannot access localStorage:', e);
        }

        const saveIndicator = showSaveIndicator();
        const csrf = getCsrfToken();
        
        if (!csrf) {
            console.error('CSRF token not found');
            hideSaveIndicator(saveIndicator, false);
            return false;
        }

        try {
            const response = await fetch(config.saveUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrf,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.status === 'success') {
                console.log('Draft saved successfully');
                hideSaveIndicator(saveIndicator, true);
                
                // Clean up backup on successful save
                try {
                    localStorage.removeItem('final_remarks_backup');
                    localStorage.removeItem('survey_feedback_backup'); // NEW: Clear feedback backup
                    console.log('Cleared localStorage backup after successful save');
                } catch (e) {}
                
                return true;
            } else {
                throw new Error(data.message || 'Save failed');
            }
        } catch (error) {
            console.error('Save error:', error);
            
            if (retries > 0) {
                console.log(`Retrying save... (${retries} attempts left)`);
                await new Promise(resolve => setTimeout(resolve, delay));
                return saveDraft(retries - 1, delay * 2);
            }
            
            hideSaveIndicator(saveIndicator, false);
            return false;
        }
    }

    /* Back navigation handler */
    async function handleBackNavigation() {
        console.log('Back navigation triggered');
        
        const success = await saveDraft();
        
        if (success) {
            console.log('Navigation to:', config.backUrl);
            window.location.href = config.backUrl;
        } else {
            const proceed = confirm('Failed to save draft. Your data is stored locally. Click OK to proceed anyway, or Cancel to stay on this page.');
            if (proceed) {
                window.location.href = config.backUrl;
            }
        }
    }

    /* Confirm submission */
    function confirmSubmission() {
        console.log('Confirm submission triggered');
        
        const finalRemarksEl = document.getElementById('final_remarks');
        const errorBox = createErrorBox();

        // Only final_remarks is required
        if (!finalRemarksEl || !finalRemarksEl.value.trim()) {
            errorBox.style.display = 'block';
            errorBox.innerHTML = '<div class="error-icon">⚠️</div><div class="error-message">Please provide your final remarks before submitting.</div>';
            errorBox.setAttribute('aria-live', 'assertive');
            if (finalRemarksEl) finalRemarksEl.focus();
            errorBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
            return;
        }

        errorBox.style.display = 'none';
        
        const modal = document.getElementById('confirmationModal');
        if (modal) {
            modal.style.display = 'flex';
            console.log('Modal displayed');
        } else {
            console.error('Confirmation modal not found');
        }
    }

    /* Close confirmation modal */
    function closeModal() {
        const modal = document.getElementById('confirmationModal');
        if (modal) {
            modal.style.display = 'none';
            console.log('Modal closed');
        }
    }

    /* Review answers - closes modal without submitting */
    function reviewAnswers() {
        console.log('User wants to review answers');
        closeModal();
        
        // Scroll to top of form for better UX
        const form = document.getElementById('finalForm');
        if (form) {
            form.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
        
        console.log('All data preserved for review');
    }

    /* Submit form */
    async function submitForm() {
        console.log('Form submission triggered');
        
        const form = document.getElementById('finalForm');
        const submitBtn = document.querySelector('.modal-content .btn-submit');
        
        if (!form) {
            console.error('Form not found');
            return;
        }

        // Save current button state
        let originalText = 'Yes, Submit Survey';
        let originalDisabled = false;
        
        if (submitBtn) {
            originalText = submitBtn.innerHTML;
            originalDisabled = submitBtn.disabled;
            submitBtn.innerHTML = 'Submitting...';
            submitBtn.disabled = true;
        }

        // Note: FormData(form) collects all fields, including survey_feedback.
        const formData = new FormData(form);
        formData.append('confirm_submit', 'true');

        const csrf = getCsrfToken();
        if (!csrf) {
            console.error('CSRF token not found');
            if (submitBtn) {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = originalDisabled;
            }
            closeModal();
            return;
        }

        try {
            const response = await fetch(config.saveUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrf,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('Submission response:', data);

            if (data.status === 'success') {
                console.log('Submission successful, redirecting to:', config.confirmationUrl);
                window.location.href = config.confirmationUrl;
            } else {
                throw new Error(data.message || 'Submission failed');
            }
        } catch (error) {
            console.error('Submission error:', error);
            
            if (submitBtn) {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = originalDisabled;
            }
            
            closeModal();
            
            const errorBox = createErrorBox();
            errorBox.style.display = 'block';
            errorBox.innerHTML = '<div class="error-icon">⚠️</div><div class="error-message">Failed to submit survey. Please try again.</div>';
            errorBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    /* Enhanced localStorage sync with conflict resolution */
    function syncLocalStorageToSession() {
        const finalRemarksEl = document.getElementById('final_remarks');
        const surveyFeedbackEl = document.getElementById('survey_feedback'); // NEW
        
        if (!finalRemarksEl || !surveyFeedbackEl) return;

        try {
            const backupRemarks = localStorage.getItem('final_remarks_backup');
            const sessionRemarks = finalRemarksEl.value.trim();
            const backupFeedback = localStorage.getItem('survey_feedback_backup'); // NEW
            const sessionFeedback = surveyFeedbackEl.value.trim(); // NEW
            
            console.log('Sync check - Backup Remarks:', !!backupRemarks, 'Session Remarks:', !!sessionRemarks);
            console.log('Sync check - Backup Feedback:', !!backupFeedback, 'Session Feedback:', !!sessionFeedback); // NEW

            let dataRestored = false;

            // Restore Final Remarks
            if (backupRemarks && !sessionRemarks) {
                finalRemarksEl.value = backupRemarks;
                dataRestored = true;
                console.log('Restored final remarks from localStorage');
            }
            // Restore Survey Feedback
            if (backupFeedback && !sessionFeedback) { // NEW
                surveyFeedbackEl.value = backupFeedback;
                dataRestored = true;
                console.log('Restored survey feedback from localStorage');
            }
            
            // If we restored any data, immediately save it to the server session
            if (dataRestored) {
                saveDraft().catch(error => {
                    console.error('Failed to sync restored data:', error);
                });
            }
            // If we have current session data (meaning a fresh load), clear old backups
            else if (sessionRemarks || sessionFeedback) {
                console.log('Keeping session data, clearing old backups');
                localStorage.removeItem('final_remarks_backup');
                localStorage.removeItem('survey_feedback_backup'); // NEW
            }

        } catch (e) {
            console.warn('LocalStorage access error:', e);
        }
    }

    // Initialize everything
    syncLocalStorageToSession();

    // Modal click outside to close
    const modal = document.getElementById('confirmationModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal();
            }
        });
    }

    // Auto-save draft on input
    const fieldsToWatch = [
        document.getElementById('final_remarks'),
        document.getElementById('survey_feedback') // NEW: Watch the new field
    ].filter(el => el); // Filter out any elements that might not exist

    if (fieldsToWatch.length > 0) {
        const debouncedSave = debounce(() => {
            saveDraft().catch(error => {
                console.error('Auto-save failed:', error);
            });
        }, 2000);

        fieldsToWatch.forEach(el => {
            el.addEventListener('input', function() {
                // Hide any existing errors when user starts typing in the required field
                const errorBox = document.getElementById('error-box');
                const finalRemarksEl = document.getElementById('final_remarks');
                if (errorBox && finalRemarksEl && finalRemarksEl.value.trim()) {
                    errorBox.style.display = 'none';
                }
                debouncedSave();
            });
        });
    }

    // Expose functions to global scope
    window.handleBackNavigation = handleBackNavigation;
    window.confirmSubmission = confirmSubmission;
    window.submitForm = submitForm;
    window.closeModal = closeModal;
    window.reviewAnswers = reviewAnswers;

    console.log('Final remarks script initialized successfully');
});