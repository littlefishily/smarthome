# Troubleshooting Guide

## Проблемы при запуске

### 1. ModuleNotFoundError: No module named 'flask'

**Причина:** Python пакеты не установлены

**Решение:**
```bash
pip install -r requirements.txt
```

### 2. Port already in use

**Причина:** Порт 8000 уже занят

**Решение:**
```bash
# Найти процесс, занимающий порт
sudo lsof -i :8000

# Убить процесс
sudo kill -9 <PID>

# Или запустить на другом порту
python3 main.py --port 8001
```

### 3. Permission denied when accessing /dev/ttyUSB0

**Причина:** Пользователь не имеет прав на доступ к последовательному порту

**Решение:**
```bash
# Добавить пользователя в группу dialout
sudo usermod -a -G dialout $USER

# Применить изменения (или перезагрузиться)
newgrp dialout

# Или установить права
sudo chmod 666 /dev/ttyUSB0
```

---

## Проблемы с RTU

### RTU не подключается

**Проверки:**

1. **Физическое подключение**
   ```bash
   # Проверить наличие устройства
   ls -la /dev/tty*
   ls -la /dev/ttyUSB*
   ls -la /dev/ttyS*
   ```

2. **Права доступа**
   ```bash
   # Проверить права
   ls -l /dev/ttyUSB0
   
   # Дать права (временно)
   sudo chmod 666 /dev/ttyUSB0
   
   # Или постоянно
   sudo usermod -a -G dialout $(whoami)
   ```

3. **Параметры подключения**
   - Проверьте скорость передачи (baudrate)
   - Проверьте имя порта
   - Убедитесь что slave_id соответствует устройству

4. **Кабель и устройство**
   - Проверьте целостность кабеля
   - Убедитесь что устройство включено
   - Проверьте настройки Modbus на устройстве

### RTU читает нули или неправильные значения

**Причины:**
- Неверный slave_id
- Неверные адреса регистров
- Проблема с типом данных (int16, int32 и т.д.)
- Неверная скорость передачи

**Решение:**
1. Проверьте документацию устройства
2. Используйте Modbus RTU монитор для проверки (ModbusRTU-Scanner и т.д.)
3. Проверьте логи: `sudo journalctl -u smarthome -f`

### Timeout при чтении

**Причины:**
- Слишком короткое время ожидания (timeout)
- Неверная скорость передачи
- Проблемы со связью

**Решение:**
```json
{
  "modbus_rtu": {
    "timeout": 2
  }
}
```

---

## Проблемы с TCP сервером

### TCP порт не открывается

```bash
# Проверить слушаемые порты
netstat -tlnp | grep 5020

# Проверить файрвол
sudo ufw status
sudo ufw allow 5020

# Проверить в логах
sudo journalctl -u smarthome -f
```

### Клиент не может подключиться к TCP

```bash
# Проверить доступность
telnet <ip> 5020

# Или с nc
nc -zv <ip> 5020

# Ping хоста
ping <ip>
```

### TCP сервер работает но не отвечает на запросы

- Проверьте конфигурацию: `GET /api/modbus/tcp/status`
- Проверьте логи: `sudo journalctl -u smarthome -f`
- Попробуйте перезагрузить сервер:
  ```bash
  curl -X POST http://localhost:8000/api/modbus/tcp/stop
  curl -X POST http://localhost:8000/api/modbus/tcp/start
  ```

---

## Проблемы с веб-интерфейсом

### Страница не загружается

1. **Проверить статус сервиса**
   ```bash
   sudo systemctl status smarthome
   ```

2. **Проверить логи**
   ```bash
   sudo journalctl -u smarthome -f
   ```

3. **Проверить сетевую доступность**
   ```bash
   telnet localhost 8000
   curl http://localhost:8000
   ```

### API запросы возвращают ошибки

1. **Проверить формат JSON**
   ```bash
   # Проверить синтаксис JSON
   echo '{"test": "value"}' | python3 -m json.tool
   ```

2. **Проверить логи**
   ```bash
   sudo journalctl -u smarthome -f | grep "ERROR"
   ```

3. **Проверить конфигурацию**
   ```bash
   cat /etc/smarthome/config.json | python3 -m json.tool
   ```

---

## Проблемы с конфигурацией

### Конфигурация не сохраняется

**Причины:**
- Недостаточно прав на запись
- Путь к файлу неверный
- JSON синтаксис неверный

**Решение:**
```bash
# Проверить права
ls -l /etc/smarthome/config.json

# Проверить владельца
sudo chown smarthome:smarthome /etc/smarthome/config.json

# Проверить синтаксис
cat /etc/smarthome/config.json | python3 -m json.tool
```

### Изменения конфигурации не применяются

Перезагрузите сервис:
```bash
sudo systemctl restart smarthome
```

---

## Проблемы с сетью

### Невозможно установить статический IP

```bash
# Проверить конфигурацию netplan
ls -la /etc/netplan/

# Проверить синтаксис
sudo netplan validate

# Применить конфигурацию
sudo netplan apply

# Проверить статус интерфейса
ip addr show eth0
```

### Изменение hostname не работает

```bash
# Проверить текущее имя хоста
hostname

# Установить новое имя (временно)
sudo hostname newname

# Установить постоянно
sudo hostnamectl set-hostname newname

# Проверить
cat /etc/hostname
```

---

## Общие команды для отладки

### Просмотр логов

```bash
# Последние 100 строк
sudo journalctl -u smarthome -n 100

# В реальном времени
sudo journalctl -u smarthome -f

# За последний час
sudo journalctl -u smarthome --since "1 hour ago"

# С фильтром по уровню
sudo journalctl -u smarthome -p err
```

### Проверка статуса сервиса

```bash
# Полный статус
sudo systemctl status smarthome

# Только active/inactive
sudo systemctl is-active smarthome

# Перезагрузка
sudo systemctl restart smarthome

# Отладка
sudo systemctl start smarthome -vvv
```

### Тестирование API

```bash
# Базовый тест
curl -v http://localhost:8000/api/system/status

# С форматированием
curl -s http://localhost:8000/api/system/status | jq .

# POST запрос
curl -X POST http://localhost:8000/api/modbus/rtu/connect \
  -H "Content-Type: application/json" \
  -d '{"port":"/dev/ttyUSB0","baudrate":9600}' | jq .
```

### Проверка портов и сетей

```bash
# Слушаемые порты
sudo netstat -tlnp

# Или с ss
sudo ss -tlnp

# Активные соединения
sudo netstat -tnp | grep ESTABLISHED

# Маршруты
ip route show

# DNS
cat /etc/resolv.conf
```

---

## Когда обращаться в поддержку

Предоставьте:

1. **Логи**
   ```bash
   sudo journalctl -u smarthome -n 200 > logs.txt
   ```

2. **Конфигурацию**
   ```bash
   cat /etc/smarthome/config.json
   ```

3. **Информацию о системе**
   ```bash
   uname -a
   python3 --version
   pip list
   ```

4. **Результаты диагностики**
   ```bash
   sudo systemctl status smarthome
   curl http://localhost:8000/api/system/status
   ```

---

## Полезные ссылки

- [Pymodbus Documentation](https://pymodbus.readthedocs.io/)
- [Modbus Specification](http://www.modbus.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [systemd Documentation](https://systemd.io/)

---

Если проблема не решена, проверьте GitHub Issues или создайте новый issue с описанием проблемы и логами.
