"""Resumen legible de ERC y DRC."""
import json, collections
from pathlib import Path
B = Path(__file__).resolve().parent.parent / 'build'
e = json.loads((B / 'sch/erc.json').read_text()); ev = [v for s in e['sheets'] for v in s['violations']]
print('ERC:', collections.Counter(v['severity'] for v in ev) or 'limpio')
for v in ev: print('  ', v['severity'], v['type'], [i['description'][:70] for i in v['items']])
d = json.loads((B / 'pcb/drc.json').read_text())
print('DRC:', dict(collections.Counter(v['type'] for v in d['violations'])) or 'limpio', '| sin conectar:', len(d['unconnected_items']), '| paridad:', len(d.get('schematic_parity', [])))
for v in (d['violations'] + d['unconnected_items'] + d.get('schematic_parity', []))[:15]:
    print('  ', v['severity'], v['type'], [(i['description'][:55], round(i['pos']['x'], 1), round(i['pos']['y'], 1)) for i in v['items']])
