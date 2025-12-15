// Функции управления вкладками
function switchTab(tabName) {
    // Скрыть все вкладки
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    // Деактивировать все кнопки вкладок
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });

    // Показать выбранную вкладку
    document.getElementById(tabName).classList.add('active');

    // Активировать соответствующую кнопку
    event.target.classList.add('active');

    // Загрузить данные вкладки
    if (tabName === 'network') {
        refreshNetworkConfig();
    } else if (tabName === 'modbus-tcp') {
        refreshTCPStatus();
    } else if (tabName === 'config') {
        loadConfig();
    }
}

// Функции для сетевых настроек
function setHostname() {
    const hostname = document.getElementById('hostname-input').value;
    if (!hostname) {
        alert('Пожалуйста, введите имя хоста');
        return;
    }

    fetch('/api/network/hostname', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ hostname: hostname })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Имя хоста установлено успешно');
            refreshNetworkConfig();
        } else {
            alert('Ошибка при установке имени хоста');
        }
    })
    .catch(error => console.error('Error:', error));
}

function refreshNetworkConfig() {
    fetch('/api/network/config')
    .then(response => response.json())
    .then(data => {
        let html = '';
        
        if (data.interfaces) {
            html += '<div><strong>Интерфейсы:</strong></div>';
            for (const [iface, info] of Object.entries(data.interfaces)) {
                html += `<div style="margin-left: 20px;">
                    <strong>${iface}:</strong> ${info.ip} (${info.status})
                </div>`;
            }
        }
        
        if (data.hostname) {
            html += `<div><strong>Имя хоста:</strong> ${data.hostname}</div>`;
            document.getElementById('hostname-input').value = data.hostname;
        }
        
        document.getElementById('network-info').innerHTML = html || 'Нет данных';
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('network-info').innerHTML = 'Ошибка загрузки данных';
    });
}

// Функции для Modbus RTU
function connectRTU() {
    const port = document.getElementById('rtu-port').value;
    const baudrate = parseInt(document.getElementById('rtu-baudrate').value);

    fetch('/api/modbus/rtu/connect', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            port: port,
            baudrate: baudrate
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showStatus('RTU подключен успешно', 'success');
            updateRTUStatus();
        } else {
            showStatus('Ошибка подключения: ' + (data.error || 'Unknown error'), 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showStatus('Ошибка: ' + error, 'error');
    });
}

function disconnectRTU() {
    fetch('/api/modbus/rtu/disconnect', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showStatus('RTU отключен', 'success');
            updateRTUStatus();
        } else {
            showStatus('Ошибка отключения', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showStatus('Ошибка: ' + error, 'error');
    });
}

function readRTU() {
    const slaveId = parseInt(document.getElementById('rtu-read-slave').value);
    const type = document.getElementById('rtu-read-type').value;
    const startAddr = parseInt(document.getElementById('rtu-read-start').value);
    const quantity = parseInt(document.getElementById('rtu-read-qty').value);

    fetch('/api/modbus/rtu/read', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            slave_id: slaveId,
            type: type,
            start_addr: startAddr,
            quantity: quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        const resultDiv = document.getElementById('rtu-read-result');
        if (data.success) {
            resultDiv.className = 'result-panel success';
            resultDiv.innerHTML = `<strong>Данные:</strong> ${JSON.stringify(data.data)}`;
        } else {
            resultDiv.className = 'result-panel error';
            resultDiv.innerHTML = `<strong>Ошибка:</strong> ${data.error}`;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('rtu-read-result').innerHTML = 'Ошибка: ' + error;
    });
}

function writeRTU() {
    const slaveId = parseInt(document.getElementById('rtu-write-slave').value);
    const type = document.getElementById('rtu-write-type').value;
    const addr = parseInt(document.getElementById('rtu-write-addr').value);
    let value = document.getElementById('rtu-write-value').value;

    // Попытаться распарсить как JSON если выглядит как массив
    if (value.startsWith('[')) {
        try {
            value = JSON.parse(value);
        } catch (e) {
            alert('Неверный формат JSON для массива');
            return;
        }
    } else if (type === 'coil' || type === 'register') {
        value = isNaN(value) ? (value.toLowerCase() === 'true' ? 1 : 0) : parseInt(value);
    }

    fetch('/api/modbus/rtu/write', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            slave_id: slaveId,
            type: type,
            addr: addr,
            value: value
        })
    })
    .then(response => response.json())
    .then(data => {
        const resultDiv = document.getElementById('rtu-write-result');
        if (data.success) {
            resultDiv.className = 'result-panel success';
            resultDiv.innerHTML = '<strong>Успешно!</strong> Данные записаны';
        } else {
            resultDiv.className = 'result-panel error';
            resultDiv.innerHTML = `<strong>Ошибка:</strong> ${data.error}`;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('rtu-write-result').innerHTML = 'Ошибка: ' + error;
    });
}

function updateRTUStatus() {
    fetch('/api/modbus/rtu/status')
    .then(response => response.json())
    .then(data => {
        const statusDiv = document.getElementById('rtu-status');
        if (data.connected) {
            statusDiv.innerHTML = `RTU: <span class="badge online">Подключено</span>`;
        } else {
            statusDiv.innerHTML = `RTU: <span class="badge offline">Отключено</span>`;
        }
    })
    .catch(error => console.error('Error:', error));
}

// Функции для Modbus TCP
function startTCPServer() {
    const host = document.getElementById('tcp-host').value;
    const port = parseInt(document.getElementById('tcp-port').value);

    fetch('/api/modbus/tcp/start', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            host: host,
            port: port
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showStatus('TCP сервер запущен успешно', 'success');
            refreshTCPStatus();
        } else {
            showStatus('Ошибка запуска: ' + (data.error || 'Unknown error'), 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showStatus('Ошибка: ' + error, 'error');
    });
}

function stopTCPServer() {
    fetch('/api/modbus/tcp/stop', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showStatus('TCP сервер остановлен', 'success');
            refreshTCPStatus();
        } else {
            showStatus('Ошибка остановки', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showStatus('Ошибка: ' + error, 'error');
    });
}

function refreshTCPStatus() {
    fetch('/api/modbus/tcp/status')
    .then(response => response.json())
    .then(data => {
        let html = '';
        
        if (data.error) {
            html = 'Ошибка загрузки статуса';
        } else {
            html = `<div><strong>Статус:</strong> ${data.running ? 'Запущен' : 'Остановлен'}</div>`;
            html += `<div><strong>Хост:</strong> ${data.host}</div>`;
            html += `<div><strong>Порт:</strong> ${data.port}</div>`;
        }
        
        document.getElementById('tcp-status-info').innerHTML = html;

        // Обновить статус в шапке
        const statusDiv = document.getElementById('tcp-status');
        if (data.running) {
            statusDiv.innerHTML = `TCP: <span class="badge online">Запущено</span>`;
        } else {
            statusDiv.innerHTML = `TCP: <span class="badge offline">Остановлено</span>`;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('tcp-status-info').innerHTML = 'Ошибка загрузки данных';
    });
}

// Функции для конфигурации
function loadConfig() {
    fetch('/api/config/get')
    .then(response => response.json())
    .then(data => {
        document.getElementById('config-editor').value = JSON.stringify(data, null, 2);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Ошибка загрузки конфигурации');
    });
}

function saveConfig() {
    const configText = document.getElementById('config-editor').value;
    
    try {
        const config = JSON.parse(configText);
        
        fetch('/api/config/update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showStatus('Конфигурация сохранена успешно', 'success');
            } else {
                showStatus('Ошибка сохранения конфигурации', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showStatus('Ошибка: ' + error, 'error');
        });
    } catch (e) {
        alert('Ошибка парсинга JSON: ' + e.message);
    }
}

// Функция для вывода статуса
function showStatus(message, type) {
    // Можно добавить toast уведомление
    console.log(`[${type.toUpperCase()}] ${message}`);
    alert(message);
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    updateRTUStatus();
    refreshTCPStatus();
    refreshNetworkConfig();

    // Обновлять статус каждые 5 секунд
    setInterval(() => {
        updateRTUStatus();
        refreshTCPStatus();
    }, 5000);
});
