"""
Менеджер конфигурации - сохранение и загрузка настроек
"""
import json
import logging
import os
from typing import Dict, Any
import threading

logger = logging.getLogger(__name__)


class ConfigManager:
    """Управление конфигурацией приложения"""
    
    DEFAULT_CONFIG = {
        "network": {
            "hostname": "smarthome",
            "ip_mode": "dhcp",  # dhcp или static
            "ip_address": "192.168.1.100",
            "netmask": "255.255.255.0",
            "gateway": "192.168.1.1",
            "dns": ["8.8.8.8", "8.8.4.4"]
        },
        "modbus_tcp": {
            "enabled": True,
            "host": "0.0.0.0",
            "port": 5020,
            "max_connections": 10
        },
        "modbus_rtu": {
            "enabled": True,
            "port": "/dev/ttyUSB0",
            "baudrate": 9600,
            "timeout": 1,
            "auto_reconnect": True,
            "reconnect_interval": 5
        },
        "devices": [],
        "logging": {
            "level": "INFO",
            "file": "/var/log/smarthome/controller.log"
        }
    }
    
    def __init__(self, config_file: str = "/etc/smarthome/config.json"):
        """
        Инициализация менеджера конфигурации
        
        Args:
            config_file: Путь к файлу конфигурации
        """
        self.config_file = config_file
        self.config = self.DEFAULT_CONFIG.copy()
        self.lock = threading.Lock()
        self.load()
    
    def load(self) -> bool:
        """Загрузить конфигурацию из файла"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Объединить с дефолтными значениями
                    self.config = self._deep_merge(self.DEFAULT_CONFIG, loaded_config)
                logger.info(f"Configuration loaded from {self.config_file}")
                return True
            else:
                logger.warning(f"Config file not found: {self.config_file}, using defaults")
                self.save()
                return False
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return False
    
    def save(self) -> bool:
        """Сохранить конфигурацию в файл"""
        try:
            with self.lock:
                # Создать директорию если её нет
                config_dir = os.path.dirname(self.config_file)
                if config_dir and not os.path.exists(config_dir):
                    os.makedirs(config_dir, exist_ok=True)
                
                with open(self.config_file, 'w') as f:
                    json.dump(self.config, f, indent=2)
                logger.info(f"Configuration saved to {self.config_file}")
                return True
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Получить значение из конфигурации"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    def set(self, key: str, value: Any) -> bool:
        """Установить значение в конфигурацию"""
        try:
            keys = key.split('.')
            config = self.config
            
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            config[keys[-1]] = value
            self.save()
            return True
        except Exception as e:
            logger.error(f"Error setting configuration: {e}")
            return False
    
    def get_all(self) -> Dict[str, Any]:
        """Получить всю конфигурацию"""
        return self.config.copy()
    
    def update(self, updates: Dict[str, Any]) -> bool:
        """Обновить множество значений"""
        try:
            with self.lock:
                self.config = self._deep_merge(self.config, updates)
                self.save()
                return True
        except Exception as e:
            logger.error(f"Error updating configuration: {e}")
            return False
    
    @staticmethod
    def _deep_merge(base: Dict, updates: Dict) -> Dict:
        """Рекурсивное объединение словарей"""
        result = base.copy()
        for key, value in updates.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = ConfigManager._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
