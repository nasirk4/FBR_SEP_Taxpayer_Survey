// static/js/cross_system_script.js
document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('crossSystemForm');
    if (!form) return;

    // Get CSRF token from the first hidden input with the name 'csrfmiddlewaretoken'
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    // The submit URL is the action attribute of the form
    const submitUrl = form.action;

    // --- Helper Functions for Modals and Errors ---

    // Helper function to create/get inline error box
    function createErrorBox() {
        const errorBox = document.createElement('div');
        errorBox.className = 'error-box';
        errorBox.id = 'error-box';
        errorBox.style.display = 'none';
        const section = document.querySelector('.section');
        if (section) {
            // Prepend the error box at the top of the main section
            section.prepend(errorBox);
        }
        return errorBox;
    }

    // Helper function to create modal for errors
    function createErrorModal(message) {
        const existingModal = document.getElementById('error-modal');
        if (existingModal) existingModal.remove();

        const modal = document.createElement('div');
        modal.id = 'error-modal';
        modal.className = 'error-modal';
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-labelledby', 'error-modal-title');
        modal.setAttribute('aria-describedby', 'error-modal-message');
        modal.innerHTML = `
            <div class="error-modal-content">
                <h2 id="error-modal-title" class="error-modal-title">⚠️ Error</h2>
                <p id="error-modal-message" class="error-modal-message">${message}</p>
                <button type="button" class="btn btn-close-modal" aria-label="Close">Close</button>
            </div>
        `;
        document.body.appendChild(modal);

        const closeButton = modal.querySelector('.btn-close-modal');
        closeButton.focus();

        closeButton.addEventListener('click', () => modal.remove());
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.remove();
        });

        document.addEventListener('keydown', function handleEscape(e) {
            if (e.key === 'Escape') {
                modal.remove();
                document.removeEventListener('keydown', handleEscape);
            }
        });
    }

    // Helper function to create confirmation modal for skip section
    function createConfirmationModal(onConfirm) {
        const existingModal = document.getElementById('confirmation-modal');
        if (existingModal) existingModal.remove();

        const modal = document.createElement('div');
        modal.id = 'confirmation-modal';
        modal.className = 'confirmation-modal';
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-labelledby', 'confirmation-modal-title');
        modal.setAttribute('aria-describedby', 'confirmation-modal-message');
        modal.innerHTML = `
            <div class="confirmation-modal-content">
                <h2 id="confirmation-modal-title" class="confirmation-modal-title">Confirm Skip</h2>
                <p id="confirmation-modal-message" class="confirmation-modal-message">
                    Are you sure you want to skip this optional section? This is the final main section before concluding the survey.
                </p>
                <div class="modal-buttons">
                    <button type="button" class="btn btn-confirm" aria-label="Confirm">Confirm</button>
                    <button type="button" class="btn btn-cancel" aria-label="Cancel">Cancel</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);

        const confirmButton = modal.querySelector('.btn-confirm');
        const cancelButton = modal.querySelector('.btn-cancel');

        cancelButton.focus();

        confirmButton.addEventListener('click', () => {
            modal.remove();
            onConfirm();
        });

        cancelButton.addEventListener('click', () => modal.remove());

        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.remove();
        });

        document.addEventListener('keydown', function handleEscape(e) {
            if (e.key === 'Escape') {
                modal.remove();
                document.removeEventListener('keydown', handleEscape);
            }
        });
    }

    // Helper function to display errors
    function showError(message, type = 'inline') {
        if (type === 'modal') {
            createErrorModal(message);
        } else {
            let errorBox = document.getElementById('error-box');
            if (!errorBox) {
                errorBox = createErrorBox();
            }
            errorBox.style.display = 'block';
            errorBox.innerHTML = `<div class="error-icon">⚠️</div><div class="error-message">${message}</div>`;
            errorBox.setAttribute('aria-live', 'assertive');
            setTimeout(() => errorBox.scrollIntoView({ behavior: 'smooth', block: 'center' }), 100);
        }
    }

    // --- Skip section functionality (Kept the skip logic) ---
    window.skipSection = function(redirectUrl) {
        if (!redirectUrl) {
            console.error('Skip redirect URL not provided.');
            return;
        }

        createConfirmationModal(() => {
            const formData = new FormData();
            formData.append('skip_section', 'true');

            fetch(submitUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.status === 'success') {
                    window.location.href = redirectUrl; // Redirect to final_remarks
                } else {
                    showError(data.message || 'Error skipping section', 'modal');
                }
            })
            .catch(error => {
                console.error('Skip section error:', error);
                showError('Network error occurred. Could not skip section.', 'modal');
            });
        });
    };

    // --- Handle back navigation (Saves draft then navigates) (Kept the save draft logic) ---
    window.handleBackNavigation = function(backUrl) {
        if (!backUrl) {
            console.error('Back URL not provided.');
            return;
        }
        
        const formData = new FormData(form);
        formData.append('save_draft', 'true');

        fetch(submitUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) {
                // Draft saving failed, but we still try to navigate back
                console.warn('Draft save failed, attempting to navigate back anyway.');
            }
            // Navigate back regardless of save status, prioritizing user experience
            window.location.href = backUrl;
        })
        .catch(error => {
            // Network error on save, warn the user, then navigate
            console.error('Back navigation error: Network issue during draft save. Navigating anyway.', error);
            showError('Warning: Could not save draft due to a network error. Navigating back now.', 'modal');
            
            // Navigate after a brief delay to show the warning
            setTimeout(() => {
                window.location.href = backUrl;
            }, 1000); 
        });
    };

    // --- Form submission (Retaining standard HTML5 required validation) ---
    // Since we removed character limit validation, we rely on the browser's native 'required' attribute validation.
    form.addEventListener('submit', function (e) {
        // Standard form submission proceeds unless native validation fails.
    });

    // --- Auto-save functionality removed as it is unnecessary for simple radio buttons ---
});