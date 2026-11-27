#!/usr/bin/env python3
"""Generate the IR ring strobe driver KiCad project (schematic + PCB).

GPIO (3.3V) -> 100R -> Nch MOSFET gate (10k pull-down) -> low-side switch
of the +12V line feeding the FRS5CC LED ring via JST-XH. Bulk 1000uF/25V
(+10uF ceramic) sits on the +12V node next to the switch so the pulse
current comes from the capacitors, not the boost converter.

Schematic emission follows the exact KiCad 7.0 dialect proven in the
TPS613221A boost project (unquoted uuids, global labels for all nets).
PCB is emitted as text and zone-filled afterwards:
    python3 build_design.py
    xvfb-run -a python3 fill_zones.py IR_ring_strobe.kicad_pcb
"""
import math
import os
import re
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = "IR_ring_strobe"
SYM_DIR = "/usr/share/kicad/symbols"
FP_DIR = "/usr/share/kicad/footprints"


def U():
    return str(uuid.uuid4())


def fmt(v):
    s = ("%.4f" % v).rstrip("0").rstrip(".")
    return s if s not in ("-0", "") else "0"


def extract_symbol(libfile, name):
    txt = open(os.path.join(SYM_DIR, libfile), encoding="utf-8").read()
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


def symbol_pins(libfile, name):
    """Pins of subunit _1_1: {number: (x, y)} in symbol coords (y up)."""
    block = extract_symbol(libfile, name + "_1_1")
    pins = {}
    for m in re.finditer(
            r'\(pin\s+\S+\s+\S+\s*\(at\s+(-?[\d.]+)\s+(-?[\d.]+)\s+\d+\)'
            r'.*?\(number\s+"(\d+)"', block, re.S):
        pins[m.group(3)] = (float(m.group(1)), float(m.group(2)))
    return pins


def _rot(ox, oy, rot):
    if rot == 90:
        return (oy, -ox)
    if rot == 180:
        return (-ox, -oy)
    if rot == 270:
        return (-oy, ox)
    return (ox, oy)


def pin_file_pos(pins, num, pos, rot=0):
    px, py = pins[num]
    ox, oy = _rot(px, -py, rot)
    return (round(pos[0] + ox, 2), round(pos[1] + oy, 2))


def place_by_pin(pins, num, target, rot=0):
    px, py = pins[num]
    ox, oy = _rot(px, -py, rot)
    return (round(target[0] - ox, 2), round(target[1] - oy, 2))


PARTS = {
    "J1": ("Connector_Generic", "Conn_01x03", "IN 12V/GND/STROBE",
           "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical"),
    "J2": ("Connector_Generic", "Conn_01x02", "RING OUT JST-XH",
           "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical"),
    "Q1": ("Device", "Q_NMOS_GSD", "MTN2306AN3/AO3400A",
           "Package_TO_SOT_SMD:SOT-23"),
    "R1": ("Device", "R", "100",
           "Resistor_SMD:R_0603_1608Metric_Pad0.98x0.95mm_HandSolder"),
    "R2": ("Device", "R", "10k",
           "Resistor_SMD:R_0603_1608Metric_Pad0.98x0.95mm_HandSolder"),
    "C1": ("Device", "C_Polarized", "1000uF/25V",
           "Capacitor_THT:CP_Radial_D10.0mm_P5.00mm"),
    "C2": ("Device", "C", "10uF",
           "Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder"),
    "TP2": ("Connector", "TestPoint", "GATE",
            "TestPoint:TestPoint_Pad_D1.5mm"),
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
    block = extract_symbol(lib + ".kicad_sym", sym)
    block = block.replace('(symbol "%s"' % sym,
                          '(symbol "%s:%s"' % (lib, sym), 1)
    lib_blocks.append(block)
    PINS[sym] = symbol_pins(lib + ".kicad_sym", sym)


PLAN = {
    "J1": ("1", (30, 50), 0),
    "J2": ("1", (102, 50), 0),
    "C1": ("1", (56, 64), 0),
    "C2": ("1", (64, 64), 0),
    "Q1": ("3", (84, 78), 0),
    "R1": ("2", (68, 83.08), 90),
    "R2": ("1", (64, 90), 0),
    "TP2": ("1", (72, 90), 0),
}
POS = {}
PINPOS = {}
for ref, (anch, target, rot) in PLAN.items():
    sym = PARTS[ref][1]
    pos = place_by_pin(PINS[sym], anch, target, rot)
    POS[ref] = (pos, rot)
    for num in PINS[sym]:
        PINPOS[(ref, num)] = pin_file_pos(PINS[sym], num, pos, rot)

wires = []
junctions = []
labels = []


def wire(a, b):
    wires.append((a[0], a[1], b[0], b[1]))


def stub_label(a, b, text):
    wire(a, b)
    junctions.append(a)
    labels.append((text, b[0], b[1]))


def PP(ref, pinnum):
    return PINPOS[(ref, pinnum)]


wire(PP("J1", "1"), PP("J2", "1"))
wire((56, 50), PP("C1", "1")); junctions.append((56, 50))
wire((64, 50), PP("C2", "1")); junctions.append((64, 50))
wire(PP("C1", "2"), (56, 78)); labels.append(("GND", 56, 78))
wire(PP("C2", "2"), (64, 78)); labels.append(("GND", 64, 78))
stub_label((84, 50), (84, 45), "+12V")

wire(PP("J1", "2"), (38, 52.54)); labels.append(("GND", 38, 52.54))
wire(PP("J1", "3"), (38, 55.08)); labels.append(("STROBE", 38, 55.08))

wire(PP("J2", "2"), (102, 78))
wire((102, 78), PP("Q1", "3"))

wire(PP("Q1", "2"), (84, 94)); labels.append(("GND", 84, 94))

wire(PP("Q1", "1"), PP("R1", "2"))
wire(PP("R1", "1"), (52, 83.08))
wire((52, 83.08), (52, 92)); labels.append(("STROBE", 52, 92))
wire((64, 83.08), PP("R1", "2"))
wire((64, 83.08), PP("R2", "1")); junctions.append((64, 83.08))
wire(PP("R2", "2"), (64, 102)); labels.append(("GND", 64, 102))
wire((72, 83.08), PP("TP2", "1")); junctions.append((72, 83.08))


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
sch.append('  (paper "A4")')
sch.append('  (title_block (title "IR LED ring strobe driver - GPIO to '
           'MOSFET 12V pulse switch") (date "2026-11-27") (rev "A"))')
sch.append('  (lib_symbols')
for b in lib_blocks:
    sch.append('    ' + b.replace('\n', '\n    '))
sch.append('  )')
for ref in ("J1", "J2", "C1", "C2", "Q1", "R1", "R2", "TP2"):
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
    for num in sorted(PINS[sym]):
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
sch.append('  (sheet_instances (path "/" (page "1")))')
sch.append(')')
with open(os.path.join(HERE, PROJ + ".kicad_sch"), "w") as f:
    f.write("\n".join(sch) + "\n")


PCB_PARTS = [

    ("J1", "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical",
     (3.5, 10), 0, {"1": "+12V", "2": "GND", "3": "STROBE"}),
    ("J2", "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical",
     (33.75, 10), 0, {"1": "+12V", "2": "DRAIN"}),
    ("C1", "Capacitor_THT:CP_Radial_D10.0mm_P5.00mm",
     (21.5, 13), 0, {"1": "+12V", "2": "GND"}),
    ("C2", "Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder",
     (16.5, 16.5), 0, {"1": "+12V", "2": "GND"}),
    ("Q1", "Package_TO_SOT_SMD:SOT-23",
     (30, 20), 0, {"1": "GATE", "2": "GND", "3": "DRAIN"}),
    ("R1", "Resistor_SMD:R_0603_1608Metric_Pad0.98x0.95mm_HandSolder",
     (20.5, 20.5), 0, {"1": "STROBE", "2": "GATE"}),
    ("R2", "Resistor_SMD:R_0603_1608Metric_Pad0.98x0.95mm_HandSolder",
     (25.5, 22.5), 0, {"1": "GATE", "2": "GND"}),
    ("TP2", "TestPoint:TestPoint_Pad_D1.5mm",
     (22.3, 25.5), 0, {"1": "GATE"}),
]
NETS = ["", "+12V", "GND", "STROBE", "DRAIN", "GATE"]
NETNO = {n: i for i, n in enumerate(NETS)}


def rot_xy(x, y, rot):
    r = math.radians(rot)
    return (x * math.cos(r) - y * math.sin(r),
            x * math.sin(r) + y * math.cos(r))


def load_fp(spec):
    libname, fpname = spec.split(":")
    path = os.path.join(FP_DIR, libname + ".pretty", fpname + ".kicad_mod")
    txt = open(path, encoding="utf-8").read()
    txt = txt.replace('(module ', '(footprint ', 1)
    return txt


def pad_pos(spec, pos, rot, pads_cache={}):
    if spec not in pads_cache:
        txt = load_fp(spec)
        pads = {}
        for m in re.finditer(
                r'\(pad\s+"?(\d+)"?\s+\S+\s+\S+\s*\(at\s+(-?[\d.]+)\s+'
                r'(-?[\d.]+)(?:\s+(-?[\d.]+))?\)', txt):
            pads[m.group(1)] = (float(m.group(2)), float(m.group(3)))
        pads_cache[spec] = pads
    out = {}
    for num, (ox, oy) in pads_cache[spec].items():
        rx, ry = rot_xy(ox, oy, -rot)
        out[num] = (pos[0] + rx, pos[1] + ry)
    return out


def fp_block(ref, spec, pos, rot, netmap):
    txt = load_fp(spec)
    pads = pad_pos(spec, pos, rot)
    head, rest = txt.split("\n", 1)
    lines = [head,
             '  (tstamp %s)' % U(),
             '  (at %s %s %d)' % (fmt(pos[0]), fmt(pos[1]), rot)]
    rest = re.sub(r'(\(fp_text reference )"?[^"\s\)]+"?',
                  r'\1"%s"' % ref, rest, count=1)
    rest = re.sub(r'(\(fp_text value )"?[^"\s\)]+"?',
                  r'\1"%s"' % VAL_OF[ref], rest, count=1)

    def pad_repl(m):
        num = m.group(1)
        seg = m.group(0)
        net = netmap.get(num)
        if net:
            seg = seg.rstrip()
            assert seg.endswith(")")
            seg = seg[:-1] + ' (net %d "%s"))' % (NETNO[net], net)
        return seg
    rest = re.sub(r'\(pad\s+"?(\d+)"?(?:[^()]|\([^()]*\))*\)', pad_repl,
                  rest)
    return "\n".join(lines) + "\n" + rest, pads


tracks = []


def T(net, w, pts):
    tracks.append((net, w, pts))


PPB = {}
blocks = []
for ref, spec, pos, rot, netmap in PCB_PARTS:
    blk, pads = fp_block(ref, spec, pos, rot, netmap)
    blocks.append(blk)
    PPB[ref] = pads

J1, J2, C1, C2 = PPB["J1"], PPB["J2"], PPB["C1"], PPB["C2"]
Q1, R1, R2, TP2 = PPB["Q1"], PPB["R1"], PPB["R2"], PPB["TP2"]


T("+12V", 1.0, [J1["1"], J2["1"]])
T("+12V", 0.8, [(21.5, 10), C1["1"]])
T("+12V", 0.8, [(15.55, 10), C2["1"]])

T("DRAIN", 1.0, [J2["2"], (36.25, 20), Q1["3"]])

T("GND", 0.6, [J1["2"], (6.2, 12.54)])
T("GND", 0.6, [C1["2"], (26.5, 11.2)])
T("GND", 0.6, [C2["2"], (17.45, 18.6)])
T("GND", 0.6, [Q1["2"], (28.6, 23.2)])
T("GND", 0.6, [R2["2"], (27.6, 22.5)])

T("STROBE", 0.4, [J1["3"], (3.5, 22), (19.7, 22), R1["1"]])

T("GATE", 0.4, [R1["2"], (27, 20.5), (27, 19.05), Q1["1"]])
T("GATE", 0.4, [(23.4, 20.5), (23.4, 22.5), R2["1"]])
T("GATE", 0.4, [(22.3, 20.5), TP2["1"]])

VIAS = [
    (6.2, 12.54, "GND"), (26.5, 11.2, "GND"), (17.45, 18.6, "GND"),
    (28.6, 23.2, "GND"), (27.6, 22.5, "GND"),
    (2, 3, "GND"), (38.5, 5.5, "GND"), (6, 28, "GND"),
]
SILK = [
    ("+12V", 9, 7.6, 0.9),
    ("STR", 3.5, 17.9, 0.9),
    ("RING", 33.0, 14.8, 0.9),
    ("IR RING STROBE DRIVER", 20, 28.2, 1.1),
]
HOLES = [(2.5, 27.5, -3.4), (37.5, 27.5, -3.4), (37.5, 2.5, 3.4)]

pcb = []
pcb.append("""(kicad_pcb (version 20221018) (generator pcbnew)
  (general (thickness 1.6) (legacy_teardrops no))
  (paper "A4")
  (title_block
    (title "IR LED ring strobe driver")
    (company "Tenmo project")
  )
  (layers
    (0 "F.Cu" signal)
    (31 "B.Cu" signal)
    (32 "B.Adhes" user "B.Adhesive")
    (33 "F.Adhes" user "F.Adhesive")
    (34 "B.Paste" user)
    (35 "F.Paste" user)
    (36 "B.SilkS" user)
    (37 "F.SilkS" user)
    (38 "B.Mask" user)
    (39 "F.Mask" user)
    (40 "Dwgs.User" user)
    (41 "Cmts.User" user)
    (44 "Edge.Cuts" user)
    (46 "B.CrtYd" user)
    (47 "F.CrtYd" user)
    (48 "B.Fab" user)
    (49 "F.Fab" user)
  )
  (setup
    (pad_to_mask_clearance 0)
    (pcbplotparams
      (layerselection 0x00010fc_ffffffff)
      (plot_on_all_layers_selection 0x0000000_00000000)
      (disableapertmacros false)
      (usegerberextensions false)
      (usegerberattributes true)
      (usegerberadvancedattributes true)
      (creategerberjobfile true)
      (dashed_line_dash_ratio 12.000000)
      (dashed_line_gap_ratio 3.000000)
      (svgprecision 6)
      (plotframeref false)
      (viasonmask false)
      (mode 1)
      (useauxorigin false)
      (hpglpennumber 1)
      (hpglpenspeed 20)
      (hpglpendiameter 15.000000)
      (pdf_front_fp_property_popups true)
      (pdf_back_fp_property_popups true)
      (pdf_metadata true)
      (pdf_pagetitle_as_basename true)
      (drc_exclusions_comment "")
      (outputdir "gerber")
    )
  )""")
for i, n in enumerate(NETS):
    if n:
        pcb.append('  (net %d "%s")' % (i, n))
for blk in blocks:
    pcb.append(blk)
for (x1, y1, x2, y2) in [(0, 0, 40, 0), (40, 0, 40, 30),
                         (40, 30, 0, 30), (0, 30, 0, 0)]:
    pcb.append("""  (gr_line (start %s %s) (end %s %s) (layer "Edge.Cuts") (width 0.1) (tstamp %s))"""
               % (fmt(x1), fmt(y1), fmt(x2), fmt(y2), U()))
for (tx, x, y, size) in SILK:
    pcb.append("""  (gr_text "%s" (at %s %s 0) (layer "F.SilkS") (tstamp %s)
    (effects (font (size %s %s) (thickness %s)))
  )""" % (tx, fmt(x), fmt(y), U(), fmt(size), fmt(size), fmt(size * 0.15)))
for (hx, hy, dy) in HOLES:


    txt = load_fp("MountingHole:MountingHole_2.2mm_M2")
    head, rest = txt.split("\n", 1)
    rest = re.sub(r'(\(fp_text reference )"?[^"\s\)]+"?',
                  r'\1"H"', rest, count=1)
    rest = re.sub(r'(\(fp_text reference "H" \(at )[^)]*(\))',
                  r'\g<1>0 %s\2' % fmt(dy), rest, count=1)
    rest = re.sub(r'(\(fp_text value "[^"]*" \(at )[^)]*(\))',
                  r'\g<1>0 %s\2' % fmt(dy), rest, count=1)
    pcb.append("\n".join([head,
                          '  (tstamp %s)' % U(),
                          '  (at %s %s)' % (fmt(hx), fmt(hy))])
               + "\n" + rest)
for (net, w, pts) in tracks:
    for a, b in zip(pts, pts[1:]):
        pcb.append("""  (segment (start %s %s) (end %s %s) (width %s) (layer "F.Cu") (net %d) (tstamp %s))"""
                   % (fmt(a[0]), fmt(a[1]), fmt(b[0]), fmt(b[1]), fmt(w),
                      NETNO[net], U()))
for (x, y, net) in VIAS:
    pcb.append("""  (via (at %s %s) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (free) (net %d) (tstamp %s))"""
               % (fmt(x), fmt(y), NETNO[net], U()))
for layer in ("F.Cu", "B.Cu"):
    pcb.append("""  (zone (net %d) (net_name "GND") (layer "%s") (tstamp %s) (hatch edge 0.5)
    (connect_pads (clearance 0.25))
    (min_thickness 0.25)
    (filled_areas_thickness no)
    (fill yes (thermal_gap 0.3) (thermal_bridge_width 0.4))
    (polygon (pts (xy 0.3 0.3) (xy 39.7 0.3) (xy 39.7 29.7) (xy 0.3 29.7)))
  )""" % (NETNO["GND"], layer, U()))
pcb.append(")")
with open(os.path.join(HERE, PROJ + ".kicad_pcb"), "w") as f:
    f.write("\n".join(pcb) + "\n")

with open(os.path.join(HERE, PROJ + ".kicad_pro"), "w") as f:
    f.write('{\n  "board": {},\n  "meta": {"filename": "%s.kicad_pro", '
            '"version": 1},\n  "schematic": {},\n  "text_variables": {}\n}\n'
            % PROJ)
with open(os.path.join(HERE, "sym-lib-table"), "w") as f:
    f.write('(sym_lib_table\n'
            '  (lib (name "Device")(type "KiCad")(uri '
            '"${KICAD7_SYMBOL_DIR}/Device.kicad_sym")(options "")'
            '(descr ""))\n'
            '  (lib (name "Connector_Generic")(type "KiCad")(uri '
            '"${KICAD7_SYMBOL_DIR}/Connector_Generic.kicad_sym")'
            '(options "")(descr ""))\n'
            '  (lib (name "Connector")(type "KiCad")(uri '
            '"${KICAD7_SYMBOL_DIR}/Connector.kicad_sym")(options "")'
            '(descr ""))\n)\n')
with open(os.path.join(HERE, "fp-lib-table"), "w") as f:
    f.write('(fp_lib_table\n')
    for libname in ("Connector_PinHeader_2.54mm", "Connector_JST",
                    "Capacitor_THT", "Capacitor_SMD", "Package_TO_SOT_SMD",
                    "Resistor_SMD", "TestPoint", "MountingHole"):
        f.write('  (lib (name "%s")(type "KiCad")(uri '
                '"${KICAD7_FOOTPRINT_DIR}/%s.pretty")(options "")'
                '(descr ""))\n' % (libname, libname))
    f.write(')\n')

with open(os.path.join(HERE, "netlist.txt"), "w") as f:
    f.write("Expected nets (design intent):\n")
    f.write("+12V : J1.1 C1.1 C2.1 J2.1\n")
    f.write("GND  : J1.2 C1.2 C2.2 Q1.2(S) R2.2\n")
    f.write("DRAIN: J2.2 Q1.3(D)\n")
    f.write("GATE : Q1.1(G) R1.2 R2.1 TP2.1\n")
    f.write("STROBE: J1.3 R1.1\n")
print("generated", PROJ)
