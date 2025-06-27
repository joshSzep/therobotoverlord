/**
 * Password validation for The Robot Overlord
 *
 * Provides real-time feedback on password requirements:
 * - At least 8 characters
 * - At least one uppercase letter
 * - At least one lowercase letter
 * - At least one digit
 * - At least one special character
 */

document.addEventListener('DOMContentLoaded', function() {
    // Find password fields
    const passwordField = document.getElementById('password');
    const confirmPasswordField = document.getElementById('confirm_password');

    if (passwordField) {
        // Create validation feedback container
        const feedbackContainer = document.createElement('div');
        feedbackContainer.className = 'password-requirements';
        feedbackContainer.innerHTML = `
            <div class="requirement-title">PASSWORD REQUIREMENTS:</div>
            <ul>
                <li id="length-req">At least 8 characters</li>
                <li id="uppercase-req">At least one uppercase letter</li>
                <li id="lowercase-req">At least one lowercase letter</li>
                <li id="digit-req">At least one digit</li>
                <li id="special-req">At least one special character</li>
            </ul>
        `;

        // Insert feedback container after password field's parent div
        passwordField.parentNode.appendChild(feedbackContainer);

        // Style the requirements
        const style = document.createElement('style');
        style.textContent = `
            .password-requirements {
                margin-top: 5px;
                padding: 10px;
                background-color: #1a1a1a;
                border: 1px solid #444;
                border-radius: 3px;
                font-size: 0.9em;
            }

            .requirement-title {
                font-weight: bold;
                margin-bottom: 5px;
                color: #cc0000;
            }

            .password-requirements ul {
                margin: 0;
                padding-left: 20px;
            }

            .password-requirements li {
                margin: 3px 0;
                color: #777;
            }

            .password-requirements li.valid {
                color: #2ecc71;
            }

            .password-requirements li.valid::before {
                content: "✓ ";
            }

            .password-requirements li.invalid {
                color: #e74c3c;
            }

            .password-requirements li.invalid::before {
                content: "✗ ";
            }
        `;
        document.head.appendChild(style);

        // Add input event listener to password field
        passwordField.addEventListener('input', function() {
            validatePassword(this.value);
        });

        // If confirm password field exists, add validation for it
        if (confirmPasswordField) {
            confirmPasswordField.addEventListener('input', function() {
                validatePasswordMatch(passwordField.value, this.value);
            });

            // Create match feedback element
            const matchFeedback = document.createElement('div');
            matchFeedback.id = 'password-match-feedback';
            matchFeedback.style.marginTop = '5px';
            matchFeedback.style.color = '#e74c3c';
            confirmPasswordField.parentNode.appendChild(matchFeedback);
        }
    }

    /**
     * Validates password against requirements and updates UI
     */
    function validatePassword(password) {
        // Check requirements
        const lengthValid = password.length >= 8;
        const uppercaseValid = /[A-Z]/.test(password);
        const lowercaseValid = /[a-z]/.test(password);
        const digitValid = /\d/.test(password);
        const specialValid = /[!@#$%^&*(),.?":{}|<>]/.test(password);

        // Update UI
        updateRequirementUI('length-req', lengthValid);
        updateRequirementUI('uppercase-req', uppercaseValid);
        updateRequirementUI('lowercase-req', lowercaseValid);
        updateRequirementUI('digit-req', digitValid);
        updateRequirementUI('special-req', specialValid);

        // If confirm password field exists, check match
        if (confirmPasswordField && confirmPasswordField.value) {
            validatePasswordMatch(password, confirmPasswordField.value);
        }

        return lengthValid && uppercaseValid && lowercaseValid && digitValid && specialValid;
    }

    /**
     * Updates the UI for a specific requirement
     */
    function updateRequirementUI(elementId, isValid) {
        const element = document.getElementById(elementId);
        if (element) {
            element.classList.remove('valid', 'invalid');
            element.classList.add(isValid ? 'valid' : 'invalid');
        }
    }

    /**
     * Validates that passwords match and updates UI
     */
    function validatePasswordMatch(password, confirmPassword) {
        const matchFeedback = document.getElementById('password-match-feedback');
        if (matchFeedback) {
            if (!confirmPassword) {
                matchFeedback.textContent = '';
            } else if (password === confirmPassword) {
                matchFeedback.textContent = '✓ Passwords match';
                matchFeedback.style.color = '#2ecc71';
            } else {
                matchFeedback.textContent = '✗ Passwords do not match';
                matchFeedback.style.color = '#e74c3c';
            }
        }
    }
});
