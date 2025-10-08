# Настройка мониторинга PingTower

## Обзор

Система мониторинга использует Celery для периодического выполнения задач мониторинга эндпоинтов. Каждую минуту система собирает все активные эндпоинты из базы данных и отправляет их на внешний API мониторинга.

## Архитектура

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │  Celery Beat    │    │ Celery Worker   │
│   (Port 8000)   │    │  (Scheduler)    │    │  (Task Exec)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │     Redis       │
                    │  (Message Queue)│
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │  External API   │
                    │  (Monitoring)   │
                    └─────────────────┘
```

## Компоненты

### 1. Celery Beat (Планировщик)
- Запускает задачу мониторинга каждую минуту
- Файл: `celery_beat.py`

### 2. Celery Worker (Исполнитель задач)
- Выполняет задачи мониторинга
- Файл: `celery_worker.py`

### 3. Monitoring Service
- Сервис для работы с внешним API мониторинга
- Файл: `app/services/monitoring_service.py`

### 4. Monitoring Tasks
- Celery задачи для мониторинга
- Файл: `app/tasks/monitoring.py`

## Настройка

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка Redis

Redis уже настроен на внешнем сервере:
- Адрес: `203.81.208.57:6379`
- Логин: `admin`
- Пароль: `Passw0rd`

### 3. Настройка внешнего API

API мониторинга:
- URL: `http://203.81.208.57:8020/api/v1/test-endpoints`
- Таймаут: 30 секунд
- Максимум одновременных запросов: 20

## Запуск

### Вариант 1: Docker Compose (рекомендуемый)

```bash
# Запуск всех сервисов (включая локальный Redis)
docker-compose -f docker-compose.monitoring.yml up --build

# Запуск в фоновом режиме
docker-compose -f docker-compose.monitoring.yml up -d --build
```

### Вариант 2: Локальный запуск с Redis

```bash
# Терминал 1: Запуск Redis
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Терминал 2: FastAPI приложение
python run.py

# Терминал 3: Celery Beat (планировщик)
python celery_beat_local.py

# Терминал 4: Celery Worker (исполнитель)
python celery_worker_local.py
```

### Вариант 3: Ручной запуск (требует внешний Redis)

```bash
# Терминал 1: FastAPI приложение
python run.py

# Терминал 2: Celery Beat (планировщик)
python celery_beat.py

# Терминал 3: Celery Worker (исполнитель)
python celery_worker.py
```

## Тестирование

### 1. Тест подключения

```bash
python test_monitoring.py
```

### 2. Проверка статуса Celery

```bash
# В Python консоли
from app.core.celery_app import celery_app
inspect = celery_app.control.inspect()
print(inspect.stats())
```

### 3. Ручной запуск задачи

```bash
# В Python консоли
from app.tasks.monitoring import monitor_all_endpoints
result = monitor_all_endpoints.delay()
print(result.get())
```

## Логирование

Все логи сохраняются в папке `logs/`:
- Логи FastAPI: `logs/api.log`
- Логи Celery: `logs/celery.log`
- Логи мониторинга: `logs/monitoring.log`

## Мониторинг

### 1. Проверка активных задач

```bash
# В Python консоли
from app.core.celery_app import celery_app
inspect = celery_app.control.inspect()
print(inspect.active())
```

### 2. Проверка расписания

```bash
# В Python консоли
from app.core.celery_app import celery_app
print(celery_app.conf.beat_schedule)
```

## Устранение неполадок

### 1. Celery не подключается к Redis

- Проверьте доступность Redis: `telnet 203.81.208.57 6379`
- Проверьте логин/пароль в конфигурации

### 2. Внешний API недоступен

- Проверьте доступность API: `curl http://203.81.208.57:8020/api/v1/test-endpoints`
- Проверьте логи в `logs/monitoring.log`

### 3. Задачи не выполняются

- Проверьте статус воркеров: `python test_monitoring.py`
- Перезапустите Celery Worker

## Конфигурация

Основные настройки в `app/core/celery_app.py`:

```python
# Частота мониторинга (каждую минуту)
"schedule": crontab(minute="*")

# Таймаут для внешнего API
timeout = 30

# Максимум одновременных запросов
max_concurrent = 20
```

## API Endpoints

### Мониторинг
- `POST /resources/` - создание ресурса
- `POST /resources/endpoints` - добавление эндпоинтов
- `POST /user/selected-endpoints` - выбор эндпоинтов для мониторинга

### Тестирование
- `GET /health` - проверка здоровья API
- `python test_monitoring.py` - полный тест системы
