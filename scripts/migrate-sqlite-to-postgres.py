import sqlite3
import psycopg2
from psycopg2.extras import execute_values
import os
from pathlib import Path

# Config
SQLITE_DB = 'data/db/registry.db'  # adjust paths
POSTGRES_HOST = 'localhost'
POSTGRES_DB = 'portfolio'
POSTGRES_USER = 'postgres'
POSTGRES_PASSWORD = 'password'
POSTGRES_PORT = 5432

def migrate_table(cur_sqlite, cur_pg, table_name):
    cur_sqlite.execute(f"SELECT * FROM {table_name}")
    rows = cur_sqlite.fetchall()
    if rows:
        columns = [desc[0] for desc in cur_sqlite.description]
        execute_values(cur_pg, f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join([c + ' TEXT' for c in columns])})", rows)

def main():
    pg_conn = psycopg2.connect(host=POSTGRES_HOST, database=POSTGRES_DB, user=POSTGRES_USER, password=POSTGRES_PASSWORD, port=POSTGRES_PORT)
    pg_cur = pg_conn.cursor()

    sqlite_path = Path(SQLITE_DB)
    if sqlite_path.exists():
        sqlite_conn = sqlite3.connect(sqlite_path)
        sqlite_cur = sqlite_conn.cursor()

        sqlite_cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = sqlite_cur.fetchall()

        for table in tables:
            table_name = table[0]
            migrate_table(sqlite_cur, pg_cur, table_name)
            print(f"Migrated {table_name}")

        sqlite_conn.close()
    pg_conn.commit()
    pg_cur.close()
    pg_conn.close()
    print("Migration complete.")

if __name__ == '__main__':
    main()
