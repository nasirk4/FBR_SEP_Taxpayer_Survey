// static/js/cross_system_script.js

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('crossSystemForm');
    if (!form) return;

    // Get URLs and CSRF token from data attributes
    const submitUrl = form.dataset.submitUrl;
    const csrfToken = form.dataset.csrfToken;
    const skipRedirectUrl = form.dataset.skipRedirectUrl;
    const backUrl = form.dataset.backUrl;

    // Global flag to track if the form is already submitting after character limit confirmation
    let isSubmitting = false; 

    // Helper function to create/get error box
    function createErrorBox() {
        const errorBox = document.createElement('div');
        errorBox.className = 'error-box';
        errorBox.id = 'error-box';
        errorBox.style.display = 'none';
        const section = document.querySelector('.section');
        if (section) {
            section.prepend(errorBox);
        }
        return errorBox;
    }

    // Helper function to display errors consistently
    function showError(message) {
        let errorBox = document.getElementById('error-box');
        if (!errorBox) {
            errorBox = createErrorBox();
        }
        errorBox.style.display = 'block';
        errorBox.innerHTML = `<div class="error-icon">⚠️</div><div class="error-message">${message}</div>`;
        errorBox.setAttribute('aria-live', 'assertive');
        
        // Scroll to error for visibility
        setTimeout(() => errorBox.scrollIntoView({ behavior: 'smooth', block: 'center' }), 100);
    }
    
    // Initial error box scrolling (for server-side errors, if any)
    const initialErrorBox = document.getElementById('error-box');
    if (initialErrorBox) {
        setTimeout(() => initialErrorBox.scrollIntoView({ behavior: 'smooth', block: 'center' }), 100);
    }

    // Character counters setup
    const textareas = [
        { element: document.querySelector('textarea[name="xs1_coordination_gap"]'), counter: document.getElementById('xs1_char_count') },
        { element: document.querySelector('textarea[name="xs2_single_change"]'), counter: document.getElementById('xs2_char_count') },
        { element: document.querySelector('textarea[name="xs3_systemic_feedback"]'), counter: document.getElementById('xs3_char_count') }
    ];

    textareas.forEach(({ element, counter }) => {
        if (element && counter) {
            updateCharCounter(element, counter);
            element.addEventListener('input', function() {
                updateCharCounter(this, counter);
            });
        }
    });

    function updateCharCounter(textarea, counter) {
        const length = textarea.value.length;
        const maxLength = 1000;
        counter.textContent = `${length}/${maxLength} characters`;
        
        if (length > maxLength * 0.9) {
            counter.style.color = length > maxLength ? '#dc3545' : '#ffc107';
        } else {
            counter.style.color = '#666';
        }
    }

    // --------------------------------------------------------
    // Global Functions (Skip and Back Navigation)
    // --------------------------------------------------------

    // Skip section functionality
    window.skipSection = function() {
        if (confirm('Are you sure you want to skip this optional section? You can still provide this feedback later if you change your mind.')) {
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
                    window.location.href = skipRedirectUrl;
                } else {
                    showError(data.message || 'Error skipping section');
                }
            })
            .catch(error => {
                console.error('Skip section error:', error);
                showError('Network error occurred. Could not skip section.');
            });
        }
    };

    // Handle back navigation (Saves draft then navigates)
    window.handleBackNavigation = function() {
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
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                window.location.href = backUrl;
            } else {
                showError(data.message || 'Error saving draft before navigation.');
            }
        })
        .catch(error => {
            console.error('Back navigation error:', error);
            showError('Network error occurred. Draft not saved. Please try again.');
        });
    };

    // --------------------------------------------------------
    // Local Event Listeners
    // --------------------------------------------------------

    // Form submission (Client-side validation)
    form.addEventListener('submit', function (e) {
        // Fix for double-submission after confirmation
        if (isSubmitting) {
            e.preventDefault();
            return;
        }

        let hasExceededLimit = false;

        textareas.forEach(({ element, counter }) => {
            if (element.value.length > 1000) {
                hasExceededLimit = true;
                counter.style.color = '#dc3545'; 
                counter.classList.add('char-limit-exceeded');
            }
        });

        if (hasExceededLimit) {
            e.preventDefault();
            showError('Some responses exceed the 1000-character limit. Please shorten your answers or confirm to proceed.');
            
            if (confirm('Some responses exceed the recommended character limit. Do you want to proceed anyway?')) {
                // 1. Set the flag to true to block subsequent submit events
                isSubmitting = true; 
                
                // 2. Manually trigger the native form submission, bypassing this listener
                this.submit(); 
            }
            // If the user cancels, the form submission remains prevented.
        }
    });

    // Auto-save draft functionality
    let autoSaveTimeout;
    
    form.addEventListener('input', function() {
        clearTimeout(autoSaveTimeout);
        autoSaveTimeout = setTimeout(function() {
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
                    console.error('Auto-save failed with status:', response.status);
                }
                return response.json();
            })
            .then(data => {
                if (data && data.status !== 'success') {
                    console.error('Draft save error:', data.message);
                }
            })
            .catch(error => {
                console.error('Auto-save network error:', error);
                // Intentionally silent the error to avoid interrupting user flow
            });
        }, 2000); // Wait 2 seconds after last input
    });
});