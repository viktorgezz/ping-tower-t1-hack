#!/usr/bin/env python3
"""
Скрипт для тестирования подключения к Redis
"""
import redis
import sys

def test_redis_connection(host="localhost", port=6379, password=None, db=0):
    """Тест подключения к Redis"""
    try:
        # Создаем подключение
        r = redis.Redis(
            host=host,
            port=port,
            password=password,
            db=db,
            decode_responses=True
        )
        
        # Тестируем подключение
        r.ping()
        print(f"✅ Успешное подключение к Redis: {host}:{port}")
        
        # Тестируем запись/чтение
        r.set("test_key", "test_value")
        value = r.get("test_key")
        
        if value == "test_value":
            print("✅ Запись и чтение работают корректно")
            r.delete("test_key")  # Очищаем тестовый ключ
            return True
        else:
            print("❌ Ошибка записи/чтения")
            return False
            
    except redis.ConnectionError as e:
        print(f"❌ Ошибка подключения к Redis: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

def test_external_redis():
    """Тест внешнего Redis"""
    print("🔍 Тестирование внешнего Redis...")
    return test_redis_connection(
        host="203.81.208.57",
        port=6379,
        password="Passw0rd",
        db=0
    )

def test_local_redis():
    """Тест локального Redis"""
    print("🔍 Тестирование локального Redis...")
    return test_redis_connection(
        host="localhost",
        port=6379,
        password=None,
        db=0
    )

if __name__ == "__main__":
    print("🔍 Тестирование подключения к Redis")
    print("=" * 50)
    
    # Тест 1: Внешний Redis
    external_ok = test_external_redis()
    
    print()
    
    # Тест 2: Локальный Redis
    local_ok = test_local_redis()
    
    print("\n" + "=" * 50)
    print("📊 Результаты тестирования:")
    print(f"Внешний Redis (203.81.208.57): {'✅' if external_ok else '❌'}")
    print(f"Локальный Redis (localhost): {'✅' if local_ok else '❌'}")
    
    if local_ok:
        print("\n🎉 Локальный Redis работает! Используйте локальную конфигурацию.")
    elif external_ok:
        print("\n⚠️  Внешний Redis работает, но есть проблемы с аутентификацией.")
    else:
        print("\n❌ Ни один Redis не доступен. Запустите локальный Redis:")
        print("docker run -d --name redis -p 6379:6379 redis:7-alpine")
