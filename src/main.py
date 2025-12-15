import asyncio
import signal
from aiohttp import web
from src.config import Config
from src.modbus_rtu import ModbusRTUManager
from src.tcp_rtu_gateway import TCPRTUGateway
from src.modbus_tcp_gateway import ModbusTCPGateway
from src.mqtt_rtu_bridge import MQTTRTUBridge
from src.webui import create_app


async def main():
	cfg = Config('config.yaml')

	rtu_cfg = cfg.get('modbus_rtu', {})
	rtu = ModbusRTUManager(port=rtu_cfg.get('port', '/dev/ttyUSB0'),
						  baudrate=rtu_cfg.get('baudrate', 19200),
						  parity=rtu_cfg.get('parity', 'N'),
						  stopbits=rtu_cfg.get('stopbits', 1),
						  timeout=rtu_cfg.get('timeout', 2))

	print('Connecting to Modbus RTU...')
	try:
		ok = rtu.connect()
		print('Modbus RTU connected:', ok)
	except Exception as e:
		print('Modbus RTU connect failed:', e)

	# start TCP gateway (JSON-over-TCP) and transparent Modbus-TCP
	tcp_cfg = cfg.get('modbus_tcp', {})
	tcp_gateway = TCPRTUGateway(rtu, host='0.0.0.0', port=tcp_cfg.get('listen_port', 5020))
	mbtcp_port = tcp_cfg.get('mb_port', 502)
	modbus_tcp_gateway = ModbusTCPGateway(rtu, host='0.0.0.0', port=mbtcp_port)

	# start MQTT bridge
	mqtt_cfg = cfg.get('mqtt', {})
	mqtt_bridge = MQTTRTUBridge(rtu, broker=mqtt_cfg.get('broker', 'localhost'), port=mqtt_cfg.get('port', 1883), username=mqtt_cfg.get('username',''), password=mqtt_cfg.get('password',''))

	# web app
	app = create_app(cfg, rtu)
	runner = web.AppRunner(app)
	await runner.setup()
	site = web.TCPSite(runner, '0.0.0.0', 8080)

	# start services
	await tcp_gateway.start()
	await modbus_tcp_gateway.start()
	mqtt_bridge.start()
	await site.start()

	print('Web UI available on http://0.0.0.0:8080')
	print('TCP gateway listening on', tcp_gateway.port)

	# wait for termination
	stop_event = asyncio.Event()

	def _on_signal(*_):
		stop_event.set()

	loop = asyncio.get_running_loop()
	try:
		loop.add_signal_handler(signal.SIGINT, _on_signal)
		loop.add_signal_handler(signal.SIGTERM, _on_signal)
	except Exception:
		pass

	await stop_event.wait()

	print('Stopping...')
	await tcp_gateway.stop()
	await modbus_tcp_gateway.stop()
	await mqtt_bridge.stop()
	await runner.cleanup()
	rtu.close()


if __name__ == '__main__':
	asyncio.run(main())
