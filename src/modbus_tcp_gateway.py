import asyncio
import struct


class ModbusException(Exception):
    def __init__(self, code: int):
        self.code = code


class ModbusTCPGateway:
    """Transparent Modbus TCP -> Modbus RTU gateway (MBAP framing).

    Supports function codes 3 (Read Holding Registers) and 6 (Write Single Register).
    Uses `ModbusRTUManager` methods which are synchronous; blocking calls are executed
    via `asyncio.to_thread` so the asyncio loop stays responsive.
    """

    def __init__(self, rtu_manager, host='0.0.0.0', port=502):
        self.rtu = rtu_manager
        self.host = host
        self.port = port
        self.server = None

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        try:
            while True:
                # Read MBAP header (7 bytes)
                header = await reader.readexactly(7)
                tid, pid, length, uid = struct.unpack('>HHHB', header)
                pdu_len = length - 1
                pdu = await reader.readexactly(pdu_len)

                func = pdu[0]
                resp_pdu = b''
                try:
                    if func == 1 or func == 2:
                        # Read Coils (1) or Read Discrete Inputs (2)
                        if len(pdu) < 5:
                            raise ModbusException(3)
                        addr = struct.unpack('>H', pdu[1:3])[0]
                        count = struct.unpack('>H', pdu[3:5])[0]
                        if func == 1:
                            bits = await asyncio.to_thread(self.rtu.read_coils, uid, addr, count)
                        else:
                            bits = await asyncio.to_thread(self.rtu.read_discrete_inputs, uid, addr, count)
                        bytecount = (count + 7) // 8
                        b = bytearray(bytecount)
                        for i in range(min(len(bits), count)):
                            if bits[i]:
                                byte_index = i // 8
                                bit_index = i % 8
                                b[byte_index] |= (1 << bit_index)
                        resp_pdu = struct.pack('>B B', func, bytecount) + bytes(b)
                    elif func == 3:
                        # Read Holding Registers: request: func(1) + addr(2) + count(2)
                        if len(pdu) < 5:
                            raise ModbusException(3)
                        addr = struct.unpack('>H', pdu[1:3])[0]
                        count = struct.unpack('>H', pdu[3:5])[0]
                        regs = await asyncio.to_thread(self.rtu.read_holding_registers, uid, addr, count)
                        bytecount = len(regs) * 2
                        resp_pdu = struct.pack('>B B', 3, bytecount) + b''.join(struct.pack('>H', r & 0xFFFF) for r in regs)
                    elif func == 6:
                        # Write Single Register: request: func(1) + addr(2) + value(2)
                        if len(pdu) < 5:
                            raise ModbusException(3)
                        addr = struct.unpack('>H', pdu[1:3])[0]
                        value = struct.unpack('>H', pdu[3:5])[0]
                        await asyncio.to_thread(self.rtu.write_register, uid, addr, value)
                        # successful response echoes request
                        resp_pdu = pdu[:5]
                    elif func == 5:
                        # Write Single Coil: func(1) + addr(2) + value(2)
                        if len(pdu) < 5:
                            raise ModbusException(3)
                        addr = struct.unpack('>H', pdu[1:3])[0]
                        value = struct.unpack('>H', pdu[3:5])[0]
                        coil_value = True if value == 0xFF00 else False
                        await asyncio.to_thread(self.rtu.write_coil, uid, addr, coil_value)
                        resp_pdu = pdu[:5]
                    elif func == 15:
                        # Write Multiple Coils: func(1) + addr(2) + qty(2) + bytecount(1) + values
                        if len(pdu) < 6:
                            raise ModbusException(3)
                        addr = struct.unpack('>H', pdu[1:3])[0]
                        qty = struct.unpack('>H', pdu[3:5])[0]
                        bytecount = pdu[5]
                        coils_bytes = pdu[6:6+bytecount]
                        coils = []
                        for i in range(qty):
                            byte_index = i // 8
                            bit_index = i % 8
                            if byte_index < len(coils_bytes):
                                bit = (coils_bytes[byte_index] >> bit_index) & 0x01
                            else:
                                bit = 0
                            coils.append(bool(bit))
                        await asyncio.to_thread(self.rtu.write_coils, uid, addr, coils)
                        resp_pdu = struct.pack('>B H H', 15, addr, qty)
                    elif func == 16:
                        # Write Multiple Registers: func(1) + addr(2) + qty(2) + bytecount(1) + values(2*qty)
                        if len(pdu) < 6:
                            raise ModbusException(3)
                        addr = struct.unpack('>H', pdu[1:3])[0]
                        qty = struct.unpack('>H', pdu[3:5])[0]
                        bytecount = pdu[5]
                        regs_bytes = pdu[6:6+bytecount]
                        regs = []
                        for i in range(qty):
                            off = i*2
                            if off+1 < len(regs_bytes):
                                val = struct.unpack('>H', regs_bytes[off:off+2])[0]
                            else:
                                val = 0
                            regs.append(val)
                        await asyncio.to_thread(self.rtu.write_registers, uid, addr, regs)
                        resp_pdu = struct.pack('>B H H', 16, addr, qty)
                    elif func == 22:
                        # Mask Write Register (0x16): func(1) + ref_addr(2) + and_mask(2) + or_mask(2)
                        if len(pdu) < 7:
                            raise ModbusException(3)
                        addr = struct.unpack('>H', pdu[1:3])[0]
                        and_mask = struct.unpack('>H', pdu[3:5])[0]
                        or_mask = struct.unpack('>H', pdu[5:7])[0]
                        await asyncio.to_thread(self.rtu.mask_write_register, uid, addr, and_mask, or_mask)
                        # response echoes the request (func + addr + and + or)
                        resp_pdu = pdu[:7]
                    else:
                        # Illegal function
                        raise ModbusException(1)
                except ModbusException as me:
                    resp_pdu = struct.pack('>B B', func | 0x80, me.code)
                except Exception:
                    # Slave device failure
                    resp_pdu = struct.pack('>B B', func | 0x80, 4)

                # Build MBAP for response: tid(2), pid(2=0), length(2)=unitId+PDU, unitId(1)
                mbap = struct.pack('>HHH', tid, 0, len(resp_pdu) + 1) + struct.pack('>B', uid)
                writer.write(mbap + resp_pdu)
                await writer.drain()
        except asyncio.IncompleteReadError:
            pass
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
