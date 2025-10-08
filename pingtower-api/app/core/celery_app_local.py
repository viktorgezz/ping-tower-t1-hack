from celery import Celery
from celery.schedules import crontab
from app.core.config import settings
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создание экземпляра Celery для локального запуска
celery_app = Celery(
    "pingtower",
    broker="redis://localhost:6379/0",  # Локальный Redis
    backend="redis://localhost:6379/0",
    include=["app.tasks.monitoring"]
)

# Конфигурация Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Настройки для периодических задач
    beat_schedule={
        "monitor-endpoints": {
            "task": "app.tasks.monitoring.monitor_all_endpoints",
            "schedule": crontab(minute="*"),  # каждую минуту
        },
    },
    # Настройки для обработки задач
    task_routes={
        "app.tasks.monitoring.*": {"queue": "monitoring"},
    },
    # Настройки для обработки ошибок
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    # Настройки для логирования
    worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
    worker_task_log_format="[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s",
)

# Настройка логирования для Celery
@celery_app.task(bind=True)
def debug_task(self):
    logger.info(f"Request: {self.request!r}")

if __name__ == "__main__":
    celery_app.start()
