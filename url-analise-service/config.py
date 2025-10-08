"""
Конфигурация для URL Analysis Service
"""

import os
from typing import Optional

class Settings:
    """Настройки приложения"""
    
    # Настройки сервера
    HOST: str = os.getenv('HOST', '0.0.0.0')
    PORT: int = int(os.getenv('PORT', 8000))
    RELOAD: bool = os.getenv('RELOAD', 'true').lower() == 'true'
    
    # Настройки Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv('KAFKA_BOOTSTRAP_SERVERS', '193.124.114.117:9092')
    KAFKA_TOPIC: str = os.getenv('KAFKA_TOPIC', 'endpoint_test_results')
    KAFKA_USERNAME: str = os.getenv('KAFKA_USERNAME', 'user1')
    KAFKA_PASSWORD: str = os.getenv('KAFKA_PASSWORD', 'pass1')
    KAFKA_SECURITY_PROTOCOL: str = os.getenv('KAFKA_SECURITY_PROTOCOL', 'SASL_PLAINTEXT')
    KAFKA_SASL_MECHANISM: str = os.getenv('KAFKA_SASL_MECHANISM', 'PLAIN')
    
    # Настройки логирования
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    # Настройки парсера URL
    DEFAULT_MAX_PAGES: int = int(os.getenv('DEFAULT_MAX_PAGES', '50'))
    DEFAULT_DELAY: float = float(os.getenv('DEFAULT_DELAY', '0.3'))
    
    # Настройки тестера эндпоинтов
    DEFAULT_MAX_CONCURRENT: int = int(os.getenv('DEFAULT_MAX_CONCURRENT', '20'))
    DEFAULT_TIMEOUT: int = int(os.getenv('DEFAULT_TIMEOUT', '15'))
    
    # Настройки Telegram уведомлений
    TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', '8427093098:AAHMU1khBdU22vfvlsXh8fccigW30EgzI1g')
    TELEGRAM_CHAT_ID: str = os.getenv('TELEGRAM_CHAT_ID', '1377775487')
    TELEGRAM_ENABLED: bool = os.getenv('TELEGRAM_ENABLED', 'true').lower() == 'true'
    
    @classmethod
    def get_kafka_config(cls) -> dict:
        """Возвращает конфигурацию Kafka"""
        return {
            'bootstrap_servers': cls.KAFKA_BOOTSTRAP_SERVERS,
            'topic': cls.KAFKA_TOPIC,
            'security_protocol': cls.KAFKA_SECURITY_PROTOCOL,
            'sasl_mechanism': cls.KAFKA_SASL_MECHANISM,
            'sasl_plain_username': cls.KAFKA_USERNAME,
            'sasl_plain_password': cls.KAFKA_PASSWORD
        }
    
    @classmethod
    def get_server_config(cls) -> dict:
        """Возвращает конфигурацию сервера"""
        return {
            'host': cls.HOST,
            'port': cls.PORT,
            'reload': cls.RELOAD
        }
    
    @classmethod
    def get_telegram_config(cls) -> dict:
        """Возвращает конфигурацию Telegram"""
        return {
            'bot_token': cls.TELEGRAM_BOT_TOKEN,
            'chat_id': cls.TELEGRAM_CHAT_ID,
            'enabled': cls.TELEGRAM_ENABLED
        }

# Глобальный экземпляр настроек
settings = Settings()
