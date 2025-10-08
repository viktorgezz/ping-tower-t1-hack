#!/usr/bin/env python3
"""
Скрипт для запуска URL Analysis Service
"""

import uvicorn
import os
import sys
from pathlib import Path

def main():
    """Запуск сервиса"""
    
    # Проверяем наличие необходимых файлов
    required_files = ['main.py', 'url_parser.py', 'endpoint_tester.py', 'requirements.txt']
    missing_files = [f for f in required_files if not Path(f).exists()]
    
    if missing_files:
        print(f"❌ Отсутствуют необходимые файлы: {', '.join(missing_files)}")
        sys.exit(1)
    
    # Настройки по умолчанию
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8000))
    reload = os.getenv('RELOAD', 'true').lower() == 'true'
    
    print("🚀 Запуск URL Analysis Service...")
    print(f"📍 Адрес: http://{host}:{port}")
    print(f"📚 Документация: http://{host}:{port}/docs")
    print(f"🔄 Автоперезагрузка: {'Включена' if reload else 'Отключена'}")
    
    # Настройки Kafka
    kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    kafka_topic = os.getenv('KAFKA_TOPIC', 'endpoint_test_results')
    
    print(f"📨 Kafka сервер: {kafka_servers}")
    print(f"📋 Kafka топик: {kafka_topic}")
    
    try:
        # Запуск сервера
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Сервис остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
