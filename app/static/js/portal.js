(function(){
  // Smooth scrolling
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // Navbar background on scroll
  window.addEventListener('scroll', function() {
    const navbar = document.querySelector('.navbar-custom');
    if (!navbar) return;
    if (window.scrollY > 100) {
      navbar.style.background = 'rgba(255, 255, 255, 0.98)';
    } else {
      navbar.style.background = 'rgba(255, 255, 255, 0.95)';
    }
  });

  // Animation on scroll for feature cards
  const observerOptions = { threshold: 0.1, rootMargin: '0px 0px -50px 0px' };
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
      }
    });
  }, observerOptions);

  // Apply animations to feature cards
  document.querySelectorAll('.feature-card').forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(card);
  });

  // Corner login behaviour with error handling
  (function(){
    const corner = document.getElementById('cornerLogin');
    const closeBtn = document.getElementById('closeCornerLogin');
    if(!corner) return;

    // Close handler
    closeBtn && closeBtn.addEventListener('click', function(){ 
        corner.style.display = 'none'; 
    });

    // Auto hide when scrolled too far (small UX tweak)
    window.addEventListener('scroll', function(){
      if(window.scrollY > 600){ 
          corner.style.opacity = '0.85'; 
      } else { 
          corner.style.opacity = '1'; 
      }
    });

    // Corner login form handling - ESTO DEBE ESTAR DENTRO DE ESTA FUNCIÓN
    const cornerForm = corner.querySelector('form');
    if (cornerForm) {
        // Process existing flash messages
        processCornerFlashMessages();
        
        // Form submission validation
        cornerForm.addEventListener('submit', function(e) {
            if (!validateCornerForm()) {
                e.preventDefault();
            }
        });

        // Clear errors on input
        const inputs = cornerForm.querySelectorAll('input');
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                clearCornerError(this);
            });
        });
    }

    function processCornerFlashMessages() {
        // Look for flash messages in the page
        const flashMessages = document.querySelectorAll('.alert, [class*="error"], [class*="flash"]');
        
        let foundErrors = false;
        
        flashMessages.forEach(flash => {
            const message = flash.textContent.toLowerCase();
            
            // Check if message is related to corner login
            if (message.includes('login') || message.includes('acceso') || 
                message.includes('usuario') || message.includes('perfil') || 
                message.includes('contraseña') || message.includes('password') ||
                message.includes('incorrecto') || message.includes('inválido')) {
                
                foundErrors = true;
                // Show corner login if hidden
                corner.style.display = 'block';
                corner.style.opacity = '1';
                
                // Assign message to appropriate field
                if (message.includes('usuario') || message.includes('perfil')) {
                    showCornerError('perfil', flash.textContent);
                } else if (message.includes('contraseña') || message.includes('password')) {
                    showCornerError('contrasenna', flash.textContent);
                } else {
                    // Generic login error - show on both fields
                    showCornerError('perfil', 'Credenciales incorrectas');
                    showCornerError('contrasenna', 'Credenciales incorrectas');
                }
                
                // Hide the original flash message
                flash.style.display = 'none';
            }
        });

        // También buscar en elementos de texto directo
        if (!foundErrors) {
            const allTextElements = document.querySelectorAll('body *');
            allTextElements.forEach(element => {
                if (element.children.length === 0 && element.textContent.trim()) {
                    const text = element.textContent.toLowerCase();
                    if ((text.includes('usuario') || text.includes('contraseña')) && 
                        text.length < 150) {
                        
                        corner.style.display = 'block';
                        corner.style.opacity = '1';
                        showCornerError('perfil', 'Credenciales incorrectas');
                        showCornerError('contrasenna', 'Credenciales incorrectas');
                        element.style.display = 'none';
                    }
                }
            });
        }
    }

    function validateCornerForm() {
        let isValid = true;
        const form = corner.querySelector('form');
        
        // Validate username
        const usernameInput = form.querySelector('input[name="perfil"]');
        if (usernameInput && !usernameInput.value.trim()) {
            showCornerErrorElement(usernameInput, 'El usuario es requerido');
            isValid = false;
        }
        
        // Validate password
        const passwordInput = form.querySelector('input[name="contrasenna"]');
        if (passwordInput && !passwordInput.value.trim()) {
            showCornerErrorElement(passwordInput, 'La contraseña es requerida');
            isValid = false;
        }
        
        return isValid;
    }

    function showCornerError(fieldName, message) {
        const form = corner.querySelector('form');
        const input = form.querySelector(`input[name="${fieldName}"]`);
        if (input) {
            showCornerErrorElement(input, message);
        }
    }

    function showCornerErrorElement(input, message) {
        // Clear previous error
        clearCornerError(input);
        
        // Add error class
        input.classList.add('is-invalid');
        
        // Create error message element
        const errorDiv = document.createElement('div');
        errorDiv.className = 'corner-error-message';
        errorDiv.textContent = message;
        errorDiv.style.cssText = 'color: #dc3545; font-size: 0.7rem; margin-top: 0.2rem; display: block;';
        
        // Insert after input
        input.parentNode.insertBefore(errorDiv, input.nextSibling);
        
        // Focus the field with error
        input.focus();
    }

    function clearCornerError(input) {
        input.classList.remove('is-invalid');
        
        // Remove existing error message
        const existingError = input.parentNode.querySelector('.corner-error-message');
        if (existingError) {
            existingError.remove();
        }
    }

  })(); 

})();