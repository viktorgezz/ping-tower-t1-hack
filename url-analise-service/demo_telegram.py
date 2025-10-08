#!/usr/bin/env python3
"""
Демонстрационный скрипт для показа работы Telegram уведомлений
"""

from telegram_service import telegram_service

def demo_telegram_notifications():
    """Демонстрация различных типов уведомлений"""
    
    print("🎯 Демонстрация Telegram уведомлений для URL Analysis Service")
    print("=" * 60)
    
    # Проверяем конфигурацию
    config = telegram_service.config
    print(f"📋 Конфигурация:")
    print(f"   Bot Token: {'✅' if config['bot_token'] else '❌'}")
    print(f"   Chat ID: {'✅' if config['chat_id'] else '❌'}")
    print(f"   Включен: {'✅' if config['enabled'] else '❌'}")
    print()
    
    if not config['enabled'] or not config['bot_token'] or not config['chat_id']:
        print("⚠️  Telegram не настроен! Уведомления не будут отправлены.")
        print("   Для настройки установите переменные окружения:")
        print("   - TELEGRAM_BOT_TOKEN")
        print("   - TELEGRAM_CHAT_ID")
        print("   - TELEGRAM_ENABLED=true")
        return
    
    # Демонстрация 1: Приветственное сообщение
    print("1️⃣  Отправка приветственного сообщения...")
    success = telegram_service.send_message(
        "🎉 <b>URL Analysis Service</b> запущен!\n\n"
        "Сервис готов к мониторингу эндпоинтов и отправке уведомлений об ошибках."
    )
    print(f"   Результат: {'✅ Успешно' if success else '❌ Ошибка'}")
    print()
    
    # Демонстрация 2: Уведомление об ошибке 500
    print("2️⃣  Отправка уведомления об ошибке 500...")
    success = telegram_service.send_error_notification(
        url="https://example.com/api/endpoint",
        status_code=500,
        error_message="Внутренняя ошибка сервера"
    )
    print(f"   Результат: {'✅ Успешно' if success else '❌ Ошибка'}")
    print()
    
    # Демонстрация 3: Уведомление об ошибке сервиса
    print("3️⃣  Отправка уведомления об ошибке сервиса...")
    success = telegram_service.send_service_error_notification(
        service_name="URL Parser",
        error_message="Ошибка подключения к базе данных"
    )
    print(f"   Результат: {'✅ Успешно' if success else '❌ Ошибка'}")
    print()
    
    # Демонстрация 4: Сводка мониторинга
    print("4️⃣  Отправка сводки мониторинга...")
    success = telegram_service.send_monitoring_summary(
        total_urls=25,
        successful=23,
        failed=2,
        avg_response_time=0.856
    )
    print(f"   Результат: {'✅ Успешно' if success else '❌ Ошибка'}")
    print()
    
    print("🎯 Демонстрация завершена!")
    print("   Проверьте ваш Telegram чат для просмотра уведомлений.")

if __name__ == "__main__":
    demo_telegram_notifications()
