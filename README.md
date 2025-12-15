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
# Recommended (runs module as package):
python3 -m src.main

# Or use the provided launcher from repository root:
python3 smarthome.py
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

## Установка и использование (быстрая инструкция)

- **Автоматический установщик (Ubuntu, рекомендуемый)**
	- В репозитории есть скрипт `packaging/install.sh`, который копирует проект в `/opt/smarthome`, создаёт виртуальное окружение, устанавливает зависимости и разворачивает systemd unit.
	- Запуск (в каталоге репозитория):

```bash
sudo packaging/install.sh
```

- **Ручная установка (для разработчиков / тестирования)**
	- Создайте venv, установите зависимости и запустите сервис вручную:

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python3 src/main.py
```

- **Systemd (пример)** — если вы используете автоматический инсталлятор, unit уже будет установлен и включён. Иначе создайте `/etc/systemd/system/smarthome.service` как в разделе "Systemd unit (пример)" выше и выполните:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now smarthome.service
```

- **Настройка**: отредактируйте `config.yaml` в `/opt/smarthome` (если использовали инсталлятор) или в корне репозитория при ручном запуске. Файл создаётся при первом запуске с значениями по умолчанию.

- **Проверка статуса**:

```bash
sudo systemctl status smarthome.service
journalctl -u smarthome.service -f
```

## Примечания по безопасности и эксплуатация
- Web-интерфейс по умолчанию не защищён; развёртывайте за доверенной сетью или проксируйте через TLS/аутентификацию для продакшена.
- Команды `nmcli`, `netplan`, `timedatectl` выполняются с `sudo` и могут прервать удалённые сессии — применяйте изменения с локальным доступом или осторожно.

## Управление Modbus slave-устройствами

- UI: откройте `http://<device>:8080/ui/config` и перейдите к разделу "Slaves" — там можно просмотреть, добавить, редактировать, удалить и просканировать slave-устройства.
- Автоскан: при желании можно включить автоскан при старте, отредактировав `config.yaml` (поля `slaves_autoscan_on_start`, `slaves_scan_start`, `slaves_scan_end`). По умолчанию автоскан выключён.
- API endpoints:
	- `GET /api/slaves` — получить список известных slave-устройств (JSON `{ok: true, slaves: [...]}`)
	- `POST /api/slaves` — добавить slave (payload JSON: `{"unit":1,"name":"...","description":"..."}`)
	- `PUT /api/slaves/{unit}` — обновить имя/описание slave (payload JSON: `{"name":"...","description":"..."}`)
	- `DELETE /api/slaves/{unit}` — удалить slave
	- `POST /api/slaves/scan` — запустить сканирование диапазона Modbus unit-ов и добавить обнаруженные в `config.yaml` (payload JSON optional: `{"start":1,"end":32}`)

Примечание: сканирование посылает запрос чтения регистра к каждому unit в диапазоне; убедитесь, что подключённые устройства корректно обрабатывают такие запросы.

