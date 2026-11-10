"""Placa del satélite de voz: colocación explícita desde el netlist del esquema.

Ejecutar con ./kpy.sh gen_pcb.py [colocar|terminar]. El ruteo lo hace Freerouting (route.py).
"""
import json, math, sys, uuid, xml.etree.ElementTree as ET
from pathlib import Path
import pcbnew as pcb
import design as D

HERE = Path(__file__).resolve().parent; OUT = HERE.parent / 'build/pcb'
FP = '/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/'
ROOT_ID = str(uuid.uuid5(uuid.NAMESPACE_URL, 'mc/satelite-voz/r1'))
uid = lambda s: str(uuid.uuid5(uuid.NAMESPACE_URL, 'mc/satelite-voz/' + s))
mm = pcb.FromMM; pt = lambda x, y: pcb.VECTOR2I(mm(x), mm(y))
CX, CY, RADIUS = 100.0, 100.0, 31.0
BOARD = HERE / f'{D.NAME}.kicad_pcb'
POWER = ['+5V', '+3V3', 'VBUS', '/SPK_P', '/SPK_N']
HOLES = [(CX + 26.5 * math.cos(math.radians(a)), CY + 26.5 * math.sin(math.radians(a))) for a in (38, 142, 205, 335)]

# ref: (x, y, rotación). Antena arriba, USB abajo, parlante a la derecha, micrófono a la izquierda.
PLACE = {
    'U1': (100, 83.6, 0),
    'C3': (86.2, 79.8, 90), 'C4': (88.4, 79.8, 90), 'R3': (86.2, 84.8, 90), 'C5': (88.4, 84.8, 90),
    'MK1': (79.5, 96.5, 0), 'C6': (79.5, 92.6, 0), 'R5': (84.6, 96.2, 90),
    'J3': (76.0, 101.8, 0),
    'D1': (100, 104.0, 0), 'C9': (100, 108.6, 0), 'U5': (108.4, 109.6, 90), 'C10': (112.2, 109.6, 90),
    'U4': (117.0, 100.0, 0), 'C7': (117.0, 95.6, 0), 'C8': (112.6, 97.4, 90), 'R4': (112.6, 102.4, 90),
    'J2': (123.0, 104.0, 90),
    'J1': (100, 127.2, 0), 'U2': (100, 116.8, 90), 'R1': (93.4, 123.8, 90), 'R2': (106.6, 123.8, 90),
    'F1': (107.4, 118.2, 0), 'U3': (89.6, 113.6, 0), 'C1': (93.6, 116.8, 0), 'C2': (85.6, 110.4, 0),
    'SW1': (116.2, 120.6, 0), 'SW2': (84.0, 120.6, 0),
}

def place():
    OUT.mkdir(parents=True, exist_ok=True)
    xml = ET.parse(HERE.parent / 'build/sch/netlist.xml').getroot()
    board = pcb.BOARD(); board.SetCopperLayerCount(2)
    st = board.GetDesignSettings(); st.SetBoardThickness(mm(1.6))
    st.m_MinClearance = mm(.15); st.m_TrackMinWidth = mm(.15); st.m_CopperEdgeClearance = mm(.4); st.m_MinThroughDrill = mm(.2); st.m_ViasMinSize = mm(.6)
    nets, node = {}, {}
    for n in xml.findall('./nets/net'):
        name = n.attrib['name']; net = pcb.NETINFO_ITEM(board, name); board.Add(net); nets[name] = net
        for x in n.findall('node'): node[(x.attrib['ref'], x.attrib['pin'])] = (net, x.attrib.get('pinfunction', ''), x.attrib.get('pintype', 'passive'))
    ns = st.m_NetSettings; d = ns.GetDefaultNetclass()
    d.SetClearance(mm(.15)); d.SetTrackWidth(mm(.2)); d.SetViaDiameter(mm(.6)); d.SetViaDrill(mm(.3))
    pw = pcb.NETCLASS('Power'); pw.SetClearance(mm(.15)); pw.SetTrackWidth(mm(.4)); pw.SetViaDiameter(mm(.8)); pw.SetViaDrill(mm(.4)); ns.SetNetclass('Power', pw)
    for n in POWER: ns.SetNetclassPatternAssignment(n, 'Power')
    ns.RecomputeEffectiveNetclasses()
    for ref, sym, value, footprint, mpn, _, _ in D.PARTS:
        lib, name = footprint.split(':'); fp = pcb.FootprintLoad(FP + lib + '.pretty', name)
        board.Add(fp); fp.SetReference(ref); fp.SetValue(value); fp.SetFPID(pcb.LIB_ID(lib, name))
        path = pcb.KIID_PATH(); path.push_back(pcb.KIID(ROOT_ID)); path.push_back(pcb.KIID(uid(ref))); fp.SetPath(path)
        x, y, a = PLACE[ref]; fp.SetPosition(pt(x, y)); fp.SetOrientationDegrees(a)
        fp.Value().SetVisible(False); fp.Reference().SetVisible(False)
        comp = xml.find(f'./components/comp[@ref="{ref}"]')
        for key in ['datasheet', 'description']:
            if comp.find(key) is not None: {'datasheet': fp.SetDatasheet if hasattr(fp, 'SetDatasheet') else (lambda v: None), 'description': fp.SetLibDescription}[key](comp.find(key).text or '')
        for field in comp.findall('./fields/field'):
            if field.attrib['name'] in ('Footprint', 'Datasheet', 'Description'): continue
            f = pcb.PCB_FIELD(fp, pcb.FIELD_T_USER, field.attrib['name']); f.SetText(field.text or ''); f.SetVisible(False); fp.Add(f)
        for pad in fp.Pads():
            n = node.get((ref, pad.GetNumber()))
            if n: pad.SetNet(n[0]); pad.SetPinFunction(n[1]); pad.SetPinType(n[2])
    for i, (x, y) in enumerate(HOLES, 1):
        fp = pcb.FootprintLoad(FP + 'MountingHole.pretty', 'MountingHole_2.7mm_M2.5'); fp.SetFPID(pcb.LIB_ID('MountingHole', 'MountingHole_2.7mm_M2.5'))
        fp.SetAttributes(fp.GetAttributes() | pcb.FP_BOARD_ONLY | pcb.FP_EXCLUDE_FROM_BOM | pcb.FP_EXCLUDE_FROM_POS_FILES)
        board.Add(fp); fp.SetReference(f'H{i}'); fp.SetPosition(pt(x, y)); fp.Reference().SetVisible(False); fp.Value().SetVisible(False)
    edge = pcb.PCB_SHAPE(board); edge.SetShape(pcb.SHAPE_T_CIRCLE); edge.SetCenter(pt(CX, CY)); edge.SetEnd(pt(CX + RADIUS, CY)); edge.SetLayer(pcb.Edge_Cuts); edge.SetWidth(mm(.05)); board.Add(edge)
    for text, x, y, size in [('SATÉLITE DE VOZ r1', 100, 112.4, 1.0), ('MIC', 79.5, 99.6, .8), ('RESET', 84.0, 123.9, .8), ('BOOT', 116.2, 123.9, .8),
                             ('PARLANTE', 121.5, 110.6, .8), ('3V3 TX RX GND', 80.6, 105.6, .8)]:
        t = pcb.PCB_TEXT(board); t.SetText(text); t.SetLayer(pcb.F_SilkS); t.SetPosition(pt(x, y)); t.SetTextSize(pt(size, size)); t.SetTextThickness(mm(.15))
        if text.startswith('3V3'): t.SetTextAngleDegrees(270)
        board.Add(t)
    for text, y, size in [('SATÉLITE DE VOZ r1', 96, 1.6), ('Diseñado por Claude Fable 5.2', 100, 1.2), ('Prototipo: medir antes de usar', 104, 1.0)]:
        t = pcb.PCB_TEXT(board); t.SetText(text); t.SetLayer(pcb.B_SilkS); t.SetMirrored(True); t.SetPosition(pt(100, y)); t.SetTextSize(pt(size, size)); t.SetTextThickness(mm(.18)); board.Add(t)
    board.SetFileName(str(BOARD)); board.BuildConnectivity(); pcb.SaveBoard(str(BOARD), board)
    project(); assert pcb.ExportSpecctraDSN(board, str(OUT / 'sin-rutear.dsn'))
    print('colocados', len(D.PARTS), 'componentes +', len(HOLES), 'anclajes')

def project():
    pro = HERE / f'{D.NAME}.kicad_pro'; p = json.loads(pro.read_text())
    p['board'] = dict(design_settings=dict(rules=dict(min_clearance=.15, min_track_width=.15, min_via_annular_width=.13, min_via_diameter=.6, min_through_hole_diameter=.2,
                      min_hole_clearance=.15, min_copper_edge_clearance=.4, min_silk_clearance=0, min_hole_to_hole=.25),
                      rule_severities=dict(lib_footprint_mismatch='ignore', lib_footprint_issues='ignore', silk_overlap='ignore', silk_over_copper='ignore', silk_edge_clearance='ignore')))
    p['net_settings'] = dict(classes=[dict(name='Default', clearance=.15, track_width=.2, via_diameter=.6, via_drill=.3),
                                      dict(name='Power', clearance=.15, track_width=.4, via_diameter=.8, via_drill=.4)],
                             netclass_patterns=[dict(netclass='Power', pattern=n) for n in POWER], meta=dict(version=4))
    p['erc'] = dict(erc_exclusions=[], rule_severities=dict(simulation_model_issue='error'))      # el banco eléctrico exige este chequeo activo
    pro.write_text(json.dumps(p, indent=2) + '\n')

def import_routes():
    board = pcb.LoadBoard(str(BOARD))
    assert pcb.ImportSpecctraSES(board, str(OUT / 'ruteado.ses'))
    # Vías que el autoruteador dejó sin pista en alguna de las dos caras: no conectan nada.
    tracks = list(board.GetTracks()); loose = []
    for via in [t for t in tracks if t.GetClass() == 'PCB_VIA' and t.GetNetname() != 'GND']:
        sides = {t.GetLayer() for t in tracks if t.GetClass() != 'PCB_VIA' and t.GetNetCode() == via.GetNetCode() and via.GetPosition() in (t.GetStart(), t.GetEnd())}
        on_pad = any(p.GetNetCode() == via.GetNetCode() and p.HitTest(via.GetPosition()) for f in board.GetFootprints() for p in f.Pads())
        if len(sides) < 2 and not on_pad: loose.append(via)
    for via in loose: board.Remove(via)
    pcb.SaveBoard(str(BOARD), board); print('ruteo importado; vías sueltas quitadas:', len(loose))

def finish():
    board = pcb.LoadBoard(str(BOARD)); gnd = board.FindNet('GND')
    for layer in [pcb.F_Cu, pcb.B_Cu]:
        z = pcb.ZONE(board); z.SetLayer(layer); z.SetNetCode(gnd.GetNetCode()); z.SetLocalClearance(mm(.25)); z.SetMinThickness(mm(.2))
        z.SetThermalReliefGap(mm(.25)); z.SetThermalReliefSpokeWidth(mm(.35)); z.SetPadConnection(pcb.ZONE_CONNECTION_THERMAL); z.SetZoneName('GND'); z.SetIslandRemovalMode(pcb.ISLAND_REMOVAL_MODE_ALWAYS)
        poly = z.Outline(); poly.NewOutline()
        for i in range(72):
            a = math.radians(i * 5); poly.Append(mm(CX + (RADIUS - .2) * math.cos(a)), mm(CY + (RADIUS - .2) * math.sin(a)))
        board.Add(z)
    # Pads de masa con geometría especial: unión sólida al plano (el alivio térmico no alcanza).
    for ref, num in [('MK1', '3'), ('U2', '2')]:
        for pad in board.FindFootprintByReference(ref).Pads():
            if pad.GetNumber() == num: pad.SetLocalZoneConnection(pcb.ZONE_CONNECTION_FULL)
    filler = pcb.ZONE_FILLER(board); filler.Fill(board.Zones())
    # Vías de costura: solo donde ya hay cobre de masa en las dos caras, lejos de todo lo demás.
    zones = [z for z in board.Zones() if z.GetNetname() == 'GND']
    fills = [z.GetFilledPolysList(z.GetLayer()) for z in zones]
    ring = [(0, 0)] + [(.75 * math.cos(math.radians(a)), .75 * math.sin(math.radians(a))) for a in range(0, 360, 30)]
    stitched = 0; existing = [(pcb.ToMM(t.GetPosition().x), pcb.ToMM(t.GetPosition().y)) for t in board.GetTracks() if t.GetClass() == 'PCB_VIA']
    for ix in range(-10, 11):
        for iy in range(-10, 11):
            x, y = CX + ix * 3.0 + (iy % 2) * 1.5, CY + iy * 3.0
            if any(math.hypot(x - ex, y - ey) < 1.2 for ex, ey in existing): continue
            if math.hypot(x - CX, y - CY) > RADIUS - 1.5: continue
            if 90 < x < 110 and y < 97.5: continue      # bajo el módulo ya hay vías térmicas propias
            if all(f.Contains(pt(x + dx, y + dy)) for f in fills for dx, dy in ring):
                via = pcb.PCB_VIA(board); via.SetPosition(pt(x, y)); via.SetWidth(pcb.F_Cu, mm(.6)) if via.SetWidth.__doc__ and 'PCB_LAYER_ID' in via.SetWidth.__doc__ else via.SetWidth(mm(.6))
                via.SetDrill(mm(.3)); via.SetViaType(pcb.VIATYPE_THROUGH); via.SetLayerPair(pcb.F_Cu, pcb.B_Cu); via.SetNetCode(gnd.GetNetCode()); board.Add(via); stitched += 1
    # Islas de masa que quedaron sin ninguna vía: buscar un punto fino dentro de la isla que también tenga cobre del otro lado.
    def add_via(x, y):
        via = pcb.PCB_VIA(board); via.SetPosition(pt(x, y)); via.SetWidth(pcb.F_Cu, mm(.6)) if via.SetWidth.__doc__ and 'PCB_LAYER_ID' in via.SetWidth.__doc__ else via.SetWidth(mm(.6))
        via.SetDrill(mm(.3)); via.SetViaType(pcb.VIATYPE_THROUGH); via.SetLayerPair(pcb.F_Cu, pcb.B_Cu); via.SetNetCode(gnd.GetNetCode()); board.Add(via); existing.append((x, y))
    filler = pcb.ZONE_FILLER(board); filler.Fill(board.Zones())
    fills = [z.GetFilledPolysList(z.GetLayer()) for z in zones]
    through = existing + [(pcb.ToMM(p.GetPosition().x), pcb.ToMM(p.GetPosition().y)) for f in board.GetFootprints() for p in f.Pads() if p.GetNetname() == 'GND' and p.GetDrillSize().x]
    small = [(0, 0)] + [(.5 * math.cos(math.radians(a)), .5 * math.sin(math.radians(a))) for a in range(0, 360, 30)]
    rescued = 0
    for k, fill in enumerate(fills):
        other = fills[1 - k]
        for i in range(fill.OutlineCount()):
            if any(fill.Contains(pt(x, y), i) for x, y in through): continue
            box = fill.Outline(i).BBox(); found = False
            x = pcb.ToMM(box.GetX())
            while x < pcb.ToMM(box.GetRight()) and not found:
                y = pcb.ToMM(box.GetY())
                while y < pcb.ToMM(box.GetBottom()) and not found:
                    if all(fill.Contains(pt(x + dx, y + dy), i) and other.Contains(pt(x + dx, y + dy)) for dx, dy in small) and not any(math.hypot(x - ex, y - ey) < 1.0 for ex, ey in through):
                        add_via(x, y); through.append((x, y)); rescued += 1; found = True
                    y += .25
                x += .25
    print('islas rescatadas con vía:', rescued)
    filler = pcb.ZONE_FILLER(board); filler.Fill(board.Zones()); board.BuildConnectivity(); pcb.SaveBoard(str(BOARD), board)
    print('planos de masa rellenos; pistas y vías', len(board.GetTracks()), '| vías de costura', stitched)

if __name__ == '__main__':
    {'colocar': place, 'importar': import_routes, 'terminar': finish}[sys.argv[1] if len(sys.argv) > 1 else 'colocar']()
