#!/usr/bin/env python3
"""
Пример использования контроллера умного дома через Python API
"""
import requests
import json
import time

# Конфигурация
BASE_URL = "http://localhost:8000/api"
SLAVE_ID = 1

class SmartHomeClient:
    """Клиент для взаимодействия с контроллером"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    # ==================== System ====================
    
    def get_system_status(self):
        """Получить статус системы"""
        response = requests.get(f"{self.base_url}/system/status")
        return response.json()
    
    # ==================== Network ====================
    
    def get_network_config(self):
        """Получить конфигурацию сети"""
        response = requests.get(f"{self.base_url}/network/config")
        return response.json()
    
    def get_hostname(self):
        """Получить имя хоста"""
        response = requests.get(f"{self.base_url}/network/hostname")
        return response.json()
    
    def set_hostname(self, hostname: str):
        """Установить имя хоста"""
        response = requests.post(
            f"{self.base_url}/network/hostname",
            json={"hostname": hostname}
        )
        return response.json()
    
    # ==================== RTU ====================
    
    def rtu_connect(self, port: str, baudrate: int = 9600):
        """Подключиться к RTU"""
        response = requests.post(
            f"{self.base_url}/modbus/rtu/connect",
            json={"port": port, "baudrate": baudrate}
        )
        return response.json()
    
    def rtu_disconnect(self):
        """Отключиться от RTU"""
        response = requests.post(f"{self.base_url}/modbus/rtu/disconnect")
        return response.json()
    
    def rtu_status(self):
        """Получить статус RTU"""
        response = requests.get(f"{self.base_url}/modbus/rtu/status")
        return response.json()
    
    def read_holding_registers(self, slave_id: int, start_addr: int, quantity: int):
        """Чтение регистров удержания"""
        response = requests.post(
            f"{self.base_url}/modbus/rtu/read",
            json={
                "slave_id": slave_id,
                "type": "holding_registers",
                "start_addr": start_addr,
                "quantity": quantity
            }
        )
        return response.json()
    
    def read_input_registers(self, slave_id: int, start_addr: int, quantity: int):
        """Чтение входных регистров"""
        response = requests.post(
            f"{self.base_url}/modbus/rtu/read",
            json={
                "slave_id": slave_id,
                "type": "input_registers",
                "start_addr": start_addr,
                "quantity": quantity
            }
        )
        return response.json()
    
    def read_coils(self, slave_id: int, start_addr: int, quantity: int):
        """Чтение катушек"""
        response = requests.post(
            f"{self.base_url}/modbus/rtu/read",
            json={
                "slave_id": slave_id,
                "type": "coils",
                "start_addr": start_addr,
                "quantity": quantity
            }
        )
        return response.json()
    
    def read_discrete_inputs(self, slave_id: int, start_addr: int, quantity: int):
        """Чтение дискретных входов"""
        response = requests.post(
            f"{self.base_url}/modbus/rtu/read",
            json={
                "slave_id": slave_id,
                "type": "discrete_inputs",
                "start_addr": start_addr,
                "quantity": quantity
            }
        )
        return response.json()
    
    def write_register(self, slave_id: int, addr: int, value: int):
        """Запись одного регистра"""
        response = requests.post(
            f"{self.base_url}/modbus/rtu/write",
            json={
                "slave_id": slave_id,
                "type": "register",
                "addr": addr,
                "value": value
            }
        )
        return response.json()
    
    def write_coil(self, slave_id: int, addr: int, value: bool):
        """Запись одной катушки"""
        response = requests.post(
            f"{self.base_url}/modbus/rtu/write",
            json={
                "slave_id": slave_id,
                "type": "coil",
                "addr": addr,
                "value": value
            }
        )
        return response.json()
    
    def write_registers(self, slave_id: int, addr: int, values: list):
        """Запись нескольких регистров"""
        response = requests.post(
            f"{self.base_url}/modbus/rtu/write",
            json={
                "slave_id": slave_id,
                "type": "registers",
                "addr": addr,
                "value": values
            }
        )
        return response.json()
    
    # ==================== TCP ====================
    
    def tcp_status(self):
        """Получить статус TCP сервера"""
        response = requests.get(f"{self.base_url}/modbus/tcp/status")
        return response.json()
    
    def tcp_start(self, host: str = "0.0.0.0", port: int = 5020):
        """Запустить TCP сервер"""
        response = requests.post(
            f"{self.base_url}/modbus/tcp/start",
            json={"host": host, "port": port}
        )
        return response.json()
    
    def tcp_stop(self):
        """Остановить TCP сервер"""
        response = requests.post(f"{self.base_url}/modbus/tcp/stop")
        return response.json()


def main():
    """Пример использования"""
    
    client = SmartHomeClient(BASE_URL)
    
    print("=" * 50)
    print("Smart Home Controller - Python Client Example")
    print("=" * 50)
    
    # Пример 1: Получить статус системы
    print("\n[1] System Status")
    print("-" * 50)
    status = client.get_system_status()
    print(json.dumps(status, indent=2))
    
    # Пример 2: Получить сетевую конфигурацию
    print("\n[2] Network Configuration")
    print("-" * 50)
    network = client.get_network_config()
    print(json.dumps(network, indent=2))
    
    # Пример 3: Подключиться к RTU
    print("\n[3] Connecting to RTU")
    print("-" * 50)
    result = client.rtu_connect("/dev/ttyUSB0", 9600)
    print(f"Connection result: {result}")
    
    # Пример 4: Чтение регистров
    print("\n[4] Reading Holding Registers")
    print("-" * 50)
    data = client.read_holding_registers(slave_id=1, start_addr=0, quantity=10)
    if data.get('success'):
        print(f"Register values: {data.get('data')}")
    else:
        print(f"Error: {data.get('error')}")
    
    # Пример 5: Запись регистра
    print("\n[5] Writing Register")
    print("-" * 50)
    result = client.write_register(slave_id=1, addr=0, value=100)
    print(f"Write result: {result}")
    
    # Пример 6: Запуск TCP сервера
    print("\n[6] Starting TCP Server")
    print("-" * 50)
    result = client.tcp_start()
    print(f"Start result: {result}")
    
    # Пример 7: Получить статус TCP
    print("\n[7] TCP Server Status")
    print("-" * 50)
    status = client.tcp_status()
    print(json.dumps(status, indent=2))
    
    # Пример 8: Мониторинг в реальном времени
    print("\n[8] Real-time Monitoring (10 seconds)")
    print("-" * 50)
    for i in range(5):
        status = client.rtu_status()
        print(f"[{i+1}] RTU Connected: {status.get('connected')}")
        time.sleep(2)


if __name__ == '__main__':
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to controller")
        print("Make sure the application is running on http://localhost:8000")
    except Exception as e:
        print(f"Error: {e}")
