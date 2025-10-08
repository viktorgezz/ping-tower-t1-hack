# Настройка Kafka

## 🔧 Конфигурация подключения

Сервис настроен для подключения к внешней Kafka с аутентификацией:

- **Сервер**: 193.124.114.117:9092
- **UI**: 193.124.114.117:8080
- **Пользователь**: user1
- **Пароль**: pass1
- **Протокол**: SASL_PLAINTEXT
- **Механизм**: PLAIN

## 🚀 Быстрый запуск

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Тест подключения к Kafka
```bash
python test_kafka_connection.py
```

### 3. Запуск сервиса
```bash
python start_service.py
```

### 4. Полный тест стека
```bash
python test_full_stack.py
```

## 🐳 Запуск с Docker

```bash
# Запуск только сервиса (подключение к внешней Kafka)
docker-compose up url-analysis-service

# Запуск с Kafka UI
docker-compose up
```

## 🔍 Проверка работы

### API эндпоинты
- **Документация**: http://localhost:8000/docs
- **Health check**: http://localhost:8000/health
- **Парсинг URL**: POST http://localhost:8000/api/v1/parse-url
- **Тестирование**: POST http://localhost:8000/api/v1/test-endpoints

### Kafka UI
- **Адрес**: http://localhost:8080 (при запуске с Docker)
- **Внешний UI**: http://193.124.114.117:8080

## 📝 Примеры использования

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

## ⚙️ Переменные окружения

```bash
# Основные настройки
export KAFKA_BOOTSTRAP_SERVERS=193.124.114.117:9092
export KAFKA_TOPIC=endpoint_test_results
export KAFKA_USERNAME=user1
export KAFKA_PASSWORD=pass1
export KAFKA_SECURITY_PROTOCOL=SASL_PLAINTEXT
export KAFKA_SASL_MECHANISM=PLAIN

# Настройки сервиса
export PORT=8000
export HOST=0.0.0.0
export RELOAD=true
```

## 🛠️ Устранение неполадок

### Ошибка подключения к Kafka
1. Проверьте доступность сервера: `telnet 193.124.114.117 9092`
2. Проверьте учетные данные
3. Запустите тест: `python test_kafka_connection.py`

### Ошибка отправки в Kafka
1. Убедитесь, что топик `endpoint_test_results` существует
2. Проверьте права пользователя на запись в топик
3. Проверьте логи сервиса

### API недоступен
1. Проверьте, что сервис запущен: `python start_service.py`
2. Проверьте порт: `netstat -an | grep 8000`
3. Проверьте логи сервиса

## 📊 Мониторинг

### Логи сервиса
```bash
# При запуске через Python
tail -f logs/app.log

# При запуске через Docker
docker logs url-analysis-service -f
```

### Kafka UI
- Откройте http://localhost:8080
- Проверьте топик `endpoint_test_results`
- Мониторьте сообщения в реальном времени

### Health checks
```bash
# API health
curl http://localhost:8000/health

# Kafka connection test
python test_kafka_connection.py
```
