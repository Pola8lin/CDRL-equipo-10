
import os

import psycopg

from psycopg import sql


def get_connection():
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "cdrl"),
        user=os.getenv("POSTGRES_USER", "cdrl_dev"),
        password=os.getenv("POSTGRES_PASSWORD", "cdrl_dev_only"),
    )


def main():
    users = {
        "cdrl_migrator_login": (
            "cdrl_migrator",
            os.getenv("CDRL_MIGRATOR_PASSWORD"),
        ),
        "cdrl_writer_login": (
            "cdrl_writer",
            os.getenv("CDRL_WRITER_PASSWORD"),
        ),
        "cdrl_reader_login": (
            "cdrl_reader",
            os.getenv("CDRL_READER_PASSWORD"),
        ),
        "cdrl_operator_login": (
            "cdrl_operator",
            os.getenv("CDRL_OPERATOR_PASSWORD"),
        ),
    }

    with get_connection() as conn:
        with conn.cursor() as cur:
            for username, (role, password) in users.items():
                if not password:
                    raise ValueError(
                        f"Falta la contraseña de {username}"
                    )

                cur.execute(
                    "SELECT 1 FROM pg_roles WHERE rolname = %s",
                    (username,),
                )

                exists = cur.fetchone() is not None

                if not exists:
                    cur.execute(
                        sql.SQL(
                            "CREATE ROLE {} LOGIN PASSWORD {}"
                        ).format(
                            sql.Identifier(username),
                            sql.Literal(password),
                        )
                    )
                else:
                    cur.execute(
                        sql.SQL(
                            "ALTER ROLE {} PASSWORD {}"
                        ).format(
                            sql.Identifier(username),
                            sql.Literal(password),
                        )
                    )

                cur.execute(
                    sql.SQL("GRANT {} TO {}").format(
                        sql.Identifier(role),
                        sql.Identifier(username),
                    )
                )

        conn.commit()

    print("Usuarios creados correctamente.")


if __name__ == "__main__":
    main()  