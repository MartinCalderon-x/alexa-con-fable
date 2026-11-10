"""Material para el video: esquema por bloques, placa en cada etapa, vistas 3D y archivos de fabricación."""
import subprocess, sys
from pathlib import Path
import gen_sch, design as D
HERE = Path(__file__).resolve().parent; B = HERE.parent / 'build'; M = HERE.parent / 'material'
K = str(HERE / 'kcli.sh'); PCB = str(HERE / f'{D.NAME}.kicad_pcb')
run = lambda *a: subprocess.run([str(x) for x in a], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
STEPS = [('1-alimentacion', ['J1', 'R1', 'R2', 'U2', 'F1', 'C1', 'U3', 'C2'], 0), ('2-cerebro', ['U1', 'C3', 'C4'], 1), ('3-microfono', ['MK1', 'C6', 'R5'], 2),
         ('4-amplificador', ['U4', 'R4', 'C7', 'C8', 'J2'], 3), ('5-led', ['U5', 'C10', 'D1', 'C9'], 4), ('6-botones', ['R3', 'C5', 'SW1', 'SW2', 'J3'], 5)]

def schematic():
    out = M / 'esquema'; out.mkdir(parents=True, exist_ok=True); tmp = B / 'sch/pasos'; tmp.mkdir(parents=True, exist_ok=True)
    for f in ['sym-lib-table', f'{D.NAME}.kicad_pro']: (tmp / f).write_text((HERE / f).read_text())
    parts, titles = [], []
    for name, refs, title in STEPS + [('7-completo', None, 6)]:
        parts = None if refs is None else parts + refs; titles.append(title)
        saved = D.BLOCKS; D.BLOCKS = [saved[i] for i in titles]
        sch = gen_sch.build(parts, tmp / f'{D.NAME}.kicad_sch'); D.BLOCKS = saved
        run(K, 'sch', 'export', 'pdf', '--exclude-drawing-sheet', '--no-background-color', '-o', tmp / f'{name}.pdf', sch)
        run('pdftoppm', '-r', '200', '-png', '-singlefile', tmp / f'{name}.pdf', out / name)
        run(K, 'sch', 'export', 'svg', '--exclude-drawing-sheet', '--no-background-color', '-o', tmp / name, sch)
        (tmp / name / f'{D.NAME}.svg').rename(out / f'{name}.svg')
    gen_sch.build()

def board():
    out = M / 'placa'; out.mkdir(parents=True, exist_ok=True)
    for name, pcb in [('1-colocada', B / 'pcb/01-colocada.kicad_pcb'), ('2-ruteada', B / 'pcb/02-ruteada.kicad_pcb'), ('3-final', PCB)]:
        for tag, layers in [('frente', 'F.Cu,Edge.Cuts,F.SilkS'), ('dorso', 'B.Cu,Edge.Cuts'), ('ambas', 'B.Cu,F.Cu,Edge.Cuts,F.SilkS')]:
            run(K, 'pcb', 'export', 'svg', '--layers', layers, '--mode-single', '--page-size-mode', '2', '--exclude-drawing-sheet', '-o', out / f'{name}-{tag}.svg', pcb)
            run(K, 'pcb', 'export', 'pdf', '--layers', layers, '--mode-single', '-o', B / 'pcb/tmp.pdf', pcb)
            run('pdftoppm', '-r', '600', '-x', '1583', '-y', '1583', '-W', '1560', '-H', '1560', '-png', '-singlefile', B / 'pcb/tmp.pdf', out / f'{name}-{tag}')
    for name, pcb in [('1-colocada', B / 'pcb/01-colocada.kicad_pcb'), ('3-final', PCB)]:
        for side in ['top', 'bottom']:
            run(K, 'pcb', 'render', '--side', side, '--width', '2160', '--height', '2160', '--quality', 'high', '--background', 'transparent', '-o', out / f'{name}-3d-{side}.png', pcb)
    run(K, 'pcb', 'render', '--perspective', '--rotate', '-55,0,25', '--zoom', '0.9', '--width', '2160', '--height', '2160', '--quality', 'high', '--background', 'transparent', '-o', out / '3-final-3d-perspectiva.png', PCB)

def turntable(frames=90):
    out = B / 'giro'; out.mkdir(parents=True, exist_ok=True)
    for i in range(frames):
        run(K, 'pcb', 'render', '--perspective', '--rotate', f'-58,0,{i * 360 / frames:.1f}', '--zoom', '0.85', '--width', '1080', '--height', '1080', '--quality', 'basic', '--background', 'opaque', '-o', out / f'f{i:03d}.png', PCB)
    (M / 'placa').mkdir(parents=True, exist_ok=True)
    run('ffmpeg', '-y', '-framerate', '30', '-i', out / 'f%03d.png', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '14', M / 'placa/giro-3d.mp4')

def fabrication():
    out = HERE.parent / 'out/fabricacion'; (out / 'gerbers').mkdir(parents=True, exist_ok=True)
    run(K, 'pcb', 'export', 'gerbers', '--layers', 'F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts', '-o', out / 'gerbers', PCB)
    run(K, 'pcb', 'export', 'drill', '--format', 'excellon', '--excellon-separate-th', '-o', str(out / 'gerbers') + '/', PCB)
    run(K, 'pcb', 'export', 'pos', '--format', 'csv', '--units', 'mm', '--side', 'front', '-o', out / 'posiciones.csv', PCB)
    run(K, 'sch', 'export', 'bom', '--fields', 'Reference,Value,Footprint,MPN,${QUANTITY}', '--labels', 'Refs,Valor,Huella,MPN,Cant', '--group-by', 'Value,Footprint,MPN', '-o', out / 'bom.csv', HERE / f'{D.NAME}.kicad_sch')
    run(K, 'sch', 'export', 'pdf', '-o', out / 'esquema.pdf', HERE / f'{D.NAME}.kicad_sch')
    run(K, 'pcb', 'export', 'step', '--subst-models', '--force', '-o', out / 'placa.step', PCB)

if __name__ == '__main__':
    for step in sys.argv[1:] or ['schematic', 'board', 'fabrication']: globals()[step](); print('listo:', step)
