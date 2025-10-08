from confluent_kafka import Producer
from config import config
import json
from datetime import datetime


def send_test_alert():
    """Отправка тестового уведомления в Kafka"""
    producer = Producer(config.kafka_config)

    # ЗАМЕНИТЕ 123456789 на ваш реальный Telegram ID из бота!
    alert_data = {
        'telegram_id': 691902762,
        'resource_id': 'test-resource-001',
        'resource_name': 'Тестовый сайт',
        'status': 'DOWN',
        'message': 'Тестовое уведомление: сайт недоступен',
        'timestamp': datetime.now().isoformat()
    }

    producer.produce(
        config.KAFKA_ALERTS_TOPIC,
        json.dumps(alert_data).encode('utf-8')
    )
    producer.flush()
    print(f"✅ Test alert sent to Kafka topic: {config.KAFKA_ALERTS_TOPIC}")


if __name__ == "__main__":
    send_test_alert()