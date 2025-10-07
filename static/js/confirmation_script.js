// static/js/confirmation_script.js
document.addEventListener('DOMContentLoaded', function () {
    const copyButton = document.getElementById('copy-reference');
    const printButton = document.getElementById('print-page');
    const referenceNumber = document.getElementById('reference-number');

    // Copy reference number functionality
    if (copyButton && referenceNumber) {
        copyButton.addEventListener('click', async function () {
            try {
                await navigator.clipboard.writeText(referenceNumber.textContent);
                
                // Visual feedback
                const originalText = copyButton.textContent;
                copyButton.textContent = 'Copied!';
                copyButton.style.background = '#28a745';
                
                setTimeout(() => {
                    copyButton.textContent = originalText;
                    copyButton.style.background = '';
                }, 2000);
                
            } catch (err) {
                console.error('Failed to copy:', err);
                alert('Failed to copy reference number. Please copy it manually: ' + referenceNumber.textContent);
            }
        });
    }

    // Print functionality
    if (printButton) {
        printButton.addEventListener('click', function () {
            window.print();
        });
    }

    // Auto-focus on reference number for accessibility
    if (referenceNumber) {
        referenceNumber.setAttribute('tabindex', '0');
        referenceNumber.focus();
    }

    // Log confirmation page load
    console.log('Confirmation page loaded successfully');
    if (referenceNumber) {
        console.log('Reference number:', referenceNumber.textContent);
    }
});