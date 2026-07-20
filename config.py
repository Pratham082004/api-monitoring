import os

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "api_monitoring.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")

DATASET_PATH = os.path.join(BASE_DIR, "dataset", "api_monitoring_rich_dataset.csv")

LOG_DIR = os.path.join(BASE_DIR, "logs")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

DAILY_REPORT_PATH = os.path.join(REPORTS_DIR, "daily_report.csv")
MONTHLY_REPORT_PATH = os.path.join(REPORTS_DIR, "monthly_report.csv")

# Monitoring thresholds
STATUS_CODE_CRITICAL = 500
RESPONSE_TIME_HIGH_MS = 3000
DOWNTIME_CRITICAL_MINUTES = 30

# Scheduler
SCHEDULER_ENABLED = True
SCHEDULER_INTERVAL_SECONDS = 60  # how often monitoring job runs

# Email (SMTP)
SMTP_ENABLED = False  # keep off by default
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.example.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USERNAME = os.environ.get("SMTP_USERNAME", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
ALERT_EMAIL_TO = os.environ.get("ALERT_EMAIL_TO", "admin@example.com")
ALERT_EMAIL_FROM = os.environ.get("ALERT_EMAIL_FROM", SMTP_USERNAME or "alerts@example.com")

# Pagination defaults
LOGS_PAGE_SIZE = 10
