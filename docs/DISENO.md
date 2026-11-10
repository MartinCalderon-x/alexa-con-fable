# Satélite de voz r1 — notas del diseño

Diseñado por Claude Fable 5.2 (Claude Code) el 10 de noviembre de 2026. **Prototipo sin
fabricar ni medir.** ERC y DRC comprueban reglas de dibujo; no validan el comportamiento
eléctrico, térmico, acústico ni de radio.

## Pedido

Un satélite de voz chico: escucha, responde por un parlante, muestra su estado con un LED
y se alimenta y programa por USB-C. Pensado para ESPHome / Home Assistant o un agente propio.

## Resultado

| Dato | Valor |
|---|---|
| Placa | Redonda, 62 mm, 2 capas, 1,6 mm, 4 anclajes M2.5 |
| Componentes | 28 (20 líneas de BOM) |
| Verificación del esquema (ERC) | 0 errores, 1 aviso (pad térmico del amplificador declarado sin tipo en la biblioteca) |
| Verificación de la placa (DRC) | 0 infracciones, 0 conexiones pendientes, paridad con el esquema |
| Ruteo | Freerouting 2.5.0, unos 10 s; planos de masa en las dos caras con 106 vías de costura |

## Bloques

1. **USB-C y alimentación.** Conector de 16 pines, resistencias de 5,1 kΩ en CC1/CC2, protección
   USBLC6-2SC6, polyfuse de 1 A y regulador AP2112K a 3,3 V (600 mA).
2. **ESP32-S3-WROOM-1 (N8R2).** Antena y blindaje del módulo; USB nativo en IO19/IO20.
3. **Micrófono ICS-43434** por I2S en IO4 (SCK), IO5 (WS), IO6 (SD).
4. **Amplificador MAX98357A** por I2S en IO39 (BCLK), IO40 (LRCLK), IO41 (DIN), IO38 (apagado);
   salida a conector JST-PH para parlante de 4–8 Ω.
5. **LED WS2812B** en IO21 con buffer 74AHCT1G125 para llevar el dato de 3,3 V a 5 V.
6. **Botones BOOT y RESET** y conector de depuración (3V3, TX, RX, GND).

Las razones de cada decisión están en `design.py` (`DECISIONS`).

## Lo que cambió durante el diseño (sirve para el guion)

- La primera asignación de pines puso el amplificador en IO15–18, del lado izquierdo del módulo,
  con el amplificador a la derecha de la placa. El autoruteador informó 7 conexiones sin resolver:
  4 eran de masa (las cierra el plano de cobre) y 3 eran reales: VBUS entre los dos lados del USB-C,
  USB D− y la señal del LED. Se reproduce con la copia en `build/intento1/`.
  Reasigné el amplificador a pines del lado derecho y crucé BOOT/RESET: ruteo completo.
- El primer relleno de masa dejó una isla de cobre sin unir y un pad del micrófono sin conexión;
  se resolvió con unión sólida en ese pad y vías de costura.
- El WS2812B a 5 V no garantiza leer un "1" de 3,3 V: se agregó el buffer en lugar de confiar en
  que "suele andar".

## Pendiente antes de fabricar o energizar

- [ ] Revisión humana del esquema y de la placa contra las hojas de datos (pinout de U2, U4, U5 y MK1).
- [ ] Micrófono de puerto inferior: confirmar el agujero acústico de la huella y sellarlo contra la carcasa.
- [ ] Antena: la zona sin cobre del módulo queda dentro de la placa, no al aire; medir alcance Wi-Fi.
- [ ] Corriente: el pico de Wi-Fi más audio puede pasar los 500 mA de un puerto USB 2.0; medir y limitar volumen.
- [ ] Vías térmicas del módulo con taladro de 0,2 mm: confirmar con el fabricante o cambiarlas a 0,3 mm.
- [ ] Par USB D+/D− sin control de impedancia: suficiente para velocidad completa (12 Mb/s) por longitud corta; verificar enumeración.
- [ ] Temperatura del regulador (disipa hasta ~0,8 W en pico) y del amplificador.
- [ ] Sin carcasa ni firmware todavía.
