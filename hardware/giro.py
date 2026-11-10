"""Barrido 3D de la placa con fondo transparente para el reel (150 cuadros, 6 s a 25 fps)."""
import subprocess, sys
from multiprocessing import Pool
from pathlib import Path
HERE = Path(__file__).resolve().parent; OUT = HERE.parent / 'build/giro9x16'; N = 150
def frame(i):
    z = 60 - 70 * i / (N - 1)
    subprocess.run([str(HERE / 'kcli.sh'), 'pcb', 'render', '--perspective', '--rotate', f'-56,0,{z:.2f}', '--zoom', '0.9', '--width', '1400', '--height', '1400',
                    '--quality', sys.argv[1] if len(sys.argv) > 1 else 'high', '--background', 'transparent', '--light-top', '0.30', '--light-bottom', '0.05', '--light-camera', '0.12', '--light-side', '0.25,0.95,0.85', '--light-side-elevation', '25', '-o', str(OUT / f'{i:04d}.png'), str(HERE / 'satelite_voz.kicad_pcb')],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    with Pool(4) as p: list(p.imap_unordered(frame, range(N)))
    print('listo', N)
