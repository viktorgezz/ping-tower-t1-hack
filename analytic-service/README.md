# Analytic Service

Микросервис для аналитики и мониторинга веб-ресурсов, построенный на Spring Boot с использованием ClickHouse и Apache Kafka.

## Описание

Analytic Service предназначен для сбора, обработки и анализа метрик веб-ресурсов. Сервис получает данные о проверках эндпоинтов через Kafka, сохраняет их в ClickHouse и предоставляет REST API для получения аналитических отчетов.

## Основные возможности

- 📊 **Аналитика метрик**: Анализ времени отклика, статус-кодов, типов ошибок
- 🔍 **Мониторинг URL**: Отслеживание доступности и производительности конкретных ресурсов
- 📈 **Визуализация данных**: Генерация отчетов с графиками и диаграммами
- ⚡ **Real-time обработка**: Получение данных в реальном времени через Kafka
- 🗄️ **Высокопроизводительное хранение**: Использование ClickHouse для быстрых аналитических запросов

## Технологический стек

- **Java 21** - основной язык разработки
- **Spring Boot 3.5.6** - фреймворк приложения
- **Spring Kafka** - интеграция с Apache Kafka
- **ClickHouse** - аналитическая база данных
- **Docker** - контейнеризация
- **Maven** - система сборки
- **Lombok** - упрощение кода
- **SpringDoc OpenAPI** - документация API
- **Testcontainers** - тестирование с контейнерами

## Архитектура

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Kafka     │───▶│  Analytic   │───▶│ ClickHouse  │
│  Producer   │    │   Service   │    │  Database   │
└─────────────┘    └─────────────┘    └─────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │   REST API  │
                   │  (Reports)  │
                   └─────────────┘
```

## Структура проекта

```
src/main/java/ru/viktorgezz/analytic_service/
├── controller/           # REST контроллеры
│   └── AnalyticsController.java
├── dao/                 # Слой доступа к данным
│   ├── ChartsDao.java
│   ├── CommonMetricsDao.java
│   └── SpecificUrlMetricsDao.java
├── kafka/              # Kafka интеграция
│   ├── KafkaConsumer.java
│   └── KafkaMessageConverter.java
├── model/              # Модели данных
│   ├── charts/         # Модели для графиков
│   ├── Check.java      # Модель проверки
│   └── Incident.java   # Модель инцидента
└── service/            # Бизнес-логика
    ├── impl/           # Реализации сервисов
    └── intrf/          # Интерфейсы сервисов
```

## API Endpoints

### GET /report
Получение отчета по конкретному URL за указанный интервал времени.

**Параметры:**
- `url` (String) - URL для анализа
- `intervalHour` (int) - интервал в часах

**Пример запроса:**
```bash
GET /report?url=https://example.com&intervalHour=24
```

### GET /report-common
Получение общего отчета по всем URL.

**Пример запроса:**
```bash
GET /report-common
```

## Установка и запуск

### Предварительные требования

- Java 21+
- Maven 3.9+
- Docker и Docker Compose
- ClickHouse
- Apache Kafka

### Локальная разработка

1. **Клонирование репозитория:**
```bash
git clone <repository-url>
cd analytic-service
```

2. **Настройка переменных окружения:**
Создайте файл `.env` в корне проекта:
```env
SERVER_PORT=8085
SPRING_APPLICATION_NAME=analytic-service
CLICKHOUSE_URL=jdbc:ch://localhost:8123/default
CLICKHOUSE_USERNAME=admin
CLICKHOUSE_PASSWORD=password
CLICKHOUSE_DRIVER=com.clickhouse.jdbc.ClickHouseDriver
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_SECURITY_PROTOCOL=PLAINTEXT
KAFKA_SASL_MECHANISM=PLAIN
KAFKA_SASL_JAAS=org.apache.kafka.common.security.plain.PlainLoginModule required username="user" password="pass";
KAFKA_CONSUMER_GROUP_ID=analytic-service
KAFKA_AUTO_OFFSET_RESET=earliest
KAFKA_KEY_DESERIALIZER=org.apache.kafka.common.serialization.StringDeserializer
KAFKA_VALUE_DESERIALIZER=org.apache.kafka.common.serialization.StringDeserializer
```

3. **Запуск через Maven:**
```bash
mvn spring-boot:run
```

### Docker

1. **Сборка образа:**
```bash
docker build -t analytic-service .
```

2. **Запуск через Docker Compose:**
```bash
docker-compose up -d
```

## Конфигурация

Основные настройки находятся в `src/main/resources/application.yml`:

```yaml
spring:
  application:
    name: analytic-service
  datasource:
    url: jdbc:ch://203.81.208.57:8123/default
    username: admin
    password: Passw0rd
    driver-class-name: com.clickhouse.jdbc.ClickHouseDriver
  kafka:
    bootstrap-servers: 193.124.114.117:9092
    consumer:
      group-id: analytic-service
      auto-offset-reset: earliest

server:
  port: 8085
```

## База данных

Сервис использует ClickHouse для хранения метрик. Схема таблицы `checks`:

```sql
CREATE TABLE checks
(
    url String,
    timestamp DateTime('UTC'),
    success Bool,
    error Nullable(String),
    response_time Float32,
    status_code UInt16,
    content_type Nullable(String),
    content_length Nullable(UInt32),
    headers Map(String, String),
    is_https Bool,
    redirect_chain Array(String),
    security_headers Map(String, String),
    technology_stack Array(String)
)
ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(timestamp)
ORDER BY (url, timestamp);
```

## Kafka Integration

Сервис подписан на топик `endpoint_test_results` и обрабатывает сообщения в формате JSON, содержащие данные о проверках веб-ресурсов.

## Тестирование

Запуск тестов:
```bash
mvn test
```

Тесты используют Testcontainers для интеграционного тестирования с ClickHouse.

## Мониторинг

Сервис включает Spring Boot Actuator для мониторинга:
- Health checks: `/actuator/health`
- Metrics: `/actuator/metrics`
- Swagger UI: `/swagger-ui.html`

## Разработка

### Добавление новых метрик

1. Создайте новую модель в пакете `model/charts/`
2. Добавьте метод в `ChartsService`
3. Реализуйте логику в `ChartsServiceImpl`
4. Добавьте соответствующий DAO метод
5. Обновите контроллер для экспонирования новой метрики

### Структура данных Check

```java
public class Check {
    private String url;                    // URL ресурса
    private OffsetDateTime timestamp;      // Время проверки
    private Boolean success;               // Успешность проверки
    private String error;                  // Описание ошибки
    private Float responseTime;            // Время отклика
    private Integer statusCode;            // HTTP статус код
    private String contentType;            // Тип контента
    private Integer contentLength;         // Размер контента
    private Map<String, String> headers;   // HTTP заголовки
    private Boolean isHttps;               // Использование HTTPS
    private List<String> redirectChain;    // Цепочка редиректов
    private String sslInfo;                // SSL информация
    private Map<String, String> securityHeaders; // Заголовки безопасности
    private List<String> technologyStack;  // Технологический стек
}
```

## Лицензия

Этот проект является внутренним продуктом и не предназначен для публичного использования.

## Контакты

Для вопросов и предложений обращайтесь к команде разработки.
