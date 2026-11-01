import json
import math
import platform
import sys
import time
import uuid

from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT))

load_dotenv(ROOT / ".env")

from src.database import get_connection


# Configuración reproducible
ROW_COUNT = 10_000
PAGE_SIZE = 50
PAGE_OFFSET = 9_000
SAMPLES = 100
WARMUPS = 10

INDEX_NAME = "idx_telemetry_device_timestamp_id"


def percentile(values, percent):
    ordered = sorted(values)
    position = math.ceil((percent / 100) * len(ordered)) - 1
    return round(ordered[position], 4)


def measure_query(connection, query, params):
    start = time.perf_counter_ns()

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()

    elapsed_ms = (time.perf_counter_ns() - start) / 1_000_000

    return elapsed_ms, rows


def summarize(values):
    return {
        "p50_ms": percentile(values, 50),
        "p95_ms": percentile(values, 95),
        "min_ms": round(min(values), 4),
        "max_ms": round(max(values), 4),
        "sample_count": len(values),
    }


def main():
    device_id = f"m08-benchmark-{uuid.uuid4().hex}"

    offset_query = """
        SELECT id, device_id, timestamp, metric, value, unit
        FROM telemetry_reading
        WHERE device_id = %s
        ORDER BY timestamp DESC, id DESC
        LIMIT %s OFFSET %s
    """

    keyset_query = """
        SELECT id, device_id, timestamp, metric, value, unit
        FROM telemetry_reading
        WHERE device_id = %s
          AND (timestamp, id) < (%s, %s)
        ORDER BY timestamp DESC, id DESC
        LIMIT %s
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version()")
            database_version = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM pg_indexes
                    WHERE tablename = 'telemetry_reading'
                      AND indexname = %s
                )
                """,
                (INDEX_NAME,),
            )

            if not cursor.fetchone()[0]:
                raise RuntimeError("No se encontró el índice M08.")

            print("Preparando datos sintéticos...")

            base_time = datetime.now(timezone.utc)

            cursor.execute(
                """
                INSERT INTO telemetry_reading
                    (device_id, timestamp, metric, value, unit)
                SELECT
                    %s,
                    %s + (n * INTERVAL '1 second'),
                    'temperature',
                    20 + MOD(n, 30),
                    '°C'
                FROM generate_series(1, %s) AS n
                """,
                (device_id, base_time, ROW_COUNT),
            )

        connection.commit()

        print(f"Registros sintéticos insertados: {ROW_COUNT}")

        # Obtener el registro anterior a la página que compararemos.
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT timestamp, id
                FROM telemetry_reading
                WHERE device_id = %s
                ORDER BY timestamp DESC, id DESC
                LIMIT 1 OFFSET %s
                """,
                (device_id, PAGE_OFFSET - 1),
            )

            anchor = cursor.fetchone()

        if anchor is None:
            raise RuntimeError("No se pudo obtener el cursor de referencia.")

        anchor_timestamp, anchor_id = anchor

        offset_params = (device_id, PAGE_SIZE, PAGE_OFFSET)
        keyset_params = (
            device_id,
            anchor_timestamp,
            anchor_id,
            PAGE_SIZE,
        )

        # Comprobar que ambas estrategias devuelven la misma página.
        _, offset_rows = measure_query(
            connection, offset_query, offset_params
        )

        _, keyset_rows = measure_query(
            connection, keyset_query, keyset_params
        )

        if offset_rows != keyset_rows:
            raise RuntimeError(
                "OFFSET y KEYSET no devolvieron los mismos registros."
            )

        print("Verificación de resultados: correcta.")
        print("Iniciando calentamiento...")

        for _ in range(WARMUPS):
            measure_query(connection, offset_query, offset_params)
            measure_query(connection, keyset_query, keyset_params)

        offset_times = []
        keyset_times = []

        print("Ejecutando mediciones...")

        # Alternar el orden para reducir sesgos por orden de ejecución.
        for sample in range(SAMPLES):
            if sample % 2 == 0:
                elapsed, _ = measure_query(
                    connection, offset_query, offset_params
                )
                offset_times.append(elapsed)

                elapsed, _ = measure_query(
                    connection, keyset_query, keyset_params
                )
                keyset_times.append(elapsed)
            else:
                elapsed, _ = measure_query(
                    connection, keyset_query, keyset_params
                )
                keyset_times.append(elapsed)

                elapsed, _ = measure_query(
                    connection, offset_query, offset_params
                )
                offset_times.append(elapsed)

        results = {
            "benchmark": "M08 PostgreSQL pagination",
            "generated_at_utc": datetime.now(
                timezone.utc
            ).isoformat(),
            "environment": {
                "python": sys.version.split()[0],
                "platform": platform.platform(),
                "database": database_version,
            },
            "dataset": {
                "synthetic_records": ROW_COUNT,
                "page_size": PAGE_SIZE,
                "page_offset": PAGE_OFFSET,
                "device_id": device_id,
            },
            "configuration": {
                "index": INDEX_NAME,
                "warmup_runs_per_strategy": WARMUPS,
                "samples_per_strategy": SAMPLES,
                "comparison_results_equal": True,
            },
            "offset": summarize(offset_times),
            "keyset": summarize(keyset_times),
            "limitations": [
                "Medición realizada en PostgreSQL local.",
                "No representa resultados de Firestore.",
                "Los tiempos dependen del entorno de ejecución.",
                "La comparación corresponde a una página profunda "
                "y a un conjunto sintético controlado.",
            ],
        }

    finally:
        # Eliminar solamente los datos creados por esta ejecución.
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM telemetry_reading WHERE device_id = %s",
                (device_id,),
            )

        connection.commit()
        connection.close()

        print("Datos sintéticos eliminados.")

    output_dir = ROOT / "artifacts"
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "m08-benchmark-results.json"

    output_file.write_text(
        json.dumps(results, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )

    print("\nRESULTADOS DEL BENCHMARK")
    print("========================")
    print("OFFSET:", results["offset"])
    print("KEYSET:", results["keyset"])
    print(f"\nArchivo generado: {output_file}")


if __name__ == "__main__":
    main()