import aiohttp
from aiohttp import web
import json
import ipaddress
import subprocess
import os
from datetime import datetime
from pathlib import Path
from . import ntp_sync


async def index(request):
    return web.Response(text="<html><head><meta charset='utf-8'><title>SmartHome Controller</title></head><body><h1>SmartHome Controller</h1><a href='/ui/config'>Open Settings</a></body></html>", content_type='text/html')


async def ui_config_page(request):
    html = """
    <html><head><meta charset='utf-8'><title>Settings</title>
    <style>label{display:block;margin-top:8px}input,textarea{width:320px}</style>
    </head>
    <body>
    <h2>Settings</h2>
    <h3>LAN</h3>
    <form id='lan'>
      <label>Hostname: <input id='hostname' name='hostname'></label>
      <label><input type='checkbox' id='dhcp' name='dhcp'> Use DHCP</label>
      <label>Address: <input id='address' name='address'></label>
      <label>Netmask: <input id='netmask' name='netmask'></label>
      <label>Gateway: <input id='gateway' name='gateway'></label>
      <button type='button' onclick='saveLan()'>Save & Apply LAN</button>
      <pre id='lan_msg'></pre>
    </form>

    <h3>NTP</h3>
    <form id='ntp'>
      <label>Servers (comma separated): <input id='ntp_servers' name='ntp_servers'></label>
      <button type='button' onclick='saveNtp()'>Save & Sync NTP</button>
      <pre id='ntp_msg'></pre>
    </form>

    <h3>Modbus RTU</h3>
    <form id='modbus'>
      <label>Port: <input id='rtu_port' name='rtu_port'></label>
      <label>Baudrate: <input id='rtu_baud' name='rtu_baud'></label>
      <button type='button' onclick='saveModbus()'>Save Modbus</button>
      <pre id='modbus_msg'></pre>
    </form>

    <script>
    function show(id,msg){document.getElementById(id).innerText=msg}
    async function load(){
      let r=await fetch('/api/config'); let j=await r.json();
      document.getElementById('hostname').value=j.lan.hostname||'';
      document.getElementById('dhcp').checked=!!j.lan.dhcp;
      document.getElementById('address').value=j.lan.address||'';
      document.getElementById('netmask').value=j.lan.netmask||'';
      document.getElementById('gateway').value=j.lan.gateway||'';
      document.getElementById('rtu_port').value=j.modbus_rtu.port||'';
      document.getElementById('rtu_baud').value=j.modbus_rtu.baudrate||'';
      document.getElementById('ntp_servers').value=(j.ntp && j.ntp.servers)? j.ntp.servers.join(',') : '';
    }

    function validIP(ip){try{if(!ip) return false; return !!(ip && ip.split('.').length===4); }catch(e){return false}}

    async function saveLan(){
      const payload={lan:{hostname:document.getElementById('hostname').value, dhcp:document.getElementById('dhcp').checked, address:document.getElementById('address').value, netmask:document.getElementById('netmask').value, gateway:document.getElementById('gateway').value}};
      // simple validation
      if(!payload.lan.hostname){show('lan_msg','Hostname required'); return}
      if(!payload.lan.dhcp){ if(!validIP(payload.lan.address) || !validIP(payload.lan.gateway)){show('lan_msg','Invalid IP or gateway'); return} }
      let r=await fetch('/api/apply_lan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
      let j=await r.json(); show('lan_msg', JSON.stringify(j,null,2));
    }

    async function saveNtp(){
      const servers = document.getElementById('ntp_servers').value.split(',').map(s=>s.trim()).filter(Boolean);
      if(servers.length===0){show('ntp_msg','Provide at least one server'); return}
      let r=await fetch('/api/apply_ntp',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({ntp:{servers}})});
      let j=await r.json(); show('ntp_msg', JSON.stringify(j,null,2));
    }

    async function saveModbus(){
      const payload={modbus_rtu:{port:document.getElementById('rtu_port').value, baudrate: parseInt(document.getElementById('rtu_baud').value||0)}};
      let r=await fetch('/api/config',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
      let t=await r.text(); show('modbus_msg', t);
    }

    load();
    </script>
    </body></html>
    """
    return web.Response(text=html, content_type='text/html')


def create_app(config, rtu_manager):
    app = web.Application()
    app['config'] = config
    app['rtu'] = rtu_manager
    app.add_routes([
        web.get('/', index),
        web.get('/ui/config', ui_config_page),
        web.get('/api/config', api_get_config),
        web.post('/api/config', api_post_config),
        web.post('/api/modbus/read', api_modbus_read),
        web.post('/api/apply_lan', api_apply_lan),
        web.post('/api/apply_ntp', api_apply_ntp),
        web.get('/api/ntp_status', api_ntp_status),
        web.post('/api/preview_lan', api_preview_lan)
    ])
    return app


async def api_get_config(request):
    cfg = request.app['config'].data
    return web.json_response(cfg)


async def api_post_config(request):
    data = await request.json()
    cfg = request.app['config']
    # merge incoming top-level keys
    for k, v in data.items():
        cfg.data.setdefault(k, {})
        if isinstance(v, dict):
            cfg.data[k].update(v)
        else:
            cfg.data[k] = v
    cfg.save()
    return web.Response(text='ok')


async def api_modbus_read(request):
    data = await request.json()
    unit = int(data.get('unit', 1))
    addr = int(data.get('address', 0))
    count = int(data.get('count', 1))
    try:
        regs = request.app['rtu'].read_holding_registers(unit, addr, count)
        return web.json_response({'ok': True, 'registers': regs})
    except Exception as e:
        return web.json_response({'ok': False, 'error': str(e)})


def _netmask_to_prefix(netmask: str) -> int:
    try:
        return ipaddress.IPv4Network('0.0.0.0/' + netmask).prefixlen
    except Exception:
        # support dotted netmask
        try:
            return sum(bin(int(x)).count('1') for x in netmask.split('.'))
        except Exception:
            return 24


async def api_apply_lan(request):
    data = await request.json()
    lan = data.get('lan') or {}
    cfg = request.app['config']
    # basic validation
    hostname = lan.get('hostname')
    dhcp = bool(lan.get('dhcp', True))
    address = lan.get('address')
    netmask = lan.get('netmask')
    gateway = lan.get('gateway')
    if not hostname:
        return web.json_response({'ok': False, 'error': 'hostname_required'}, status=400)
    if not dhcp:
        try:
            ipaddress.IPv4Address(address)
            ipaddress.IPv4Address(gateway)
        except Exception:
            return web.json_response({'ok': False, 'error': 'invalid_ip'}, status=400)

    cfg.data.setdefault('lan', {})
    cfg.data['lan'].update({'hostname': hostname, 'dhcp': dhcp, 'address': address, 'netmask': netmask, 'gateway': gateway})
    cfg.save()

    result = {'ok': True, 'actions': [], 'applied': []}
    # log requested change
    _log_action('apply_lan_request', {'lan': cfg.data['lan']})

    # try to set hostname
    try:
        subprocess.run(['sudo', 'hostnamectl', 'set-hostname', hostname], check=True)
        result['actions'].append('hostname_set')
        result['applied'].append('hostname')
    except Exception as e:
        result['actions'].append('hostname_set_failed:' + str(e))

    nmcli_ok = False
    # apply IP via nmcli if available
    try:
        proc = subprocess.run(['nmcli', '-t', '-f', 'NAME,DEVICE', 'connection', 'show', '--active'], capture_output=True, text=True, check=False)
        lines = [l for l in proc.stdout.splitlines() if l.strip()]
        if lines:
            conn = lines[0].split(':', 1)[0]
            if dhcp:
                subprocess.run(['sudo', 'nmcli', 'connection', 'modify', conn, 'ipv4.method', 'auto'], check=True)
                subprocess.run(['sudo', 'nmcli', 'connection', 'up', conn], check=True)
                result['actions'].append('nmcli_set_dhcp')
            else:
                prefix = str(_netmask_to_prefix(netmask))
                addr_with_prefix = f"{address}/{prefix}"
                subprocess.run(['sudo', 'nmcli', 'connection', 'modify', conn, 'ipv4.method', 'manual', 'ipv4.addresses', addr_with_prefix, 'ipv4.gateway', gateway], check=True)
                subprocess.run(['sudo', 'nmcli', 'connection', 'up', conn], check=True)
                result['actions'].append('nmcli_set_static')
            nmcli_ok = True
            result['applied'].append('nmcli')
        else:
            result['actions'].append('no_active_connection')
    except Exception as e:
        result['actions'].append('nmcli_failed:' + str(e))

    # if nmcli not available or failed, try netplan (common on Ubuntu servers)
    if not nmcli_ok:
        try:
            prefix = str(_netmask_to_prefix(netmask))
            netplan_yaml = _build_netplan_yaml(address, prefix, gateway, dhcp)
            # write netplan file via sudo tee
            subprocess.run(['sudo', 'tee', '/etc/netplan/99-smarthome.yaml'], input=netplan_yaml.encode('utf-8'), check=True)
            subprocess.run(['sudo', 'netplan', 'apply'], check=True)
            result['actions'].append('netplan_applied')
            result['applied'].append('netplan')
        except Exception as e:
            result['actions'].append('netplan_failed:' + str(e))

    _log_action('apply_lan_result', result)
    return web.json_response(result)


def _build_netplan_yaml(address, prefix, gateway, dhcp):
    iface = _detect_interface()
    if not iface:
        iface = 'eth0'
    if dhcp:
        yaml = f"""network:\n  version: 2\n  ethernets:\n    {iface}:\n      dhcp4: true\n"""
    else:
        yaml = f"""network:\n  version: 2\n  ethernets:\n    {iface}:\n      addresses: [ {address}/{prefix} ]\n      gateway4: {gateway}\n      nameservers:\n        addresses: [8.8.8.8,8.8.4.4]\n"""
    return yaml


def _log_action(action: str, details: dict):
    try:
        p = Path('logs')
        p.mkdir(exist_ok=True)
        lf = p / 'actions.log'
        entry = {'time': datetime.utcnow().isoformat() + 'Z', 'action': action, 'details': details}
        with open(lf, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


async def api_preview_lan(request):
    data = await request.json()
    lan = data.get('lan') or {}
    hostname = lan.get('hostname')
    dhcp = bool(lan.get('dhcp', True))
    address = lan.get('address')
    netmask = lan.get('netmask')
    gateway = lan.get('gateway')
    preview = {'commands': [], 'netplan': None}
    preview['commands'].append(['hostnamectl', 'set-hostname', hostname])
    prefix = str(_netmask_to_prefix(netmask))
    addr_with_prefix = f"{address}/{prefix}"
    # nmcli commands (preview)
    preview['commands'].append(['nmcli', 'connection', 'modify', '<conn>', 'ipv4.method', 'auto' if dhcp else 'manual'])
    if not dhcp:
        preview['commands'].append(['nmcli', 'connection', 'modify', '<conn>', 'ipv4.addresses', addr_with_prefix, 'ipv4.gateway', gateway])
    # netplan
    preview['netplan'] = _build_netplan_yaml(address, prefix, gateway, dhcp)
    _log_action('preview_lan', {'preview': preview})
    return web.json_response(preview)


def _detect_interface():
    # Try nmcli to find connected device
    try:
        proc = subprocess.run(['nmcli', '-t', '-f', 'DEVICE,STATE', 'device', 'status'], capture_output=True, text=True, check=False)
        for line in proc.stdout.splitlines():
            if not line.strip():
                continue
            parts = line.split(':')
            if len(parts) >= 2:
                dev, state = parts[0], parts[1]
                if state.lower() in ('connected', 'connected_vlan', 'connected (externally-managed)'):
                    return dev
    except Exception:
        pass

    # Fallback: use ip route to determine interface used for default route
    try:
        proc = subprocess.run(['ip', 'route', 'get', '8.8.8.8'], capture_output=True, text=True, check=False)
        out = proc.stdout
        if out:
            for token in out.split():
                if token == 'dev':
                    idx = out.split().index('dev')
                    if idx + 1 < len(out.split()):
                        return out.split()[idx + 1]
    except Exception:
        pass

    # Last resort: pick first non-loopback interface
    try:
        for name in os.listdir('/sys/class/net'):
            if name == 'lo' or name.startswith('docker') or name.startswith('veth'):
                continue
            return name
    except Exception:
        pass

    return None
