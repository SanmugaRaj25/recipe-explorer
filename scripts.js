document.addEventListener('DOMContentLoaded', () => {
    // Ensure SweetAlert2 is loaded
    if (typeof Swal === 'undefined') {
        console.error('SweetAlert2 is not loaded. Please include the SweetAlert2 library.');
        return;
    }

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    if (forms.length === 0) {
        console.warn('No forms with the class "needs-validation" found.');
    } else {
        forms.forEach(form => {
            form.addEventListener('submit', event => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                    Swal.fire({
                        icon: 'error',
                        title: 'Oops...',
                        text: 'Please fill out all required fields!',
                    });
                }
                form.classList.add('was-validated');
            });
        });
    }

    // Success alert on button click
    const successButton = document.querySelector('#success-btn');
    if (!successButton) {
        console.warn('No element with ID "success-btn" found.');
    } else {
        successButton.addEventListener('click', () => {
            Swal.fire({
                icon: 'success',
                title: 'Success!',
                text: 'Your form has been submitted.',
            });
        });
    }
});
