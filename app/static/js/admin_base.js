// JS para admin_base: toggle sidebar
(function(){
  document.getElementById('toggleSidebar')?.addEventListener('click', function(){
    const sb = document.getElementById('adminSidebar');
    if(!sb) return;
    sb.classList.toggle('d-none');
  });

  // Populate schedule modal when opened from a 'Programar' button
  try{
    var scheduleModal = document.getElementById('scheduleModal');
    if (scheduleModal) {
      scheduleModal.addEventListener('show.bs.modal', function (event) {
        var button = event.relatedTarget;
        if (!button) return;
        var campaignId = button.getAttribute('data-campaign-id');
        var campaignDate = button.getAttribute('data-campaign-date') || '';
        var inputId = document.getElementById('sched_campaign_id');
        var inputDate = document.getElementById('scheduled_at');
        var inputTz = document.getElementById('tz_offset');
        if (inputId) inputId.value = campaignId;
        if (inputDate) {
          if (campaignDate) {
            // campaignDate arrived from server as UTC string 'YYYY-MM-DDTHH:MM'
            try {
              var d = new Date(campaignDate + 'Z'); // parse as UTC
              // format as local datetime-local value: YYYY-MM-DDTHH:MM
              var yyyy = d.getFullYear();
              var mm = String(d.getMonth() + 1).padStart(2, '0');
              var dd = String(d.getDate()).padStart(2, '0');
              var hh = String(d.getHours()).padStart(2, '0');
              var min = String(d.getMinutes()).padStart(2, '0');
              inputDate.value = yyyy + '-' + mm + '-' + dd + 'T' + hh + ':' + min;
            } catch (e) {
              inputDate.value = campaignDate;
            }
          } else {
            inputDate.value = '';
          }
        }
        if (inputTz) {
          // set current browser timezone offset in minutes (getTimezoneOffset)
          try { inputTz.value = String(new Date().getTimezoneOffset()); } catch(e) { inputTz.value = ''; }
        }
        // Update form action to include campaign id
        var form = document.getElementById('scheduleForm');
        if (form && campaignId) {
          var action = form.getAttribute('action') || '';
          // If the action already targets '/schedule' (simple endpoint), keep it as-is
          if (action.endsWith('/schedule')) {
            // no change needed
          } else if (action.indexOf('/0/schedule') !== -1) {
            action = action.replace('/0/schedule', '/' + campaignId + '/schedule');
          } else if (/\/0\//.test(action)) {
            // fallback: replace '/0/' segment
            action = action.replace(/\/0\//, '/' + campaignId + '/');
          } else {
            // last resort: append campaign id at end
            if (!action.endsWith('/')) action += '/';
            action = action + campaignId + '/schedule';
          }
          form.setAttribute('action', action);
        }
      });
    }
  }catch(e){ console.warn(e); }
  // Ensure tz_offset is fresh at submit time in case the user changed system tz after opening modal
  try {
    var scheduleFormEl = document.getElementById('scheduleForm');
    if (scheduleFormEl) {
      scheduleFormEl.addEventListener('submit', function(){
        var inputTz = document.getElementById('tz_offset');
        if (inputTz) {
          try { inputTz.value = String(new Date().getTimezoneOffset()); } catch(e) { /* ignore */ }
        }
      });
    }
  } catch(e){ console.warn(e); }
  // Populate delete modal when opened from an 'Eliminar' button
  try{
    var deleteModal = document.getElementById('deleteModal');
    if (deleteModal) {
      deleteModal.addEventListener('show.bs.modal', function (event) {
        var button = event.relatedTarget;
        if (!button) return;
        var campaignId = button.getAttribute('data-campaign-id');
        var campaignName = button.getAttribute('data-campaign-name') || 'Campaña';
        var inputId = document.getElementById('delete_campaign_id');
        var nameEl = document.getElementById('delete_campaign_name');
        if (inputId) inputId.value = campaignId;
        if (nameEl) nameEl.textContent = campaignName;
        // Update delete form action to include campaign id
        var form = document.getElementById('deleteForm');
        if (form && campaignId) {
          var action = form.getAttribute('action') || '';
          // If action already targets a simple '/.../delete' endpoint (no id), keep it as-is.
          // If it targets '/0/delete' or contains '/0/' placeholder, replace that placeholder.
          // If it targets a numeric id (e.g. '/123/delete') leave as-is.
          var hasZeroDelete = action.indexOf('/0/delete') !== -1;
          var hasZeroSegment = /\/0\//.test(action);
          var hasNumericDelete = /\/\d+\/delete$/.test(action);
          var endsWithDelete = action.endsWith('/delete') || action.endsWith('/delete/');

          if (hasZeroDelete) {
            action = action.replace('/0/delete', '/' + campaignId + '/delete');
          } else if (hasZeroSegment) {
            action = action.replace(/\/0\//, '/' + campaignId + '/');
          } else if (hasNumericDelete) {
            // already points to a specific id, do nothing
          } else if (endsWithDelete) {
            // points to the simple delete endpoint like '/admin/campaigns/delete' — do nothing
          } else {
            // fallback: append campaignId/delete
            if (!action.endsWith('/')) action += '/';
            action = action + campaignId + '/delete';
          }
          form.setAttribute('action', action);
        }
      });
    }
  }catch(e){ console.warn(e); }
})();
