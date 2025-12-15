# REST API Documentation

## Base URL

```
http://<controller-ip>:8000/api
```

## Authentication

Текущая версия не имеет встроенной аутентификации. Для продакшена рекомендуется использовать reverse proxy с SSL/TLS.

## Response Format

Все ответы в формате JSON.

### Успешный ответ

```json
{
  "success": true,
  "data": { ... }
}
```

### Ошибка

```json
{
  "success": false,
  "error": "Error message"
}
```

---

## System Endpoints

### Get System Status

```
GET /system/status
```

**Response:**
```json
{
  "rtu": {
    "connected": true,
    "port": "/dev/ttyUSB0",
    "baudrate": 9600
  },
  "tcp": {
    "running": true,
    "host": "0.0.0.0",
    "port": 5020
  },
  "hostname": "smarthome-controller"
}
```

---

## Network Endpoints

### Get Network Config

```
GET /network/config
```

**Response:**
```json
{
  "interfaces": {
    "eth0": {
      "ip": "192.168.1.100",
      "status": "UP"
    }
  },
  "hostname": "smarthome-controller"
}
```

### Get Hostname

```
GET /network/hostname
```

**Response:**
```json
{
  "hostname": "smarthome-controller"
}
```

### Set Hostname

```
POST /network/hostname
```

**Request:**
```json
{
  "hostname": "new-hostname"
}
```

**Response:**
```json
{
  "success": true
}
```

---

## Configuration Endpoints

### Get Configuration

```
GET /config/get
```

**Response:** (Полный JSON конфиг)

### Update Configuration

```
POST /config/update
```

**Request:**
```json
{
  "modbus_rtu": {
    "baudrate": 19200
  }
}
```

**Response:**
```json
{
  "success": true
}
```

---

## Modbus RTU Endpoints

### Get RTU Status

```
GET /modbus/rtu/status
```

**Response:**
```json
{
  "connected": true,
  "port": "/dev/ttyUSB0",
  "baudrate": 9600
}
```

### Connect to RTU

```
POST /modbus/rtu/connect
```

**Request:**
```json
{
  "port": "/dev/ttyUSB0",
  "baudrate": 9600
}
```

**Response:**
```json
{
  "success": true
}
```

### Disconnect from RTU

```
POST /modbus/rtu/disconnect
```

**Response:**
```json
{
  "success": true
}
```

### Read Modbus Data

```
POST /modbus/rtu/read
```

**Request:**
```json
{
  "slave_id": 1,
  "type": "holding_registers",
  "start_addr": 0,
  "quantity": 10
}
```

**Parameters:**
- `slave_id`: (1-247) Адрес slave устройства
- `type`: Тип чтения:
  - `coils` - Катушки (0-9999)
  - `discrete_inputs` - Дискретные входы (10000-19999)
  - `holding_registers` - Регистры удержания (40000-49999)
  - `input_registers` - Входные регистры (30000-39999)
- `start_addr`: Начальный адрес
- `quantity`: Количество элементов для чтения

**Response:**
```json
{
  "success": true,
  "data": [100, 200, 300, ...]
}
```

### Write Modbus Data

```
POST /modbus/rtu/write
```

**Request (одиночная запись):**
```json
{
  "slave_id": 1,
  "type": "register",
  "addr": 0,
  "value": 100
}
```

**Request (множественная запись):**
```json
{
  "slave_id": 1,
  "type": "registers",
  "addr": 0,
  "value": [100, 200, 300]
}
```

**Parameters:**
- `slave_id`: (1-247) Адрес slave устройства
- `type`: Тип записи:
  - `coil` - Одна катушка
  - `register` - Один регистр
  - `coils` - Несколько катушек
  - `registers` - Несколько регистров
- `addr`: Адрес для записи
- `value`: Значение или массив значений

**Response:**
```json
{
  "success": true
}
```

---

## Modbus TCP Endpoints

### Get TCP Server Status

```
GET /modbus/tcp/status
```

**Response:**
```json
{
  "running": true,
  "host": "0.0.0.0",
  "port": 5020
}
```

### Start TCP Server

```
POST /modbus/tcp/start
```

**Request:**
```json
{
  "host": "0.0.0.0",
  "port": 5020
}
```

**Response:**
```json
{
  "success": true
}
```

### Stop TCP Server

```
POST /modbus/tcp/stop
```

**Response:**
```json
{
  "success": true
}
```

---

## Examples

### Пример 1: Чтение температуры

```bash
curl -X POST http://localhost:8000/api/modbus/rtu/read \
  -H "Content-Type: application/json" \
  -d '{
    "slave_id": 1,
    "type": "input_registers",
    "start_addr": 0,
    "quantity": 1
  }'
```

### Пример 2: Управление реле

```bash
curl -X POST http://localhost:8000/api/modbus/rtu/write \
  -H "Content-Type: application/json" \
  -d '{
    "slave_id": 1,
    "type": "coil",
    "addr": 0,
    "value": true
  }'
```

### Пример 3: Массовая запись регистров

```bash
curl -X POST http://localhost:8000/api/modbus/rtu/write \
  -H "Content-Type: application/json" \
  -d '{
    "slave_id": 1,
    "type": "registers",
    "addr": 100,
    "value": [1000, 2000, 3000, 4000, 5000]
  }'
```

### Пример 4: Python скрипт

```python
import requests
import json

BASE_URL = "http://localhost:8000/api"

# Чтение регистров
response = requests.post(
    f"{BASE_URL}/modbus/rtu/read",
    json={
        "slave_id": 1,
        "type": "holding_registers",
        "start_addr": 0,
        "quantity": 10
    }
)

data = response.json()
if data['success']:
    print("Данные:", data['data'])
else:
    print("Ошибка:", data['error'])

# Запись регистра
response = requests.post(
    f"{BASE_URL}/modbus/rtu/write",
    json={
        "slave_id": 1,
        "type": "register",
        "addr": 0,
        "value": 500
    }
)

print("Запись успешна:", response.json()['success'])
```

---

## Error Codes

| Code | Description |
|------|-------------|
| 200 | OK |
| 400 | Bad Request |
| 404 | Not Found |
| 500 | Internal Server Error |

## Rate Limiting

Текущая версия не имеет ограничений на количество запросов. Для продакшена рекомендуется добавить rate limiting.

## Versioning

Current API Version: **v1.0**

API может измениться в будущих версиях.

---

## Changelog

### v1.0 (Current)
- Initial release
- RTU master functionality
- TCP server support
- Network configuration
- Web UI
