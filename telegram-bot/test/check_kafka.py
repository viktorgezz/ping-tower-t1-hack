from confluent_kafka import Consumer, KafkaError
from config import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_kafka_connection():
    """Проверка подключения к Kafka"""
    print("🔍 Testing Kafka connection...")
    print(f"   Brokers: {config.KAFKA_BROKERS}")
    print(f"   Username: {config.KAFKA_USERNAME}")
    print(f"   Topic: {config.KAFKA_ALERTS_TOPIC}")

    try:
        consumer = Consumer(config.kafka_config)

        # Попробуем получить metadata для проверки подключения
        metadata = consumer.list_topics(timeout=10)
        print("✅ Successfully connected to Kafka cluster")

        # Проверим существование топика
        if config.KAFKA_ALERTS_TOPIC in metadata.topics:
            print(f"✅ Topic '{config.KAFKA_ALERTS_TOPIC}' exists")
        else:
            print(f"❌ Topic '{config.KAFKA_ALERTS_TOPIC}' does not exist")
            print("Available topics:")
            for topic in metadata.topics:
                print(f"  - {topic}")

        consumer.close()

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n💡 Troubleshooting tips:")
        print("1. Check if Kafka broker is running")
        print("2. Verify network connectivity: telnet 193.124.114.117 9092")
        print("3. Check username/password")
        print("4. Verify topic exists")
        print("5. Check firewall settings")


if __name__ == "__main__":
    check_kafka_connection()