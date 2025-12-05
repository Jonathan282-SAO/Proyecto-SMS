// JS para inicializar canvas de reportes si Chart.js está presente
(function(){
  (function(){
    const canvas = document.getElementById('reportsChart');
    if (!canvas) return;
    if (!window.Chart) {
      // Chart.js no está cargado: no hacemos nada pero evitamos errores
      return;
    }

    // Datos proporcionados por plantilla: preferimos leer un <script type="application/json" id="reports-data"> con JSON.
    let data = { labels: [], messages: [], campaigns: [] };
    try {
      const el = document.getElementById('reports-data');
      if (el && el.textContent) {
        data = JSON.parse(el.textContent || '{}') || data;
      } else if (window.REPORTS_DATA) {
        data = window.REPORTS_DATA;
      }
    } catch (err) {
      console.warn('No se pudo parsear reports-data JSON, usando valores por defecto', err);
    }

    const ctx = canvas.getContext('2d');
    const chartData = {
      labels: data.labels || [],
      datasets: [
        {
          label: 'Mensajes',
          data: data.messages || [],
          borderColor: 'rgba(54, 162, 235, 1)',
          backgroundColor: 'rgba(54, 162, 235, 0.2)',
          fill: true,
          tension: 0.25
        },
        {
          label: 'Campañas',
          data: data.campaigns || [],
          borderColor: 'rgba(75, 192, 192, 1)',
          backgroundColor: 'rgba(75, 192, 192, 0.15)',
          fill: true,
          tension: 0.25
        }
      ]
    };

    const config = {
      type: 'line',
      data: chartData,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: true, position: 'bottom' }
        },
        scales: {
          x: { display: true },
          y: { beginAtZero: true }
        }
      }
    };

    try {
      new Chart(ctx, config);
    } catch (e) {
      // Evitar errores en navegadores antiguos o si config falla
      console.error('No se pudo inicializar el gráfico de reportes', e);
    }
  })();
})();
