# Email Alerts Service 📧

Сервис для отправки email уведомлений с поддержкой Docker и Docker Compose.

## Описание

Email Alerts Service - это простой и надежный сервис для отправки email уведомлений. Сервис поддерживает различные типы уведомлений (ERROR, WARNING, INFO) и может быть легко интегрирован в существующие системы мониторинга.

## Возможности

- ✅ Отправка email уведомлений через SMTP
- ✅ Поддержка различных типов уведомлений
- ✅ Docker и Docker Compose поддержка
- ✅ Настройка через переменные окружения
- ✅ Логирование всех операций
- ✅ Безопасная работа в контейнере
- ✅ Готовность к масштабированию

## Быстрый старт

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd email-allerts
```

### 2. Настройка переменных окружения

Скопируйте файл примера конфигурации:

```bash
cp env.example .env
```

Отредактируйте файл `.env` и укажите ваши SMTP настройки:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
TEST_RECIPIENTS=recipient1@example.com,recipient2@example.com
```

### 3. Запуск с Docker Compose

```bash
# Сборка и запуск сервиса
docker-compose up --build

# Запуск в фоновом режиме
docker-compose up -d --build

# Просмотр логов
docker-compose logs -f email-alerts
```

### 4. Остановка сервиса

```bash
# Остановка сервиса
docker-compose down

# Остановка с удалением volumes
docker-compose down -v
```

## Конфигурация

### Переменные окружения

| Переменная | Описание | Обязательная | По умолчанию |
|------------|----------|--------------|--------------|
| `SMTP_SERVER` | SMTP сервер | Да | smtp.gmail.com |
| `SMTP_PORT` | Порт SMTP сервера | Да | 587 |
| `SMTP_USERNAME` | Имя пользователя SMTP | Да | - |
| `SMTP_PASSWORD` | Пароль SMTP | Да | - |
| `FROM_EMAIL` | Email отправителя | Нет | SMTP_USERNAME |
| `TEST_RECIPIENTS` | Тестовые получатели | Нет | - |

### Поддерживаемые SMTP провайдеры

- **Gmail**: smtp.gmail.com:587
- **Outlook**: smtp-mail.outlook.com:587
- **Yahoo**: smtp.mail.yahoo.com:587
- **Custom SMTP**: любой SMTP сервер

## Использование

### Программное использование

```python
from main import EmailAlertService

# Создание экземпляра сервиса
service = EmailAlertService()

# Отправка простого email
service.send_email(
    to_emails=['user@example.com'],
    subject='Test Email',
    body='This is a test message'
)

# Отправка уведомления о тревоге
service.send_alert(
    alert_type='ERROR',
    message='Critical system failure detected',
    recipients=['admin@example.com', 'support@example.com']
)
```

### Типы уведомлений

- `ERROR` - Критические ошибки
- `WARNING` - Предупреждения
- `INFO` - Информационные сообщения

## Разработка

### Локальная разработка

1. Установите Python 3.11+
2. Создайте виртуальное окружение:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

3. Установите зависимости:

```bash
pip install -r requirements.txt
```

4. Настройте переменные окружения и запустите:

```bash
python main.py
```

### Структура проекта

```
email-allerts/
├── main.py              # Основной код сервиса
├── requirements.txt     # Python зависимости
├── Dockerfile          # Docker образ
├── docker-compose.yml  # Docker Compose конфигурация
├── env.example         # Пример переменных окружения
└── README.md           # Документация
```

## Безопасность

- Сервис работает под непривилегированным пользователем
- Пароли и чувствительные данные передаются через переменные окружения
- Поддержка TLS для SMTP соединений
- Логирование всех операций для аудита

## Мониторинг и логирование

Сервис ведет подробные логи всех операций:

```bash
# Просмотр логов в реальном времени
docker-compose logs -f email-alerts

# Просмотр последних 100 строк логов
docker-compose logs --tail=100 email-alerts
```

## Расширение функциональности

Сервис готов к расширению следующими возможностями:

- REST API для внешних вызовов
- Веб-интерфейс для управления
- Интеграция с Redis для очередей
- Поддержка шаблонов email
- Планировщик задач
- Метрики и мониторинг

## Устранение неполадок

### Частые проблемы

1. **Ошибка аутентификации SMTP**
   - Проверьте правильность логина и пароля
   - Для Gmail используйте App Password вместо обычного пароля

2. **Сервис не запускается**
   - Проверьте наличие файла `.env`
   - Убедитесь, что все обязательные переменные заданы

3. **Письма не доставляются**
   - Проверьте настройки SMTP сервера
   - Убедитесь, что порт не заблокирован файрволом

### Логи для диагностики

```bash
# Подробные логи
docker-compose logs --tail=50 email-alerts

# Логи с временными метками
docker-compose logs -t email-alerts
```

## Лицензия

MIT License

## Поддержка

Для вопросов и предложений создайте issue в репозитории проекта.

---

**Примечание**: Убедитесь, что ваши SMTP настройки корректны перед запуском в продакшене.
