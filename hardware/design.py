"""Satélite de voz r1 — fuente única del diseño (componentes, redes y posiciones).

Diseñado por Claude Fable 5.2 a partir de un pedido de un párrafo. Prototipo sin
fabricar ni medir: ERC/DRC no reemplazan pruebas eléctricas, térmicas ni de antena.
"""
NAME = 'satelite_voz'
TITLE = 'Satélite de voz r1'
REV = 'r1'

R0603 = 'Resistor_SMD:R_0603_1608Metric'
C0603 = 'Capacitor_SMD:C_0603_1608Metric'
C0805 = 'Capacitor_SMD:C_0805_2012Metric'

# Pines sin red asignada reciben marca de "no conectado".
ESP_NETS = {
    '3V3': '+3V3', 'GND': 'GND', 'EN': 'EN', 'IO0': 'BOOT',
    'IO4': 'MIC_SCK', 'IO5': 'MIC_WS', 'IO6': 'MIC_SD',
    'IO39': 'AMP_BCLK', 'IO40': 'AMP_LRCLK', 'IO41': 'AMP_DIN', 'IO38': 'AMP_SD',
    'USB_D-': 'USB_DN', 'USB_D+': 'USB_DP', 'IO21': 'LED_3V3',
    'TXD0': 'UART_TX', 'RXD0': 'UART_RX',
}

# ref, símbolo, valor, huella, MPN, (x, y, rotación) en el esquema, redes por nombre o número de pin
PARTS = [
    # --- USB-C y alimentación ---
    ('J1', 'Connector:USB_C_Receptacle_USB2.0_16P', 'USB-C', 'Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal', 'GCT USB4105-GF-A',
     (45.72, 81.28, 0), {'VBUS': 'VBUS', 'GND': 'GND', 'SHIELD': 'GND', 'CC1': 'CC1', 'CC2': 'CC2', 'D+': 'USB_DP', 'D-': 'USB_DN'}),
    ('R1', 'Device:R', '5.1k', R0603, 'YAGEO RC0603FR-075K1L', (91.44, 104.14, 0), {'1': 'CC1', '2': 'GND'}),
    ('R2', 'Device:R', '5.1k', R0603, 'YAGEO RC0603FR-075K1L', (104.14, 104.14, 0), {'1': 'CC2', '2': 'GND'}),
    ('U2', 'Power_Protection:USBLC6-2SC6', 'USBLC6-2SC6', 'Package_TO_SOT_SMD:SOT-23-6', 'ST USBLC6-2SC6',
     (111.76, 78.74, 0), {'1': 'USB_DP', '6': 'USB_DP', '3': 'USB_DN', '4': 'USB_DN', 'VBUS': 'VBUS', 'GND': 'GND'}),
    ('F1', 'Device:Polyfuse', '1A', 'Fuse:Fuse_1206_3216Metric', 'Littelfuse 1206L100THYR', (91.44, 50.8, 0), {'1': 'VBUS', '2': '+5V'}),
    ('C1', 'Device:C', '10u', C0805, 'Murata GRM21BR61A106KE19L', (129.54, 50.8, 0), {'1': '+5V', '2': 'GND'}),
    ('U3', 'Regulator_Linear:AP2112K-3.3', 'AP2112K-3.3', 'Package_TO_SOT_SMD:SOT-23-5', 'Diodes Inc AP2112K-3.3TRG1',
     (152.4, 48.26, 0), {'VIN': '+5V', 'EN': '@manual', 'VOUT': '+3V3', 'GND': 'GND'}),
    ('C2', 'Device:C', '10u', C0805, 'Murata GRM21BR61A106KE19L', (175.26, 50.8, 0), {'1': '+3V3', '2': 'GND'}),
    # --- Microcontrolador ---
    ('U1', 'RF_Module:ESP32-S3-WROOM-1', 'ESP32-S3-WROOM-1', 'RF_Module:ESP32-S3-WROOM-1', 'Espressif ESP32-S3-WROOM-1-N8R2',
     (228.6, 114.3, 0), ESP_NETS),
    ('C3', 'Device:C', '10u', C0805, 'Murata GRM21BR61A106KE19L', (251.46, 68.58, 0), {'1': '+3V3', '2': 'GND'}),
    ('C4', 'Device:C', '100n', C0603, 'Murata GRM188R71E104KA01D', (264.16, 68.58, 0), {'1': '+3V3', '2': 'GND'}),
    ('R3', 'Device:R', '10k', R0603, 'YAGEO RC0603FR-0710KL', (99.06, 157.48, 0), {'1': '+3V3', '2': 'EN'}),
    ('C5', 'Device:C', '1u', C0603, 'Murata GRM188R71C105KA12D', (99.06, 182.88, 0), {'1': 'EN', '2': 'GND'}),
    ('SW1', 'Switch:SW_Push', 'BOOT', 'Button_Switch_SMD:SW_SPST_PTS810', 'C&K PTS810SJM250SMTRLFS', (55.88, 160.02, 0), {'1': 'BOOT', '2': 'GND'}),
    ('SW2', 'Switch:SW_Push', 'RESET', 'Button_Switch_SMD:SW_SPST_PTS810', 'C&K PTS810SJM250SMTRLFS', (55.88, 177.8, 0), {'1': 'EN', '2': 'GND'}),
    ('J3', 'Connector_Generic:Conn_01x04', 'DEBUG', 'Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical', 'Harwin M20-9990446',
     (63.5, 218.44, 0), {'1': '+3V3', '2': 'UART_TX', '3': 'UART_RX', '4': 'GND'}),
    # --- Micrófono I2S ---
    ('MK1', 'Sensor_Audio:ICS-43434', 'ICS-43434', 'Sensor_Audio:InvenSense_ICS-43434-6_3.5x2.65mm', 'TDK InvenSense ICS-43434',
     (325.12, 58.42, 0), {'VDD': '+3V3', 'GND': 'GND', 'LR': 'GND', 'WS': 'MIC_WS', 'SCK': 'MIC_SCK', 'SD': 'MIC_SD'}),
    ('C6', 'Device:C', '100n', C0603, 'Murata GRM188R71E104KA01D', (294.64, 58.42, 0), {'1': '+3V3', '2': 'GND'}),
    ('R5', 'Device:R', '100k', R0603, 'YAGEO RC0603FR-07100KL', (363.22, 68.58, 0), {'1': 'MIC_SD', '2': 'GND'}),
    # --- Amplificador I2S y parlante ---
    ('U4', 'Audio:MAX98357A', 'MAX98357A', 'Package_DFN_QFN:TQFN-16-1EP_3x3mm_P0.5mm_EP1.23x1.23mm', 'Analog Devices MAX98357AETE+T',
     (325.12, 124.46, 0), {'VDD': '+5V', 'GND': 'GND', 'PAD': 'GND', 'DIN': 'AMP_DIN', 'BCLK': 'AMP_BCLK', 'LRCLK': 'AMP_LRCLK',
                           '~{SD_MODE}': 'AMP_SD', 'OUTP': 'SPK_P', 'OUTN': 'SPK_N'}),
    ('R4', 'Device:R', '100k', R0603, 'YAGEO RC0603FR-07100KL', (284.48, 139.7, 0), {'1': 'AMP_SD', '2': 'GND'}),
    ('C7', 'Device:C', '10u', C0805, 'Murata GRM21BR61A106KE19L', (355.6, 139.7, 0), {'1': '+5V', '2': 'GND'}),
    ('C8', 'Device:C', '100n', C0603, 'Murata GRM188R71E104KA01D', (368.3, 139.7, 0), {'1': '+5V', '2': 'GND'}),
    ('J2', 'Connector_Generic:Conn_01x02', 'PARLANTE', 'Connector_JST:JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal', 'JST S2B-PH-K-S',
     (373.38, 116.84, 0), {'1': 'SPK_P', '2': 'SPK_N'}),
    # --- LED de estado ---
    ('U5', '74xGxx:74AHCT1G125', '74AHCT1G125', 'Package_TO_SOT_SMD:SOT-23-5', 'TI SN74AHCT1G125DBVR',
     (304.8, 198.12, 0), {'1': 'GND', '2': 'LED_3V3', '4': 'LED_5V', 'GND': 'GND', 'VCC': '+5V'}),
    ('C10', 'Device:C', '100n', C0603, 'Murata GRM188R71E104KA01D', (259.08, 198.12, 0), {'1': '+5V', '2': 'GND'}),
    ('D1', 'LED:WS2812B', 'WS2812B', 'LED_SMD:LED_WS2812B_PLCC4_5.0x5.0mm_P3.2mm', 'Worldsemi WS2812B',
     (350.52, 198.12, 0), {'VDD': '+5V', 'VSS': 'GND', 'DIN': 'LED_5V'}),
    ('C9', 'Device:C', '100n', C0603, 'Murata GRM188R71E104KA01D', (378.46, 198.12, 0), {'1': '+5V', '2': 'GND'}),
]

# Modelos de simulación para el banco de alimentación (qa/). Resistencias y capacitores se simulan con su valor;
# todo lo que no figura acá queda excluido y sus cargas las declara el banco (qa/spec.json).
SIM = {
    'U3': {'Sim.Device': 'SUBCKT', 'Sim.Library': '${KIPRJMOD}/qa/models/equivalentes.lib', 'Sim.Name': 'LDO_3V3_DECLARADO', 'Sim.Pins': '1=VIN 2=GND 3=EN 5=VOUT'},
    'F1': {'Sim.Device': 'R', 'Sim.Params': 'r=0.21', 'Sim.Pins': '1=+ 2=-'},
}

POWER_NETS = ['GND', '+3V3', '+5V', 'VBUS']
# Redes que el ERC debe considerar alimentadas desde afuera o a través de pasivos.
POWER_FLAGS = [('VBUS', 40.64, 251.46), ('+5V', 66.04, 251.46), ('GND', 91.44, 251.46)]

# Uniones dibujadas a mano: EN del regulador unido a su entrada (siempre encendido).
EXTRA_WIRES = [('U3', [(144.78, 48.26), (142.24, 48.26), (142.24, 45.72)])]

BLOCKS = [
    ('1 · USB-C, protección y 3,3 V', 25.4, 30.48),
    ('2 · ESP32-S3: Wi-Fi, USB nativo y dos buses I2S', 190.5, 30.48),
    ('3 · Micrófono digital I2S', 284.48, 30.48),
    ('4 · Amplificador clase D y parlante', 284.48, 96.52),
    ('5 · LED de estado con adaptación a 5 V', 248.92, 170.18),
    ('6 · Botones, reset y depuración', 25.4, 139.7),
    ('Nombres de red iguales = conexión. Prototipo sin fabricar ni medir.', 25.4, 271.78),
]

# Decisiones que el guion puede contar (cada una tiene un porqué comprobable).
DECISIONS = [
    ('ESP32-S3-WROOM-1', 'Módulo con antena y blindaje certificados: evita diseñar RF. USB nativo en IO19/IO20, sin chip USB-serie.'),
    ('Dos buses I2S separados', 'Micrófono (IO4-6) y amplificador (IO39-41) no comparten reloj: escuchar y hablar a la vez sin depender del modo dúplex.'),
    ('AMP_SD con 100k a masa', 'El amplificador arranca apagado: sin chasquido en el parlante mientras el ESP32 inicia.'),
    ('74AHCT1G125 para el LED', 'El WS2812B a 5 V pide 3,5 V para leer un "1"; el ESP32 entrega 3,3 V. El buffer lo lleva a 5 V dentro de especificación.'),
    ('Polyfuse de 1 A + USBLC6', 'Corto en el parlante o descarga en el conector no llegan al puerto USB de la computadora.'),
    ('CC1/CC2 con 5,1k', 'Sin estas dos resistencias un cargador USB-C no entrega tensión.'),
    ('Pines elegidos por ubicación', 'Micrófono en pines del lado izquierdo del módulo, amplificador en los del derecho, LED y USB abajo: pistas cortas y sin cruces.'),
    ('Pines de arranque libres', 'IO0, IO3, IO45 e IO46 definen el modo de arranque; solo IO0 se usa, para el botón BOOT.'),
]
