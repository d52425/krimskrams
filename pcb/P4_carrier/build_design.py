#!/usr/bin/env python3
"""Generate the ESP32-P4 (Waveshare 32088) carrier board KiCad project.

The carrier plugs onto the 32088's 2x20 header (J8) and carries the
whole power chain for one Tenmou node:

    J8 pin40 VBUS / pin39 VSYS (solder-jumper select, SJ1)
      -> polyfuse F1 -> input bulk 470uF
      -> mezzanine pins into an AE-LMR62421 boost module (30x30mm,
         M3 standoffs, no terminal blocks) and back in at +12V
      -> bulk 1000uF/25V + 10uF -> Nch MOSFET low-side switch
      -> TB111 screw-terminal ring output (FRS5CC), strobe from J8 pin10

Board: 86x68mm, 2-layer. The 32088 header numbering is consecutive
per column (left column 1-20, right column 21-40, counted from the
RJ45 end) - NOT the usual interleaved 2x20 numbering - so J8 is a
custom programmatic footprint whose pad numbers are the module's
physical pin numbers. On the carrier (module RJ45 end at the left,
USB end at the right, seen from above) physical pins 1-20 run along
the TOP row left->right and 21-40 along the BOTTOM row left->right.

Schematic is emitted as text in the KiCad 7.0 dialect (KiCad 10 reads
it and migrates on save); the PCB is built with the pcbnew API. Run
with the KiCad-bundled python:

    KICAD_SHARE=<kicad share dir> <kicad python3> build_design.py

Then fill zones / DRC / gerbers with kicad-cli:

    kicad-cli pcb drc --refill-zones --save-board P4_carrier.kicad_pcb
    kicad-cli pcb export gerbers --output gerber/ P4_carrier.kicad_pcb
    kicad-cli pcb export drill --output gerber/ P4_carrier.kicad_pcb
"""
import json
import math
import os
import re
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = "P4_carrier"
KICAD_SHARE = os.environ.get("KICAD_SHARE", "/usr/share/kicad")
SYM_DIR = os.path.join(KICAD_SHARE, "symbols")
FP_DIR = os.path.join(KICAD_SHARE, "footprints")


def U():
    return str(uuid.uuid4())


def fmt(v):
    s = ("%.4f" % v).rstrip("0").rstrip(".")
    return s if s not in ("-0", "") else "0"






LOCAL_Q_NMOS_GSD = r'''(symbol "Q_NMOS_GSD" (pin_names (offset 0) hide) (in_bom yes) (on_board yes)
        (property "Reference" "Q" (at 5.08 1.27 0)
          (effects (font (size 1.27 1.27)) (justify left))
        )
        (property "Value" "Q_NMOS_GSD" (at 5.08 -1.27 0)
          (effects (font (size 1.27 1.27)) (justify left))
        )
        (property "Footprint" "" (at 5.08 2.54 0)
          (effects (font (size 1.27 1.27)) hide)
        )
        (property "Datasheet" "~" (at 0 0 0)
          (effects (font (size 1.27 1.27)) hide)
        )
        (property "ki_keywords" "transistor NMOS N-MOS N-MOSFET" (at 0 0 0)
          (effects (font (size 1.27 1.27)) hide)
        )
        (property "ki_description" "N-MOSFET transistor, gate/source/drain" (at 0 0 0)
          (effects (font (size 1.27 1.27)) hide)
        )
        (symbol "Q_NMOS_GSD_0_1"
          (polyline
            (pts
              (xy 0.254 0)
              (xy -2.54 0)
            )
            (stroke (width 0) (type default))
            (fill (type none))
          )
          (polyline
            (pts
              (xy 0.254 1.905)
              (xy 0.254 -1.905)
            )
            (stroke (width 0.254) (type default))
            (fill (type none))
          )
          (polyline
            (pts
              (xy 0.762 -1.27)
              (xy 0.762 -2.286)
            )
            (stroke (width 0.254) (type default))
            (fill (type none))
          )
          (polyline
            (pts
              (xy 0.762 0.508)
              (xy 0.762 -0.508)
            )
            (stroke (width 0.254) (type default))
            (fill (type none))
          )
          (polyline
            (pts
              (xy 0.762 2.286)
              (xy 0.762 1.27)
            )
            (stroke (width 0.254) (type default))
            (fill (type none))
          )
          (polyline
            (pts
              (xy 2.54 2.54)
              (xy 2.54 1.778)
            )
            (stroke (width 0) (type default))
            (fill (type none))
          )
          (polyline
            (pts
              (xy 2.54 -2.54)
              (xy 2.54 0)
              (xy 0.762 0)
            )
            (stroke (width 0) (type default))
            (fill (type none))
          )
          (polyline
            (pts
              (xy 0.762 -1.778)
              (xy 3.302 -1.778)
              (xy 3.302 1.778)
              (xy 0.762 1.778)
            )
            (stroke (width 0) (type default))
            (fill (type none))
          )
          (polyline
            (pts
              (xy 1.016 0)
              (xy 2.032 0.381)
              (xy 2.032 -0.381)
              (xy 1.016 0)
            )
            (stroke (width 0) (type default))
            (fill (type outline))
          )
          (polyline
            (pts
              (xy 2.794 0.508)
              (xy 2.921 0.381)
              (xy 3.683 0.381)
              (xy 3.81 0.254)
            )
            (stroke (width 0) (type default))
            (fill (type none))
          )
          (polyline
            (pts
              (xy 3.302 0.381)
              (xy 2.921 -0.254)
              (xy 3.683 -0.254)
              (xy 3.302 0.381)
            )
            (stroke (width 0) (type default))
            (fill (type none))
          )
          (circle (center 1.651 0) (radius 2.794)
            (stroke (width 0.254) (type default))
            (fill (type none))
          )
          (circle (center 2.54 -1.778) (radius 0.254)
            (stroke (width 0) (type default))
            (fill (type outline))
          )
          (circle (center 2.54 1.778) (radius 0.254)
            (stroke (width 0) (type default))
            (fill (type outline))
          )
        )
        (symbol "Q_NMOS_GSD_1_1"
          (pin input line (at -5.08 0 0) (length 2.54)
            (name "G" (effects (font (size 1.27 1.27))))
            (number "1" (effects (font (size 1.27 1.27))))
          )
          (pin passive line (at 2.54 -5.08 90) (length 2.54)
            (name "S" (effects (font (size 1.27 1.27))))
            (number "2" (effects (font (size 1.27 1.27))))
          )
          (pin passive line (at 2.54 5.08 270) (length 2.54)
            (name "D" (effects (font (size 1.27 1.27))))
            (number "3" (effects (font (size 1.27 1.27))))
          )
        )
      )'''





P4_PIN_NAMES = {
    1: "GPIO25/DP", 2: "GPIO24/DM", 3: "GND", 4: "GPIO7/SDA",
    5: "GPIO8/SCL", 6: "GPIO2", 7: "GPIO3", 8: "GND", 9: "GPIO4",
    10: "GPIO5", 11: "GPIO6", 12: "GPIO14", 13: "GND", 14: "GPIO15",
    15: "GPIO16", 16: "GPIO17", 17: "GPIO18", 18: "GND",
    19: "GPIO19", 20: "GPIO54",
    21: "GPIO48", 22: "GPIO47", 23: "GND", 24: "GPIO46", 25: "GPIO33",
    26: "GPIO32", 27: "GPIO27", 28: "GND", 29: "GPIO26", 30: "RUN",
    31: "GPIO23", 32: "GPIO22", 33: "GND", 34: "GPIO21", 35: "GPIO20",
    36: "3V3", 37: "EN", 38: "GND", 39: "VSYS", 40: "VBUS",
}


def gen_p4_symbol():
    """(symbol "P4_HDR" ...) text: pins 1-20 left, 21-40 right."""
    out = []
    out.append('(symbol "P4_HDR" (pin_names (offset 0.254)) (in_bom yes) (on_board yes)')
    out.append('  (property "Reference" "J" (at -10.16 27.94 0)'
               ' (effects (font (size 1.27 1.27)) (justify left)))')
    out.append('  (property "Value" "ESP32-P4-POE-ETH" (at -10.16 -27.94 0)'
               ' (effects (font (size 1.27 1.27)) (justify left)))')
    out.append('  (property "Footprint" "" (at 0 0 0)'
               ' (effects (font (size 1.27 1.27)) hide))')
    out.append('  (property "Datasheet" "~" (at 0 0 0)'
               ' (effects (font (size 1.27 1.27)) hide))')
    out.append('  (symbol "P4_HDR_0_1"')
    out.append('    (rectangle (start -10.16 25.4) (end 10.16 -25.4)'
               ' (stroke (width 0.254) (type default)) (fill (type background)))')
    out.append('  )')
    out.append('  (symbol "P4_HDR_1_1"')
    for k in range(1, 21):
        y = 24.13 - (k - 1) * 2.54
        out.append('    (pin passive line (at -12.7 %s 0) (length 2.54)'
                   ' (name "%s" (effects (font (size 1.27 1.27))))'
                   ' (number "%d" (effects (font (size 1.27 1.27)))))'
                   % (fmt(y), P4_PIN_NAMES[k], k))
    for k in range(21, 41):
        y = 24.13 - (k - 21) * 2.54
        out.append('    (pin passive line (at 12.7 %s 180) (length 2.54)'
                   ' (name "%s" (effects (font (size 1.27 1.27))))'
                   ' (number "%d" (effects (font (size 1.27 1.27)))))'
                   % (fmt(y), P4_PIN_NAMES[k], k))
    out.append('  )')
    out.append(')')
    return "\n".join(out)


P4_SYMBOL = gen_p4_symbol()


def _symbol_block(txt, name):
    start = txt.index('(symbol "%s"' % name)
    depth, i = 0, start
    while True:
        c = txt[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                break
        i += 1
    return txt[start:i + 1]


def extract_symbol(libfile, name):
    """Return the (symbol "name" ...) block text from a library file.

    KiCad 10 split libraries (<Lib>.kicad_symdir/<Symbol>.kicad_sym, one
    file per root symbol, subunits inside) are resolved as well.
    """
    if name.startswith("Q_NMOS_GSD"):
        return _symbol_block(LOCAL_Q_NMOS_GSD, name)
    if name.startswith("P4_HDR"):
        return _symbol_block(P4_SYMBOL, name)
    p = os.path.join(SYM_DIR, libfile)
    if os.path.exists(p):
        txt = open(p, encoding="utf-8").read()
    else:
        base = libfile[:-len(".kicad_sym")] if libfile.endswith(".kicad_sym") else libfile
        root = re.sub(r"_\d+_\d+$", "", name)
        txt = open(os.path.join(SYM_DIR, base + ".kicad_symdir",
                                root + ".kicad_sym"), encoding="utf-8").read()
    return _symbol_block(txt, name)


def symbol_pins(libfile, name):
    """Pins of subunit _1_1: {number: (x, y, angle)} in symbol coords."""
    block = extract_symbol(libfile, name + "_1_1")
    pins = {}
    for m in re.finditer(
            r'\(pin\s+\S+\s+\S+\s*\(at\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(\d+)\)'
            r'.*?\(number\s+"(\d+)"', block, re.S):
        pins[m.group(4)] = (float(m.group(1)), float(m.group(2)),
                            int(m.group(3)))
    return pins


def symbol_pin_names(libfile, name):
    block = extract_symbol(libfile, name + "_1_1")
    names = {}
    for m in re.finditer(
            r'\(pin\s+\S+\s+\S+\s*\(at\s+.*?\(name\s+"([^"]*)"'
            r'.*?\(number\s+"(\d+)"', block, re.S):
        names[m.group(2)] = m.group(1)
    return names


def _rot(ox, oy, rot):
    if rot == 90:
        return (oy, -ox)
    if rot == 180:
        return (-ox, -oy)
    if rot == 270:
        return (-oy, ox)
    return (ox, oy)


def pin_file_pos(pins, num, pos, rot=0):
    px, py = pins[num][0], pins[num][1]
    ox, oy = _rot(px, -py, rot)
    return (round(pos[0] + ox, 2), round(pos[1] + oy, 2))


def place_by_pin(pins, num, target, rot=0):
    px, py = pins[num][0], pins[num][1]
    ox, oy = _rot(px, -py, rot)
    return (round(target[0] - ox, 2), round(target[1] - oy, 2))


PARTS = {
    "J8": ("Local", "P4_HDR", "ESP32-P4-POE-ETH (32088)", "custom:HDR_2x20_P4"),
    "SJ1": ("Connector_Generic", "Conn_01x03", "5V SEL (HDR+CAP)", "custom:HDR_1x03_P2.54"),
    "F1": ("Device", "Fuse", "PTC 1A", "custom:PTC_P5.00mm"),
    "C3": ("Device", "C_Polarized", "470uF/16V", "Capacitor_THT:CP_Radial_D8.0mm_P3.50mm"),
    "J3": ("Connector_Generic", "Conn_01x02", "BOOST IN MEZZ", "custom:MZ_1x02_P5.08"),
    "J4": ("Connector_Generic", "Conn_01x02", "BOOST OUT MEZZ", "custom:MZ_1x02_P5.08"),
    "C1": ("Device", "C_Polarized", "1000uF/25V PX", "Capacitor_THT:CP_Radial_D10.0mm_P5.00mm"),
    "C2": ("Device", "C", "10uF", "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P2.50mm"),
    "Q1": ("Device", "Q_NMOS_GSD", "MTN2306AN3/IRLML6344", "Package_TO_SOT_SMD:SOT-23"),
    "R1": ("Device", "R", "100", "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal"),
    "R2": ("Device", "R", "10k", "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal"),
    "R3": ("Device", "R", "1k", "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal"),
    "D1": ("Device", "LED", "12V PILOT", "LED_THT:LED_D3.0mm"),
    "J2": ("Connector_Generic", "Conn_01x02", "RING OUT TB111", "custom:TB111_1x02_P5.08"),
    "TP1": ("Connector_Generic", "Conn_01x01", "TP +5V", "custom:TestPoint_D2.0mm"),
    "TP2": ("Connector_Generic", "Conn_01x01", "TP +12V", "custom:TestPoint_D2.0mm"),
}
VAL_OF = {r: v[2] for r, v in PARTS.items()}
FP_OF = {r: v[3] for r, v in PARTS.items()}

PINS = {}
lib_blocks = []
_seen = set()
for _ref, (lib, sym, _val, _fp) in PARTS.items():
    if (lib, sym) in _seen:
        continue
    _seen.add((lib, sym))
    if sym == "P4_HDR":
        block = P4_SYMBOL
    elif sym == "Q_NMOS_GSD":
        block = extract_symbol("Device.kicad_sym", sym)
    else:
        block = extract_symbol(lib + ".kicad_sym", sym)
    block = block.replace('(symbol "%s"' % sym,
                          '(symbol "%s:%s"' % (lib, sym), 1)
    lib_blocks.append(block)
    if sym == "P4_HDR":
        PINS[sym] = {str(k): ((-12.7 if k <= 20 else 12.7),
                              24.13 - ((k - 1) % 20) * 2.54,
                              0 if k <= 20 else 180)
                     for k in range(1, 41)}
    else:
        PINS[sym] = symbol_pins(lib + ".kicad_sym", sym)

print("LED symbol pins:", symbol_pin_names("Device.kicad_sym", "LED"))
print("Fuse symbol pins:", symbol_pin_names("Device.kicad_sym", "Fuse"))



LED_NAMES = symbol_pin_names("Device.kicad_sym", "LED")
LED_A = [n for n, nm in LED_NAMES.items() if nm == "A"][0]
LED_K = [n for n, nm in LED_NAMES.items() if nm == "K"][0]
print("LED anode pin:", LED_A, "cathode pin:", LED_K)


PLAN = {
    "J8": ("1", (32.3, 60), 0),
    "SJ1": ("1", (82, 52), 0),
    "F1": ("1", (108, 52), 0),
    "TP1": ("1", (128, 46), 0),
    "C3": ("1", (108, 76), 0),
    "J3": ("1", (82, 80), 0),
    "J4": ("1", (82, 100), 0),
    "C1": ("1", (108, 98), 0),
    "C2": ("1", (124, 98), 0),
    "TP2": ("1", (140, 86), 0),
    "Q1": ("3", (168, 104), 0),
    "R1": ("1", (150, 109.08), 0),
    "R2": ("1", (157.62, 116), 0),
    "R3": ("1", (146, 66), 0),
    "D1": (LED_A, (160, 66), 0),
    "J2": ("1", (186, 98), 0),
}
POS = {}
PINPOS = {}
PINANG = {}
for ref, (anch, target, rot) in PLAN.items():
    sym = PARTS[ref][1]
    pos = place_by_pin(PINS[sym], anch, target, rot)
    POS[ref] = (pos, rot)
    for num in PINS[sym]:
        PINPOS[(ref, num)] = pin_file_pos(PINS[sym], num, pos, rot)
        PINANG[(ref, num)] = PINS[sym][num][2]

wires = []
junctions = []
labels = []
no_connects = []


def wire(a, b):
    wires.append((a[0], a[1], b[0], b[1]))


def stub_label(a, b, text):
    wire(a, b)
    junctions.append(a)
    labels.append((text, b[0], b[1]))


def PP(ref, pinnum):
    return PINPOS[(ref, pinnum)]



_OUT = {0: (-1, 0), 180: (1, 0), 90: (0, 1), 270: (0, -1)}

STUBS = {
    "J8": {"3": "GND", "8": "GND", "13": "GND", "18": "GND",
           "23": "GND", "28": "GND", "33": "GND", "38": "GND",
           "39": "VSYS", "40": "VBUS", "10": "STROBE"},
    "SJ1": {"1": "VBUS", "2": "+5V_IN", "3": "VSYS"},
    "F1": {"1": "+5V_IN", "2": "+5V"},
    "C3": {"1": "+5V", "2": "GND"},
    "J3": {"1": "+5V", "2": "GND"},
    "J4": {"1": "+12V", "2": "GND"},
    "C1": {"1": "+12V", "2": "GND"},
    "C2": {"1": "+12V", "2": "GND"},
    "Q1": {"3": "DRAIN", "2": "GND"},
    "R1": {"1": "STROBE"},
    "R2": {"2": "GND"},
    "R3": {"1": "+12V"},
    "D1": {LED_K: "GND"},
    "J2": {"1": "+12V", "2": "DRAIN"},
    "TP1": {"1": "+5V"},
    "TP2": {"1": "+12V"},
}
for ref, tab in STUBS.items():
    for num, text in tab.items():
        p = PP(ref, num)
        dx, dy = _OUT[PINANG[(ref, num)]]
        stub_label(p, (round(p[0] + dx * 6.35, 2),
                       round(p[1] + dy * 6.35, 2)), text)


wire(PP("Q1", "1"), PP("R1", "2"))
wire(PP("R1", "2"), PP("R2", "1"))
junctions.append(PP("R1", "2"))
wire(PP("R3", "2"), PP("D1", LED_A))


for k in range(1, 41):
    if str(k) not in STUBS["J8"]:
        no_connects.append(PP("J8", str(k)))


def _on_segment(p, a, b):
    (px, py), (ax, ay), (bx, by) = p, a, b
    cross = (bx - ax) * (py - ay) - (by - ay) * (px - ax)
    if abs(cross) > 0.01:
        return False
    dot = (px - ax) * (px - bx) + (py - ay) * (py - by)
    return dot < -0.001


split_wires = []
for (x1, y1, x2, y2) in wires:
    cuts = [(jx, jy) for (jx, jy) in junctions
            if _on_segment((jx, jy), (x1, y1), (x2, y2))]
    cuts.sort(key=lambda p: (p[0] - x1) ** 2 + (p[1] - y1) ** 2)
    pts = [(x1, y1)] + cuts + [(x2, y2)]
    for a, b in zip(pts, pts[1:]):
        split_wires.append((a[0], a[1], b[0], b[1]))
wires = split_wires

sheet_uuid = U()
sch = []
sch.append('(kicad_sch (version 20230121) (generator eeschema)')
sch.append('  (uuid %s)' % sheet_uuid)
sch.append('  (paper "A3")')
sch.append('  (title_block (title "ESP32-P4 (32088) carrier - 5V select, '
           'polyfuse, AE-LMR62421 boost, IR ring strobe") '
           '(date "2026-11-27") (rev "A"))')
sch.append('  (lib_symbols')
for b in lib_blocks:
    sch.append('    ' + b.replace('\n', '\n    '))
sch.append('  )')
for ref in ("J8", "SJ1", "F1", "C3", "J3", "J4", "C1", "C2", "Q1",
            "R1", "R2", "R3", "D1", "J2", "TP1", "TP2"):
    lib, sym = PARTS[ref][0], PARTS[ref][1]
    pos, r = POS[ref]
    sch.append('  (symbol (lib_id "%s:%s") (at %.2f %.2f %d) (unit 1) '
               '(in_bom yes) (on_board yes) (dnp no) (uuid %s)'
               % (lib, sym, pos[0], pos[1], r, U()))
    sch.append('    (property "Reference" "%s" (at %.2f %.2f 0) '
               '(effects (font (size 1.27 1.27))))'
               % (ref, pos[0], pos[1] - 2.54))
    sch.append('    (property "Value" "%s" (at %.2f %.2f 0) '
               '(effects (font (size 1.27 1.27))))'
               % (VAL_OF[ref], pos[0], pos[1] + 2.54))
    sch.append('    (property "Footprint" "%s" (at %.2f %.2f 0) '
               '(effects (font (size 1.27 1.27)) hide))'
               % (FP_OF[ref], pos[0], pos[1]))
    sch.append('    (property "Datasheet" "" (at %.2f %.2f 0) '
               '(effects (font (size 1.27 1.27)) hide))' % (pos[0], pos[1]))
    for num in sorted(PINS[sym], key=lambda s: (len(s), s)):
        sch.append('    (pin "%s" (uuid %s))' % (num, U()))
    sch.append('    (instances (project "%s" (path "/%s" '
               '(reference "%s") (unit 1))))' % (PROJ, sheet_uuid, ref))
    sch.append('  )')
for (x1, y1, x2, y2) in wires:
    sch.append('  (wire (pts (xy %.2f %.2f) (xy %.2f %.2f)) '
               '(stroke (width 0) (type default)) (uuid %s))'
               % (x1, y1, x2, y2, U()))
for (x, y) in junctions:
    sch.append('  (junction (at %.2f %.2f) (diameter 0) (color 0 0 0 0) '
               '(uuid %s))' % (x, y, U()))
for (text, x, y) in labels:
    sch.append('  (global_label "%s" (shape input) (at %.2f %.2f 0) '
               '(effects (font (size 1.27 1.27)) (justify left)) (uuid %s))'
               % (text, x, y, U()))
for (x, y) in no_connects:
    sch.append('  (no_connect (at %.2f %.2f) (uuid %s))' % (x, y, U()))
sch.append('  (sheet_instances (path "/" (page "1")))')
sch.append(')')
with open(os.path.join(HERE, PROJ + ".kicad_sch"), "w") as f:
    f.write("\n".join(sch) + "\n")
print("schematic written")



import pcbnew
MM = pcbnew.FromMM

board = pcbnew.BOARD()
nets = {}
for name in ("VBUS", "VSYS", "+5V_IN", "+5V", "+12V", "GND", "STROBE",
             "DRAIN", "GATE", "LED_A"):
    ni = pcbnew.NETINFO_ITEM(board, name)
    board.Add(ni)
    nets[name] = ni.GetNetCode()


def load_fp(lib, name):
    return pcbnew.FootprintLoad(os.path.join(FP_DIR, lib + ".pretty"), name)


def add_fp(lib, name, ref, value, pos, rot=0, netmap=None):
    fp = load_fp(lib, name)
    fp.SetReference(ref)
    fp.SetValue(value)
    fp.SetPosition(pcbnew.VECTOR2I(MM(pos[0]), MM(pos[1])))
    fp.SetOrientationDegrees(rot)
    board.Add(fp)
    if netmap:
        for pad in fp.Pads():
            n = netmap.get(pad.GetNumber())
            if n:
                pad.SetNetCode(nets[n])
    return fp


CUSTOM_PAD_POS = {}


def pad_pos(fp, num):
    key = (fp.GetReference(), str(num))
    if key in CUSTOM_PAD_POS:
        return CUSTOM_PAD_POS[key]
    for pad in fp.Pads():
        if pad.GetNumber() == str(num):
            p = pad.GetPosition()
            return (pcbnew.ToMM(p.x), pcbnew.ToMM(p.y))
    raise KeyError(num)


def track(a, b, w, net, layer=pcbnew.F_Cu):
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1])))
    t.SetEnd(pcbnew.VECTOR2I(MM(b[0]), MM(b[1])))
    t.SetWidth(MM(w))
    t.SetLayer(layer)
    t.SetNetCode(nets[net])
    board.Add(t)


def via(pos, net):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pcbnew.VECTOR2I(MM(pos[0]), MM(pos[1])))
    v.SetViaType(pcbnew.VIATYPE_THROUGH)
    v.SetDrill(MM(0.3))
    v.SetWidth(MM(0.6))
    v.SetNetCode(nets[net])
    board.Add(v)




def _layers(*ids):
    ls = pcbnew.LSET()
    for i in ids:
        ls.AddLayer(i)
    return ls


def _new_fp(name, ref, value, pos):
    fp = pcbnew.FOOTPRINT(board)
    fp.SetFPID(pcbnew.LIB_ID("custom", name))
    fp.SetReference(ref)
    fp.SetValue(value)
    fp.SetPosition(pcbnew.VECTOR2I(MM(pos[0]), MM(pos[1])))
    board.Add(fp)
    return fp


def _abs(fp, lx, ly):
    """Footprint-child setters take absolute board coords in KiCad 10
    (they store position minus the footprint origin). Convert the
    intended footprint-local coords to absolute."""
    fp_pos = fp.GetPosition()
    return (round(pcbnew.ToMM(fp_pos.x) + lx, 3),
            round(pcbnew.ToMM(fp_pos.y) + ly, 3))


def _pth(fp, num, lx, ly, net=None, size=1.7, drill=1.0, rect=False):
    p = pcbnew.PAD(fp)
    p.SetNumber(str(num))
    p.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
    p.SetShape(pcbnew.PAD_SHAPE_RECT if rect else pcbnew.PAD_SHAPE_CIRCLE)
    p.SetSize(pcbnew.VECTOR2I(MM(size), MM(size)))
    p.SetDrillSize(pcbnew.VECTOR2I(MM(drill), MM(drill)))
    p.SetLayerSet(_layers(pcbnew.F_Cu, pcbnew.B_Cu,
                          pcbnew.F_Mask, pcbnew.B_Mask))
    ax, ay = _abs(fp, lx, ly)
    p.SetPosition(pcbnew.VECTOR2I(MM(ax), MM(ay)))
    if net:
        p.SetNetCode(nets[net])
    fp.Add(p)
    fp_pos = fp.GetPosition()
    CUSTOM_PAD_POS[(fp.GetReference(), str(num))] = (
        round(pcbnew.ToMM(fp_pos.x) + lx, 2),
        round(pcbnew.ToMM(fp_pos.y) + ly, 2))
    return p


def _npth(fp, num, lx, ly, drill, clearance=1.0):
    """Non-plated clearance hole (no net, never soldered). The local
    clearance keeps every copper pour - above all GND - away from
    the hole edge."""
    p = pcbnew.PAD(fp)
    p.SetNumber(str(num))
    p.SetAttribute(pcbnew.PAD_ATTRIB_NPTH)
    p.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
    p.SetSize(pcbnew.VECTOR2I(MM(drill), MM(drill)))
    p.SetDrillSize(pcbnew.VECTOR2I(MM(drill), MM(drill)))
    p.SetLayerSet(_layers(pcbnew.F_Cu, pcbnew.B_Cu,
                          pcbnew.F_Mask, pcbnew.B_Mask))
    p.SetLocalClearance(MM(clearance))
    ax, ay = _abs(fp, lx, ly)
    p.SetPosition(pcbnew.VECTOR2I(MM(ax), MM(ay)))
    fp.Add(p)
    return p


def _smd(fp, num, lx, ly, w, h, net=None):
    p = pcbnew.PAD(fp)
    p.SetNumber(str(num))
    p.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    p.SetShape(pcbnew.PAD_SHAPE_RECT)
    p.SetSize(pcbnew.VECTOR2I(MM(w), MM(h)))
    p.SetLayerSet(_layers(pcbnew.F_Cu, pcbnew.F_Paste, pcbnew.F_Mask))
    ax, ay = _abs(fp, lx, ly)
    p.SetPosition(pcbnew.VECTOR2I(MM(ax), MM(ay)))
    if net:
        p.SetNetCode(nets[net])
    fp.Add(p)
    fp_pos = fp.GetPosition()
    CUSTOM_PAD_POS[(fp.GetReference(), str(num))] = (
        round(pcbnew.ToMM(fp_pos.x) + lx, 2),
        round(pcbnew.ToMM(fp_pos.y) + ly, 2))
    return p


def _fp_rect(fp, layer, x1, y1, x2, y2, width=0.12):
    for a, b in [((x1, y1), (x2, y1)), ((x2, y1), (x2, y2)),
                 ((x2, y2), (x1, y2)), ((x1, y2), (x1, y1))]:
        s = pcbnew.PCB_SHAPE(fp)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        sa = _abs(fp, a[0], a[1])
        sb = _abs(fp, b[0], b[1])
        s.SetStart(pcbnew.VECTOR2I(MM(sa[0]), MM(sa[1])))
        s.SetEnd(pcbnew.VECTOR2I(MM(sb[0]), MM(sb[1])))
        s.SetLayer(layer)
        s.SetWidth(MM(width))
        fp.Add(s)







J8_POS = (26.26, 30.61)
j8 = _new_fp("HDR_2x20_P4", "J8", VAL_OF["J8"], J8_POS)
J8_NETS = {3: "GND", 8: "GND", 13: "GND", 18: "GND", 23: "GND",
           28: "GND", 33: "GND", 38: "GND", 39: "VSYS", 40: "VBUS",
           10: "STROBE"}
for k in range(1, 21):
    _pth(j8, k, (k - 1) * 2.54, 0, J8_NETS.get(k), rect=(k == 1))
for k in range(21, 41):
    _pth(j8, k, (k - 21) * 2.54, 17.78, J8_NETS.get(k))
_fp_rect(j8, pcbnew.F_CrtYd, -22.26, -1.61, 55.74, 19.39)
_fp_rect(j8, pcbnew.F_SilkS, -22.26, -1.61, 55.74, 19.39)
_dot = pcbnew.PCB_SHAPE(j8)
_dot.SetShape(pcbnew.SHAPE_T_CIRCLE)
_dc = _abs(j8, -1.6, 0)
_de = _abs(j8, -1.0, 0)
_dot.SetCenter(pcbnew.VECTOR2I(MM(_dc[0]), MM(_dc[1])))
_dot.SetEnd(pcbnew.VECTOR2I(MM(_de[0]), MM(_de[1])))
_dot.SetLayer(pcbnew.F_SilkS)
_dot.SetWidth(MM(0.12))
_dot.SetFilled(True)
j8.Add(_dot)
j8.Reference().SetPosition(pcbnew.VECTOR2I(MM(43), MM(35.5)))
j8.Value().SetPosition(pcbnew.VECTOR2I(MM(43), MM(42.5)))
j8.Value().SetVisible(False)





SJ1_POS = (73.26, 54)
sj1 = _new_fp("HDR_1x03_P2.54", "SJ1", VAL_OF["SJ1"], SJ1_POS)
_pth(sj1, 1, 2.54, 0, "VBUS", size=1.7, drill=1.0)
_pth(sj1, 2, 0, 0, "+5V_IN", size=1.7, drill=1.0)
_pth(sj1, 3, -2.54, 0, "VSYS", size=1.7, drill=1.0)
_fp_rect(sj1, pcbnew.F_CrtYd, -3.81, -1.27, 3.81, 1.27)
sj1.Reference().SetPosition(pcbnew.VECTOR2I(MM(73.26), MM(51.3)))
sj1.Value().SetVisible(False)


F1_POS = (62, 26)
f1 = _new_fp("PTC_P5.00mm", "F1", VAL_OF["F1"], F1_POS)
_pth(f1, 1, 0, 0, "+5V_IN", size=1.7, drill=0.9)
_pth(f1, 2, -5, 0, "+5V", size=1.7, drill=0.9)
_fp_rect(f1, pcbnew.F_CrtYd, -6.2, -1.7, 1.2, 1.7)
_fp_rect(f1, pcbnew.F_SilkS, -6.2, -1.7, 1.2, 1.7)
f1.Reference().SetPosition(pcbnew.VECTOR2I(MM(59.5), MM(22.1)))
f1.Value().SetVisible(False)


def _testpoint(ref, pos, net):
    tp = _new_fp("TestPoint_D2.0mm", ref, "", pos)
    _smd(tp, 1, 0, 0, 2.0, 2.0, net)
    _fp_rect(tp, pcbnew.F_CrtYd, -1.1, -1.1, 1.1, 1.1)
    tp.Reference().SetPosition(pcbnew.VECTOR2I(MM(pos[0]), MM(pos[1] - 2.3)))
    tp.Value().SetVisible(False)
    return tp


tp1 = _testpoint("TP1", (44, 24.2), "+5V")
tp2 = _testpoint("TP2", (43, 9.4), "+12V")


c3 = add_fp("Capacitor_THT", "CP_Radial_D8.0mm_P3.50mm",
            "C3", VAL_OF["C3"], (51, 19), 270, {"1": "+5V", "2": "GND"})
c3.Reference().SetPosition(pcbnew.VECTOR2I(MM(43), MM(18.5)))











def _mezz(ref, pos, plus_net, ref_dx=3.4, ref_dy=-2.5):


    mz = _new_fp("MZ_1x02_P5.08", ref, VAL_OF[ref], pos)
    _pth(mz, 1, 0, 0, plus_net, size=2.6, drill=1.5)
    _pth(mz, 2, 0, -5.08, "GND", size=2.6, drill=1.5)
    _fp_rect(mz, pcbnew.F_CrtYd, -1.8, -6.88, 1.8, 1.8)
    mz.Reference().SetPosition(pcbnew.VECTOR2I(MM(pos[0] + ref_dx),
                                               MM(pos[1] + ref_dy)))
    mz.Value().SetVisible(False)
    return mz


j3 = _mezz("J3", (4.5, 10.08), "+5V")
j4 = _mezz("J4", (27.5, 10.08), "+12V", ref_dx=-7)














lh = _new_fp("LEG_CLEAR_7", "LH1", "BOOST LEG CLEARANCE", (31, -4))
for i, (lx, ly) in enumerate([(4.5, 20.5), (4.5, 23.0),
                              (25.5, 20.5), (25.5, 23.0)]):
    _npth(lh, i + 1, -lx, ly, 1.8)
for i, lx in enumerate([12.46, 15.0, 17.54]):
    _npth(lh, i + 5, -lx, 3.0, 1.8)
lh.Reference().SetPosition(pcbnew.VECTOR2I(MM(16), MM(11.5)))
lh.Value().SetVisible(False)
c1 = add_fp("Capacitor_THT", "CP_Radial_D10.0mm_P5.00mm",
            "C1", VAL_OF["C1"], (50, 8), 270, {"1": "+12V", "2": "GND"})
c1.Reference().SetPosition(pcbnew.VECTOR2I(MM(43.5), MM(4.5)))
for _p in c1.Pads():
    if _p.GetNumber() == "2":
        _p.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)
c2 = add_fp("Capacitor_THT", "C_Disc_D5.0mm_W2.5mm_P2.50mm",
            "C2", VAL_OF["C2"], (58.75, 2), 0, {"1": "+12V", "2": "GND"})
c2.Reference().SetPosition(pcbnew.VECTOR2I(MM(60), MM(5.4)))
q1 = add_fp("Package_TO_SOT_SMD", "SOT-23",
            "Q1", VAL_OF["Q1"], (64, 6), 0,
            {"1": "GATE", "2": "GND", "3": "DRAIN"})
q1.Reference().SetPosition(pcbnew.VECTOR2I(MM(67.4), MM(6)))
r1 = add_fp("Resistor_THT", "R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",
            "R1", VAL_OF["R1"], (61.5, 9.5), 270,
            {"1": "GATE", "2": "STROBE"})
r1.Reference().SetPosition(pcbnew.VECTOR2I(MM(64.4), MM(13.5)))
r2 = add_fp("Resistor_THT", "R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",
            "R2", VAL_OF["R2"], (58.2, 9.5), 270,
            {"1": "GATE", "2": "GND"})
r2.Reference().SetPosition(pcbnew.VECTOR2I(MM(55.2), MM(13.5)))
r3 = add_fp("Resistor_THT", "R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",
            "R3", VAL_OF["R3"], (67.69, 19), 0,
            {"1": "+12V", "2": "LED_A"})
r3.Reference().SetPosition(pcbnew.VECTOR2I(MM(67.69), MM(21.8)))
d1 = add_fp("LED_THT", "LED_D3.0mm",
            "D1", VAL_OF["D1"], (79, 19), 270,
            {LED_A: "LED_A", LED_K: "GND"})
d1.Reference().SetPosition(pcbnew.VECTOR2I(MM(79), MM(15.4)))



j2 = _new_fp("TB111_1x02_P5.08", "J2", VAL_OF["J2"], (81, 12))
_pth(j2, 1, 0, 0, "+12V", size=2.6, drill=1.4)
_pth(j2, 2, 0, -5.08, "DRAIN", size=2.6, drill=1.4)
_fp_rect(j2, pcbnew.F_CrtYd, -7.5, -7.68, 3.5, 2.6)
j2.Reference().SetPosition(pcbnew.VECTOR2I(MM(76), MM(3.4)))
j2.Value().SetVisible(False)




for i, (hx, hy) in enumerate([(4, -1), (28, -1), (4, 23), (28, 23)]):
    h = add_fp("MountingHole", "MountingHole_3.2mm_M3",
               "H%d" % (i + 1), "", (hx, hy), 0)
    h.Reference().SetVisible(False)
    h.Value().SetVisible(False)
    if i >= 2:






        for _sh in h.GraphicalItems():
            if (_sh.GetLayer() == pcbnew.F_CrtYd
                    and _sh.GetShape() == pcbnew.SHAPE_T_CIRCLE):
                _sh.SetRadius(MM(3.2))



for i, (hx, hy) in enumerate([(82, -1), (4, 54), (82, 54)]):
    h = add_fp("MountingHole", "MountingHole_3.2mm_M3",
               "H%d" % (i + 5), "", (hx, hy), 0)
    h.Reference().SetVisible(False)
    h.Value().SetVisible(False)

for _fp in board.GetFootprints():
    _bb = _fp.GetCourtyard(pcbnew.F_CrtYd).BBox()
    print(_fp.GetReference(), "courtyard x %.2f..%.2f y %.2f..%.2f" % (
        pcbnew.ToMM(_bb.GetLeft()), pcbnew.ToMM(_bb.GetRight()),
        pcbnew.ToMM(_bb.GetTop()), pcbnew.ToMM(_bb.GetBottom())),
        "pads", {p.GetNumber(): (round(pcbnew.ToMM(p.GetPosition().x), 2),
                                 round(pcbnew.ToMM(p.GetPosition().y), 2))
                 for p in _fp.Pads()})



track(pad_pos(j8, "40"), (75.8, 50.6), 0.6, "VBUS")
track((75.8, 50.6), pad_pos(sj1, "1"), 0.6, "VBUS")
track(pad_pos(j8, "39"), (70.72, 50.6), 0.6, "VSYS")
track((70.72, 50.6), pad_pos(sj1, "3"), 0.6, "VSYS")

track(pad_pos(sj1, "2"), (73.26, 56.8), 0.8, "+5V_IN")
track((73.26, 56.8), (77.5, 56.8), 0.8, "+5V_IN")
track((77.5, 56.8), (77.5, 23), 0.6, "+5V_IN")
track((77.5, 23), (62, 23), 0.8, "+5V_IN")
track((62, 23), pad_pos(f1, "1"), 0.8, "+5V_IN")



track(pad_pos(f1, "2"), (57, 24.2), 1.0, "+5V")
track((57, 24.2), (44, 24.2), 1.0, "+5V")
track((48, 24.2), (48, 19), 1.0, "+5V")
track((48, 19), pad_pos(c3, "1"), 1.0, "+5V")
track((48, 19), (48, 13.9), 1.0, "+5V")
track((48, 13.9), (10, 13.9), 1.0, "+5V")
track((10, 13.9), (10, 10.08), 1.0, "+5V")
track((10, 10.08), pad_pos(j3, "1"), 1.0, "+5V")



track(pad_pos(j4, "1"), (46.5, 10.08), 0.8, "+12V")
via((46.5, 10.08), "+12V")


track((46.5, 10.08), (46.5, 0), 1.0, "+12V", pcbnew.B_Cu)
track((46.5, 0), (76, 0), 1.0, "+12V", pcbnew.B_Cu)
track((55, 0), (55, 8), 1.0, "+12V", pcbnew.B_Cu)
track((55, 8), pad_pos(c1, "1"), 1.0, "+12V", pcbnew.B_Cu)
track(pad_pos(c2, "1"), (58.75, 0), 1.0, "+12V", pcbnew.B_Cu)
track((76, 0), (76, 12), 1.0, "+12V", pcbnew.B_Cu)
track((76, 12), pad_pos(j2, "1"), 1.0, "+12V", pcbnew.B_Cu)

track(pad_pos(r3, "1"), (67.69, 8), 0.5, "+12V")
track((67.69, 8), (76, 8), 0.5, "+12V")
via((76, 8), "+12V")
track(pad_pos(r3, "2"), pad_pos(d1, LED_A), 0.5, "LED_A")
track(pad_pos(d1, LED_K), (82.5, 21.54), 0.5, "GND")
via((82.5, 21.54), "GND")


track(pad_pos(q1, "3"), (72, 6), 1.0, "DRAIN")
track((72, 6), (72, 2), 1.0, "DRAIN")
track((72, 2), (83.6, 2), 1.0, "DRAIN")
track((83.6, 2), (83.6, 6.92), 1.0, "DRAIN")
track((83.6, 6.92), pad_pos(j2, "2"), 1.0, "DRAIN")

track(pad_pos(q1, "1"), (61.5, 5.05), 0.4, "GATE")
track((61.5, 5.05), pad_pos(r1, "1"), 0.4, "GATE")
track(pad_pos(r2, "1"), pad_pos(r1, "1"), 0.4, "GATE")

track(pad_pos(q1, "2"), (63.06, 10.5), 0.6, "GND")
via((63.06, 10.5), "GND")


track(pad_pos(r1, "2"), (61.5, 21), 0.4, "STROBE")
track((61.5, 21), (59.8, 21), 0.4, "STROBE")
track((59.8, 21), (59.8, 27.3), 0.4, "STROBE")
track((59.8, 27.3), (49.12, 27.3), 0.4, "STROBE")
track((49.12, 27.3), pad_pos(j8, "10"), 0.4, "STROBE")

for p in [(2.5, 27), (84, 27), (36, -3), (84.5, -3.5)]:
    via(p, "GND")



for a, b in [((0, -5), (86, -5)), ((86, -5), (86, 58)),
             ((86, 58), (0, 58)), ((0, 58), (0, -5))]:
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1])))
    s.SetEnd(pcbnew.VECTOR2I(MM(b[0]), MM(b[1])))
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetWidth(MM(0.1))
    board.Add(s)


for a, b in [((1, -4), (31, -4)), ((31, -4), (31, 26)),
             ((31, 26), (1, 26)), ((1, 26), (1, -4))]:
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1])))
    s.SetEnd(pcbnew.VECTOR2I(MM(b[0]), MM(b[1])))
    s.SetLayer(pcbnew.F_SilkS)
    s.SetWidth(MM(0.12))
    board.Add(s)


for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNetCode(nets["GND"])
    z.SetLocalClearance(MM(0.25))
    z.SetMinThickness(MM(0.25))
    chain = pcbnew.SHAPE_LINE_CHAIN()
    for (cx, cy) in [(0.3, -4.7), (85.7, -4.7), (85.7, 57.7), (0.3, 57.7)]:
        chain.Append(MM(cx), MM(cy))
    chain.SetClosed(True)
    z.Outline().AddOutline(chain)
    board.Add(z)





def silk(text, pos, size=0.9):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(text)
    t.SetPosition(pcbnew.VECTOR2I(MM(pos[0]), MM(pos[1])))
    t.SetLayer(pcbnew.F_SilkS)
    t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
    t.SetTextSize(pcbnew.VECTOR2I(MM(size), MM(size)))
    t.SetTextThickness(MM(size * 0.15))
    board.Add(t)


def silk_b(text, pos, size=0.9):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(text)
    t.SetPosition(pcbnew.VECTOR2I(MM(pos[0]), MM(pos[1])))
    t.SetLayer(pcbnew.B_SilkS)
    t.SetMirrored(True)
    t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
    t.SetTextSize(pcbnew.VECTOR2I(MM(size), MM(size)))
    t.SetTextThickness(MM(size * 0.15))
    board.Add(t)


silk("BOOST MODULE (AE-LMR62421)", (3, 12.2), 1.0)
silk("CAP SIDE", (10.8, 24.3), 0.8)
silk("ESP32-P4-POE-ETH (32088)", (33, 40.5), 1.2)
silk("VBUS", (76.6, 54), 0.8)
silk("VSYS", (66.8, 54), 0.8)
silk("R+", (75.6, 12), 0.8)
silk("R-", (75.6, 6.92), 0.8)
silk("MAX 18V", (44, -0.8), 0.9)




os.makedirs(os.path.join(HERE, "custom.pretty"), exist_ok=True)
_io = pcbnew.PCB_IO_KICAD_SEXPR()
for _cfp in (j8, sj1, f1, tp1, tp2, j3, j4, j2, lh):
    _io.FootprintSave(os.path.join(HERE, "custom.pretty"), _cfp)

board.Save(os.path.join(HERE, PROJ + ".kicad_pcb"))
print("pcb written")

pro = {
    "board": {"design_settings": {"defaults": {}}, "layer_presets": [], "viewports": []},
    "boards": [],
    "cvpcb": {"equivalence_files": []},
    "erc": {"erc_exclusions": [], "meta": {"version": 0}, "pin_map": [], "rule_severities": {}},
    "libraries": {"pinned_footprint_libs": [], "pinned_symbol_libs": []},
    "meta": {"filename": PROJ + ".kicad_pro", "version": 1},
    "net_settings": {"classes": [{"bus_width": 12, "clearance": 0.2, "diff_pair_gap": 0.25,
                                  "diff_pair_via_gap": 0.25, "diff_pair_width": 0.2,
                                  "microvia_diameter": 0.3, "microvia_drill": 0.1, "name": "Default",
                                  "pcb_color": "rgba(0, 0, 0, 0.000)", "schematic_color": "rgba(0, 0, 0, 0.000)",
                                  "track_width": 0.25, "via_diameter": 0.6, "via_drill": 0.3,
                                  "wire_width": 6}], "meta": {"version": 3}, "net_colors": None, "netclass_assignments": None, "netclass_patterns": []},
    "pcbnew": {"last_paths": {"gencad": "", "idf": "", "netlist": "", "plot": "", "pos_files": "", "specctra_dsn": "", "step": "", "svg": "", "vrml": ""}, "page_layout_descr_file": ""},
    "schematic": {"annotate_start_num": 0, "drawing": {}, "legacy_lib_dir": "", "legacy_lib_list": [], "meta": {"version": 1}, "pin_symbol_size": 0, "text_offset_ratio": 0.08},
    "text_variables": {},
}
open(os.path.join(HERE, PROJ + ".kicad_pro"), "w").write(json.dumps(pro, indent=1))


sym_libs = ["Device", "Connector_Generic", "Connector"]
fp_libs = ["Capacitor_THT", "Package_TO_SOT_SMD", "Resistor_THT",
           "LED_THT", "MountingHole"]
with open(os.path.join(HERE, "sym-lib-table"), "w") as f:
    f.write("(sym_lib_table\n  (version 7)\n")
    for n in sym_libs:
        f.write('  (lib (name "%s") (type "KiCad") (uri "${KICAD10_SYMBOL_DIR}/%s.kicad_symdir") (options "") (descr ""))\n' % (n, n))
    f.write(")\n")
with open(os.path.join(HERE, "fp-lib-table"), "w") as f:
    f.write("(fp_lib_table\n  (version 7)\n")
    f.write('  (lib (name "custom") (type "KiCad") (uri "${KIPRJMOD}/custom.pretty") (options "") (descr ""))\n')
    for n in fp_libs:
        f.write('  (lib (name "%s") (type "KiCad") (uri "${KICAD10_FOOTPRINT_DIR}/%s.pretty") (options "") (descr ""))\n' % (n, n))
    f.write(")\n")

with open(os.path.join(HERE, "netlist.txt"), "w") as f:
    f.write("Expected nets (design intent):\n")
    f.write("VBUS  : J8.40 SJ1.1\n")
    f.write("VSYS  : J8.39 SJ1.3\n")
    f.write("+5V_IN: SJ1.2 F1.1 (SJ1 bridge selects VBUS or VSYS)\n")
    f.write("+5V   : F1.2 C3.1 J3.1 TP1.1\n")
    f.write("+12V  : J4.1 C1.1 C2.1 TP2.1 J2.1 R3.1\n")
    f.write("GND   : J8.3/8/13/18/23/28/33/38 C3.2 J3.2 J4.2 C1.2 C2.2 Q1.2(S) R2.2 D1.K\n")
    f.write("DRAIN : J2.2 Q1.3(D)\n")
    f.write("GATE  : Q1.1(G) R1.1 R2.1\n")
    f.write("STROBE: J8.10 R1.2\n")
    f.write("LED_A : R3.2 D1.A\n")
print("project written")
