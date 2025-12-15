"""
Modbus TCP Server - предоставление доступа к RTU устройствам через TCP
"""
import logging
from typing import Dict, Any
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.server import StartAsyncTcpServer
from pymodbus.device import ModbusDeviceIdentification, ModbusBasicQuery
import asyncio
import threading

logger = logging.getLogger(__name__)


class ModbusTCPServer:
    """TCP сервер для предоставления доступа к RTU устройствам"""
    
    def __init__(self, host: str = '0.0.0.0', port: int = 502):
        """
        Инициализация Modbus TCP сервера
        
        Args:
            host: IP адрес для прослушивания
            port: TCP порт (502 для стандартного Modbus, обычно используют 5020-5030 если нет прав)
        """
        self.host = host
        self.port = port
        self.server = None
        self.running = False
        self.server_thread = None
        
    def start(self) -> bool:
        """Запуск TCP сервера"""
        try:
            # Создание data stores
            store = ModbusSlaveContext(
                di=ModbusSequentialDataBlock(0, [0] * 100),
                co=ModbusSequentialDataBlock(0, [0] * 100),
                hr=ModbusSequentialDataBlock(0, [0] * 100),
                ir=ModbusSequentialDataBlock(0, [0] * 100)
            )
            
            context = ModbusServerContext(slaves={1: store}, single=False)
            
            # Информация об устройстве
            identity = ModbusDeviceIdentification(
                info_name='Smart Home Controller',
                info_code=0x01,
                info_text='Modbus TCP Gateway for RTU Devices',
                vendor_name='SmartHome',
                product_code='SH-CTRL-001',
                vendor_url='http://localhost:8000',
                product_name='Smart Home Controller',
                model_name='v1.0',
                major_min_ver=1,
                minor_min_ver=0,
                major_maj_ver=1,
                minor_maj_ver=0
            )
            
            # Запуск сервера в отдельном потоке
            self.server_thread = threading.Thread(
                target=self._run_server,
                args=(context, identity),
                daemon=True
            )
            self.server_thread.start()
            self.running = True
            logger.info(f"Started Modbus TCP Server on {self.host}:{self.port}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting Modbus TCP Server: {e}")
            return False
    
    def _run_server(self, context, identity):
        """Запуск сервера"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Запуск асинхронного сервера
            loop.run_until_complete(
                StartAsyncTcpServer(
                    context=context,
                    identity=identity,
                    address=(self.host, self.port),
                    allow_reuse_address=True
                )
            )
        except Exception as e:
            logger.error(f"Server error: {e}")
    
    def stop(self):
        """Остановка TCP сервера"""
        self.running = False
        logger.info("Stopped Modbus TCP Server")
    
    def get_status(self) -> Dict[str, Any]:
        """Получить статус сервера"""
        return {
            "running": self.running,
            "host": self.host,
            "port": self.port
        }
