"""
Контроллер умного дома - основное приложение
"""
import logging
import json
import os
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from app.config_manager import ConfigManager
from app.network_manager import NetworkManager
from app.modbus.rtu_master import ModbusRTUMaster
from app.modbus.tcp_server import ModbusTCPServer

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SmartHomeController:
    """Основное приложение контроллера умного дома"""
    
    def __init__(self):
        """Инициализация контроллера"""
        # Получить абсолютный путь к директории приложения
        app_dir = Path(__file__).parent.absolute()
        template_dir = app_dir / 'web' / 'templates'
        static_dir = app_dir / 'web' / 'static'
        
        self.app = Flask(__name__, 
                        template_folder=str(template_dir),
                        static_folder=str(static_dir))
        CORS(self.app)
        
        # Менеджеры
        self.config_manager = ConfigManager(config_file='./config/config.json')
        self.network_manager = NetworkManager()
        self.rtu_master = None
        self.tcp_server = None
        
        # Регистрация маршрутов
        self._register_routes()
        
        # Инициализация компонентов
        self._initialize_components()
    
    def _initialize_components(self):
        """Инициализация компонентов на основе конфигурации"""
        # Инициализировать RTU мастер
        rtu_config = self.config_manager.get('modbus_rtu', {})
        if rtu_config.get('enabled'):
            self.rtu_master = ModbusRTUMaster(
                port=rtu_config.get('port', '/dev/ttyUSB0'),
                baudrate=rtu_config.get('baudrate', 9600),
                timeout=rtu_config.get('timeout', 1)
            )
            self.rtu_master.connect()
        
        # Инициализировать TCP сервер
        tcp_config = self.config_manager.get('modbus_tcp', {})
        if tcp_config.get('enabled'):
            self.tcp_server = ModbusTCPServer(
                host=tcp_config.get('host', '0.0.0.0'),
                port=tcp_config.get('port', 5020)
            )
            self.tcp_server.start()
    
    def _register_routes(self):
        """Регистрация всех маршрутов приложения"""
        
        # Веб интерфейс
        @self.app.route('/')
        def index():
            return render_template('index.html')
        
        # API маршруты
        @self.app.route('/api/system/status', methods=['GET'])
        def get_system_status():
            return jsonify(self._get_system_status())
        
        # Сетевые настройки
        @self.app.route('/api/network/config', methods=['GET'])
        def get_network_config():
            return jsonify(self.network_manager.get_network_config())
        
        @self.app.route('/api/network/hostname', methods=['GET', 'POST'])
        def network_hostname():
            if request.method == 'POST':
                data = request.get_json()
                hostname = data.get('hostname')
                success = self.network_manager.set_hostname(hostname)
                return jsonify({'success': success})
            else:
                return jsonify({'hostname': self.network_manager.get_hostname()})
        
        # Конфигурация
        @self.app.route('/api/config/get', methods=['GET'])
        def get_config():
            return jsonify(self.config_manager.get_all())
        
        @self.app.route('/api/config/update', methods=['POST'])
        def update_config():
            data = request.get_json()
            success = self.config_manager.update(data)
            return jsonify({'success': success})
        
        # Modbus RTU
        @self.app.route('/api/modbus/rtu/status', methods=['GET'])
        def get_rtu_status():
            if self.rtu_master:
                return jsonify(self.rtu_master.get_status())
            return jsonify({'error': 'RTU not initialized'})
        
        @self.app.route('/api/modbus/rtu/connect', methods=['POST'])
        def rtu_connect():
            try:
                data = request.get_json()
                port = data.get('port')
                baudrate = data.get('baudrate', 9600)
                
                if self.rtu_master:
                    self.rtu_master.disconnect()
                
                self.rtu_master = ModbusRTUMaster(port=port, baudrate=baudrate)
                success = self.rtu_master.connect()
                return jsonify({'success': success})
            except Exception as e:
                logger.error(f"Error connecting to RTU: {e}")
                return jsonify({'success': False, 'error': str(e)})
        
        @self.app.route('/api/modbus/rtu/disconnect', methods=['POST'])
        def rtu_disconnect():
            if self.rtu_master:
                self.rtu_master.disconnect()
                return jsonify({'success': True})
            return jsonify({'success': False, 'error': 'RTU not initialized'})
        
        @self.app.route('/api/modbus/rtu/read', methods=['POST'])
        def rtu_read():
            try:
                if not self.rtu_master:
                    return jsonify({'success': False, 'error': 'RTU not initialized'})
                
                data = request.get_json()
                slave_id = data.get('slave_id')
                read_type = data.get('type')  # coils, discrete_inputs, holding_registers, input_registers
                start_addr = data.get('start_addr')
                quantity = data.get('quantity')
                
                if read_type == 'coils':
                    result = self.rtu_master.read_coils(slave_id, start_addr, quantity)
                elif read_type == 'discrete_inputs':
                    result = self.rtu_master.read_discrete_inputs(slave_id, start_addr, quantity)
                elif read_type == 'holding_registers':
                    result = self.rtu_master.read_holding_registers(slave_id, start_addr, quantity)
                elif read_type == 'input_registers':
                    result = self.rtu_master.read_input_registers(slave_id, start_addr, quantity)
                else:
                    return jsonify({'success': False, 'error': 'Unknown read type'})
                
                return jsonify(result)
            except Exception as e:
                logger.error(f"Error reading from RTU: {e}")
                return jsonify({'success': False, 'error': str(e)})
        
        @self.app.route('/api/modbus/rtu/write', methods=['POST'])
        def rtu_write():
            try:
                if not self.rtu_master:
                    return jsonify({'success': False, 'error': 'RTU not initialized'})
                
                data = request.get_json()
                slave_id = data.get('slave_id')
                write_type = data.get('type')  # coil, register, coils, registers
                addr = data.get('addr')
                value = data.get('value')
                
                if write_type == 'coil':
                    result = self.rtu_master.write_coil(slave_id, addr, value)
                elif write_type == 'register':
                    result = self.rtu_master.write_register(slave_id, addr, value)
                elif write_type == 'coils':
                    result = self.rtu_master.write_coils(slave_id, addr, value)
                elif write_type == 'registers':
                    result = self.rtu_master.write_registers(slave_id, addr, value)
                else:
                    return jsonify({'success': False, 'error': 'Unknown write type'})
                
                return jsonify(result)
            except Exception as e:
                logger.error(f"Error writing to RTU: {e}")
                return jsonify({'success': False, 'error': str(e)})
        
        # Modbus TCP
        @self.app.route('/api/modbus/tcp/status', methods=['GET'])
        def get_tcp_status():
            if self.tcp_server:
                return jsonify(self.tcp_server.get_status())
            return jsonify({'error': 'TCP server not initialized'})
        
        @self.app.route('/api/modbus/tcp/start', methods=['POST'])
        def tcp_start():
            try:
                data = request.get_json()
                host = data.get('host', '0.0.0.0')
                port = data.get('port', 5020)
                
                if self.tcp_server:
                    self.tcp_server.stop()
                
                self.tcp_server = ModbusTCPServer(host=host, port=port)
                success = self.tcp_server.start()
                return jsonify({'success': success})
            except Exception as e:
                logger.error(f"Error starting TCP server: {e}")
                return jsonify({'success': False, 'error': str(e)})
        
        @self.app.route('/api/modbus/tcp/stop', methods=['POST'])
        def tcp_stop():
            if self.tcp_server:
                self.tcp_server.stop()
                return jsonify({'success': True})
            return jsonify({'success': False, 'error': 'TCP server not initialized'})
    
    def _get_system_status(self) -> dict:
        """Получить общий статус системы"""
        return {
            'rtu': self.rtu_master.get_status() if self.rtu_master else None,
            'tcp': self.tcp_server.get_status() if self.tcp_server else None,
            'hostname': self.network_manager.get_hostname()
        }
    
    def run(self, host: str = '0.0.0.0', port: int = 8000, debug: bool = False):
        """Запуск приложения"""
        logger.info(f"Starting Smart Home Controller on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)


def create_app():
    """Factory функция для создания приложения"""
    return SmartHomeController()


if __name__ == '__main__':
    controller = create_app()
    controller.run()
