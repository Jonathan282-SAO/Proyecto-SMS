document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('loginForm');
    if (!form) return;
    
    // Verificar si hay mensajes flash del servidor
    const flashMessages = document.querySelectorAll('.flashes li, [class*="flash-"]');
    
    flashMessages.forEach(flash => {
        const message = flash.textContent.toLowerCase();
        
        if (message.includes('usuario') || message.includes('perfil') || 
            (message.includes('incorrecto') && !message.includes('contraseña'))) {
            showError('perfil', flash.textContent);
            flash.style.display = 'none';
        }
        
        if (message.includes('contraseña') || message.includes('password') ||
            (message.includes('incorrecto') && message.includes('contraseña'))) {
            showError('contrasenna', flash.textContent);
            flash.style.display = 'none';
        }
    });
    
    // Validación en tiempo real
    form.addEventListener('submit', function(event) {
        let hasErrors = false;
        
        // Validar perfil
        const perfil = document.getElementById('perfil');
        const perfilValue = perfil ? perfil.value.trim() : '';
        if (!perfilValue) {
            showError('perfil', 'El nombre de perfil es requerido');
            hasErrors = true;
        } else {
            hideError('perfil');
        }
        
        // Validar contraseña
        const contrasenna = document.getElementById('contrasenna');
        const contrasennaValue = contrasenna ? contrasenna.value.trim() : '';
        if (!contrasennaValue) {
            showError('contrasenna', 'La contraseña es requerida');
            hasErrors = true;
        } else {
            hideError('contrasenna');
        }
        
        if (hasErrors) {
            event.preventDefault();
        }
    });
    
    // Limpiar errores al escribir
    const perfilInput = document.getElementById('perfil');
    if (perfilInput) {
        perfilInput.addEventListener('input', function() {
            if (this.value.trim()) {
                hideError('perfil');
            }
        });
    }
    
    const contrasennaInput = document.getElementById('contrasenna');
    if (contrasennaInput) {
        contrasennaInput.addEventListener('input', function() {
            if (this.value.trim()) {
                hideError('contrasenna');
            }
        });
    }
});

function showError(field, message) {
    const input = document.getElementById(field);
    const errorDiv = document.getElementById(field + '-error');
    
    if (input && errorDiv) {
        input.classList.add('is-invalid');
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        
        // Enfocar el campo con error
        input.focus();
    }
}

function hideError(field) {
    const input = document.getElementById(field);
    const errorDiv = document.getElementById(field + '-error');
    
    if (input && errorDiv) {
        input.classList.remove('is-invalid');
        errorDiv.style.display = 'none';
    }
}