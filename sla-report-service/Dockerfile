FROM python:3.9-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    libfreetype6-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов
COPY requirements.txt .
COPY main.py .
COPY DejaVuSans.ttf .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Создание директории для временных файлов
RUN mkdir -p /tmp/reports

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]