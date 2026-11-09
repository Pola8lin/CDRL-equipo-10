import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from src.database import get_connection


MIGRATION_FILE = ROOT / "db" / "migrations" / "01_create_table.sql"
SECURITY_MIGRATION_FILE = ROOT / "db" / "migrations" / "03_security_roles.sql"
M08_MIGRATION_FILE = ROOT / "db" / "migrations" / "04_m08_pagination_index.sql"
M09_SECURITY_MIGRATION_FILE = ROOT / "db" / "migrations" / "05_m09_security_hardening.sql"
SEED_FILE = ROOT / "db" / "seed" / "02_insert_data.sql"


def execute_sql_file(connection, path):
    sql = path.read_text(encoding="utf-8")
    with connection.cursor() as cursor:
        cursor.execute(sql)
    connection.commit()


def main():
    migrations = (
        ("migracion inicial", MIGRATION_FILE),
        ("roles base", SECURITY_MIGRATION_FILE),
        ("indice de paginacion M08", M08_MIGRATION_FILE),
        ("endurecimiento de permisos M09", M09_SECURITY_MIGRATION_FILE),
        ("datos sinteticos", SEED_FILE),
    )
    for label, path in migrations:
        print(f"Aplicando {label}...")
        with get_connection() as connection:
            execute_sql_file(connection, path)
    print("Base de datos preparada correctamente.")


if __name__ == "__main__":
    main()
