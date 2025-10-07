// home/nasirk4/FBR_SEP_Taxpayer_Survey/static/js/base_script.js

/**
 * FBR Survey Progress Manager
 * Handles progress bar display and step navigation
 */

class ProgressManager {
    constructor() {
        this.config = {
            totalSteps: 6,
            animationDuration: 500,
            pulseInterval: 2000
        };
        
        this.elements = {
            progressBar: document.getElementById('progressBar'),
            progressPercentage: document.getElementById('progressPercentage'),
            steps: document.querySelectorAll('.step')
        };
        
        this.state = {
            currentStep: window.djangoContext?.currentStep || 1,
            progressPercentage: window.djangoContext?.progressPercentage || 0
        };
        
        this.init();
    }

    /**
     * Initialize the progress manager
     */
    init() {
        this.validateState();
        this.updateDisplay();
        this.setupAnimations();
        this.logInitialState();
    }

    /**
     * Validate the current state against server values
     */
    validateState() {
        const { currentStep, progressPercentage } = this.state;
        
        if (currentStep < 1 || currentStep > this.config.totalSteps) {
            console.warn(`Invalid currentStep: ${currentStep}, resetting to 1`);
            this.state.currentStep = 1;
        }
        
        if (progressPercentage < 0 || progressPercentage > 100) {
            console.warn(`Invalid progressPercentage: ${progressPercentage}, resetting to 0`);
            this.state.progressPercentage = 0;
        }
    }

    /**
     * Update all progress displays
     */
    updateDisplay() {
        this.updateProgressBar();
        this.updateStepStates();
        this.updatePercentageDisplay();
    }

    /**
     * Update the progress bar width
     */
    updateProgressBar() {
        if (this.elements.progressBar) {
            this.elements.progressBar.style.width = `${this.state.progressPercentage}%`;
        }
    }

    /**
     * Update the percentage text display
     */
    updatePercentageDisplay() {
        if (this.elements.progressPercentage) {
            this.elements.progressPercentage.textContent = `${this.state.progressPercentage}%`;
        }
    }

    /**
     * Update step completion and active states
     */
    updateStepStates() {
        this.elements.steps.forEach((step, index) => {
            const stepNumber = index + 1;
            const stepCircle = step.querySelector('.step-circle');
            
            // Clear previous states
            step.classList.remove('active', 'completed');
            
            // Apply new states
            if (stepNumber < this.state.currentStep) {
                step.classList.add('completed');
            } else if (stepNumber === this.state.currentStep) {
                step.classList.add('active');
                this.activateStep(stepCircle);
            }
        });
    }

    /**
     * Activate a step with pulse animation
     */
    activateStep(stepCircle) {
        if (!stepCircle) return;
        
        // Reset animation
        stepCircle.style.animation = 'none';
        
        // Force reflow
        void stepCircle.offsetWidth;
        
        // Apply pulse animation
        stepCircle.style.animation = `pulse ${this.config.pulseInterval}ms infinite`;
    }

    /**
     * Setup progress bar animations
     */
    setupAnimations() {
        setTimeout(() => {
            if (this.elements.progressBar) {
                this.elements.progressBar.style.backgroundSize = '200% 100%';
            }
        }, this.config.animationDuration);
    }

    /**
     * Add completion effects when survey is finished
     */
    addCompletionEffects() {
        if (this.state.progressPercentage === 100) {
            if (this.elements.progressBar) {
                this.elements.progressBar.classList.add('completed');
            }
            
            // Add bounce animation to completed steps
            document.querySelectorAll('.step.completed .step-circle').forEach(circle => {
                circle.style.animation = 'bounce 0.6s ease-in-out';
            });
        }
    }

    /**
     * Log initial state for debugging
     */
    logInitialState() {
        console.log('Progress Manager initialized:', {
            currentStep: this.state.currentStep,
            progressPercentage: this.state.progressPercentage,
            totalSteps: this.config.totalSteps
        });
    }

    /**
     * Public method to update step (for navigation)
     */
    setStep(step) {
        if (step >= 1 && step <= this.config.totalSteps) {
            this.state.currentStep = step;
            this.updateDisplay();
        }
    }

    /**
     * Get current progress state
     */
    getCurrentState() {
        return {
            currentStep: this.state.currentStep,
            progressPercentage: this.state.progressPercentage
        };
    }
}

/**
 * Navigation Controller
 * Handles survey navigation and form submissions
 */
class NavigationController {
    constructor() {
        this.progressManager = null;
        this.init();
    }

    /**
     * Initialize navigation controller
     */
    init() {
        this.setupEventListeners();
    }

    /**
     * Setup global event listeners
     */
    setupEventListeners() {
        // Next button handlers
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('btn-next')) {
                this.handleNextButton(e.target);
            }
        });

        // Submit button handlers
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('btn-submit')) {
                this.handleSubmitButton(e.target);
            }
        });
    }

    /**
     * Handle next button clicks
     */
    handleNextButton(button) {
        if (this.progressManager) {
            const currentState = this.progressManager.getCurrentState();
            const nextStep = Math.min(this.progressManager.config.totalSteps, currentState.currentStep + 1);
            this.progressManager.setStep(nextStep);
        }
    }

    /**
     * Handle submit button clicks
     */
    handleSubmitButton(button) {
        if (this.progressManager) {
            this.progressManager.setStep(6); // Final step
        }
        this.prepareFormSubmission();
    }

    /**
     * Prepare form for submission
     */
    prepareFormSubmission() {
        const form = document.querySelector('form');
        if (form) {
            // Ensure confirmation field exists
            let confirmField = form.querySelector('input[name="confirm_submit"]');
            if (!confirmField) {
                confirmField = document.createElement('input');
                confirmField.type = 'hidden';
                confirmField.name = 'confirm_submit';
                form.appendChild(confirmField);
            }
            confirmField.value = 'true';
        }
    }

    /**
     * Set progress manager instance
     */
    setProgressManager(manager) {
        this.progressManager = manager;
    }
}

/**
 * Modal Controller
 * Handles confirmation modals and dialogs
 */
class ModalController {
    constructor() {
        this.modals = new Map();
        this.init();
    }

    /**
     * Initialize modal controller
     */
    init() {
        this.registerModals();
        this.setupEventListeners();
    }

    /**
     * Register all modals on the page
     */
    registerModals() {
        const modalElements = document.querySelectorAll('.modal');
        modalElements.forEach(modal => {
            const modalId = modal.id;
            this.modals.set(modalId, modal);
        });
    }

    /**
     * Setup modal event listeners
     */
    setupEventListeners() {
        // Close modals when clicking outside
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.closeModal(e.target.id);
            }
        });

        // Close modals with close buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-close') || 
                e.target.closest('.modal-close')) {
                const modal = e.target.closest('.modal');
                if (modal) {
                    this.closeModal(modal.id);
                }
            }
        });
    }

    /**
     * Open a modal by ID
     */
    openModal(modalId) {
        const modal = this.modals.get(modalId);
        if (modal) {
            modal.style.display = 'block';
            document.body.style.overflow = 'hidden';
        }
    }

    /**
     * Close a modal by ID
     */
    closeModal(modalId) {
        const modal = this.modals.get(modalId);
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = '';
        }
    }

    /**
     * Toggle modal visibility
     */
    toggleModal(modalId) {
        const modal = this.modals.get(modalId);
        if (modal) {
            if (modal.style.display === 'block') {
                this.closeModal(modalId);
            } else {
                this.openModal(modalId);
            }
        }
    }
}

/**
 * Global navigation functions
 * Maintained for backward compatibility
 */

/**
 * Handle back navigation
 * @param {string} targetUrl - URL to navigate to
 */
function handleBackNavigation(targetUrl) {
    window.location.href = targetUrl;
}

/**
 * Open confirmation modal
 */
function openModal() {
    const modalController = window.modalController;
    if (modalController) {
        modalController.openModal('confirmationModal');
    }
}

/**
 * Close confirmation modal
 */
function closeModal() {
    const modalController = window.modalController;
    if (modalController) {
        modalController.closeModal('confirmationModal');
    }
}

/**
 * Handle modal back action
 */
function handleModalBack() {
    const progressManager = window.progressManager;
    if (progressManager) {
        progressManager.setStep(6);
    }
    closeModal();
}

/**
 * Submit form with progress update
 */
function submitForm() {
    const progressManager = window.progressManager;
    if (progressManager) {
        progressManager.setStep(6);
    }
    
    const form = document.querySelector('form');
    if (form) {
        let confirmField = form.querySelector('input[name="confirm_submit"]');
        if (!confirmField) {
            confirmField = document.createElement('input');
            confirmField.type = 'hidden';
            confirmField.name = 'confirm_submit';
            form.appendChild(confirmField);
        }
        confirmField.value = 'true';
        form.submit();
    }
}

/**
 * Initialize the application when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing FBR Survey Application...');
    
    // Initialize progress manager
    window.progressManager = new ProgressManager();
    
    // Initialize navigation controller
    window.navigationController = new NavigationController();
    window.navigationController.setProgressManager(window.progressManager);
    
    // Initialize modal controller
    window.modalController = new ModalController();
    
    console.log('FBR Survey Application initialized successfully');
});

/**
 * Error boundary for unhandled errors
 */
window.addEventListener('error', function(e) {
    console.error('Application error:', e.error);
});

/**
 * Export for testing (if needed)
 */
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        ProgressManager,
        NavigationController,
        ModalController
    };
}