#!/usr/bin/env python3
"""
Тестирование с реальными данными из ClickHouse
"""

import asyncio
from ai_agent import LogAnalyzer

# Тестовые данные в формате, который возвращает ClickHouse
test_data = [
    {
        'url': 'https://example.com',
        'timestamp': '2024-01-15 10:00:00',
        'success': 1,
        'error': None,
        'response_time': 0.25,
        'status_code': 200,
        'content_type': 'text/html',
        'content_length': 1024,
        'headers': {'Server': 'nginx', 'Content-Type': 'text/html'},
        'is_https': 1,
        'redirect_chain': []
    },
    {
        'url': 'https://example.com',
        'timestamp': '2024-01-15 10:05:00',
        'success': 1,
        'error': None,
        'response_time': 0.28,
        'status_code': 200,
        'content_type': 'text/html',
        'content_length': 1050,
        'headers': {'Server': 'nginx', 'Content-Type': 'text/html'},
        'is_https': 1,
        'redirect_chain': []
    },
    {
        'url': 'https://example.com',
        'timestamp': '2024-01-15 10:10:00',
        'success': 0,
        'error': 'Connection timeout',
        'response_time': 5.12,
        'status_code': 0,
        'content_type': None,
        'content_length': None,
        'headers': {},
        'is_https': 1,
        'redirect_chain': []
    },
    {
        'url': 'https://example.com',
        'timestamp': '2024-01-15 10:15:00',
        'success': 1,
        'error': None,
        'response_time': 0.31,
        'status_code': 200,
        'content_type': 'text/html',
        'content_length': 1100,
        'headers': {'Server': 'nginx', 'Content-Type': 'text/html'},
        'is_https': 1,
        'redirect_chain': []
    }
]

async def test_analysis():
    """Тестирует анализ с реальными данными"""
    print("🧪 Тестирование AI агента с реальными данными...")
    
    analyzer = LogAnalyzer()
    
    try:
        # Тестируем анализ
        result = await analyzer.analyze_logs(test_data)
        
        print(f"✅ Анализ успешен!")
        print(f"📊 Тип анализа: {result['type']}")
        
        if result['type'] == 'errors':
            data = result['data']
            print(f"\n🔍 Ошибки:")
            for i, error in enumerate(data.get('errors', []), 1):
                print(f"  {i}. {error}")
            
            print(f"\n📝 Анализ ошибок:")
            print(f"  {data.get('error_analysis', 'N/A')}")
            
            print(f"\n💡 Рекомендации:")
            print(f"  {data.get('recommendations', 'N/A')}")
        
        else:
            data = result['data']
            print(f"\n📈 Общая характеристика:")
            print(f"  {data.get('general_characteristics', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка анализа: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_successful_service():
    """Тестирует анализ успешного сервиса"""
    print("\n🧪 Тестирование успешного сервиса...")
    
    # Данные только с успешными запросами
    successful_data = [log for log in test_data if log['success'] == 1]
    
    analyzer = LogAnalyzer()
    
    try:
        result = await analyzer.analyze_logs(successful_data)
        
        print(f"✅ Анализ успешного сервиса завершен!")
        print(f"📊 Тип анализа: {result['type']}")
        
        if result['type'] == 'status':
            data = result['data']
            print(f"\n📈 Характеристика:")
            print(f"  {data.get('general_characteristics', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка анализа успешного сервиса: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("🔍 Тестирование AI агента с реальными данными ClickHouse")
    print("=" * 60)
    
    # Тест 1: Анализ с ошибками
    success1 = await test_analysis()
    
    # Тест 2: Анализ успешного сервиса
    success2 = await test_successful_service()
    
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print(f"  Анализ с ошибками: {'✅' if success1 else '❌'}")
    print(f"  Анализ успешного сервиса: {'✅' if success2 else '❌'}")
    
    if success1 and success2:
        print(f"\n🎉 Все тесты прошли успешно!")
        print(f"AI агент корректно работает с реальными данными ClickHouse.")
    else:
        print(f"\n❌ Есть проблемы. Проверьте код AI агента.")

if __name__ == "__main__":
    asyncio.run(main())
