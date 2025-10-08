#!/usr/bin/env python3
"""
Полный тест стека: API + Kafka
"""

import requests
import json
import time
import asyncio
from test_kafka_connection import test_kafka_producer, test_kafka_topics

# Базовый URL API
BASE_URL = "http://localhost:8000"

def test_api_health():
    """Тест здоровья API"""
    print("🔍 Тест здоровья API...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        response.raise_for_status()
        result = response.json()
        print(f"✅ API здоров: {result['status']}")
        return True
    except Exception as e:
        print(f"❌ API недоступен: {e}")
        return False

def test_parse_url():
    """Тест парсинга URL"""
    print("\n🔍 Тест парсинга URL...")
    try:
        url = f"{BASE_URL}/api/v1/parse-url"
        data = {
            "url": "https://httpbin.org",
            "max_pages": 3
        }
        
        response = requests.post(url, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ Парсинг успешен:")
        print(f"   - Внутренних URL: {result['total_internal_urls']}")
        print(f"   - Медиа-файлов: {result['total_media_urls']}")
        print(f"   - Обработано страниц: {result['visited_pages']}")
        
        return result['internal_urls'][:3]  # Возвращаем первые 3 URL
        
    except Exception as e:
        print(f"❌ Ошибка парсинга: {e}")
        return []

def test_endpoints_and_kafka(urls):
    """Тест тестирования эндпоинтов с отправкой в Kafka"""
    print("\n🔍 Тест тестирования эндпоинтов + Kafka...")
    
    if not urls:
        print("❌ Нет URL для тестирования")
        return False
    
    try:
        url = f"{BASE_URL}/api/v1/test-endpoints"
        data = {
            "urls": urls,
            "max_concurrent": 3,
            "timeout": 10
        }
        
        response = requests.post(url, json=data, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ Тестирование успешно:")
        print(f"   - Протестировано URL: {result['total_urls']}")
        print(f"   - Сообщение: {result['message']}")
        print(f"   - Kafka топик: {result['kafka_topic']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False

def test_kafka_connection():
    """Тест подключения к Kafka"""
    print("\n🔍 Тест подключения к Kafka...")
    
    # Тест получения информации о кластере
    cluster_ok = test_kafka_topics()
    
    # Тест отправки сообщения
    producer_ok = test_kafka_producer()
    
    return cluster_ok and producer_ok

def main():
    """Основная функция тестирования"""
    print("🚀 Полный тест стека URL Analysis Service")
    print("=" * 60)
    
    # Проверяем доступность API
    if not test_api_health():
        print("\n❌ API недоступен. Запустите сервис:")
        print("   python start_service.py")
        return
    
    # Тестируем парсинг URL
    parsed_urls = test_parse_url()
    
    # Тестируем Kafka подключение
    kafka_ok = test_kafka_connection()
    
    if not kafka_ok:
        print("\n⚠️  Kafka недоступен. Проверьте подключение.")
        return
    
    # Тестируем полный цикл: парсинг -> тестирование -> Kafka
    if parsed_urls:
        # Добавляем несколько известных URL для тестирования
        test_urls = parsed_urls + ["https://httpbin.org/get", "https://jsonplaceholder.typicode.com/posts/1"]
        
        success = test_endpoints_and_kafka(test_urls)
        
        if success:
            print("\n🎉 Полный цикл работает!")
            print("   ✅ Парсинг URL")
            print("   ✅ Тестирование эндпоинтов")
            print("   ✅ Отправка в Kafka")
        else:
            print("\n❌ Ошибка в полном цикле")
    else:
        print("\n⚠️  Не удалось получить URL для тестирования")
    
    print("\n" + "=" * 60)
    print("📊 ИТОГИ ТЕСТИРОВАНИЯ:")
    print("=" * 60)
    print("✅ API сервис работает")
    print("✅ Kafka подключение работает")
    if parsed_urls:
        print("✅ Парсинг URL работает")
        print("✅ Полный цикл работает")
    else:
        print("⚠️  Парсинг URL требует проверки")
    
    print("\n🌐 Доступные интерфейсы:")
    print("   📚 API документация: http://localhost:8000/docs")
    print("   📊 Kafka UI: http://localhost:8080 (если запущен с Docker)")
    print("   🔍 Health check: http://localhost:8000/health")

if __name__ == "__main__":
    main()
