@echo off
echo PingTower API - Запуск для Windows
echo ==================================

echo Создание виртуального окружения...
python -m venv venv

echo Активация виртуального окружения...
call venv\Scripts\activate.bat

echo Установка зависимостей...
pip install -r requirements-windows.txt

echo Инициализация базы данных...
python -c "from app.core.init_db import init_db; init_db()"

echo Запуск сервера...
python run.py

pause
