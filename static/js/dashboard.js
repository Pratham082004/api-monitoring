async function fetchJSON(url) {
  const res = await fetch(url, { headers: { 'Accept': 'application/json' }});
  if (!res.ok) throw new Error(`HTTP ${res.status} for ${url}`);
  return await res.json();
}

function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value ?? 0;
}

function chartDataLabels(obj) {
  return Object.keys(obj || {});
}

document.addEventListener('DOMContentLoaded', async () => {
  // Dashboard page
  const statusDist = document.getElementById('statusDistChart');
  if (statusDist) {
    try {
      const data = await fetchJSON('/dashboard/api/metrics');

      setText('kpiTotalApis', data.kpis.totalApis);
      setText('kpiHealthyApis', data.kpis.healthyApis);
      setText('kpiFailedApis', data.kpis.failedApis);
      setText('kpiCriticalIncidents', data.kpis.criticalIncidents);
      setText('kpiAvgResponse', data.kpis.avgResponseTimeMs.toFixed ? data.kpis.avgResponseTimeMs.toFixed(2) : data.kpis.avgResponseTimeMs);
      setText('kpiUptime', data.kpis.uptimePct.toFixed ? data.kpis.uptimePct.toFixed(2) : data.kpis.uptimePct);

      // status distribution
      createDoughnutChart('statusDistChart', data.statusDistribution);

      // response trend line
      createLineChart('responseTrendChart', data.responseTimeTrend, 'Response Time (ms)');

      // failure distribution
      createDoughnutChart('failureDistChart', data.failureDistribution);

      // regional performance table
      const tbody = document.querySelector('#regionTable tbody');
      if (tbody) {
        tbody.innerHTML = '';
        (data.regionPerformance || []).forEach(row => {
          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td>${row.region}</td>
            <td>${row.total}</td>
            <td>${(row.avg ?? 0).toFixed ? row.avg.toFixed(2) : row.avg}</td>
            <td>${row.failures}</td>
          `;
          tbody.appendChild(tr);
        });
      }

      document.getElementById('lastUpdated').textContent = `Updated: ${new Date().toLocaleString()}`;
    } catch (e) {
      console.error(e);
      document.getElementById('lastUpdated').textContent = 'Failed to load metrics';
    }
  }

  // Logs page
  if (document.getElementById('logsTable')) {
    const tbody = document.querySelector('#logsTable tbody');
    let page = 1;
    const pageSize = 10;

    async function load() {
      const search = document.getElementById('searchInput')?.value || '';
      const statusCode = document.getElementById('statusCodeInput')?.value || '';
      const region = document.getElementById('regionInput')?.value || '';

      const params = new URLSearchParams({
        page: String(page),
        pageSize: String(pageSize)
      });
      if (search) params.set('search', search);
      if (statusCode) params.set('statusCode', statusCode);
      if (region) params.set('region', region);

      const data = await fetchJSON(`/monitor/logs/data?${params.toString()}`);
      tbody.innerHTML = '';
      (data.rows || []).forEach(r => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${r.Timestamp}</td>
          <td>${r.ApiName || ''}</td>
          <td>${r.EndpointURL || ''}</td>
          <td>${r.StatusCode}</td>
          <td>${r.ResponseTime}</td>
          <td>${r.FailureReason || ''}</td>
          <td>${r.Region || ''}</td>
          <td>${r.IncidentSeverity || ''}</td>
        `;
        tbody.appendChild(tr);
      });

      document.getElementById('pageInfo').textContent = `Page ${page} / ${data.totalPages || 1}`;
      document.getElementById('btnPrev').disabled = page <= 1;
      document.getElementById('btnNext').disabled = page >= (data.totalPages || 1);
    }

    document.getElementById('btnPrev').addEventListener('click', () => { page--; load(); });
    document.getElementById('btnNext').addEventListener('click', () => { page++; load(); });

    document.getElementById('btnApplyFilters').addEventListener('click', () => {
      page = 1;
      load();
    });

    load();
  }

  // Alerts page
  if (document.getElementById('alertsTable')) {
    const tbody = document.querySelector('#alertsTable tbody');

    async function loadAlerts() {
      const data = await fetchJSON('/alerts/data?limit=200');
      tbody.innerHTML = '';
      const empty = document.getElementById('alertsEmpty');
      if (empty) empty.textContent = '';

      const rows = data.rows || [];
      if (!rows.length) {
        if (empty) empty.textContent = 'No alerts yet.';
        return;
      }

      rows.forEach(r => {
        const tr = document.createElement('tr');
        const sevClass = r.Severity === 'critical' ? 'table-danger' :
                          r.Severity === 'high' ? 'table-warning' : '';
        tr.className = sevClass;
        tr.innerHTML = `
          <td>${r.AlertTime}</td>
          <td>${r.AlertType}</td>
          <td>${r.Severity || ''}</td>
          <td>${r.AlertMessage}</td>
          <td>${r.ApiName || ''}</td>
        `;
        tbody.appendChild(tr);
      });
    }

    document.getElementById('btnRefresh').addEventListener('click', loadAlerts);
    loadAlerts();
  }

  // Reports page
  if (document.getElementById('dailyLink')) {
    // links are server-side; enabled state already calculated via template context, but keep JS for future.
  }

});
