FROM python:3.11-slim

# Установка системных зависимостей включая инструменты для компиляции и PostgreSQL клиент
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Сначала копируем только requirements.txt для лучшего кэширования
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Создание пользователя для безопасности
RUN adduser --disabled-password --gecos '' app && \
    chown -R app:app /app
USER app

# Открытие порта
EXPOSE 8000

# Переменные окружения
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Команда запуска (лучше использовать полный путь к python)
CMD ["python", "run.py"]