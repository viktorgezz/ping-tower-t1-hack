# URL Analysis Service

FastAPI сервис для анализа URL и тестирования эндпоинтов с отправкой результатов в Kafka.

## Возможности

- **Парсинг сайтов**: Извлечение всех URL с сайта (внутренние ссылки и медиа-файлы)
- **Тестирование эндпоинтов**: Подробный анализ доступности, производительности и безопасности
- **Kafka интеграция**: Отправка результатов тестирования в Kafka для дальнейшей обработки

## Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Настройте переменные окружения (опционально):
```bash
export KAFKA_BOOTSTRAP_SERVERS=193.124.114.117:9092
export KAFKA_TOPIC=endpoint_test_results
export KAFKA_USERNAME=user1
export KAFKA_PASSWORD=pass1
export KAFKA_SECURITY_PROTOCOL=SASL_PLAINTEXT
export KAFKA_SASL_MECHANISM=PLAIN
```

## Запуск

```bash
python main.py
```

Или с помощью uvicorn:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Сервис будет доступен по адресу: http://localhost:8000

## API Эндпоинты

### 1. Парсинг URL сайта

**POST** `/api/v1/parse-url`

Извлекает все URL с указанного сайта.

**Запрос:**
```json
{
  "url": "https://example.com",
  "max_pages": 50
}
```

**Ответ:**
```json
{
  "internal_urls": ["https://example.com/page1", "https://example.com/page2"],
  "media_urls": ["https://example.com/image.jpg", "https://example.com/style.css"],
  "visited_pages": 10,
  "total_internal_urls": 2,
  "total_media_urls": 2
}
```

### 2. Тестирование эндпоинтов

**POST** `/api/v1/test-endpoints`

Тестирует список URL и отправляет результаты в Kafka.

**Запрос:**
```json
{
  "urls": ["https://example.com", "https://google.com"],
  "max_concurrent": 20,
  "timeout": 15
}
```

**Ответ:**
```json
{
  "message": "Протестировано 2 эндпоинтов. Успешных: 2",
  "total_urls": 2,
  "kafka_topic": "endpoint_test_results",
  "batch_id": "test_2_1704110400"
}
```

## Формат данных в Kafka

Каждое сообщение в Kafka содержит один топик со списком результатов тестирования:

```json
[
  {
    "url": "https://example.com",
    "timestamp": "2024-01-01T12:00:00Z",
    "success": true,
    "error": null,
    "response_time": 0.245,
    "status_code": 200,
    "content_type": "text/html",
    "content_length": "12345",
    "headers": {...},
    "is_https": true,
    "technology_stack": ["nginx", "php"],
    "security_headers": {
      "strict-transport-security": "max-age=31536000",
      "x-content-type-options": "nosniff"
    },
    "content_analysis": {
      "title": "Example Page",
      "meta_tags": {...},
      "element_count": {
        "links": 10,
        "images": 5,
        "scripts": 3
      }
    },
    "additional_checks": {
      "robots_txt": {"exists": true},
      "sitemap_xml": {"exists": true},
      "favicon": {"exists": true}
    },
    "redirect_chain": [],
    "ssl_info": {...},
    "request_id": "test_2_1704110400",
    "batch_timestamp": "2024-01-01T12:00:00Z",
    "service_version": "1.0.0"
  },
  {
    "url": "https://google.com",
    "timestamp": "2024-01-01T12:00:01Z",
    "success": true,
    "error": null,
    "response_time": 0.156,
    "status_code": 200,
    "content_type": "text/html",
    "content_length": "98765",
    "headers": {...},
    "is_https": true,
    "technology_stack": ["gws"],
    "security_headers": {
      "strict-transport-security": "max-age=31536000"
    },
    "content_analysis": {
      "title": "Google",
      "meta_tags": {...},
      "element_count": {
        "links": 15,
        "images": 8,
        "scripts": 5
      }
    },
    "additional_checks": {
      "robots_txt": {"exists": true},
      "sitemap_xml": {"exists": true},
      "favicon": {"exists": true}
    },
    "redirect_chain": [],
    "ssl_info": {...},
    "request_id": "test_2_1704110400",
    "batch_timestamp": "2024-01-01T12:00:01Z",
    "service_version": "1.0.0"
  }
]
```

## Дополнительные эндпоинты

### Проверка здоровья сервиса

**GET** `/health`

Возвращает статус сервиса.

### Документация API

**GET** `/docs` - Swagger UI документация
**GET** `/redoc` - ReDoc документация

## Примеры использования

### Парсинг сайта

```bash
curl -X POST "http://localhost:8000/api/v1/parse-url" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "max_pages": 10
  }'
```

### Тестирование эндпоинтов

```bash
curl -X POST "http://localhost:8000/api/v1/test-endpoints" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://example.com", "https://google.com"],
    "max_concurrent": 10,
    "timeout": 30
  }'
```

## Настройка Kafka

По умолчанию сервис подключается к внешней Kafka на `193.124.114.117:9092` с аутентификацией.

Для изменения настроек используйте переменные окружения:
- `KAFKA_BOOTSTRAP_SERVERS` - адрес Kafka сервера (по умолчанию: 193.124.114.117:9092)
- `KAFKA_TOPIC` - название топика (по умолчанию: endpoint_test_results)
- `KAFKA_USERNAME` - имя пользователя (по умолчанию: user1)
- `KAFKA_PASSWORD` - пароль (по умолчанию: pass1)
- `KAFKA_SECURITY_PROTOCOL` - протокол безопасности (по умолчанию: SASL_PLAINTEXT)
- `KAFKA_SASL_MECHANISM` - механизм SASL (по умолчанию: PLAIN)

### Тестирование подключения к Kafka

```bash
python test_kafka_connection.py
```

## Архитектура

- **main.py** - основной FastAPI сервис
- **url_parser.py** - модуль для парсинга URL с сайтов
- **endpoint_tester.py** - модуль для тестирования эндпоинтов
- **requirements.txt** - зависимости проекта

## Особенности

- Асинхронная обработка запросов
- Поддержка SSL/TLS
- Детальный анализ безопасности (security headers)
- Определение технологического стека
- Анализ содержимого страниц
- Проверка дополнительных ресурсов (robots.txt, sitemap.xml, favicon)
- Обработка редиректов
- Настраиваемые таймауты и лимиты параллельности
