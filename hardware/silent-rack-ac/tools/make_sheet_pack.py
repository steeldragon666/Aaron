#!/usr/bin/env python3
"""
Sheet-metal pack CP-SRA16-SMP-001 for the SRA-16 - laser-cut parts generated
from rack_layout.py via tools/sheetmetal.py, so every hole follows the CAD.

Outputs (relative to hardware/silent-rack-ac/):
  cad/dxf/cut/<ID>.dxf          cut geometry only (outline, holes, cut-outs), 1:1 mm - send these to the laser
  cad/dxf/info/<ID>.dxf         same + bend lines, part-ID etch text and notes on separate layers
  cad/dxf/nest/<material>_<n>.dxf   parts nested on 1200 x 800 blanks (cut layer + sheet outline)
  cad/dxf/SRA16_sheet_metal_DXF.zip
  bom/sheet_metal_parts.csv, bom/sheet_metal_nesting.csv
  drawings/CP-SRA16-SMP-001_s1..s6.svg + CP-SRA16-SMP-001.pdf
  docs/SHEET_METAL.md

Usage: python3 tools/make_sheet_pack.py [--no-pdf] [key=value ...]
"""
import csv
import math
import os
import subprocess
import sys
import zipfile
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import sheetmetal as SMP  # noqa: E402
import make_weld_pack as WP  # noqa: E402
from make_weld_pack import Svg, INK, THIN, TODAY  # noqa: E402

N_SHEETS = 6
BLANK = (1200.0, 800.0)      # cutter bed / blank size used for nesting
MARGIN, GAP = 8.0, 6.0
RED = "#c0392b"


# ======================================================================= geometry helpers
arc_pts, poly_pts = SMP.arc_pts, SMP.loop_pts


def xform(rot, h, dx, dy):
    """Placement: optional 90 deg CCW rotation of a part of height h, then translate."""
    if rot:
        return lambda u, v: (dx + h - v, dy + u)
    return lambda u, v: (dx + u, dy + v)


# ======================================================================= DXF
def dxf_doc():
    import ezdxf
    from ezdxf import units
    ezdxf.options.write_fixed_meta_data_for_testing = True   # no timestamps or random GUIDs: same part, same file
    doc = ezdxf.new("R2000", setup=True)
    doc.units = units.MM
    doc.header["$INSUNITS"] = 4
    doc.header["$MEASUREMENT"] = 1
    for name, color, lt in (("CUT", 7, "CONTINUOUS"), ("BEND", 1, "DASHED"), ("ETCH", 3, "CONTINUOUS"),
                            ("NOTES", 8, "CONTINUOUS"), ("SHEET", 5, "DASHED")):
        if name not in doc.layers:
            doc.layers.add(name, color=color, linetype=lt)
    return doc


def add_part(msp, p, tf=None, rot=False, info=False, label=None):
    tf = tf or (lambda u, v: (u, v))

    def lw(loop, layer="CUT"):
        pts = [tf(*q) for q in loop["pts"]]
        msp.add_lwpolyline([(x, y, 0, 0, b) for (x, y), b in zip(pts, loop["bulge"])], format="xyseb",
                           close=True, dxfattribs={"layer": layer})
    lw(p.outline)
    for h in p.holes:
        msp.add_circle(tf(h["u"], h["v"]), h["d"] / 2.0, dxfattribs={"layer": "CUT"})
    for q in p.squares:
        a = q["a"] / 2.0
        lw({"pts": SMP.rect(q["u"] - a, q["v"] - a, q["u"] + a, q["v"] + a), "bulge": [0] * 4})
    for c in p.cuts:
        lw(c)
    if label:
        x, y = tf(*label_spot(p))
        msp.add_text(label, height=5.0 if min(p.w, p.h) > 30 else 2.5,
                     dxfattribs={"layer": "NOTES" if not info else "ETCH", "rotation": 90 if rot else 0}
                     ).set_placement((x, y))
    if info:
        for b in p.bends:
            msp.add_line(tf(b["u0"], b["v0"]), tf(b["u1"], b["v1"]), dxfattribs={"layer": "BEND"})
            x, y = tf((b["u0"] + b["u1"]) / 2.0, (b["v0"] + b["v1"]) / 2.0)
            msp.add_text("BEND %s 90 R%g" % (b["dir"], b["R"]), height=3.0,
                         dxfattribs={"layer": "BEND"}).set_placement((x + 2, y + 1.5))


def label_spot(p):
    """A spot inside the part clear of holes for the ID etch."""
    best, bd = (p.w / 2, p.h / 2), -1
    for fu in (0.5, 0.3, 0.7, 0.2, 0.8):
        for fv in (0.5, 0.35, 0.65, 0.2, 0.8):
            u, v = p.w * fu, p.h * fv
            if not SMP.point_in_poly(u, v, poly_pts(p.outline)):
                continue
            d = min([math.dist((u, v), (h["u"], h["v"])) - h["d"] / 2 for h in p.holes] +
                    [math.dist((u, v), (q["u"], q["v"])) - q["a"] for q in p.squares] + [1e9])
            for c in p.cuts:
                xs, ys = [x for x, _ in c["pts"]], [y for _, y in c["pts"]]
                if min(xs) - 5 <= u <= max(xs) + 5 and min(ys) - 5 <= v <= max(ys) + 5:
                    d = -1
            if d > bd:
                best, bd = (u, v), d
    return best


def notes_lines(p, sm):
    m = SMP.MATERIALS[p.mat]
    out = ["%s  %s" % (p.id, p.name), "%s %.1f mm, qty %d, %s" % (m["name"], p.t, p.qty, m["finish"]),
           "flat %.1f x %.1f mm, %s" % (p.w, p.h, p.view), "fits: %s" % p.where,
           "%s  %s rev %s  generated %s" % (SMP.DOC_NO, "rack_layout v" + sm["D"].get("version", ""), SMP.REV, TODAY)]
    for b in p.bends:
        out.append("bend %s 90 deg, R%g inside (K %.2f flat allowance)" % (b["dir"], b["R"], SMP.SM["k_factor"]))
    return out + p.notes


def write_dxfs(sm, out):
    for sub in ("cut", "info", "nest"):
        os.makedirs(os.path.join(out, sub), exist_ok=True)
    files = []
    for p in sm["parts"]:
        for kind in ("cut", "info"):
            doc = dxf_doc()
            msp = doc.modelspace()
            add_part(msp, p, info=(kind == "info"), label=p.id if kind == "info" else None)
            if kind == "info":
                for i, t in enumerate(notes_lines(p, sm)):
                    msp.add_text(t, height=3.5, dxfattribs={"layer": "NOTES"}).set_placement((0, -12 - 6 * i))
            fn = os.path.join(out, kind, dxf_name(p))
            doc.saveas(fn)
            files.append(fn)
    return files


# ======================================================================= nesting (MaxRects, best short side fit)
class MaxRects:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.free = [(0.0, 0.0, W, H)]
        self.used = []

    def find(self, w, h):
        best = None
        for fx, fy, fw, fh in self.free:
            for rw, rh, rot in ((w, h, False), (h, w, True)):
                if rw <= fw + 1e-9 and rh <= fh + 1e-9:
                    key = (min(fw - rw, fh - rh), max(fw - rw, fh - rh), fy, fx)
                    if best is None or key < best[0]:
                        best = (key, fx, fy, rw, rh, rot)
        return best

    def place(self, x, y, w, h):
        new = []
        for fx, fy, fw, fh in self.free:
            if x >= fx + fw or x + w <= fx or y >= fy + fh or y + h <= fy:
                new.append((fx, fy, fw, fh))
                continue
            if x > fx:
                new.append((fx, fy, x - fx, fh))
            if x + w < fx + fw:
                new.append((x + w, fy, fx + fw - x - w, fh))
            if y > fy:
                new.append((fx, fy, fw, y - fy))
            if y + h < fy + fh:
                new.append((fx, y + h, fw, fy + fh - y - h))
        new = list(dict.fromkeys((round(a, 6), round(b, 6), round(c, 6), round(d, 6)) for a, b, c, d in new))

        def inside(a, b):
            return a[0] >= b[0] - 1e-6 and a[1] >= b[1] - 1e-6 and a[0] + a[2] <= b[0] + b[2] + 1e-6 and \
                a[1] + a[3] <= b[1] + b[3] + 1e-6
        self.free = [a for i, a in enumerate(new) if not any(j != i and inside(a, b) for j, b in enumerate(new))]
        self.used.append((x, y, w, h))


def nest(sm):
    """{material key: [sheet: [(part, x, y, rot)]]} on BLANK with MARGIN and GAP (x, y = lower-left of the part)."""
    groups = OrderedDict()
    for p in sm["parts"]:                                   # same stock -> same blanks (skins + thin parts)
        groups.setdefault((SMP.MATERIALS[p.mat]["name"], p.t), []).extend([p] * p.qty)
    W, H = BLANK[0] - 2 * MARGIN + GAP, BLANK[1] - 2 * MARGIN + GAP
    res = OrderedDict()
    for key, ps in groups.items():
        bins = []
        for p in sorted(ps, key=lambda q: (-q.w * q.h, q.id)):
            placed = False
            for b in bins:
                f = b["mr"].find(p.w + GAP, p.h + GAP)
                if f:
                    _, x, y, rw, rh, rot = f
                    b["mr"].place(x, y, rw, rh)
                    b["parts"].append((p, MARGIN + x, MARGIN + y, rot))
                    placed = True
                    break
            if not placed:
                mr = MaxRects(W, H)
                f = mr.find(p.w + GAP, p.h + GAP)
                if not f:
                    raise ValueError("%s does not fit a %gx%g blank" % (p.id, *BLANK))
                _, x, y, rw, rh, rot = f
                mr.place(x, y, rw, rh)
                bins.append({"mr": mr, "parts": [(p, MARGIN + x, MARGIN + y, rot)]})
        res[key] = [b["parts"] for b in bins]
    return res


def mat_short(name):
    return "SS304" if "Stainless" in name else "plate" if "plate" in name else "steel"


def mat_tag(key):
    name, t = key
    return "%s_%gmm" % (mat_short(name), t)


def dxf_name(p):
    return "%s_%gmm_%s_x%d.dxf" % (p.id, p.t, mat_short(SMP.MATERIALS[p.mat]["name"]), p.qty)


def write_nests(nests, out):
    files = []
    for key, sheets in nests.items():
        for i, sheet in enumerate(sheets):
            doc = dxf_doc()
            msp = doc.modelspace()
            msp.add_lwpolyline(SMP.rect(0, 0, BLANK[0], BLANK[1]), close=True, dxfattribs={"layer": "SHEET"})
            for p, x, y, rot in sheet:
                add_part(msp, p, xform(rot, p.h, x, y), rot=rot, label=p.id)
            fn = os.path.join(out, "nest", "%s_sheet%d.dxf" % (mat_tag(key), i + 1))
            doc.saveas(fn)
            files.append(fn)
    return files


# ======================================================================= CSV
def write_csvs(sm, nests):
    os.makedirs(os.path.join(ROOT, "bom"), exist_ok=True)
    with open(os.path.join(ROOT, "bom", "sheet_metal_parts.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "name", "material", "thickness_mm", "qty", "flat_w_mm", "flat_h_mm", "mass_kg_each",
                    "holes", "square_holes", "cutouts", "edge_notches", "bends", "cut_length_m_each", "pierces_each",
                    "finish",
                    "fits", "hold_for", "dxf"])
        for p in sm["parts"]:
            m = SMP.MATERIALS[p.mat]
            w.writerow([p.id, p.name, m["name"], p.t, p.qty, "%.1f" % p.w, "%.1f" % p.h, "%.2f" % p.mass(),
                        len(p.holes), len(p.squares), len(p.cuts), sum(1 for b in p.outline["bulge"] if b < 0),
                        len(p.bends), "%.2f" % (p.cut_length() / 1000),
                        p.pierces(), m["finish"], p.where, p.hold, "cad/dxf/cut/%s" % dxf_name(p)])
    with open(os.path.join(ROOT, "bom", "sheet_metal_nesting.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["material", "thickness_mm", "blank", "parts", "used_pct", "dxf"])
        for key, sheets in nests.items():
            for i, sheet in enumerate(sheets):
                used = sum(p.w * p.h for p, *_ in sheet) / (BLANK[0] * BLANK[1]) * 100
                w.writerow([key[0], key[1], "%gx%g" % BLANK, " ".join(p.id for p, *_ in sheet),
                            "%.0f" % used, "cad/dxf/nest/%s_sheet%d.dxf" % (mat_tag(key), i + 1)])


# ======================================================================= drawings
def title_block(sh, sm, n, title, scale):
    D = sm["D"]
    tb = (272, 247, 140, 42)
    sh.rect(*tb, sw=0.5, fill="#ffffff")
    rows = [("PROJECT", "SRA-16 Silent AC Rack - laser-cut sheet-metal parts"),
            ("TITLE", title),
            ("DOC NO.", "%s   SHEET %d OF %d   REV %s" % (SMP.DOC_NO, n, N_SHEETS, SMP.REV)),
            ("SCALE", "%s @ A3   UNITS mm   LAYOUT v%s" % (scale, D.get("version", ""))),
            ("DATE", "%s   DRAWN Claude (AI) for Carbon Project" % TODAY),
            ("STATUS", "FOR CUTTING - DXF is the master; confirm hardware (sheet 5)")]
    for i, (k, v) in enumerate(rows):
        y = tb[1] + 6.2 + i * 6.3
        sh.text(tb[0] + 2, y, k, size=1.9, weight="bold")
        sh.text(tb[0] + 19, y, v, size=WP.fit_text(v, 118, 2.15))
        if i:
            sh.line(tb[0], y - 4.6, tb[0] + tb[2], y - 4.6, w=0.15)
    sh.line(tb[0] + 17, tb[1], tb[0] + 17, tb[1] + tb[3], w=0.15)


def draw_part(sh, p, x0, y0, k, fill="#eef1f4", holes=True, bends=True, sw=0.25, mirror=False):
    """Part with its blank's top-left at paper (x0, y0), k paper mm per mm; v up (mirror: u flipped)."""
    P = lambda u, v: (x0 + ((p.w - u) if mirror else u) * k, y0 + (p.h - v) * k)   # noqa: E731
    sh.poly([P(*q) for q in poly_pts(p.outline)], w=sw, fill=fill, close=True)
    if holes:
        for h in p.holes:
            x, y = P(h["u"], h["v"])
            sh.circle(x, y, max(h["d"] / 2 * k, 0.28), sw=0.12, fill="#ffffff")
        for q in p.squares:
            a = max(q["a"] * k, 0.4)
            x, y = P(q["u"], q["v"])
            sh.rect(x - a / 2, y - a / 2, a, a, sw=0.1, fill="#ffffff")
        for c in p.cuts:
            sh.poly([P(*q) for q in poly_pts(c)], w=0.15, fill="#ffffff", close=True)
    if bends:
        for b in p.bends:
            (ax, ay), (bx, by) = P(b["u0"], b["v0"]), P(b["u1"], b["v1"])
            sh.line(ax, ay, bx, by, w=0.25, c=RED, dash="1.6 0.8")
    return P


def hole_legend(p):
    g = OrderedDict()
    for h in p.holes:
        k = (h["d"], h["use"].split(" (")[0])
        g[k] = g.get(k, 0) + 1
    out = ["%d x D%g %s" % (n, d, u) for (d, u), n in g.items()]
    if p.squares:
        out.append("%d x %g sq %s" % (len(p.squares), p.squares[0]["a"], p.squares[0]["use"]))
    for c in p.cuts:
        out.append(c["use"])
    notches = sum(1 for b in p.outline["bulge"] if b < 0)
    if notches:
        out.append("%d x R%g edge notch, joint strip screw" % (notches, SMP.SM["frame_screw"] / 2.0))
    merged = OrderedDict()
    for o in out:
        merged[o] = merged.get(o, 0) + 1
    return [("%s (x%d)" % (o, n) if n > 1 and not o[0].isdigit() else o) for o, n in merged.items()]


SCALES = [1.0, 0.5, 0.2, 0.1, 1 / 15.0, 0.05, 0.04]


def part_cell(sh, p, cx, cy, cw, ch):
    """One flat pattern in a cell: title, part, overall dims, bend dims, legend."""
    sh.rect(cx, cy, cw, ch, sw=0.15, c="#b8bec5")
    m = SMP.MATERIALS[p.mat]
    sh.text(cx + 2, cy + 4.2, "%s  x%d" % (p.id, p.qty), size=2.8, weight="bold")
    sh.text(cx + 22, cy + 4.2, p.name, size=WP.fit_text(p.name, cw - 24, 1.9))
    sh.text(cx + 2, cy + 7.8, "%s %.1f - %s" % (m["name"], p.t, m["finish"]), size=WP.fit_text(
        "%s %.1f - %s" % (m["name"], p.t, m["finish"]), cw - 4, 1.7), c=THIN)
    leg = hole_legend(p)
    nleg = min(len(leg), 4)
    aw, ah = cw - 16, ch - 12 - 9 - nleg * 2.6
    k = next((s for s in SCALES if p.w * s <= aw and p.h * s <= ah), SCALES[-1])
    pw, ph = p.w * k, p.h * k
    x0 = cx + 10 + (aw - pw) / 2
    y0 = cy + 10.5 + (ah - ph) / 2
    draw_part(sh, p, x0, y0, k)
    WP.hdim(sh, x0, x0 + pw, y0 + ph, y0 + ph + 3.6, "%.1f" % p.w, size=1.7, above=False)
    WP.vdim(sh, y0, y0 + ph, x0, x0 - 3.2, "%.1f" % p.h, size=1.7)
    for b in p.bends:
        if abs(b["v0"] - b["v1"]) < 1e-6:                   # horizontal bend line: dim from the bottom edge
            yb = y0 + (p.h - b["v0"]) * k
            sh.text(x0 + pw + 1.2, yb + 0.6, "%.1f" % b["v0"], size=1.6, c=RED)
        else:
            xb = x0 + b["u0"] * k
            sh.text(xb, y0 - 1.0, "%.1f" % b["u0"], size=1.6, c=RED, anchor="middle")
    sc = "1:%g" % round(1 / k) if k < 1 else "1:1"
    sh.text(cx + cw - 2, cy + 4.2, sc, size=1.9, anchor="end", c=THIN)
    for i, t in enumerate(leg[:4]):
        sh.text(cx + 2, cy + ch - 2 - (nleg - 1 - i) * 2.6, t, size=WP.fit_text(t, cw - 4, 1.75))


def sheet_parts(sm, ids, n, title):
    sh = Svg()
    WP.border(sh)
    parts = {p.id: p for p in sm["parts"]}
    cols, rows = 3, 3
    x0, y0, cw, ch = 12.0, 12.0, 132.0, 77.3
    for i, pid in enumerate(ids):
        r, c = divmod(i, cols)
        if r >= rows:
            break
        if r == rows - 1 and c == cols - 1:
            ch_ = 235 - (y0 + r * ch) - 1
        else:
            ch_ = ch - 1
        part_cell(sh, parts[pid], x0 + c * cw, y0 + r * ch, cw - 1, ch_)
    title_block(sh, sm, n, title, "as noted per part")
    return sh


def elevations(sm, sh, ox, oy, k):
    """Exterior elevations with the skin pieces, strips, hardware and skirts. Returns bottom y."""
    D = sm["D"]
    ps = [p for p in sm["parts"] if p.place]
    zb0 = D["z_base0"]
    H = D["z_toprail1"] - zb0
    W, DP = D["ext_w"], D["ext_d"]
    ground = oy + (H + zb0) * k                               # floor line on paper
    views = [("front", "FRONT", W), ("left", "LEFT SIDE", DP), ("rear", "REAR", W), ("right", "RIGHT SIDE", DP)]
    x = ox
    fills = {"skin": "#e9ecef", "sm": "#cfd6dd"}
    for face, lab, width in views:
        sh.rect(x, oy, width * k, H * k, sw=0.1, c="#cfd4da", fill="none", dash="0.8 0.6")
        for p, place, mirror in [(q, q.place, False) for q in ps] + [(q, q.twin_place, True) for q in ps if q.twin_place]:
            if place[0] != face:
                continue
            du, dv = place[1] if face in ("left", "right") else 0, place[2]
            P = draw_part(sh, p, x + du * k, oy + (H - dv - p.h) * k, k, fill=fills.get(p.mat, "#e9ecef"),
                          bends=False, sw=0.2, mirror=mirror)
            if p.mat == "skin":
                u, v = label_spot(p)
                tx, ty = P(u, v)
                sh.text(tx, ty + 1.0, p.id, size=2.6 if p.h * k > 8 else 1.9, anchor="middle", weight="bold", c=RED)
        # skirts under the frame
        sh.line(x - 3, ground, x + width * k + 3, ground, w=0.4)
        sh.rect(x + (D["skin"] + D["pad_w"] + 2) * k, oy + H * k + 1.5, (width - 2 * (D["skin"] + D["pad_w"] + 2)) * k,
                (zb0 - 10 - 1.5) * k, sw=0.15, fill="#adb5bd")
        sh.text(x + width * k / 2, ground + 4.5, lab, size=2.3, anchor="middle", weight="bold")
        views_x = x
        # hardware seen on this face
        if face == "front":
            for zc in D["hinge_z_lower"] + D["hinge_z_upper"]:
                sh.rect(views_x - 0.5, oy + (H - (zc - zb0) - 50) * k, (D["hw_x_left"] + 10) * k, 100 * k, sw=0.12,
                        fill="#8d99a6")
            for zc in D["latch_z_lower"] + D["latch_z_upper"]:
                sh.rect(views_x + (D["hw_x_right"] - 14) * k, oy + (H - (zc - zb0) - 20) * k,
                        (W - D["hw_x_right"] + 16) * k, 40 * k, sw=0.12, fill="#8d99a6")
        if face == "left":
            for zc in D["hinge_z_lower"] + D["hinge_z_upper"]:
                sh.rect(views_x + (DP - D["skin"] - (D["hw_y_side"] + 10)) * k + D["skin"] * k,
                        oy + (H - (zc - zb0) - 50) * k, (D["hw_y_side"] + 10) * k, 100 * k, sw=0.12, fill="#8d99a6")
        if face == "right":
            for zc in D["latch_z_lower"] + D["latch_z_upper"]:
                sh.rect(views_x + (D["hw_y_side"] - 6) * k, oy + (H - (zc - zb0) - 12) * k, 55 * k, 24 * k, sw=0.12,
                        fill="#8d99a6")
        x += width * k + 12
    return ground + 8


def sheet1(sm, nests):
    D = sm["D"]
    sh = Svg()
    WP.border(sh)
    k = 1 / 20.0
    WP.heading(sh, 14, 16, "SKIN LAYOUT - EXTERIOR ELEVATIONS 1:20 (pieces as seen from outside)", size=2.6)
    yb = elevations(sm, sh, 16, 24, k)
    # top view under the front view
    tp = [p for p in sm["parts"] if p.id == "TP1"][0]
    draw_part(sh, tp, 16, yb + 6, k)
    sh.text(16 + tp.w * k / 2, yb + 6 + tp.h * k + 4.5, "TOP (front edge at bottom)", size=2.3, anchor="middle",
            weight="bold")
    sh.text(16 + tp.w * k / 2, yb + 6 + tp.h * k / 2, "TP1", size=2.6, anchor="middle", weight="bold", c=RED)
    WP.paragraph(sh, 60, yb + 10, [
        "Grey bars: hinges (front + left), latches + keepers (front + right).",
        "Strips JS/JR cover the skin joints on the mid and shelf rails.",
        "Skirts SK1-SK3 sit under the base rails between the castor pads.",
        "Dots: D8 screw holes on the frame rivnuts (weld pack sheet 6).",
        "Every frame rivnut is matched by a hole (checked by sheetmetal.py).",
    ], size=1.9, lh=3.0)
    # parts table (right)
    x0 = 250
    WP.heading(sh, x0, 16, "PARTS (one DXF each)", size=2.6)
    rows = []
    for p in sm["parts"]:
        rows.append((p.id, str(p.qty), p.name.split(" (")[0].replace("Door stiffener, ", "Stiffener ") +
                     ("  - HOLD %s" % p.hold if p.hold else ""),
                     "%g" % p.t, "%.0f x %.0f" % (p.w, p.h), str(len(p.holes) + len(p.squares)), str(len(p.bends))))
    y = WP.table(sh, x0, 18, [(10, "c"), (7, "c"), (78, "l"), (8, "c"), (26, "r"), (16, "c"), (11, "c")], rows,
                 head=("ID", "QTY", "PART", "t", "FLAT", "HOLES", "BENDS"), size=1.75, rh=3.05)
    tot = sum(p.qty for p in sm["parts"])
    kg = sum(p.qty * p.mass() for p in sm["parts"])
    nb = {mat_tag(k_): len(v) for k_, v in nests.items()}
    sh.text(x0, y + 3.6, "%d pieces, %.0f kg. Largest blank %.0f x %.0f (limit %.0f x %.0f)." % (
        tot, kg, *max(((p.w, p.h) for p in sm["parts"]), key=lambda q: q[0] * q[1]), D["sheet_max_l"],
        D["sheet_max_w"]), size=1.85, weight="bold")
    sh.text(x0, y + 7.0, "Blanks %gx%g: %s" % (BLANK[0], BLANK[1], ", ".join("%s x%d" % (a, b) for a, b in nb.items())),
            size=WP.fit_text("Blanks: " + str(nb), 158, 1.85))
    WP.heading(sh, x0, y + 16, "ORDERING", size=2.4)
    WP.paragraph(sh, x0, y + 21, [
        "Send cad/dxf/cut/ - each file is named ID_thickness_material_qty,",
        "e.g. SL3_1.2mm_steel_x1.dxf - plus bom/sheet_metal_parts.csv.",
        "Or cut the nested blanks in cad/dxf/nest/ on a %gx%g bed." % BLANK,
        "Folding: %d parts, %d bends (flat blanks: R = t, K %.2f)." % (
            sum(1 for p in sm["parts"] if p.bends), sum(p.qty * len(p.bends) for p in sm["parts"]),
            SMP.SM["k_factor"]),
        "Tap the four PD1 pads M8 after cutting. Coat after folding.",
        "HOLD %s until tape check M3: they move with the mid rail." % " ".join(sm["hold"]),
    ], size=1.85, lh=3.05)
    WP.heading(sh, 14, 216, "NOTES", size=2.4)
    WP.paragraph(sh, 14, 221, [
        "1  DXF (cad/dxf/cut) is the master geometry, 1:1 mm. info/ adds bend lines, ID etch and notes on layers.",
        "2  Skins %.1f mm steel (Zincanneal/CR4), powder coat both sides, then bond 3 mm MLV inside (D8 at the frame "
        "screws: it is the gasket)." % D["skin_t"],
        "3  Frame screws: M6 x 20 flanged button head through D%.0f (+-1 mm frame tolerance) into the frame" % SMP.SM["frame_screw"],
        "   rivnuts. Rivets: 4.8 mm blind, D%.0f holes. Deburr all holes; mask nothing - coat before rivnuts." % SMP.SM["rivet"],
        "4  Folded parts: flat blanks for R = t inside, K %.2f. Check one test bend on your brake first." % SMP.SM["k_factor"],
        "5  Split skins meet on the rail centreline with a 1 mm gap and R4 notches round each strip screw; the strip",
        "   clamps both edges (sealant under). Detail J, sheet 5.",
    ], size=1.85, lh=3.05)
    title_block(sh, sm, 1, "Skin layout, parts list", "1:20 (elevations)")
    return sh


def sheet5(sm):
    """19in rail + hardware schedule + assembly sequence."""
    D = sm["D"]
    HW = SMP.RL.HW
    sh = Svg()
    WP.border(sh)
    parts = {p.id: p for p in sm["parts"]}
    part_cell(sh, parts["RR1"], 12, 12, 192, 58)
    WP.heading(sh, 14, 80, "HARDWARE - hole patterns assume these parts (confirm before cutting)", size=2.5)
    n_h = len(D["hinge_z_lower"]) + len(D["hinge_z_upper"])
    n_l = len(D["latch_z_lower"]) + len(D["latch_z_upper"])
    frame_holes = sum(1 for h in sm["frame_holes"] if h["use"] != "spacer")
    rivets = n_h * 2 * len(HW["hinge_holes"]) + n_l * (len(HW["latch_holes"]) + len(HW["keeper_rivets"]))
    rows = [
        ("Lift-off butt hinge, stainless", str(n_h), "100 long; rivet line %.1f mm from the knuckle axis on both leaves "
         "(drill the leaves to suit), 3 x D5 per leaf at 35 pitch" % (D["hw_x_left"] + HW["knuckle_r"])),
        ("Adjustable toggle latch, stainless", str(n_l), "base 4 x D5 on %g x %g, first row %.1f mm behind the door "
         "face (detail L); hook engages the KB1 slot" % (HW["latch_holes"][2][0] - HW["latch_holes"][0][0],
                                                          2 * HW["latch_holes"][1][1],
                                                          D["hw_y_side"] + HW["latch_holes"][0][0])),
        ("Latch keeper KB1 (made, sheet 4)", str(n_l), "riveted to door + stiffener, 2 x D5"),
        ("Pull handle %g c/c" % HW["handle_pitch"], "2", "2 x M5 from inside, through door + DA stiffener"),
        ("Blind rivet 4.8 mm, stainless", str(rivets), "4.8 x 8 (grip 3-5) for hinges and KB1, 4.8 x 6 for the latch "
         "bases; grips: door leaf 4.4, side leaf 3.2, KB1 3.6"),
        ("M6 x 20 flanged button head", str(frame_holes), "skins, strips and skirts into the frame rivnuts"),
        ("Polycarbonate 6 mm, %gx%g" % (D["win_w"] + 40, D["win_h"] + 40), "2", "drilled 8 x D5 to the WR1 pattern"),
        ("EPDM 10 mm spacer frame + 8 x M4 x 35", "1", "window clamp: skin / pane / spacer / pane / WR1"),
        ("Exhaust flanged spigot D150", "1", "4 x M5 on PCD %g at 45 deg (RP1)" % SMP.SM["spigot_pcd"]),
        ("Brush cable grommet 200 x 40", "1", "4 x M4 on %g x %g (RP2)" % SMP.SM["grommet_pattern"]),
        ("16 mm drain bulkhead barb", "1", "D%g in SK2" % SMP.RL.SKIRT["drain_d"]),
    ]
    y = WP.table(sh, 14, 82, [(50, "l"), (9, "c"), (131, "l")], rows, head=("ITEM", "QTY", "HOLES / NOTE"),
                 size=1.75, rh=3.4)
    WP.heading(sh, 14, y + 8, "ASSEMBLY", size=2.5)
    WP.paragraph(sh, 14, y + 13, [
        "1  Coat all parts. Bond MLV inside the skins and doors: punch it D8 at the frame screws (it is the gasket), "
        "clear it 3 mm round rivets and M4/M5 holes.",
        "2  Doors: bond the DA stiffener frame inside (legs inboard, 2 mm inside the frame opening), rivet the hinges "
        "and KB1 keepers through skin + angle, fit handles.",
        "3  Lower door: glazing unit - outer pane, EPDM spacer, inner pane, WR1 - clamped with 8 x M4 from outside.",
        "4  Side skins bottom to top, then the JS strips over the joints (acoustic sealant under each strip edge).",
        "5  Rear skins + JR strip, exhaust spigot and cable grommet; top skin last (it overlaps the side and rear skins).",
        "6  Skirts SK1-SK3 up into the base-rail rivnuts. Hang the doors on the lift-off hinges, rivet the latches to "
        "the right-hand skins and adjust them to pull the doors 3 mm onto the seal.",
    ], size=1.85, lh=3.2)
    details(sm, sh, 212, 16)
    title_block(sh, sm, 5, "19in rail, hardware, assembly, details", "as noted")
    return sh


def _post(sh, M, x0, y0, f=30.0, t=2.0, r=4.0):
    """SHS section (plan or elevation) with its corner radius, as a hatched ring."""
    def rs(cx, cy, half, rr):
        pts = []
        for qx, qy, a0 in ((cx + half - rr, cy - half + rr, -90), (cx + half - rr, cy + half - rr, 0),
                           (cx - half + rr, cy + half - rr, 90), (cx - half + rr, cy - half + rr, 180)):
            for i in range(7):
                a = math.radians(a0 + 15 * i)
                pts.append((qx + rr * math.cos(a), qy + rr * math.sin(a)))
        return pts
    c = (x0 + f / 2, y0 + f / 2)
    d = "M" + " L".join("%.2f %.2f" % M(*q) for q in rs(c[0], c[1], f / 2, r)) + " Z M" + \
        " L".join("%.2f %.2f" % M(*q) for q in rs(c[0], c[1], f / 2 - t, max(r - t, 0.3))) + " Z"
    sh.add('<path d="%s" fill="#eef1f4" fill-rule="evenodd" stroke="none"/>' % d)
    sh.add('<path d="%s" fill="url(#hatch)" fill-rule="evenodd" stroke="%s" stroke-width="0.3"/>' % (d, INK))


def _band(sh, M, x0, y0, x1, y1, fill, sw=0.2, c=INK):
    (a, b), (cx, cy) = M(x0, y0), M(x1, y1)
    sh.rect(min(a, cx), min(b, cy), abs(cx - a), abs(cy - b), sw=sw, fill=fill, c=c)


def _rivet(sh, M, u, v, inward, grip):
    """4.8 blind rivet, head on the outer face at (u, v), tail `grip` further in; inward = +-u or +-v."""
    ax, sg = inward
    for a0, a1, h in ((-1.4, 0.0, 4.75), (0.0, grip, 2.4), (grip, grip + 2.6, 3.2)):   # head, shank, blind bulb
        if ax == "v":
            _band(sh, M, u - h, v + sg * a0, u + h, v + sg * a1, RED, sw=0.1, c="#7b241c")
        else:
            _band(sh, M, u + sg * a0, v - h, u + sg * a1, v + h, RED, sw=0.1, c="#7b241c")


DETAIL_COL = OrderedDict([("skin", ("#c9ced4", "skin 1.2 steel")), ("mlv", ("#3a3d42", "MLV 3 (mass-loaded vinyl)")),
                          ("foam", ("#b9c3a9", "melamine foam 30")), ("angle", ("#7d8792", "DA angle / strip, 1.2 steel")),
                          ("hw", ("#9aa4ae", "hinge, latch, KB1, rivnut")), ("screw", ("#5c636a", "M6 screw")),
                          ("rivet", (RED, "rivet 4.8 blind"))])


def details(sm, sh, x, y):
    """Plan sections at a hinge (H) and a latch (L), a section through a skin joint (J), all 1:1, and the
    colour key. Fills x .. 408, y .. 232 (x = 212 leaves the left column to the tables)."""
    D = sm["D"]
    HW = SMP.RL.HW
    sk, ml, st = D["skin_t"], D["mlv_t"], D["strip_t"]
    s, f, ds, W = D["skin"], D["frame"], D["door_stiff"], D["ext_w"]
    fs = SMP.SM["frame_screw"]
    C = {k: v[0] for k, v in DETAIL_COL.items()}
    E = 70.0                                                  # drawn extent of skins in H

    def lbl(M, p0, p1, t, anchor="start"):
        a, b = M(*p0)
        c, d = M(*p1)
        sh.line(a, b, c, d, w=0.12)
        sh.circle(a, b, 0.35, sw=0, fill=INK)
        sh.text(c + (0.8 if anchor == "start" else -0.8), d + 0.6, t, size=1.6, anchor=anchor)

    # ---------------- H: hinge corner, plan (front at the bottom, left side at the left)
    ox, oy = x + 20, y + 84
    M = lambda u, v: (ox + u, oy - v)                        # noqa: E731
    WP.heading(sh, x, y, "H  HINGE CORNER - PLAN 1:1", size=2.2)
    sx0 = D["stiff_x0"]
    _band(sh, M, 0, s, sk, E, C["skin"])                     # side skin (starts behind the door)
    _band(sh, M, sk, s, s, E, C["mlv"])
    _band(sh, M, 0, 0, E, sk, C["skin"])                     # door skin
    _band(sh, M, 0, sk, sx0, s, C["mlv"])                    # door MLV, cut back under the DA angle
    _band(sh, M, sx0 + ds, sk, E, s, C["mlv"])
    _band(sh, M, sx0, sk, sx0 + ds, sk + st, C["angle"])                     # DA flat leg
    _band(sh, M, sx0 + ds - st, sk + st, sx0 + ds, sk + ds, C["angle"])      # DA upstand, inboard
    _band(sh, M, sx0 + ds, s, E, s + f, C["foam"], sw=0.1)                   # door foam
    _band(sh, M, s, s + f, s + f, E, C["foam"], sw=0.1)                      # side-bay foam behind the post
    _post(sh, M, s, s, f)
    kr, ht = HW["knuckle_r"], HW["hinge_t"]
    leaf = D["hw_x_left"] + HW["leaf_over"]
    _band(sh, M, -kr, -ht, leaf, 0, C["hw"])                 # door leaf
    _band(sh, M, -ht, -kr, 0, leaf, C["hw"])                 # frame leaf
    cx, cy = M(-kr, -kr)
    sh.circle(cx, cy, kr, sw=0.3, fill=C["hw"])
    sh.circle(cx, cy, 0.5, sw=0, fill=INK)
    _rivet(sh, M, D["hw_x_left"], -ht, ("v", 1), ht + sk + st)
    _rivet(sh, M, -ht, D["hw_y_side"], ("u", 1), ht + sk)
    a = D["hw_x_left"] + kr
    x0_, y0_ = M(-kr, -kr)
    x1_, _ = M(D["hw_x_left"], 0)
    WP.hdim(sh, x0_, x1_, M(0, -ht - 1.5)[1], y0_ + 11, "%.1f" % a, size=1.7)       # knuckle axis to rivet
    _, y1_ = M(0, D["hw_y_side"])
    WP.vdim(sh, y0_, y1_, M(-ht - 1.5, 0)[0], x0_ - 11, "%.1f" % a, size=1.7)
    px, py = M(s + f / 2, s + f / 2)
    sh.text(px, py + 0.6, "SHS 30", size=1.5, anchor="middle")
    lbl(M, (-ht / 2, D["hw_y_side"] + 5), (4, E + 6), "side leaf: 3 rivets behind the post (relieve the MLV + foam)")
    lbl(M, (sx0 + ds - st / 2, sk + ds - 2), (40, 44), "DA angle %gx%gx%g, bonded" % (ds, ds, st))
    lbl(M, (-kr - 3, -kr - 3), (-10, -24), "lift-off hinge, knuckle axis %g outside the corner" % kr)

    # ---------------- L: latch corner, plan (right side at the right)
    ox2, oy2 = 392.0, y + 106
    M2 = lambda u, v: (ox2 + (u - W), oy2 - v)               # noqa: E731
    WP.heading(sh, 306, y, "L  LATCH CORNER - PLAN 1:1", size=2.2)
    u0, V2 = W - 80, 100.0
    x1 = D["stiff_x1"]
    _band(sh, M2, W - sk, s, W, V2, C["skin"])
    _band(sh, M2, W - s, s, W - sk, V2, C["mlv"])
    _band(sh, M2, u0, 0, W, sk, C["skin"])
    _band(sh, M2, x1, sk, W, s, C["mlv"])
    _band(sh, M2, u0, sk, x1 - ds, s, C["mlv"])
    _band(sh, M2, x1 - ds, sk, x1, sk + st, C["angle"])
    _band(sh, M2, x1 - ds, sk + st, x1 - ds + st, sk + ds, C["angle"])
    _band(sh, M2, u0, s, x1 - ds, s + f, C["foam"], sw=0.1)
    _band(sh, M2, W - s - f, s + f, W - s, V2, C["foam"], sw=0.1)
    _post(sh, M2, W - s - f, s, f)
    hx, yh = D["hw_x_right"], D["hw_y_side"]
    kg, kb = HW["keeper_gap"], HW["keeper_leg_b"]
    cv, cw_, _ = HW["catch"]
    _band(sh, M2, hx - 14, -st, W + kg + st, 0, C["hw"])                    # KB1 leg A on the door face
    _band(sh, M2, W + kg, -st, W + kg + st, cv - cw_ / 2, C["hw"])          # KB1 leg B, slot cut away
    _band(sh, M2, W + kg, cv + cw_ / 2, W + kg + st, kb, C["hw"])
    lb0, lb1 = yh + HW["latch_holes"][0][0] - 12, yh + HW["latch_holes"][2][0] + 15
    _band(sh, M2, W, lb0, W + 1.5, lb1, C["hw"])                            # latch base plate
    _band(sh, M2, W + 1.5, lb0 + 4, W + 13, lb1 - 2, "#dfe3e8", sw=0.15)     # toggle lever
    _band(sh, M2, W + 3.5, cv - 1, W + 5.5, lb0 + 4, C["hw"], sw=0.15)      # hook arm
    _band(sh, M2, W + kg + 0.3, cv - 1, W + 5.5, cv + 1, C["hw"], sw=0.15)  # hook tip in the slot
    _rivet(sh, M2, hx, -st, ("v", 1), 3 * st)
    for dy in sorted(set(q[0] for q in HW["latch_holes"])):
        _rivet(sh, M2, W + 1.5, yh + dy, ("u", -1), 1.5 + sk)
    lbl(M2, (W + 8, lb1 - 3), (W + 12, V2 + 3.5), "toggle latch, 4 rivets in the side skin", anchor="end")
    lbl(M2, (W + 3, cv), (W + 12, -9), "its hook in the KB1 slot pulls the door onto the seal", anchor="end")
    lbl(M2, (hx - 8, -st / 2), (W - 64, -14), "KB1 keeper: 2 rivets through door + DA", anchor="start")
    sh.text(306, oy2 + 20.5, "Latch rivets %.1f and %.1f behind the door face; KB1 rivets %.1f in from the side." % (
        yh + HW["latch_holes"][0][0], yh + HW["latch_holes"][2][0], W - hx), size=1.6)

    # ---------------- J: skin joint on a rail, section through a strip screw (outside at the left)
    y3 = y + 136
    WP.heading(sh, x, y3, "J  SKIN JOINT ON A RAIL - SECTION THROUGH A STRIP SCREW 1:1", size=2.2)
    ox3, oz = x + 82, y3 + 42
    M3 = lambda u, v: (ox3 + u, oz - v)                      # noqa: E731  u = 0 on the rail's outer face
    V3, rv, sw2 = 34.0, fs / 2.0, D["strip_w"] / 2.0
    _band(sh, M3, 0.3, f / 2 + 0.5, f, V3, C["foam"], sw=0.1)
    _band(sh, M3, 0.3, -V3, f, -f / 2 - 0.5, C["foam"], sw=0.1)
    _post(sh, M3, 0, -f / 2, f)
    for sg in (1, -1):                                       # MLV, skins and strip all clear the screw (D8)
        lo, hi = sorted((sg * rv, sg * V3))
        _band(sh, M3, -ml, lo, 0, hi, C["mlv"])
        _band(sh, M3, -ml - sk, lo, -ml, hi, C["skin"])
        lo, hi = sorted((sg * rv, sg * sw2))
        _band(sh, M3, -ml - sk - st, lo, -ml - sk, hi, C["angle"])
    _band(sh, M3, -1.0, -6.5, 0, 6.5, C["hw"], sw=0.15)     # rivnut flange, bedded in the MLV
    _band(sh, M3, 0, -4.5, 13, 4.5, C["hw"], sw=0.15)       # rivnut body in its D9 hole
    uh = -ml - sk - st
    _band(sh, M3, uh - 3.3, -6.5, uh, 6.5, C["screw"])      # flanged button head
    _band(sh, M3, uh, -3, uh + 20, 3, C["screw"])           # M6 x 20
    lbl(M3, (uh - 3.3, 4), (-22, 12), "M6 x 20 flanged button head, snug (~3 N m)", anchor="end")
    lbl(M3, (uh + st / 2, 20), (-22, 20), "strip JS / JR %gx%g, D8 at each screw" % (D["strip_w"], st), anchor="end")
    lbl(M3, (-ml - sk / 2, 29), (-22, 28), "skins %g: 1 mm joint gap, R4 notch each side" % sk, anchor="end")
    lbl(M3, (-ml / 2, -26), (-22, -22), "MLV %g, one piece, D8 hole: the gasket" % ml, anchor="end")
    lbl(M3, (uh, -sw2 + 1), (-22, -30), "acoustic sealant under both strip edges", anchor="end")
    lbl(M3, (6, -3.5), (36, -6), "M6 steel rivnut, flat head", anchor="start")
    lbl(M3, (f - 1, 9), (36, 8), "rail SHS 30x30x2", anchor="start")
    lbl(M3, (f / 2, 25), (36, 24), "bay foam", anchor="start")

    # ---------------- colour key
    kx, ky = 352.0, y3 + 8
    sh.text(kx, ky, "KEY", size=1.9, weight="bold")
    for i, (k, (col, t)) in enumerate(DETAIL_COL.items()):
        yy = ky + 3 + i * 4.2
        sh.rect(kx, yy, 6, 2.6, sw=0.12, fill=col)
        sh.text(kx + 7.5, yy + 2.1, t, size=1.6)
    yy = ky + 3 + len(DETAIL_COL) * 4.2
    sh.rect(kx, yy, 6, 2.6, sw=0.12, fill="url(#hatch)")
    sh.text(kx + 7.5, yy + 2.1, "frame SHS 30x30x2 (weld pack)", size=1.6)
    return oz + V3 + 4


def sheet6(sm, nests):
    sh = Svg()
    WP.border(sh)
    WP.heading(sh, 14, 16, "NESTING ON %g x %g BLANKS (MaxRects, %g mm gap, %g mm margin) - cad/dxf/nest/" % (
        BLANK[0], BLANK[1], GAP, MARGIN), size=2.5)
    k = 1 / 16.0
    bw, bh = BLANK[0] * k, BLANK[1] * k
    x, y = 14.0, 22.0
    i = 0
    for key, sheets in nests.items():
        for j, sheet in enumerate(sheets):
            if x + bw > 408:
                x, y = 14.0, y + bh + 9
            if y + bh > 238 and x + bw > 270:
                break
            sh.rect(x, y, bw, bh, sw=0.25, fill="#ffffff")
            for p, px, py, rot in sheet:
                w, h = (p.h, p.w) if rot else (p.w, p.h)
                rx, ry = x + px * k, y + (BLANK[1] - py - h) * k
                sh.rect(rx, ry, w * k, h * k, sw=0.12, fill="#dfe6ee" if p.mat != "ss12" else "#e9e2cf")
                if w * k < len(p.id) * 1.1 + 0.6 and h * k > w * k:          # narrow and tall: label up the part
                    fs_ = min(2.0, max(1.0, w * k * 0.75))
                    sh.text(rx + w * k / 2 + fs_ * 0.35, ry + h * k / 2, p.id, size=fs_, anchor="middle", rot=-90)
                else:
                    sh.text(rx + w * k / 2, ry + h * k / 2 + 0.7, p.id, size=min(2.0, max(1.1, h * k / 3)),
                            anchor="middle")
            used = sum(p.w * p.h for p, *_ in sheet) / (BLANK[0] * BLANK[1]) * 100
            sh.text(x, y + bh + 3.2, "%s sheet %d - %.0f%% used" % (mat_tag(key).replace("_", " "), j + 1, used),
                    size=1.8)
            x += bw + 6
            i += 1
    nb = sum(len(v) for kk, v in nests.items() if kk[1] == sm["D"]["skin_t"] and "Stainless" not in kk[0])
    WP.heading(sh, 338, 26, "NOTES", size=2.4)
    WP.paragraph(sh, 338, 31, [
        "Blanks are the %g x %g sheet / bed size. Each nest" % BLANK,
        "DXF has the parts on CUT and the blank on SHEET.",
        "",
        "%d steel %g blanks: the big skins cannot share a" % (nb, sm["D"]["skin_t"]),
        "blank (no two fit together), so their offcuts",
        "carry the strips, stiffeners, keepers and skirts.",
        "",
        "PD1 (8 mm), PC1 (3 mm) and RR1 (2 mm) are small:",
        "cut them from offcuts or order them as cut parts;",
        "their nests are shown for completeness.",
        "",
        "Parts may turn 90 deg (no grain on coated steel).",
        "%g mm between parts, %g mm from the blank edge." % (GAP, MARGIN),
    ], size=1.8, lh=3.0)
    title_block(sh, sm, 6, "Nesting on 1200 x 800 blanks", "1:16")
    return sh


# ======================================================================= markdown
def write_md(sm, nests, files):
    D = sm["D"]
    HW = SMP.RL.HW
    L = ["# SRA-16 sheet-metal parts (laser cut)", "",
         "| | |", "|---|---|",
         "| Drawing | %s, %d sheets (`drawings/%s.pdf`) |" % (SMP.DOC_NO, N_SHEETS, SMP.DOC_NO),
         "| Generated | `tools/make_sheet_pack.py` from `rack_layout.py` v%s on %s |" % (D.get("version", ""), TODAY),
         "| DXF | `cad/dxf/cut/` (cut geometry only), `cad/dxf/info/` (+ bend lines, ID etch, notes), "
         "`cad/dxf/nest/` (nested %gx%g blanks), all zipped in `cad/dxf/SRA16_sheet_metal_DXF.zip` |" % BLANK,
         "| Size limit | every flat blank fits %.0f x %.0f (checked) |" % (D["sheet_max_l"], D["sheet_max_w"]),
         "| Skins | %.1f mm steel, powder coated, 3 mm MLV bonded inside; the welded frame is unchanged |" % D["skin_t"],
         "| Hold point | %s move with the AC grille split: cut them after tape check M3 (`docs/DESIGN.md` §3). "
         "The other %d part types can be cut now. |" % (", ".join(sm["hold"]), len(sm["parts"]) - len(sm["hold"])),
         "", "## What changed", "",
         "The 15 mm ply skins are now laser-cut %.1f mm steel. The frame and the inside of the cabinet are unchanged, "
         "so the outside shrinks to %.1f W x %.1f D x %.1f H mm." % (D["skin_t"], D["ext_w"], D["ext_d"], D["ext_h"]),
         "",
         "- **Split skins.** The side skins are split into %d pieces, on the mid and shelf rails. The rear skin is split "
         "into %d, on the shelf rail. Every piece fits %.0f x %.0f." % (len(D["side_splits"]) + 1, len(D["rear_splits"]) + 1,
                                                                    D["sheet_max_l"], D["sheet_max_w"]),
         "- **Joint strips.** Each joint sits on a rail centreline with a 1 mm gap, and both skin edges have R%g "
         "notches round each strip screw. A %g x %g strip covers the joint and is screwed through the notches into "
         "the rail's rivnuts (detail J, sheet 5). The MLV behind stays one piece per side." % (
             SMP.SM["frame_screw"] / 2.0, D["strip_w"], D["strip_t"]),
         "- **Doors.** The doors are flat skins stiffened by a bonded 20 x 20 angle frame. The hinges and toggle latches "
         "are riveted through the skins, so the frame needs **no extra holes**.",
         "- **Acoustics.** %.1f mm steel plus MLV weighs about as much as 15 mm ply plus MLV. It has no coincidence dip "
         "in the speech band, so the insertion loss is the same or slightly better." % D["skin_t"],
         "", "## Parts", "", "| ID | Qty | Part | Material | t mm | Flat mm | Holes | Bends | Fits |",
         "|---|---:|---|---|---:|---|---:|---:|---|"]
    for p in sm["parts"]:
        L.append("| %s | %d | %s | %s | %g | %.1f x %.1f | %d | %d | %s |" % (
            p.id, p.qty, p.name, SMP.MATERIALS[p.mat]["name"], p.t, p.w, p.h, len(p.holes) + len(p.squares),
            len(p.bends), p.where))
    L += ["", "## Holes", "",
          "| Hole | Size | For |", "|---|---|---|",
          "| Frame screw | D%g | M6 x 20 flanged button head into a frame rivnut. The hole is 2 mm oversize for the "
          "frame tolerance. |" % SMP.SM["frame_screw"],
          "| Rivet | D%g | 4.8 mm blind rivet: hinges, latch bases, keepers |" % SMP.SM["rivet"],
          "| M5 | D%g | pull handles, exhaust spigot flange |" % SMP.SM["m5"],
          "| M4 | D%g | window clamp, cable grommet |" % SMP.SM["m4"],
          "| Rail bolt | D%g | M6 through the 19in rail and rail spacer into the upright rivnut |" % SMP.SM["rail_bolt"],
          "| Tap M8 | D%g | castor pads (tap after cutting) |" % SMP.SM["tap_m8"],
          "| Cage nut | %g square | EIA-310, 3 per U |" % SMP.SM["sq_hole"],
          "| Joint notch | R%g edge notch | split skins, centred 0.5 mm beyond the edge: clearance for the joint "
          "strip's M6 screws |" % (SMP.SM["frame_screw"] / 2.0),
          "", "## Hardware (confirm before cutting)", "",
          "The hardware holes suit the parts below. If yours differ, change `HW` in `rack_layout.py` and re-run.", "",
          "- **Hinges:** lift-off butt hinges, %d off. On both leaves the rivets sit **%.1f mm from the knuckle "
          "axis**. The axis is on the front-left corner. Drill the hinge leaves to suit if needed." % (
              len(D["hinge_z_lower"]) + len(D["hinge_z_upper"]), D["hw_x_left"] + HW["knuckle_r"]),
          "- **Latches:** adjustable toggle latches, %d off, riveted to the right-hand side skins. The hook engages "
          "the slot in the KB1 keeper on the door." % (len(D["latch_z_lower"]) + len(D["latch_z_upper"])),
          "- **Window:** 2 x 6 mm polycarbonate, %g x %g, with a 10 mm EPDM spacer frame. Clamp the stack to the lower "
          "door with the WR1 frame and 8 x M4 x 35." % (D["win_w"] + 40, D["win_h"] + 40),
          "- **Rear skin:** a D150 exhaust spigot (4 x M5 on PCD %g) and a 200 x 40 brush cable grommet." % (
              SMP.SM["spigot_pcd"]),
          "", "## Nesting (%g x %g blanks)" % BLANK, "",
          "| Material | Blanks | Parts |", "|---|---:|---|"]
    for key, sheets in nests.items():
        L.append("| %s %g mm | %d | %s |" % (key[0], key[1], len(sheets),
                                              "; ".join(" ".join(p.id for p, *_ in s) for s in sheets)))
    L += ["", "## Assembly", "",
          "1. **Coat, then line.**",
          "   - Powder coat all the parts.",
          "   - Bond the MLV inside the skins and doors. Punch it D8 at the frame screws: it is the gasket over the "
          "rivnut flanges. Cut it back 3 mm round rivets, M4/M5 holes and cut-outs.",
          "   - Snug the M6 frame screws (about 3 N m); the MLV must not squeeze out.",
          "2. **Doors.**",
          "   1. Bond the stiffener frame (DA1-DA5): legs inboard, 2 mm inside the frame opening.",
          "   2. Rivet the hinges and the KB1 keepers through the skin and the angle.",
          "   3. Fit the pull handles.",
          "   4. Fit the glazing unit in the lower door.",
          "3. **Side skins.**",
          "   1. Fit the pieces bottom to top.",
          "   2. Fit the JS strips over the joints with acoustic sealant under each strip edge.",
          "4. **Rear skins.**",
          "   1. Fit both pieces and the JR strip.",
          "   2. Fit the exhaust spigot and the cable grommet.",
          "5. **Top skin.** Fit it last; it overlaps the side and rear skins.",
          "6. **Skirts.** Screw SK1-SK3 up into the base-rail rivnuts.",
          "7. **Hang the doors and fit the latches.**",
          "   1. Hang the doors on the lift-off hinges.",
          "   2. Rivet the latches to the pre-cut holes in the right-hand skins.",
          "   3. Adjust each latch so it pulls its door onto the seal (about 3 mm compression).",
          "",
          "## Checks built into the generator", "",
          "- Every flat blank fits %.0f x %.0f." % (D["sheet_max_l"], D["sheet_max_w"]),
          "- Every frame rivnut used for a skin, strip or skirt is matched by a hole in a sheet part. Mirror twins "
          "(joint strips, side skirts) are verified hole-for-hole before they are merged.",
          "- Holes clear the part edges by 1.5 t (minimum 2.5 mm) and clear bend zones by 1.5 t.",
          "- Holes do not overlap, and the rack-rail bolt holes match all four uprights.",
          "- Split skins are notched round every joint-strip screw.",
          "", "## Files", ""]
    L += ["- `%s`" % f for f in files]
    with open(os.path.join(ROOT, "docs", "SHEET_METAL.md"), "w") as fh:
        fh.write("\n".join(L) + "\n")


# ======================================================================= main
def main(argv):
    do_pdf = "--no-pdf" not in argv
    overrides = {k: float(v) for k, v in (a.split("=", 1) for a in argv if "=" in a)}
    sm = SMP.build(overrides)
    sm["D"]["version"] = SMP.RL.VERSION
    sm["hold"] = SMP.tape_hold(overrides)                  # parts that move with tape check M3
    for p in sm["parts"]:
        if p.id in sm["hold"]:
            p.hold = "M3"
            p.notes.append("HOLD: moves with the AC grille split (tape check M3) - cut it after M3 is measured.")
    probs = SMP.check(sm)
    for p in probs:
        print("PROBLEM:", p)
    out = os.path.join(ROOT, "cad", "dxf")
    for sub in ("cut", "info", "nest"):
        d = os.path.join(out, sub)
        if os.path.isdir(d):
            for fn in os.listdir(d):
                if fn.endswith(".dxf"):
                    os.remove(os.path.join(d, fn))
    files = write_dxfs(sm, out)
    nests = nest(sm)
    files += write_nests(nests, out)
    write_csvs(sm, nests)
    zp = os.path.join(out, "SRA16_sheet_metal_DXF.zip")
    entries = [(f, os.path.relpath(f, out)) for f in files] + [
        (os.path.join(ROOT, "bom", n), n) for n in ("sheet_metal_parts.csv", "sheet_metal_nesting.csv")]
    with zipfile.ZipFile(zp, "w") as z:
        for f, arc in entries:
            zi = zipfile.ZipInfo(arc, date_time=(2026, 1, 1, 0, 0, 0))   # fixed stamp: reproducible zip
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            with open(f, "rb") as fh:
                z.writestr(zi, fh.read())
    ddir = os.path.join(ROOT, "drawings")
    ids = [p.id for p in sm["parts"]]
    skins = [i for i in ids if i[:2] in ("SL", "SR", "RP", "TP")]
    mid = [i for i in ids if i[:2] in ("DL", "DU", "JS", "JR") or i in ("DA1", "DA2", "DA3", "DA4")]
    small = [i for i in ids if i not in skins + mid and i != "RR1"]
    sheets = [sheet1(sm, nests),
              sheet_parts(sm, skins, 2, "Flat patterns - side, rear and top skins"),
              sheet_parts(sm, mid, 3, "Flat patterns - doors, joint strips, door stiffeners"),
              sheet_parts(sm, small, 4, "Flat patterns - stiffeners, keepers, window, skirts, tray, plates"),
              sheet5(sm), sheet6(sm, nests)]
    svgs = []
    for i, s in enumerate(sheets):
        fn = os.path.join(ddir, "%s_s%d.svg" % (SMP.DOC_NO, i + 1))
        with open(fn, "w") as fh:
            fh.write(s.svg())
        svgs.append(fn)
    rel = ["cad/dxf/SRA16_sheet_metal_DXF.zip", "cad/dxf/cut/<ID>.dxf (%d parts)" % len(ids),
           "cad/dxf/info/<ID>.dxf", "cad/dxf/nest/*.dxf (%d blanks)" % sum(len(v) for v in nests.values()),
           "bom/sheet_metal_parts.csv", "bom/sheet_metal_nesting.csv", "drawings/%s_s1..s%d.svg" % (SMP.DOC_NO, N_SHEETS)]
    if do_pdf:
        pdf = os.path.join(ddir, "%s.pdf" % SMP.DOC_NO)
        subprocess.run(["node", os.path.join(HERE, "render", "svg2pdf.mjs"), pdf] + svgs, check=True)
        rel.insert(0, "drawings/%s.pdf" % SMP.DOC_NO)
    write_md(sm, nests, rel)
    tot = sum(p.qty for p in sm["parts"])
    print("sheet metal: %d part types, %d pieces, %.1f kg; blanks %s; %s" % (
        len(ids), tot, sum(p.qty * p.mass() for p in sm["parts"]),
        ", ".join("%s x%d" % (mat_tag(k), len(v)) for k, v in nests.items()), "check OK" if not probs else "PROBLEMS"))
    return 0 if not probs else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
