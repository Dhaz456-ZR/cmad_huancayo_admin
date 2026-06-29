document.addEventListener('DOMContentLoaded', function() {
    // Toggle mostrar/ocultar contraseña
    const togglePassword = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('password');

    if (togglePassword && passwordInput) {
        togglePassword.addEventListener('click', function() {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            this.textContent = type === 'password' ? '👁' : '👁‍🗨';
        });
    }

    // Refrescar CAPTCHA
    const refreshCaptcha = document.getElementById('refreshCaptcha');
    const captchaQuestion = document.getElementById('captchaQuestion');

    if (refreshCaptcha && captchaQuestion) {
        refreshCaptcha.addEventListener('click', function() {
            const num1 = Math.floor(Math.random() * 10) + 1;
            const num2 = Math.floor(Math.random() * 10) + 1;
            captchaQuestion.textContent = `${num1} + ${num2} = ?`;
            captchaQuestion.dataset.resultado = num1 + num2;
        });
    }

    // Inicializar CAPTCHA
    if (captchaQuestion) {
        const num1 = Math.floor(Math.random() * 10) + 1;
        const num2 = Math.floor(Math.random() * 10) + 1;
        captchaQuestion.textContent = `${num1} + ${num2} = ?`;
        captchaQuestion.dataset.resultado = num1 + num2;
    }

    // Validar formulario antes de enviar
    const loginForm = document.getElementById('loginForm');
    const loading = document.getElementById('loading');
    const mensaje = document.getElementById('mensaje');

    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const usuario = document.getElementById('usuario');
            const password = document.getElementById('password');
            const captchaInput = document.getElementById('captchaInput');
            
            // Validar CAPTCHA
            if (captchaQuestion && captchaInput) {
                const resultado = parseInt(captchaQuestion.dataset.resultado);
                const respuesta = parseInt(captchaInput.value);
                
                if (respuesta !== resultado) {
                    e.preventDefault();
                    mostrarMensaje('❌ CAPTCHA incorrecto. Intente nuevamente.', 'error');
                    
                    // Refrescar CAPTCHA
                    const num1 = Math.floor(Math.random() * 10) + 1;
                    const num2 = Math.floor(Math.random() * 10) + 1;
                    captchaQuestion.textContent = `${num1} + ${num2} = ?`;
                    captchaQuestion.dataset.resultado = num1 + num2;
                    captchaInput.value = '';
                    
                    return false;
                }
            }
            
            // Mostrar loading
            if (loading) {
                loading.style.display = 'block';
            }
            
            // Ocultar mensaje anterior
            if (mensaje) {
                mensaje.style.display = 'none';
            }
        });
    }

    // Función para mostrar mensajes
    function mostrarMensaje(texto, tipo) {
        if (mensaje) {
            mensaje.textContent = texto;
            mensaje.className = 'mensaje ' + tipo;
            mensaje.style.display = 'block';
            
            setTimeout(function() {
                mensaje.style.opacity = '0';
                setTimeout(function() {
                    mensaje.style.display = 'none';
                    mensaje.style.opacity = '1';
                }, 500);
            }, 5000);
        }
    }

    // Auto-ocultar mensaje de error si existe
    if (mensaje && mensaje.textContent.trim() !== '') {
        mensaje.style.display = 'block';
        setTimeout(function() {
            mensaje.style.opacity = '0';
            setTimeout(function() {
                mensaje.style.display = 'none';
                mensaje.style.opacity = '1';
            }, 500);
        }, 5000);
    }
});