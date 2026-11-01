
CREATE INDEX IF NOT EXISTS idx_telemetry_device_timestamp_id
ON telemetry_reading (
    device_id ASC,
    timestamp DESC,
    id DESC
);
