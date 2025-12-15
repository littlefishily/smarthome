# Dockerfile для контроллера умного дома
FROM ubuntu:22.04

LABEL maintainer="SmartHome Project"
LABEL description="Smart Home Controller - Modbus RTU/TCP Gateway"

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    git \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование файлов
COPY . /app/

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Создание директорий для логов и конфигураций
RUN mkdir -p /var/log/smarthome \
    && mkdir -p /etc/smarthome

# Копирование конфигурации
COPY config/config.json /etc/smarthome/

# Создание пользователя
RUN useradd -m -s /bin/bash smarthome \
    && chown -R smarthome:smarthome /app \
    && chown -R smarthome:smarthome /var/log/smarthome \
    && chown -R smarthome:smarthome /etc/smarthome

# Переключение на пользователя
USER smarthome

# Expose порты
EXPOSE 8000 5020

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/system/status')" || exit 1

# Запуск приложения
CMD ["python3", "main.py"]
