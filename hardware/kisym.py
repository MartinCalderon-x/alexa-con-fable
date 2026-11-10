"""Lectura mínima de bibliotecas de símbolos de KiCad: bloque, herencia y pines."""
import re
from pathlib import Path
SHARE = Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport')

def _block(text, start):
    depth = 0; in_str = False; i = start
    while i < len(text):
        c = text[i]
        if in_str:
            if c == '\\': i += 1
            elif c == '"': in_str = False
        elif c == '"': in_str = True
        elif c == '(': depth += 1
        elif c == ')':
            depth -= 1
            if depth == 0: return text[start:i + 1]
        i += 1
    raise ValueError('bloque sin cerrar')

_cache = {}
def raw(lib, name):
    text = _cache.setdefault(lib, (SHARE / 'symbols' / f'{lib}.kicad_sym').read_text())
    m = re.search(r'\(symbol "%s"\s' % re.escape(name), text)
    if not m: raise KeyError(f'{lib}:{name}')
    return _block(text, m.start())

def prop(block, key):
    m = re.search(r'\(property "%s" "((?:[^"\\]|\\.)*)"' % re.escape(key), block)
    return m.group(1) if m else ''

def flat(lib, name):
    """Símbolo listo para incrustar en lib_symbols (herencia resuelta)."""
    b = raw(lib, name)
    m = re.search(r'\(extends "([^"]+)"\)', b)
    if m:
        parent = m.group(1); pb = flat(lib, parent).replace(f'(symbol "{lib}:{parent}"', f'(symbol "{parent}"', 1)
        pb = pb.replace(f'(symbol "{parent}_', f'(symbol "{name}_').replace(f'(symbol "{parent}"', f'(symbol "{name}"', 1)
        for key in re.findall(r'\(property "([^"]+)"', b):
            v = prop(b, key)
            pb = re.sub(r'(\(property "%s" )"(?:[^"\\]|\\.)*"' % key, lambda mm: mm.group(1) + '"' + v.replace('\\', '\\\\') + '"', pb, count=1)
        b = pb
    return b.replace(f'(symbol "{name}"', f'(symbol "{lib}:{name}"', 1)

PIN = re.compile(r'\(pin (\w+) \w+\s*\(at ([-\d.]+) ([-\d.]+) (\d+)\)\s*\(length ([\d.]+)\)(\s*\(hide yes\))?\s*\(name "([^"]*)"[\s\S]*?\(number "([^"]*)"')
def pins(lib, name, unit=1):
    b = flat(lib, name); out = []
    for m in re.finditer(r'\(symbol "%s_(\d+)_(\d+)"' % re.escape(name), b):
        if int(m.group(1)) not in (0, unit): continue
        for p in PIN.finditer(_block(b, m.start())):
            out.append(dict(type=p.group(1), x=float(p.group(2)), y=float(p.group(3)), angle=int(p.group(4)), hidden=bool(p.group(6)), name=p.group(7), number=p.group(8)))
    return out

if __name__ == '__main__':
    import sys
    for arg in sys.argv[1:]:
        lib, name = arg.split(':'); ps = pins(lib, name)
        print('==', arg, '| fp:', prop(flat(lib, name), 'Footprint'))
        print('  ' + '  '.join(f"{p['number']}:{p['name']}@{p['x']},{p['y']},{p['angle']}{'h' if p['hidden'] else ''}" for p in ps))
