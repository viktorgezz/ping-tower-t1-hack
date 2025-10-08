# PingTower API - PowerShell скрипт для запуска
Write-Host "PingTower API - Запуск для Windows" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green

Write-Host "Создание виртуального окружения..." -ForegroundColor Yellow
python -m venv venv

Write-Host "Активация виртуального окружения..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

Write-Host "Установка зависимостей..." -ForegroundColor Yellow
pip install -r requirements-windows.txt

Write-Host "Инициализация базы данных..." -ForegroundColor Yellow
python -c "from app.core.init_db import init_db; init_db()"

Write-Host "Запуск сервера..." -ForegroundColor Yellow
python run.py

Read-Host "Нажмите Enter для выхода"
