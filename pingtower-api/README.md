# PingTower API

Мониторинг API эндпоинтов с уведомлениями и аналитикой.

## 🚀 Быстрый старт

### Через Docker (рекомендуется)

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://gitlab.com/YOUR_USERNAME/pingtower-api.git
   cd pingtower-api
   ```

2. **Настройте переменные окружения:**
   ```bash
   cp .env.example .env
   # Отредактируйте .env файл с вашими настройками
   ```

3. **Запустите приложение:**
   ```bash
   docker-compose up --build
   ```

4. **Откройте Swagger UI:**
   - http://localhost:8000/docs

## 📋 Требования

- Docker & Docker Compose
- PostgreSQL 15+ (внешняя база данных)

## 🔧 Конфигурация

### Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `DATABASE_URL` | URL подключения к PostgreSQL | `postgresql://admin:Passw0rd@203.81.208.57:5432/hack` |
| `SECRET_KEY` | Секретный ключ для JWT | `your-secret-key-here-change-in-production` |
| `HOST` | Хост для запуска сервера | `0.0.0.0` |
| `PORT` | Порт для запуска сервера | `8000` |
| `DEBUG` | Режим отладки | `False` |

## 📚 API Документация

После запуска приложения доступна интерактивная документация:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 🗄️ База данных

Приложение автоматически создает все необходимые таблицы при первом запуске.

### Схема базы данных:

- `users` - Пользователи системы
- `resources` - Мониторируемые ресурсы
- `endpoints` - Эндпоинты для мониторинга
- `logs` - Логи проверок
- `notification_channels` - Каналы уведомлений
- `alert_rules` - Правила уведомлений

## 🔐 Аутентификация

API использует JWT токены для аутентификации:

1. **Регистрация:** `POST /auth/register`
2. **Вход:** `POST /auth/login`
3. **Обновление токена:** `POST /auth/refresh`

## 📊 Основные эндпоинты

- `GET /resources` - Список ресурсов
- `POST /resources` - Создание ресурса
- `POST /resources/{id}/endpoints/discover` - Автообнаружение эндпоинтов
- `GET /logs` - Логи мониторинга
- `GET /user/profile` - Профиль пользователя

## 🛠️ Разработка

### Локальная разработка

1. **Установите зависимости:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # или
   venv\Scripts\activate  # Windows
   
   pip install -r requirements.txt
   ```

2. **Запустите приложение:**
   ```bash
   python run.py
   ```

## 📝 Лицензия

MIT License