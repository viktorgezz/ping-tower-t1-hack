#!/usr/bin/env python3
"""
Тест подключения к Kafka с аутентификацией
"""

import json
import time
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация Kafka
KAFKA_CONFIG = {
    'bootstrap_servers': '193.124.114.117:9092',
    'security_protocol': 'SASL_PLAINTEXT',
    'sasl_mechanism': 'PLAIN',
    'sasl_plain_username': 'user1',
    'sasl_plain_password': 'pass1'
}

TOPIC_NAME = 'endpoint_test_results'

def test_kafka_producer():
    """Тест отправки сообщения в Kafka"""
    print("🔍 Тестирование Kafka Producer...")
    
    try:
        # Создаем producer
        producer = KafkaProducer(
            **KAFKA_CONFIG,
            value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        
        # Тестовое сообщение
        test_message = {
            'test': True,
            'timestamp': time.time(),
            'message': 'Тест подключения к Kafka',
            'service': 'url-analysis-service'
        }
        
        # Отправляем сообщение
        future = producer.send(TOPIC_NAME, key='test_key', value=test_message)
        record_metadata = future.get(timeout=10)
        
        print(f"✅ Сообщение успешно отправлено!")
        print(f"   Топик: {record_metadata.topic}")
        print(f"   Партиция: {record_metadata.partition}")
        print(f"   Offset: {record_metadata.offset}")
        
        producer.close()
        return True
        
    except KafkaError as e:
        print(f"❌ Ошибка Kafka: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

def test_kafka_consumer():
    """Тест получения сообщений из Kafka"""
    print("\n🔍 Тестирование Kafka Consumer...")
    
    try:
        # Создаем consumer
        consumer = KafkaConsumer(
            TOPIC_NAME,
            **KAFKA_CONFIG,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            key_deserializer=lambda k: k.decode('utf-8') if k else None,
            auto_offset_reset='latest',
            consumer_timeout_ms=5000  # 5 секунд таймаут
        )
        
        print("📨 Ожидание сообщений...")
        message_count = 0
        
        for message in consumer:
            message_count += 1
            print(f"✅ Получено сообщение #{message_count}:")
            print(f"   Ключ: {message.key}")
            print(f"   Значение: {message.value}")
            print(f"   Партиция: {message.partition}")
            print(f"   Offset: {message.offset}")
            
            # Ограничиваем количество сообщений для теста
            if message_count >= 3:
                break
        
        consumer.close()
        
        if message_count == 0:
            print("ℹ️  Сообщений не найдено (это нормально для нового топика)")
        
        return True
        
    except KafkaError as e:
        print(f"❌ Ошибка Kafka: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

def test_kafka_topics():
    """Тест получения списка топиков"""
    print("\n🔍 Тестирование получения списка топиков...")
    
    try:
        from kafka.admin import KafkaAdminClient, ConfigResource, ConfigResourceType
        
        admin_client = KafkaAdminClient(**KAFKA_CONFIG)
        
        # Получаем список топиков
        metadata = admin_client.describe_cluster()
        print(f"✅ Подключение к кластеру успешно!")
        print(f"   Cluster ID: {metadata.cluster_id}")
        print(f"   Брокеры: {len(metadata.brokers)}")
        
        # Получаем список топиков
        topics = admin_client.list_topics()
        print(f"📋 Доступные топики: {list(topics)}")
        
        admin_client.close()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка получения информации о кластере: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 Тест подключения к Kafka")
    print("=" * 50)
    print(f"📍 Сервер: {KAFKA_CONFIG['bootstrap_servers']}")
    print(f"👤 Пользователь: {KAFKA_CONFIG['sasl_plain_username']}")
    print(f"📋 Топик: {TOPIC_NAME}")
    print("=" * 50)
    
    # Тестируем подключение
    tests = [
        ("Получение информации о кластере", test_kafka_topics),
        ("Отправка сообщения", test_kafka_producer),
        ("Получение сообщений", test_kafka_consumer)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}...")
        result = test_func()
        results.append((test_name, result))
    
    # Итоги
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print("=" * 50)
    
    success_count = 0
    for test_name, result in results:
        status = "✅ УСПЕХ" if result else "❌ ОШИБКА"
        print(f"   {test_name}: {status}")
        if result:
            success_count += 1
    
    print(f"\n🎯 Успешно пройдено: {success_count}/{len(results)} тестов")
    
    if success_count == len(results):
        print("🎉 Все тесты пройдены! Kafka готов к работе.")
    else:
        print("⚠️  Некоторые тесты не пройдены. Проверьте настройки.")

if __name__ == "__main__":
    main()
