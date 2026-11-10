"""Vuelca la geometría de una placa a JSON para animarla (pistas, vías, pads, cuerpos). Uso: ./kpy.sh geometria.py placa.kicad_pcb salida.json [drc.json]"""
import json, sys
import pcbnew as pcb
mm = pcb.ToMM
b = pcb.LoadBoard(sys.argv[1]); out = dict(tracks=[], vias=[], pads=[], parts=[], open=[])
for t in b.GetTracks():
    if t.GetClass() == 'PCB_VIA': out['vias'].append([mm(t.GetPosition().x), mm(t.GetPosition().y), t.GetNetname()])
    else: out['tracks'].append([mm(t.GetStart().x), mm(t.GetStart().y), mm(t.GetEnd().x), mm(t.GetEnd().y), 0 if t.GetLayer() == pcb.F_Cu else 1, mm(t.GetWidth()), t.GetNetname()])
HEIGHT = dict(U1=3.2, J1=3.2, J2=6.0, J3=8.5, D1=1.6, SW1=2.5, SW2=2.5, U4=0.8, MK1=1.0)
for f in b.GetFootprints():
    box = f.GetCourtyard(pcb.F_CrtYd).BBox(); ref = f.GetReference()
    if ref == 'U1':                       # el patio del módulo incluye la zona libre de la antena: usar el cuerpo
        x, y = mm(f.GetPosition().x), mm(f.GetPosition().y); r = [x - 9, y - 12.75, x + 9, y + 12.75]
    else: r = [mm(box.GetX()), mm(box.GetY()), mm(box.GetRight()), mm(box.GetBottom())]
    if not ref.startswith('H'): out['parts'].append([ref] + r + [HEIGHT.get(ref, 0.9 if ref[0] in 'UF' else 0.6)])
    for p in f.Pads():
        bb = p.GetBoundingBox(); out['pads'].append([mm(bb.GetX()), mm(bb.GetY()), mm(bb.GetRight()), mm(bb.GetBottom()), p.GetNetname(), ref, p.GetNumber(), 1 if p.GetDrillSize().x else 0])
if len(sys.argv) > 3:
    for v in json.load(open(sys.argv[3]))['unconnected_items']:
        a, c = v['items'][0], v['items'][1]
        if 'GND' not in a['description']: out['open'].append([a['pos']['x'], a['pos']['y'], c['pos']['x'], c['pos']['y'], a['description'].split('[')[1].split(']')[0]])
json.dump(out, open(sys.argv[2], 'w')); print({k: len(v) for k, v in out.items()})
