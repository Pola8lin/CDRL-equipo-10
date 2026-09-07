CREATE TABLE IF NOT EXISTS telemetry_reading (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(50) NOT NULL CHECK (TRIM(device_id) <> ''),
    timestamp TIMESTAMPTZ NOT NULL,
    metric VARCHAR(50) NOT NULL CHECK (metric = 'temperature'),
    value NUMERIC(7, 2) NOT NULL CHECK (value >= -50.00 AND value <= 100.00),
    unit VARCHAR(10) NOT NULL CHECK (unit = '°C')
);