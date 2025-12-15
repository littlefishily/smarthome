import yaml
from pathlib import Path

DEFAULT_CONFIG = {
    'lan': {
        'hostname': 'smarthome-controller',
        'dhcp': True,
        'address': '192.168.1.100',
        'netmask': '255.255.255.0',
        'gateway': '192.168.1.1'
    },
    'modbus_rtu': {
        'port': '/dev/ttyUSB0',
        'baudrate': 19200,
        'parity': 'N',
        'stopbits': 1,
        'timeout': 2
    },
    'modbus_tcp': {
        'listen_port': 5020
    },
    'mqtt': {
        'broker': 'localhost',
        'port': 1883,
        'username': '',
        'password': ''
    },
    'ntp': {
        'servers': ['pool.ntp.org']
    }
}

class Config:
    def __init__(self, path: str = 'config.yaml'):
        self.path = Path(path)
        self.data = DEFAULT_CONFIG.copy()
        self.load()

    def load(self):
        if self.path.exists():
            with open(self.path, 'r', encoding='utf-8') as f:
                try:
                    loaded = yaml.safe_load(f)
                    if isinstance(loaded, dict):
                        # merge shallow
                        self.data.update(loaded)
                except Exception:
                    pass

    def save(self):
        with open(self.path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(self.data, f)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()
