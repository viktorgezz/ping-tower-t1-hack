#!/usr/bin/env python3
"""
Тестирование API с реальными данными
"""

import requests
import json

def test_api_with_real_data():
    """Тестирует API с реальными URL из ClickHouse"""
    base_url = "http://localhost:8001"
    
    print("🧪 Тестирование API с реальными данными...")
    
    # URL из тестовых данных
    test_urls = [
        "https://example.com",
        "https://api.example.com", 
        "http://blog.example.com",
        "https://shop.example.com"
    ]
    
    for url in test_urls:
        print(f"\n🔍 Тестирование URL: {url}")
        print("-" * 50)
        
        try:
            # Тест анализа
            response = requests.post(f"{base_url}/analyze", json={
                "url": url,
                "check_count": 10
            })
            
            print(f"📊 Статус ответа: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Анализ успешен!")
                print(f"   Тип анализа: {result['analysis_type']}")
                
                if result['analysis_type'] == 'errors':
                    data = result['data']
                    errors = data.get('errors', [])
                    print(f"   Количество ошибок: {len(errors)}")
                    if errors:
                        print(f"   Первая ошибка: {errors[0]}")
                    
                    print(f"   Анализ: {data.get('error_analysis', 'N/A')[:100]}...")
                    print(f"   Рекомендации: {data.get('recommendations', 'N/A')[:100]}...")
                
                else:
                    data = result['data']
                    print(f"   Характеристика: {data.get('general_characteristics', 'N/A')[:100]}...")
                
            else:
                print(f"❌ Ошибка: {response.status_code}")
                print(f"   Детали: {response.text}")
                
        except Exception as e:
            print(f"❌ Ошибка запроса: {e}")
    
    # Тест health check
    print(f"\n🏥 Проверка здоровья сервиса...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   Статус: {response.status_code}")
        if response.status_code == 200:
            health = response.json()
            print(f"   ClickHouse: {health.get('clickhouse', 'unknown')}")
    except Exception as e:
        print(f"   Ошибка: {e}")

def main():
    print("🔧 Тестирование API с реальными данными ClickHouse")
    print("=" * 60)
    
    test_api_with_real_data()
    
    print(f"\n✅ Тестирование завершено!")
    print(f"Если все тесты прошли успешно, API готов к работе.")

if __name__ == "__main__":
    main()
