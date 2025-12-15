"""
Modbus RTU Master - взаимодействие с RTU устройствами через последовательный порт
"""
import logging
from typing import List, Dict, Any
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException
import threading
import time

logger = logging.getLogger(__name__)


class ModbusRTUMaster:
    """Клиент для работы с Modbus RTU устройствами"""
    
    def __init__(self, port: str, baudrate: int = 9600, timeout: int = 1):
        """
        Инициализация Modbus RTU мастера
        
        Args:
            port: Последовательный порт (/dev/ttyUSB0, COM3 и т.д.)
            baudrate: Скорость передачи
            timeout: Таймаут ответа в секундах
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.client = None
        self.connected = False
        self.lock = threading.Lock()
        
    def connect(self) -> bool:
        """Подключение к RTU устройствам"""
        try:
            self.client = ModbusSerialClient(
                method='rtu',
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            self.connected = self.client.connect()
            if self.connected:
                logger.info(f"Connected to Modbus RTU on {self.port} at {self.baudrate} baud")
            else:
                logger.error(f"Failed to connect to {self.port}")
            return self.connected
        except Exception as e:
            logger.error(f"Error connecting to Modbus RTU: {e}")
            return False
    
    def disconnect(self):
        """Отключение от RTU устройств"""
        if self.client:
            self.client.close()
            self.connected = False
            logger.info("Disconnected from Modbus RTU")
    
    def read_coils(self, slave_id: int, start_addr: int, quantity: int) -> Dict[str, Any]:
        """Чтение дискретных выходов (катушек)"""
        with self.lock:
            try:
                if not self.connected:
                    return {"success": False, "error": "Not connected"}
                
                result = self.client.read_coils(start_addr, quantity, slave_id=slave_id)
                if hasattr(result, 'bits'):
                    return {"success": True, "data": result.bits}
                else:
                    return {"success": False, "error": str(result)}
            except Exception as e:
                logger.error(f"Error reading coils: {e}")
                return {"success": False, "error": str(e)}
    
    def read_discrete_inputs(self, slave_id: int, start_addr: int, quantity: int) -> Dict[str, Any]:
        """Чтение дискретных входов"""
        with self.lock:
            try:
                if not self.connected:
                    return {"success": False, "error": "Not connected"}
                
                result = self.client.read_discrete_inputs(start_addr, quantity, slave_id=slave_id)
                if hasattr(result, 'bits'):
                    return {"success": True, "data": result.bits}
                else:
                    return {"success": False, "error": str(result)}
            except Exception as e:
                logger.error(f"Error reading discrete inputs: {e}")
                return {"success": False, "error": str(e)}
    
    def read_holding_registers(self, slave_id: int, start_addr: int, quantity: int) -> Dict[str, Any]:
        """Чтение регистров удержания"""
        with self.lock:
            try:
                if not self.connected:
                    return {"success": False, "error": "Not connected"}
                
                result = self.client.read_holding_registers(start_addr, quantity, slave_id=slave_id)
                if hasattr(result, 'registers'):
                    return {"success": True, "data": result.registers}
                else:
                    return {"success": False, "error": str(result)}
            except Exception as e:
                logger.error(f"Error reading holding registers: {e}")
                return {"success": False, "error": str(e)}
    
    def read_input_registers(self, slave_id: int, start_addr: int, quantity: int) -> Dict[str, Any]:
        """Чтение входных регистров"""
        with self.lock:
            try:
                if not self.connected:
                    return {"success": False, "error": "Not connected"}
                
                result = self.client.read_input_registers(start_addr, quantity, slave_id=slave_id)
                if hasattr(result, 'registers'):
                    return {"success": True, "data": result.registers}
                else:
                    return {"success": False, "error": str(result)}
            except Exception as e:
                logger.error(f"Error reading input registers: {e}")
                return {"success": False, "error": str(e)}
    
    def write_coil(self, slave_id: int, addr: int, value: bool) -> Dict[str, Any]:
        """Запись одной катушки"""
        with self.lock:
            try:
                if not self.connected:
                    return {"success": False, "error": "Not connected"}
                
                result = self.client.write_coil(addr, value, slave_id=slave_id)
                if hasattr(result, 'function_code'):
                    return {"success": True}
                else:
                    return {"success": False, "error": str(result)}
            except Exception as e:
                logger.error(f"Error writing coil: {e}")
                return {"success": False, "error": str(e)}
    
    def write_register(self, slave_id: int, addr: int, value: int) -> Dict[str, Any]:
        """Запись одного регистра"""
        with self.lock:
            try:
                if not self.connected:
                    return {"success": False, "error": "Not connected"}
                
                result = self.client.write_register(addr, value, slave_id=slave_id)
                if hasattr(result, 'function_code'):
                    return {"success": True}
                else:
                    return {"success": False, "error": str(result)}
            except Exception as e:
                logger.error(f"Error writing register: {e}")
                return {"success": False, "error": str(e)}
    
    def write_coils(self, slave_id: int, start_addr: int, values: List[bool]) -> Dict[str, Any]:
        """Запись нескольких катушек"""
        with self.lock:
            try:
                if not self.connected:
                    return {"success": False, "error": "Not connected"}
                
                result = self.client.write_coils(start_addr, values, slave_id=slave_id)
                if hasattr(result, 'function_code'):
                    return {"success": True}
                else:
                    return {"success": False, "error": str(result)}
            except Exception as e:
                logger.error(f"Error writing coils: {e}")
                return {"success": False, "error": str(e)}
    
    def write_registers(self, slave_id: int, start_addr: int, values: List[int]) -> Dict[str, Any]:
        """Запись нескольких регистров"""
        with self.lock:
            try:
                if not self.connected:
                    return {"success": False, "error": "Not connected"}
                
                result = self.client.write_registers(start_addr, values, slave_id=slave_id)
                if hasattr(result, 'function_code'):
                    return {"success": True}
                else:
                    return {"success": False, "error": str(result)}
            except Exception as e:
                logger.error(f"Error writing registers: {e}")
                return {"success": False, "error": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """Получить статус соединения"""
        return {
            "connected": self.connected,
            "port": self.port,
            "baudrate": self.baudrate
        }
