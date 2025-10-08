#!/usr/bin/env python3
"""
Адаптивные запросы к ClickHouse с проверкой существования колонок
"""

import clickhouse_connect
from config import settings

class AdaptiveClickHouseClient:
    def __init__(self):
        self.client = None
        self.available_columns = None
    
    def connect(self):
        """Подключается к ClickHouse"""
        self.client = clickhouse_connect.get_client(
            host=settings.CLICKHOUSE_HOST,
            port=settings.CLICKHOUSE_PORT,
            database=settings.CLICKHOUSE_DATABASE,
            username=settings.CLICKHOUSE_USER,
            password=settings.CLICKHOUSE_PASSWORD
        )
        return self.client
    
    def get_table_columns(self, table_name="checks"):
        """Получает список доступных колонок в таблице"""
        if self.available_columns is not None:
            return self.available_columns
        
        try:
            query = f"DESCRIBE {table_name}"
            result = self.client.query(query)
            self.available_columns = [row[0] for row in result.result_rows]
            return self.available_columns
        except Exception as e:
            print(f"Ошибка при получении структуры таблицы: {e}")
            return []
    
    def build_select_query(self, table_name="checks", where_clause="", limit=100):
        """Строит SELECT запрос только с доступными колонками"""
        columns = self.get_table_columns(table_name)
        
        # Базовые колонки, которые нам нужны
        required_columns = [
            'url', 'timestamp', 'success', 'error', 
            'response_time', 'status_code'
        ]
        
        # Дополнительные колонки, если они есть
        optional_columns = [
            'content_type', 'content_length', 'headers', 
            'is_https', 'redirect_chain', 'ssl_info', 
            'security_headers', 'technology_stack'
        ]
        
        # Выбираем только существующие колонки
        select_columns = []
        for col in required_columns + optional_columns:
            if col in columns:
                select_columns.append(col)
        
        if not select_columns:
            raise Exception("Не найдено ни одной подходящей колонки в таблице")
        
        query = f"SELECT {', '.join(select_columns)} FROM {table_name}"
        
        if where_clause:
            query += f" WHERE {where_clause}"
        
        query += f" ORDER BY timestamp DESC LIMIT {limit}"
        
        return query, select_columns
    
    def get_checks_data(self, url, limit=100):
        """Получает данные проверок для указанного URL"""
        if not self.client:
            self.connect()
        
        try:
            query, columns = self.build_select_query(
                where_clause="url = %(url)s",
                limit=limit
            )
            
            result = self.client.query(query, {'url': url})
            
            # Конвертируем результат в список словарей
            data = []
            for row in result.result_rows:
                record = {}
                for i, col in enumerate(columns):
                    if i < len(row):
                        record[col] = row[i]
                    else:
                        record[col] = None
                data.append(record)
            
            return data, columns
            
        except Exception as e:
            raise Exception(f"Ошибка при получении данных: {e}")

def test_adaptive_query():
    """Тестирует адаптивный запрос"""
    print("🧪 Тестирование адаптивного запроса...")
    
    client = AdaptiveClickHouseClient()
    
    try:
        # Подключаемся
        client.connect()
        print("✅ Подключение к ClickHouse успешно")
        
        # Получаем структуру таблицы
        columns = client.get_table_columns()
        print(f"📋 Доступные колонки: {columns}")
        
        # Тестируем запрос
        data, used_columns = client.get_checks_data("https://example.com", limit=5)
        print(f"✅ Получено {len(data)} записей")
        print(f"📊 Использованные колонки: {used_columns}")
        
        if data:
            print(f"\n🔍 Пример записи:")
            for key, value in data[0].items():
                print(f"  {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    test_adaptive_query()
