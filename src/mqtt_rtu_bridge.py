import asyncio
import json
from asyncio_mqtt import Client, MqttError

class MQTTRTUBridge:
    def __init__(self, rtu_manager, broker='localhost', port=1883, username='', password=''):
        self.rtu = rtu_manager
        self.broker = broker
        self.port = port
        self.username = username
        self.password = password
        self._task = None

    async def _run(self):
        try:
            async with Client(self.broker, port=self.port, username=self.username or None, password=self.password or None) as client:
                async with client.unfiltered_messages() as messages:
                    await client.subscribe('modbus/rtu/request')
                    async for msg in messages:
                        try:
                            payload = msg.payload.decode('utf-8')
                            req = json.loads(payload)
                            if req.get('cmd') == 'read_holding':
                                unit = int(req.get('unit', 1))
                                address = int(req.get('address', 0))
                                count = int(req.get('count', 1))
                                regs = self.rtu.read_holding_registers(unit, address, count)
                                resp = {'ok': True, 'registers': regs}
                            else:
                                resp = {'ok': False, 'error': 'unknown_cmd'}
                        except Exception as e:
                            resp = {'ok': False, 'error': str(e)}
                        await client.publish('modbus/rtu/response', json.dumps(resp))
        except MqttError:
            await asyncio.sleep(5)

    def start(self):
        self._task = asyncio.create_task(self._run())

    async def stop(self):
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except Exception:
                pass
