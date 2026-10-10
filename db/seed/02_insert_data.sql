INSERT INTO telemetry_reading (device_id, timestamp, metric, value, unit)
SELECT
    'sensor-001',
    '2026-09-06T10:30:00Z',
    'temperature',
    23.50,
    CHR(176) || 'C'
WHERE NOT EXISTS (
    SELECT 1
    FROM telemetry_reading
    WHERE device_id = 'sensor-001'
      AND timestamp = '2026-09-06T10:30:00Z'::timestamptz
      AND metric = 'temperature'
);