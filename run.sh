#!/bin/bash
# Скрипт для запуска контроллера в режиме разработки

echo "Smart Home Controller - Development Mode"
echo "========================================"
echo ""

# Проверка наличия Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Создание виртуального окружения если его нет
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Активация виртуального окружения
echo "Activating virtual environment..."
source venv/bin/activate

# Установка зависимостей
echo "Installing dependencies..."
pip install -r requirements.txt

# Создание логов директории
mkdir -p logs
mkdir -p config

# Запуск приложения
echo ""
echo "Starting application on http://localhost:8000"
echo "Press Ctrl+C to stop"
echo ""

export FLASK_DEBUG=true
export FLASK_APP=main.py
python3 main.py
