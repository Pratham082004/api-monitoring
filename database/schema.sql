-- SQLite schema for API Monitoring System

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS APIs (
    ApiID INTEGER PRIMARY KEY AUTOINCREMENT,
    ApiName TEXT NOT NULL,
    EndpointURL TEXT NOT NULL,
    Status TEXT NOT NULL DEFAULT 'active',
    CreatedAt TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS MonitoringLogs (
    LogID INTEGER PRIMARY KEY AUTOINCREMENT,
    ApiID INTEGER NOT NULL,
    Timestamp TEXT NOT NULL,
    StatusCode INTEGER NOT NULL,
    ResponseTime REAL NOT NULL,
    FailureReason TEXT,
    Region TEXT,
    IncidentSeverity TEXT,
    FOREIGN KEY (ApiID) REFERENCES APIs(ApiID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Alerts (
    AlertID INTEGER PRIMARY KEY AUTOINCREMENT,
    ApiID INTEGER NOT NULL,
    AlertType TEXT NOT NULL,
    AlertMessage TEXT NOT NULL,
    AlertTime TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (ApiID) REFERENCES APIs(ApiID) ON DELETE CASCADE
);

-- Helpful indexes
CREATE INDEX IF NOT EXISTS idx_monitoringlogs_apiid_ts ON MonitoringLogs(ApiID, Timestamp);
CREATE INDEX IF NOT EXISTS idx_monitoringlogs_statuscode ON MonitoringLogs(StatusCode);
CREATE INDEX IF NOT EXISTS idx_alerts_apiid_time ON Alerts(ApiID, AlertTime);
