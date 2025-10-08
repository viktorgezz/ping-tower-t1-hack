#!/usr/bin/env python3
"""
Скрипт для проверки структуры таблицы checks в ClickHouse
"""

import clickhouse_connect
from config import settings

def check_table_structure():
    """Проверяет структуру таблицы checks"""
    try:
        print("🔍 Проверка структуры таблицы checks...")
        
        client = clickhouse_connect.get_client(
            host=settings.CLICKHOUSE_HOST,
            port=settings.CLICKHOUSE_PORT,
            database=settings.CLICKHOUSE_DATABASE,
            username=settings.CLICKHOUSE_USER,
            password=settings.CLICKHOUSE_PASSWORD
        )
        
        # Проверяем существование таблицы
        tables_query = "SHOW TABLES"
        tables_result = client.query(tables_query)
        tables = [row[0] for row in tables_result.result_rows]
        
        print(f"📋 Существующие таблицы: {tables}")
        
        if 'checks' not in tables:
            print("❌ Таблица 'checks' не найдена!")
            return False
        
        # Получаем структуру таблицы
        structure_query = "DESCRIBE checks"
        structure_result = client.query(structure_query)
        
        print(f"\n📊 Структура таблицы 'checks':")
        print("-" * 50)
        for row in structure_result.result_rows:
            print(f"  {row[0]:<20} | {row[1]:<15} | {row[2] if len(row) > 2 else ''}")
        
        # Проверяем количество записей
        count_query = "SELECT COUNT(*) as total FROM checks"
        count_result = client.query(count_query)
        total_records = count_result.result_rows[0][0]
        print(f"\n📈 Всего записей в таблице: {total_records}")
        
        # Показываем пример записи
        if total_records > 0:
            sample_query = "SELECT * FROM checks LIMIT 1"
            sample_result = client.query(sample_query)
            
            print(f"\n🔍 Пример записи:")
            print("-" * 50)
            columns = [col[0] for col in sample_result.column_names]
            sample_row = sample_result.result_rows[0]
            
            for i, col in enumerate(columns):
                value = sample_row[i] if i < len(sample_row) else "N/A"
                print(f"  {col:<20} | {str(value)[:50]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def main():
    print("🔍 Проверка структуры таблицы ClickHouse")
    print("=" * 50)
    
    if check_table_structure():
        print(f"\n✅ Проверка завершена успешно!")
    else:
        print(f"\n❌ Ошибка при проверке структуры таблицы")

if __name__ == "__main__":
    main()
