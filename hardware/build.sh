#!/usr/bin/env bash
# Regenera todo: esquema → ERC → netlist → colocación → ruteo → planos de masa → DRC.
set -euo pipefail
cd "$(dirname -- "${BASH_SOURCE[0]}")"
mkdir -p ../build/sch ../build/pcb
python3 gen_sch.py
./kcli.sh sch erc --severity-all --format json -o ../build/sch/erc.json satelite_voz.kicad_sch >/dev/null
./kcli.sh sch export netlist --format kicadxml -o ../build/sch/netlist.xml satelite_voz.kicad_sch >/dev/null
./kpy.sh gen_pcb.py colocar
cp satelite_voz.kicad_pcb ../build/pcb/01-colocada.kicad_pcb
python3 route.py
grep -o 'final score.*violations)' ../build/pcb/router.log | tail -1
./kpy.sh gen_pcb.py importar 2>&1 | grep -v 'memory leak'
cp satelite_voz.kicad_pcb ../build/pcb/02-ruteada.kicad_pcb
./kpy.sh gen_pcb.py terminar 2>&1 | grep -v 'memory leak'
./kcli.sh pcb drc --severity-all --schematic-parity --format json -o ../build/pcb/drc.json satelite_voz.kicad_pcb >/dev/null
python3 report.py
