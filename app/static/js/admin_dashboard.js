// Inicialización del gráfico de actividad en el dashboard de admin
(function(){
  // Intento de leer datos desde el script[type=application/json] inyectado por la plantilla
  var labels = [];
  var messagesData = [];
  var campaignsData = [];
  try {
    var raw = document.getElementById('admin-activity-data')?.textContent || null;
    if (raw) {
      var parsed = JSON.parse(raw);
      labels = parsed.labels || [];
      messagesData = parsed.messages || [];
      campaignsData = parsed.campaigns || [];
    }
  } catch (e) {
    // Fallback a variables globales si existen
    labels = window.activity_labels || [];
    messagesData = window.activity_messages || [];
    campaignsData = window.activity_campaigns || [];
    console.warn('admin_dashboard: no se pudo parsear admin-activity-data, usando globals', e);
  }

  (function(){
    const canvas = document.getElementById('activityChart');
    if(!canvas) return;
    const ctx = canvas.getContext('2d');
    // Evitar re-inicializar si ya existe
    if (canvas._initialized) return;
    canvas._initialized = true;

    new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Mensajes',
            data: messagesData,
            borderColor: '#0d6efd',
            backgroundColor: 'rgba(13,110,253,0.12)',
            tension: 0.3,
            fill: true
          },
          {
            label: 'Campañas',
            data: campaignsData,
            borderColor: '#6c757d',
            backgroundColor: 'rgba(108,117,125,0.08)',
            tension: 0.3,
            fill: true
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
        plugins: { legend: { position: 'top' } }
      }
    });
  })();

})();
