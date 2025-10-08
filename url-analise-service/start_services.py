#!/usr/bin/env python3
"""
Скрипт для запуска всех сервисов (URL Analysis Service + Kafka)
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def run_command(command, background=False):
    """Запуск команды"""
    try:
        if background:
            return subprocess.Popen(command, shell=True)
        else:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка выполнения команды '{command}': {e}")
        return None

def check_docker():
    """Проверка наличия Docker"""
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker найден")
            return True
        else:
            print("❌ Docker не найден")
            return False
    except FileNotFoundError:
        print("❌ Docker не установлен")
        return False

def check_docker_compose():
    """Проверка наличия Docker Compose"""
    try:
        result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker Compose найден")
            return True
        else:
            print("❌ Docker Compose не найден")
            return False
    except FileNotFoundError:
        print("❌ Docker Compose не установлен")
        return False

def start_with_docker():
    """Запуск с помощью Docker Compose"""
    print("🐳 Запуск с помощью Docker Compose...")
    
    # Проверяем наличие docker-compose.yml
    if not Path('docker-compose.yml').exists():
        print("❌ Файл docker-compose.yml не найден")
        return False
    
    # Останавливаем существующие контейнеры
    print("🛑 Остановка существующих контейнеров...")
    run_command('docker-compose down')
    
    # Запускаем сервисы
    print("🚀 Запуск сервисов...")
    result = run_command('docker-compose up -d')
    
    if result is not None:
        print("✅ Сервисы запущены!")
        print("\n📋 Доступные сервисы:")
        print("   🌐 URL Analysis Service: http://localhost:8000")
        print("   📚 API Документация: http://localhost:8000/docs")
        print("   📊 Kafka UI: http://localhost:8080")
        print("   📨 Kafka: localhost:9092")
        
        print("\n🔍 Проверка статуса контейнеров:")
        run_command('docker-compose ps')
        
        return True
    else:
        print("❌ Ошибка запуска сервисов")
        return False

def start_without_docker():
    """Запуск без Docker (только Python сервис)"""
    print("🐍 Запуск только Python сервиса...")
    
    # Проверяем наличие необходимых файлов
    required_files = ['main.py', 'url_parser.py', 'endpoint_tester.py', 'requirements.txt']
    missing_files = [f for f in required_files if not Path(f).exists()]
    
    if missing_files:
        print(f"❌ Отсутствуют необходимые файлы: {', '.join(missing_files)}")
        return False
    
    # Устанавливаем зависимости
    print("📦 Установка зависимостей...")
    result = run_command('pip install -r requirements.txt')
    if result is None:
        print("❌ Ошибка установки зависимостей")
        return False
    
    # Запускаем сервис
    print("🚀 Запуск URL Analysis Service...")
    print("📍 Сервис будет доступен по адресу: http://localhost:8000")
    print("📚 Документация: http://localhost:8000/docs")
    print("⚠️  Примечание: Kafka не будет доступен без Docker")
    print("\n🛑 Для остановки нажмите Ctrl+C")
    
    try:
        run_command('python start_service.py')
    except KeyboardInterrupt:
        print("\n👋 Сервис остановлен")
        return True

def main():
    """Основная функция"""
    print("🚀 URL Analysis Service - Запуск сервисов")
    print("=" * 50)
    
    # Проверяем наличие Docker
    has_docker = check_docker()
    has_docker_compose = check_docker_compose()
    
    if has_docker and has_docker_compose:
        print("\nВыберите способ запуска:")
        print("1. Полный стек с Docker (рекомендуется)")
        print("2. Только Python сервис")
        
        choice = input("\nВведите номер (1 или 2): ").strip()
        
        if choice == "1":
            success = start_with_docker()
        elif choice == "2":
            success = start_without_docker()
        else:
            print("❌ Неверный выбор")
            success = False
    else:
        print("\n⚠️  Docker не найден, запускаем только Python сервис...")
        success = start_without_docker()
    
    if success:
        print("\n🎉 Сервисы успешно запущены!")
    else:
        print("\n❌ Ошибка запуска сервисов")
        sys.exit(1)

if __name__ == "__main__":
    main()
