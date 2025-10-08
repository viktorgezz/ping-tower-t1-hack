#!/usr/bin/env python3
"""
Скрипт для тестирования мониторинга
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.celery_app import celery_app
from app.tasks.monitoring import test_monitoring_connection, monitor_all_endpoints
import time

def test_celery_connection():
    """Тест подключения к Celery"""
    print("Тестирование подключения к Celery...")
    
    try:
        # Проверяем статус Celery
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        
        if stats:
            print("✅ Celery подключен успешно")
            print(f"Активные воркеры: {list(stats.keys())}")
        else:
            print("❌ Нет активных воркеров Celery")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка подключения к Celery: {e}")
        return False
    
    return True

def test_monitoring_api():
    """Тест внешнего API мониторинга"""
    print("\nТестирование внешнего API мониторинга...")
    
    try:
        # Запускаем тестовую задачу
        result = test_monitoring_connection.delay()
        
        # Ждем результат (максимум 60 секунд)
        try:
            task_result = result.get(timeout=60)
            print(f"✅ Результат теста API: {task_result}")
            return task_result.get("status") == "success"
        except Exception as e:
            print(f"❌ Таймаут или ошибка выполнения задачи: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка запуска тестовой задачи: {e}")
        return False

def test_monitoring_task():
    """Тест основной задачи мониторинга"""
    print("\nТестирование основной задачи мониторинга...")
    
    try:
        # Запускаем задачу мониторинга
        result = monitor_all_endpoints.delay()
        
        # Ждем результат
        try:
            task_result = result.get(timeout=60)
            print(f"✅ Результат мониторинга: {task_result}")
            return task_result.get("status") == "success"
        except Exception as e:
            print(f"❌ Таймаут или ошибка выполнения задачи: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка запуска задачи мониторинга: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Запуск тестов мониторинга PingTower")
    print("=" * 50)
    
    # Тест 1: Подключение к Celery
    celery_ok = test_celery_connection()
    
    if celery_ok:
        # Тест 2: Внешний API
        api_ok = test_monitoring_api()
        
        # Тест 3: Основная задача
        monitoring_ok = test_monitoring_task()
        
        print("\n" + "=" * 50)
        print("📊 Результаты тестирования:")
        print(f"Celery: {'✅' if celery_ok else '❌'}")
        print(f"API мониторинга: {'✅' if api_ok else '❌'}")
        print(f"Задача мониторинга: {'✅' if monitoring_ok else '❌'}")
        
        if all([celery_ok, api_ok, monitoring_ok]):
            print("\n🎉 Все тесты прошли успешно!")
        else:
            print("\n⚠️  Некоторые тесты не прошли. Проверьте логи.")
    else:
        print("\n❌ Celery не подключен. Запустите воркер: python celery_worker.py")
