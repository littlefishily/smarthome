#!/bin/bash
# Примеры использования REST API

echo "Smart Home Controller - REST API Examples"
echo "=========================================="
echo ""

# Переменные
BASE_URL="http://localhost:8000/api"
SLAVE_ID=1

# Пример 1: Статус системы
echo "[1] System Status"
echo "---------"
curl -s $BASE_URL/system/status | jq .
echo ""

# Пример 2: Сетевая конфигурация
echo "[2] Network Configuration"
echo "---------"
curl -s $BASE_URL/network/config | jq .
echo ""

# Пример 3: Имя хоста
echo "[3] Hostname"
echo "---------"
curl -s $BASE_URL/network/hostname | jq .
echo ""

# Пример 4: Статус RTU
echo "[4] RTU Status"
echo "---------"
curl -s $BASE_URL/modbus/rtu/status | jq .
echo ""

# Пример 5: Подключение к RTU
echo "[5] Connecting to RTU"
echo "---------"
curl -s -X POST $BASE_URL/modbus/rtu/connect \
  -H "Content-Type: application/json" \
  -d '{"port": "/dev/ttyUSB0", "baudrate": 9600}' | jq .
echo ""

# Пример 6: Чтение регистров
echo "[6] Reading Holding Registers"
echo "---------"
curl -s -X POST $BASE_URL/modbus/rtu/read \
  -H "Content-Type: application/json" \
  -d '{
    "slave_id": '$SLAVE_ID',
    "type": "holding_registers",
    "start_addr": 0,
    "quantity": 10
  }' | jq .
echo ""

# Пример 7: Чтение входных регистров
echo "[7] Reading Input Registers"
echo "---------"
curl -s -X POST $BASE_URL/modbus/rtu/read \
  -H "Content-Type: application/json" \
  -d '{
    "slave_id": '$SLAVE_ID',
    "type": "input_registers",
    "start_addr": 0,
    "quantity": 5
  }' | jq .
echo ""

# Пример 8: Чтение катушек
echo "[8] Reading Coils"
echo "---------"
curl -s -X POST $BASE_URL/modbus/rtu/read \
  -H "Content-Type: application/json" \
  -d '{
    "slave_id": '$SLAVE_ID',
    "type": "coils",
    "start_addr": 0,
    "quantity": 10
  }' | jq .
echo ""

# Пример 9: Запись одного регистра
echo "[9] Writing Single Register"
echo "---------"
curl -s -X POST $BASE_URL/modbus/rtu/write \
  -H "Content-Type: application/json" \
  -d '{
    "slave_id": '$SLAVE_ID',
    "type": "register",
    "addr": 0,
    "value": 100
  }' | jq .
echo ""

# Пример 10: Запись одной катушки
echo "[10] Writing Single Coil"
echo "---------"
curl -s -X POST $BASE_URL/modbus/rtu/write \
  -H "Content-Type: application/json" \
  -d '{
    "slave_id": '$SLAVE_ID',
    "type": "coil",
    "addr": 0,
    "value": true
  }' | jq .
echo ""

# Пример 11: Запись нескольких регистров
echo "[11] Writing Multiple Registers"
echo "---------"
curl -s -X POST $BASE_URL/modbus/rtu/write \
  -H "Content-Type: application/json" \
  -d '{
    "slave_id": '$SLAVE_ID',
    "type": "registers",
    "addr": 100,
    "value": [1000, 2000, 3000]
  }' | jq .
echo ""

# Пример 12: TCP статус
echo "[12] TCP Server Status"
echo "---------"
curl -s $BASE_URL/modbus/tcp/status | jq .
echo ""

# Пример 13: Запуск TCP сервера
echo "[13] Starting TCP Server"
echo "---------"
curl -s -X POST $BASE_URL/modbus/tcp/start \
  -H "Content-Type: application/json" \
  -d '{"host": "0.0.0.0", "port": 5020}' | jq .
echo ""

# Пример 14: Получить конфигурацию
echo "[14] Get Configuration"
echo "---------"
curl -s $BASE_URL/config/get | jq .
echo ""

echo "All examples completed!"
