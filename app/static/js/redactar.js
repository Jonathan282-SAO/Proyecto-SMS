// JS extraído de templates/redactar.html
(function(){
  function toggleUserDropdown() {
    const dropdown = document.getElementById("userDropdown");
    if(!dropdown) return;
    dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
  }

  // Cerrar el menú si se hace clic fuera de él
  document.addEventListener("click", function(event) {
    const dropdown = document.getElementById("userDropdown");
    const toggle = document.querySelector(".user-dropdown-toggle");
    if (dropdown && dropdown.style.display === "block" && !dropdown.contains(event.target) && event.target !== toggle) {
      dropdown.style.display = "none";
    }
  });

  // Validación de caracteres especiales (protecciones null-safe)
  const mensajeTextarea = document.getElementById('mensaje-textarea');
  if (mensajeTextarea) {
    mensajeTextarea.addEventListener('input', function(e) {
      const texto = this.value;
      const textoLimpio = texto.replace(/[^a-zA-Z0-9\s.,!?¿¡()\-]/g, '');
      if (texto !== textoLimpio) {
        this.value = textoLimpio;
        alert('Se han removido caracteres especiales. No se permiten acentos, ñ ni símbolos especiales.');
      }
    });
  }

  // Validación del formulario antes de enviar
  const redactarForm = document.querySelector('form');
  if (redactarForm) {
    redactarForm.addEventListener('submit', function(e) {
      const mensaje = document.getElementById('mensaje-textarea')?.value || '';
      const asunto = document.getElementById('asunto-input')?.value || '';
      const grupo = document.getElementById('grupos')?.value || '';
      const modalidad = document.querySelector('input[name="modalidad"]:checked');

      if (!modalidad) {
        e.preventDefault();
        alert('Por favor, seleccione una modalidad de envío (Correo o SMS).');
        return;
      }

      if (!grupo) {
        e.preventDefault();
        alert('Por favor, seleccione un grupo destino.');
        return;
      }

      if (/[ñáéíóúÑÁÉÍÓÚ]/.test(asunto)) {
        e.preventDefault();
        alert('El asunto no puede contener la letra "ñ" ni caracteres con acento.');
        return;
      }

      // Mostrar modal de confirmación con vista previa
      e.preventDefault();
      showSendPreview({asunto: asunto, mensaje: mensaje, grupo: grupo, modalidad: modalidad.value});
    });
  }

  // Modal de confirmación de envío
  function showSendPreview(data) {
    let modal = document.getElementById('sendPreviewModal');
    if (!modal) return;
    modal.querySelector('.preview-asunto').innerText = data.asunto || '';
    modal.querySelector('.preview-mensaje').innerText = data.mensaje || '';
    
    const grupoSelect = document.getElementById('grupos');
    const grupoOption = grupoSelect.options[grupoSelect.selectedIndex];
    const grupoNombre = grupoOption ? grupoOption.text : `ID: ${data.grupo}`;
    modal.querySelector('.preview-meta').innerText = `Grupo: ${grupoNombre} • Modalidad: ${data.modalidad}`;
    try {
      const bs = new bootstrap.Modal(modal);
      bs.show();
    } catch (e) {
      modal.style.display = 'block';
    }
  }

  // Confirmar envío desde modal
  window.confirmSend = function() {
    const form = document.querySelector('form');
    // cerrar modal si bootstrap
    try { bootstrap.Modal.getInstance(document.getElementById('sendPreviewModal'))?.hide(); } catch(e) {}
    if(form) form.submit();
  };

  // Exponer funciones globales usadas en template
  window.toggleUserDropdown = toggleUserDropdown;
  window.showSendPreview = showSendPreview;

})();
