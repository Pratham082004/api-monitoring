# API Monitoring System (Flask)

Web-based API monitoring dashboard that tracks API health, response times, status codes, failures, uptime percentage, generates analytical reports, and records alerts.

## Features
- Dashboard with KPI cards + interactive charts (Chart.js)
- API management (CRUD)
- Monitoring logs with search, filtering, pagination
- Alerts (rules: 5xx, high response time, downtime)
- Daily & monthly CSV reports
- Optional SMTP email notifications (disabled by default)

## Tech Stack
- Backend: Python + Flask
- Database: SQLite (development)
- Job Scheduler: APScheduler
- Analytics: pandas, numpy
- Frontend: Bootstrap 5, Chart.js, vanilla JS

## Project Layout
- `app.py` - Flask entrypoint
- `config.py` - configuration (DB path, thresholds, scheduler interval, SMTP)
- `database/` - `schema.sql`, `db_connection.py`
- `models/` - DB access helpers
- `routes/` - Flask blueprints
- `services/` - monitoring + alert + report logic
- `scheduler/` - APScheduler wrapper
- `templates/`, `static/` - UI assets
- `dataset/` - `api_monitoring_rich_dataset.csv` (used to seed + simulate monitoring)
- `reports/` - generated CSV outputs
- `logs/` - log files

## Setup (development)
1. Create/activate a Python environment.
2. Install dependencies:
   
```bash
   pip install -r requirements.txt
   
```
3. Run the server:
   
```bash
   python app.py
   
```
4. Open:
   - http://localhost:5000/dashboard

## Routes
- Dashboard:
  - `GET /dashboard`
  - `GET /dashboard/api/metrics` (dashboard KPIs + charts)
- Regional performance:
  - `GET /dashboard/api/region-performance`
- Downtime analysis:
  - `GET /dashboard/api/downtime`
- API Management:
  - `GET /api/manage` (page)
  - `GET/POST/PUT/DELETE /api/apis` endpoints (JSON)
- Monitoring Logs:
  - `GET /monitor/logs` (page)
  - `GET /monitor/logs/data` (JSON, paginated)
- Alerts:
  - `GET /alerts/` (page)
  - `GET /alerts/data?limit=200` (JSON)
- Reports:
  - `GET /reports/` (page)

## SMTP Alerts (optional)
SMTP is disabled by default.
To enable, set environment variables:
- `SMTP_ENABLED=true` (enable in code if you choose to wire it from env)
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `ALERT_EMAIL_TO`
- `ALERT_EMAIL_FROM`

## Notes
- On startup, DB schema is initialized from `database/schema.sql`.
- The monitoring scheduler periodically runs `run_monitoring_cycle()` and inserts `MonitoringLogs` and `Alerts`.
- If the dataset file is missing, monitoring will still run but logs/alerts won’t be meaningful until APIs are added via API management.
