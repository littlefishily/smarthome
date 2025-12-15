"""
Тесты для Modbus RTU функциональности
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from app.modbus.rtu_master import ModbusRTUMaster


class TestModbusRTUMaster(unittest.TestCase):
    """Тестирование Modbus RTU мастера"""
    
    def setUp(self):
        """Подготовка тестов"""
        self.rtu = ModbusRTUMaster(port='/dev/ttyUSB0', baudrate=9600)
    
    @patch('app.modbus.rtu_master.ModbusSerialClient')
    def test_connect(self, mock_client):
        """Тест подключения"""
        mock_client_instance = MagicMock()
        mock_client_instance.connect.return_value = True
        mock_client.return_value = mock_client_instance
        
        result = self.rtu.connect()
        self.assertTrue(result)
        self.assertTrue(self.rtu.connected)
    
    def test_disconnect(self):
        """Тест отключения"""
        self.rtu.client = MagicMock()
        self.rtu.connected = True
        
        self.rtu.disconnect()
        self.assertFalse(self.rtu.connected)
    
    def test_get_status(self):
        """Тест получения статуса"""
        self.rtu.connected = True
        status = self.rtu.get_status()
        
        self.assertTrue(status['connected'])
        self.assertEqual(status['port'], '/dev/ttyUSB0')
        self.assertEqual(status['baudrate'], 9600)


if __name__ == '__main__':
    unittest.main()
