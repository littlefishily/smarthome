import ntplib
import subprocess
from time import ctime

def query_servers(servers):
    c = ntplib.NTPClient()
    results = {}
    for s in servers:
        try:
            r = c.request(s, version=3)
            results[s] = {'tx_time': r.tx_time, 'tx_time_str': ctime(r.tx_time)}
        except Exception as e:
            results[s] = {'error': str(e)}
    return results

def apply_system_ntp(enable=True):
    # Enable systemd-timesyncd/ntp using timedatectl
    try:
        subprocess.run(['sudo', 'timedatectl', 'set-ntp', 'true' if enable else 'false'], check=True)
        return True
    except Exception:
        return False

def sync_once(server):
    try:
        subprocess.run(['sudo', 'ntpdate', '-u', server], check=True)
        return True
    except Exception:
        return False
