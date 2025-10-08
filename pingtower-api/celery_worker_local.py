#!/usr/bin/env python3
"""
Скрипт для запуска Celery Worker (локальный Redis)
"""
import os
import sys

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.celery_app_local import celery_app

if __name__ == "__main__":
    # Запуск Celery worker
    celery_app.worker_main([
        "worker",
        "--loglevel=info",
        "--queues=monitoring",
        "--concurrency=2",
        "--hostname=pingtower-worker@%h"
    ])
