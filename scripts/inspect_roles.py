
import psycopg


def main():
    with psycopg.connect(
        host="localhost",
        port="5432",
        dbname="cdrl",
        user="cdrl_dev",
        password="cdrl_dev_only",
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    rolname,
                    rolsuper,
                    rolcreaterole,
                    rolcreatedb,
                    rolcanlogin
                FROM pg_roles
                WHERE rolname IN (
                    'cdrl_migrator',
                    'cdrl_writer',
                    'cdrl_reader',
                    'cdrl_operator'
                )
                ORDER BY rolname;
            """)

            for row in cur.fetchall():
                print(row)


if __name__ == "__main__":
    main()