# Support multiple pymodbus versions: try common import locations
try:
    from pymodbus.client.sync import ModbusSerialClient as ModbusClient
except Exception:
    try:
        from pymodbus.client import ModbusSerialClient as ModbusClient
    except Exception:
        try:
            from pymodbus.client.serial import ModbusSerialClient as ModbusClient
        except Exception:
            ModbusClient = None

if ModbusClient is None:
    raise ImportError("pymodbus ModbusSerialClient not found. Install 'pymodbus' (v2.x) or adjust imports.")

class ModbusRTUManager:
    def __init__(self, port='/dev/ttyUSB0', baudrate=19200, parity='N', stopbits=1, timeout=2):
        self.port = port
        self.baudrate = baudrate
        self.parity = parity
        self.stopbits = stopbits
        self.timeout = timeout
        self.client = None

    def connect(self):
        if self.client and self.client.connect():
            return True
        self.client = ModbusClient(method='rtu', port=self.port, baudrate=self.baudrate,
                                   parity=self.parity, stopbits=self.stopbits, timeout=self.timeout)
        return self.client.connect()

    def close(self):
        if self.client:
            try:
                self.client.close()
            except Exception:
                pass

    def read_holding_registers(self, unit, address, count):
        if not self.client:
            raise RuntimeError('Modbus client not connected')
        rr = self.client.read_holding_registers(address, count, unit=unit)
        if rr is None:
            raise RuntimeError('No response')
        if hasattr(rr, 'isError') and rr.isError():
            raise RuntimeError(f'Modbus error: {rr}')
        return getattr(rr, 'registers', [])

    def write_register(self, unit, address, value):
        if not self.client:
            raise RuntimeError('Modbus client not connected')
        wr = self.client.write_register(address, value, unit=unit)
        if hasattr(wr, 'isError') and wr.isError():
            raise RuntimeError(f'Modbus write error: {wr}')
        return True

    def write_registers(self, unit, address, values):
        if not self.client:
            raise RuntimeError('Modbus client not connected')
        wr = self.client.write_registers(address, values, unit=unit)
        if hasattr(wr, 'isError') and wr.isError():
            raise RuntimeError(f'Modbus write error: {wr}')
        return True

    def write_coil(self, unit, address, value: bool):
        if not self.client:
            raise RuntimeError('Modbus client not connected')
        wr = self.client.write_coil(address, value, unit=unit)
        if hasattr(wr, 'isError') and wr.isError():
            raise RuntimeError(f'Modbus write coil error: {wr}')
        return True

    def write_coils(self, unit, address, values):
        if not self.client:
            raise RuntimeError('Modbus client not connected')
        wr = self.client.write_coils(address, values, unit=unit)
        if hasattr(wr, 'isError') and wr.isError():
            raise RuntimeError(f'Modbus write coils error: {wr}')
        return True

    def mask_write_register(self, unit, address, and_mask, or_mask):
        if not self.client:
            raise RuntimeError('Modbus client not connected')
        # pymodbus has mask_write_register
        if not hasattr(self.client, 'mask_write_register'):
            raise RuntimeError('mask_write_register not supported by client')
        wr = self.client.mask_write_register(address, and_mask, or_mask, unit=unit)
        if hasattr(wr, 'isError') and wr.isError():
            raise RuntimeError(f'Modbus mask write error: {wr}')
        return True

    def read_coils(self, unit, address, count):
        if not self.client:
            raise RuntimeError('Modbus client not connected')
        rr = self.client.read_coils(address, count, unit=unit)
        if rr is None:
            raise RuntimeError('No response')
        if hasattr(rr, 'isError') and rr.isError():
            raise RuntimeError(f'Modbus error: {rr}')
        bits = getattr(rr, 'bits', None)
        if bits is None:
            return []
        return [bool(b) for b in bits[:count]]

    def read_discrete_inputs(self, unit, address, count):
        if not self.client:
            raise RuntimeError('Modbus client not connected')
        rr = self.client.read_discrete_inputs(address, count, unit=unit)
        if rr is None:
            raise RuntimeError('No response')
        if hasattr(rr, 'isError') and rr.isError():
            raise RuntimeError(f'Modbus error: {rr}')
        bits = getattr(rr, 'bits', None)
        if bits is None:
            return []
        return [bool(b) for b in bits[:count]]
