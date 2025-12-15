#!/bin/bash
# Скрипт установки контроллера умного дома

set -e

echo "=== Smart Home Controller Installation Script ==="
echo ""

# Проверка прав администратора
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root!"
   exit 1
fi

echo "[1/7] Creating smarthome user..."
useradd -m -s /bin/bash smarthome 2>/dev/null || echo "User already exists"

echo "[2/7] Creating installation directories..."
mkdir -p /opt/smarthome
mkdir -p /etc/smarthome
mkdir -p /var/log/smarthome

echo "[3/7] Installing system dependencies..."
apt-get update
apt-get install -y python3 python3-pip python3-venv

echo "[4/7] Copying application files..."
cp -r . /opt/smarthome/

echo "[5/7] Installing Python dependencies..."
cd /opt/smarthome
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "[6/7] Setting up configuration..."
cp config/config.json /etc/smarthome/
chown -R smarthome:smarthome /opt/smarthome
chown -R smarthome:smarthome /etc/smarthome
chown -R smarthome:smarthome /var/log/smarthome
chmod 755 /var/log/smarthome

echo "[7/7] Installing systemd service..."
cp systemd/smarthome.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable smarthome.service

echo ""
echo "=== Installation Complete! ==="
echo ""
echo "Next steps:"
echo "1. Configure your settings: sudo nano /etc/smarthome/config.json"
echo "2. Start the service: sudo systemctl start smarthome"
echo "3. Check status: sudo systemctl status smarthome"
echo "4. View logs: sudo journalctl -u smarthome -f"
echo ""
echo "Access the web interface at: http://<your-device-ip>:8000"
echo ""
