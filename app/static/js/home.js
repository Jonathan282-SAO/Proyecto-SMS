// JS extraído de templates/home.html
(function(){
  document.getElementById('searchInput')?.addEventListener('input', function() {
    const filter = this.value.toLowerCase();
    const messagesList = document.querySelectorAll('#enviosList li');
    messagesList.forEach(function(message) {
      if(message.textContent.toLowerCase().indexOf(filter) > -1) {
        message.style.display = '';
      } else {
        message.style.display = 'none';
      }
    });
  });

  function toggleUserDropdown() {
    const dropdown = document.getElementById("userDropdown");
    if(!dropdown) return;
    dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
  }

  document.addEventListener("click", function(event) {
    const dropdown = document.getElementById("userDropdown");
    const toggle = document.querySelector(".user-dropdown-toggle");
    if (dropdown && dropdown.style.display === "block" && !dropdown.contains(event.target) && event.target !== toggle) {
      dropdown.style.display = "none";
    }
  });

  window.toggleUserDropdown = toggleUserDropdown;

})();
