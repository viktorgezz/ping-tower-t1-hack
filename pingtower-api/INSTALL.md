# Инструкция по установке PingTower API

## Быстрый старт

### 1. Установка зависимостей

```bash
# Создание виртуального окружения
python -m venv venv

# Активация виртуального окружения
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

### 2. Запуск сервера

```bash
# Запуск через скрипт (рекомендуется)
python run.py

# Или напрямую
python main.py
```

### 3. Проверка работы

Откройте в браузере:
- http://localhost:8000/docs - Swagger UI
- http://localhost:8000/health - Health check

## Тестирование

```bash
# Запуск автоматических тестов
python test_api.py
```

## Docker

### Сборка и запуск

```bash
# Сборка образа
docker build -t pingtower-api .

# Запуск контейнера
docker run -p 8000:8000 pingtower-api
```

### Docker Compose

```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

## Переменные окружения

Скопируйте `env.example` в `.env` и настройте:

```bash
cp env.example .env
```

Основные переменные:
- `SECRET_KEY` - секретный ключ для JWT
- `DEBUG` - режим отладки
- `HOST` - хост для привязки
- `PORT` - порт для привязки

## Структура API

### Аутентификация
- `POST /auth/register` - Регистрация
- `POST /auth/login` - Вход
- `POST /auth/refresh` - Обновление токена
- `POST /auth/logout` - Выход

### Ресурсы
- `GET /resources` - Список ресурсов
- `POST /resources` - Создание ресурса
- `GET /resources/{id}` - Детали ресурса
- `POST /resources/{id}/endpoints/discover` - Обнаружение эндпоинтов
- `PUT /resources/{id}/endpoints` - Настройка эндпоинтов
- `DELETE /resources/{id}` - Удаление ресурса
- `GET /resources/{id}/stats` - Статистика

### Логи
- `GET /logs` - Список логов
- `GET /logs/{id}/analysis` - AI-анализ

### Пользователь
- `GET /user/profile` - Профиль
- `PUT /user/profile` - Обновление профиля
- `GET /user/notification-channels` - Каналы уведомлений
- `POST /user/notification-channels` - Добавление канала
- `DELETE /user/notification-channels/{id}` - Удаление канала
- `GET /user/alert-rules` - Правила оповещений
- `POST /user/alert-rules` - Создание правила
- `PUT /user/alert-rules/{id}` - Обновление правила
- `DELETE /user/alert-rules/{id}` - Удаление правила
- `GET /user/notification-logs` - Логи уведомлений

## Примеры использования

### Регистрация и создание ресурса

```bash
# 1. Регистрация
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "name": "Иван Иванов"
  }'

# 2. Создание ресурса (используйте токен из ответа выше)
curl -X POST "http://localhost:8000/resources" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Мой сайт",
    "url": "https://example.com"
  }'
```

## Устранение неполадок

### Порт занят
```bash
# Измените порт в config.py или через переменную окружения
export PORT=8001
python run.py
```

### Ошибки импорта
```bash
# Убедитесь, что виртуальное окружение активировано
# и все зависимости установлены
pip install -r requirements.txt
```

### Проблемы с Docker
```bash
# Очистка Docker кэша
docker system prune -a

# Пересборка образа
docker build --no-cache -t pingtower-api .
```

## Поддержка

При возникновении проблем:
1. Проверьте логи сервера
2. Убедитесь, что все зависимости установлены
3. Проверьте настройки в config.py
4. Создайте issue в репозитории
