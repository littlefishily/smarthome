"""
Менеджер сетевых настроек
"""
import logging
import subprocess
from typing import Dict, Any
import socket
import ipaddress

logger = logging.getLogger(__name__)


class NetworkManager:
    """Управление сетевыми настройками"""
    
    def __init__(self):
        """Инициализация менеджера сети"""
        pass
    
    def get_hostname(self) -> str:
        """Получить имя хоста"""
        try:
            return socket.gethostname()
        except Exception as e:
            logger.error(f"Error getting hostname: {e}")
            return "unknown"
    
    def set_hostname(self, hostname: str) -> bool:
        """Установить имя хоста"""
        try:
            if not self._is_valid_hostname(hostname):
                logger.error(f"Invalid hostname: {hostname}")
                return False
            
            subprocess.run(
                ["sudo", "hostnamectl", "set-hostname", hostname],
                check=True,
                capture_output=True
            )
            logger.info(f"Hostname changed to: {hostname}")
            return True
        except Exception as e:
            logger.error(f"Error setting hostname: {e}")
            return False
    
    def get_ip_address(self, interface: str = "eth0") -> str:
        """Получить IP адрес интерфейса"""
        try:
            result = subprocess.run(
                ["ip", "addr", "show", interface],
                capture_output=True,
                text=True,
                check=True
            )
            
            for line in result.stdout.split('\n'):
                if 'inet ' in line:
                    return line.strip().split()[1].split('/')[0]
            
            return "Not configured"
        except Exception as e:
            logger.error(f"Error getting IP address: {e}")
            return "Error"
    
    def get_network_config(self) -> Dict[str, Any]:
        """Получить текущую конфигурацию сети"""
        try:
            config = {}
            
            # Получить список интерфейсов
            result = subprocess.run(
                ["ip", "link", "show"],
                capture_output=True,
                text=True,
                check=True
            )
            
            interfaces = {}
            for line in result.stdout.split('\n'):
                if ':' in line and not line.startswith(' '):
                    parts = line.split(':')
                    if len(parts) >= 2:
                        iface_name = parts[1].strip()
                        interfaces[iface_name] = {
                            "ip": self.get_ip_address(iface_name),
                            "status": "UP" if "UP" in line else "DOWN"
                        }
            
            config['interfaces'] = interfaces
            config['hostname'] = self.get_hostname()
            
            return config
        except Exception as e:
            logger.error(f"Error getting network config: {e}")
            return {}
    
    @staticmethod
    def _is_valid_hostname(hostname: str) -> bool:
        """Проверить валидность имени хоста"""
        if len(hostname) > 253:
            return False
        
        if hostname.endswith("."):
            hostname = hostname[:-1]
        
        allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-"
        return all(c in allowed for c in hostname) and not hostname.startswith('-')
    
    @staticmethod
    def _is_valid_ip(ip: str) -> bool:
        """Проверить валидность IP адреса"""
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def _is_valid_netmask(netmask: str) -> bool:
        """Проверить валидность маски сети"""
        try:
            ipaddress.ip_address(netmask)
            # Проверить что это валидная маска
            mask_int = int(ipaddress.ip_address(netmask))
            # Валидная маска имеет вид 111...1110...0
            inverted = mask_int ^ 0xffffffff
            return (inverted & (inverted + 1)) == 0
        except ValueError:
            return False
    
    def configure_static_ip(self, interface: str, ip: str, netmask: str, gateway: str) -> bool:
        """Настроить статический IP"""
        try:
            if not self._is_valid_ip(ip):
                logger.error(f"Invalid IP address: {ip}")
                return False
            
            if not self._is_valid_netmask(netmask):
                logger.error(f"Invalid netmask: {netmask}")
                return False
            
            if not self._is_valid_ip(gateway):
                logger.error(f"Invalid gateway: {gateway}")
                return False
            
            # Создать конфиг для netplan
            config_content = f"""
network:
  version: 2
  ethernets:
    {interface}:
      dhcp4: no
      addresses:
        - {ip}/{self._netmask_to_cidr(netmask)}
      gateway4: {gateway}
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
"""
            
            config_path = f"/etc/netplan/01-{interface}.yaml"
            
            with open(config_path, 'w') as f:
                f.write(config_content)
            
            subprocess.run(["sudo", "netplan", "apply"], check=True, capture_output=True)
            logger.info(f"Static IP configured on {interface}")
            return True
            
        except Exception as e:
            logger.error(f"Error configuring static IP: {e}")
            return False
    
    def enable_dhcp(self, interface: str) -> bool:
        """Включить DHCP на интерфейсе"""
        try:
            config_content = f"""
network:
  version: 2
  ethernets:
    {interface}:
      dhcp4: true
"""
            
            config_path = f"/etc/netplan/01-{interface}.yaml"
            
            with open(config_path, 'w') as f:
                f.write(config_content)
            
            subprocess.run(["sudo", "netplan", "apply"], check=True, capture_output=True)
            logger.info(f"DHCP enabled on {interface}")
            return True
            
        except Exception as e:
            logger.error(f"Error enabling DHCP: {e}")
            return False
    
    @staticmethod
    def _netmask_to_cidr(netmask: str) -> int:
        """Конвертировать маску сети в CIDR нотацию"""
        return sum(bin(int(x)).count('1') for x in netmask.split('.'))
