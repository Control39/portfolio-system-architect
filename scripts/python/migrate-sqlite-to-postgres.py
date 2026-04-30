import logging
import os
import re
import sqlite3
from pathlib import Path

import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values

# Config
SQLITE_DB = os.environ.get("SQLITE_DB", "data/db/registry.db")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
POSTGRES_DB = os.environ.get("POSTGRES_DB", "portfolio")
POSTGRES_USER = os.environ.get("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_PORT = int(os.environ.get("POSTGRES_PORT", 5432))

# Требуется установка POSTGRES_PASSWORD через переменную окружения
if not POSTGRES_PASSWORD:
    raise RuntimeError("POSTGRES_PASSWORD environment variable is required")

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("migration.log", mode="a", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def is_valid_table_name(table_name):
    """Проверить, что имя таблицы состоит только из букв, цифр и подчеркиваний"""
    # Дополнительная проверка длины имени таблицы
    if len(table_name) > 63:  # Максимальная длина имени таблицы в PostgreSQL
        return False
    return re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", table_name) is not None


def is_valid_column_name(column_name):
    """Проверить, что имя колонки состоит только из букв, цифр и подчеркиваний"""
    # В PostgreSQL имена колонок имеют те же ограничения, что и имена таблиц
    # но для семантической ясности создаем отдельную функцию
    if len(column_name) > 63:  # Максимальная длина имени колонки в PostgreSQL
        return False
    return re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", column_name) is not None


def migrate_table(cur_sqlite, cur_pg, table_name):
    """Мигрировать таблицу из SQLite в PostgreSQL"""
    # Валидировать имя таблицы
    if not is_valid_table_name(table_name):
        raise ValueError(f"Invalid table name: {table_name}")

    # Использовать безопасный SQL запрос для выбора данных
    # Используем psycopg2.sql для безопасного построения запроса
    select_query = sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name))
    # SQLite не поддерживает psycopg2.sql, поэтому преобразуем в строку после валидации
    # Имя таблицы уже валидировано, но для безопасности используем безопасный подход
    cur_sqlite.execute(str(select_query))
    rows = cur_sqlite.fetchall()

    if rows:
        columns = [desc[0] for desc in cur_sqlite.description]
        # Валидировать имена колонок
        for col in columns:
            if not is_valid_column_name(col):
                raise ValueError(f"Invalid column name: {col}")

        # Создать таблицу в PostgreSQL с валидированными именами
        columns_def = ", ".join([f"{c} TEXT" for c in columns])
        create_table_query = sql.SQL("CREATE TABLE IF NOT EXISTS {} ({})").format(
            sql.Identifier(table_name),
            sql.SQL(columns_def),
        )
        cur_pg.execute(create_table_query)

        # Вставить данные
        # Используем безопасный SQL запрос с psycopg2.sql
        # execute_values автоматически экранирует значения
        try:
            insert_query = sql.SQL("INSERT INTO {} VALUES %s").format(
                sql.Identifier(table_name),
            )
            execute_values(cur_pg, insert_query, rows)
        except psycopg2.Error as e:
            logger.error(
                f"Ошибка PostgreSQL при вставке данных в таблицу {table_name}: {e}",
            )
            raise


def main():
    pg_conn = None
    pg_cur = None
    sqlite_conn = None
    sqlite_cur = None

    try:
        pg_conn = psycopg2.connect(
            host=POSTGRES_HOST,
            database=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            port=POSTGRES_PORT,
        )
        pg_cur = pg_conn.cursor()
        logger.info("Успешное подключение к PostgreSQL")
    except psycopg2.OperationalError as e:
        logger.error(f"Ошибка подключения к PostgreSQL: {e}")
        return 1

    sqlite_path = Path(SQLITE_DB)
    if sqlite_path.exists():
        try:
            sqlite_conn = sqlite3.connect(sqlite_path)
            sqlite_cur = sqlite_conn.cursor()
            logger.info(f"Успешное подключение к SQLite: {sqlite_path}")
        except sqlite3.Error as e:
            logger.error(f"Ошибка подключения к SQLite {sqlite_path}: {e}")
            return 1
    else:
        logger.error(f"Файл SQLite базы данных не найден: {sqlite_path}")
        return 1

    try:
        sqlite_cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = sqlite_cur.fetchall()

        for table in tables:
            table_name = table[0]
            # Валидировать имя таблицы перед миграцией
            if is_valid_table_name(table_name):
                migrate_table(sqlite_cur, pg_cur, table_name)
                logger.info(f"Миграция таблицы завершена: {table_name}")
            else:
                logger.warning(f"Пропущено недопустимое имя таблицы: {table_name}")

        sqlite_conn.close()
        logger.info("Соединение с SQLite закрыто")

        # Фиксация транзакции и закрытие соединений
        pg_conn.commit()
        logger.info("Транзакция в PostgreSQL зафиксирована")

        if pg_cur:
            pg_cur.close()
            logger.info("Курсор PostgreSQL закрыт")

        if pg_conn:
            pg_conn.close()
            logger.info("Соединение с PostgreSQL закрыто")

        logger.info("Миграция завершена успешно")
        return 0  # Успешное завершение

    except Exception as e:
        logger.error(f"Неожиданная ошибка во время миграции: {e}")

        # Закрытие соединений в случае ошибки
        if sqlite_conn:
            sqlite_conn.close()
            logger.info("Соединение с SQLite закрыто после ошибки")

        if pg_conn:
            pg_conn.rollback()
            logger.info("Транзакция в PostgreSQL отменена")

            if pg_cur:
                pg_cur.close()

            pg_conn.close()
            logger.info("Соединение с PostgreSQL закрыто после ошибки")

        return 1  # Завершение с ошибкой

    finally:
        # Дополнительная проверка закрытия соединений
        if sqlite_conn and sqlite_conn.closed == 0:
            sqlite_conn.close()
            logger.info("Соединение с SQLite принудительно закрыто в блоке finally")

        if pg_conn and not pg_conn.closed:
            pg_conn.close()
            logger.info("Соединение с PostgreSQL принудительно закрыто в блоке finally")


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
