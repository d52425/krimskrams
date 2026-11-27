#!/usr/bin/env python3
"""Connectivity + clearance check for IR_ring_strobe.kicad_pcb.

Union-find over pads / tracks / vias with geometric touch tests, plus
GND zone-fill containment. Then a different-net clearance scan on F.Cu.
Run under xvfb (pcbnew needs wx):  xvfb-run -a python3 check_conn.py
"""
import math
import sys
import wx

app = wx.App()
import pcbnew

MM = 1e6
b = pcbnew.LoadBoard("IR_ring_strobe.kicad_pcb")

parent = {}


def find(x):
    parent.setdefault(x, x)
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


def union(a, c):
    ra, rc = find(a), find(c)
    if ra != rc:
        parent[ra] = rc


def mm(v):
    return v / MM


pads = []
for fp in b.GetFootprints():
    ref = fp.GetReference()
    for p in fp.Pads():
        net = p.GetNetname()
        if not net:
            continue
        pos = p.GetPosition()
        size = p.GetSize()
        pads.append(("%s.%s" % (ref, p.GetNumber()), net,
                     mm(pos.x), mm(pos.y),
                     min(mm(size.x), mm(size.y)) / 2.0,
                     p.GetDrillSize().x > 0))

tracks = []
vias = []
for t in b.GetTracks():
    net = t.GetNetname()
    if isinstance(t, pcbnew.PCB_VIA):
        pos = t.GetPosition()
        vias.append((net, mm(pos.x), mm(pos.y), mm(t.GetWidth()) / 2.0))
    else:
        s, e = t.GetStart(), t.GetEnd()
        tracks.append((net, mm(s.x), mm(s.y), mm(e.x), mm(e.y),
                       mm(t.GetWidth()) / 2.0))


def d_pt_seg(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    if L2 == 0:
        return math.hypot(px - x1, py - y1)
    tt = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / L2))
    return math.hypot(px - (x1 + tt * dx), py - (y1 + tt * dy))


def d_seg_seg(a, c):
    (x1, y1, x2, y2), (x3, y3, x4, y4) = a, c
    def orient(px, py, qx, qy, rx, ry):
        return (qx - px) * (ry - py) - (qy - py) * (rx - px)
    d1 = orient(x3, y3, x4, y4, x1, y1)
    d2 = orient(x3, y3, x4, y4, x2, y2)
    d3 = orient(x1, y1, x2, y2, x3, y3)
    d4 = orient(x1, y1, x2, y2, x4, y4)
    if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)):
        return 0.0
    return min(d_pt_seg(x1, y1, x3, y3, x4, y4),
               d_pt_seg(x2, y2, x3, y3, x4, y4),
               d_pt_seg(x3, y3, x1, y1, x2, y2),
               d_pt_seg(x4, y4, x1, y1, x2, y2))


for i, (pid, net, x, y, r, thru) in enumerate(pads):
    find("P%d" % i)
    if thru:
        pass
for i in range(len(tracks)):
    find("T%d" % i)
for i in range(len(vias)):
    find("V%d" % i)
find("ZF")
find("ZB")

EPS = 0.02
for i, (pid, net, x, y, r, thru) in enumerate(pads):
    for j, (n2, x1, y1, x2, y2, w) in enumerate(tracks):
        if n2 == net and d_pt_seg(x, y, x1, y1, x2, y2) <= r + w + EPS:
            union("P%d" % i, "T%d" % j)
    for j, (n2, vx, vy, vr) in enumerate(vias):
        if n2 == net and math.hypot(x - vx, y - vy) <= r + vr + EPS:
            union("P%d" % i, "V%d" % j)
for i, (n1, x1, y1, x2, y2, w1) in enumerate(tracks):
    for j, (n2, vx, vy, vr) in enumerate(vias):
        if n1 == n2 and d_pt_seg(vx, vy, x1, y1, x2, y2) <= w1 + vr + EPS:
            union("T%d" % i, "V%d" % j)
    for j in range(i + 1, len(tracks)):
        n2, a1, b1, a2, b2, w2 = tracks[j]
        if n1 == n2 and d_seg_seg((x1, y1, x2, y2), (a1, b1, a2, b2)) \
                <= w1 + w2 + EPS:
            union("T%d" % i, "T%d" % j)


def zone_polys(layer):
    polys = []
    for z in b.Zones():
        if z.GetNetname() != "GND":
            continue
        if z.GetFirstLayer() != layer:
            continue
        filled = z.GetFilledPolysList(z.GetFirstLayer())
        for oi in range(filled.OutlineCount()):
            chain = filled.Outline(oi)
            pts = []
            for pi in range(chain.PointCount()):
                p = chain.CPoint(pi)
                pts.append((mm(p.x), mm(p.y)))
            polys.append(pts)
    return polys


def in_poly(px, py, pts):
    inside = False
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        if (y1 > py) != (y2 > py):
            xin = x1 + (py - y1) * (x2 - x1) / (y2 - y1)
            if px < xin:
                inside = not inside
    return inside


print("stage: track/via unions done", flush=True)
for layer, zn in ((pcbnew.F_Cu, "ZF"), (pcbnew.B_Cu, "ZB")):
    polys = zone_polys(layer)
    if not polys:
        print("WARN: no filled polys on layer", layer)
        continue
    for i, (pid, net, x, y, r, thru) in enumerate(pads):
        if net == "GND" and (layer == pcbnew.B_Cu or not thru):
            if any(in_poly(x, y, p) for p in polys):
                union("P%d" % i, zn)
        if net == "GND" and thru and layer == pcbnew.F_Cu:
            if any(in_poly(x, y, p) for p in polys):
                union("P%d" % i, zn)
    for j, (net, vx, vy, vr) in enumerate(vias):
        if net == "GND" and any(in_poly(vx, vy, p) for p in polys):
            union("V%d" % j, zn)
    for j, (net, x1, y1, x2, y2, w) in enumerate(tracks):
        if net == "GND" and layer == pcbnew.F_Cu:
            if any(in_poly(x1, y1, p) or in_poly(x2, y2, p) for p in polys):
                union("T%d" % j, zn)


for j, (net, vx, vy, vr) in enumerate(vias):
    if net == "GND":
        union("V%d" % j, "ZF")
        union("V%d" % j, "ZB")

print("stage: unions done", flush=True)
clusters = {}
for i, (pid, net, x, y, r, thru) in enumerate(pads):
    clusters.setdefault(net, {}).setdefault(find("P%d" % i), []).append(pid)
ok = True
for net in sorted(clusters):
    groups = clusters[net]
    print(net, "clusters:", len(groups))
    for g, members in groups.items():
        print("   -", ", ".join(sorted(members)))
    if len(groups) > 1:
        ok = False
print("CONNECTIVITY:", "OK" if ok else "SPLIT NETS FOUND")

print("stage: zones done", flush=True)

items = []
for (pid, net, x, y, r, thru) in pads:
    items.append((net, "pad", (x, y, r), pid))
for (net, x1, y1, x2, y2, w) in tracks:
    items.append((net, "seg", (x1, y1, x2, y2, w), "track"))
for (net, x, y, r) in vias:
    items.append((net, "pad", (x, y, r), "via"))
worst = []
for i in range(len(items)):
    for j in range(i + 1, len(items)):
        n1, k1, g1, id1 = items[i]
        n2, k2, g2, id2 = items[j]
        if n1 == n2:
            continue
        if k1 == "pad" and k2 == "pad":
            d = math.hypot(g1[0] - g2[0], g1[1] - g2[1]) - g1[2] - g2[2]
        elif k1 == "seg" and k2 == "seg":
            d = d_seg_seg(g1[:4], g2[:4]) - g1[4] - g2[4]
        else:
            if k1 == "seg":
                g1, g2, id1, id2 = g2, g1, id2, id1
            d = d_pt_seg(g1[0], g1[1], g2[0], g2[1], g2[2], g2[3]) \
                - g1[2] - g2[4]
        if d < 0.15:
            worst.append((round(d, 3), n1, id1, n2, id2))
worst.sort()
print("CLEARANCE <0.15mm pairs:", len(worst))
for w in worst[:20]:
    print("   ", w)
sys.exit(0 if ok else 1)
