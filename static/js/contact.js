document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.getElementById('contact-form');
    const formMessage = document.getElementById('form-message');
    
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form data
            const name = document.getElementById('name').value.trim();
            const email = document.getElementById('email').value.trim();
            const message = document.getElementById('message').value.trim();
            
            // Simple validation
            if (!name || !email || !message) {
                showMessage('Please fill in all fields.', 'error');
                return;
            }
            
            if (!isValidEmail(email)) {
                showMessage('Please enter a valid email address.', 'error');
                return;
            }
            
            // Create request data
            const data = {
                name: name,
                email: email,
                message: message
            };
            
            // Show loading message
            showMessage('Sending message...', 'info');
            
            // Send data to server
            fetch('/api/submit_contact', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showMessage(data.message || 'Message sent successfully!', 'success');
                    contactForm.reset(); // Clear form
                } else {
                    showMessage(data.message || 'Error sending message. Please try again.', 'error');
                }
            })
            .catch(error => {
                console.error('Error submitting form:', error);
                showMessage('Network error. Please try again later.', 'error');
            });
        });
    }
    
    // Email validation function
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    // Show form messages
    function showMessage(message, type) {
        if (formMessage) {
            formMessage.textContent = message;
            formMessage.className = 'alert';
            
            switch (type) {
                case 'success':
                    formMessage.classList.add('alert-success');
                    break;
                case 'error':
                    formMessage.classList.add('alert-error');
                    break;
                case 'info':
                default:
                    formMessage.classList.add('alert-info');
                    break;
            }
            
            // Scroll to the message
            formMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }
});
