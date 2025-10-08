# Быстрый старт

## 🚀 Запуск за 3 шага

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Запуск сервиса
```bash
python start_service.py
```

### 3. Проверка работы
Откройте браузер: http://localhost:8000/docs

## 🐳 Запуск с Docker (рекомендуется)

```bash
python start_services.py
```

Выберите опцию 1 для полного стека с Kafka.

## 📋 Тестирование API

```bash
python test_api.py
```

## 🔧 Основные эндпоинты

- **POST** `/api/v1/parse-url` - Парсинг URL сайта
- **POST** `/api/v1/test-endpoints` - Тестирование эндпоинтов
- **GET** `/health` - Проверка здоровья
- **GET** `/docs` - Документация API

## 📨 Kafka

Подключение к внешней Kafka:
- Kafka UI: http://localhost:8080 (при запуске с Docker)
- Kafka сервер: 193.124.114.117:9092
- Пользователь: user1 / pass1
- Топик: `endpoint_test_results`

### Тест подключения к Kafka
```bash
python test_kafka_connection.py
```

## 🛠️ Переменные окружения

```bash
export KAFKA_BOOTSTRAP_SERVERS=193.124.114.117:9092
export KAFKA_TOPIC=endpoint_test_results
export KAFKA_USERNAME=user1
export KAFKA_PASSWORD=pass1
export KAFKA_SECURITY_PROTOCOL=SASL_PLAINTEXT
export KAFKA_SASL_MECHANISM=PLAIN
export PORT=8000
```

## 📝 Примеры запросов

### Парсинг сайта
```bash
curl -X POST "http://localhost:8000/api/v1/parse-url" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "max_pages": 10}'
```

### Тестирование эндпоинтов
```bash
curl -X POST "http://localhost:8000/api/v1/test-endpoints" \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://example.com", "https://google.com"]}'
```
