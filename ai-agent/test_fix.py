#!/usr/bin/env python3
"""
Тестирование исправленной версии сервиса
"""

import requests
import json

def test_api():
    """Тестирует API после исправления"""
    base_url = "http://localhost:8001"
    
    print("🧪 Тестирование исправленного API...")
    
    # Тест health check
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"   Статус: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Тест анализа
    test_data = {
        "url": "https://example.com",
        "check_count": 5
    }
    
    try:
        print(f"\n🔍 Тестирование анализа для {test_data['url']}...")
        response = requests.post(f"{base_url}/analyze", json=test_data)
        
        print(f"📊 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Анализ успешен!")
            print(f"   URL: {result['url']}")
            print(f"   Тип анализа: {result['analysis_type']}")
            
            if result['analysis_type'] == 'errors':
                data = result['data']
                print(f"   Ошибки: {len(data.get('errors', []))}")
                if data.get('errors'):
                    print(f"   Первая ошибка: {data['errors'][0]}")
            else:
                data = result['data']
                print(f"   Характеристика: {data.get('general_characteristics', 'N/A')[:100]}...")
            
            return True
        else:
            print(f"❌ Ошибка анализа: {response.status_code}")
            print(f"   Детали: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
        return False

def main():
    print("🔧 Тестирование исправленного сервиса")
    print("=" * 50)
    
    if test_api():
        print(f"\n🎉 Все тесты прошли успешно!")
        print(f"Сервис работает корректно с адаптивными запросами.")
    else:
        print(f"\n❌ Есть проблемы. Проверьте логи сервиса:")
        print(f"docker-compose logs -f")

if __name__ == "__main__":
    main()
