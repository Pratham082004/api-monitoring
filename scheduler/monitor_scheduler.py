from __future__ import annotations

import os
from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler

import config
from services.monitoring_service import run_monitoring_cycle
from services.report_service import generate_daily_report, generate_monthly_report


_scheduler: BackgroundScheduler | None = None


def start_scheduler(app) -> None:
    global _scheduler
    if _scheduler is not None:
        return

    _scheduler = BackgroundScheduler(timezone="UTC")

    def job_wrapper():
        with app.app_context():
            try:
                res = run_monitoring_cycle()
                app.logger.info(f"Monitoring job result: {res}")

                # Daily/monthly report generation hooks
                now = datetime.now(timezone.utc)
                generate_daily_report(now=now)
                generate_monthly_report(now=now)
            except Exception as e:
                app.logger.exception(f"Monitoring scheduler job failed: {e}")

    _scheduler.add_job(job_wrapper, "interval", seconds=config.SCHEDULER_INTERVAL_SECONDS, id="monitoring-job")
    _scheduler.start()


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
