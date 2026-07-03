document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('loginAdminForm');
    
    // Validación básica del captcha
    form.addEventListener('submit', function(e) {
        const captchaInput = document.querySelector('input[name="captcha"]');
        const captchaValue = captchaInput.value.trim();
        
        if (captchaValue !== '16') {
            e.preventDefault();
            // Mostrar error sin alert()
            const errorDiv = document.querySelector('.error-message');
            if (errorDiv) {
                errorDiv.innerHTML = '<i class="fas fa-exclamation-circle"></i> La respuesta de verificación es incorrecta. 6 + 10 = 16';
                errorDiv.style.display = 'flex';
            } else {
                // Crear mensaje de error si no existe
                const newError = document.createElement('div');
                newError.className = 'error-message';
                newError.innerHTML = '<i class="fas fa-exclamation-circle"></i> La respuesta de verificación es incorrecta. 6 + 10 = 16';
                form.insertBefore(newError, form.firstChild);
            }
            return;
        }
        
        // Si todo está bien, el formulario se envía normalmente
        console.log('Login admin enviado');
    });
});