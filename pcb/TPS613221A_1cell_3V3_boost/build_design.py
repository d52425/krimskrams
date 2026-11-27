#!/usr/bin/env python3
"""Generate KiCad project: single-cell (1x AA/AAA) -> 3.3V boost, TPS613221A.
Board 30x20mm, 2-layer. Run: python3 build_design.py
Outputs .kicad_sch / .kicad_pcb / .kicad_pro next to this script.
"""
import os, re, sys, uuid, json

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = "TPS613221A_1cell_3V3"
KICAD_SHARE = os.environ.get("KICAD_SHARE", "/usr/share/kicad")
SYMDIR = os.path.join(KICAD_SHARE, "symbols")
FPDIR = os.path.join(KICAD_SHARE, "footprints")

def U():
    return str(uuid.uuid4())

def extract_symbol(libfile, name):
    """Return the (symbol "name" ...) block text from a .kicad_sym file.

    KiCad 10 split libraries (<Lib>.kicad_symdir/<Symbol>.kicad_sym, one
    file per root symbol, subunits inside) are resolved as well.
    """
    p = os.path.join(SYMDIR, libfile)
    if os.path.exists(p):
        txt = open(p).read()
    else:
        base = libfile[:-len(".kicad_sym")] if libfile.endswith(".kicad_sym") else libfile
        root = re.sub(r"_\d+_\d+$", "", name)
        txt = open(os.path.join(SYMDIR, base + ".kicad_symdir", root + ".kicad_sym")).read()
    start = txt.index('(symbol "%s"' % name)
    depth = 0
    for i in range(start, len(txt)):
        c = txt[i]
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
            if depth == 0:
                return txt[start:i + 1]
    raise ValueError(name)

def symbol_pins(libfile, name):
    """Parse pins of subunit _1_1: {number: (x, y)} in symbol coords (y up)."""
    block = extract_symbol(libfile, name + "_1_1")
    pins = {}
    for m in re.finditer(r'\(pin\s+\S+\s+\S+\s*\(at\s+(-?[\d.]+)\s+(-?[\d.]+)\s+\d+\).*?\(number\s+"(\d+)"', block, re.S):
        pins[m.group(3)] = (float(m.group(1)), float(m.group(2)))
    return pins

def pin_file_pos(pins, num, pos, rot=0, mirror=False):
    """Absolute file coords (y down) of a pin for an instance at pos."""
    px, py = pins[num]
    ox, oy = px, -py
    if rot == 90:
        ox, oy = oy, -ox
    elif rot == 180:
        ox, oy = -ox, -oy
    elif rot == 270:
        ox, oy = -oy, ox
    if mirror:
        ox = -ox
    return (round(pos[0] + ox, 2), round(pos[1] + oy, 2))

def place_by_pin(pins, num, target, rot=0):
    """Instance pos so that pin `num` lands on target."""
    px, py = pins[num]
    ox, oy = px, -py
    if rot == 90:
        ox, oy = oy, -ox
    elif rot == 180:
        ox, oy = -ox, -oy
    elif rot == 270:
        ox, oy = -oy, ox
    return (round(target[0] - ox, 2), round(target[1] - oy, 2))


SYMS = [

    ("Regulator_Switching.kicad_sym", "TPS613221ADBV"),
    ("Device.kicad_sym", "L"),
    ("Device.kicad_sym", "C"),
    ("Connector_Generic.kicad_sym", "Conn_01x03"),
    ("Jumper.kicad_sym", "SolderJumper_2_Open"),
    ("Connector.kicad_sym", "TestPoint"),
]
LIBID = {
    "TPS613221ADBV": "Regulator_Switching:TPS613221ADBV",
    "L": "Device:L",
    "C": "Device:C",
    "Conn_01x03": "Connector_Generic:Conn_01x03",
    "SolderJumper_2_Open": "Jumper:SolderJumper_2_Open",
    "TestPoint": "Connector:TestPoint",
}
PINS = {}
lib_blocks = []
for libfile, name in SYMS:
    nick = LIBID[name].split(":")[0]
    block = extract_symbol(libfile, name)


    block = block.replace('(symbol "%s"' % name, '(symbol "%s:%s"' % (nick, name), 1)
    lib_blocks.append(block)
    PINS[name] = symbol_pins(libfile, name)


ROW = 60.0
plan = {}
plan["J1"] = ("Conn_01x03", "BAT/GND/+3V3", "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical", "1", (33.08, ROW), 0)
plan["SJ1"] = ("SolderJumper_2_Open", "SJ_BRIDGE=ON", "Jumper:SolderJumper-2_P1.3mm_Open_Pad1.0x1.5mm", "1", (40.0, ROW), 0)
plan["L1"] = ("L", "4.7uH", "Inductor_SMD:L_1008_2520Metric", "1", (56.0, ROW), 90)
plan["U1"] = ("TPS613221ADBV", "TPS613221ADBVT", "Package_TO_SOT_SMD:SOT-23-5", "1", (89.84, ROW), 0)
plan["C1"] = ("C", "22uF", "Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder", "1", (51.5, 74.0), 0)
plan["C2"] = ("C", "22uF", "Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder", "1", (120.0, 74.0), 0)
plan["C3"] = ("C", "1uF", "Capacitor_SMD:C_0603_1608Metric_Pad1.08x0.95mm_HandSolder", "1", (132.0, 74.0), 0)
plan["TP1"] = ("TestPoint", "TP_BAT", "TestPoint:TestPoint_Pad_D1.5mm", "1", (49.0, 80.0), 0)
plan["TP2"] = ("TestPoint", "TP_SW", "TestPoint:TestPoint_Pad_D1.5mm", "1", (76.0, 80.0), 0)
plan["TP3"] = ("TestPoint", "TP_3V3", "TestPoint:TestPoint_Pad_D1.5mm", "1", (138.0, 80.0), 0)

POS = {}
PINPOS = {}
for ref, (sym, val, fp, anch, target, rot) in plan.items():
    pos = place_by_pin(PINS[sym], anch, target, rot)
    POS[ref] = (pos, rot)
    for num in PINS[sym]:
        PINPOS[(ref, num)] = pin_file_pos(PINS[sym], num, pos, rot)

wires = []
junctions = []
labels = []
noconnects = []

def wire(a, b):
    wires.append((a[0], a[1], b[0], b[1]))

def stub_label(a, b, text):
    wire(a, b)
    junctions.append(a)
    labels.append((text, b[0], b[1]))


wire(PINPOS[("J1", "1")], PINPOS[("SJ1", "1")])
wire(PINPOS[("SJ1", "2")], PINPOS[("L1", "1")])

wire((51.5, ROW), PINPOS[("C1", "1")]); junctions.append((51.5, ROW))
wire(PINPOS[("C1", "2")], (51.5, 88.0)); labels.append(("GND", 51.5, 88.0))

wire((49.0, ROW), PINPOS[("TP1", "1")]); junctions.append((49.0, ROW))

stub_label((54.5, ROW), (54.5, 55.0), "BAT")

wire(PINPOS[("L1", "2")], PINPOS[("U1", "1")])
wire((76.0, ROW), PINPOS[("TP2", "1")]); junctions.append((76.0, ROW))
stub_label((82.0, ROW), (82.0, 55.0), "SW")

wire(PINPOS[("U1", "2")], (100.0, 78.0)); labels.append(("GND", 100.0, 78.0))

noconnects.append(PINPOS[("U1", "3")])
noconnects.append(PINPOS[("U1", "5")])

vout_end = (146.0, ROW)
wire(PINPOS[("U1", "4")], vout_end)

wire((120.0, ROW), PINPOS[("C2", "1")]); junctions.append((120.0, ROW))
wire(PINPOS[("C2", "2")], (120.0, 88.0)); labels.append(("GND", 120.0, 88.0))
wire((132.0, ROW), PINPOS[("C3", "1")]); junctions.append((132.0, ROW))
wire(PINPOS[("C3", "2")], (132.0, 88.0)); labels.append(("GND", 132.0, 88.0))

wire((138.0, ROW), PINPOS[("TP3", "1")]); junctions.append((138.0, ROW))

wire(vout_end, (152.0, ROW)); labels.append(("+3V3", 152.0, ROW))

wire(vout_end, (146.0, 100.0))
wire((146.0, 100.0), (33.08, 100.0))
wire((33.08, 100.0), PINPOS[("J1", "3")])

wire(PINPOS[("J1", "2")], (42.0, PINPOS[("J1", "2")][1])); labels.append(("GND", 42.0, PINPOS[("J1", "2")][1]))


def _on_segment(p, a, b):
    (px, py), (ax, ay), (bx, by) = p, a, b
    cross = (bx - ax) * (py - ay) - (by - ay) * (px - ax)
    if abs(cross) > 0.01:
        return False
    dot = (px - ax) * (px - bx) + (py - ay) * (py - by)
    return dot < -0.001

split_wires = []
for (x1, y1, x2, y2) in wires:
    cuts = [(jx, jy) for (jx, jy) in junctions if _on_segment((jx, jy), (x1, y1), (x2, y2))]
    cuts.sort(key=lambda p: (p[0] - x1) ** 2 + (p[1] - y1) ** 2)
    pts = [(x1, y1)] + cuts + [(x2, y2)]
    for a, b in zip(pts, pts[1:]):
        split_wires.append((a[0], a[1], b[0], b[1]))
wires = split_wires

sheet_uuid = U()
sch = []
sch.append('(kicad_sch (version 20230121) (generator eeschema)')
sch.append('  (uuid %s)' % sheet_uuid)
sch.append('  (paper "A5")')
sch.append('  (title_block (title "Single-cell 1.5V -> 3.3V boost (TPS613221A)") (date "2026-11-26") (rev "A"))')
sch.append('  (lib_symbols')
for b in lib_blocks:
    sch.append('    ' + b.replace('\n', '\n    '))
sch.append('  )')
for ref, (sym, val, fp, anch, target, rot) in plan.items():
    pos, r = POS[ref]
    sch.append('  (symbol (lib_id "%s") (at %.2f %.2f %d) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid %s)' % (LIBID[sym], pos[0], pos[1], r, U()))
    sch.append('    (property "Reference" "%s" (at %.2f %.2f 0) (effects (font (size 1.27 1.27))))' % (ref, pos[0], pos[1] - 2.54))
    sch.append('    (property "Value" "%s" (at %.2f %.2f 0) (effects (font (size 1.27 1.27))))' % (val, pos[0], pos[1] + 2.54))
    sch.append('    (property "Footprint" "%s" (at %.2f %.2f 0) (effects (font (size 1.27 1.27)) hide))' % (fp, pos[0], pos[1]))
    sch.append('    (property "Datasheet" "" (at %.2f %.2f 0) (effects (font (size 1.27 1.27)) hide))' % (pos[0], pos[1]))
    for num in sorted(PINS[sym]):
        sch.append('    (pin "%s" (uuid %s))' % (num, U()))
    sch.append('    (instances (project "%s" (path "/%s" (reference "%s") (unit 1))))' % (PROJ, sheet_uuid, ref))
    sch.append('  )')
for (x1, y1, x2, y2) in wires:
    sch.append('  (wire (pts (xy %.2f %.2f) (xy %.2f %.2f)) (stroke (width 0) (type default)) (uuid %s))' % (x1, y1, x2, y2, U()))
for (x, y) in junctions:
    sch.append('  (junction (at %.2f %.2f) (diameter 0) (color 0 0 0 0) (uuid %s))' % (x, y, U()))
for (text, x, y) in labels:
    sch.append('  (global_label "%s" (shape input) (at %.2f %.2f 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid %s))' % (text, x, y, U()))
for (x, y) in noconnects:
    sch.append('  (no_connect (at %.2f %.2f) (uuid %s))' % (x, y, U()))
sch.append('  (sheet_instances (path "/" (page "1")))')
sch.append(')')
open(os.path.join(HERE, PROJ + ".kicad_sch"), "w").write("\n".join(sch) + "\n")
print("schematic written")


import pcbnew
MM = pcbnew.FromMM

board = pcbnew.BOARD()
nets = {}
for name in ("BAT", "GND", "SW", "+3V3"):
    ni = pcbnew.NETINFO_ITEM(board, name)
    board.Add(ni)
    nets[name] = ni.GetNetCode()

def load_fp(lib, name):
    return pcbnew.FootprintLoad(os.path.join(FPDIR, lib + ".pretty"), name)

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

def pad_pos(fp, num):
    for pad in fp.Pads():
        if pad.GetNumber() == num:
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

Y = 6.35
j1 = add_fp("Connector_PinHeader_2.54mm", "PinHeader_1x03_P2.54mm_Vertical", "J1", "BAT/GND/+3V3",
            (4.5, Y), 0, {"1": "BAT", "2": "GND", "3": "+3V3"})
sj1 = add_fp("Jumper", "SolderJumper-2_P1.3mm_Open_Pad1.0x1.5mm", "SJ1", "BRIDGE=ON",
             (8.05, Y), 0, {"1": "BAT", "2": "BAT"})
c1 = add_fp("Capacitor_SMD", "C_0805_2012Metric_Pad1.18x1.45mm_HandSolder", "C1", "22uF",
            (9.5, 9.5), 0, {"1": "BAT", "2": "GND"})

c1.Reference().SetPosition(pcbnew.VECTOR2I(MM(9.5), MM(12.3)))
l1 = add_fp("Inductor_SMD", "L_1008_2520Metric", "L1", "4.7uH DFE252012P-4R7M",
            (11.8, Y), 0, {"1": "BAT", "2": "SW"})

l1.Reference().SetPosition(pcbnew.VECTOR2I(MM(13.6), MM(4.3)))
u1 = add_fp("Package_TO_SOT_SMD", "SOT-23-5", "U1", "TPS613221ADBVT",
            (16.2, Y), 0, {"1": "SW", "2": "GND", "4": "+3V3"})


for pad in u1.Pads():
    if pad.GetNumber() == "2":
        pad.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)
c2 = add_fp("Capacitor_SMD", "C_0805_2012Metric_Pad1.18x1.45mm_HandSolder", "C2", "22uF",
            (20.6, 8.6), 0, {"1": "+3V3", "2": "GND"})
c3 = add_fp("Capacitor_SMD", "C_0603_1608Metric_Pad1.08x0.95mm_HandSolder", "C3", "1uF",
            (19.4, 11.5), 0, {"1": "+3V3", "2": "GND"})
tp1 = add_fp("TestPoint", "TestPoint_Pad_D1.5mm", "TP1", "BAT", (9.9, 2.2), 0, {"1": "BAT"})


tp1.Reference().SetPosition(pcbnew.VECTOR2I(MM(10.6), MM(4.3)))
tp2 = add_fp("TestPoint", "TestPoint_Pad_D1.5mm", "TP2", "SW", (13.6, 10.2), 0, {"1": "SW"})
tp3 = add_fp("TestPoint", "TestPoint_Pad_D1.5mm", "TP3", "+3V3", (24.5, 12.5), 0, {"1": "+3V3"})
for i, (hx, hy) in enumerate([(28.2, 2.0), (28.2, 18.0), (1.8, 18.0)]):
    add_fp("MountingHole", "MountingHole_2.2mm_M2", "H%d" % (i + 1), "", (hx, hy), 0)


track(pad_pos(j1, "1"), pad_pos(sj1, "1"), 0.8, "BAT")
track(pad_pos(sj1, "2"), pad_pos(l1, "1"), 0.8, "BAT")
c1p1 = pad_pos(c1, "1")
track((c1p1[0], Y), c1p1, 0.8, "BAT")
tp1p = pad_pos(tp1, "1")
track((tp1p[0], Y), tp1p, 0.5, "BAT")

c1p2 = pad_pos(c1, "2")
track(c1p2, (c1p2[0], 11.3), 0.6, "GND"); via((c1p2[0], 11.3), "GND")
track(pad_pos(u1, "2"), (14.35, Y), 0.6, "GND"); via((14.35, Y), "GND")
track(pad_pos(j1, "2"), (6.4, pad_pos(j1, "2")[1]), 0.6, "GND"); via((6.4, pad_pos(j1, "2")[1]), "GND")
c2p2 = pad_pos(c2, "2")
track(c2p2, (c2p2[0], 10.6), 0.6, "GND"); via((c2p2[0], 10.6), "GND")
c3p2 = pad_pos(c3, "2")
track(c3p2, (21.6, 11.5), 0.6, "GND"); via((21.6, 11.5), "GND")
via((28.0, 4.0), "GND"); via((28.0, 16.0), "GND"); via((4.0, 17.5), "GND")


l1p2 = pad_pos(l1, "2")
u1p1 = pad_pos(u1, "1")
track(l1p2, (l1p2[0], u1p1[1]), 0.5, "SW")
track((l1p2[0], u1p1[1]), u1p1, 0.5, "SW")
tp2p = pad_pos(tp2, "1")
track((13.2, u1p1[1]), (13.2, tp2p[1]), 0.5, "SW")
track((13.2, tp2p[1]), tp2p, 0.5, "SW")

u1p4 = pad_pos(u1, "4")
track(u1p4, (18.6, u1p4[1]), 0.8, "+3V3")
track((18.6, u1p4[1]), (18.6, 8.6), 0.8, "+3V3")
track((18.6, 8.6), pad_pos(c2, "1"), 0.8, "+3V3")
track((18.6, 8.6), pad_pos(c3, "1"), 0.8, "+3V3")


c2p1 = pad_pos(c2, "1")
track(c2p1, (c2p1[0], 5.6), 0.8, "+3V3")
track((c2p1[0], 5.6), (24.5, 5.6), 0.8, "+3V3")
track((24.5, 5.6), (24.5, 15.8), 0.8, "+3V3")
track((24.5, 15.8), (4.5, 15.8), 0.8, "+3V3")
track((4.5, 15.8), pad_pos(j1, "3"), 0.8, "+3V3")


for a, b in [((0, 0), (30, 0)), ((30, 0), (30, 20)), ((30, 20), (0, 20)), ((0, 20), (0, 0))]:
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1])))
    s.SetEnd(pcbnew.VECTOR2I(MM(b[0]), MM(b[1])))
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetWidth(MM(0.1))
    board.Add(s)


for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNetCode(nets["GND"])
    z.SetLocalClearance(MM(0.4))
    z.SetMinThickness(MM(0.25))
    chain = pcbnew.SHAPE_LINE_CHAIN()
    for (cx, cy) in [(0.3, 0.3), (29.7, 0.3), (29.7, 19.7), (0.3, 19.7)]:
        chain.Append(MM(cx), MM(cy))
    chain.SetClosed(True)
    z.Outline().AddOutline(chain)
    board.Add(z)


def silk(text, pos, size=1.1):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(text)
    t.SetPosition(pcbnew.VECTOR2I(MM(pos[0]), MM(pos[1])))
    t.SetLayer(pcbnew.F_SilkS)
    t.SetTextSize(pcbnew.VECTOR2I(MM(size), MM(size)))
    t.SetTextThickness(MM(0.18))
    board.Add(t)

silk("1CELL->3V3 TPS613221A", (15.0, 17.8), 1.2)
silk("BAT", (1.7, Y), 0.9)
silk("GND", (1.7, Y + 2.54), 0.9)
silk("3V3", (1.7, Y + 5.08), 0.9)

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


sym_libs = ["Regulator_Switching", "Device", "Connector_Generic", "Jumper", "Connector"]
fp_libs = ["Package_TO_SOT_SMD", "Inductor_SMD", "Capacitor_SMD",
           "Connector_PinHeader_2.54mm", "Jumper", "TestPoint", "MountingHole"]
with open(os.path.join(HERE, "sym-lib-table"), "w") as f:
    f.write("(sym_lib_table\n  (version 7)\n")
    for n in sym_libs:
        f.write('  (lib (name "%s") (type "KiCad") (uri "${KICAD10_SYMBOL_DIR}/%s.kicad_sym") (options "") (descr ""))\n' % (n, n))
    f.write(")\n")
with open(os.path.join(HERE, "fp-lib-table"), "w") as f:
    f.write("(fp_lib_table\n  (version 7)\n")
    for n in fp_libs:
        f.write('  (lib (name "%s") (type "KiCad") (uri "${KICAD10_FOOTPRINT_DIR}/%s.pretty") (options "") (descr ""))\n' % (n, n))
    f.write(")\n")
print("project written")
