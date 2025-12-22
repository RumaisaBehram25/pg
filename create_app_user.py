import psycopg2
from psycopg2 import sql

POSTGRES_HOST = "localhost"
POSTGRES_PORT = "5432"
POSTGRES_DB = "pharma_db"
POSTGRES_SUPERUSER = "postgres"
POSTGRES_SUPERUSER_PASS = "Messa25@@"

APP_USER = "pharmacy_app"
APP_USER_PASS = "Messa25@@"


def create_app_user():
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        database=POSTGRES_DB,
        user=POSTGRES_SUPERUSER,
        password=POSTGRES_SUPERUSER_PASS
    )
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        cursor.execute(f"SELECT 1 FROM pg_roles WHERE rolname = '{APP_USER}'")
        exists = cursor.fetchone()

        if exists:
            print(f"[OK] User '{APP_USER}' already exists")
        else:
            cursor.execute(sql.SQL("CREATE USER {} WITH PASSWORD {}").format(
                sql.Identifier(APP_USER),
                sql.Literal(APP_USER_PASS)
            ))
            print(f"[OK] Created user '{APP_USER}'")

        cursor.execute(f"GRANT CONNECT ON DATABASE {POSTGRES_DB} TO {APP_USER}")
        cursor.execute(f"GRANT USAGE ON SCHEMA public TO {APP_USER}")
        cursor.execute(f"GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO {APP_USER}")
        cursor.execute(f"GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO {APP_USER}")
        cursor.execute(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO {APP_USER}")
        cursor.execute(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO {APP_USER}")

        print(f"[OK] Granted permissions to '{APP_USER}'")
        print("\nSetup complete! Update your .env file:")
        print(f"DATABASE_URL=postgresql://{APP_USER}:{APP_USER_PASS}@localhost:5432/{POSTGRES_DB}")

    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    create_app_user()

