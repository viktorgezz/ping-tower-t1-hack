import requests
import json
import time

# Базовый URL API
BASE_URL = "http://localhost:8000"

def test_parse_url():
    """Тест парсинга URL"""
    print("=== Тест парсинга URL ===")
    
    url = f"{BASE_URL}/api/v1/parse-url"
    data = {
        "url": "https://httpbin.org",
        "max_pages": 5
    }
    
    try:
        response = requests.post(url, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ Успешно! Найдено:")
        print(f"   - Внутренних URL: {result['total_internal_urls']}")
        print(f"   - Медиа-файлов: {result['total_media_urls']}")
        print(f"   - Обработано страниц: {result['visited_pages']}")
        
        # Показываем первые несколько URL
        if result['internal_urls']:
            print("   Первые внутренние URL:")
            for url in result['internal_urls'][:3]:
                print(f"     - {url}")
                
        return result['internal_urls'][:5]  # Возвращаем первые 5 URL для тестирования
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return []

def test_endpoints(urls):
    """Тест тестирования эндпоинтов"""
    print("\n=== Тест тестирования эндпоинтов ===")
    
    if not urls:
        print("❌ Нет URL для тестирования")
        return
    
    url = f"{BASE_URL}/api/v1/test-endpoints"
    data = {
        "urls": urls,
        "max_concurrent": 5,
        "timeout": 10
    }
    
    try:
        response = requests.post(url, json=data, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ Успешно!")
        print(f"   - Протестировано URL: {result['total_urls']}")
        print(f"   - Сообщение: {result['message']}")
        print(f"   - Kafka топик: {result['kafka_topic']}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def test_health():
    """Тест проверки здоровья сервиса"""
    print("=== Тест проверки здоровья ===")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ Сервис здоров: {result['status']}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def test_root():
    """Тест корневого эндпоинта"""
    print("=== Тест корневого эндпоинта ===")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ Сервис доступен: {result['message']}")
        print(f"   Версия: {result['version']}")
        print(f"   Доступные эндпоинты: {list(result['endpoints'].keys())}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    print("🚀 Запуск тестов API...")
    print(f"Базовый URL: {BASE_URL}")
    
    # Проверяем доступность сервиса
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print("✅ Сервис доступен")
    except:
        print("❌ Сервис недоступен. Убедитесь, что он запущен на порту 8000")
        exit(1)
    
    # Запускаем тесты
    test_root()
    test_health()
    
    # Тест парсинга URL
    parsed_urls = test_parse_url()
    
    # Тест тестирования эндпоинтов (используем найденные URL + несколько известных)
    test_urls = parsed_urls + ["https://httpbin.org/get", "https://jsonplaceholder.typicode.com/posts/1"]
    test_endpoints(test_urls)
    
    print("\n🎉 Все тесты завершены!")
