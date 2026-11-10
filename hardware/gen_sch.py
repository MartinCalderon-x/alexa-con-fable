"""Genera satelite_voz.kicad_sch desde design.py con símbolos de la biblioteca de KiCad.

Cada pin recibe un tramo corto y una etiqueta de red o un símbolo de alimentación.
Uso: python3 gen_sch.py [--hasta N]   (N = cantidad de bloques, para las capturas paso a paso)
"""
import json, math, re, sys, uuid
from pathlib import Path
import kisym
import design as D

HERE = Path(__file__).resolve().parent
ROOT_ID = str(uuid.uuid5(uuid.NAMESPACE_URL, 'mc/satelite-voz/r1'))
uid = lambda s: str(uuid.uuid5(uuid.NAMESPACE_URL, 'mc/satelite-voz/' + s))
Q = lambda s: json.dumps(s, ensure_ascii=False)
r4 = lambda v: round(v, 4)
STUB = 5.08

def rot(x, y, a):
    c, s = round(math.cos(math.radians(a))), round(math.sin(math.radians(a)))
    return x * c - y * s, x * s + y * c

def lib_property(block, key):
    m = re.search(r'\(property "%s" ' % key, block)
    b = kisym._block(block, m.start())
    at = re.search(r'\(at ([-\d.]+) ([-\d.]+) (\d+)\)', b)
    eff = re.search(r'\(effects', b)
    effects = kisym._block(b, eff.start()) if eff else '(effects(font(size 1.27 1.27)))'
    return float(at.group(1)), float(at.group(2)), int(at.group(3)), effects

class Sheet:
    def __init__(self):
        self.libs = {}; self.items = []; self.npwr = 0

    def lib(self, sym):
        if sym not in self.libs: self.libs[sym] = kisym.flat(*sym.split(':'))
        return self.libs[sym]

    def power(self, net, x, y, direction):
        """direction: vector unitario hacia donde se aleja del pin (coordenadas de hoja, y hacia abajo)."""
        sym = 'power:' + net; self.lib(sym); self.npwr += 1; ref = f'#PWR{self.npwr:03d}'
        base = (0, 1) if net == 'GND' else (0, -1)          # hacia dónde se dibuja con rotación 0
        angle = {(0, 1): {(0, 1): 0, (1, 0): 90, (0, -1): 180, (-1, 0): 270},
                 (0, -1): {(0, -1): 0, (-1, 0): 90, (0, 1): 180, (1, 0): 270}}[base][direction]
        tx, ty = x + direction[0] * 4.6, y + direction[1] * 4.6
        just = '' if direction[0] == 0 else '(justify %s)' % ('left' if direction[0] > 0 else 'right')
        self.items.append(
            f'(symbol(lib_id {Q(sym)})(at {r4(x)} {r4(y)} {angle})(unit 1)(exclude_from_sim no)(in_bom yes)(on_board yes)(dnp no)(uuid {Q(uid(ref))})'
            f'(property "Reference" {Q(ref)}(at {r4(x)} {r4(y)} 0)(effects(font(size 1.27 1.27))(hide yes)))'
            f'(property "Value" {Q(net)}(at {r4(tx)} {r4(ty)} 0)(effects(font(size 1.1 1.1)){just}))'
            f'(property "Footprint" ""(at {r4(x)} {r4(y)} 0)(effects(font(size 1.27 1.27))(hide yes)))'
            f'(pin "1"(uuid {Q(uid(ref + "p"))}))'
            f'(instances(project {Q(D.NAME)}(path {Q("/" + ROOT_ID)}(reference {Q(ref)})(unit 1)))))')

    def wire(self, a, b, key):
        self.items.append(f'(wire(pts(xy {r4(a[0])} {r4(a[1])})(xy {r4(b[0])} {r4(b[1])}))(stroke(width 0)(type default))(uuid {Q(uid(key))}))')

    def label(self, net, x, y, direction, key):
        angle = {(1, 0): 0, (-1, 0): 180, (0, -1): 90, (0, 1): 270}[direction]
        just = 'left' if direction in [(1, 0), (0, -1)] else 'right'
        self.items.append(f'(label {Q(net)}(at {r4(x)} {r4(y)} {angle})(effects(font(size 1.1 1.1))(justify {just} bottom))(uuid {Q(uid(key))}))')

    def part(self, ref, sym, value, footprint, mpn, pos, nets):
        x, y, a = pos; block = self.lib(sym); name = sym.split(':')[1]
        props = ''
        for key, text in [('Reference', ref), ('Value', value)]:
            px, py, pa, effects = lib_property(block, key)
            qx, qy = rot(px, py, a)
            props += f'(property {Q(key)} {Q(text)}(at {r4(x + qx)} {r4(y - qy)} {pa}){effects})'
        props += f'(property "Footprint" {Q(footprint)}(at {x} {y} 0)(effects(font(size 1.27 1.27))(hide yes)))'
        props += f'(property "MPN" {Q(mpn)}(at {x} {y} 0)(effects(font(size 1.27 1.27))(hide yes)))'
        sim = D.SIM.get(ref)                  # modelo para el banco eléctrico; lo demás queda fuera de la simulación
        for key, val in (sim or {}).items(): props += f'(property {Q(key)} {Q(val)}(at {x} {y} 0)(effects(font(size 1.27 1.27))(hide yes)))'
        in_sim = 'no' if (sim is not None or sym in ('Device:R', 'Device:C')) else 'yes'
        pins = kisym.pins(*sym.split(':'))
        self.items.append(
            f'(symbol(lib_id {Q(sym)})(at {x} {y} {a})(unit 1)(exclude_from_sim {in_sim})(in_bom yes)(on_board yes)(dnp no)(uuid {Q(uid(ref))}){props}'
            + ''.join(f'(pin {Q(p["number"])}(uuid {Q(uid(ref + "/" + p["number"]))}))' for p in pins)
            + f'(instances(project {Q(D.NAME)}(path {Q("/" + ROOT_ID)}(reference {Q(ref)})(unit 1)))))')
        done = {}
        for p in pins:
            net = nets.get(p['number'], nets.get(p['name']))
            qx, qy = rot(p['x'], p['y'], a); px, py = x + qx, y - qy
            ox, oy = rot(*{0: (-1, 0), 180: (1, 0), 90: (0, -1), 270: (0, 1)}[p['angle']], a)
            direction = (int(ox), int(-oy)); spot = (r4(px), r4(py))
            if spot in done:
                assert done[spot] == net, f'{ref}: pines apilados con redes distintas en {spot}'
                continue
            done[spot] = net
            if net is None:
                if p['type'] != 'no_connect':
                    self.items.append(f'(no_connect(at {spot[0]} {spot[1]})(uuid {Q(uid(ref + p["number"] + "nc"))}))')
                continue
            if net == '@manual': continue
            if net in D.POWER_NETS and direction[1] == 0:
                # Pin horizontal: codo para que el símbolo de alimentación quede vertical y legible.
                corner = (px + direction[0] * 2.54, py); vertical = (0, 1) if net == 'GND' else (0, -1)
                end = (corner[0], corner[1] + vertical[1] * 2.54)
                self.wire((px, py), corner, ref + p['number'] + 'w'); self.wire(corner, end, ref + p['number'] + 'v')
                self.power(net, end[0], end[1], vertical); continue
            length = STUB / 2 if net in D.POWER_NETS else STUB
            end = (px + direction[0] * length, py + direction[1] * length)
            self.wire((px, py), end, ref + p['number'] + 'w')
            if net in D.POWER_NETS: self.power(net, end[0], end[1], direction)
            else: self.label(net, end[0], end[1], direction, ref + p['number'] + 'l')

    def flag(self, net, x, y):
        self.lib('power:PWR_FLAG'); ref = '#FLG%02d' % (len([i for i in self.items if 'PWR_FLAG' in i]) + 1)
        self.items.append(
            f'(symbol(lib_id "power:PWR_FLAG")(at {x} {y} 0)(unit 1)(exclude_from_sim no)(in_bom yes)(on_board yes)(dnp no)(uuid {Q(uid(ref))})'
            f'(property "Reference" {Q(ref)}(at {x} {y} 0)(effects(font(size 1.27 1.27))(hide yes)))'
            f'(property "Value" "PWR_FLAG"(at {x} {r4(y - 5.2)} 0)(effects(font(size 1 1))))'
            f'(property "Footprint" ""(at {x} {y} 0)(effects(font(size 1.27 1.27))(hide yes)))'
            f'(pin "1"(uuid {Q(uid(ref + "p"))}))(instances(project {Q(D.NAME)}(path {Q("/" + ROOT_ID)}(reference {Q(ref)})(unit 1)))))')
        self.wire((x, y), (x + 10.16, y), ref + 'w')
        self.power(net, x + 10.16, y, (0, 1) if net == 'GND' else (0, -1))

    def text(self, value, x, y, size=2.0):
        self.items.append(f'(text {Q(value)}(at {x} {y} 0)(effects(font(size {size} {size})(bold yes))(justify left bottom))(uuid {Q(uid(value))}))')

    def dump(self):
        libs = ''.join(self.libs[k] for k in sorted(self.libs))
        head = (f'(kicad_sch(version 20250114)(generator "eeschema")(generator_version "9.0")(uuid {Q(ROOT_ID)})(paper "A3")'
                f'(title_block(title {Q(D.TITLE)})(rev {Q(D.REV)})(company "Martín Calderón")'
                f'(comment 1 "Diseñado por Claude Fable 5.2 · prototipo sin fabricar ni medir"))(lib_symbols{libs})')
        tail = f'(sheet_instances(path "/"(page "1")))(embedded_fonts no))'
        return head + '\n' + '\n'.join(self.items) + '\n' + tail + '\n'

def build(parts=None, out=None, titles=True):
    s = Sheet()
    for p in D.PARTS:
        if parts is None or p[0] in parts: s.part(*p)
    if parts is None:
        for net, x, y in D.POWER_FLAGS: s.flag(net, x, y)
    for owner, pts in D.EXTRA_WIRES:
        if parts is None or owner in parts:
            for i in range(len(pts) - 1): s.wire(pts[i], pts[i + 1], f'{owner}x{pts[i]}')
            s.items.append(f'(junction(at {pts[-1][0]} {pts[-1][1]})(diameter 0)(color 0 0 0 0)(uuid {Q(uid(owner + "j"))}))')
    if titles:
        for i, (title, x, y) in enumerate(D.BLOCKS): s.text(title, x, y, 2.0 if i < 6 else 1.5)
    out = out or HERE / f'{D.NAME}.kicad_sch'
    out.write_text(s.dump())
    pro = HERE / f'{D.NAME}.kicad_pro'
    if not pro.exists(): pro.write_text(json.dumps(dict(meta=dict(filename=pro.name, version=3)), indent=2) + '\n')
    return out

if __name__ == '__main__':
    print(build(), len(D.PARTS), 'componentes')
