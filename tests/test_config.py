"""
Тесты для конфигурации
"""
import unittest
import json
import tempfile
import os
from app.config_manager import ConfigManager


class TestConfigManager(unittest.TestCase):
    """Тестирование менеджера конфигурации"""
    
    def setUp(self):
        """Подготовка тестов"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, 'test_config.json')
        self.config_manager = ConfigManager(config_file=self.config_file)
    
    def tearDown(self):
        """Очистка после тестов"""
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        os.rmdir(self.temp_dir)
    
    def test_save_and_load(self):
        """Тест сохранения и загрузки конфигурации"""
        self.config_manager.set('test_key', 'test_value')
        
        new_config = ConfigManager(config_file=self.config_file)
        self.assertEqual(new_config.get('test_key'), 'test_value')
    
    def test_get_set(self):
        """Тест установки и получения значений"""
        self.config_manager.set('network.hostname', 'test-host')
        value = self.config_manager.get('network.hostname')
        self.assertEqual(value, 'test-host')
    
    def test_get_all(self):
        """Тест получения всей конфигурации"""
        config = self.config_manager.get_all()
        self.assertIsInstance(config, dict)
        self.assertIn('network', config)


if __name__ == '__main__':
    unittest.main()
