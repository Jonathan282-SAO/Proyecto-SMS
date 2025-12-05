// JS extraído de templates/extras/ayuda.html
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

  // Mejorar la experiencia del acordeón
  document.addEventListener('DOMContentLoaded', function() {
    const accordionItems = document.querySelectorAll('.accordion-button');
    accordionItems.forEach(item => {
      item.addEventListener('click', function() {
        this.classList.toggle('active');
      });
    });
  });

  window.toggleUserDropdown = toggleUserDropdown;
})();
