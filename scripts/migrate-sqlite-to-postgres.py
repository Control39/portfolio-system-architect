import sqlite3
import psycopg2
from psycopg2.extras import execute_values
from psycopg2 import sql
import os
from pathlib import Path
import re

# Config
SQLITE_DB = os.environ.get('SQLITE_DB', 'data/db/registry.db')
POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
POSTGRES_DB = os.environ.get('POSTGRES_DB', 'portfolio')
POSTGRES_USER = os.environ.get('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
POSTGRES_PORT = int(os.environ.get('POSTGRES_PORT', 5432))

# Требуется установка POSTGRES_PASSWORD через переменную окружения
if not POSTGRES_PASSWORD:
    raise RuntimeError("POSTGRES_PASSWORD environment variable is required")

def is_valid_table_name(table_name):
    """Проверить, что имя таблицы состоит только из букв, цифр и подчеркиваний"""
    # Дополнительная проверка длины имени таблицы
    if len(table_name) > 63:  # Максимальная длина имени таблицы в PostgreSQL
        return False
    return re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table_name) is not None

def migrate_table(cur_sqlite, cur_pg, table_name):
    """Мигрировать таблицу из SQLite в PostgreSQL"""
    # Валидировать имя таблицы
    if not is_valid_table_name(table_name):
        raise ValueError(f"Invalid table name: {table_name}")
    
    # Использовать параметризованный запрос для выбора данных
    # Для SELECT * FROM table_name используем проверенное имя таблицы
    # Так как имя таблицы уже прошло валидацию, можно безопасно использовать форматирование
    cur_sqlite.execute(f"SELECT * FROM {table_name}")
    rows = cur_sqlite.fetchall()
    if rows:
        columns = [desc[0] for desc in cur_sqlite.description]
        # Валидировать имена колонок
        for col in columns:
            if not is_valid_table_name(col):
                raise ValueError(f"Invalid column name: {col}")
        
        # Создать таблицу в PostgreSQL с валидированными именами
        columns_def = ', '.join([f'{c} TEXT' for c in columns])
        create_table_query = sql.SQL("CREATE TABLE IF NOT EXISTS {} ({})").format(
            sql.Identifier(table_name),
            sql.SQL(columns_def)
        )
        cur_pg.execute(create_table_query)
        
        # Вставить данные
        # execute_values автоматически экранирует значения
        if rows:
            execute_values(cur_pg, f"INSERT INTO {table_name} VALUES %s", rows)

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
            # Валидировать имя таблицы перед миграцией
            if is_valid_table_name(table_name):
                migrate_table(sqlite_cur, pg_cur, table_name)
                print(f"Migrated {table_name}")
            else:
                print(f"Skipping invalid table name: {table_name}")

        sqlite_conn.close()
    pg_conn.commit()
    pg_cur.close()
    pg_conn.close()
    print("Migration complete.")

if __name__ == '__main__':
    main()