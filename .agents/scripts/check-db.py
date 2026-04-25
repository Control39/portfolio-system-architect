#!/usr/bin/env python3
"""
Проверка структуры базы данных мониторинга
"""

import sqlite3
import sys

def main():
    db_path = ".agents/data/trigger_metrics.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Получить все таблицы
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        if not tables:
            print("В базе данных нет таблиц")
            return
        
        print("=" * 60)
        print("СТРУКТУРА БАЗЫ ДАННЫХ МОНИТОРИНГА")
        print("=" * 60)
        
        for table_info in tables:
            table_name = table_info[0]
            print(f"\n📊 Таблица: {table_name}")
            
            # Получить структуру таблицы
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            print("  Колонки:")
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, pk = col
                print(f"    {col_name}: {col_type} {'PRIMARY KEY' if pk else ''}")
            
            # Получить количество записей
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  Количество записей: {count}")
            
            # Показать несколько записей
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 2")
                rows = cursor.fetchall()
                print("  Примеры записей:")
                for i, row in enumerate(rows):
                    print(f"    Запись {i+1}: {row}")
        
        print("\n" + "=" * 60)
        
        # Проверить индексы
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index'")
        indexes = cursor.fetchall()
        
        if indexes:
            print("\n📈 Индексы:")
            for idx_name, idx_sql in indexes:
                print(f"  {idx_name}: {idx_sql}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()