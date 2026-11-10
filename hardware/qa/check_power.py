"""Banco eléctrico de la alimentación del satélite de voz, con el método del probador de physical-ai.

El esquemático de KiCad es la fuente: se exporta a SPICE, se le agregan la fuente USB y las cargas declaradas en
spec.json, se simula en ngspice y se compara contra límites definidos antes de ejecutar. Cada control negativo
debe fallar por la razón esperada. Una simulación aprobada no valida el producto físico.

Uso:  ~/repos/physical-ai/.venv/bin/python qa/check_power.py     → build/qa/report.json y curvas por caso
"""
import json, re, subprocess, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; HW = HERE.parent; OUT = HW.parent / 'build/qa'
LAB = Path.home() / 'repos/physical-ai'
sys.path.insert(0, str(LAB / 'scripts'))
from spice_lab import sha, tools, simulate        # utilidades del probador: versiones fijadas y ejecución de ngspice

def export():
    """Mismo paso que export_design del probador, con la CLI aislada de esta producción."""
    OUT.mkdir(parents=True, exist_ok=True); sch = HW / 'satelite_voz.kicad_sch'
    for args in (['sch', 'erc', '--format', 'json', '--severity-all', '-o', str(OUT / 'erc.json'), str(sch)],
                 ['sch', 'export', 'netlist', '--format', 'spice', '-o', str(OUT / 'exported.cir'), str(sch)]):
        subprocess.run([str(HW / 'kcli.sh')] + args, check=True, capture_output=True, timeout=60)
    erc = json.loads((OUT / 'erc.json').read_text()); bad = [v for s in erc['sheets'] for v in s['violations'] if v['severity'] == 'error']
    if bad or any(x['key'] == 'simulation_model_issue' for x in erc.get('ignored_checks', [])): raise ValueError('ERC con errores o chequeo SPICE deshabilitado')
    text = (OUT / 'exported.cir').read_text()
    if not re.search(r'(?m)^XU3 \+5V GND \+5V \+3V3 LDO_3V3_DECLARADO$', text): raise ValueError('Pinout del regulador incorrecto en la exportación')
    if not re.search(r'(?m)^RF1 VBUS \+5V ', text) or not re.search(r'(?m)^R3 \+3V3 /EN 10k$', text): raise ValueError('Faltan el fusible o la red de EN')
    return text

def netlist(text, case, spec):
    d = spec['declarados']
    head, body = text.split('\n', 2)[:2], text.split('\n', 2)[2]          # título e .include no se tocan
    for a, b in (('+3V3', 'n3v3'), ('+5V', 'n5v'), ('/EN', 'en'), ('/', 'n_')): body = body.replace(a, b)
    text = '\n'.join(head) + '\n' + re.sub(r'\bGND\b', '0', body)
    text = re.sub(r'(?m)^(C(?:1|2|3|7) \S+ \S+) 10u$', lambda m: f"{m[1]} {10e-6 * case['cap_escala']:.6g}", text)
    text = re.sub(r'(?m)^RF1 (\S+) (\S+) .*$', lambda m: f"RF1 {m[1]} {m[2]} {d['fusible_ohm']}", text)
    if case.get('en_a_masa'): text = re.sub(r'(?m)^XU3 n5v 0 n5v n3v3', 'XU3 n5v 0 0 n3v3', text)
    ohm = case['parlante_ohm']; iavg = d['amplificador_potencia_w'][str(ohm)] / (d['amplificador_rendimiento'] * 5.0) if ohm else 0.0
    r = d['esp32_rafaga']
    bench = f'''* --- banco: fuente USB con cable y cargas declaradas ---
Vusb src 0 PWL(0 0 1m {case['vin']})
Rcable src VBUS {d['fuente_cable_ohm']}
Iesp_base n3v3 0 PWL(0 0 19m 0 19.2m {d['esp32_base_a']})
Iesp_wifi n3v3 0 PULSE(0 {d['esp32_pico_wifi_a'] - d['esp32_base_a']} 22m 20u 20u {r['ancho_s']} {r['periodo_s']})
* las cargas son fuentes de corriente ideales: este diodo evita tensiones negativas sin sentido si falta el riel
.model DPROT D(Is=1e-9 N=1 Rs=0.05)
Dprot 0 n3v3 DPROT
Iled n5v 0 PWL(0 0 24m 0 24.2m {d['led_a']})
Bamp n5v 0 I = time > 25m ? {2 * iavg} * sin(6283.185307 * time)^2 : 0
.options reltol=1e-4 abstol=1e-9 vntol=1e-7 temp=25 tnom=25 method=gear
.control
set noaskquit
set wr_singlescale
set wr_vecnames
set numdgt=12
tran {spec['max_step_s']} {spec['stop_s']} 0 {spec['max_step_s']}
wrdata transient.dat v(VBUS) v(n5v) v(n3v3) v(en) i(Vusb)
quit
.endc
.end
'''
    return re.sub(r'(?im)^\.end\s*$', lambda _: bench, text), iavg

def evaluate(rows, case, spec, iavg):
    a = np.array(rows); t, vbus, v5, v3, en, iusb = a.T; iusb = -iusb; lim, d = spec['limites'], spec['declarados']
    w = (t >= spec['ventana_s'][0]) & (t <= spec['ventana_s'][1]); up = t >= 0.018
    r = d['esp32_rafaga']; iesp = np.where(t < 0.0192, 0, d['esp32_base_a']) + np.where((t >= 0.022) & (((t - 0.022) % r['periodo_s']) < r['ancho_s']), d['esp32_pico_wifi_a'] - d['esp32_base_a'], 0)
    t3 = float(t[np.argmax(v3 >= 3.0)]) if (v3 >= 3.0).any() else None
    ten = float(t[np.argmax(en >= d['umbral_en_v'])]) if (en >= d['umbral_en_v']).any() else None
    m = dict(v3v3_min_v=float(v3[up].min()), v3v3_max_v=float(v3[up].max()), v5_min_v=float(v5[w].min()),
             corriente_media_a=float(np.trapezoid(iusb[w], t[w]) / (t[w][-1] - t[w][0])), corriente_pico_a=float(iusb[w].max()),
             ldo_potencia_media_w=float(np.trapezoid(((v5 - v3) * iesp)[w], t[w]) / (t[w][-1] - t[w][0])),
             ldo_potencia_pico_w=float(((v5 - v3) * iesp)[w].max()),
             espera_en_s=None if t3 is None or ten is None else ten - t3, amplificador_media_a=iavg, muestras=len(t))
    c = dict(v3v3=bool(lim['v3v3_v'][0] <= m['v3v3_min_v'] and m['v3v3_max_v'] <= lim['v3v3_v'][1]),
             v5=bool(m['v5_min_v'] >= lim['v5_min_v']), fusible=bool(m['corriente_media_a'] <= lim['fusible_retencion_a']),
             secuencia_en=bool(m['espera_en_s'] is not None and m['espera_en_s'] >= lim['espera_en_min_s']),
             ldo_potencia=bool(m['ldo_potencia_media_w'] <= lim['ldo_potencia_max_w']))
    return dict(checks=c, metrics=m, cumple_todo=all(c.values()))

def main():
    binary, kicad, versions = tools(); spec = json.loads((HERE / 'spec.json').read_text())
    text = export(); report = dict(passed=False, hardware='no_validado', versions=versions, spec=spec, cases={}, hallazgos=[],
                                    input_sha256={p.name: sha(p) for p in [HW / 'satelite_voz.kicad_sch', HERE / 'spec.json', HERE / 'models/equivalentes.lib', Path(__file__)]},
                                    export_sha256=sha(OUT / 'exported.cir'))
    raw = {}
    for case in spec['casos']:
        net, iavg = netlist(text, case, spec); header, rows = simulate(binary, net, OUT / case['id'])
        logs = (OUT / case['id'] / 'stdout.log').read_text() + (OUT / case['id'] / 'stderr.log').read_text()
        if re.search(r'(?i)aborted|timestep too small', logs) or abs(rows[-1][0] - spec['stop_s']) > 1e-9: raise ValueError(f"Simulación incompleta en {case['id']}; revisar logs")
        res = evaluate(rows, case, spec, iavg); raw[case['id']] = rows
        must = case.get('debe_fallar')
        if must: res['passed'] = all(not res['checks'][k] for k in must); res['control_negativo'] = must
        else: res['passed'] = res['cumple_todo']
        if case.get('igual_a'): res['identico'] = rows == raw[case['igual_a']]; res['passed'] = res['passed'] and res['identico']
        a = np.array(rows); idx = np.unique(np.r_[np.arange(0, len(a), max(1, len(a) // 6000)), len(a) - 1])
        np.savetxt(OUT / case['id'] / 'curves.csv', a[idx], delimiter=',', header='time_s,vbus_v,v5_v,v3v3_v,en_v,iusb_a', comments='', fmt='%.9g')
        report['cases'][case['id']] = res; m = res['metrics']
        print(f"{case['id']:32s} 3V3 {m['v3v3_min_v']:.3f}–{m['v3v3_max_v']:.3f} V | 5V mín {m['v5_min_v']:.2f} V | I media {m['corriente_media_a']:.2f} A pico {m['corriente_pico_a']:.2f} A | "
              f"LDO {m['ldo_potencia_media_w']:.2f} W | {'OK' if res['passed'] else 'FALLA'}" + (f" (control negativo: falla {must})" if must else ''), flush=True)
    nom = report['cases']['nominal']['metrics']; usb2 = spec['declarados']['usb2_puerto_a']
    if nom['corriente_media_a'] > usb2:
        report['hallazgos'].append(f"Con parlante de 8 Ω a potencia máxima y Wi-Fi transmitiendo, el consumo medio es {nom['corriente_media_a']:.2f} A: supera los {usb2} A de un puerto USB 2.0. Pide una fuente de 1 A o más, o limitar el volumen en el firmware.")
    if nom['ldo_potencia_pico_w'] > spec['limites']['ldo_potencia_max_w']:
        report['hallazgos'].append(f"El regulador disipa {nom['ldo_potencia_pico_w']:.2f} W durante cada ráfaga de Wi-Fi (media {nom['ldo_potencia_media_w']:.2f} W). Con transmisión sostenida hay que medir su temperatura.")
    report['passed'] = all(c['passed'] for c in report['cases'].values())
    (OUT / 'report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print('\nHallazgos:'); [print(' -', h) for h in report['hallazgos']]
    print('\nBanco:', 'APROBADO' if report['passed'] else 'NO APROBADO', '· hardware no validado'); sys.exit(0 if report['passed'] else 1)

if __name__ == '__main__': main()
