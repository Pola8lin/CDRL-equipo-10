
from datetime import datetime, timedelta, timezone

from src.database import get_connection
from src.database_pagination import get_telemetry_page


DEVICE_ID = "m08-pagination-test"


def test_postgres_pagination_without_duplicates_after_insert():
    # Limpiar posibles datos de una ejecución anterior.
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM telemetry_reading WHERE device_id = %s",
                (DEVICE_ID,),
            )

            # Insertar 7 lecturas sintéticas.
            now = datetime.now(timezone.utc)

            for i in range(7):
                cur.execute(
                    """
                    INSERT INTO telemetry_reading
                    (device_id, timestamp, metric, value, unit)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        DEVICE_ID,
                        now + timedelta(minutes=i),
                        "temperature",
                        20 + i,
                        "°C",
                    ),
                )

    try:
        # Obtener la primera página.
        page1 = get_telemetry_page(DEVICE_ID, page_size=3)

        assert len(page1["items"]) == 3
        assert page1["has_more"] is True
        assert page1["next_cursor"] is not None

        # Insertar una lectura más reciente entre páginas.
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO telemetry_reading
                    (device_id, timestamp, metric, value, unit)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        DEVICE_ID,
                        now + timedelta(days=1),
                        "temperature",
                        25,
                        "°C",
                    ),
                )

        # Continuar usando el cursor anterior.
        page2 = get_telemetry_page(
            DEVICE_ID,
            page_size=3,
            cursor=page1["next_cursor"],
        )

        assert len(page2["items"]) == 3
        assert page2["has_more"] is True

        page3 = get_telemetry_page(
            DEVICE_ID,
            page_size=3,
            cursor=page2["next_cursor"],
        )

        assert len(page3["items"]) == 1
        assert page3["has_more"] is False
        assert page3["next_cursor"] is None

        # Verificar que no existan duplicados.
        all_items = (
            page1["items"]
            + page2["items"]
            + page3["items"]
        )

        ids = [item[0] for item in all_items]

        assert len(ids) == 7
        assert len(set(ids)) == 7
        assert ids == sorted(ids, reverse=True)

        # La nueva lectura no debe aparecer al continuar
        # desde el cursor de la primera página.
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id
                    FROM telemetry_reading
                    WHERE device_id = %s
                      AND timestamp = %s
                    """,
                    (DEVICE_ID, now + timedelta(days=1)),
                )
                inserted_id = cur.fetchone()[0]

        assert inserted_id not in ids

    finally:
        # Eliminar exclusivamente los registros sintéticos.
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM telemetry_reading WHERE device_id = %s",
                    (DEVICE_ID,),
                )
