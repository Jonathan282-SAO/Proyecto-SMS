// JavaScript para gestión de modales y acciones en grupos
(function(){
  // Funciones para los modales
  function openModal() { document.getElementById('modal')?.style.setProperty('display','block'); }
  function closeModal() { document.getElementById('modal')?.style.setProperty('display','none'); }
  function openServicesModal() { document.getElementById('servicesModal')?.style.setProperty('display','block'); }
  function closeServicesModal() { document.getElementById('servicesModal')?.style.setProperty('display','none'); }

  function acceptServicesModal() {
    const selected = document.querySelectorAll(".service-checkbox:checked");
    const box = document.getElementById("servicesBox");
    if(!box) return;
    box.innerHTML = "";
    selected.forEach(chk => {
      const input = document.createElement("input");
      input.type = "hidden";
      input.name = "usuarios";
      input.value = chk.value;
      box.appendChild(input);
      const label = document.createElement("div");
      label.classList.add("selected-user");
      const uname = chk.dataset && chk.dataset.username ? chk.dataset.username : ('Usuario ' + chk.value);
      label.innerHTML = '<span class="su-name">' + uname + '</span>' + (chk.dataset.role === 'admin' ? ' <span class="badge bg-secondary su-admin">admin</span>' : '');
      box.appendChild(label);
    });
    closeServicesModal();
  }

  function toggleUserDropdown() {
    const dropdown = document.getElementById("userDropdown");
    if(!dropdown) return;
    dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
  }

  function toggleFilterMenu(evt) {
    if (evt && typeof evt.stopPropagation === 'function') evt.stopPropagation();
    const filterMenu = document.getElementById("filterMenu"); if(!filterMenu) return;
    filterMenu.style.display = filterMenu.style.display === "block" ? "none" : "block";
  }

  // Estado de orden actual: criterio y dirección
  let _currentSort = null; // 'services' | 'messages' | null
  let _currentDir = 'desc'; // 'asc' or 'desc'

  function sortGroupsBy(criteria) {
    const label = document.getElementById('filterLabel'); if(!label) return;
    // Texto descriptivo
    let text = 'Filtro: ';
    if (criteria === 'services') text += 'Mayor cantidad de Usuarios';
    else if (criteria === 'messages') text += 'Mayor cantidad de mensajes enviados';
    else text += criteria;
    label.innerText = text; label.style.display = 'inline-block';
    label.style.transform = 'translateY(-2px)';
    setTimeout(() => { label.style.transform = 'none'; }, 200);

    // Determinar dirección: si se selecciona el mismo criterio, alternar
    if (_currentSort === criteria) {
      _currentDir = (_currentDir === 'desc') ? 'asc' : 'desc';
    } else {
      _currentSort = criteria;
      _currentDir = 'desc'; // por defecto mostrar mayor → menor
    }

    // Reordenar DOM
    const container = document.getElementById('groupsList');
    if (!container) return;
    const rows = Array.from(container.querySelectorAll(':scope > .group-row'));

    const getValue = (row) => {
      try {
        if (criteria === 'services') {
          const el = row.querySelector('.group-services');
          return parseInt((el?.textContent || '').replace(/[^0-9]/g,'')) || 0;
        } else if (criteria === 'messages') {
          const el = row.querySelector('.group-messages');
          return parseInt((el?.textContent || '').replace(/[^0-9]/g,'')) || 0;
        }
      } catch (e) { return 0; }
      return 0;
    };

    rows.sort((a,b) => {
      const va = getValue(a);
      const vb = getValue(b);
      return (_currentDir === 'desc') ? (vb - va) : (va - vb);
    });

    // Reinsertar en nuevo orden
    rows.forEach(r => container.appendChild(r));

    // ocultar el menú de filtro
    const fm = document.getElementById("filterMenu"); if(fm) fm.style.display = 'none';
  }

  function closeEditModal() { const modal = document.getElementById('editGroupModal'); if (modal) modal.style.display = 'none'; }
  function openEditModal() { const modal = document.getElementById('editGroupModal'); if (modal) modal.style.display = 'block'; }

  function initEditAndDeleteButtons(){
    document.querySelectorAll('.edit-button').forEach(btn => {
      btn.addEventListener('click', function () {
        const id = this.dataset.id;
        const name = this.dataset.name || '';
        const users = (this.dataset.users || '').split(',').filter(Boolean).map(s => s.trim());
        const form = document.getElementById('editGroupForm'); if (!form) return;
        const tpl = form.dataset.actionTemplate || form.action || '';
        form.action = tpl.replace('/0', '/' + id);
        const nombreInput = document.getElementById('edit_nombre'); if(nombreInput) nombreInput.value = name;
        document.querySelectorAll('.edit-user-checkbox').forEach(cb => { cb.checked = users.includes(cb.value); });
        openEditModal();
      });
    });

    document.querySelectorAll('.delete-button').forEach(btn => {
      btn.addEventListener('click', function () {
        const id = this.dataset.id;
        const name = this.dataset.name || '';
        const form = document.getElementById('deleteGroupForm'); if (!form) return;
        const tpl = form.dataset.actionTemplate || form.action || '';
        form.action = tpl.replace('/0', '/' + id);
        const nameEl = document.getElementById('deleteGroupName'); if(nameEl) nameEl.innerText = name;
        const modal = document.getElementById('deleteGroupModal'); if(modal) modal.style.display = 'block';
      });
    });
  }

  document.addEventListener('click', function (e) {
    const modal = document.getElementById('editGroupModal');
    if (!modal || modal.style.display !== 'block') return;
    const content = modal.querySelector('.modal-content');
    if (content && !content.contains(e.target) && !e.target.classList.contains('edit-button')) { closeEditModal(); }
  });

  document.addEventListener('click', function (e) {
    const modal = document.getElementById('deleteGroupModal');
    if (!modal || modal.style.display !== 'block') return;
    const content = modal.querySelector('.modal-content');
    if (content && !content.contains(e.target) && !e.target.classList.contains('delete-button')) { const m = document.getElementById('deleteGroupModal'); if(m) m.style.display = 'none'; }
  });

  // Exponer funciones globales usadas por atributos onclick
  window.openModal = openModal;
  window.closeModal = closeModal;
  window.openServicesModal = openServicesModal;
  window.closeServicesModal = closeServicesModal;
  window.acceptServicesModal = acceptServicesModal;
  window.toggleUserDropdown = toggleUserDropdown;
  window.toggleFilterMenu = toggleFilterMenu;
  window.sortGroupsBy = sortGroupsBy;
  window.closeEditModal = closeEditModal;
  window.closeDeleteModal = function(){ const m = document.getElementById('deleteGroupModal'); if(m) m.style.display = 'none'; };

  if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', initEditAndDeleteButtons); }
  else { initEditAndDeleteButtons(); }

})();
