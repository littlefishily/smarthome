from typing import List, Dict, Optional


class SlaveManager:
    """Manage Modbus RTU slave device entries persisted in Config.data['slaves']."""

    def __init__(self, config):
        self.config = config
        self._ensure()

    def _ensure(self):
        self.config.data.setdefault('slaves', [])

    def list_slaves(self) -> List[Dict]:
        return list(self.config.data.get('slaves', []))

    def get_slave(self, unit: int) -> Optional[Dict]:
        for s in self.config.data.get('slaves', []):
            if int(s.get('unit')) == int(unit):
                return s
        return None

    def add_slave(self, entry: Dict) -> Dict:
        # ensure unit present
        unit = int(entry.get('unit'))
        if self.get_slave(unit):
            raise ValueError(f"slave with unit {unit} already exists")
        e = {'unit': unit, 'name': entry.get('name', ''), 'description': entry.get('description', '')}
        self.config.data.setdefault('slaves', []).append(e)
        self.config.save()
        return e

    def update_slave(self, unit: int, entry: Dict) -> Dict:
        s = self.get_slave(unit)
        if not s:
            raise KeyError(f"slave {unit} not found")
        s['name'] = entry.get('name', s.get('name', ''))
        s['description'] = entry.get('description', s.get('description', ''))
        self.config.save()
        return s

    def remove_slave(self, unit: int) -> bool:
        lst = self.config.data.get('slaves', [])
        for i, s in enumerate(lst):
            if int(s.get('unit')) == int(unit):
                lst.pop(i)
                self.config.save()
                return True
        return False

    def scan(self, rtu_manager, start: int = 1, end: int = 32, probe_address: int = 0):
        """Scan for active Modbus units by probing a register. Returns list of discovered unit ints."""
        found = []
        for unit in range(start, end + 1):
            try:
                # try reading one holding register at probe_address
                regs = rtu_manager.read_holding_registers(unit, probe_address, 1)
                # if we get a response (list/tuple), consider device present
                if regs is not None:
                    if not self.get_slave(unit):
                        # add with a generic name
                        self.add_slave({'unit': unit, 'name': f'slave-{unit}', 'description': ''})
                    found.append(unit)
            except Exception:
                # no response or error — ignore
                continue
        return found
