# SmartHome Controller Firmware

Минималистичная прошивка для контроллера умного дома под Ubuntu. Включает
- Modbus RTU менеджер
- Прозрачный Modbus-TCP (MBAP → RTU) шлюз
- JSON-over-TCP шлюз для быстрых запросов
- MQTT ↔ RTU мост
- Веб-интерфейс для настройки LAN, Modbus, MQTT и NTP

## Требования
- Ubuntu (требуется для применения сетевых/NTP команд)
- Python 3.10+
- Права `sudo` для применения сетевых и NTP настроек

## Быстрый старт
1. Создайте виртуальное окружение и установите зависимости:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Отредактируйте `config.yaml` при необходимости (после первого запуска файл создаётся со значениями по умолчанию).

3. Запустите контроллер:

```bash
python3 src/main.py
```

По умолчанию веб-интерфейс доступен на `http://0.0.0.0:8080`.

## Веб-интерфейс
- Откройте `http://<device>:8080/ui/config` для настроек LAN, NTP и Modbus RTU.
- Превью конфигурации LAN доступно через `/api/preview_lan` (не применяет изменения).

## Применение сетевых и NTP настроек
- Применение сетевых настроек выполняется через `nmcli` (если установлен) или через `netplan`.
- Для применения требуется `sudo`; веб-сервер попытается выполнить команды `hostnamectl`, `nmcli` или `netplan apply`.
- NTP применение использует `timedatectl` и `ntpdate` (если доступны).

ВНИМАНИЕ: применение сетевых настроек может разорвать текущую SSH/сессию.

## Systemd unit (пример)
Создайте файл `/etc/systemd/system/smarthome.service` с содержимым:

```ini
[Unit]
Description=SmartHome Controller
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/smarthome
ExecStart=/opt/smarthome/venv/bin/python /opt/smarthome/src/main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Затем выполните:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now smarthome.service
```

## Конфигурация
- Файл конфигурации: `config.yaml` (формат YAML). Параметры: `lan`, `modbus_rtu`, `modbus_tcp`, `mqtt`, `ntp`.

## Отладка
- Логи и действия по изменению сетевых настроек сохраняются в `logs/actions.log` в папке запуска.
- Если что-то не работает, запустите вручную `python3 src/main.py` в терминале и посмотрите stdout/stderr.

## Вклад
- Pull requests и issues приветствуются.
