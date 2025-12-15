import asyncio
import json
from typing import Callable

class TCPRTUGateway:
    """Simple JSON-over-TCP gateway: client sends JSON request and receives JSON response.

    Request example: {"cmd": "read_holding", "unit": 1, "address": 0, "count": 2}
    Response: {"ok": true, "registers": [0,1]} or {"ok": false, "error": "..."}
    """
    def __init__(self, rtu_manager, host='0.0.0.0', port=5020):
        self.rtu = rtu_manager
        self.host = host
        self.port = port
        self.server = None

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        addr = writer.get_extra_info('peername')
        try:
            data = await reader.readline()
            if not data:
                writer.close()
                await writer.wait_closed()
                return
            req = json.loads(data.decode('utf-8').strip())
            resp = {'ok': False}
            try:
                if req.get('cmd') == 'read_holding':
                    unit = int(req.get('unit', 1))
                    address = int(req.get('address', 0))
                    count = int(req.get('count', 1))
                    regs = self.rtu.read_holding_registers(unit, address, count)
                    resp = {'ok': True, 'registers': regs}
                elif req.get('cmd') == 'write':
                    unit = int(req.get('unit', 1))
                    address = int(req.get('address', 0))
                    value = int(req.get('value', 0))
                    self.rtu.write_register(unit, address, value)
                    resp = {'ok': True}
                else:
                    resp = {'ok': False, 'error': 'unknown_cmd'}
            except Exception as e:
                resp = {'ok': False, 'error': str(e)}
            out = (json.dumps(resp) + "\n").encode('utf-8')
            writer.write(out)
            await writer.drain()
        except Exception:
            pass
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    async def start(self):
        self.server = await asyncio.start_server(self.handle_client, self.host, self.port)

    async def stop(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()
