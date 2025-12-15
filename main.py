#!/usr/bin/env python3
"""
Главная точка входа приложения контроллера умного дома
"""
import os
import sys
import logging
from pathlib import Path

# Добавить корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/smarthome/controller.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    try:
        logger.info("Starting Smart Home Controller...")
        
        controller = create_app()
        
        # Получить хост и порт из переменных окружения или использовать дефолты
        host = os.environ.get('APP_HOST', '0.0.0.0')
        port = int(os.environ.get('APP_PORT', 8000))
        debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
        
        logger.info(f"Starting Flask app on {host}:{port}")
        controller.run(host=host, port=port, debug=debug)
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}", exc_info=True)
        sys.exit(1)
