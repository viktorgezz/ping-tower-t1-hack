# PingTower - Система мониторинга веб-ресурсов

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)
![Kafka](https://img.shields.io/badge/Apache_Kafka-231F20?style=for-the-badge&logo=apache-kafka&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![ClickHouse](https://img.shields.io/badge/ClickHouse-FFCC01?style=for-the-badge&logo=clickhouse&logoColor=black)
![Spring Boot](https://img.shields.io/badge/Spring_Boot-6DB33F?style=for-the-badge&logo=spring-boot&logoColor=white)

## 📋 Описание проекта

**PingTower** - это комплексная система мониторинга веб-ресурсов, построенная на микросервисной архитектуре. Система обеспечивает непрерывный мониторинг доступности, производительности и безопасности веб-сайтов и API с использованием современных технологий и AI-анализа.

Решение кейса - __PingTower: сервисы под присмотром__ на хакатоне [__Т1.Нижний Новгород 2025__](https://impulse.t1.ru/event/ecayIfzH/?utm_source=codenrock&utm_medium=banner&utm_campaign=promo) (4 место)

Команда __Back2Back__

Состав:

- Лулаков Даниил - Back-end, Dev-ops [[certificate](https://github.com/danlylacov/ping-tower-t1-hack/blob/main/Хакатон_Т1_Нижний_Новгород_Certificate.pdf)]
- Атюцкий Никита - Back-end
- Гезенцвей Виктор - Back-end [[certificate](https://github.com/viktorgezz/ping-tower-t1-hack/blob/main/%D0%A5%D0%B0%D0%BA%D0%B0%D1%82%D0%BE%D0%BD%20%D0%A21%20%D0%9D%D0%B8%D0%B6%D0%BD%D0%B8%D0%B9%20%D0%9D%D0%BE%D0%B2%D0%B3%D0%BE%D1%80%D0%BE%D0%B4%20Certificate_2025-10-08_10_47_13.679Z-1.pdf)]
- Колесникова Лариса - Front-end
- Беляев Валерий - Analitics


Презентация: [click](https://github.com/danlylacov/ping-tower-t1-hack/blob/main/PingTower.pptx)


### 🎯 Основные возможности

- 🔍 **Мониторинг в реальном времени** - непрерывная проверка доступности веб-ресурсов
- 📊 **Аналитика и отчетность** - детальная аналитика производительности с AI-анализом
- 🚨 **Система уведомлений** - многоуровневые уведомления через Telegram и Email
- 📈 **SLA отчеты** - автоматическая генерация отчетов в PDF формате
- 🤖 **AI-анализ логов** - интеллектуальный анализ ошибок и рекомендации
- 🌐 **Веб-интерфейс** - современный React-интерфейс для управления системой
- 🔐 **Безопасность** - JWT аутентификация и защищенные API

## 🚀 Компоненты системы

### 1. **PingTower Frontend** (`pingtower-frontend/`)
**Современный веб-интерфейс для управления системой мониторинга**

- **Технологии**: React 18, TypeScript, Vite, Tailwind CSS
- **Функции**:
  - Панель мониторинга в реальном времени
  - Управление ресурсами и эндпоинтами
  - Просмотр аналитики и отчетов
  - Личный кабинет пользователя
  - Адаптивный дизайн (mobile-first)

**Порт**: 3000 (dev), 80 (production)

### 2. **PingTower API** (`pingtower-api/`)
**Основной API сервис системы**

- **Технологии**: FastAPI, PostgreSQL, SQLAlchemy, Celery
- **Функции**:
  - REST API для управления ресурсами
  - JWT аутентификация и авторизация
  - Управление пользователями и ресурсами
  - Планировщик задач мониторинга
  - Интеграция с внешними сервисами

**Порт**: 8000

### 3. **URL Analysis Service** (`url-analise-service/`)
**Сервис анализа и тестирования веб-ресурсов**

- **Технологии**: FastAPI, aiohttp, Kafka
- **Функции**:
  - Парсинг сайтов и извлечение URL
  - Тестирование эндпоинтов
  - Анализ безопасности (SSL, headers)
  - Определение технологического стека
  - Отправка результатов в Kafka

**Порт**: 8000

### 4. **Analytic Service** (`analytic-service/`)
**Сервис аналитики и обработки метрик**

- **Технологии**: Spring Boot, ClickHouse, Kafka
- **Функции**:
  - Обработка метрик из Kafka
  - Аналитика производительности
  - Генерация отчетов и графиков
  - Хранение в ClickHouse
  - REST API для получения аналитики

**Порт**: 8085

### 5. **AI Agent** (`ai-agent/`)
**Сервис AI-анализа логов и ошибок**

- **Технологии**: FastAPI, ClickHouse, AI/ML
- **Функции**:
  - Анализ логов сервисов
  - Категоризация ошибок
  - Генерация рекомендаций
  - Адаптивные запросы к ClickHouse
  - Интеллектуальная диагностика

**Порт**: 8000

### 6. **Telegram Bot** (`telegram-bot/`)
**Telegram бот для уведомлений**

- **Технологии**: Python, aiogram, Kafka
- **Функции**:
  - Получение уведомлений из Kafka
  - Отправка алертов в Telegram
  - Интерактивные команды
  - Управление подписками
  - Интеграция с другими сервисами

### 7. **Email Alerts** (`email-allerts/`)
**Сервис email уведомлений**

- **Технологии**: Python, SMTP
- **Функции**:
  - Отправка email уведомлений
  - Поддержка различных типов алертов
  - Настраиваемые шаблоны
  - SMTP интеграция
  - Логирование операций

### 8. **SLA Report Service** (`sla-report-service/`)
**Сервис генерации отчетов SLA**

- **Технологии**: FastAPI, ReportLab, Matplotlib
- **Функции**:
  - Генерация PDF отчетов
  - Создание графиков и диаграмм
  - Поддержка кириллицы
  - Настраиваемые шаблоны
  - REST API для генерации

**Порт**: 8021

### 9. **Service Scripts** (`service_scripts/`)
**Инфраструктурные скрипты и конфигурации**

- **Технологии**: Ansible, Docker Compose
- **Функции**:
  - Автоматическое развертывание инфраструктуры
  - Настройка мониторинга (Prometheus, Grafana)
  - Конфигурация Nginx reverse proxy
  - Управление Docker контейнерами

## 🛠️ Технологический стек

### Backend
- **Python 3.9+** - основной язык разработки
- **FastAPI** - веб-фреймворк для API
- **Spring Boot** - Java фреймворк для аналитики
- **PostgreSQL** - основная база данных
- **ClickHouse** - аналитическая база данных
- **Redis** - кэш и очереди задач
- **Apache Kafka** - брокер сообщений

### Frontend
- **React 18** - UI библиотека
- **TypeScript** - типизация
- **Vite** - сборщик
- **Tailwind CSS** - стилизация
- **Zustand** - управление состоянием

### Infrastructure
- **Docker & Docker Compose** - контейнеризация
- **Ansible** - автоматизация развертывания
- **Nginx** - reverse proxy
- **Prometheus** - мониторинг метрик
- **Grafana** - визуализация данных

### AI/ML
- **Python AI libraries** - анализ логов
- **ClickHouse analytics** - обработка больших данных
- **Adaptive queries** - оптимизация запросов

## 🚀 Быстрый старт

### Предварительные требования

- Docker и Docker Compose
- Git
- Минимум 4GB RAM
- Порты: 3000, 8000, 8085, 8021

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd ping-tower-t1-hack
```

### 2. Настройка переменных окружения

Создайте файлы `.env` в каждом сервисе на основе `env.example`


### 3. Запуск через Docker Compose

Запустите каждый сервис через команды

```bash
# Запуск всех сервисов
docker-compose up --build -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

### 4. Доступ к сервисам

- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Analytic Service**: http://localhost:8085/swagger-ui.html
- **SLA Reports**: http://localhost:8021/docs


## 🔧 Конфигурация

### Основные настройки

| Сервис | Порт | База данных | Зависимости |
|--------|------|-------------|-------------|
| Frontend | 3000 | - | API |
| API | 8000 | PostgreSQL | Redis, Celery |
| URL Analysis | 8000 | - | Kafka |
| Analytic | 8085 | ClickHouse | Kafka |
| AI Agent | 8000 | ClickHouse | - |
| Telegram Bot | - | - | Kafka |
| Email Alerts | - | - | SMTP |
| SLA Reports | 8021 | - | - |



## 📈 Использование

### 1. Регистрация и авторизация

```bash
# Регистрация пользователя
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Авторизация
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'
```

### 2. Добавление ресурса для мониторинга

```bash
curl -X POST "http://localhost:8000/resources" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Website", "url": "https://example.com"}'
```

### 3. Анализ URL

```bash
curl -X POST "http://localhost:8000/api/v1/parse-url" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "max_pages": 10}'
```

### 4. Генерация SLA отчета

```bash
curl -X POST "http://localhost:8021/generate-report" \
  -H "Content-Type: application/json" \
  -d '{
    "resourceId": "123",
    "resourceName": "My Service",
    "url": "https://example.com",
    "metrics": {
      "uptime": 99.9,
      "avgResponseTime": 150,
      "incidents": 5,
      "mttr": 30,
      "slaCompliance": 99.5
    }
  }'
```

## 🔍 API Документация

### Основные эндпоинты

#### PingTower API (`/api/v1/`)
- `POST /auth/register` - Регистрация пользователя
- `POST /auth/login` - Авторизация
- `GET /resources` - Список ресурсов
- `POST /resources` - Создание ресурса
- `GET /logs` - Логи мониторинга

#### URL Analysis Service (`/api/v1/`)
- `POST /parse-url` - Парсинг сайта
- `POST /test-endpoints` - Тестирование эндпоинтов

#### Analytic Service (`/report`)
- `GET /report` - Отчет по URL
- `GET /report-common` - Общий отчет

#### AI Agent (`/analyze`)
- `POST /analyze` - Анализ логов сервиса

#### SLA Reports (`/generate-report`)
- `POST /generate-report` - Генерация PDF отчета

## 🚨 Система уведомлений

### Типы уведомлений

1. **ERROR** - Критические ошибки
2. **WARNING** - Предупреждения
3. **INFO** - Информационные сообщения

### Каналы уведомлений

- **Telegram Bot** - мгновенные уведомления
- **Email** - детальные отчеты
- **Web Dashboard** - визуальные алерты


## 🔒 Безопасность

### Аутентификация и авторизация

- JWT токены для API доступа
- Роли пользователей (admin, user)
- Защищенные эндпоинты
- CORS настройки

### Безопасность данных

- Шифрование паролей
- HTTPS для всех соединений
- Валидация входных данных
- Логирование безопасности

## 📝 Разработка

### Структура проекта

```
ping-tower-t1-hack/
├── pingtower-frontend/     # React приложение
├── pingtower-api/         # Основной API
├── url-analise-service/   # Анализ URL
├── analytic-service/      # Аналитика (Java)
├── ai-agent/             # AI анализ
├── telegram-bot/         # Telegram бот
├── email-allerts/        # Email уведомления
├── sla-report-service/   # Генерация отчетов
├── service_scripts/      # Инфраструктура
└── README.md            # Документация
```

### Добавление нового сервиса

1. Создайте папку для сервиса
2. Добавьте `Dockerfile` и `docker-compose.yml`
3. Обновите основной `docker-compose.yml`
4. Добавьте документацию в README

### Стандарты кодирования

- **Python**: PEP 8, Black formatter
- **JavaScript/TypeScript**: ESLint, Prettier
- **Java**: Google Java Style Guide
- **Docker**: Multi-stage builds
- **API**: OpenAPI/Swagger документация


## 📄 Лицензия

MIT License - см. файл [LICENSE](LICENSE)



---

**PingTower** - надежный инструмент для мониторинга веб-ресурсов с современной архитектурой и AI-анализом.
