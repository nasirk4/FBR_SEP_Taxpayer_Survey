// static/js/role_specific_script.js

function handleBackNavigation(url) {
    saveLP5Data(); // Save LP5 checkbox states before navigating
    window.location.href = url;
}

// Enhanced safe JSON parsing utility function
function safeJsonParse(jsonString, defaultValue = {}) {
    if (!jsonString || typeof jsonString !== 'string') {
        return defaultValue;
    }
    
    const cleaned = jsonString.trim();
    
    // Handle empty or malformed cases
    if (!cleaned || cleaned === '{}' || cleaned === '[]' || cleaned === 'null' || cleaned === '""' || cleaned === '{') {
        return defaultValue;
    }
    
    try {
        // First try direct JSON parse
        return JSON.parse(cleaned);
    } catch (error) {
        console.warn('First JSON parse attempt failed, trying to clean Python-style JSON:', error);
        
        try {
            // Clean Python-style JSON (True/False, single quotes)
            let cleanedJson = cleaned
                .replace(/'/g, '"')  // Replace single quotes with double quotes
                .replace(/True/g, 'true')  // Replace Python True with JavaScript true
                .replace(/False/g, 'false')  // Replace Python False with JavaScript false
                .replace(/None/g, 'null');  // Replace Python None with JavaScript null
            
            // Remove any escape sequences that might have been added by Django
            cleanedJson = cleanedJson.replace(/\\u0027/g, "'")
                                    .replace(/\\u0022/g, '"');
            
            return JSON.parse(cleanedJson);
        } catch (secondError) {
            console.error('JSON parse error after cleaning:', secondError, 'for original string:', jsonString);
            return defaultValue;
        }
    }
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
        lp3: document.getElementById('lp3_error_inline'),
        lp4: document.getElementById('lp4_error_inline'),
        lp5: document.getElementById('lp5_error_inline'),
        lp6: document.getElementById('lp6_error_inline'),
        ca1: document.getElementById('ca1_error_inline'),
        ca2: document.getElementById('ca2_error_inline'),
        ca3: document.getElementById('ca3_error_inline'),
        ca4: document.getElementById('ca4_error_inline'),
        ca5: document.getElementById('ca5_error_inline'),
        ca6_challenge: document.getElementById('ca6_challenge_error_inline'),
        ca6_improvement: document.getElementById('ca6_improvement_error_inline')
    };

    // Reset invalid lp5_saved_data to prevent malformed JSON
    // TODO: Backend should ensure lp5_tax_types_json is valid JSON (e.g., '{}' or '') to avoid this warning
    const savedDataElement = document.getElementById('lp5_saved_data');
    if (savedDataElement && savedDataElement.value === '{') {
        console.warn('Invalid lp5_saved_data detected, resetting to empty string');
        savedDataElement.value = '';
    }

    // --- Legal Practitioner Logic ---

    // LP5: Dynamic Tax-Type Grid Logic
    function updateLP5Section() {
        const lp5Section = document.getElementById('lp5_section');
        const lp5VisibleInput = document.getElementById('lp5_visible');
        
        if (!lp5Section || !lp5VisibleInput) return;

        // Collect all challenges from LP2, LP3, LP4
        const allChallenges = {};
        
        // Check LP2 challenges
        const lp2Radios = document.querySelectorAll('input[name^="lp2_"]');
        lp2Radios.forEach(radio => {
            if (radio.checked && (radio.value === 'moderate_challenge' || radio.value === 'major_challenge')) {
                const functionName = radio.name.replace('lp2_', '');
                allChallenges[functionName] = true;
            }
        });

        // Check LP3 challenges
        const lp3Radios = document.querySelectorAll('input[name^="lp3_"]');
        lp3Radios.forEach(radio => {
            if (radio.checked && (radio.value === 'moderate_challenge' || radio.value === 'major_challenge')) {
                const functionName = radio.name.replace('lp3_', '');
                allChallenges[functionName] = true;
            }
        });

        // Check LP4 challenges
        const lp4Radios = document.querySelectorAll('input[name^="lp4_"]');
        lp4Radios.forEach(radio => {
            if (radio.checked && (radio.value === 'moderate_challenge' || radio.value === 'major_challenge')) {
                const functionName = radio.name.replace('lp4_', '');
                allChallenges[functionName] = true;
            }
        });

        const hasModerateMajorChallenges = Object.keys(allChallenges).length > 0;
        
        lp5Section.style.display = hasModerateMajorChallenges ? 'block' : 'none';
        lp5VisibleInput.value = hasModerateMajorChallenges ? '1' : '0';

        if (hasModerateMajorChallenges) {
            populateLP5Table(Object.keys(allChallenges));
        } else {
            clearLP5Table();
            hideError('lp5');
        }
    }

    function populateLP5Table(challengingFunctions) {
        const tableBody = document.querySelector('#lp5_tax_type_table tbody');
        if (!tableBody) return;

        tableBody.innerHTML = '';

        const functionMap = {
            'appeals_commissioner': 'Appeal filings before Commissioner',
            'appellate_tribunal': 'Appellate Tribunal representations',
            'high_court': 'High Court/Supreme Court references',
            'audit_responses': 'Audit responses & compliance',
            'show_cause': 'Show cause notice responses',
            'return_filing': 'Return filing & compliance',
            'amendments': 'Return amendments & rectifications',
            'withholding': 'Withholding statements & compliance',
            'risk_assessment': 'Risk assessment procedures',
            'tax_planning': 'Tax planning advisory services',
            'adr': 'Alternate Dispute Resolution',
            'settlement': 'Settlement procedures',
            'epayments': 'e-Payments & refund processing',
            'cpr_corrections': 'CPR corrections',
            'correspondence': 'FBR correspondence management'
        };

        // Use enhanced safe JSON parsing for saved data
        const savedDataElement = document.getElementById('lp5_saved_data');
        console.log('Raw LP5 saved data:', savedDataElement?.value);
        
        const savedTaxTypes = safeJsonParse(savedDataElement?.value, {});
        console.log('Parsed LP5 saved data:', savedTaxTypes);

        challengingFunctions.forEach(func => {
            const row = document.createElement('tr');
            const displayName = functionMap[func] || func;
            
            // Get saved checkbox states for this function
            const savedFunctionData = savedTaxTypes[func] || {};
            const incomeTaxChecked = !!savedFunctionData.income_tax; 
            const salesTaxChecked = !!savedFunctionData.sales_tax;
            
            row.innerHTML = `
                <td class="function-name">${functionMap[func] || func}</td>
                <td class="tax-type-option">
                    <input type="checkbox" name="lp5_${func}_income" value="income_tax"
                           ${incomeTaxChecked ? 'checked' : ''}
                           aria-label="Income Tax for ${displayName}">
                </td>
                <td class="tax-type-option">
                    <input type="checkbox" name="lp5_${func}_sales" value="sales_tax"
                           ${salesTaxChecked ? 'checked' : ''}
                           aria-label="Sales Tax/FED for ${displayName}">
                </td>
            `;
            console.log(`Function: ${func}, Income Tax: ${incomeTaxChecked}, Sales Tax: ${salesTaxChecked}`);
            tableBody.appendChild(row);
        });

        // Add event listeners to LP5 checkboxes to save data on change
        const lp5Checkboxes = document.querySelectorAll('input[name^="lp5_"]');
        lp5Checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', saveLP5Data);
        });
    }

    function saveLP5Data() {
        const lp5Checkboxes = document.querySelectorAll('input[name^="lp5_"]');
        const savedData = {};
        
        lp5Checkboxes.forEach(checkbox => {
            const nameParts = checkbox.name.split('_');
            const func = nameParts.slice(1, -1).join('_'); // Join all parts except 'lp5' and tax type
            const taxType = nameParts[nameParts.length - 1] === 'income' ? 'income_tax' : 'sales_tax';
            if (checkbox.checked) {
                if (!savedData[func]) {
                    savedData[func] = {};
                }
                savedData[func][taxType] = true;
            }
        });

        const savedDataElement = document.getElementById('lp5_saved_data');
        if (savedDataElement) {
            try {
                const previousValue = savedDataElement.value;
                savedDataElement.value = JSON.stringify(savedData);
                // Log only when data changes to reduce verbosity
                if (savedDataElement.value !== previousValue) {
                    console.log('LP5 data saved:', savedDataElement.value);
                }
            } catch (error) {
                console.error('Error saving LP5 data:', error);
            }
        }
    }

    function clearLP5Table() {
        const tableBody = document.querySelector('#lp5_tax_type_table tbody');
        if (tableBody) {
            tableBody.innerHTML = '';
        }
    }

    // Grid validation helper
    function validateGrid(gridPrefix, errorField) {
        const radios = document.querySelectorAll(`input[name^="${gridPrefix}_"]`);
        let allCompleted = true;
        
        for (let i = 0; i < radios.length; i += 5) {
            const rowRadios = Array.from(radios).slice(i, i + 5);
            const hasSelection = rowRadios.some(radio => radio.checked);
            if (!hasSelection) {
                allCompleted = false;
                break;
            }
        }
        
        if (!allCompleted) {
            showError(errorField, `Please complete all rows in ${gridPrefix.toUpperCase()}`);
            return false;
        } else {
            hideError(errorField);
            return true;
        }
    }

    // Text validation helper (modified to allow empty input)
    function validateText(textareaId, errorField) {
        const textarea = document.getElementById(textareaId);
        const value = textarea ? textarea.value.trim() : '';
        hideError(errorField); // Always valid, even if empty
        return true;
    }

    // Validate Legal Practitioner Section
    function validateLegalSection() {
        let isValid = true;

        // LP1: Overall Digital Support
        const lp1Selected = document.querySelector('input[name="lp1_digital_support"]:checked');
        if (!lp1Selected) {
            showError('lp1', 'Please select an option for LP1 (Overall Digital Support)');
            isValid = false;
        } else {
            hideError('lp1');
        }

        // LP2: Representation & Appeals Grid
        if (!validateGrid('lp2', 'lp2')) {
            isValid = false;
        }

        // LP3: Compliance & Advisory Grid
        if (!validateGrid('lp3', 'lp3')) {
            isValid = false;
        }

        // LP4: Dispute Resolution & Documentation Grid
        if (!validateGrid('lp4', 'lp4')) {
            isValid = false;
        }

        // LP5: Tax-Type Impact (conditional)
        const lp5Visible = document.getElementById('lp5_visible')?.value === '1';
        if (lp5Visible) {
            const lp5Checkboxes = document.querySelectorAll('input[name^="lp5_"]:checked');
            if (lp5Checkboxes.length === 0) {
                showError('lp5', 'Please indicate tax types for your challenging functions in LP5');
                isValid = false;
            } else {
                hideError('lp5');
            }
        }

        // LP6: Priority Improvement (optional)
        validateText('lp6_priority_improvement', 'lp6');

        return isValid;
    }

    // Validate Customs Agent Section
    function validateCustomsSection() {
        let isValid = true;

        // CA1: Training
        const ca1Selected = document.querySelector('input[name="ca1_training"]:checked');
        if (!ca1Selected) {
            showError('ca1', 'Please select an option for CA1 (Training)');
            isValid = false;
        } else {
            hideError('ca1');
        }

        // CA2: System Integration
        const ca2Selected = document.querySelector('input[name="ca2_system_integration"]:checked');
        if (!ca2Selected) {
            showError('ca2', 'Please select an option for CA2 (System Integration)');
            isValid = false;
        } else {
            hideError('ca2');
        }

        // CA3: Customs Function Challenges Grid
        if (!validateGrid('ca3', 'ca3')) {
            isValid = false;
        }

        // CA4: Process Effectiveness Grid
        if (!validateGrid('ca4', 'ca4')) {
            isValid = false;
        }

        // CA5: Policy Impact
        const ca5Selected = document.querySelector('input[name="ca5_policy_impact"]:checked');
        if (!ca5Selected) {
            showError('ca5', 'Please select an option for CA5 (Policy Impact)');
            isValid = false;
        } else {
            hideError('ca5');
        }

        // CA6: Combined Challenge & Improvement
        const ca6Challenge = document.getElementById('ca6_biggest_challenge');
        if (!ca6Challenge || !ca6Challenge.value) {
            showError('ca6_challenge', 'Please select your biggest challenge in CA6');
            isValid = false;
        } else {
            hideError('ca6_challenge');
        }

        // CA6: Improvement (optional)
        validateText('ca6_improvement', 'ca6_improvement');

        return isValid;
    }

    // Clear validation errors when user interacts
    function clearValidationErrorsOnInteraction() {
        const allRadios = document.querySelectorAll('input[type="radio"]');
        allRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                const name = this.name;
                if (name.startsWith('lp1')) hideError('lp1');
                if (name.startsWith('ca1')) hideError('ca1');
                if (name.startsWith('ca2')) hideError('ca2');
                if (name.startsWith('ca5')) hideError('ca5');
                if (name.startsWith('lp2_') || name.startsWith('lp3_') || name.startsWith('lp4_')) {
                    updateLP5Section();
                }
            });
        });

        const gridRadios = document.querySelectorAll('input[name^="lp2_"], input[name^="lp3_"], input[name^="lp4_"], input[name^="ca3_"], input[name^="ca4_"]');
        gridRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                const gridPrefix = this.name.split('_')[0];
                hideError(gridPrefix);
            });
        });

        document.addEventListener('change', function(e) {
            if (e.target.name && e.target.name.startsWith('lp5_')) {
                hideError('lp5');
            }
        });

        const textareas = document.querySelectorAll('textarea');
        textareas.forEach(textarea => {
            textarea.addEventListener('input', function() {
                if (this.id === 'lp6_priority_improvement') hideError('lp6');
                if (this.id === 'ca6_improvement') hideError('ca6_improvement');
            });
        });

        const ca6Dropdown = document.getElementById('ca6_biggest_challenge');
        if (ca6Dropdown) {
            ca6Dropdown.addEventListener('change', function() {
                hideError('ca6_challenge');
            });
        }
    }

    function validateAllFields() {
        let isValid = true;

        const lpSection = document.querySelector('input[name="lp1_digital_support"]');
        if (lpSection && !validateLegalSection()) {
            isValid = false;
        }

        const caSection = document.querySelector('input[name="ca1_training"]');
        if (caSection && !validateCustomsSection()) {
            isValid = false;
        }

        return isValid;
    }

    function initializeConditionalSections() {
        console.log('Initializing conditional sections...');

        const challengeRadios = document.querySelectorAll('input[name^="lp2_"], input[name^="lp3_"], input[name^="lp4_"]');
        challengeRadios.forEach(radio => {
            radio.addEventListener('change', updateLP5Section);
        });

        // Initialize LP5 section on page load with delay to ensure DOM is ready
        setTimeout(() => {
            updateLP5Section();
        }, 100);
        
        clearValidationErrorsOnInteraction();
        console.log('Conditional sections initialized successfully');
    }

    const form = document.getElementById('roleSpecificForm');
    if (form) {
        form.addEventListener('submit', function (e) {
            console.log('Form submission initiated...');

            // Save LP5 data before validation to ensure it's captured
            saveLP5Data();

            const isValid = validateAllFields();

            if (!isValid) {
                console.log('Form validation failed - preventing submission');
                e.preventDefault();
                const firstError = document.querySelector('.validation-error-inline[style*="display: block"]');
                if (firstError) {
                    firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            } else {
                console.log('Form validation passed - allowing submission to cross-system-perspectives');
            }
        });

        form.addEventListener('change', function(e) {
            if (e.target.type === 'radio' || e.target.type === 'checkbox') {
                if (e.target.name === 'lp1_digital_support') {
                    const lp1Selected = document.querySelector('input[name="lp1_digital_support"]:checked');
                    if (lp1Selected) hideError('lp1');
                }
                if (e.target.name === 'ca1_training') {
                    const ca1Selected = document.querySelector('input[name="ca1_training"]:checked');
                    if (ca1Selected) hideError('ca1');
                }
            }
        });

        form.addEventListener('input', function(e) {
            if (e.target.type === 'textarea') {
                if (e.target.id === 'lp6_priority_improvement' && e.target.value.trim()) {
                    hideError('lp6');
                }
                if (e.target.id === 'ca6_improvement' && e.target.value.trim()) {
                    hideError('ca6_improvement');
                }
            }
        });
    }

    // Handle browser navigation (back/forward) to save LP5 data
    window.addEventListener('beforeunload', saveLP5Data);

    initializeConditionalSections();
    console.log('Role-specific form initialization complete');
});