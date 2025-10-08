#!/usr/bin/env python3
"""
Тестовый скрипт для проверки интеграции Telegram уведомлений
"""

import asyncio
import sys
import os
from telegram_service import telegram_service
from endpoint_tester import EndpointTester

async def test_telegram_notifications():
    """Тестирует различные типы Telegram уведомлений"""
    
    print("🧪 Тестирование Telegram уведомлений...")
    
    # Тест 1: Простое сообщение
    print("\n1. Тестирование простого сообщения...")
    success = telegram_service.send_message("🧪 Тестовое сообщение от URL Analysis Service")
    print(f"   Результат: {'✅ Успешно' if success else '❌ Ошибка'}")
    
    # Тест 2: Уведомление об ошибке эндпоинта
    print("\n2. Тестирование уведомления об ошибке эндпоинта...")
    success = telegram_service.send_error_notification(
        url="https://httpstat.us/500",
        status_code=500,
        error_message="Тестовая ошибка 500"
    )
    print(f"   Результат: {'✅ Успешно' if success else '❌ Ошибка'}")
    
    # Тест 3: Уведомление об ошибке сервиса
    print("\n3. Тестирование уведомления об ошибке сервиса...")
    success = telegram_service.send_service_error_notification(
        service_name="Test Service",
        error_message="Тестовая ошибка сервиса"
    )
    print(f"   Результат: {'✅ Успешно' if success else '❌ Ошибка'}")
    
    # Тест 4: Сводка мониторинга
    print("\n4. Тестирование сводки мониторинга...")
    success = telegram_service.send_monitoring_summary(
        total_urls=10,
        successful=8,
        failed=2,
        avg_response_time=1.234
    )
    print(f"   Результат: {'✅ Успешно' if success else '❌ Ошибка'}")
    
    print("\n🎉 Тестирование завершено!")

async def test_endpoint_with_500_error():
    """Тестирует отправку уведомлений при реальной ошибке 500"""
    
    print("\n🔍 Тестирование с реальным эндпоинтом, возвращающим 500...")
    
    tester = EndpointTester(max_concurrent=1, timeout=10)
    
    try:
        await tester.init_session()
        
        # Тестируем эндпоинт, который возвращает 500
        result = await tester.test_endpoint("https://httpstat.us/500")
        
        print(f"   URL: {result['url']}")
        print(f"   Статус код: {result.get('status_code')}")
        print(f"   Успешно: {result.get('success')}")
        print(f"   Ошибка: {result.get('error')}")
        
        if result.get('status_code') == 500:
            print("   ✅ Уведомление о статусе 500 должно было быть отправлено")
        else:
            print("   ⚠️  Эндпоинт не вернул статус 500")
            
    except Exception as e:
        print(f"   ❌ Ошибка при тестировании: {e}")
    finally:
        await tester.close_session()

def test_configuration():
    """Проверяет конфигурацию Telegram"""
    
    print("\n⚙️  Проверка конфигурации Telegram...")
    
    config = telegram_service.config
    print(f"   Bot Token: {'✅ Установлен' if config['bot_token'] else '❌ Не установлен'}")
    print(f"   Chat ID: {'✅ Установлен' if config['chat_id'] else '❌ Не установлен'}")
    print(f"   Включен: {'✅ Да' if config['enabled'] else '❌ Нет'}")
    
    if not config['bot_token'] or not config['chat_id']:
        print("\n⚠️  Внимание: Telegram не настроен полностью!")
        print("   Установите переменные окружения:")
        print("   - TELEGRAM_BOT_TOKEN")
        print("   - TELEGRAM_CHAT_ID")
        return False
    
    return True

async def main():
    """Основная функция тестирования"""
    
    print("🚀 Запуск тестов интеграции Telegram...")
    
    # Проверяем конфигурацию
    if not test_configuration():
        print("\n❌ Тестирование прервано из-за неправильной конфигурации")
        return
    
    # Тестируем уведомления
    await test_telegram_notifications()
    
    # Тестируем с реальным эндпоинтом
    await test_endpoint_with_500_error()
    
    print("\n✅ Все тесты завершены!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Тестирование прервано пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка при тестировании: {e}")
        sys.exit(1)
