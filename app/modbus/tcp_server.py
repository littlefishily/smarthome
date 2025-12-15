"""
Modbus TCP Server - предоставление доступа к RTU устройствам через TCP
"""
import logging
from typing import Dict, Any
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.device import ModbusDeviceIdentification
import asyncio
import threading
import time

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
                info={
                    0x00: 'Smart Home Controller',
                    0x01: 0x01,
                    0x02: 'Modbus TCP Gateway for RTU Devices',
                    0x03: 'SmartHome',
                    0x04: 'SH-CTRL-001',
                    0x05: 'http://localhost:8000',
                    0x06: 'Smart Home Controller',
                    0x07: 'v1.0',
                }
            )
            
            # Запуск сервера в отдельном потоке
            self.server_thread = threading.Thread(
                target=self._run_server,
                args=(context, identity),
                daemon=True
            )
            self.server_thread.start()
            self.running = True
            time.sleep(0.5)  # Даем серверу время на запуск
            logger.info(f"Started Modbus TCP Server on {self.host}:{self.port}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting Modbus TCP Server: {e}")
            return False
    
    def _run_server(self, context, identity):
        """Запуск сервера"""
        try:
            # Использовать правильный импорт для версии pymodbus
            try:
                from pymodbus.server.async_io import StartAsyncTcpServer as AsyncServer
            except ImportError:
                # Fallback для старых версий
                from pymodbus.server import StartAsyncTcpServer as AsyncServer
            
            async def run_async_server():
                await AsyncServer(
                    context=context,
                    identity=identity,
                    address=(self.host, self.port),
                    allow_reuse_address=True
                )
            
            # Попытка запустить с asyncio.run
            try:
                asyncio.run(run_async_server())
            except RuntimeError as e:
                # Если есть проблема с event loop, используем альтернативный способ
                if "asyncio.run() cannot be called from a running event loop" in str(e):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(run_async_server())
                else:
                    raise
        except Exception as e:
            logger.error(f"Server error: {e}")
            self.running = False
    
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
