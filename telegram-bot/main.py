import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import config
from bot.handlers import router

# Выбор реализации consumer
try:
    from bot.kafka_consumer import KafkaAlertConsumer

    USE_MOCK = False
except Exception as e:
    logging.warning(f"Kafka not available, using mock: {e}")
    from bot.kafka_consumer_mock import KafkaAlertConsumerMock as KafkaAlertConsumer

    USE_MOCK = True

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Основная функция запуска бота"""
    logger.info("Starting Telegram bot...")

    # Инициализация бота и диспетчера
    bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    if USE_MOCK:
        logger.info("Using MOCK Kafka consumer")
    else:
        logger.info("Using REAL Kafka consumer")

    # Инициализация Kafka потребителя
    kafka_consumer = KafkaAlertConsumer(bot)
    kafka_task = None

    try:
        # Запускаем потребителя Kafka в фоне
        kafka_task = asyncio.create_task(kafka_consumer.start_consumer())

        # Запускаем бота
        logger.info("Bot is starting...")
        await dp.start_polling(bot)

    except Exception as e:
        logger.error(f"Error starting bot: {e}")

    finally:
        # Корректное завершение работы
        logger.info("Shutting down...")

        # Останавливаем Kafka consumer
        if hasattr(kafka_consumer, 'stop_consumer'):
            await kafka_consumer.stop_consumer()

        # Отменяем задачу Kafka
        if kafka_task:
            kafka_task.cancel()
            try:
                await kafka_task
            except asyncio.CancelledError:
                pass

        # Закрываем сессию бота
        await bot.session.close()
        logger.info("Bot stopped successfully")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")