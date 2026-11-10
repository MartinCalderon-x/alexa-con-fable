"""Ruteo automático con Freerouting 2.5.0 (jar y Java locales del repo physical-ai)."""
import os, subprocess
from pathlib import Path
HERE = Path(__file__).resolve().parent; OUT = HERE.parent / 'build/pcb'
LAB = Path.home() / 'repos/physical-ai/tools/freerouting'
JAR = LAB / 'freerouting-2.5.0.jar'; JAVA = LAB / 'java/jdk-25.0.5+8-jre/Contents/Home/bin/java'
for n in ['router-config', 'router-home', 'router-tmp']: (OUT / n).mkdir(parents=True, exist_ok=True)
ses = OUT / 'ruteado.ses'; ses.unlink(missing_ok=True)
argv = [str(JAVA), '-Djava.awt.headless=true', f'-Duser.home={OUT / "router-home"}', f'-Djava.io.tmpdir={OUT / "router-tmp"}', '-Xmx3g', '-jar', str(JAR),
        f'--user_data_path={OUT / "router-config"}', '-da', '-dl', '--gui.enabled=false', '--api_server.enabled=false', '--profile.allow_telemetry=false',
        '--usage_and_diagnostic_data.disable_analytics=true', '-de', str(OUT / 'sin-rutear.dsn'), '-do', str(ses), '-inc', 'GND',
        '--router.fanout.enabled=true', '--router.copper_to_edge_clearance_um=400', '--router.autorouter.max_passes=30', '-mt', '2']
with (OUT / 'router.log').open('w') as log:
    subprocess.run(argv, cwd=OUT, env=dict(HOME=str(OUT / 'router-home'), TMPDIR=str(OUT / 'router-tmp') + '/', PATH=os.defpath, LC_ALL='C', LANG='C'),
                   stdout=log, stderr=subprocess.STDOUT, timeout=900, check=True)
assert ses.is_file() and ses.stat().st_size > 1000, 'ruteo incompleto'
print('sesión de ruteo generada:', ses.stat().st_size, 'bytes')
