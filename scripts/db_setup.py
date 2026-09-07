import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.database import get_connection


MIGRATION_FILE = ROOT / "db" / "migrations" / "01_create_table.sql"
SEED_FILE = ROOT / "db" / "seed" / "02_insert_data.sql"


def execute_sql_file(connection, path):
    sql = path.read_text(encoding="utf-8")

    with connection.cursor() as cursor:
        cursor.execute(sql)

    connection.commit()


def main():
    print("Aplicando migración...")
    with get_connection() as connection:
        execute_sql_file(connection, MIGRATION_FILE)

    print("Aplicando seed...")
    with get_connection() as connection:
        execute_sql_file(connection, SEED_FILE)

    print("Base de datos preparada correctamente.")


if __name__ == "__main__":
    main()