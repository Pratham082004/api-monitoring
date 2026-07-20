import logging
import os
from flask import Flask, redirect, url_for

import config
from database.db_connection import init_db
from routes.dashboard_routes import bp_dashboard
from routes.api_routes import bp_api
from routes.monitor_routes import bp_monitor
from routes.monitor_routes import bp_alerts
from routes.dashboard_routes import bp_reports

# Ensure log/report folders exist
os.makedirs(config.LOG_DIR, exist_ok=True)
os.makedirs(config.REPORTS_DIR, exist_ok=True)
os.makedirs(os.path.dirname(config.DB_PATH), exist_ok=True)


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Logging
    app_logger = logging.getLogger("api_monitoring")
    app_logger.setLevel(logging.INFO)

    # Avoid duplicate handlers on reload
    if not app_logger.handlers:
        file_handler = logging.FileHandler(os.path.join(config.LOG_DIR, "monitoring.log"))
        err_handler = logging.FileHandler(os.path.join(config.LOG_DIR, "error.log"))
        file_handler.setLevel(logging.INFO)
        err_handler.setLevel(logging.ERROR)

        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        err_handler.setFormatter(formatter)

        app_logger.addHandler(file_handler)
        app_logger.addHandler(err_handler)

    app.logger = app_logger

    # DB init
    init_db()

    # Register blueprints
    app.register_blueprint(bp_dashboard)
    app.register_blueprint(bp_api, url_prefix="/api")
    app.register_blueprint(bp_monitor, url_prefix="/monitor")
    app.register_blueprint(bp_alerts, url_prefix="/alerts")
    app.register_blueprint(bp_reports, url_prefix="/reports")

    @app.route("/")
    def index():
        return redirect(url_for("dashboard.dashboard"))

    return app


if __name__ == "__main__":
    # Scheduler starts inside scheduler module import to keep separation
    from scheduler.monitor_scheduler import start_scheduler

    flask_app = create_app()

    if config.SCHEDULER_ENABLED:
        start_scheduler(flask_app)

    flask_app.run(host="0.0.0.0", port=5000, debug=True)
