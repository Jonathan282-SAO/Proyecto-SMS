// JS extraído de templates/notificaciones.html
(function(){
  // Búsqueda en tiempo real
  document.getElementById('searchInputN')?.addEventListener('input', function () {
    const filter = this.value.toLowerCase();
    const liItems = document.querySelectorAll('#mensajesList li');
    liItems.forEach(function (li) {
      const textoEl = li.querySelector('.mensaje-texto');
      const texto = textoEl ? textoEl.textContent.toLowerCase() : '';
      if (texto.indexOf(filter) > -1) {
        li.style.display = '';
      } else {
        li.style.display = 'none';
      }
    });
  });

  function toggleUserDropdown() {
    const dropdown = document.getElementById("userDropdown");
    if(!dropdown) return;
    dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
  }

  // Cerrar el menú si se hace clic fuera de él
  document.addEventListener("click", function (event) {
    const dropdown = document.getElementById("userDropdown");
    const toggle = document.querySelector(".user-dropdown-toggle");
    if (dropdown && dropdown.style.display === "block" && !dropdown.contains(event.target) && event.target !== toggle) {
      dropdown.style.display = "none";
    }
  });

  // Abrir modal de detalles
  document.querySelectorAll('.btn-detalles').forEach(button => {
    button.addEventListener('click', function () {
      const title = this.getAttribute('data-title') || '';
      const text = this.getAttribute('data-text') || '';
      const author = this.getAttribute('data-author') || '';
      const sent = this.getAttribute('data-sent') || '';
      const priority = this.getAttribute('data-priority') || '';
      showNotificationDetails({title, text, author, sent, priority});
    });
  });

  function showNotificationDetails(data) {
    // crear o seleccionar modal
    let modal = document.getElementById('notificationDetailModal');
    if (!modal) return;
    modal.querySelector('.modal-title').innerText = data.title || 'Detalle';
    modal.querySelector('.modal-body .nd-text').innerText = data.text || '';
    modal.querySelector('.nd-meta .nd-sent').innerText = data.sent ? (new Date(data.sent)).toLocaleString() : '';
    modal.querySelector('.nd-meta .nd-author').innerText = data.author || '';
    const badge = modal.querySelector('.nd-meta .nd-badge');
    badge.className = 'badge nd-badge';
    if (data.priority === 'alta') badge.classList.add('bg-danger');
    else if (data.priority === 'media') badge.classList.add('bg-warning');
    else badge.classList.add('bg-success');
    badge.innerText = data.priority ? (data.priority.charAt(0).toUpperCase() + data.priority.slice(1) + ' Prioridad') : '';
    // show bootstrap modal if available
    try {
      const bsModal = new bootstrap.Modal(modal);
      bsModal.show();
    } catch (e) {
      modal.style.display = 'block';
    }
  }

  // Exponer toggle global si es necesario
  window.toggleUserDropdown = toggleUserDropdown;
})();
