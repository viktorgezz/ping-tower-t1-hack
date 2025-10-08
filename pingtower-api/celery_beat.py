#!/usr/bin/env python3
"""
Скрипт для запуска Celery Beat (планировщик)
"""
import os
import sys

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.celery_app import celery_app

if __name__ == "__main__":
    # Запуск Celery beat
    celery_app.start([
        "beat",
        "--loglevel=info",
        "--scheduler=celery.beat:PersistentScheduler"
    ])
