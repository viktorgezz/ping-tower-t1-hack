# Docker команды для сервиса анализа логов

## 🚀 Основные команды

### Запуск сервиса
```bash
# Сборка и запуск в фоне
docker-compose up --build -d

# Запуск с просмотром логов
docker-compose up --build
```

### Управление сервисом
```bash
# Остановка
docker-compose down

# Перезапуск
docker-compose restart

# Просмотр логов
docker-compose logs -f

# Просмотр логов только за последние 100 строк
docker-compose logs --tail=100 -f
```

### Отладка
```bash
# Вход в контейнер
docker-compose exec log-analyzer bash

# Просмотр статуса контейнеров
docker-compose ps

# Пересборка без кэша
docker-compose build --no-cache
```

## 🔧 Полезные команды

### Очистка
```bash
# Остановка и удаление контейнеров
docker-compose down

# Удаление образов
docker-compose down --rmi all

# Полная очистка (включая volumes)
docker-compose down -v --rmi all
```

### Мониторинг
```bash
# Использование ресурсов
docker stats log-analyzer-api

# Логи в реальном времени
docker-compose logs -f --tail=50
```

## 📋 Проверка работы

После запуска сервис будет доступен:
- **API:** http://localhost:8001
- **Документация:** http://localhost:8001/docs
- **Health check:** http://localhost:8001/health

## 🐛 Решение проблем

### Если контейнер не запускается:
```bash
# Проверьте логи
docker-compose logs log-analyzer

# Пересоберите образ
docker-compose build --no-cache
```

### Если не подключается к ClickHouse:
```bash
# Проверьте подключение из контейнера
docker-compose exec log-analyzer python -c "
import clickhouse_connect
client = clickhouse_connect.get_client(host='203.81.208.57', port=8123, username='admin', password='Passw0rd')
print(client.command('SELECT 1'))
"
```
