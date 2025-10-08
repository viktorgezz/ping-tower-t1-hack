import asyncio
import json
import logging
from confluent_kafka import Consumer, KafkaError, KafkaException
from aiogram import Bot
from .utils import format_alert_message
from config import config

logger = logging.getLogger(__name__)


class KafkaAlertConsumer:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.consumer = None
        self.running = False

    async def start_consumer(self):
        """Запуск потребителя Kafka с аутентификацией"""
        kafka_conf = config.kafka_config

        logger.info(f"Connecting to Kafka: {config.KAFKA_BROKERS}")
        logger.info(f"Topic: {config.KAFKA_ALERTS_TOPIC}")
        logger.info(f"Username: {config.KAFKA_USERNAME}")

        try:
            self.consumer = Consumer(kafka_conf)
            self.consumer.subscribe([config.KAFKA_ALERTS_TOPIC])
            self.running = True

            logger.info("Kafka consumer started successfully")

            # Тестовый poll для проверки подключения
            msg = self.consumer.poll(1.0)
            if msg is None:
                logger.info("Kafka connection test successful")
            else:
                logger.info(f"Received test message: {msg.value()}")

            while self.running:
                msg = self.consumer.poll(1.0)

                if msg is None:
                    await asyncio.sleep(0.5)
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        logger.debug("Reached end of partition")
                        continue
                    elif msg.error().code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
                        logger.error(f"Topic {config.KAFKA_ALERTS_TOPIC} does not exist")
                        await asyncio.sleep(5)
                        continue
                    elif msg.error().code() == KafkaError.NETWORK_EXCEPTION:
                        logger.error("Network exception, reconnecting...")
                        await asyncio.sleep(5)
                        continue
                    else:
                        logger.error(f"Kafka error: {msg.error()}")
                        continue

                await self.process_message(msg)

        except KafkaException as e:
            logger.error(f"Kafka exception: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in Kafka consumer: {e}")
        finally:
            await self.stop_consumer()

    async def process_message(self, msg):
        """Обработка сообщения из Kafka"""
        try:
            alert_data = json.loads(msg.value().decode('utf-8'))
            telegram_id = alert_data.get('telegram_id')

            if telegram_id:
                logger.info(f"Received alert for user {telegram_id}")
                await self.send_alert_to_user(telegram_id, alert_data)
                # Коммитим offset после успешной обработки
                self.consumer.commit(msg)
            else:
                logger.warning("No telegram_id in alert data")

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Kafka message: {e}")
            logger.error(f"Raw message: {msg.value()}")
        except Exception as e:
            logger.error(f"Error processing Kafka message: {e}")

    async def send_alert_to_user(self, telegram_id: int, alert_data: dict):
        """Отправка уведомления пользователю"""
        try:
            message = format_alert_message(alert_data)
            await self.bot.send_message(telegram_id, message, parse_mode="Markdown")
            logger.info(f"✅ Alert sent to user {telegram_id}")
        except Exception as e:
            logger.error(f"Failed to send alert to {telegram_id}: {e}")

    async def stop_consumer(self):
        """Остановка потребителя Kafka"""
        self.running = False
        if self.consumer:
            try:
                self.consumer.close()
                logger.info("Kafka consumer stopped gracefully")
            except Exception as e:
                logger.error(f"Error closing consumer: {e}")