// Funciones de modales para Grupos
function openModal() {
  document.getElementById("modal").style.display = "flex";
}

function closeModal() {
  document.getElementById("modal").style.display = "none";
  resetModal();
}

function cancelModal() {
  closeModal();
}

function acceptModal() {
  // Obtener y validar el nombre del grupo.
  const groupName = document.getElementById("groupName").value.trim();
  if (groupName === "") {
    alert("Por favor, ingresa el nombre del grupo.");
    return;
  }

  // Contar el número total de servicios añadidos.
  const servicesBox = document.getElementById("servicesBox");
  const servicesCount = servicesBox.querySelectorAll('.service-item').length;

  // Crear una nueva fila para el grupo
  const groupsList = document.getElementById("groupsList");
  const groupRow = document.createElement("div");
  groupRow.className = "group-row";
  groupRow.innerHTML = `
    <div class="group-name">${groupName}</div>
    <div class="group-services">${servicesCount}</div>
    <div class="group-messages">0</div>
  `;
  groupsList.appendChild(groupRow);

  closeModal();
}

function openServicesModal() {
  document.getElementById("servicesModal").style.display = "flex";
}

function closeServicesModal() {
  document.getElementById("servicesModal").style.display = "none";
}

function acceptServicesModal() {
  const checkboxes = document.querySelectorAll('#servicesTableBody .service-checkbox');
  const servicesBox = document.getElementById("servicesBox");
  servicesBox.innerHTML = "";
  checkboxes.forEach(function(checkbox) {
    if (checkbox.checked) {
      const row = checkbox.closest("tr");
      const serviceName = row.children[1].textContent;
      const serviceItem = document.createElement("div");
      serviceItem.className = "service-item";
      serviceItem.textContent = serviceName;
      servicesBox.appendChild(serviceItem);
    }
  });
  closeServicesModal();
}

function resetModal() {
  document.getElementById("groupName").value = "";
  const servicesBox = document.getElementById("servicesBox");
  while (servicesBox.firstChild) {
    servicesBox.removeChild(servicesBox.firstChild);
  }
  document.querySelectorAll('#servicesTableBody .service-checkbox').forEach(cb => cb.checked = false);
}

// Cerrar modales al hacer clic fuera del contenido
window.onclick = function(event) {
  const modal = document.getElementById('modal');
  const servicesModal = document.getElementById('servicesModal');
  if (event.target == modal) closeModal();
  if (event.target == servicesModal) closeServicesModal();
}

// Filtro de búsqueda en el modal de servicios
document.addEventListener("DOMContentLoaded", function() {
  document.getElementById("serviceSearch").addEventListener("input", function() {
    const filter = this.value.toLowerCase();
    document.querySelectorAll("#servicesTableBody tr").forEach(function(row) {
      const serviceName = row.children[1].textContent.toLowerCase();
      row.style.display = serviceName.includes(filter) ? "" : "none";
    });
  });

  // Recuperar la lista de grupos del localStorage o iniciar con un array vacío.
  let grupos = JSON.parse(localStorage.getItem("gruposData")) || [];
  
  // Si no hay grupos, se crean algunos de ejemplo.
  if (grupos.length === 0) {
    grupos = ["Grupo Alpha", "Grupo Beta", "Grupo Gamma"];
    localStorage.setItem("gruposData", JSON.stringify(grupos));
  }
  
  // Seleccionar el contenedor donde se mostrarán los grupos.
  const groupsList = document.getElementById("groupsList");
  
  // Por cada grupo, crear una fila con tres columnas:
  // • Nombre del grupo
  // • Número total de servicios (inicialmente 0)
  // • Número total de mensajes enviados (inicialmente 0)
  grupos.forEach(function(grupo) {
    const row = document.createElement("div");
    row.className = "group-row";
    row.innerHTML = `
      <div class="group-name">${grupo}</div>
      <div class="group-services">0</div>
      <div class="group-messages">0</div>
    `;
    groupsList.appendChild(row);
  });
});

// Al cargar el documento, se intentan poblar ambos: 
// - El dropdown de grupos (página Redactar)
// - La lista de grupos (página Grupos)
document.addEventListener("DOMContentLoaded", function() {
  // Si la página tiene el select "grupos", se poblá con data
  if (document.getElementById("grupos")) {
    populateGroupsDropdown();
  }
  // Si la página tiene el contenedor "groupsList", se poblá la lista
  if (document.getElementById("groupsList")) {
    populateGroupsList();
  }
});

// Función para poblar el dropdown en la página Redactar
function populateGroupsDropdown() {
  // Intentar recuperar la lista de grupos del localStorage
  let grupos = JSON.parse(localStorage.getItem("gruposData")) || [];
  
  // Si no hay grupos, se crean algunos de ejemplo por defecto
  if (grupos.length === 0) {
    grupos = ["Grupo Alpha", "Grupo Beta", "Grupo Gamma"];
    localStorage.setItem("gruposData", JSON.stringify(grupos));
  }
  
  // Obtener el elemento select y reiniciarlo
  const selectElement = document.getElementById("grupos");
  selectElement.innerHTML = '<option value="">-- Seleccionar --</option>';
  
  // Agregar cada grupo como una opción
  grupos.forEach(function(grupo) {
    const option = document.createElement("option");
    option.value = grupo;
    option.textContent = grupo;
    selectElement.appendChild(option);
  });
}

// Función para poblar la lista de grupos en la página Grupos (si la tienes)
function populateGroupsList() {
  const groupsList = document.getElementById("groupsList");
  groupsList.innerHTML = "";
  let grupos = JSON.parse(localStorage.getItem("gruposData")) || [];
  
  // Si no hay grupos, se crean algunos de ejemplo
  if (grupos.length === 0) {
    grupos = ["Grupo Alpha", "Grupo Beta", "Grupo Gamma"];
    localStorage.setItem("gruposData", JSON.stringify(grupos));
  }
  
  // Por cada grupo, crear una fila y agregarla al contenedor
  grupos.forEach(function(grupo) {
    const row = document.createElement("div");
    row.className = "group-row";
    row.innerHTML = `
      <div class="group-name">${grupo}</div>
      <div class="group-services">0</div>
      <div class="group-messages">0</div>
    `;
    groupsList.appendChild(row);
  });
}

// Función de filtrado (muestra/oculta el menú de filtro)
function filterGroups() {
  var menu = document.getElementById("filterMenu");
  if (menu.style.display === "none" || menu.style.display === "") {
    menu.style.display = "block";
  } else {
    menu.style.display = "none";
  }
}

// Función para ordenar las filas de los grupos según el criterio seleccionado
function sortGroupsBy(criteria) {
  const groupsList = document.getElementById("groupsList");
  // Convertir la colección de filas en un array
  let rows = Array.from(groupsList.getElementsByClassName("group-row"));
  
  if (criteria === "services") {
    rows.sort((a, b) => {
      let aVal = parseInt(a.querySelector(".group-services").textContent) || 0;
      let bVal = parseInt(b.querySelector(".group-services").textContent) || 0;
      return bVal - aVal;
    });
  } else if (criteria === "messages") {
    rows.sort((a, b) => {
      let aVal = parseInt(a.querySelector(".group-messages").textContent) || 0;
      let bVal = parseInt(b.querySelector(".group-messages").textContent) || 0;
      return bVal - aVal;
    });
  }
  
  // Vaciar el contenedor y volver a insertar las filas en orden
  groupsList.innerHTML = "";
  rows.forEach(row => groupsList.appendChild(row));
  // Ocultar el menú tras la selección.
  document.getElementById("filterMenu").style.display = "none";
}

// Cerrar el menú de filtro si se hace clic fuera
document.addEventListener("click", function(event) {
  const menu = document.getElementById("filterMenu");
  const filtroIcon = document.querySelector(".icono-filtro");
  if (menu.style.display === "block" && !menu.contains(event.target) && event.target !== filtroIcon) {
    menu.style.display = "none";
  }
});

document.addEventListener('DOMContentLoaded', function() {
  // --- Funciones para el menú de usuario en la pestaña Redactar ---
  const userToggle = document.querySelector('.user-dropdown-toggle.user-name');
  const userDropdown = document.querySelector('.user-dropdown');
  if (userToggle && userDropdown) {
    // Alterna el despliegue al hacer clic en el nombre de usuario
    userToggle.addEventListener('click', function(e) {
      e.stopPropagation(); // Evita que el clic se propague y cierre el menú al instante
      userDropdown.style.display = (userDropdown.style.display === 'block') ? 'none' : 'block';
    });
    // Cierra el menú si se hace clic fuera de él
    document.addEventListener('click', function() {
      userDropdown.style.display = 'none';
    });
  }

  // --- Funciones para el menú de filtrado en la pestaña Grupos ---
  const filtroBtn = document.querySelector('.icono-filtro');
  if (filtroBtn) {
    filtroBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      const filterMenu = document.getElementById('filterMenu');
      filterMenu.style.display = (filterMenu.style.display === 'block') ? 'none' : 'block';
    });
    // Cierra el menú de filtrado si se hace clic en cualquier otro lugar
    document.addEventListener('click', function() {
      const filterMenu = document.getElementById('filterMenu');
      if (filterMenu) {
        filterMenu.style.display = 'none';
      }
    });
  }

  // --- Otras funciones existentes para Grupos (modales, filtrado real, etc.) ---

  // Ejemplo: Población de datos en el select de la pestaña Redactar
  if (document.getElementById("grupos")) {
    populateGroupsDropdown();
  }
  // Población de la lista en la pestaña Grupos
  if (document.getElementById("groupsList")) {
    populateGroupsList();
  }

  // Filtro de búsqueda en el modal de servicios
  if (document.getElementById("serviceSearch")) {
    document.getElementById("serviceSearch").addEventListener("input", function() {
      const filter = this.value.toLowerCase();
      document.querySelectorAll("#servicesTableBody tr").forEach(function(row) {
        const serviceName = row.children[1].textContent.toLowerCase();
        row.style.display = serviceName.includes(filter) ? "" : "none";
      });
    });
  }

  // Sección de carga inicial para los grupos (localStorage)
  let grupos = JSON.parse(localStorage.getItem("gruposData")) || [];
  if (grupos.length === 0) {
    grupos = ["Grupo Alpha", "Grupo Beta", "Grupo Gamma"];
    localStorage.setItem("gruposData", JSON.stringify(grupos));
  }
  
  // Si estamos en la pestaña Grupos, llenamos el contenedor
  if (document.getElementById("groupsList")) {
    const groupsList = document.getElementById("groupsList");
    groupsList.innerHTML = "";
    grupos.forEach(function(grupo) {
      const row = document.createElement("div");
      row.className = "group-row";
      row.innerHTML = `
        <div class="group-name">${grupo}</div>
        <div class="group-services">0</div>
        <div class="group-messages">0</div>
      `;
      groupsList.appendChild(row);
    });
  }
});

// Función para poblar el dropdown en la pestaña Redactar
function populateGroupsDropdown() {
  let grupos = JSON.parse(localStorage.getItem("gruposData")) || [];
  if (grupos.length === 0) {
    grupos = ["Grupo Alpha", "Grupo Beta", "Grupo Gamma"];
    localStorage.setItem("gruposData", JSON.stringify(grupos));
  }
  const selectElement = document.getElementById("grupos");
  selectElement.innerHTML = '<option value="">-- Seleccionar --</option>';
  grupos.forEach(function(grupo) {
    const option = document.createElement("option");
    option.value = grupo;
    option.textContent = grupo;
    selectElement.appendChild(option);
  });
}

// Función para poblar la lista de grupos en la pestaña Grupos
function populateGroupsList() {
  const groupsList = document.getElementById("groupsList");
  groupsList.innerHTML = "";
  let grupos = JSON.parse(localStorage.getItem("gruposData")) || [];
  if (grupos.length === 0) {
    grupos = ["Grupo Alpha", "Grupo Beta", "Grupo Gamma"];
    localStorage.setItem("gruposData", JSON.stringify(grupos));
  }
  grupos.forEach(function(grupo) {
    const row = document.createElement("div");
    row.className = "group-row";
    row.innerHTML = `
      <div class="group-name">${grupo}</div>
      <div class="group-services">0</div>
      <div class="group-messages">0</div>
    `;
    groupsList.appendChild(row);
  });
}

// Función para mostrar/ocultar el menú de usuario
function toggleUserMenu() {
  const userMenu = document.querySelector('.user-dropdown');
  if (userMenu) {
    userMenu.style.display = (userMenu.style.display === 'block') ? 'none' : 'block';
  }
}

// Cerrar el menú de usuario si se hace clic fuera de él
document.addEventListener('click', function(event) {
  const userMenu = document.querySelector('.user-dropdown');
  const userToggle = document.querySelector('.user-dropdown-toggle.user-name');
  if (userMenu && userToggle && !userMenu.contains(event.target) && event.target !== userToggle) {
    userMenu.style.display = 'none';
  }
});

document.addEventListener("DOMContentLoaded", function() {
  // --- Filtro de Búsqueda en el Modal de Servicios ---
  const serviceSearchInput = document.getElementById("serviceSearch");
  if (serviceSearchInput) {
    serviceSearchInput.addEventListener("input", function() {
      const filter = this.value.toLowerCase();
      document.querySelectorAll("#servicesTableBody tr").forEach(function(row) {
        const serviceName = row.children[1].textContent.toLowerCase();
        row.style.display = serviceName.includes(filter) ? "" : "none";
      });
    });
  }

  // --- Botón de Filtrado en la Pestaña Grupos ---
  const filtroBtn = document.querySelector(".icono-filtro");
  if (filtroBtn) {
    filtroBtn.addEventListener("click", function(e) {
      e.stopPropagation();  // Evita que el clic se propague y cierre el menú inmediatamente
      const filterMenu = document.getElementById("filterMenu");
      if (filterMenu) {
        // Alterna el despliegue del menú de filtrado
        if (filterMenu.style.display === "none" || filterMenu.style.display === "") {
          filterMenu.style.display = "block";
        } else {
          filterMenu.style.display = "none";
        }
      }
    });
  }

  // Cerrar el menú de filtrado cuando se haga clic fuera de él
  document.addEventListener("click", function() {
    const filterMenu = document.getElementById("filterMenu");
    if (filterMenu) {
      filterMenu.style.display = "none";
    }
  });

  // --- Si tienes funciones para cargar grupos en Redactar y Grupos, asegúrate de llamarlas también ---
  if (document.getElementById("grupos")) {
    populateGroupsDropdown();
  }
  if (document.getElementById("groupsList")) {
    populateGroupsList();
  }
});

// Función para poblar el dropdown de grupos en la pestaña Redactar
function populateGroupsDropdown() {
  let grupos = JSON.parse(localStorage.getItem("gruposData")) || [];
  if (grupos.length === 0) {
    grupos = ["Grupo Alpha", "Grupo Beta", "Grupo Gamma"];
    localStorage.setItem("gruposData", JSON.stringify(grupos));
  }
  const selectElement = document.getElementById("grupos");
  selectElement.innerHTML = '<option value="">-- Seleccionar --</option>';
  grupos.forEach(function(grupo) {
    const option = document.createElement("option");
    option.value = grupo;
    option.textContent = grupo;
    selectElement.appendChild(option);
  });
}

// Función para poblar la lista de grupos en la pestaña Grupos
function populateGroupsList() {
  const groupsList = document.getElementById("groupsList");
  groupsList.innerHTML = "";
  let grupos = JSON.parse(localStorage.getItem("gruposData")) || [];
  if (grupos.length === 0) {
    grupos = ["Grupo Alpha", "Grupo Beta", "Grupo Gamma"];
    localStorage.setItem("gruposData", JSON.stringify(grupos));
  }
  grupos.forEach(function(grupo) {
    const row = document.createElement("div");
    row.className = "group-row";
    row.innerHTML = `
      <div class="group-name">${grupo}</div>
      <div class="group-services">0</div>
      <div class="group-messages">0</div>
    `;
    groupsList.appendChild(row);
  });
}
