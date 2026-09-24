#!/usr/bin/env python3
"""
A3 general-arrangement drawing for the SRA-16 Silent AC Rack, generated from
the same rack_layout.py solids (OpenCascade hidden-line removal + true
sections), so the drawing always matches the CAD.

Output: drawings/CP-SRA16-GA-001.svg (A3 landscape, 1:15)
"""
import datetime
import math
import os
import sys

import cadquery as cq
from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt
from OCP.HLRAlgo import HLRAlgo_Projector
from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "cad", "fusion", "SilentRackAC"))
sys.path.insert(0, HERE)
import rack_layout as RL  # noqa: E402
from build_cadquery import make_part  # noqa: E402

SCALE = 15.0          # 1:15 on A3
DOC_NO = "CP-SRA16-GA-001"
REV = "A"


# ------------------------------------------------------------------ geometry
def edge_polys(shape, u_axis, v_axis, n_curve=24):
    """Edges of a 2-D result -> list of polylines in (u, v)."""
    out = []
    if shape is None:
        return out
    for e in shape.Edges():
        if e.geomType() == "LINE":
            pts = [e.startPoint(), e.endPoint()]
        else:
            pts = e.positions([i / n_curve for i in range(n_curve + 1)])
        out.append([(p.dot(u_axis), p.dot(v_axis)) for p in pts])
    return out


def hlr(shape, n_dir, x_dir):
    """Visible sharp + outline edges of `shape` projected along n_dir."""
    algo = HLRBRep_Algo()
    algo.Add(shape.wrapped)
    algo.Projector(HLRAlgo_Projector(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(*n_dir), gp_Dir(*x_dir))))
    algo.Update()
    algo.Hide()
    hs = HLRBRep_HLRToShape(algo)
    polys = []
    for comp in (hs.VCompound(), hs.OutLineVCompound()):
        if comp is not None and not comp.IsNull():
            polys += edge_polys(cq.Shape.cast(comp), cq.Vector(1, 0, 0), cq.Vector(0, 1, 0))
    return polys


def section_faces(solids, axis, pos, u_axis, v_axis):
    """True cross-sections: list of (part, [outer, holes...]) in (u, v)."""
    big = 5000.0
    n = {"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}[axis]
    base = {"x": (pos, 550, 950), "y": (325, pos, 950), "z": (325, 550, pos)}[axis]
    plane = cq.Face.makePlane(big, big, basePnt=cq.Vector(*base), dir=cq.Vector(*n))
    out = []
    for part, sol in solids:
        bb = sol.BoundingBox()
        lo = {"x": bb.xmin, "y": bb.ymin, "z": bb.zmin}[axis]
        hi = {"x": bb.xmax, "y": bb.ymax, "z": bb.zmax}[axis]
        if not (lo < pos < hi):
            continue
        sec = sol.intersect(plane)
        for f in sec.Faces():
            loops = []
            for w in [f.outerWire()] + f.innerWires():
                segs = []
                for e in w.Edges():
                    ps = [e.startPoint(), e.endPoint()] if e.geomType() == "LINE" else \
                        e.positions([i / 24 for i in range(25)])
                    segs.append([(p.dot(u_axis), p.dot(v_axis)) for p in ps])
                loops.append(chain(segs))
            out.append((part, loops))
    return out


def chain(segs, tol=0.05):
    """Order edge polylines head-to-tail into one closed loop."""
    if not segs:
        return []
    rem = [list(s) for s in segs]
    loop = rem.pop(0)
    d = lambda a, b: math.hypot(a[0] - b[0], a[1] - b[1])
    while rem:
        end = loop[-1]
        i = min(range(len(rem)), key=lambda k: min(d(rem[k][0], end), d(rem[k][-1], end)))
        seg = rem.pop(i)
        if d(seg[-1], end) < d(seg[0], end):
            seg = seg[::-1]
        loop += seg[1:]
    return loop


def clip_solids(solids, axis, lo, hi):
    """Keep the portion of every solid with lo <= coord <= hi (for 'beyond' views)."""
    B = 6000.0
    rng = {"x": ((lo, -B, -B), (hi, B, B)), "y": ((-B, lo, -B), (B, hi, B)), "z": ((-B, -B, lo), (B, B, hi))}[axis]
    (x0, y0, z0), (x1, y1, z1) = rng
    box = cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, pnt=cq.Vector(x0, y0, z0))
    keep = []
    for part, s in solids:
        bb = s.BoundingBox()
        c0 = {"x": bb.xmin, "y": bb.ymin, "z": bb.zmin}[axis]
        c1 = {"x": bb.xmax, "y": bb.ymax, "z": bb.zmax}[axis]
        if c1 <= lo or c0 >= hi:
            continue
        if c0 >= lo and c1 <= hi:
            keep.append(s)
        else:
            r = s.intersect(box)
            if r.Volume() > 1.0:
                keep.append(r)
    return cq.Compound.makeCompound(keep)


# ------------------------------------------------------------------ SVG helpers
class Sheet:
    def __init__(self):
        self.el = []

    def add(self, s):
        self.el.append(s)

    def line(self, x1, y1, x2, y2, w=0.25, c="#111", dash=None, extra=""):
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        self.add('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width="%.2f"%s %s/>'
                 % (x1, y1, x2, y2, c, w, d, extra))

    def text(self, x, y, s, size=2.5, anchor="start", weight="normal", c="#111", rot=None):
        tr = ' transform="rotate(%.1f %.2f %.2f)"' % (rot, x, y) if rot is not None else ""
        s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        self.add('<text x="%.2f" y="%.2f" font-size="%.2f" text-anchor="%s" font-weight="%s" fill="%s"%s>%s</text>'
                 % (x, y, size, anchor, weight, c, tr, s))

    def rect(self, x, y, w, h, sw=0.35, fill="none", c="#111"):
        self.add('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="%s" stroke="%s" stroke-width="%.2f"/>'
                 % (x, y, w, h, fill, c, sw))

    def poly(self, pts, w=0.18, c="#222", fill="none", close=False, dash=None, marker=None):
        d = "M" + " L".join("%.2f %.2f" % p for p in pts) + (" Z" if close else "")
        extra = ' stroke-dasharray="%s"' % dash if dash else ""
        if marker:
            extra += ' marker-end="url(#%s)"' % marker
        self.add('<path d="%s" fill="%s" stroke="%s" stroke-width="%.2f" stroke-linejoin="round" '
                 'stroke-linecap="round"%s/>' % (d, fill, c, w, extra))

    def svg(self):
        head = ('<svg xmlns="http://www.w3.org/2000/svg" width="420mm" height="297mm" viewBox="0 0 420 297" '
                'font-family="Arial, Helvetica, sans-serif">\n<defs>\n')
        for name, col in (("aCold", "#1f6fe0"), ("aHot", "#d9481f"), ("aRoom", "#23913f"), ("aExh", "#d99a00"),
                          ("aDim", "#111")):
            if name == "aDim":
                head += ('<marker id="%s" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="3.2" markerHeight="3.2" '
                         'orient="auto-start-reverse"><path d="M0 1.5 L10 5 L0 8.5 z" fill="%s"/></marker>\n' % (name, col))
            else:
                head += ('<marker id="%s" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="4" markerHeight="4" '
                         'orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>\n' % (name, col))
        head += '</defs>\n<rect x="0" y="0" width="420" height="297" fill="#ffffff"/>\n'
        return head + "\n".join(self.el) + "\n</svg>\n"


class View:
    """Model (u, v) mm -> paper mm, origin at paper point (ox, oy) for model (u0, v0)."""

    def __init__(self, sheet, ox, oy, u0=0.0, v0=0.0, flip_u=False):
        self.s, self.ox, self.oy, self.u0, self.v0, self.fu = sheet, ox, oy, u0, v0, flip_u

    def p(self, u, v):
        du = (u - self.u0) / SCALE
        return (self.ox - du if self.fu else self.ox + du, self.oy - (v - self.v0) / SCALE)

    def polys(self, polys, w=0.13, c="#333"):
        for pl in polys:
            self.s.poly([self.p(*q) for q in pl], w=w, c=c)

    def dim_h(self, u1, u2, v, off, text=None, above=False):
        (x1, y1), (x2, y2) = self.p(u1, v), self.p(u2, v)
        y = y1 + (-off if above else off)
        self.s.line(x1, y1 + (-0.8 if above else 0.8), x1, y + (-1.2 if above else 1.2), w=0.13)
        self.s.line(x2, y2 + (-0.8 if above else 0.8), x2, y + (-1.2 if above else 1.2), w=0.13)
        self.s.add('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="#111" stroke-width="0.18" '
                   'marker-start="url(#aDim)" marker-end="url(#aDim)"/>' % (x1, y, x2, y))
        self.s.text((x1 + x2) / 2, y - 0.8, text or "%g" % round(abs(u2 - u1), 1), size=2.2, anchor="middle")

    def dim_v(self, u, v1, v2, off, text=None, left=True):
        (x1, y1), (x2, y2) = self.p(u, v1), self.p(u, v2)
        x = x1 + (-off if left else off)
        self.s.line(x1 + (-0.8 if left else 0.8), y1, x + (-1.2 if left else 1.2), y1, w=0.13)
        self.s.line(x2 + (-0.8 if left else 0.8), y2, x + (-1.2 if left else 1.2), y2, w=0.13)
        self.s.add('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="#111" stroke-width="0.18" '
                   'marker-start="url(#aDim)" marker-end="url(#aDim)"/>' % (x, y1, x, y2))
        tx = x - 0.9 if left else x + 2.6
        self.s.text(tx, (y1 + y2) / 2, text or "%g" % round(abs(v2 - v1), 1), size=2.2, anchor="middle",
                    rot=-90)

    def level(self, u, v, label, right=True, length=14):
        x, y = self.p(u, v)
        x2 = x + length if right else x - length
        self.s.line(x, y, x2, y, w=0.13, dash="1.2 0.8")
        tri = [(x2, y), (x2 - 1.3, y - 1.6), (x2 + 1.3, y - 1.6)]
        self.s.poly(tri, w=0.15, fill="#111", close=True)
        self.s.text(x2 + (1.8 if right else -1.8), y - 0.5, label, size=2.0, anchor="start" if right else "end")


def lighten(rgb, k=0.45):
    r, g, b = (c + (1 - c) * k for c in rgb)
    return "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))


def main():
    parts, D = RL.build_parts()
    solids = [(p, make_part(p)) for p in parts]
    by_name = {p["name"]: s for p, s in solids}
    W, DP, H = D["ext_w"], D["ext_d"], D["ext_h"]
    sh = Sheet()

    # ---------------- frame + title block
    sh.rect(8, 8, 404, 281, sw=0.6)
    tb = (272, 247, 140, 42)
    sh.rect(*tb, sw=0.5)
    rows = [
        ("PROJECT", "SRA-16 Silent AC Rack - Dimplex GDC14RBA bay + %d RU acoustic rack" % D["ru_count"]),
        ("TITLE", "General arrangement - elevations and sections"),
        ("DOC NO.", "%s    REV %s" % (DOC_NO, REV)),
        ("SCALE", "1:%d @ A3    UNITS mm    LAYOUT v%s" % (SCALE, RL.VERSION)),
        ("DATE", "%s    DRAWN Claude (AI) for Carbon Project" % datetime.date.today().isoformat()),
        ("STATUS", "CONCEPT - verify AC dims (Note 1) before cutting"),
    ]
    for i, (k, v) in enumerate(rows):
        y = tb[1] + 6.2 + i * 6.3
        sh.text(tb[0] + 2, y, k, size=1.9, weight="bold")
        sh.text(tb[0] + 19, y, v, size=2.3)
        if i:
            sh.line(tb[0], y - 4.6, tb[0] + tb[2], y - 4.6, w=0.15)
    sh.line(tb[0] + 17, tb[1], tb[0] + 17, tb[1] + tb[3], w=0.15)

    floor_y = 234.0
    top_margin = floor_y - H / SCALE

    # ---------------- FRONT VIEW (doors removed)
    hide_front = {"Door lower (AC bay)", "Door lower MLV", "Door upper (rack)", "Door upper MLV", "Handle upper door",
                  "Handle lower door", "Window pane outer", "Window pane inner", "Foam door lower", "Foam door upper",
                  "Skirt front"}
    front = cq.Compound.makeCompound([s for p, s in solids if p["name"] not in hide_front])
    vf = View(sh, 30, floor_y)
    vf.polys(hlr(front, (0, -1, 0), (1, 0, 0)))
    sh.text(30 + W / SCALE / 2, floor_y + 15, "FRONT VIEW - DOORS REMOVED", size=3.0, anchor="middle", weight="bold")
    vf.dim_h(0, W, 0, 6)
    vf.dim_v(0, 0, H, 7)
    vf.dim_v(0, D["z_rack0"], D["z_rack1"], 3.2, text="%d RU = %.1f" % (D["ru_count"], D["z_rack1"] - D["z_rack0"]))
    vf.dim_v(0, D["z_ac0"], D["z_ac1"], 3.2, text="AC %.0f" % D["ac_h"])
    vf.dim_h(D["x_in0"], D["x_ac0"], D["z_ac0"] + 420, 0, text="%.0f" % D["ac_side_gap"])
    sh.line(vf.p(0, 0)[0] - 3, floor_y, vf.p(W, 0)[0] + 3, floor_y, w=0.35)

    # ---------------- SECTION A-A (X = centreline), viewed from the right
    xc = D["x_mid"]
    beyond = clip_solids(solids, "x", -10, xc)
    va = View(sh, 106, floor_y)
    va.polys(hlr(beyond, (1, 0, 0), (0, 1, 0)), w=0.1, c="#9a9da3")
    for part, loops in section_faces(solids, "x", xc, cq.Vector(0, 1, 0), cq.Vector(0, 0, 1)):
        d = ""
        for lp in loops:
            d += "M" + " L".join("%.2f %.2f" % va.p(*q) for q in lp) + " Z "
        sh.add('<path d="%s" fill="%s" fill-rule="evenodd" stroke="#1d1f23" stroke-width="0.14"/>'
               % (d, lighten(part["color"])))
    flows = [
        ("aCold", "#1f6fe0", [(210, 1000), (150, 1060), (120, 1160), (118, 1640), (150, 1690), (400, 1700)]),
        ("aCold", "#1f6fe0", [(118, 1250), (150, 1330), (420, 1340)]),
        ("aHot", "#d9481f", [(640, 1520), (900, 1520), (965, 1450), (965, 1150), (955, 1020), (820, 880),
                             (600, 800), (470, 760)]),
        ("aRoom", "#23913f", [(-60, 45), (200, 55), (700, 60), (950, 80), (955, 230), (940, 310), (820, 305),
                              (600, 320), (470, 330)]),
        ("aExh", "#d99a00", [(D["exh_y"], D["exh_z0"]), (D["exh_y"] + 10, 700), (D["exh_y"] + 78, 752),
                             (D["exh_run_y0"] + 20, D["exh_run_z"]), (DP + 120, D["exh_run_z"])]),
    ]
    for mk, col, pts in flows:
        sh.poly([va.p(*q) for q in pts], w=0.7, c=col, marker=mk)
    sh.text(106 + DP / SCALE / 2, floor_y + 15, "SECTION A-A  (X = %.0f, looking -X)" % xc, size=3.0,
            anchor="middle", weight="bold")
    va.dim_h(0, DP, 0, 6)
    va.dim_h(D["y_in0"], D["y_frail"], H, 5, text="%.0f" % D["front_plenum"], above=True)
    va.dim_h(D["y_frail"], D["y_rrail"], H, 5, text="%.0f rail spacing" % D["rail_spacing"], above=True)
    va.dim_h(D["y_rrail"], D["y_in1"], H, 5, text="%.0f" % D["rear_plenum"], above=True)
    for v, lab in ((D["z_rack1"], "%.1f  top of RU%d" % (D["z_rack1"], D["ru_count"])),
                   (D["z_rack0"], "%.0f  RU1 (shelf top %.0f)" % (D["z_rack0"], D["z_shelf1"])),
                   (D["z_ac1"], "%.0f  AC top" % D["z_ac1"]),
                   (D["exh_run_z"], "%.0f  exhaust CL" % D["exh_run_z"]),
                   (D["z_split"], "%.0f  partition" % D["z_split"]),
                   (D["z_ac0"], "%.0f  AC floor" % D["z_ac0"]),
                   (60.0, "60  drain CL")):
        va.level(DP + 70, v, lab, right=True, length=6)
    sh.line(va.p(-80, 0)[0], floor_y, va.p(DP + 140, 0)[0], floor_y, w=0.35)

    # ---------------- REAR VIEW
    vr = View(sh, 222 + W / SCALE, floor_y, flip_u=True)       # u = X, mirrored (looking from the rear)
    rear_pl = hlr(cq.Compound.makeCompound([s for p, s in solids]), (0, 1, 0), (-1, 0, 0))
    # projector x axis is -X, so u = -X: shift so that u = 0 at X = W
    for pl in rear_pl:
        sh.poly([vr.p(-q[0], q[1]) for q in pl], w=0.13, c="#333")
    sh.text(222 + W / SCALE / 2, floor_y + 15, "REAR VIEW", size=3.0, anchor="middle", weight="bold")
    vr.dim_h(W, 0, 0, 6, text="%.0f" % W)
    ex, ez = D["exh_x"], D["exh_run_z"]
    vr.dim_h(W, ex, ez, 0, text="%.1f" % (W - ex))
    vr.dim_v(0, 0, ez, 5, text="%.0f" % ez, left=False)
    x_e, y_e = vr.p(ex, ez)
    sh.line(x_e, y_e - 5.5, x_e + 4, y_e - 13, w=0.15)
    sh.text(x_e + 4.5, y_e - 15.8, "EXHAUST SPIGOT D150", size=2.0, anchor="start")
    sh.text(x_e + 4.5, y_e - 13.4, "to outdoors (flex duct)", size=1.8, anchor="start")
    x_d, y_d = vr.p(D["drain_x"], 60)
    sh.line(x_d, y_d + 0.8, x_d, floor_y + 9.2, w=0.15)
    sh.text(x_d - 1, floor_y + 11.2, "DRAIN D16 barb (to floor waste / pump)", size=1.8, anchor="end")
    sx, sy = vr.p(D["x_mid"], D["z_toprail0"] - 126)
    sh.text(sx, sy - 5, "CABLE ENTRY (brush, lined box)", size=1.8, anchor="middle")
    sh.line(vr.p(W + 20, 0)[0], floor_y, vr.p(-20, 0)[0], floor_y, w=0.35)

    # ---------------- SECTION C-C (plan at Z = 700)
    zc = 700.0
    below = clip_solids(solids, "z", -10, zc)
    vp = View(sh, 296, 26 + DP / SCALE, u0=0, v0=0)
    vp.polys(hlr(below, (0, 0, 1), (1, 0, 0)), w=0.1, c="#9a9da3")
    for part, loops in section_faces(solids, "z", zc, cq.Vector(1, 0, 0), cq.Vector(0, 1, 0)):
        d = ""
        for lp in loops:
            d += "M" + " L".join("%.2f %.2f" % vp.p(q[0], q[1]) for q in lp) + " Z "
        sh.add('<path d="%s" fill="%s" fill-rule="evenodd" stroke="#1d1f23" stroke-width="0.14"/>'
               % (d, lighten(part["color"])))
    # plan is drawn with rear at the top: v = Y
    sh.text(296 + W / SCALE / 2, 26 + DP / SCALE + 11, "SECTION C-C  (Z = %.0f)" % zc, size=3.0,
            anchor="middle", weight="bold")
    vp.dim_h(0, W, 0, 4.5)
    vp.dim_v(0, 0, DP, 4.5)
    sh.text(vp.p(W, 0)[0] + 2.5, vp.p(W, 0)[1] - 1, "FRONT", size=2.0)
    sh.text(vp.p(W, DP)[0] + 2.5, vp.p(W, DP)[1] + 2, "REAR", size=2.0)

    # section markers on the front view
    xa, _ = vf.p(xc, 0)
    sh.text(xa, top_margin - 4, "A", size=2.6, anchor="middle", weight="bold")
    sh.line(xa, top_margin - 3, xa, floor_y + 1, w=0.18, dash="4 1 1 1", c="#555")
    _, yc_ = vf.p(0, zc)
    sh.line(vf.p(0, 0)[0] - 2, yc_, vf.p(W, 0)[0] + 2, yc_, w=0.18, dash="4 1 1 1", c="#555")
    sh.text(vf.p(W, 0)[0] + 3, yc_ + 0.8, "C", size=2.6, weight="bold")

    # ---------------- legend + notes
    lx, ly = 272, 124
    sh.text(lx, ly, "AIRFLOW (Section A-A)", size=2.6, weight="bold")
    for i, (col, lab) in enumerate((("#1f6fe0", "Cold supply: AC outlet > hood > front plenum > IT"),
                                    ("#d9481f", "Hot return: IT > rear plenum > shelf > AC upper grille"),
                                    ("#23913f", "Room air: plinth > lined riser > AC lower grille"),
                                    ("#d99a00", "Condenser exhaust: spigot > elbow > rear wall"))):
        y = ly + 4.2 + i * 3.8
        sh.line(lx, y - 0.8, lx + 7, y - 0.8, w=0.9, c=col)
        sh.text(lx + 9, y, lab, size=2.1)
    notes = [
        "NOTES",
        "1. AC reference geometry = Dimplex GDC14RBA (label 476W x 358D x 840H, 31.5 kg).",
        "   Notch, grille split (~420), spigot and outlet sizes are photo/manual",
        "   estimates - tape-check (docs/DESIGN.md s.3) before cutting panels.",
        "2. Walls: 15 birch ply + 5 kg/m2 MLV + 40 melamine foam (FR) in a 40x40",
        "   aluminium T-slot frame. All joints sealed; no line-of-sight openings.",
        "3. Closed loop: cold and hot zones separated by the shelf, hood, IT +",
        "   blanking panels and air dams. Verified by voxel flood-fill (zone_check).",
        "4. Condenser zone below partition draws room air through the plinth",
        "   labyrinth; exhaust D150 insulated duct to rear spigot -> outdoors.",
        "5. Docking seals: EPDM gaskets + brush strip at AC back (Y=%.0f), AC" % D["y_ac1"],
        "   held back by retention bar; hood drop-collar seals on AC top.",
        "6. Drip tray 1.2 SS full bay floor; AC drain + tray -> 16 mm hose, fall",
        "   to floor waste or condensate pump. Leak sensor in tray.",
        "7. 19in rails EIA-310, %.0f mm rail spacing; blank all unused RU." % D["rail_spacing"],
        "8. External %.0f W x %.0f D x %.0f H (+ handles 36, spigot 60)." % (W, DP, H),
    ]
    for i, t in enumerate(notes):
        sh.text(lx, 146 + i * 3.35, t, size=2.05 if i else 2.6, weight="bold" if i == 0 else "normal")

    # ---------------- iso render (from renders/, not to scale)
    try:
        import base64
        import io
        from PIL import Image, ImageChops
        for fn, (x0, y0, hmax), cap in (("cutaway_front_right.png", (16, 13, 76), "ISO - DOORS + RIGHT SIDE REMOVED"),
                                        ("hero_front_left.png", (122, 13, 76), "ISO - CLOSED")):
            im = Image.open(os.path.join(ROOT, "renders", fn)).convert("RGB")
            bg = Image.new("RGB", im.size, im.getpixel((2, 2)))
            bbox = ImageChops.difference(im, bg).getbbox()
            im = im.crop(bbox)
            im.thumbnail((900, 900))
            wmm = hmax * im.width / im.height
            buf = io.BytesIO()
            im.save(buf, "PNG", optimize=True)
            sh.add('<image x="%.1f" y="%.1f" width="%.1f" height="%.1f" href="data:image/png;base64,%s"/>'
                   % (x0, y0, wmm, hmax, base64.b64encode(buf.getvalue()).decode()))
            sh.text(x0 + wmm / 2, y0 + hmax + 3.2, cap + " (not to scale)", size=2.0, anchor="middle")
    except Exception as e:  # renders are optional
        print("iso render skipped:", e)

    out = os.path.join(ROOT, "drawings", "%s.svg" % DOC_NO)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as fh:
        fh.write(sh.svg())
    print("wrote", out)


if __name__ == "__main__":
    main()
