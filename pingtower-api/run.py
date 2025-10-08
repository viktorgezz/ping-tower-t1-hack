#!/usr/bin/env python3
"""
Скрипт для запуска PingTower API
"""
import uvicorn
from app.core.init_db import init_db
from app.core.config import settings

if __name__ == "__main__":
    # Инициализация базы данных
    print("Инициализация базы данных...")
    init_db()
    print("База данных инициализирована!")
    
    # Запуск сервера
    print(f"Запуск сервера на {settings.host}:{settings.port}...")
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
