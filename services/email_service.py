from __future__ import annotations

import smtplib
from email.mime.text import MIMEText

import config


def send_email(subject: str, body: str, to_email: str) -> None:
    if not config.SMTP_ENABLED:
        return

    if not config.SMTP_USERNAME or not config.SMTP_PASSWORD:
        raise RuntimeError("SMTP credentials are missing. Set SMTP_USERNAME and SMTP_PASSWORD env vars.")

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = config.ALERT_EMAIL_FROM
    msg["To"] = to_email

    with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
        server.starttls()
        server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
        server.sendmail(config.ALERT_EMAIL_FROM, [to_email], msg.as_string())
