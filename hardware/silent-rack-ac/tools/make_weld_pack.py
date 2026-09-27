#!/usr/bin/env python3
"""
Fabrication pack for the SRA-16 welded steel frame - drawing CP-SRA16-FRM-001.
Generated from rack_layout.py (via tools/weldment.py), so it tracks the CAD.

Outputs (relative to hardware/silent-rack-ac/):
  bom/frame_cut_list.csv, bom/frame_drilling.csv, bom/frame_weld_schedule.csv, bom/frame_nesting.csv
  docs/FRAME_WELD_PLAN.md                         procedure: WPS, sequence, checks, estimates
  drawings/CP-SRA16-FRM-001_s1..s6.svg            A3 sheets
  drawings/CP-SRA16-FRM-001.pdf                   the six sheets as one PDF
  cad/exports/SRA16_frame_weldment.step           weldment: hollow SHS with radii, holes, plates
  cad/exports/frame_members/<mark>.step           one per mark, datum end at origin, along +X (tube laser)

Usage: python3 tools/make_weld_pack.py [--no-step] [--no-pdf] [key=value ...]
Prices and hours are indicative (AUD, Sept 2026) for budgeting only.
"""
import csv
import datetime
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import weldment as WM  # noqa: E402

A3 = (420.0, 297.0)
N_SHEETS = 6
TODAY = datetime.date.today().isoformat()
INK, THIN = "#15181c", "#5b6168"
FILL = {"post": "#dde2e8", "rail": "#dde2e8", "upright": "#dde2e8", "ledge": "#aeb8c2", "pad": "#8f99a3",
        "spacer": "#f1f3f5"}
STAGE_COL = {"SA-L": (0.20, 0.45, 0.80), "SA-R": (0.18, 0.62, 0.36), "BOX": (0.90, 0.52, 0.14),
             "BENCH": (0.55, 0.57, 0.60), "FINAL": (0.35, 0.37, 0.40), "LOOSE": (0.80, 0.80, 0.82)}

# indicative AUD (Sept 2026) - budgeting only
PRICE = {"shs_bar": 52.0, "fb_bar": 22.0, "pad_fb_m": 32.0, "cap_fb_m": 6.0, "rivnut": 0.35, "m8": 0.40,
         "consumables": 60.0, "coat": 320.0, "rate": 110.0}


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ======================================================================= SVG
class Svg:
    def __init__(self):
        self.el = []

    def add(self, s):
        self.el.append(s)

    def line(self, x1, y1, x2, y2, w=0.25, c=INK, dash=None, cap="butt"):
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        self.add('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width="%.2f" '
                 'stroke-linecap="%s"%s/>' % (x1, y1, x2, y2, c, w, cap, d))

    def rect(self, x, y, w, h, sw=0.3, fill="none", c=INK, dash=None, rx=0):
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        self.add('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" rx="%.2f" fill="%s" stroke="%s" '
                 'stroke-width="%.2f"%s/>' % (x, y, w, h, rx, fill, c, sw, d))

    def circle(self, cx, cy, r, sw=0.2, fill="none", c=INK, dash=None):
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        self.add('<circle cx="%.2f" cy="%.2f" r="%.2f" fill="%s" stroke="%s" stroke-width="%.2f"%s/>'
                 % (cx, cy, r, fill, c, sw, d))

    def poly(self, pts, w=0.2, c=INK, fill="none", close=False, dash=None, marker=None):
        d = "M" + " L".join("%.2f %.2f" % p for p in pts) + (" Z" if close else "")
        extra = ' stroke-dasharray="%s"' % dash if dash else ""
        if marker:
            extra += ' marker-end="url(#%s)"' % marker
        self.add('<path d="%s" fill="%s" stroke="%s" stroke-width="%.2f" stroke-linejoin="round"%s/>'
                 % (d, fill, c, w, extra))

    def path(self, d, w=0.2, c=INK, fill="none"):
        self.add('<path d="%s" fill="%s" stroke="%s" stroke-width="%.2f"/>' % (d, fill, c, w))

    def text(self, x, y, s, size=2.2, anchor="start", weight="normal", c=INK, rot=None, italic=False):
        tr = ' transform="rotate(%.1f %.2f %.2f)"' % (rot, x, y) if rot is not None else ""
        st = ' font-style="italic"' if italic else ""
        self.add('<text x="%.2f" y="%.2f" font-size="%.2f" text-anchor="%s" font-weight="%s" fill="%s"%s%s>%s</text>'
                 % (x, y, size, anchor, weight, c, st, tr, esc(s)))

    def arrow(self, x1, y1, x2, y2, w=0.18, c=INK):
        self.add('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width="%.2f" '
                 'marker-end="url(#aDim)"/>' % (x1, y1, x2, y2, c, w))

    def svg(self):
        head = ('<svg xmlns="http://www.w3.org/2000/svg" width="420mm" height="297mm" viewBox="0 0 420 297" '
                'font-family="Arial, Helvetica, sans-serif">\n<defs>\n'
                '<marker id="aDim" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="3.2" markerHeight="3.2" '
                'orient="auto-start-reverse"><path d="M0 1.5 L10 5 L0 8.5 z" fill="#15181c"/></marker>\n'
                '<pattern id="hatch" width="1.6" height="1.6" patternUnits="userSpaceOnUse" '
                'patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="1.6" stroke="#6d747c" '
                'stroke-width="0.25"/></pattern>\n'
                '<pattern id="ply" width="2.2" height="2.2" patternUnits="userSpaceOnUse" '
                'patternTransform="rotate(-35)"><line x1="0" y1="0" x2="0" y2="2.2" stroke="#b58a4a" '
                'stroke-width="0.3"/></pattern>\n'
                '</defs>\n<rect x="0" y="0" width="420" height="297" fill="#ffffff"/>\n')
        return head + "\n".join(self.el) + "\n</svg>\n"


# ---------------------------------------------------------------- drawing furniture
def border(sh):
    sh.rect(8, 8, 404, 281, sw=0.6)


def title_block(sh, wm, n, title, scale):
    D = wm["D"]
    tb = (272, 247, 140, 42)
    sh.rect(*tb, sw=0.5, fill="#ffffff")
    rows = [
        ("PROJECT", "SRA-16 Silent AC Rack - welded %s frame" % wm["sec_shs"].replace(" SHS", "")),
        ("TITLE", title),
        ("DOC NO.", "%s   SHEET %d OF %d   REV %s" % (WM.DOC_NO, n, N_SHEETS, WM.REV)),
        ("SCALE", "%s @ A3   UNITS mm   LAYOUT v%s" % (scale, D.get("version", ""))),
        ("DATE", "%s   DRAWN Claude (AI) for Carbon Project" % TODAY),
        ("STATUS", "FOR FABRICATION after hold point H1 (AC grille split M3)"),
    ]
    for i, (k, v) in enumerate(rows):
        y = tb[1] + 6.2 + i * 6.3
        sh.text(tb[0] + 2, y, k, size=1.9, weight="bold")
        sh.text(tb[0] + 19, y, v, size=2.15)
        if i:
            sh.line(tb[0], y - 4.6, tb[0] + tb[2], y - 4.6, w=0.15)
    sh.line(tb[0] + 17, tb[1], tb[0] + 17, tb[1] + tb[3], w=0.15)


def fit_text(s, width, size):
    """Shrink the font so s fits width (Arial ~0.5 em per char)."""
    need = len(str(s)) * 0.5 * size
    return size if need <= width else max(1.45, size * width / need)


def table(sh, x, y, cols, rows, head=None, size=2.0, rh=3.7, zebra=True, head_fill="#e6ebf0"):
    """cols = [(width, 'l'|'c'|'r'), ...]; returns bottom y."""
    W = sum(c[0] for c in cols)
    allrows = ([head] if head else []) + list(rows)
    for i, r in enumerate(allrows):
        yy = y + i * rh
        if head and i == 0:
            sh.rect(x, yy, W, rh, sw=0.0, fill=head_fill, c="none")
        elif zebra and i % 2 == 0:
            sh.rect(x, yy, W, rh, sw=0.0, fill="#f5f7f9", c="none")
        cx = x
        for (w, al), cell in zip(cols, r):
            fs = fit_text(cell, w - 1.2, size)
            if al == "l":
                sh.text(cx + 0.7, yy + rh - 1.05, cell, size=fs, weight="bold" if (head and i == 0) else "normal")
            elif al == "r":
                sh.text(cx + w - 0.7, yy + rh - 1.05, cell, size=fs, anchor="end",
                        weight="bold" if (head and i == 0) else "normal")
            else:
                sh.text(cx + w / 2, yy + rh - 1.05, cell, size=fs, anchor="middle",
                        weight="bold" if (head and i == 0) else "normal")
            cx += w
    H = rh * len(allrows)
    sh.rect(x, y, W, H, sw=0.3)
    for i in range(1, len(allrows)):
        sh.line(x, y + i * rh, x + W, y + i * rh, w=0.1, c="#9aa1a8")
    cx = x
    for w, _ in cols[:-1]:
        cx += w
        sh.line(cx, y, cx, y + H, w=0.1, c="#9aa1a8")
    return y + H


def heading(sh, x, y, s, size=2.8):
    sh.text(x, y, s, size=size, weight="bold")


def paragraph(sh, x, y, lines, size=2.05, lh=3.3, bold_first=False):
    for i, t in enumerate(lines):
        sh.text(x, y + i * lh, t, size=size, weight="bold" if (bold_first and i == 0) else "normal")
    return y + len(lines) * lh


def hdim(sh, x1, x2, yref, ydim, text, size=2.0, above=True):
    s = -1 if ydim < yref else 1
    for x in (x1, x2):
        sh.line(x, yref + 0.8 * s, x, ydim + 1.2 * s, w=0.12)
    sh.add('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width="0.18" '
           'marker-start="url(#aDim)" marker-end="url(#aDim)"/>' % (x1, ydim, x2, ydim, INK))
    sh.text((x1 + x2) / 2, ydim - 0.8 if above else ydim + 2.6, text, size=size, anchor="middle")


def vdim(sh, y1, y2, xref, xdim, text, size=2.0):
    s = -1 if xdim < xref else 1
    for y in (y1, y2):
        sh.line(xref + 0.8 * s, y, xdim + 1.2 * s, y, w=0.12)
    sh.add('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width="0.18" '
           'marker-start="url(#aDim)" marker-end="url(#aDim)"/>' % (xdim, y1, xdim, y2, INK))
    sh.text(xdim - 0.9, (y1 + y2) / 2, text, size=size, anchor="middle", rot=-90)


def ordinate(sh, xref, xdim, ys, labels, side="left", size=1.9, min_gap=2.6):
    """Ordinate dimensions: extension lines from xref to xdim, values beside the line (de-overlapped)."""
    pairs = sorted(zip(ys, labels), key=lambda q: -q[0])          # bottom (largest y) first
    placed = []
    for y, lab in pairs:
        ty = y
        if placed and placed[-1] - ty < min_gap:
            ty = placed[-1] - min_gap
        placed.append(ty)
        sh.line(xref, y, xdim, y, w=0.12)
        if side == "left":
            sh.line(xdim, y, xdim - 1.6, ty, w=0.12)
            sh.text(xdim - 2.0, ty + 0.7, lab, size=size, anchor="end")
        else:
            sh.line(xdim, y, xdim + 1.6, ty, w=0.12)
            sh.text(xdim + 2.0, ty + 0.7, lab, size=size, anchor="start")


def balloon(sh, bx, by, text, ax, ay, r=3.0):
    d = math.hypot(ax - bx, ay - by)
    if d > r:
        ex, ey = bx + (ax - bx) * r / d, by + (ay - by) * r / d
        sh.line(ex, ey, ax, ay, w=0.15)
        sh.circle(ax, ay, 0.45, sw=0, fill=INK)
    sh.circle(bx, by, r, sw=0.28, fill="#ffffff")
    sh.text(bx, by + 0.85, text, size=fit_text(text, 2 * r - 0.8, 2.3), anchor="middle", weight="bold")


def jtag(sh, x, y, text, fill="#fff3b0"):
    w = 1.25 * len(text) + 1.6
    sh.rect(x - w / 2, y - 1.6, w, 3.2, sw=0.2, fill=fill, rx=0.6)
    sh.text(x, y + 0.75, text, size=1.95, anchor="middle", weight="bold")


def weld_symbol(sh, jx, jy, rx, ry, ref=16, kind="fillet", size="3", length=None, all_round=False,
                flush=False, finish=None, both=False, tail=None, other=False):
    """AS 1101.3 style: arrow from the reference line to the joint (jx, jy); symbol below the line = arrow side."""
    sh.line(rx, ry, jx, jy, w=0.2)
    ang = math.atan2(jy - ry, jx - rx)
    ah = [(jx, jy), (jx - 2.2 * math.cos(ang - 0.3), jy - 2.2 * math.sin(ang - 0.3)),
          (jx - 2.2 * math.cos(ang + 0.3), jy - 2.2 * math.sin(ang + 0.3))]
    sh.poly(ah, w=0.1, fill=INK, close=True)
    d = 1 if jx < rx else -1                     # reference line runs away from the arrow
    x2 = rx + d * ref
    sh.line(rx, ry, x2, ry, w=0.25)
    if all_round:
        sh.circle(rx, ry, 1.1, sw=0.22, fill="#ffffff")
    cx = (rx + x2) / 2 - 1.5
    h = 2.6

    def one(sgn):                                # sgn +1 below (arrow side), -1 above (other side)
        if kind == "fillet":
            sh.poly([(cx, ry), (cx, ry + sgn * h), (cx + h, ry)], w=0.22, close=True)
        elif kind == "square":
            sh.line(cx + 0.4, ry, cx + 0.4, ry + sgn * h, w=0.22)
            sh.line(cx + 1.8, ry, cx + 1.8, ry + sgn * h, w=0.22)
        elif kind == "flare":
            sh.line(cx, ry, cx, ry + sgn * h, w=0.22)
            sh.path("M %.2f %.2f Q %.2f %.2f %.2f %.2f" % (cx + h, ry, cx + 0.4, ry, cx + 0.4, ry + sgn * h), w=0.22)
        if size:
            sh.text(cx - 0.6, ry + sgn * h * 0.5 + 0.7, size, size=1.9, anchor="end")
        if length:
            sh.text(cx + h + 0.6, ry + sgn * h * 0.5 + 0.7, length, size=1.9, anchor="start")
        if flush:
            yy = ry + sgn * (h + 0.9)
            sh.line(cx - 0.4, yy, cx + h + 0.4, yy, w=0.22)
            if finish:
                sh.text(cx + h / 2, yy + (2.3 if sgn > 0 else -0.6), finish, size=1.8, anchor="middle")
    one(1 if not other else -1)
    if both:
        one(-1)
    if tail:
        sh.line(x2, ry, x2 + d * 1.8, ry - 1.4, w=0.2)
        sh.line(x2, ry, x2 + d * 1.8, ry + 1.4, w=0.2)
        sh.text(x2 + d * 2.4, ry + 0.7, tail, size=1.8, anchor="start" if d > 0 else "end")


# ---------------------------------------------------------------- orthographic view of axis-aligned members
VIEWS = {   # (u axis, sign), (v axis, sign), (depth axis, +1 if larger coordinate is nearer)
    "front": ((0, 1), (2, 1), (1, -1)),
    "rear": ((0, -1), (2, 1), (1, 1)),
    "right": ((1, 1), (2, 1), (0, 1)),       # from +X: front on the left
    "left": ((1, -1), (2, 1), (0, -1)),      # from -X: front on the right
    "top": ((0, 1), (1, 1), (2, 1)),         # plan, rear at the top
}


class View:
    def __init__(self, sh, kind, scale, left, bottom, bbox):
        (self.ua, self.us), (self.va, self.vs), (self.da, self.ds) = VIEWS[kind]
        self.sh, self.k = sh, float(scale)
        us = [self.us * bbox[0][self.ua], self.us * bbox[1][self.ua]]
        vs = [self.vs * bbox[0][self.va], self.vs * bbox[1][self.va]]
        self.u0, self.v0 = min(us), min(vs)
        self.left, self.bottom = left, bottom
        self.w, self.h = (max(us) - min(us)) / self.k, (max(vs) - min(vs)) / self.k

    def P(self, p):
        return (self.left + (self.us * p[self.ua] - self.u0) / self.k,
                self.bottom - (self.vs * p[self.va] - self.v0) / self.k)

    def rect(self, mn, mx):
        (x0, y0), (x1, y1) = self.P(mn), self.P(mx)
        return min(x0, x1), min(y0, y1), abs(x1 - x0), abs(y1 - y0)

    def near(self, mn, mx):
        return mx[self.da] if self.ds > 0 else -mn[self.da]

    def members(self, ms, sw=0.28, fills=FILL, key="max"):
        for m in sorted(ms, key=lambda q: self.near(q["min"], q[key])):
            x, y, w, h = self.rect(m["min"], m[key])
            self.sh.rect(x, y, w, h, sw=sw, fill=fills.get(m["kind"], "#dde2e8"))

    def holes(self, ms, uses=None, visible_face=None, r=None, dash=None):
        for m in ms:
            for hl in m["holes"]:
                if uses and hl["use"] not in uses:
                    continue
                if hl["k"] == self.da:
                    vis = (hl["sg"] > 0) == (self.ds > 0)
                    if visible_face is not None and vis != visible_face:
                        continue
                    x, y = self.P(hl["p"])
                    self.sh.circle(x, y, r or max(hl["d"] / 2 / self.k, 0.35), sw=0.16,
                                   fill="#ffffff" if vis else "none", dash=None if vis else (dash or "0.5 0.35"))


# ======================================================================= helpers on the model
def face_name(j, seam):
    """Name a seam face of joint j for the shop: outer/inner/front/rear/top/bottom."""
    f = seam["face"]
    ax, sg = "XYZ".index(f[1]), f[0]
    m = j["m"]
    if ax == 2:
        return "top" if sg == "+" else "bottom"
    if ax == 1:
        if seam["external"]:
            return "front" if sg == "-" else "rear"
        return "inner" if m["sub"] == "BOX" else ("front" if sg == "-" else "rear")
    if seam["external"]:
        return "outer"
    return "inner" if m["sub"].startswith("SA") else ("left" if sg == "-" else "right")


def weld_text(j):
    fil = [face_name(j, s) for s in j["seams"] if s["type"] == "fillet"]
    fl = [face_name(j, s) + ("*" if s["external"] else "") for s in j["seams"] if s["type"] == "flush"]
    cap = [face_name(j, s) for s in j["seams"] if s["type"] == "cap"]
    parts = (["fillet 3: " + "+".join(fil)] if fil else []) + (["flush: " + ", ".join(fl)] if fl else []) + \
        (["%s: with cap" % "+".join(cap)] if cap else [])
    return "; ".join(parts)


def mlabel(m):
    return "%s %s" % (m["mark"], WM.location(m))


def mirror_sa_r(wm):
    """Give SA-R the same weld order as SA-L (mirror image), so R-numbers match L-numbers."""
    W = wm["D"]["ext_w"]
    L = {tuple(round(v, 1) for v in (W - j["p"][0], j["p"][1], j["p"][2])): j for j in wm["seq"]["SA-L"]}
    for j in wm["seq"]["SA-R"]:
        twin = L.get(tuple(round(v, 1) for v in j["p"]))
        if twin:
            j["seq"] = twin["seq"]
            j["id"] = "R%02d" % twin["seq"]
    wm["seq"]["SA-R"].sort(key=lambda j: j["seq"])


# ======================================================================= data outputs
def write_csvs(wm):
    os.makedirs(os.path.join(ROOT, "bom"), exist_ok=True)
    F = wm["F"]
    with open(os.path.join(ROOT, "bom", "frame_cut_list.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["mark", "qty", "description", "section", "cut_length_mm", "ends", "holes_each",
                    "mass_each_kg", "mass_total_kg", "sub_assembly", "positions"])
        for mk, ms in wm["marks"].items():
            if not ms:
                continue
            m = ms[0]
            w.writerow([mk, len(ms), describe(m), m["section"], "%.1f" % m["cut"], ends(m), len(m["holes"]),
                        "%.2f" % m["mass"], "%.2f" % (m["mass"] * len(ms)), stages(ms),
                        "; ".join(WM.location(q) for q in ms)])
        f = wm["D"]["frame"]
        w.writerow([wm["cap_mark"], 4, "Post top cap", "PL %gx%gx%g" % (f, f, F["cap_t"]), "%g" % f, "-", 0,
                    "%.3f" % wm["cap_mass"], "%.2f" % (4 * wm["cap_mass"]), "FINAL", "top of each post"])
    with open(os.path.join(ROOT, "bom", "frame_drilling.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["mark", "qty", "face", "use", "hole", "datum_end", "positions_mm_from_datum_end"])
        for mk, ms in wm["marks"].items():
            if not ms:
                continue
            m = ms[0]
            if m["kind"] == "pad":
                w.writerow([mk, len(ms), "plate", "castor bolts", "M8 tapped thru (6.8 drill)", "pad corner",
                            "%g mm square on pad centre" % F["castor_pcd"]])
                continue
            for face, use, pos, _ in mark_faces(ms):
                w.writerow([mk, len(ms), face, use, "D%.1f (M6 rivnut)" % F["rivnut_hole"],
                            datum_end(m), " ".join("%.1f" % p for p in pos)])
    with open(os.path.join(ROOT, "bom", "frame_weld_schedule.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["joint", "stage", "seq", "member_end", "welded_to", "weld", "grind_flush", "detail"])
        for st, js in wm["seq"].items():
            for j in js:
                grind = ", ".join(face_name(j, s) for s in j["seams"] if s["type"] == "flush" and s["external"])
                w.writerow([j["id"], st, j["seq"], mlabel(j["m"]), mlabel(j["n"]), weld_text(j).replace("*", ""),
                            grind, "A/B"])
        for k in wm["ledges"]:
            w.writerow([k["id"], k["stage"], "", mlabel(k["ledge"]), mlabel(k["rail"]),
                        "fillet 3 x %g @ %g c/c underside, %d stitches + %g returns" %
                        (F["stitch"], F["stitch_pitch"], k["stitches"], F["stitch_return"]), "-", "C"])
        for c in wm["caps"]:
            w.writerow([c["id"], "FINAL", "", "%s cap" % wm["cap_mark"], mlabel(c["post"]),
                        "seal weld all round (flush seam), incl. the top-rail ends", "all faces", "D"])
        for p in wm["pads"]:
            w.writerow([p["id"], "FINAL", "", mlabel(p["pad"]), "post + base rails at %s" % WM.location(p["pad"]),
                        "fillet 3 inner edges + seal outer edges", "outer edges", "E"])
    with open(os.path.join(ROOT, "bom", "frame_nesting.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["stock", "bar", "pieces (mark:length)", "used_mm", "offcut_mm"])
        for name, bars, L in (("SHS %s x %.1f m" % (wm["sec_shs"], F["stock_shs"] / 1000), wm["nest_shs"], F["stock_shs"]),
                              ("FB %s x %.1f m" % (wm["members"][-1]["section"] if False else "20x3", F["stock_fb"] / 1000),
                               wm["nest_fb"], F["stock_fb"])):
            for i, b in enumerate(bars):
                w.writerow([name, i + 1, " ".join("%s:%.1f" % q for q in b["pieces"]), "%.1f" % b["used"],
                            "%.1f" % b["offcut"]])


def describe(m):
    return {"post": "Post", "rail": "Side rail" if m["axis"] == 1 else "Cross rail", "upright": "Rack upright",
            "spacer": "Rail spacer (LOOSE - bolted, not welded)", "ledge": "Ledge (flat bar)",
            "pad": "Castor pad, 4x M8 tapped"}[m["kind"]]


def ends(m):
    return "square" if m["kind"] != "pad" else "-"


def datum_end(m):
    return {0: "left end", 1: "front end", 2: "bottom end"}[m["axis"]] if m.get("axis") is not None else "-"


def faces_of(m):
    """[(face label, use, [positions])] for a member's drilled faces."""
    out = {}
    for h in m["holes"]:
        out.setdefault((h["use"], h["face"]), []).append(h["s"])
    res = []
    for (use, face), pos in sorted(out.items(), key=lambda q: list(WM.FACE_USE).index(q[0][0])):
        lab = {"side": "outer side face", "rear": "rear face", "top": "top face", "skirt": "bottom face",
               "spacer": "inner face"}[use]
        res.append((lab, use, sorted(pos)))
    return res


def mark_faces(ms):
    """Drilled faces of one mark over all its positions: [(face, use, positions, [use keys])], positions from the
    datum end. One piece can serve two positions with a face used differently: S1 is a base rail (second face down,
    skirt) or a top rail (same holes up, top panel)."""
    out = []
    for m in ms:
        used = set()
        for lab, use, pos in faces_of(m):
            key = [round(p, 1) for p in pos]
            rev = sorted(round(m["cut"] - p, 1) for p in pos)
            i = next((i for i, o in enumerate(out) if i not in used and o["key"] in (key, rev)), None)
            if i is None:
                out.append({"key": key, "pos": pos, "by": {}})
                i = len(out) - 1
            used.add(i)
            out[i]["by"].setdefault((lab, use), []).append(WM.location(m).split()[0].lower())
    res = []
    for o in out:
        by = list(o["by"].items())
        if len(by) == 1:
            (lab, use), _ = by[0]
            res.append((lab, WM.FACE_USE[use], o["pos"], [use]))
            continue

        def where(v):
            return " (at %s)" % ", ".join(dict.fromkeys(v))
        res.append((" / ".join(lab.replace(" face", "") + where(v) for (lab, _), v in by),
                    " / ".join(WM.FACE_USE[use] + where(v) for (_, use), v in by), o["pos"], [u for (_, u), _ in by]))
    return res


# ======================================================================= STEP (true SHS geometry)
def build_solids(wm):
    import cadquery as cq
    F = wm["F"]
    t, ro = F["shs_t"], F["shs_ro"]
    f = wm["D"]["frame"]
    out = []
    for m in wm["members"]:
        if m["kind"] in ("post", "rail", "upright", "spacer"):
            a = m["axis"]
            mn, mx = m["min"], m["tube_max"]
            L = mx[a] - mn[a]
            org = [(mn[i] + mx[i]) / 2.0 for i in range(3)]
            org[a] = mn[a]
            nrm = [0, 0, 0]
            nrm[a] = 1
            xd = (0, 1, 0) if a == 0 else (1, 0, 0)
            pl = cq.Plane(origin=tuple(org), xDir=xd, normal=tuple(nrm))
            sk_o = cq.Sketch().rect(f, f).vertices().fillet(ro)
            sk_i = cq.Sketch().rect(f - 2 * t, f - 2 * t).vertices().fillet(max(ro - t, 0.2))
            solid = cq.Workplane(pl).placeSketch(sk_o).extrude(L).val()
            solid = solid.cut(cq.Workplane(pl).placeSketch(sk_i).extrude(L).val())
            for h in m["holes"]:
                p = list(h["p"])
                p[h["k"]] += 0.5 * h["sg"]
                d = [0, 0, 0]
                d[h["k"]] = -h["sg"]
                solid = solid.cut(cq.Solid.makeCylinder(h["d"] / 2.0, t + 1.0, cq.Vector(*p), cq.Vector(*d)))
            out.append((m, solid))
            if m["kind"] == "post":
                cap = cq.Solid.makeBox(f, f, F["cap_t"], pnt=cq.Vector(mn[0], mn[1], mx[2]))
                out.append(({"kind": "cap", "name": "Cap " + m["name"], "mark": wm["cap_mark"], "sub": "FINAL",
                             "min": [mn[0], mn[1], mx[2]], "max": [mn[0] + f, mn[1] + f, mx[2] + F["cap_t"]],
                             "holes": []}, cap))
        else:
            mn, mx = m["min"], m["max"]
            solid = cq.Solid.makeBox(mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2], pnt=cq.Vector(*mn))
            for (x, y) in m.get("taps", []):
                solid = solid.cut(cq.Solid.makeCylinder(3.4, mx[2] - mn[2] + 2, cq.Vector(x, y, mn[2] - 1),
                                                        cq.Vector(0, 0, 1)))
            out.append((m, solid))
    return out


def export_steps(wm, solids):
    import cadquery as cq
    exp = os.path.join(ROOT, "cad", "exports")
    os.makedirs(os.path.join(exp, "frame_members"), exist_ok=True)
    assy = cq.Assembly(name="SRA-16 frame weldment %s" % WM.DOC_NO)
    names = {}
    for m, s in solids:
        nm = "%s %s" % (m["mark"], WM.location(m) if m["kind"] != "cap" else m["name"].replace("Cap Post ", "cap "))
        names[nm] = names.get(nm, 0) + 1
        if names[nm] > 1:
            nm += " (%d)" % names[nm]
        r, g, b = STAGE_COL.get(m["sub"], (0.5, 0.5, 0.5))
        assy.add(s, name=nm, color=cq.Color(r, g, b, 1.0))
    assy.export(os.path.join(exp, "SRA16_frame_weldment.step"), exportType="STEP")
    done = set()
    for m, s in solids:
        if m["mark"] in done or m["kind"] == "cap":
            continue
        done.add(m["mark"])
        sh = s.translate(cq.Vector(0, 0, 0))
        a = m.get("axis")
        if a is not None:
            org = [m["min"][0], m["min"][1], m["min"][2]]
            sh = sh.translate(cq.Vector(-org[0], -org[1], -org[2]))
            if a == 1:
                sh = sh.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), -90)
            elif a == 2:
                sh = sh.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 1, 0), 90)
            bb = sh.BoundingBox()
            sh = sh.translate(cq.Vector(-bb.xmin, -bb.ymin, -bb.zmin))
        cq.exporters.export(cq.Workplane().add(sh), os.path.join(exp, "frame_members", "%s.step" % m["mark"]))
    return os.path.join(exp, "SRA16_frame_weldment.step")


# ======================================================================= sheets
def frame_bbox(wm, with_pads=True):
    (x0, x1), (y0, y1), (z0, z1) = wm["bound"]
    if with_pads:
        z0 -= wm["D"]["pad_t"]
    return ([x0, y0, z0], [x1, y1, z1])


def welded(wm):
    return [m for m in wm["members"] if m["kind"] != "spacer"]


def sheet1(wm, solids):
    from make_drawings import hlr
    import cadquery as cq
    sh = Svg()
    border(sh)
    D, F = wm["D"], wm["F"]
    org = wm["org"]
    fo = wm["frame_outer"]
    # ---------------- isometric (HLR) with mark balloons
    comp = cq.Compound.makeCompound([s for m, s in solids if m["kind"] != "spacer"])
    n = (-1 / math.sqrt(3), -1 / math.sqrt(3), 1 / math.sqrt(3))
    xd = (1 / math.sqrt(2), -1 / math.sqrt(2), 0.0)
    yd = (n[1] * xd[2] - n[2] * xd[1], n[2] * xd[0] - n[0] * xd[2], n[0] * xd[1] - n[1] * xd[0])
    polys = hlr(comp, n, xd)
    us = [p[0] for pl in polys for p in pl]
    vs = [p[1] for pl in polys for p in pl]
    R = (30.0, 20.0, 138.0, 232.0)
    k = min((R[2] - R[0]) / (max(us) - min(us)), (R[3] - R[1]) / (max(vs) - min(vs)))
    ox = (R[0] + R[2]) / 2 - (max(us) + min(us)) / 2 * k
    oy = (R[1] + R[3]) / 2 + (max(vs) + min(vs)) / 2 * k

    def iso(p):
        u = sum(p[i] * xd[i] for i in range(3))
        v = sum(p[i] * yd[i] for i in range(3))
        return ox + u * k, oy - v * k
    for pl in polys:
        sh.poly([(ox + u * k, oy - v * k) for u, v in pl], w=0.13, c="#2a2f35")
    # one anchor per mark: the nearest visible instance, kept clear of anchors already placed
    rail_of = {id(k["ledge"]): k["rail"] for k in wm["ledges"]}
    anchors = []
    for mk, ms in wm["marks"].items():
        if not ms or ms[0]["kind"] == "spacer":
            continue
        cands = []
        for m in ms:
            a = m.get("axis")
            p = [(m["min"][i] + m["max"][i]) / 2.0 for i in range(3)]
            for i in range(3):
                if i != a:
                    p[i] = m["min"][i] if i < 2 else m["max"][i]
            if a is not None:
                p[a] = m["min"][a] + 0.62 * (m["max"][a] - m["min"][a])
            score = sum(p[i] * n[i] for i in range(3))
            rail = rail_of.get(id(m))
            if rail is not None:                   # a ledge on a rail face turned away from the viewer is hidden
                b = 1 - a
                inward = (m["min"][b] + m["max"][b]) - (rail["min"][b] + rail["max"][b])
                if inward * n[b] <= 0:
                    score -= 1e6
            cands.append((score, iso(p)))
        cands.sort(key=lambda q: -q[0])
        pick = next((q for s, q in cands if all(math.hypot(q[0] - t[0], q[1] - t[1]) > 6.0 for _, t in anchors)),
                    cands[0][1])
        anchors.append((mk, pick))
    cxm = (R[0] + R[2]) / 2
    for side in (-1, 1):
        grp = sorted([a for a in anchors if (a[1][0] < cxm) == (side < 0)], key=lambda q: q[1][1])
        bx = 18.0 if side < 0 else 146.0
        last = -1e9
        for mk, (ax, ay) in grp:
            by = max(ay, last + 7.2)
            last = by
            balloon(sh, bx, by, mk, ax, ay)
    sh.text((R[0] + R[2]) / 2, 243, "ISOMETRIC - FRONT LEFT (NOT TO SCALE)", size=2.8, anchor="middle", weight="bold")
    # ---------------- orthographic 1:20
    bb = frame_bbox(wm)
    ms = welded(wm)
    S = 20
    vf = View(sh, "front", S, 176, 236, bb)
    vf.members(ms)
    vt = View(sh, "top", S, 176, 236 - vf.h - 20, bb)
    vt.members(ms)
    vs_ = View(sh, "right", S, 176 + vf.w + 16, 236, bb)
    vs_.members(ms)
    for v, lab in ((vf, "FRONT"), (vs_, "RIGHT SIDE"), (vt, "PLAN")):
        sh.text(v.left + v.w / 2, v.bottom + (9.5 if v is not vt else 6.5), lab, size=2.4, anchor="middle",
                weight="bold")
    hdim(sh, vf.P((org[0], 0, org[2]))[0], vf.P((org[0] + fo[0], 0, org[2]))[0], vf.bottom, vf.bottom + 5,
         "%g" % fo[0])
    hdim(sh, vs_.P((0, org[1], org[2]))[0], vs_.P((0, org[1] + fo[1], org[2]))[0], vs_.bottom, vs_.bottom + 5,
         "%g" % fo[1])
    vdim(sh, vf.P((0, 0, org[2]))[1], vf.P((0, 0, org[2] + fo[2]))[1], vf.left, vf.left - 15, "%g" % fo[2])
    lv = [("A 0", org[2])]
    for nm in ("Rail Mid left", "Rail Shelf left", "Rail Top left"):
        m = [q for q in ms if q["name"] == nm][0]
        lv.append(("%g" % round(m["max"][2] - org[2], 1), m["max"][2]))
    ordinate(sh, vf.left - 0.5, vf.left - 3.5, [vf.P((0, 0, z))[1] for _, z in lv], [a for a, _ in lv])
    hdim(sh, vt.P((org[0], 0, 0))[0], vt.P((org[0] + fo[0], 0, 0))[0], vt.bottom - vt.h, vt.bottom - vt.h - 4,
         "%g" % fo[0])
    vdim(sh, vt.P((0, org[1], 0))[1], vt.P((0, org[1] + fo[1], 0))[1], vt.left, vt.left - 5, "%g" % fo[1])
    # datum symbols
    for (x, y, t) in ((vf.left - 1.5, vf.P((0, 0, org[2]))[1], "A"),):
        sh.poly([(x - 2.2, y - 1.4), (x - 2.2, y + 1.4), (x - 0.2, y)], w=0.2, fill=INK, close=True)
    sh.text(vs_.left + 1, vs_.bottom + 13, "Datum B = front face (left in this view)", size=1.8)
    sh.text(vf.left - 16, vf.bottom + 13, "Datum C = left face", size=1.8)
    # ---------------- notes + mark list
    x0 = 286
    heading(sh, x0, 16, "GENERAL NOTES")
    tot = wm["totals"]
    notes = [
        "1  %s %s to %s (black or pre-primed; DuraGal OK -" % (wm["sec_shs"], F["grade"], F["std"]),
        "   grind zinc 25 mm each side of welds + extract fumes).",
        "   Flat bar and plate grade 250 (AS/NZS 3678 / 3679.1).",
        "2  Datums (all sheets): A underside of base rails, B front face,",
        "   C left face. Dimensions mm, from datums unless noted.",
        "3  GMAW, AS/NZS 1554.1 category GP. Fillets 3 mm (on 2 mm",
        "   wall). SHS joints welded all round (details A/B, sheet 4).",
        "4  Faces marked * receive panels, doors or pads: grind welds",
        "   flush. Build SA-L / SA-R flat (sheet 2), then box (sheet 3).",
        "5  Holes D%.1f for M6 steel rivnuts (fit after coating); drill" % F["rivnut_hole"],
        "   per sheet 6 before welding. Pads PL1: 4x M8 tapped.",
        "6  Tolerances: see sheet 4. Diagonals are the key checks.",
        "7  HOLD POINT H1: mid rails (S2 mid, C3 mid rear) and ledges",
        "   F2/F3 partition sit on the AC grille split M3 (%.0f above A)." % (D["z_split"] - org[2]),
        "   Tape-check M3, re-run tools/make_weld_pack.py, then weld.",
        "8  RS1 rail spacers are NOT welded: bolt to U1 after coating,",
        "   pack 0-4 mm to set the 19in rails (465.1 hole centres).",
        "9  Finish: blast + zinc primer + powder coat (sheet 4).",
        "10 Weldment %.0f kg (+ spacers %.1f kg); %d rivnuts; %d joints." %
        (tot["mass_weldment_kg"], tot["mass_spacers_kg"], tot["rivnuts"], tot["joints_shs"]),
    ]
    y = paragraph(sh, x0, 22, notes, size=1.95, lh=3.15)
    heading(sh, x0, y + 4, "MARK LIST (full cut list sheet 5)")
    rows = []
    for mk, ms_ in wm["marks"].items():
        if ms_:
            rows.append((mk, str(len(ms_)), describe(ms_[0]).replace(" (LOOSE - bolted, not welded)", " LOOSE"),
                         "%.1f" % ms_[0]["cut"] if ms_[0]["kind"] != "pad" else ms_[0]["section"]))
    f = D["frame"]
    rows.append((wm["cap_mark"], "4", "Post top cap", "PL %gx%gx%g" % (f, f, F["cap_t"])))
    table(sh, x0, y + 6, [(12, "c"), (9, "c"), (68, "l"), (32, "r")], rows,
          head=("MARK", "QTY", "DESCRIPTION", "CUT / SIZE"), size=1.95, rh=3.5)
    title_block(sh, wm, 1, "Welded frame - general arrangement + mark list", "1:%d (iso NTS)" % S)
    return sh


def side_frame_members(wm, sub):
    return [m for m in wm["members"] if m["sub"] == sub and m["kind"] in ("post", "rail", "upright", "ledge")]


def side_balloons(sh, v, ms, xl, xr, rail_side, r=3.0, gap=7.2):
    """One balloon per mark in a side-frame view. Posts and uprights go to the nearer column (the instance nearest
    it); rails and ledges go to rail_side, anchored near that end (ledges further in, clear of their rail)."""
    cx = v.left + v.w / 2
    best = {}
    for m in ms:
        a = m["axis"]
        p = [(m["min"][i] + m["max"][i]) / 2.0 for i in range(3)]
        if a == 2:
            p[2] = m["min"][2] + 0.8 * (m["max"][2] - m["min"][2])
            q = v.P(p)
            side = "l" if q[0] < cx else "r"
        else:
            side = rail_side
            f = 0.85 if m["kind"] == "rail" else 0.7
            if m["kind"] == "rail":                      # upper edge of the rail, clear of its ledge
                p[2] = m["max"][2] - 0.15 * (m["max"][2] - m["min"][2])
            ends = []
            for e in (m["min"][a], m["max"][a]):
                pe = list(p)
                pe[a] = e
                ends.append(v.P(pe))
            near, far = sorted(ends, key=lambda q: q[0], reverse=(side == "r"))
            q = (far[0] + f * (near[0] - far[0]), near[1])
        d = abs(q[0] - (xl if side == "l" else xr))
        if m["mark"] not in best or d < best[m["mark"]][0]:
            best[m["mark"]] = (d, side, q)
    for side, bx in (("l", xl), ("r", xr)):
        last = -1e9
        for mk, (_, _, (ax, ay)) in sorted([(k, b) for k, b in best.items() if b[1] == side], key=lambda t: t[1][2][1]):
            by = max(ay, last + gap)
            last = by
            balloon(sh, bx, by, mk, ax, ay, r=r)


def sheet2(wm):
    sh = Svg()
    border(sh)
    D, F = wm["D"], wm["F"]
    org, fo = wm["org"], wm["frame_outer"]
    S = 10
    msL = side_frame_members(wm, "SA-L")
    bb = frame_bbox(wm, with_pads=False)
    v = View(sh, "right", S, 44, 222, bb)            # viewed from inside (inner face up on the table), front left
    v.members(msL)
    v.holes(msL, uses=("side",), visible_face=False)
    v.holes(msL, uses=("spacer",), visible_face=True)
    # joints
    for j in wm["seq"]["SA-L"]:
        x, y = v.P(j["p"])
        m = j["m"]
        a = m["axis"]
        dx, dy = 0.0, 0.0
        if a == 1:
            dx = 6.5 if j["end"] == "start" else -6.5
        else:
            dy = -5.0 if j["end"] == "start" else 5.0
        jtag(sh, x + dx, y + dy, j["id"])
    # diagonal
    p0, p1 = v.P((0, org[1], org[2])), v.P((0, org[1] + fo[1], org[2] + fo[2]))
    sh.line(p0[0], p0[1], p1[0], p1[1], w=0.15, dash="3 1.2", c="#c0392b")
    dg = math.hypot(fo[1], fo[2])
    mx_, my_ = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
    ang = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
    sh.text(mx_ + 3, my_ + 9, "DIAGONALS %.1f EQUAL +/-1.5" % dg, size=2.0, rot=ang, c="#c0392b", weight="bold")
    # dims: overall + uprights (datum B), levels (datum A)
    yb = v.bottom
    hdim(sh, v.P((0, org[1], 0))[0], v.P((0, org[1] + fo[1], 0))[0], yb, yb + 13, "%g" % fo[1])
    ups = sorted([m for m in msL if m["kind"] == "upright"], key=lambda q: q["min"][1])
    xs = [org[1], org[1] + D["frame"]] + [c for u in ups for c in (u["min"][1], u["max"][1])] + \
         [org[1] + fo[1] - D["frame"], org[1] + fo[1]]
    xs = sorted(set(round(c, 1) for c in xs))
    for c in xs:
        px = v.P((0, c, 0))[0]
        sh.line(px, yb + 0.8, px, yb + 7.6, w=0.12)
    for c0, c1 in zip(xs[:-1], xs[1:]):
        a0, a1 = v.P((0, c0, 0))[0], v.P((0, c1, 0))[0]
        sh.add('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width="0.18" '
               'marker-start="url(#aDim)" marker-end="url(#aDim)"/>' % (a0, yb + 6.4, a1, yb + 6.4, INK))
        sh.text((a0 + a1) / 2, yb + 5.6, "%g" % round(c1 - c0, 1), size=1.8, anchor="middle")
    lv, labs = [], []
    for m in [q for q in msL if q["kind"] == "rail"]:
        for z in (m["min"][2], m["max"][2]):
            lv.append(v.P((0, 0, z))[1])
            labs.append("%g" % round(z - org[2], 1))
    for m in [q for q in msL if q["kind"] == "ledge"]:
        lv.append(v.P((0, 0, m["max"][2]))[1])
        labs.append("%g F" % round(m["max"][2] - org[2], 1))
    ordinate(sh, v.left - 0.5, v.left - 4, lv, labs, size=1.75, min_gap=2.3)
    sh.text(v.left - 26, v.bottom + 3.5, "levels from datum A", size=1.7)
    sh.text(v.left - 26, v.bottom + 6, "(F = top of ledge)", size=1.7)
    # partition ledge start
    f2 = [m for m in msL if m["kind"] == "ledge" and "partition" in m["name"]]
    if f2:
        m = f2[0]
        xa = v.P((0, m["min"][1], 0))[0]
        ya = v.P((0, 0, m["max"][2]))[1]
        sh.line(v.P((0, org[1], 0))[0], ya - 6, xa, ya - 6, w=0.15)
        sh.add('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width="0.18" '
               'marker-start="url(#aDim)" marker-end="url(#aDim)"/>' % (v.P((0, org[1], 0))[0], ya - 6, xa, ya - 6, INK))
        sh.line(xa, ya, xa, ya - 7, w=0.12)
        sh.text((v.P((0, org[1], 0))[0] + xa) / 2, ya - 6.8, "%g" % round(m["min"][1] - org[1], 1), size=1.8,
                anchor="middle")
    side_balloons(sh, v, msL, v.left - 25, v.left + v.w + 14, "r")
    sh.text(v.left + v.w / 2, 238, "SA-L  LEFT SIDE FRAME - AS WELDED ON THE TABLE (inner face up, viewed from inside)",
            size=2.5, anchor="middle", weight="bold")
    sh.text(v.left + v.w / 2, 242.2, "scale 1:%d   front (datum B) on the left   dashed circles = rivnut holes in the "
            "outer face (underneath)" % S, size=1.9, anchor="middle")
    # ---------------- SA-R (opposite hand) small
    msR = side_frame_members(wm, "SA-R")
    v2 = View(sh, "left", 20, 180, 150, bb)
    v2.members(msR, sw=0.22)
    side_balloons(sh, v2, msR, v2.left - 7, v2.left + v2.w + 5.5, "l", r=2.5, gap=6.2)
    sh.text(v2.left + v2.w / 2, v2.bottom + 6, "SA-R  RIGHT SIDE FRAME (1:20)", size=2.4, anchor="middle", weight="bold")
    sh.text(v2.left + v2.w / 2, v2.bottom + 9.2, "OPPOSITE HAND - mirror of SA-L", size=2.2, anchor="middle",
            weight="bold", c="#c0392b")
    sh.text(v2.left + v2.w / 2, v2.bottom + 12.2, "inner face up, front on the RIGHT", size=1.9, anchor="middle")
    sh.text(v2.left + v2.w / 2, v2.bottom + 15.0, "rear post is P3 (P2 is SA-L only)", size=1.9, anchor="middle")
    sh.text(v2.left + v2.w / 2, v2.bottom + 17.8, "joints R01-R12 = mirror of L01-L12", size=1.9, anchor="middle")
    sh.text(v2.left + 1, v2.bottom - v2.h - 2, "<- rear", size=1.8)
    sh.text(v2.left + v2.w - 1, v2.bottom - v2.h - 2, "front ->", size=1.8, anchor="end")
    # ---------------- steps + joint table
    x0 = 246
    heading(sh, x0, 16, "SIDE FRAMES - FIT-UP AND WELD (make SA-L, then SA-R opposite hand)")
    fl = [q for q in msL if q["kind"] == "ledge"]
    lg = {("floor" if "floor" in m["name"] else "partition" if "partition" in m["name"] else "shelf"): m for m in fl}
    rails = {m["name"].split()[1]: m for m in msL if m["kind"] == "rail"}
    gap = {k: round(rails[{"floor": "Base", "partition": "Mid", "shelf": "Shelf"}[k]]["max"][2] - lg[k]["max"][2], 1)
           for k in lg}
    steps = [
        "1  Drill all members first (sheet 6). Posts outer-face holes DOWN.",
        "2  Lay P1 + P2 flat, inner faces up, against a straight stop. Outside",
        "   of posts %g apart (datum B to rear face)." % fo[1],
        "3  Fit S1 (base, top) and S2 (mid, shelf) between the posts: S1 base",
        "   flush with the post bottoms (datum A), levels per ordinates.",
        "4  Stand U1 on the shelf rail at %g and %g from datum B." % tuple(
            round(u["min"][1] - org[1], 1) for u in ups),
        "5  Square each joint, clamp. Diagonals equal within 1.5, posts",
        "   parallel within 1. Tack 2 per joint on the up face; re-check.",
        "6  Weld in joint order L01 > L12 (balanced). Up-face seams + the",
        "   short side fillets (3F uphill) - let each joint cool.",
        "7  Turn over. Weld the outer-face seams in the same order, then",
        "   grind flush (* faces carry the side panel). Re-check diagonals.",
        "8  Inner face up again: ledges, underside stitches only (det. C):",
        "   F1 floor, top %g below S1 top; F2 partition, top %g below S2" % (gap.get("floor", 0), gap.get("partition", 0)),
        "   (mid) top, from %g to rear post; F1 shelf, %g below S2 top." % (
            round(lg["partition"]["min"][1] - org[1], 1) if "partition" in lg else 0, gap.get("shelf", 0)),
        "   Gauge: an offcut of the actual ply on the rail top.",
        "9  Flat within 2 over the frame (straight-edge the outer face).",
    ]
    y = paragraph(sh, x0, 22, steps, size=1.95, lh=3.2)
    heading(sh, x0, y + 3.5, "JOINTS SA-L (SA-R: R-numbers, mirror)")
    rows = []
    for j in wm["seq"]["SA-L"]:
        rows.append((j["id"], "%s %s" % (j["m"]["mark"], WM.location(j["m"])),
                     "%s %s" % (j["n"]["mark"], WM.location(j["n"])), weld_text(j)))
    y = table(sh, x0, y + 5.5, [(10, "c"), (36, "l"), (28, "l"), (88, "l")], rows,
              head=("JOINT", "MEMBER END", "WELDED TO", "WELD (* = external face: grind flush)"), size=1.85, rh=3.45)
    heading(sh, x0, y + 7, "LEDGES ON THE SIDE FRAMES (det. C, underside stitches only)")
    rows = [(k["id"], k["stage"], "%s %s" % (k["ledge"]["mark"], WM.location(k["ledge"])),
             "%s %s" % (k["rail"]["mark"], WM.location(k["rail"])), "%g" % round(k["ply_below_top"], 1),
             "%d x %g + returns" % (k["stitches"], F["stitch"]))
            for k in wm["ledges"] if k["stage"] in ("SA-L", "SA-R")]
    y = table(sh, x0, y + 9, [(10, "c"), (12, "c"), (34, "l"), (32, "l"), (30, "c"), (44, "l")], rows,
              head=("WELD", "FRAME", "LEDGE", "ON RAIL", "TOP BELOW RAIL", "STITCHES (@ %g c/c)" % F["stitch_pitch"]),
              size=1.85, rh=3.45)
    heading(sh, x0, y + 7, "RECORD (measure tacked, then after welding)")
    rows = [(fr, st, "", "", "", "", "") for fr in ("SA-L", "SA-R") for st in ("tacked", "welded")]
    table(sh, x0, y + 9, [(16, "c"), (16, "c"), (26, "c"), (26, "c"), (26, "c"), (26, "c"), (26, "c")], rows,
          head=("FRAME", "STAGE", "DIAG 1", "DIAG 2", "LENGTH %g" % fo[1], "FLAT <= 2", "INITIALS"), size=1.85, rh=5.0)
    title_block(sh, wm, 2, "Side frames SA-L / SA-R - fit-up, joints, ledges", "1:%d / 1:20" % S)
    return sh


def sheet3(wm):
    sh = Svg()
    border(sh)
    D = wm["D"]
    org, fo = wm["org"], wm["frame_outer"]
    S = 10
    ms = welded(wm)
    bb = frame_bbox(wm)
    vf = View(sh, "front", S, 30, 226, bb)
    vf.members(ms)
    vr = View(sh, "rear", S, 30 + vf.w + 26, 226, bb)
    vr.members(ms)
    vr.holes(ms, uses=("rear",), visible_face=True)
    for v, lab in ((vf, "FRONT (datum B face)"), (vr, "REAR")):
        sh.text(v.left + v.w / 2, v.bottom + 10.5, lab, size=2.4, anchor="middle", weight="bold")
    # joint tags: front rails on the front view, rear rails on the rear view
    for j in wm["seq"]["BOX"]:
        m = j["m"]
        front = m["min"][1] < org[1] + 1
        v = vf if front else vr
        x, y = v.P(j["p"])
        dx = 6.5 if (j["end"] == "start") == (v is vf) else -6.5
        jtag(sh, x + dx, y, j["id"])
    hdim(sh, vf.P((org[0], 0, org[2]))[0], vf.P((org[0] + fo[0], 0, org[2]))[0], vf.bottom, vf.bottom + 6,
         "%g" % fo[0])
    hdim(sh, vr.P((org[0] + fo[0], 0, org[2]))[0], vr.P((org[0], 0, org[2]))[0], vr.bottom, vr.bottom + 6,
         "%g" % fo[0])
    # levels on the front view
    lv, labs = [], []
    for m in [q for q in ms if q["kind"] == "rail" and q["axis"] == 0]:
        for z in (m["min"][2], m["max"][2]):
            lv.append(vf.P((0, 0, z))[1])
            labs.append("%g" % round(z - org[2], 1))
    ordinate(sh, vf.left - 0.5, vf.left - 4, sorted(set(lv)), [labs[lv.index(q)] for q in sorted(set(lv))],
             size=1.75, min_gap=2.3)
    # balloons for cross rails
    for v, sel in ((vf, lambda m: m["min"][1] < org[1] + 1), (vr, lambda m: m["max"][1] > org[1] + fo[1] - 1)):
        items = []
        for m in [q for q in ms if q["kind"] == "rail" and q["axis"] == 0 and sel(q)]:
            p = [(m["min"][i] + m["max"][i]) / 2.0 for i in range(3)]
            p[0] = m["min"][0] + 0.5 * (m["max"][0] - m["min"][0])
            items.append((m["mark"], v.P(p)))
        last = -1e9
        for mk, (ax, ay) in sorted(items, key=lambda q: q[1][1]):
            by = max(ay - 6, last + 7.0)
            last = by
            balloon(sh, v.left + v.w + 9.5, by, mk, ax, ay, r=2.7)
    # ---------------- base plan
    zc = org[2] + D["frame"]
    base = [m for m in ms if m["min"][2] < zc - 0.1]
    vp = View(sh, "top", S, 30 + 2 * vf.w + 64, 150, bb)
    for m in sorted(base, key=lambda q: q["max"][2]):
        x, y, w, h = vp.rect(m["min"], m["max"])
        if m["kind"] == "pad":
            sh.rect(x, y, w, h, sw=0.25, dash="1.2 0.6")
            for tx, ty in m["taps"]:
                px, py = vp.P((tx, ty, 0))
                sh.circle(px, py, 0.55, sw=0.18, dash="0.4 0.3")
        else:
            sh.rect(x, y, w, h, sw=0.28, fill=FILL.get(m["kind"], "#dde2e8"))
    vp.holes(base, uses=("skirt",), visible_face=False)
    sh.text(vp.left + vp.w / 2, vp.bottom - vp.h - 3.5, "BASE PLAN (from above, floor level)", size=2.3,
            anchor="middle", weight="bold")
    sh.text(vp.left + vp.w / 2, vp.bottom + 4.2, "dashed: PL1 pads below, 4x M8, skirt rivnuts", size=1.8,
            anchor="middle")
    hdim(sh, vp.P((org[0], 0, 0))[0], vp.P((org[0] + fo[0], 0, 0))[0], vp.bottom - vp.h, vp.bottom - vp.h - 8,
         "%g" % fo[0])
    vdim(sh, vp.P((0, org[1], 0))[1], vp.P((0, org[1] + fo[1], 0))[1], vp.left + vp.w, vp.left + vp.w + 5,
         "%g" % fo[1])
    pw = D["pad_w"]
    hx0, hy0 = vp.P((org[0], org[1], 0))
    sh.text(hx0 + 1, hy0 + 3, "PL1 %gx%g" % (pw, pw), size=1.7)
    # ---------------- assembly method pictogram
    ax0, ay0 = 198, 170
    heading(sh, ax0, ay0 - 4, "BOX ASSEMBLY (on its side)", size=2.4)
    for i, (lab, h) in enumerate((("1 SA-L flat, inner face up", 0), ("2 C rails stood up, clamped square", 1),
                                  ("3 SA-R lowered on, tack all", 2))):
        bx = ax0 + i * 27
        sh.rect(bx, ay0 + 22, 22, 3, sw=0.3, fill="#cfd8e3")
        if h >= 1:
            for cx in (bx + 1.5, bx + 10, bx + 18.5):
                sh.rect(cx, ay0 + 10, 2, 12, sw=0.25, fill="#f4d8b8")
        if h >= 2:
            sh.rect(bx, ay0 + 7, 22, 3, sw=0.3, fill="#d4ead9")
        sh.line(bx - 2, ay0 + 25, bx + 24, ay0 + 25, w=0.6)
        paragraph(sh, bx, ay0 + 29, [lab[:2] + lab[2:].split(",")[0]], size=1.7)
    paragraph(sh, ax0, ay0 + 36, [
        "4 Check the four faces and body diagonals (table), twist <= 2.",
        "5 Weld B01 > B14 in order, rolling the box so every joint is",
        "  flat or horizontal (never overhead). Cool between joints.",
        "6 Invert on the flat table: clamp PL1 pads to the table so all",
        "  four are coplanar, grind bottom seams flush, weld PW1-PW4.",
        "7 Weld PL2 caps T1-T4, grind all external faces flush.",
    ], size=1.8, lh=2.9)
    # ---------------- tables
    x0 = 284
    heading(sh, x0, 16, "BOX JOINTS (cross rails C into posts)")
    rows = []
    for j in wm["seq"]["BOX"]:
        rows.append((j["id"], "%s %s" % (j["m"]["mark"], WM.location(j["m"])),
                     "%s %s" % (j["n"]["mark"], WM.location(j["n"]).replace("post ", "")), weld_text(j)))
    y = table(sh, x0, 18, [(9, "c"), (27, "l"), (16, "l"), (72, "l")], rows,
              head=("JOINT", "RAIL END", "POST", "WELD (* grind flush)"), size=1.8, rh=3.4)
    heading(sh, x0, y + 6, "CHECK BEFORE WELDING (tacked) AND AFTER")
    fx, fy, fz = fo
    rows = [("Front / rear face diagonals", "%.1f" % math.hypot(fx, fz), "+/-2"),
            ("Left / right face diagonals", "%.1f" % math.hypot(fy, fz), "+/-2"),
            ("Top / base diagonals", "%.1f" % math.hypot(fx, fy), "+/-1.5"),
            ("Body diagonals (4, corner-corner)", "%.1f" % math.sqrt(fx * fx + fy * fy + fz * fz), "+/-3"),
            ("Outside W x D", "%g x %g" % (fx, fy), "+/-1.5"),
            ("Height (A to top)", "%g" % fz, "+/-1.5"),
            ("Pads coplanar (rock test on table)", "0", "<=1"),
            ("Rack uprights front-rear (19in rails)", "%g" % D["rail_spacing"], "+/-1")]
    y = table(sh, x0, y + 8, [(62, "l"), (32, "r"), (20, "c")], rows, head=("CHECK", "TARGET", "TOL"),
              size=1.85, rh=3.5)
    heading(sh, x0, y + 6, "PADS, CAPS, BENCH LEDGES")
    bench = [k for k in wm["ledges"] if k["stage"] == "BENCH"]
    paragraph(sh, x0, y + 11, [
        "PL1 castor pads PW1-PW4: grind the post/rail bottom seams flush,",
        "clamp pads to the flat table (frame inverted), 3 fillet on the",
        "inner edges + seal outer edges, grind outer edges flush (det. E).",
        "PL2 caps T1-T4: 3 seal fillet all round, grind flush (det. D).",
        "F3 ledges are welded on the bench BEFORE the box (rail clamped",
        "to a straight-edge, stitches from the centre out). A ledge makes",
        "the piece position-specific - paint-mark it:",
    ] + ["   %s  %s %s + %s, top %g below rail top" % (
        k["id"], k["rail"]["mark"], WM.location(k["rail"]).upper(), k["ledge"]["mark"],
        round(k["rail"]["max"][2] - k["ledge"]["max"][2], 1)) for k in bench] + [
        "Ledge on the face opposite the rear-panel holes (C1: either",
        "side); rail top = the face opposite the skirt holes.",
    ], size=1.85, lh=3.0)
    title_block(sh, wm, 3, "Box assembly - cross rails, pads, caps, checks", "1:%d" % S)
    return sh


def rsq(cx, cy, half, r, n=6):
    """Rounded-square outline (model mm, y up), anticlockwise."""
    pts = []
    for qx, qy, a0 in ((cx + half - r, cy - half + r, -90), (cx + half - r, cy + half - r, 0),
                       (cx - half + r, cy + half - r, 90), (cx - half + r, cy - half + r, 180)):
        for i in range(n + 1):
            a = math.radians(a0 + 90.0 * i / n)
            pts.append((qx + r * math.cos(a), qy + r * math.sin(a)))
    return pts


def zigzag(sh, x1, y1, x2, y2, w=0.2):
    """Break line with a zig in the middle."""
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    L = math.hypot(x2 - x1, y2 - y1) or 1.0
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    nx, ny = -uy, ux
    pts = [(x1 - ux * 2, y1 - uy * 2), (mx - ux * 1.2, my - uy * 1.2), (mx - ux * 0.4 + nx * 1.6, my - uy * 0.4 + ny * 1.6),
           (mx + ux * 0.4 - nx * 1.6, my + uy * 0.4 - ny * 1.6), (mx + ux * 1.2, my + uy * 1.2), (x2 + ux * 2, y2 + uy * 2)]
    sh.poly(pts, w=w)


def sheet4(wm):
    """Typical weld details (proportional, dimensioned) + procedure (WPS-lite), tolerances, finish."""
    sh = Svg()
    border(sh)
    D, F = wm["D"], wm["F"]
    f, t, ro = D["frame"], F["shs_t"], F["shs_ro"]
    h = f / 2.0
    fl = F["fillet"]
    WELD = "#454b52"
    LIGHT = "#eef1f4"

    def cell(i, j, title, sub):
        x, y = 14 + i * 87, 16 + j * 134
        sh.rect(x - 2, y - 5, 85, 131, sw=0.15, c="#b8bec5")
        heading(sh, x, y, title, size=2.25)
        sh.text(x + 81, y + 4, sub, size=1.7, anchor="end", c=THIN, italic=True)
        return x, y

    def mapper(ox, oy, k):
        return lambda x, y: (ox + k * x, oy - k * y)

    def poly_m(M, pts, **kw):
        sh.poly([M(*p) for p in pts], **kw)

    def box_m(M, x0, y0, x1, y1, **kw):
        (a, b), (c, d) = M(x0, y0), M(x1, y1)
        sh.rect(min(a, c), min(b, d), abs(c - a), abs(d - b), **kw)

    def ring_m(M, cx, cy, fill="url(#hatch)", bg=LIGHT):
        outer = rsq(cx, cy, h, ro)
        inner = rsq(cx, cy, h - t, max(ro - t, 0.3))
        d = ("M" + " L".join("%.2f %.2f" % M(*p) for p in outer) + " Z M" +
             " L".join("%.2f %.2f" % M(*p) for p in inner) + " Z")
        sh.add('<path d="%s" fill="%s" fill-rule="evenodd" stroke="none"/>' % (d, bg))
        sh.add('<path d="%s" fill="%s" fill-rule="evenodd" stroke="%s" stroke-width="0.3"/>' % (d, fill, INK))

    def clip(cid, x, y, w, hh):
        sh.add('<clipPath id="%s"><rect x="%.2f" y="%.2f" width="%.2f" height="%.2f"/></clipPath><g clip-path="url(#%s)">'
               % (cid, x, y, w, hh, cid))

    def notes(x, y, lines):
        paragraph(sh, x, y + 106, lines, size=1.8, lh=2.8)

    # ---------------------------------------------------------------- A: T-joint elevation
    x, y = cell(0, 0, "A  SHS T-JOINT - ELEVATION", "proportional, NTS")
    k = 1.4
    M = mapper(x + 44, y + 52, k)
    box_m(M, -f, -30, 0, 30, sw=0.3, fill="#dde2e8")                       # post
    box_m(M, 0, -h, 26, h, sw=0.3, fill=LIGHT)                             # rail
    for xx in (-f + t, -t):
        poly_m(M, [(xx, -30), (xx, 30)], w=0.15, dash="1 0.6", c=THIN)
    for yy in (-h + t, h - t):
        poly_m(M, [(0, yy), (26, yy)], w=0.15, dash="1 0.6", c=THIN)
    for sg in (1, -1):
        poly_m(M, [(0, sg * h), (0, sg * (h + fl)), (fl, sg * h)], w=0.12, fill=WELD, close=True)
    for yy in (-30, 30):
        zigzag(sh, *M(-f - 2, yy), *M(2, yy))
    zigzag(sh, *M(26, -h - 2), *M(26, h + 2))
    sh.text(*M(-h, -1), "POST", size=1.9, anchor="middle", weight="bold")
    sh.text(*M(13, -0.8), "RAIL", size=1.9, anchor="middle", weight="bold")
    jx, jy = M(fl * 0.45, h + fl * 0.45)
    weld_symbol(sh, jx, jy, jx + 12, jy - 12, ref=20, kind="fillet", size="%g" % fl, all_round=True)
    sh.text(jx + 14, jy - 18.5, "all round", size=1.7, c=THIN)
    notes(x, y, ["Square-cut end, fit tight (gap 0-1). Weld ALL", "ROUND: 3 fillet where the rail meets the post",
                 "face (shown), flare seam where the faces run", "flush (det. B). Tack 2 per joint first."])
    # ---------------------------------------------------------------- B: flush faces, plan section
    x, y = cell(1, 0, "B  FLUSH FACES - SECTION", "proportional, NTS")
    k = 2.2
    M = mapper(x + 4, y + 55, k)
    clip("clipB", *M(0, 17), 33 * k, 34 * k)
    ring_m(M, 0, 0)                                                         # post (right half shown)
    sh.add("</g>")
    zigzag(sh, *M(0, -h - 2), *M(0, h + 2))
    for sg in (1, -1):
        box_m(M, h, sg * (h - t), 31, sg * h, sw=0.3, fill="url(#hatch)")   # rail walls cut by the section
        cx_, cy_ = h - ro, sg * (h - ro)
        arc = [(cx_ + ro * math.cos(math.radians(a)), cy_ + sg * ro * math.sin(math.radians(a)))
               for a in range(0, 91, 10)]
        poly_m(M, [(h, sg * h)] + arc[::-1], w=0.1, fill=WELD, close=True)
    zigzag(sh, *M(31, -h - 2), *M(31, h + 2))
    sh.text(*M(7, -0.8), "POST", size=1.9, anchor="middle", weight="bold")
    sh.text(*M(23.5, -0.8), "RAIL", size=1.9, anchor="middle", weight="bold")
    jx, jy = M(h - 1.2, h - 0.4)
    weld_symbol(sh, jx, jy, jx + 16, jy - 13, ref=14, kind="flare", size="", flush=True, finish="G")
    sh.text(jx + 31.5, jy - 12.4, "external *", size=1.7, c=THIN)
    jx, jy = M(h - 1.2, -h + 0.4)
    weld_symbol(sh, jx, jy, jx + 16, jy + 10, ref=14, kind="flare", size="")
    sh.text(jx + 31.5, jy + 10.6, "inner face", size=1.7, c=THIN)
    notes(x, y, ["Section on the rail centreline. The tube corner", "radii leave a flare groove where faces run",
                 "flush: fill it in one pass. Faces marked * carry", "panels, seals or pads: grind FLUSH (G).",
                 "Inner faces stay as welded."])
    # ---------------------------------------------------------------- C: ledge on rail, section
    x, y = cell(2, 0, "C  LEDGE ON RAIL - SECTION", "proportional, NTS")
    k = 2.0
    ply = D["floor_t"]
    lw, lt_ = D["cleat"], D["cleat_t"]
    M = mapper(x - 4, y + 45, k)
    ltop = h - ply
    clip("clipC", *M(5, 17), 40 * k, 34 * k)
    ring_m(M, 0, 0)
    sh.add("</g>")
    zigzag(sh, *M(5, -h - 2), *M(5, h + 2))
    box_m(M, h + 1, ltop, 40, h, sw=0.3, fill="url(#ply)")                 # ply (1 mm edge gap)
    box_m(M, h, ltop - lt_, h + lw, ltop, sw=0.3, fill="#aeb8c2")          # flat bar ledge
    poly_m(M, [(h, ltop - lt_), (h, ltop - lt_ - fl), (h + fl, ltop - lt_)], w=0.12, fill=WELD, close=True)
    zigzag(sh, *M(40, ltop - 2), *M(40, h + 2))
    sh.text(*M(7.5, -0.8), "RAIL", size=1.9, anchor="start", weight="bold")
    px_, py_ = M(33, (ltop + h) / 2)
    sh.rect(px_ - 5.5, py_ - 2.2, 11, 3.2, sw=0, fill="#ffffff", c="none")
    sh.text(px_, py_ + 0.4, "PLY %g" % ply, size=1.8, anchor="middle", weight="bold")
    # dim: rail top to ledge top
    xa = M(27, 0)[0]
    sh.add('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width="0.18" '
           'marker-start="url(#aDim)" marker-end="url(#aDim)"/>' % (xa, M(0, h)[1], xa, M(0, ltop)[1], INK))
    sh.rect(xa - 3.2, (M(0, h)[1] + M(0, ltop)[1]) / 2 - 2.0, 6.4, 3.0, sw=0, fill="#ffffff", c="none")
    sh.text(xa, (M(0, h)[1] + M(0, ltop)[1]) / 2 + 0.4, "%g" % ply, size=1.8, anchor="middle")
    lx, ly = M(h + lw * 0.75, ltop - lt_)
    sh.line(lx, ly, lx + 4, ly + 7, w=0.15)
    sh.text(lx + 4.5, ly + 8.5, "%gx%g FB ledge" % (lw, lt_), size=1.8)
    jx, jy = M(h + fl * 0.4, ltop - lt_ - fl * 0.4)
    weld_symbol(sh, jx, jy, jx + 9, jy + 14, ref=24, kind="fillet", size="%g" % fl,
                length="%g-%g" % (F["stitch"], F["stitch_pitch"]))
    notes(x, y, ["Ledge top %g below the rail top for the floor" % ply,
                 "and shelf, %g for the partition: set it with an" % D["partition_t"],
                 "offcut of the real ply. Stitch the UNDERSIDE", "only - the top face is the ply seat."])
    # ---------------------------------------------------------------- D: post cap
    x, y = cell(0, 1, "D  POST TOP CAP PL2 - ELEVATION", "proportional, NTS")
    k = 1.6
    cap = F["cap_t"]
    M = mapper(x + 36, y + 32, k)
    box_m(M, -h, -28, h, 0, sw=0.3, fill="#dde2e8")
    for xx in (-h + t, h - t):
        poly_m(M, [(xx, -28), (xx, 0)], w=0.15, dash="1 0.6", c=THIN)
    box_m(M, -h, 0, h, cap, sw=0.3, fill="#aeb8c2")
    for sg in (-1, 1):
        poly_m(M, [(sg * h, 0), (sg * (h - 0.9), 0), (sg * h, 0.9)], w=0.1, fill=WELD, close=True)
    zigzag(sh, *M(-h - 2, -28), *M(h + 2, -28))
    sh.text(*M(0, -14), "POST (tube cut %g short)" % cap, size=1.7, anchor="middle")
    vdim(sh, M(0, 0)[1], M(0, cap)[1], M(-h, 0)[0], M(-h, 0)[0] - 5, "%g" % cap, size=1.7)
    jx, jy = M(h, 0.2)
    weld_symbol(sh, jx, jy, jx + 8, jy - 10, ref=14, kind="square", size="", all_round=True, flush=True, finish="G")
    sh.text(*M(0, cap + 2.5), "PL2 %gx%gx%g" % (f, f, cap), size=1.7, anchor="middle")
    sh.text(x, y + 88, "Cap top = frame top (datum A + %g)." % wm["frame_outer"][2], size=1.8)
    sh.text(x, y + 91, "Top rails butt against the cap edge.", size=1.8)
    notes(x, y, ["Cap flush with the tube faces all round: seal", "weld the seam (outside corner) and grind flush",
                 "on all faces - the top panel and side panels", "bear here. Weld after the box (step 7)."])
    # ---------------------------------------------------------------- E: castor pad
    x, y = cell(1, 1, "E  CASTOR PAD PL1", "proportional, NTS")
    pw, pt = D["pad_w"], D["pad_t"]
    pc = F["castor_pcd"]
    k = 0.45
    M = mapper(x + 4, y + 13, k)                       # plan from below, outer corner top-left, y down = inward
    Mp = lambda u, v: M(u, -v)                          # noqa: E731
    sh.rect(*Mp(0, 0), pw * k, pw * k, sw=0.3, fill="#dde2e8")
    sh.rect(*Mp(0, 0), f * k, pw * k, sw=0.18, dash="0.8 0.5")
    sh.rect(*Mp(0, 0), pw * k, f * k, sw=0.18, dash="0.8 0.5")
    c0 = pw / 2
    for dx in (-pc / 2, pc / 2):
        for dy in (-pc / 2, pc / 2):
            px_, py_ = Mp(c0 + dx, c0 + dy)
            sh.circle(px_, py_, 3.4 * k, sw=0.2, fill="#ffffff")
            rr = 4.0 * k
            sh.add('<path d="M %.2f %.2f A %.2f %.2f 0 1 1 %.2f %.2f" fill="none" stroke="%s" stroke-width="0.15"/>'
                   % (px_ + rr, py_, rr, rr, px_, py_ - rr, INK))
    hdim(sh, Mp(0, 0)[0], Mp(pw, 0)[0], Mp(0, pw)[1], Mp(0, pw)[1] + 3.5, "%g" % pw, size=1.7, above=False)
    hdim(sh, Mp(c0 - pc / 2, 0)[0], Mp(c0 + pc / 2, 0)[0], Mp(0, 0)[1], Mp(0, 0)[1] - 3, "%g" % pc, size=1.7)
    tx = Mp(pw, 0)[0] + 3
    for i, (txt, wt) in enumerate((("PLAN FROM BELOW", "bold"), ("dashed: post + base", "normal"),
                                   ("rails above, flush", "normal"), ("with the outer faces", "normal"),
                                   ("", "normal"), ("4x M8 tapped thru", "bold"), ("on %g sq, centred" % pc, "normal"),
                                   ("(match the castor)", "normal"))):
        if txt:
            sh.text(tx, Mp(0, 0)[1] + 2.5 + i * 3.4, txt, size=1.75, weight=wt)
    # section through a base rail and the pad
    k2 = 0.8
    Ms = mapper(x + 6, y + 97, k2)
    box_m(Ms, 0, 0, 62, pt, sw=0.3, fill="url(#hatch)")
    ring_m(Ms, h, pt + h)
    zigzag(sh, *Ms(62, -2), *Ms(62, pt + 2))
    poly_m(Ms, [(f, pt), (f, pt + fl), (f + fl, pt)], w=0.1, fill=WELD, close=True)
    poly_m(Ms, [(0, pt), (0, pt - 1.4), (1.4, pt)], w=0.1, fill=WELD, close=True)
    hx = (pw - pc) / 2
    for xx in (hx - 3.4, hx + 3.4):
        poly_m(Ms, [(xx, 0), (xx, pt)], w=0.15, dash="0.7 0.4")
    box_m(Ms, -2, -4, 34, 0, sw=0.18, dash="0.8 0.5")
    sh.text(*Ms(36, -3.4), "castor plate", size=1.55, c=THIN)
    sh.text(*Ms(40, pt + 24), "SECTION", size=1.8, weight="bold")
    sh.text(*Ms(40, pt + 19.5), "base rail on pad", size=1.7)
    jx, jy = Ms(f + fl * 0.4, pt + fl * 0.4)
    weld_symbol(sh, jx, jy, jx + 8, jy - 6, ref=14, kind="fillet", size="%g" % fl)
    sh.text(jx + 23.5, jy - 5.4, "inner", size=1.6, c=THIN)
    notes(x, y, ["Outer edges flush with the frame: seal weld,", "grind flush. Weld with the four pads clamped",
                 "to the flat table (coplanar). Castor bolts: plate",
                 "t + %g max - must NOT reach the rail walls." % pt])
    # ---------------------------------------------------------------- F: rivnut
    x, y = cell(2, 1, "F  M6 RIVNUT PANEL FIXING", "proportional, NTS")
    k = 2.0
    ply_t, mlv_t = wm["P"]["ply_t"], wm["P"]["mlv_t"]
    stack = ply_t + mlv_t
    bl = 35
    M = mapper(x + 36, y + 56, k)
    box_m(M, -15, -t, 15, 0, sw=0.3, fill="url(#hatch)")                    # SHS wall
    box_m(M, -F["rivnut_hole"] / 2, -t, F["rivnut_hole"] / 2, 0, sw=0, fill="#ffffff", c="none")
    box_m(M, -15, 0, 15, mlv_t, sw=0.3, fill="#3a3d42")                     # MLV
    box_m(M, -15, mlv_t, 15, stack, sw=0.3, fill="url(#ply)")               # ply
    box_m(M, -6.5, 0, 6.5, 1.0, sw=0.25, fill="#b8c0c8")                    # rivnut flange (beds into the MLV)
    poly_m(M, [(-4.5, 0), (-4.5, -3), (-5.8, -4.5), (-4.5, -6), (-4.5, -13), (4.5, -13), (4.5, -6), (5.8, -4.5),
               (4.5, -3), (4.5, 0)], w=0.25, fill="#c8d0d8", close=True)    # body with the set bulge
    box_m(M, -3, stack - bl, 3, stack, sw=0.25, fill="#8a9097")             # bolt shank
    box_m(M, -6.5, stack, 6.5, stack + 1.0, sw=0.25, fill="#6f767e")        # flange
    sh.path("M %.2f %.2f Q %.2f %.2f %.2f %.2f" % (*M(-5.5, stack + 1.0), *M(0, stack + 5.2), *M(5.5, stack + 1.0)),
            w=0.25, fill="#6f767e")
    for yy in (-7, -9, -11):
        poly_m(M, [(-3, yy), (3, yy - 0.8)], w=0.12, c="#ffffff")
    zigzag(sh, *M(-15, -t - 2), *M(-15, stack + 2))
    zigzag(sh, *M(15, -t - 2), *M(15, stack + 2))
    lx = M(15, 0)[0] + 2
    sh.text(lx, M(0, (mlv_t + stack) / 2)[1] + 0.6, "ply %g" % ply_t, size=1.7)
    sh.text(lx, M(0, mlv_t / 2)[1] + 0.6, "MLV %g" % mlv_t, size=1.7)
    sh.text(lx, M(0, -t / 2)[1] + 1.4, "SHS wall %g" % t, size=1.7)
    sh.text(lx, M(0, -9)[1], "rivnut M6", size=1.7)
    sh.text(lx, M(0, -9)[1] + 2.6, "hole D%.1f" % F["rivnut_hole"], size=1.7)
    sh.text(*M(0, stack + 7.5), "M6 x %d flanged button head" % bl, size=1.8, anchor="middle", weight="bold")
    sh.text(*M(-7, -15.5), "tube bore", size=1.6, anchor="end", c=THIN)
    notes(x, y, ["Drill before welding, deburr. Fit rivnuts", "(steel, flat head, grip 0.5-3) after coating.",
                 "Bolt: panel %g + %d = M6 x %d; check 6 min" % (stack, bl - stack, bl),
                 "engaged. Acoustic sealant under every panel."])
    # ---------------- WPS + tolerances + finish (right column)
    x0 = 280
    heading(sh, x0, 16, "WELDING PROCEDURE (WPS-lite)")
    rows = [("Process", "GMAW (MIG), short-circuit transfer"),
            ("Wire", "ER70S-6 (AWS A5.18) ~ ISO 14341-A G 42 4 M21 3Si1, 0.8"),
            ("Gas", "Ar + 15-18% CO2 (e.g. Argoshield Light), 12-15 L/min"),
            ("Start settings", "17-18.5 V, WFS 4.5-6 m/min (~70-100 A)"),
            ("", "stick-out 8-10, push 10-15 deg - prove on a coupon"),
            ("Fillet", "%g leg (%.1f throat) on %g wall; tacks 6-8 long" % (fl, fl * 0.707, t)),
            ("Positions", "1F/1G, 2F; short 3F uphill OK; no overhead"),
            ("Preheat / PWHT", "none (C350L0, t < 10)"),
            ("Heat / distortion", "balanced order (joint IDs), cool between"),
            ("Standard", "AS/NZS 1554.1 category GP"),
            ("Inspection", "100% visual: no cracks, burn-through, LOF;"),
            ("", "undercut <= 0.5; no porosity on ground faces"),
            ("Galvanised stock", "grind zinc 25 each side, fume extraction")]
    y = table(sh, x0, 18, [(30, "l"), (96, "l")], rows, size=1.85, rh=3.45, zebra=True)
    heading(sh, x0, y + 6, "FABRICATION TOLERANCES")
    rows = [("Cut length (same mark matched <= 0.5)", "+/-0.5"),
            ("Cut squareness across 30 face", "<= 0.5"),
            ("Rail levels from datum A", "+/-1"),
            ("Outside W x D x H", "+/-1.5"),
            ("Face diagonals (equal)", "+/-2"),
            ("Side frame diagonals (equal)", "+/-1.5"),
            ("Panel faces flat (straight-edge)", "<= 2"),
            ("Twist / pads coplanar", "<= 1"),
            ("Rivnut hole positions", "+/-1"),
            ("Member straightness", "L/1000")]
    y = table(sh, x0, y + 8, [(96, "l"), (30, "c")], rows, size=1.85, rh=3.45)
    heading(sh, x0, y + 6, "FINISH")
    y = paragraph(sh, x0, y + 11, [
        "Remove spatter; external * faces ground flush (80 grit), edges",
        "broken. Blast Sa 2.5 (or chemical pretreat - tubes are perforated",
        "by rivnut holes: coater to drain and dry them). Zinc-rich primer",
        "+ polyester powder, satin black or RAL 7016. Mask the earth",
        "point. Fit rivnuts after coating; bond frame to PE (M6, star",
        "washer, bare metal) and the 19in strips with 4 mm2 jumpers.",
    ], size=1.85, lh=3.0)
    heading(sh, x0, y + 5, "WELD SYMBOLS (AS 1101.3)")
    ys = y + 9
    for i, (kind, lab) in enumerate((("fillet", "fillet, size = leg"), ("flare", "flare-bevel groove (flush faces)"),
                                     ("square", "square butt / seal run"))):
        sx = x0 + 2
        sh.line(sx, ys + 3 + i * 7, sx + 14, ys + 3 + i * 7, w=0.25)
        c = sx + 5
        if kind == "fillet":
            sh.poly([(c, ys + 3 + i * 7), (c, ys + 5.6 + i * 7), (c + 2.6, ys + 3 + i * 7)], w=0.22, close=True)
        elif kind == "flare":
            sh.line(c, ys + 3 + i * 7, c, ys + 5.6 + i * 7, w=0.22)
            sh.path("M %.2f %.2f Q %.2f %.2f %.2f %.2f" % (c + 2.6, ys + 3 + i * 7, c + 0.4, ys + 3 + i * 7, c + 0.4,
                                                           ys + 5.6 + i * 7), w=0.22)
        else:
            sh.line(c, ys + 3 + i * 7, c, ys + 5.6 + i * 7, w=0.22)
            sh.line(c + 1.4, ys + 3 + i * 7, c + 1.4, ys + 5.6 + i * 7, w=0.22)
        sh.text(sx + 17, ys + 4.6 + i * 7, lab, size=1.8)
    sh.circle(x0 + 72, ys + 3, 1.1, sw=0.22)
    sh.text(x0 + 75, ys + 3.7, "weld all round", size=1.8)
    sh.line(x0 + 70.5, ys + 9.2, x0 + 73.5, ys + 9.2, w=0.22)
    sh.text(x0 + 75, ys + 10, "flush contour;  G = grind", size=1.8)
    sh.text(x0 + 72, ys + 17.6, "Symbol under the line = arrow side.", size=1.8)
    title_block(sh, wm, 4, "Weld details, procedure, tolerances, finish", "details NTS (proportional)")
    return sh


def sheet5(wm):
    sh = Svg()
    border(sh)
    D, F = wm["D"], wm["F"]
    heading(sh, 14, 16, "CUT LIST - %s (all members square cut, deburred)" % WM.DOC_NO)
    rows = []
    tot_m = 0.0
    for mk, ms in wm["marks"].items():
        if not ms:
            continue
        m = ms[0]
        tot_m += m["mass"] * len(ms)
        rows.append((mk, str(len(ms)), describe(m), m["section"], "%.1f" % m["cut"] if m["kind"] != "pad" else "-",
                     str(len(m["holes"])) if m["kind"] != "pad" else "4 M8", "%.2f" % m["mass"],
                     "%.2f" % (m["mass"] * len(ms)), stages(ms), "; ".join(WM.location(q) for q in ms)))
    f = D["frame"]
    rows.append((wm["cap_mark"], "4", "Post top cap", "PL %gx%gx%g" % (f, f, F["cap_t"]), "-", "-",
                 "%.2f" % wm["cap_mass"], "%.2f" % (4 * wm["cap_mass"]), "FINAL", "top of each post"))
    y = table(sh, 14, 18, [(10, "c"), (8, "c"), (46, "l"), (30, "l"), (18, "r"), (13, "c"), (13, "r"), (14, "r"),
                           (15, "c"), (225, "l")], rows,
              head=("MARK", "QTY", "DESCRIPTION", "SECTION", "CUT", "HOLES", "KG EA", "KG", "STAGE", "WHERE"),
              size=1.9, rh=3.6)
    t = wm["totals"]
    sh.text(14, y + 4, "Weldment %.1f kg incl. caps and weld metal (%.2f kg); spacers RS1 %.1f kg loose. SHS cut "
            "lengths of posts are %g short of the frame height (cap PL2 on top)." %
            (t["mass_weldment_kg"], t["weld_metal_kg"], t["mass_spacers_kg"], F["cap_t"]), size=1.9)
    # ---------------- nesting
    y0 = y + 12
    heading(sh, 14, y0, "STOCK NESTING (first-fit, kerf %g, %g trim per bar)" % (F["kerf"], F["trim"]))
    cols = {}
    palette = ["#cfe0f5", "#d7eed9", "#fbe3c4", "#e8d9f2", "#f7d4d4", "#d5eef0", "#f1efc9", "#e3e3e3",
               "#c9e4de", "#f4d6e8", "#dfe8c8", "#d8d8f0", "#f0dcc8", "#cce6f3", "#e6e6e6"]
    for i, mk in enumerate(wm["marks"]):
        cols[mk] = palette[i % len(palette)]
    yy = y0 + 4
    for label, bars, L in (("SHS %s, %.1f m lengths" % (wm["sec_shs"], F["stock_shs"] / 1000), wm["nest_shs"],
                            F["stock_shs"]),
                           ("FB %gx%g, %.1f m lengths" % (D["cleat"], D["cleat_t"], F["stock_fb"] / 1000),
                            wm["nest_fb"], F["stock_fb"])):
        sh.text(14, yy + 2.6, label, size=2.0, weight="bold")
        yy += 4
        kx = 330.0 / L
        for i, b in enumerate(bars):
            x = 30.0
            sh.text(14, yy + 3.2, "bar %d" % (i + 1), size=1.9)
            sh.rect(x, yy, L * kx, 4.4, sw=0.25, fill="#ffffff")
            x += F["trim"] * kx
            for mk, pl in b["pieces"]:
                sh.rect(x, yy, pl * kx, 4.4, sw=0.2, fill=cols.get(mk, "#ddd"))
                sh.text(x + pl * kx / 2, yy + 3.1, "%s %.1f" % (mk, pl), size=fit_text("%s %.1f" % (mk, pl), pl * kx, 1.8),
                        anchor="middle")
                x += (pl + F["kerf"]) * kx
            sh.text(30 + L * kx + 2, yy + 3.1, "offcut %.0f" % b["offcut"], size=1.8)
            yy += 5.6
        yy += 2.5
    # ---------------- purchase + estimate
    y1 = yy + 4
    heading(sh, 14, y1, "FRAME PURCHASE LIST (indicative AUD, Sept 2026 - get quotes)")
    rows, total = purchase_rows(wm)
    y = table(sh, 14, y1 + 2, [(118, "l"), (20, "r"), (14, "c"), (18, "r"), (20, "r")], rows,
              head=("ITEM", "QTY", "UNIT", "AUD/UNIT", "AUD"), size=1.9, rh=3.5)
    sh.text(14, y + 4, "Materials AUD %s (excl. GST). Castors, panels and rack parts are in bom/BOM.md." %
            format(round(total), ","), size=1.9, weight="bold")
    heading(sh, 214, y1, "LABOUR ESTIMATE (one-off, manual; tube-laser members save ~6 h)")
    rows, hrs = labour_rows(wm)
    y = table(sh, 214, y1 + 2, [(100, "l"), (22, "r")], rows, head=("TASK", "HOURS"), size=1.9, rh=3.5)
    sh.text(214, y + 4, "Total ~%.0f h; at AUD %.0f/h ~ AUD %s" % (hrs, PRICE["rate"], format(round(hrs * PRICE["rate"], -1),
                                                                                             ",.0f")),
            size=1.9, weight="bold")
    # ---------------- shop traveller
    y2 = y + 12
    heading(sh, 14, y2, "SHOP TRAVELLER (initial each box as the batch is done)")
    steps = ("CUT", "DEBURR", "DRILL", "PAINT MARK", "BENCH WELD", "FIT + TACK", "WELD", "QC")
    bench = set(q for k in wm["ledges"] if k["stage"] == "BENCH" for q in (k["rail"]["mark"], k["ledge"]["mark"]))
    rows = [(mk, str(len(ms_))) + ("",) * len(steps) for mk, ms_ in wm["marks"].items() if ms_]
    rows.append((wm["cap_mark"], "4") + ("",) * len(steps))
    na = {"DRILL": lambda m: not m["holes"] and m["kind"] != "pad",
          "BENCH WELD": lambda m: m["mark"] not in bench,
          "FIT + TACK": lambda m: m["kind"] == "spacer", "WELD": lambda m: m["kind"] == "spacer"}
    cols = [(12, "c"), (9, "c")] + [(15, "c")] * len(steps)
    yt = table(sh, 14, y2 + 2, cols, rows, head=("MARK", "QTY") + steps, size=1.75, rh=3.5)
    marks = [ms_ for ms_ in wm["marks"].values() if ms_] + [None]
    for i, ms_ in enumerate(marks):
        for j, st in enumerate(steps):
            cx_ = 14 + 21 + j * 15 + 7.5
            cy_ = y2 + 2 + (i + 1) * 3.5 + 1.75
            if ms_ is not None and st in na and na[st](ms_[0]):
                sh.text(cx_, cy_ + 0.6, "n/a", size=1.5, anchor="middle", c=THIN)
            elif ms_ is None and st in ("DRILL", "BENCH WELD", "FIT + TACK"):
                sh.text(cx_, cy_ + 0.6, "n/a", size=1.5, anchor="middle", c=THIN)
            else:
                sh.rect(cx_ - 1.2, cy_ - 1.2, 2.4, 2.4, sw=0.18, fill="#ffffff")
    sh.text(14, yt + 4, "BENCH WELD = F3 ledges onto C1 / C2 / C3 (sheet 3). QC = length, squareness, holes, mark "
            "legible. Keep this sheet with the job.", size=1.8)
    title_block(sh, wm, 5, "Cut list, stock nesting, purchase, labour", "-")
    return sh


def stages(ms):
    st = sorted(set(q["sub"] for q in ms))
    return "SA-L/R" if st == ["SA-L", "SA-R"] else "/".join(st)


def purchase_rows(wm):
    F, t, D = wm["F"], wm["totals"], wm["D"]
    rows, total = [], 0.0

    def add(item, qty, unit, price):
        nonlocal total
        total += qty * price
        rows.append((item, ("%g" % qty) if isinstance(qty, (int, float)) else qty, unit, "%.2f" % price,
                     "%.0f" % (qty * price)))
    add("%s %s, %.1f m length (incl. RS1 spacers)" % (wm["sec_shs"], F["grade"], F["stock_shs"] / 1000),
        len(wm["nest_shs"]), "len", PRICE["shs_bar"])
    add("Flat bar %gx%g, %.1f m length (ledges)" % (D["cleat"], D["cleat_t"], F["stock_fb"] / 1000),
        len(wm["nest_fb"]), "len", PRICE["fb_bar"])
    add("Flat bar %gx%g (castor pads, 4 x %g + saw)" % (D["pad_w"], D["pad_t"], D["pad_w"]), 0.45, "m",
        PRICE["pad_fb_m"])
    add("Flat bar %gx%g (post caps)" % (D["frame"], F["cap_t"]), 0.2, "m", PRICE["cap_fb_m"])
    n_riv = int(math.ceil(t["rivnuts"] * 1.1 / 10.0) * 10)
    add("M6 steel rivnut, flat head, grip 0.5-3 (+10%)", n_riv, "ea", PRICE["rivnut"])
    add("M8 x 12 set screw 8.8 + spring washer (castors)", t["tapped_m8"], "ea", PRICE["m8"])
    add("Welding wire, gas, discs, primer (share)", 1, "lot", PRICE["consumables"])
    add("Blast + zinc primer + powder coat (frame)", 1, "job", PRICE["coat"])
    return rows, total


def labour_rows(wm):
    t = wm["totals"]
    rows = [("Cut + deburr %d SHS + %d FB pieces, plates" % (t["cuts_shs"], t["cuts_fb"]),
             0.5 + (t["cuts_shs"] + t["cuts_fb"] + 8) * 4 / 60.0),
            ("Drill %d rivnut holes, tap %d x M8" % (t["rivnuts"], t["tapped_m8"]),
             t["rivnuts"] * 1.2 / 60.0 + t["tapped_m8"] * 1.5 / 60.0),
            ("Fit + tack SA-L, SA-R", 2.5), ("Fit + tack box, checks", 2.0), ("Ledges (10), pads, caps", 1.5),
            ("Weld %.1f m (repositioning, cooling)" % t["weld_len_m"], max(2.0, t["weld_len_m"] * 0.3)),
            ("Grind external faces flush, dress", 3.0), ("Final inspection, measure, record", 0.75)]
    hrs = sum(h for _, h in rows)
    return [(a, "%.1f" % h) for a, h in rows], hrs


def strip(sh, x, y, L, pos, lab, sub, k=0.1):
    """One drilled face as a bar at 1:10, datum end on the left, hole ordinates above."""
    sh.text(x, y + 4.4, lab, size=2.3, weight="bold")
    sh.text(x, y + 7.4, sub, size=fit_text(sub, 36, 1.55), c=THIN)
    bx, by, bh = x + 40, y + 4.2, 3.0
    sh.rect(bx, by, L * k, bh, sw=0.25, fill="#dde2e8")
    sh.poly([(bx - 0.3, by + bh / 2), (bx - 2.6, by + bh / 2 - 1.4), (bx - 2.6, by + bh / 2 + 1.4)], w=0.1, fill=INK,
            close=True)
    for q in pos:
        hx = bx + q * k
        sh.circle(hx, by + bh / 2, 0.62, sw=0.18, fill="#ffffff")
        sh.line(hx, by - 0.4, hx, by - 1.4, w=0.12)
        sh.text(hx, by - 1.8, "%g" % q, size=1.5, anchor="middle")
    sh.text(bx + L * k + 2.5, by + 2.3, "L %g" % L, size=1.8, weight="bold")


def sheet6(wm):
    sh = Svg()
    border(sh)
    F = wm["F"]
    heading(sh, 14, 16, "DRILLING SCHEDULE - D%.1f holes for M6 steel rivnuts, on the face centreline, positions "
                        "from each member's DATUM END" % F["rivnut_hole"])
    rows, strips = [], []
    for mk, ms in wm["marks"].items():
        if not ms:
            continue
        m = ms[0]
        if m["kind"] == "pad":
            rows.append((mk, str(len(ms)), "plate", "castor bolts", "-",
                         "4x M8 tapped through (6.8 drill), %g square on the pad centre" % F["castor_pcd"]))
            continue
        fl = mark_faces(ms)
        if not fl:
            if m["kind"] in ("post", "rail", "upright"):
                rows.append((mk, str(len(ms)), "-", "no holes", datum_end(m), "-"))
            continue
        for face, use, pos, _ in fl:
            rows.append((mk, str(len(ms)), face, use, datum_end(m), "  ".join("%.1f" % p for p in pos)))
            strips.append((m, len(ms), face, pos))
    y = table(sh, 14, 19, [(11, "c"), (8, "c"), (44, "l"), (80, "l"), (18, "l"), (233, "l")], rows,
              head=("MARK", "QTY", "FACE (position)", "USE", "DATUM END", "POSITIONS (mm from datum end)"),
              size=1.9, rh=3.6)
    # ---------------- piece drawings
    y0 = y + 9
    heading(sh, 14, y0, "PIECE DRILLING (1:10 - datum end on the left, one bar per drilled face)")
    yy = y0 + 1.5
    last = None
    for m, qty, face, pos in strips:
        same = last == m["mark"]
        strip(sh, 14, yy, m["cut"], pos, "" if same else "%s  x%d" % (m["mark"], qty), face)
        last = m["mark"]
        yy += 10.2
    # ---------------- notes (right column)
    x0 = 276
    heading(sh, x0, y0, "FACES AND HANDING")
    fo = wm["frame_outer"]
    y = paragraph(sh, x0, y0 + 5, [
        "Faces are named for the member IN POSITION: outer side = carries a",
        "side panel (x = 0 or %g); rear = rear panel; top = top panel;" % fo[0],
        "bottom = plinth skirt (between the castor pads); inner face of U1 =",
        "19in rail-spacer bolts (RS1, packed 0-4 mm).",
        "",
        "ONE PIECE, TWO POSITIONS: S1 (base or top side rail), C2 (base or",
        "top rear) and C3 (mid / shelf rear or top front) are identical pieces.",
        "As a base rail the second face points DOWN (skirt), as a top rail UP",
        "(top panel). Any piece fits either place until a bench ledge is",
        "welded on (sheet 3) - then paint-mark its position.",
        "",
        "Two drilled faces: the second face's holes sit midway between the",
        "first face's, so rivnut bodies never meet inside the 26 mm bore.",
        "",
        "P2 and P3 are a HANDED PAIR (rear-left / rear-right): lay them out",
        "in position and mark the faces before drilling. All other marks are",
        "identical left / right.",
        "",
        "Datum end: posts and uprights = bottom; side rails S = front end;",
        "cross rails C = left end (seen from the front).",
        "Tube laser: cad/exports/frame_members/<mark>.step has each member",
        "with its holes, datum end at the origin along +X.",
    ], size=1.85, lh=3.05)
    heading(sh, x0, y + 5, "NOT DRILLED HERE (drill on assembly)")
    paragraph(sh, x0, y + 10, [
        "Door hinges (left front post P1, front face) and cam-latch",
        "keepers (right front post): to the hardware bought.",
        "RS1 rail spacers: drill D7 through both walls at assembly to",
        "match the U1 rivnuts (M6 x 50 + packers); 19in strips to suit.",
        "Ply floor / partition / shelf: 10g x 32 wing-tip self-drilling",
        "screws through the ply into the ledges at ~200 pitch.",
        "Earth point: one U1 inner-face rivnut, rear-right upright - mask",
        "D20 during coating, star washer to bare metal.",
    ], size=1.85, lh=3.05)
    title_block(sh, wm, 6, "Drilling schedule + piece drilling drawings", "piece bars 1:10")
    return sh


# ======================================================================= markdown
def write_md(wm, files):
    D, F, t = wm["D"], wm["F"], wm["totals"]
    org, fo = wm["org"], wm["frame_outer"]
    prows, ptotal = purchase_rows(wm)
    lrows, hrs = labour_rows(wm)
    L = ["# SRA-16 welded frame - cut list and weld plan", "",
         "| | |", "|---|---|",
         "| Drawing | %s, 6 sheets (`drawings/%s.pdf`) |" % (WM.DOC_NO, WM.DOC_NO),
         "| Generated | `tools/make_weld_pack.py` from `rack_layout.py` v%s on %s |" % (D.get("version", ""), TODAY),
         "| Frame | %s %s to %s, welded; outside %g W x %g D x %g H mm |" % (
             wm["sec_shs"], F["grade"], F["std"], fo[0], fo[1], fo[2]),
         "| Mass | %.1f kg weldment + %.1f kg loose rail spacers |" % (t["mass_weldment_kg"], t["mass_spacers_kg"]),
         "| Welds | %d SHS joints all round + %d ledge stitch runs + 4 caps + 4 pads, about %.1f m |" % (
             t["joints_shs"], len(wm["ledges"]), t["weld_len_m"]),
         "| Holes | %d x D%.1f for M6 rivnuts, 16 x M8 tapped (castor pads) |" % (t["rivnuts"], F["rivnut_hole"]),
         "", "> **Hold point H1.** The mid rails (S2 at the mid level, C3 mid rear) and the partition ledges carry the "
         "partition at the AC's grille split, **M3 = %.0f mm above datum A** (%.0f mm above the floor). "
         "Tape-check M3 (`docs/DESIGN.md` §3), update `ac_split_z` if needed and re-run `tools/make_weld_pack.py` "
         "before cutting those parts. Everything else can be cut now." % (D["z_split"] - org[2], D["z_split"]), "",
         "## 1. Why 30 x 30 and what changed in the design", "",
         "The frame was bolted 40 x 40 aluminium T-slot. It is now welded %gx%g steel SHS. Because the frame depth is "
         "also the acoustic lining depth, the model now uses %g mm melamine in the frame bays (was 40). The outside "
         "stays %g x %g, so the inside grows to %g x %g mm and the height drops to %.1f mm." % (
             D["frame"], D["frame"], D["frame"], D["ext_w"], D["ext_d"], D["int_w"], D["int_d"], D["ext_h"]),
         "",
         "- **Ledges:** 20 x 3 flat bar, edge-welded, carries the floor, partition and shelf ply. A 20 mm angle does "
         "not fit under the ply inside a 30 mm rail.",
         "- **Castor pads:** %g mm plate under each corner, 4 x M8 tapped. The castors are %g mm high "
         "(`caster_h` %g minus the pad)." % (D["pad_t"], D["caster_h"] - D["pad_t"], D["caster_h"]),
         "- **Rear panel:** one piece. A 30 mm rail has no room to screw two panel edges at a split.",
         "- **19-inch rail spacers (RS1):** cut from the same SHS but **bolted**, not welded. That way the rack width "
         "can be packed out after welding distortion.", "",
         "## 2. Datums", "",
         "- **A:** underside of the base rails (height 0). The castor pads sit %g mm below A." % D["pad_t"],
         "- **B:** front face of the frame (depth 0).",
         "- **C:** left face of the frame, seen from the front (width 0).",
         "",
         "Every cut length and hole position is measured from a member's **datum end**:",
         "",
         "- posts and uprights: bottom end;",
         "- side rails S: front end;",
         "- cross rails C: left end.", "",
         "## 3. Cut list", "",
         "| Mark | Qty | Description | Section | Cut mm | Holes | kg each | Where |", "|---|---:|---|---|---:|---:|---:|---|"]
    for mk, ms in wm["marks"].items():
        if not ms:
            continue
        m = ms[0]
        L.append("| %s | %d | %s | %s | %s | %s | %.2f | %s |" % (
            mk, len(ms), describe(m), m["section"], "%.1f" % m["cut"] if m["kind"] != "pad" else "-",
            len(m["holes"]) if m["kind"] != "pad" else "4 x M8", m["mass"], "; ".join(WM.location(q) for q in ms)))
    L.append("| %s | 4 | Post top cap | PL %gx%gx%g | - | - | %.3f | top of each post |" % (
        wm["cap_mark"], D["frame"], D["frame"], F["cap_t"], wm["cap_mass"]))
    L += ["", "- The posts are cut %g mm short of the frame height; the cap PL2 makes up the difference." % F["cap_t"],
          "- **P2 and P3 are a handed pair:** they have holes on two adjacent faces. All other left/right parts are "
          "identical.",
          "- **Accuracy:** cut each mark as a matched set against a stop (±0.5 mm).", "",
          "## 4. Stock and nesting", "",
          "| Stock | Bar | Pieces (mark length) | Offcut mm |", "|---|---:|---|---:|"]
    for name, bars in (("SHS %s x %.1f m" % (wm["sec_shs"], F["stock_shs"] / 1000), wm["nest_shs"]),
                       ("FB %gx%g x %.1f m" % (D["cleat"], D["cleat_t"], F["stock_fb"] / 1000), wm["nest_fb"])):
        for i, b in enumerate(bars):
            L.append("| %s | %d | %s | %.0f |" % (name, i + 1, ", ".join("%s %.1f" % q for q in b["pieces"]),
                                                   b["offcut"]))
    L += ["", "Nesting allows a %g mm kerf and a %g mm squaring cut at the start of each bar. Most suppliers will "
          "cut the lengths in half for transport; if so, re-nest (it still fits in the same number of bars)." % (
              F["kerf"], F["trim"]), "",
          "## 5. Drilling (before welding)", "",
          "Drill Ø%.1f for M6 steel rivnuts, flat head, grip 0.5-3 mm, on the centreline of each face. "
          "Install the rivnuts **after coating**. `bom/frame_drilling.csv` gives every position; here are the rules:" % F["rivnut_hole"],
          "",
          "- **Pitch and end distance:** at most %g mm apart, first and last %g mm from the member ends." % (
              F["pitch"], F["edge"]),
          "- **Faces:**",
          "  - side panel face of every side-frame member;",
          "  - rear face of the rear posts and rear cross rails;",
          "  - top face of the top rails;",
          "  - bottom face of the base rails, for the skirts, kept %g mm clear of the castor pads." % F["skirt_clear"],
          "- **Members drilled on two faces:** the second face's holes fall midway between the first face's, so the "
          "rivnut bodies (about 14 mm long) never meet inside the 26 mm bore.",
          "- **One piece, two positions:** S1, C2 and C3 are each used at two levels. As a base rail, the second "
          "face points down for the plinth skirt. As a top rail, the same holes point up for the top panel. The "
          "pieces are interchangeable until a bench ledge is welded on.",
          "- **Panel screws:** M6 x 35 flanged button head through 15 mm ply and 3 mm MLV (sheet 4, detail F). "
          "Check at least 6 mm of thread engagement in the rivnut you buy.",
          "- **Rack uprights U1:** the inner face gets 3 rivnuts for the RS1 spacer bolts.",
          "- **Castor pads PL1:** 4 x M8 tapped through on a %g mm square." % F["castor_pcd"],
          "  - Match the pattern to the castor you buy.",
          "  - Bolt length is castor plate thickness + 8 mm at most. The bolt must not come through the pad, because "
          "two of the holes sit under rail walls.", "",
          "## 6. Welding procedure (WPS-lite)", "",
          "| | |", "|---|---|",
          "| Process | GMAW (MIG), short-circuit transfer |",
          "| Wire | ER70S-6 (AWS A5.18), ISO 14341-A G 42 4 M21 3Si1, 0.8 mm |",
          "| Gas | Ar + 15-18 % CO2, 12-15 L/min |",
          "| Starting settings | 17-18.5 V, 4.5-6 m/min wire (about 70-100 A), 8-10 mm stick-out, 10-15° push. "
          "Prove them on an offcut of the same SHS first. |",
          "| Fillet | 3 mm leg on the 2 mm wall. Tacks 6-8 mm long. |",
          "| Positions | Flat and horizontal. Short vertical-up runs are fine. **Never overhead:** roll the work instead. |",
          "| Preheat / PWHT | None |",
          "| Quality | AS/NZS 1554.1 category GP, 100 % visual inspection. |",
          "| Acceptance | No cracks, burn-through or lack of fusion. Undercut 0.5 mm max. No visible porosity on "
          "ground faces. |",
          "| Galvanised (DuraGal) stock | Grind the zinc back 25 mm each side of the joint and use fume extraction. |",
          "",
          "**Every SHS T-joint is welded all round** (sheet 4, details A and B):",
          "",
          "- faces that are **not flush** get a 3 mm fillet;",
          "- **flush faces** form a flare groove between the rounded corners. Fill it;",
          "- flush faces on the **outside of the frame** (marked `*`) carry panels, door seals or pads. **Grind them flat.**",
          "- the **top rails** stand 3 mm above the post tubes, level with the cap. Their top seam is closed "
          "when the cap is welded (T1-T4), so weld only their bottom fillet and side seams in the frame stages.",
          "", "## 7. Build sequence", "",
          "1. **Prepare.**",
          "   - Cut all marks.",
          "   - Drill and deburr (section 5). Tap the pads.",
          "   - Weld the F3 ledges onto C1 (base front), C2 (base rear) and C3 (mid rear, shelf rear) on the bench. "
          "Clamp each rail to a straight-edge and stitch from the centre out.",
          "   - Put each ledge on the face opposite the rear-panel holes, with its top 18 mm below the rail top "
          "(12 mm on the mid rear). The rail top is the face opposite the skirt holes.",
          "   - A ledge fixes the piece to one position, so paint-mark it (C2 BASE REAR and so on).",
          "2. **Side frame SA-L (sheet 2), built flat.**",
          "   1. Lay P1 and P2 down with the drilled outer faces underneath, against a straight stop, %g mm outside to outside." % fo[1],
          "   2. Fit S1 (base, top) and S2 (mid, shelf). The base S1 sits flush with the post bottoms.",
          "   3. Stand U1 on the shelf rail at %s from datum B." % " and ".join(
              "%g" % round(u["min"][1] - org[1], 1) for u in sorted(
                  [m for m in wm["members"] if m["kind"] == "upright" and m["sub"] == "SA-L"],
                  key=lambda q: q["min"][1])),
          "   4. Square every joint.",
          "   5. Check the diagonals: %.1f mm each, equal within 1.5 mm." % math.hypot(fo[1], fo[2]),
          "   6. Tack.",
          "   7. Weld joints L01-L12 in order.",
          "   8. Turn the frame over, weld the outer seams and grind them flush.",
          "   9. Turn it back, inner face up, and stitch the F1/F2 ledges, underside only.",
          "      - Set the ledge heights with an offcut of the real ply on the rail: floor and shelf 18 mm, "
          "partition 12 mm.",
          "3. **Side frame SA-R:** the same process, **opposite hand**.",
          "   - The rear post is P3.",
          "   - Joints R01-R12 mirror L01-L12.",
          "4. **Box (sheet 3), built on its side.**",
          "   1. Lay SA-L flat, inner face up.",
          "   2. Stand the seven C rails in place and clamp them square to the posts.",
          "   3. Lower SA-R on top and tack all 14 joints.",
          "   4. Check the face and body diagonals (table below) and twist.",
          "   5. Weld B01-B14 in order. Roll the box so every joint is flat or horizontal, and let each joint cool.",
          "5. **Pads and caps.**",
          "   1. Turn the frame upside down on the flat table.",
          "   2. Grind the bottom seams flush.",
          "   3. Clamp the four PL1 pads to the table so they are coplanar, then weld PW1-PW4.",
          "   4. Weld the PL2 caps (T1-T4).",
          "   5. Grind all external faces flush.",
          "6. **Inspect, then finish.**",
          "   1. Measure and record the checks.",
          "   2. Blast (Sa 2½), apply zinc-rich primer, then powder coat.",
          "   3. Fit the rivnuts, castors (M8) and RS1 spacers.",
          "   4. Bond the frame to protective earth.", "",
          "## 8. Weld schedule and sequence", "",
          "| Joint | Member end | Welded to | Weld (`*` = grind flush) |", "|---|---|---|---|"]
    for st, js in wm["seq"].items():
        for j in js:
            L.append("| %s | %s | %s | %s |" % (j["id"], mlabel(j["m"]), mlabel(j["n"]), weld_text(j)))
    for k in wm["ledges"]:
        L.append("| %s | %s | %s | 3 fillet x %g @ %g c/c underside, %d stitches + %g returns |" % (
            k["id"], mlabel(k["ledge"]), mlabel(k["rail"]), F["stitch"], F["stitch_pitch"], k["stitches"],
            F["stitch_return"]))
    L += ["| T1-T4 | PL2 caps | posts | Seal weld all round (the cap is flush with the tube), including the 3 mm "
          "of each top-rail end that stands above the tube. Grind flush. |",
          "| PW1-PW4 | PL1 pads | post + two base rails | 3 fillet on the inner edges; seal the outer edges and grind "
          "flush |", "",
          "The order alternates between diagonally opposite joints, which balances the heat input. Let each joint "
          "cool to hand-warm before welding the next one on the same member.", "",
          "## 9. Checks", "", "| Check | Target mm | Tolerance |", "|---|---:|---|"]
    fx, fy, fz = fo
    for a, b, c in (("Side frame diagonals (each)", "%.1f" % math.hypot(fy, fz), "equal ±1.5"),
                    ("Front/rear face diagonals", "%.1f" % math.hypot(fx, fz), "equal ±2"),
                    ("Top/base diagonals", "%.1f" % math.hypot(fx, fy), "equal ±1.5"),
                    ("Body diagonals", "%.1f" % math.sqrt(fx * fx + fy * fy + fz * fz), "equal ±3"),
                    ("Outside W x D x H", "%g x %g x %g" % fo, "±1.5"),
                    ("Rail levels from datum A", "per sheet 2", "±1"),
                    ("Panel faces flat", "-", "≤ 2"),
                    ("Pads coplanar (rock test)", "-", "≤ 1"),
                    ("Front-rear upright spacing (19-inch rails)", "%g" % D["rail_spacing"], "±1")):
        L.append("| %s | %s | %s |" % (a, b, c))
    L += ["", "## 10. Estimate (indicative, Sept 2026)", "",
          "Materials are indicative AUD excluding GST. Get quotes.", "",
          "| Item | Qty | Unit | AUD |", "|---|---:|---|---:|"]
    for r in prows:
        L.append("| %s | %s | %s | %s |" % (r[0], r[1], r[2], r[4]))
    L += ["| **Materials** | | | **%s** |" % format(round(ptotal), ","), "",
          "Labour, for a one-off built by hand:", "",
          "| Task | Hours |", "|---|---:|"]
    for a, h in lrows:
        L.append("| %s | %s |" % (a, h))
    L += ["| **Total** | **%.0f** |" % hrs, "",
          "**Faster options:**", "",
          "- Send the per-member STEP files to a tube-laser service. That saves about 6 h of cutting, marking and drilling.",
          "- For batches, a welding jig built from the side-frame drawing brings fit-up to minutes.",
          "- Either option makes the welded frame far cheaper than T-slot: the T-slot frame used about AUD 700 of "
          "extrusion and brackets.", "",
          "## 11. Files", ""]
    L += ["- `%s`" % f for f in files]
    with open(os.path.join(ROOT, "docs", "FRAME_WELD_PLAN.md"), "w") as fh:
        fh.write("\n".join(L) + "\n")


# ======================================================================= main
def main(argv):
    overrides, do_step, do_pdf = {}, True, True
    for a in argv:
        if a == "--no-step":
            do_step = False
        elif a == "--no-pdf":
            do_pdf = False
        elif "=" in a:
            k, v = a.split("=", 1)
            overrides[k] = float(v)
    wm = WM.build(overrides)
    wm["D"]["version"] = WM.RL.VERSION
    mirror_sa_r(wm)
    probs = WM.check(wm)
    print("weldment: %d members, %d marks, %d joints, %d rivnuts%s" % (
        len(wm["members"]), len(wm["marks"]), len(wm["joints"]), wm["totals"]["rivnuts"],
        "" if not probs else "  PROBLEMS: %s" % probs))
    write_csvs(wm)
    import cadquery  # noqa: F401  (solids for the iso view + STEP)
    solids = build_solids(wm)
    files = ["bom/frame_cut_list.csv", "bom/frame_drilling.csv", "bom/frame_weld_schedule.csv",
             "bom/frame_nesting.csv"]
    if do_step:
        export_steps(wm, solids)
        files += ["cad/exports/SRA16_frame_weldment.step", "cad/exports/frame_members/*.step (one per mark)"]
    ddir = os.path.join(ROOT, "drawings")
    os.makedirs(ddir, exist_ok=True)
    svgs = []
    for i, fn in enumerate((lambda: sheet1(wm, solids), lambda: sheet2(wm), lambda: sheet3(wm), lambda: sheet4(wm),
                            lambda: sheet5(wm), lambda: sheet6(wm))):
        p = os.path.join(ddir, "%s_s%d.svg" % (WM.DOC_NO, i + 1))
        with open(p, "w") as fh:
            fh.write(fn().svg())
        svgs.append(p)
    files += ["drawings/%s_s1..s6.svg" % WM.DOC_NO]
    if do_pdf:
        pdf = os.path.join(ddir, "%s.pdf" % WM.DOC_NO)
        subprocess.run(["node", os.path.join(HERE, "render", "svg2pdf.mjs"), pdf] + svgs, check=True)
        files.insert(0, "drawings/%s.pdf" % WM.DOC_NO)
    write_md(wm, files)
    t = wm["totals"]
    print("wrote %d sheets; weldment %.1f kg, %d SHS bars, weld %.1f m" % (
        len(svgs), t["mass_weldment_kg"], len(wm["nest_shs"]), t["weld_len_m"]))
    return 0 if not probs else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
