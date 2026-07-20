const ChartUtils = {
  fontColor: '#e5e7eb',
  gridColor: 'rgba(255,255,255,0.08)',
};

function _commonChartOptions() {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: { color: ChartUtils.fontColor },
      },
      tooltip: {
        callbacks: {
          label: (ctx) => {
            const v = ctx.parsed?.y ?? ctx.parsed ?? '';
            if (typeof v === 'number') return `${ctx.label}: ${v}`;
            return `${ctx.label}`;
          }
        }
      }
    },
    scales: {
      x: {
        ticks: { color: ChartUtils.fontColor },
        grid: { color: ChartUtils.gridColor },
      },
      y: {
        ticks: { color: ChartUtils.fontColor },
        grid: { color: ChartUtils.gridColor },
      }
    }
  };
}

function createDoughnutChart(canvasId, dataObj) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return null;

  const labels = Object.keys(dataObj || {});
  const values = labels.map(l => dataObj[l]);

  const palette = ['#60a5fa', '#34d399', '#fbbf24', '#fb7185', '#a78bfa', '#22c55e', '#93c5fd', '#f472b6', '#4ade80'];

  const ctx = canvas.getContext('2d');
  return new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: labels.map((_, i) => palette[i % palette.length]),
        borderColor: 'rgba(0,0,0,0)'
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          labels: { color: ChartUtils.fontColor }
        }
      }
    }
  });
}

function createLineChart(canvasId, pointsArr, label = 'Trend') {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return null;

  const ctx = canvas.getContext('2d');
  const data = pointsArr || [];
  const labels = data.map(p => p.x);
  const values = data.map(p => p.y);

  return new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label,
        data: values,
        borderColor: '#60a5fa',
        backgroundColor: 'rgba(96,165,250,0.15)',
        tension: 0.3,
        pointRadius: 3
      }]
    },
    options: {
      ..._commonChartOptions(),
      plugins: {
        legend: { labels: { color: ChartUtils.fontColor } }
      }
    }
  });
}
