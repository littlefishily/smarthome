#!/usr/bin/env bash
set -euo pipefail

# Simple installer for Ubuntu: copies repo to /opt/smarthome, creates venv,
# installs requirements, installs systemd unit and enables the service.

DEST=/opt/smarthome

echo "Installing SmartHome to ${DEST} (requires sudo)..."

sudo mkdir -p "${DEST}"

echo "Copying files to ${DEST} (excluding .git)"
sudo rsync -a --info=progress2 --exclude='.git' . "${DEST}/"

echo "Creating virtualenv"
sudo python3 -m venv "${DEST}/venv"

echo "Installing Python dependencies"
sudo "${DEST}/venv/bin/pip" install --upgrade pip
if [ -f "${DEST}/requirements.txt" ]; then
  sudo "${DEST}/venv/bin/pip" install -r "${DEST}/requirements.txt"
else
  echo "Warning: requirements.txt not found in ${DEST}"
fi

echo "Installing systemd unit"
if [ -f "${DEST}/packaging/smarthome.service" ]; then
  sudo cp "${DEST}/packaging/smarthome.service" /etc/systemd/system/smarthome.service
  sudo systemctl daemon-reload
  sudo systemctl enable --now smarthome.service
  echo "Service enabled and started: smarthome.service"
else
  echo "Warning: packaging/smarthome.service not found in ${DEST}"
fi

echo "Setting ownership to root:root for ${DEST} (you may change this)"
sudo chown -R root:root "${DEST}"

echo "Installation complete. Check service status with: sudo systemctl status smarthome.service"
