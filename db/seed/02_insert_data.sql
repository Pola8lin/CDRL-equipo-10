TRUNCATE TABLE telemetry_reading RESTART IDENTITY;

INSERT INTO telemetry_reading (device_id, timestamp, metric, value, unit) 
VALUES
('sensor-001', '2026-09-06T10:30:00Z', 'temperature', 23.50, '°C');