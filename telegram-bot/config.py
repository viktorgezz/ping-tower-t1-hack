import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    KAFKA_BROKERS = os.getenv('KAFKA_BROKERS', 'localhost:9092')
    KAFKA_ALERTS_TOPIC = os.getenv('KAFKA_ALERTS_TOPIC', 'pingtower-alerts')
    KAFKA_GROUP_ID = os.getenv('KAFKA_GROUP_ID', 'telegram-bot-group')
    KAFKA_USERNAME = os.getenv('KAFKA_USERNAME')
    KAFKA_PASSWORD = os.getenv('KAFKA_PASSWORD')

    @property
    def kafka_config(self):
        """Возвращает конфигурацию для Kafka с аутентификацией"""
        config = {
            'bootstrap.servers': self.KAFKA_BROKERS,
            'group.id': self.KAFKA_GROUP_ID,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False,
            'session.timeout.ms': 30000,
            'heartbeat.interval.ms': 10000,
            'request.timeout.ms': 30000,
            'socket.timeout.ms': 30000,
            'metadata.request.timeout.ms': 30000,
            'debug': 'broker,security'
        }

        # Добавляем аутентификацию если есть credentials
        if self.KAFKA_USERNAME and self.KAFKA_PASSWORD:
            config.update({
                'security.protocol': 'SASL_PLAINTEXT',
                'sasl.mechanism': 'PLAIN',
                'sasl.username': self.KAFKA_USERNAME,
                'sasl.password': self.KAFKA_PASSWORD,
            })

        return config


config = Config()