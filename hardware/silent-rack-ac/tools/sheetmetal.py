#!/usr/bin/env python3
"""
sheetmetal.py - flat patterns of every laser-cut sheet-metal part of the SRA-16
(pack CP-SRA16-SMP-001), derived from rack_layout.py (skins, doors, hardware)
and tools/weldment.py (the rivnut positions in the welded frame).

Every panel fixing hole is placed on a frame rivnut, and check() proves the
reverse too: each frame rivnut is picked up by at least one sheet part.

Part coordinates (mm): flat blank, origin bottom-left, u to the right, v up,
drawn as seen from OUTSIDE (the face you see when the part is fitted). Folded
parts show the flat blank; bend lines carry direction and radius.
Pure Python (no CAD imports).
"""
import math
import os
import sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import weldment as WM  # noqa: E402

RL = WM.RL
DOC_NO = "CP-SRA16-SMP-001"
REV = "A"
STEEL, SS = 7.85e-6, 7.93e-6          # kg/mm3

# hole sizes and bending (change to suit the shop / hardware)
SM = {
    "frame_screw": 8.0,    # M6 flanged button head into a frame rivnut; +-1 mm float for frame tolerance
    "rivet": 5.0,          # 4.8 mm blind rivet (hinges, latches, keepers)
    "m4": 4.5,             # window clamp bolts, cable grommet
    "m5": 5.5,             # pull handle, exhaust spigot flange
    "rail_bolt": 7.0,      # M6 through the 19in rail, rail spacer and packers into the upright rivnut
    "tap_m8": 6.8,         # castor pad, tapped M8 after cutting
    "k_factor": 0.33,      # air bending mild steel, inside radius = t
    "min_edge": 2.5,       # hole edge to part edge (and >= 1.5 t)
    "sq_hole": 9.5,        # EIA-310 square hole (cage nuts)
    "spigot_pcd": 190.0, "spigot_holes": 4,
    "grommet_pattern": (224.0, 64.0),
    "win_corner_r": 6.0, "slot_r": 5.0,
    # touchscreen pod on the upper door (CP-SRA16-ELC-001): centre (cabinet x, height z), outline,
    # two M4 rivnuts and the cable grommet, relative to the centre
    "pod": {"xc": 135.0, "zc": 1505.0, "w": 128.0, "h": 91.0, "rivnut_d": 6.0, "bolts": ((-46.0, 28.0), (46.0, 28.0)),
            "cable": (-30.0, -22.0), "cable_d": 20.0},
}

MATERIALS = OrderedDict([
    ("skin", {"name": "Steel sheet (Zincanneal or CR4)", "finish": "powder coat RAL 7035 both sides", "rho": STEEL}),
    ("sm", {"name": "Steel sheet (Zincanneal or CR4)", "finish": "powder coat RAL 7035", "rho": STEEL}),
    ("s20", {"name": "Steel sheet (CR4)", "finish": "zinc plate (keep cage-nut holes clear)", "rho": STEEL}),
    ("ss12", {"name": "Stainless 304 sheet, 2B", "finish": "as cut, TIG-weld corners, passivate", "rho": SS}),
    ("pl3", {"name": "Steel plate (grade 250)", "finish": "welded to frame, coated with it", "rho": STEEL}),
    ("pl8", {"name": "Steel plate (grade 250)", "finish": "welded to frame, coated with it", "rho": STEEL}),
])


def bend_math(t, R=None, K=None, ang=90.0):
    R = t if R is None else R
    K = SM["k_factor"] if K is None else K
    a = math.radians(ang)
    ba = a * (R + K * t)
    ossb = (R + t) * math.tan(a / 2.0)
    return {"R": R, "BA": ba, "OSSB": ossb, "BD": 2 * ossb - ba}


def rect(u0, v0, u1, v1):
    return [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]


def rrect(u0, v0, u1, v1, r):
    """Rounded rectangle as (points, bulges) for an LWPOLYLINE; r = 0 gives a plain rectangle."""
    if r <= 0:
        return {"pts": rect(u0, v0, u1, v1), "bulge": [0.0] * 4}
    b = math.tan(math.pi / 8.0)                      # 90 deg arc, CCW
    pts = [(u0 + r, v0), (u1 - r, v0), (u1, v0 + r), (u1, v1 - r), (u1 - r, v1), (u0 + r, v1), (u0, v1 - r), (u0, v0 + r)]
    return {"pts": pts, "bulge": [0, b, 0, b, 0, b, 0, b]}


def arc_pts(p0, p1, bulge, n=8):
    """Points along an LWPOLYLINE segment p0 -> p1 with the given bulge (excluding p0, including p1)."""
    if abs(bulge) < 1e-12:
        return [p1]
    (x0, y0), (x1, y1) = p0, p1
    theta = 4 * math.atan(bulge)
    c = math.dist(p0, p1)
    r = c / (2 * math.sin(abs(theta) / 2))
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    d = math.sqrt(max(r * r - (c / 2) ** 2, 0.0))
    ux, uy = (x1 - x0) / c, (y1 - y0) / c
    sgn = 1 if bulge > 0 else -1
    cx, cy = mx - sgn * d * uy, my + sgn * d * ux
    a0 = math.atan2(y0 - cy, x0 - cx)
    return [(cx + r * math.cos(a0 + theta * i / n), cy + r * math.sin(a0 + theta * i / n)) for i in range(1, n + 1)]


def loop_pts(loop, n=8):
    """A closed LWPOLYLINE loop (pts + bulges) as a plain polygon, arcs split into n chords."""
    pts, bl = loop["pts"], loop["bulge"]
    out = [pts[0]]
    for i in range(len(pts)):
        out += arc_pts(pts[i], pts[(i + 1) % len(pts)], bl[i], n)
    return out[:-1]


def notched_rect(w, h, bottom=(), top=(), r=4.0, off=0.5):
    """Blank w x h with semicircular screw notches in the bottom / top edge at the given u. Each notch
    centre sits `off` beyond the edge: two skins meeting with a 2*off gap on a rail share one D2r
    clearance for the joint strip's screw."""
    a = math.sqrt(r * r - off * off)
    b = -math.tan((math.pi - 2 * math.asin(off / r)) / 4.0)      # clockwise arc, into the part
    pts, bl = [(0.0, 0.0)], [0.0]
    for u in sorted(bottom):
        pts += [(u - a, 0.0), (u + a, 0.0)]
        bl += [b, 0.0]
    pts += [(w, 0.0), (w, h)]
    bl += [0.0, 0.0]
    for u in sorted(top, reverse=True):
        pts += [(u + a, h), (u - a, h)]
        bl += [b, 0.0]
    pts.append((0.0, h))
    bl.append(0.0)
    return {"pts": pts, "bulge": bl}


class Part:
    def __init__(self, pid, name, mat, t, qty, w, h, where, view="outside face shown"):
        self.id, self.name, self.mat, self.t, self.qty = pid, name, mat, t, qty
        self.w, self.h, self.where, self.view = w, h, where, view
        self.outline = {"pts": rect(0, 0, w, h), "bulge": [0.0] * 4}
        self.holes = []          # dict(u, v, d, use, src)
        self.cuts = []           # dict(pts, bulge, use)
        self.squares = []        # dict(u, v, a, use)  square holes
        self.bends = []          # dict(u0, v0, u1, v1, dir, R, note)
        self.notes = []
        self.also = []           # frame holes picked up by the mirrored twin (same blank, other hand)
        self.twin_place = None   # where the mirrored twin sits (drawn flipped on the elevations)
        self.min_edge = None     # override of SM["min_edge"] / 1.5 t where a standard fixes the web
        self.place = None        # (face, du, dv): position on the exterior elevation, v from datum A
        self.hold = ""           # tape check this part waits on (e.g. "M3"), from tape_hold()

    def hole(self, u, v, d, use, src=None):
        self.holes.append({"u": u, "v": v, "d": d, "use": use, "src": src})

    def area(self):
        pts = loop_pts(self.outline)
        a = 0.5 * abs(sum(pts[i][0] * pts[i - 1][1] - pts[i - 1][0] * pts[i][1] for i in range(len(pts))))
        a -= sum(math.pi * h["d"] ** 2 / 4.0 for h in self.holes)
        a -= sum(q["a"] ** 2 for q in self.squares)
        for c in self.cuts:
            p = c["pts"]
            a -= 0.5 * abs(sum(p[i][0] * p[i - 1][1] - p[i - 1][0] * p[i][1] for i in range(len(p))))
        return a

    def mass(self):
        return self.area() * self.t * MATERIALS[self.mat]["rho"]

    def cut_length(self):
        def per(pts):
            return sum(math.dist(pts[i], pts[i - 1]) for i in range(len(pts)))
        L = per(loop_pts(self.outline)) + sum(math.pi * h["d"] for h in self.holes) + sum(4 * q["a"] for q in self.squares)
        return L + sum(per(c["pts"]) for c in self.cuts)

    def pierces(self):
        return 1 + len(self.holes) + len(self.squares) + len(self.cuts)


def merge_twins(a, b):
    """If part b is part a flipped (u -> w - u), keep a with qty a+b and remember b's frame holes."""
    def sig(p, mirror):
        hs = sorted((round(p.w - h["u"] if mirror else h["u"], 1), round(h["v"], 1), h["d"]) for h in p.holes)
        cs = sorted(tuple(sorted((round(p.w - x if mirror else x, 1), round(y, 1)) for x, y in c["pts"]))
                    for c in p.cuts)
        os_ = sorted((round(p.w - x if mirror else x, 1), round(y, 1)) for x, y in p.outline["pts"])
        return hs, cs, os_
    if (a.w, a.h) == (b.w, b.h) and sig(a, True) == sig(b, False):
        a.qty += b.qty
        a.also += [h["src"] for h in b.holes if h["src"]] + b.also
        a.twin_place = b.place
        return [a]
    b.id += "R"
    return [a, b]


# ---------------------------------------------------------------- frame rivnuts
def frame_holes(wm):
    """All rivnut holes of the weldment: dict(key, use, p (3D), k, sg, member)."""
    out = []
    for m in wm["members"]:
        for i, h in enumerate(m["holes"]):
            out.append({"key": (m["name"], i), "use": h["use"], "p": h["p"], "k": h["k"], "sg": h["sg"],
                        "member": m})
    return out


def build(P=None):
    P = RL.resolve(P)
    D = RL.derive(P)
    wm = WM.build(P)
    fh = frame_holes(wm)
    W, DP, s = D["ext_w"], D["ext_d"], D["skin"]
    sk, st, sw2 = D["skin_t"], D["strip_t"], D["strip_w"] / 2.0
    zb0, zt1 = D["z_base0"], D["z_toprail1"]
    HW = RL.HW
    fs = SM["frame_screw"]
    parts = []

    def piece_z(cuts):
        zs = [zb0] + list(cuts) + [zt1]
        return [(zs[i] + (0.5 if i else 0.0), zs[i + 1] - (0.5 if i < len(zs) - 2 else 0.0)) for i in range(len(zs) - 1)]

    def add_frame_holes(pt, sel, to_uv, u0, v0, u1, v1, avoid=()):
        """Frame rivnut holes inside the rectangle (u0..u1, v0..v1) of part pt (keeps edge distance)."""
        e = fs / 2.0 + max(SM["min_edge"], 1.5 * pt.t)
        for h in fh:
            if not sel(h):
                continue
            u, v = to_uv(h["p"])
            if u0 + e - 1e-6 <= u <= u1 - e + 1e-6 and v0 + e - 1e-6 <= v <= v1 - e + 1e-6:
                if any(abs(h["p"][2] - a) < 1.0 for a in avoid):
                    continue
                pt.hole(u - u0, v - v0, fs, "M6 screw to frame rivnut (%s)" % WM.FACE_USE[h["use"]].lower(), h["key"])

    def joint_us(sel, uv, zj):
        """u of the rail rivnuts on a skin joint at zj (the strip's screws pass between the two skins)."""
        us = []
        for h in fh:
            if sel(h) and abs(h["p"][2] - zj) < 1.0:
                assert abs(h["p"][2] - zj) < 0.01, "joint %.2f is off the rail rivnut line %.2f" % (zj, h["p"][2])
                us.append(uv(h["p"])[0])
        return us

    def notch_joints(pt, sel, uv, i, splits):
        """Notch piece i of a split skin where it meets its neighbours (D8 clearance around each strip screw)."""
        lo = joint_us(sel, uv, splits[i - 1]) if i > 0 else []
        hi = joint_us(sel, uv, splits[i]) if i < len(splits) else []
        if lo or hi:
            pt.outline = notched_rect(pt.w, pt.h, lo, hi, fs / 2.0, 0.5)
            pt.notes.append("R%g notches on the joint edge(s) clear the joint strip's M6 screws." % (fs / 2.0))

    def left_face(h):
        return h["use"] == "side" and h["k"] == 0 and h["sg"] < 0

    def right_face(h):
        return h["use"] == "side" and h["k"] == 0 and h["sg"] > 0

    # ---------------------------------------------------------------- side skins + joint strips
    side_w = DP - 2 * s
    uv_left = lambda p: ((DP - s) - p[1], p[2])            # noqa: E731  seen from the left: front on the right
    uv_right = lambda p: (p[1] - s, p[2])                  # noqa: E731  seen from the right: front on the left
    names = ["bottom", "middle", "top", "4", "5"]
    splits = D["side_splits"]
    for tag, sel, uv, hw in (("L", left_face, uv_left, "hinge"), ("R", right_face, uv_right, "latch")):
        for i, (za, zb) in enumerate(piece_z(splits)):
            pt = Part("S%s%d" % (tag, i + 1), "Side skin %s - %s" % ("left" if tag == "L" else "right", names[i]),
                      "skin", sk, 1, side_w, zb - za,
                      "%s side, frame z %.1f-%.1f above datum A" % ("left" if tag == "L" else "right", za - zb0, zb - zb0))
            add_frame_holes(pt, sel, uv, 0, za, side_w, zb, avoid=splits)
            notch_joints(pt, sel, uv, i, splits)
            pt.place = ("left" if tag == "L" else "right", s, za - zb0)
            yh = D["hw_y_side"]
            if hw == "hinge":
                for zc in D["hinge_z_lower"] + D["hinge_z_upper"]:
                    for dz in HW["hinge_holes"]:
                        if za < zc + dz < zb:
                            u, v = uv((0, yh, zc + dz))
                            pt.hole(u, v - za, SM["rivet"], "rivet, hinge frame leaf")
            else:
                for zc in D["latch_z_lower"] + D["latch_z_upper"]:
                    for dy, dz in HW["latch_holes"]:
                        if za < zc + dz < zb:
                            u, v = uv((0, yh + dy, zc + dz))
                            pt.hole(u, v - za, SM["rivet"], "rivet, toggle latch base")
            pt.notes.append("MLV (3 mm) is one piece per side, bonded across the joints; strips JS cover the joints.")
            parts.append(pt)
    for j, zj in enumerate(splits):
        twins = []
        for sel, uv in ((left_face, uv_left), (right_face, uv_right)):
            pt = Part("JS%d" % (j + 1), "Joint strip, side skins - %s rail" % ("mid" if j == 0 else "shelf"), "sm",
                      st, 1, side_w, 2 * sw2, "over the side-skin joint on the %s rail (right side: same part, flipped)"
                      % ("mid" if j == 0 else "shelf"))
            add_frame_holes(pt, sel, uv, 0, zj - sw2, side_w, zj + sw2)
            pt.place = ("left" if sel is left_face else "right", s, zj - sw2 - zb0)
            twins.append(pt)
        parts += merge_twins(*twins)

    # ---------------------------------------------------------------- rear skin + strip
    rear_face = lambda h: h["use"] == "rear"               # noqa: E731
    uv_rear = lambda p: (W - p[0], p[2])                    # noqa: E731  seen from behind
    for i, (za, zb) in enumerate(piece_z(D["rear_splits"])):
        pt = Part("RP%d" % (i + 1), "Rear skin - %s" % ("bottom", "top", "3")[i], "skin", sk, 1, W, zb - za,
                  "rear, frame z %.1f-%.1f above datum A" % (za - zb0, zb - zb0))
        add_frame_holes(pt, rear_face, uv_rear, 0, za, W, zb, avoid=D["rear_splits"])
        notch_joints(pt, rear_face, uv_rear, i, D["rear_splits"])
        pt.place = ("rear", 0, za - zb0)
        ex, ez = D["exh_x"], D["exh_run_z"]
        if za < ez < zb:
            u, v = W - ex, ez - za
            pt.hole(u, v, 2 * (D["exh_ri"] + 1), "exhaust duct D150")
            r = SM["spigot_pcd"] / 2.0
            for k in range(SM["spigot_holes"]):
                a = math.radians(45 + 360.0 * k / SM["spigot_holes"])
                pt.hole(u + r * math.cos(a), v + r * math.sin(a), SM["m5"], "M5, exhaust spigot flange")
        zt0 = D["z_toprail0"]
        sx0, sx1, sz0, sz1 = D["x_mid"] - 100, D["x_mid"] + 100, zt0 - 146, zt0 - 106
        if za < sz0 and sz1 < zb:
            pt.cuts.append(dict(rrect(W - sx1, sz0 - za, W - sx0, sz1 - za, SM["slot_r"]), use="cable entry 200x40"))
            gu, gv = SM["grommet_pattern"]
            cu, cv = W - D["x_mid"], (sz0 + sz1) / 2.0 - za
            for du in (-gu / 2, gu / 2):
                for dv in (-gv / 2, gv / 2):
                    pt.hole(cu + du, cv + dv, SM["m4"], "M4, brush cable grommet")
        parts.append(pt)
    for j, zj in enumerate(D["rear_splits"]):
        pt = Part("JR%d" % (j + 1), "Joint strip, rear skin", "sm", st, 1, W, 2 * sw2, "over the rear-skin joint")
        add_frame_holes(pt, rear_face, uv_rear, 0, zj - sw2, W, zj + sw2)
        pt.place = ("rear", 0, zj - sw2 - zb0)
        parts.append(pt)

    # ---------------------------------------------------------------- top skin
    pt = Part("TP1", "Top skin", "skin", sk, 1, W, DP, "top, over the top rails and post caps (front at the bottom)",
              view="seen from above, front edge at the bottom")
    add_frame_holes(pt, lambda h: h["use"] == "top", lambda p: (p[0], p[1]), 0, 0, W, DP)
    pt.place = ("top", 0, 0)
    parts.append(pt)

    # ---------------------------------------------------------------- doors
    hp = HW["handle_pitch"]
    zds = D["z_door_split"]
    for pid, nm, (dz0, dz1), hz, lz, h0 in (
            ("DL1", "Door, lower (AC bay)", D["door_lo_z"], D["hinge_z_lower"], D["latch_z_lower"], zb0 + 380),
            ("DU1", "Door, upper (rack)", D["door_up_z"], D["hinge_z_upper"], D["latch_z_upper"], zds + 300)):
        pt = Part(pid, nm, "skin", sk, 1, W, dz1 - dz0, "front, frame z %.1f-%.1f above datum A" % (dz0 - zb0, dz1 - zb0),
                  view="seen from the front")
        pt.place = ("front", 0, dz0 - zb0)
        for zc in hz:
            for dz in HW["hinge_holes"]:
                pt.hole(D["hw_x_left"], zc + dz - dz0, SM["rivet"], "rivet, hinge door leaf (+ stiffener)")
        for zc in lz:
            for dz in HW["keeper_rivets"]:
                pt.hole(D["hw_x_right"], zc + dz - dz0, SM["rivet"], "rivet, latch keeper KB1 (+ stiffener)")
        for dz in (10.0, hp + 10.0):
            pt.hole(D["hw_x_right"], h0 + dz - dz0, SM["m5"], "M5, pull handle (screws from inside)")
        if pid == "DU1":
            pd = SM["pod"]
            for du, dv in pd["bolts"]:
                pt.hole(pd["xc"] + du, pd["zc"] + dv - dz0, pd["rivnut_d"], "M4 rivnut, touchscreen pod (ELC-001)")
            pt.hole(pd["xc"] + pd["cable"][0], pd["zc"] + pd["cable"][1] - dz0, pd["cable_d"],
                    "touchscreen cable, rubber grommet (ELC-001)")
        if pid == "DL1":
            wx0, wz0 = D["win_xc"] - D["win_w"] / 2, D["win_zc"] - D["win_h"] / 2
            pt.cuts.append(dict(rrect(wx0, wz0 - dz0, wx0 + D["win_w"], wz0 + D["win_h"] - dz0, SM["win_corner_r"]),
                                use="window %gx%g" % (D["win_w"], D["win_h"])))
            for du, dv in window_bolts(D):
                pt.hole(D["win_xc"] + du, D["win_zc"] + dv - dz0, SM["m4"], "M4, window clamp")
        pt.notes.append("Bond the DA stiffener frame inside (legs inboard), then rivet hinges/keepers through both.")
        parts.append(pt)

    # ---------------------------------------------------------------- door stiffener angles (folded L)
    ds, t15 = D["door_stiff"], D["strip_t"]
    bm = bend_math(t15)
    flat = 2 * ds - bm["BD"]
    bl = ds - bm["OSSB"] + bm["BA"] / 2.0
    zb1, zs0, zs1, zt0 = D["z_base1"], D["z_srail0"], D["z_srail1"], D["z_toprail0"]
    for pid, nm, (oz0, oz1), hz, lz, h0 in (
            ("DA1", "lower door", (zb1, zs0), D["hinge_z_lower"], D["latch_z_lower"], zb0 + 380),
            ("DA3", "upper door", (zs1, zt0), D["hinge_z_upper"], D["latch_z_upper"], zds + 300)):
        z0, z1 = oz0 + RL.DOOR_CLEAR, oz1 - RL.DOOR_CLEAR
        L = z1 - z0
        for side, pid_, zlist in (("left", pid, hz), ("right", pid[:2] + str(int(pid[2]) + 1), lz)):
            pt = Part(pid_, "Door stiffener, %s, %s vertical" % (nm, side), "sm", t15, 1, L, flat,
                      "inside the %s, %s edge; flat leg bonded to the skin, leg inboard" % (nm, side),
                      view="flat blank; the bonded leg is v < bend")
            pt.bends.append({"u0": 0, "v0": bl, "u1": L, "v1": bl, "dir": "UP", "R": bm["R"], "ang": 90})
            off = ds / 2.0                                   # rivet line on the bonded leg (centre of the leg)
            if side == "left":
                for zc in zlist:
                    for dz in HW["hinge_holes"]:
                        pt.hole(zc + dz - z0, off, SM["rivet"], "rivet, hinge (through door skin)")
            else:
                for zc in zlist:
                    for dz in HW["keeper_rivets"]:
                        pt.hole(zc + dz - z0, off, SM["rivet"], "rivet, latch keeper (through door skin)")
                for dz in (10.0, hp + 10.0):
                    pt.hole(h0 + dz - z0, off, SM["m5"], "M5, pull handle screw")
            parts.append(pt)
    Lh = (D["stiff_x1"] - D["stiff_x0"]) - 2 * ds
    pt = Part("DA5", "Door stiffener, horizontal (top/bottom, both doors)", "sm", t15, 4, Lh, flat,
              "inside each door, top and bottom, between the verticals", view="flat blank")
    pt.bends.append({"u0": 0, "v0": bl, "u1": Lh, "v1": bl, "dir": "UP", "R": bm["R"], "ang": 90})
    parts.append(pt)

    # ---------------------------------------------------------------- latch keeper bracket (folded L)
    kg, kb = HW["keeper_gap"], HW["keeper_leg_b"]
    A = (W + kg + t15) - (D["hw_x_right"] - 14.0)
    B = kb + t15
    kh = HW["keeper_h"]
    pt = Part("KB1", "Latch keeper bracket", "sm", t15, len(D["latch_z_lower"]) + len(D["latch_z_upper"]),
              A + B - bm["BD"], kh, "door front face at the right edge, wraps round to the side",
              view="flat blank, door leg on the left")
    blk = A - bm["OSSB"] + bm["BA"] / 2.0
    pt.bends.append({"u0": blk, "v0": 0, "u1": blk, "v1": kh, "dir": "UP", "R": bm["R"], "ang": 90})
    for dz in HW["keeper_rivets"]:
        pt.hole(14.0, kh / 2.0 + dz, SM["rivet"], "rivet to door + stiffener")
    cy, cw, ch = HW["catch"]
    cu = pt.w - (kb - cy)                                   # catch centre from leg B's free edge
    pt.cuts.append(dict(rrect(cu - cw / 2, kh / 2 - ch / 2, cu + cw / 2, kh / 2 + ch / 2, cw / 2 - 0.01),
                        use="latch catch slot"))
    parts.append(pt)

    # ---------------------------------------------------------------- window retainer
    gw, gh = D["win_w"] + 40, D["win_h"] + 40
    pt = Part("WR1", "Window retainer frame", "sm", t15, 1, gw, gh, "inside the lower door, clamps the glazing unit")
    pt.cuts.append(dict(rrect(20, 20, gw - 20, gh - 20, SM["win_corner_r"]), use="window opening"))
    for du, dv in window_bolts(D):
        pt.hole(gw / 2 + du, gh / 2 + dv, SM["m4"], "M4, window clamp")
    parts.append(pt)

    # ---------------------------------------------------------------- plinth skirts (folded L)
    SK = RL.SKIRT
    kt = D["strip_t"]
    bk = bend_math(kt)
    face = zb0 - SK["floor_gap"]
    fl = SK["flange"]
    fw = face + fl - bk["BD"]
    blf = face - bk["OSSB"] + bk["BA"] / 2.0
    xa, xb = s + D["pad_w"] + SK["pad_gap"], W - s - D["pad_w"] - SK["pad_gap"]
    ya, yb = s + D["pad_w"] + SK["pad_gap"], DP - s - D["pad_w"] - SK["pad_gap"]
    sz0, sz1 = SK["slot_z"]

    def slots(a0, a1, pitch, w, skip=None):
        n = int((a1 - a0 - 50 + (pitch - w)) // pitch)
        c0 = (a0 + a1) / 2.0 - (n - 1) * pitch / 2.0
        out = [c0 + i * pitch for i in range(n)]
        return [c for c in out if skip is None or abs(c - skip) > w / 2 + 20]

    def skirt(pid, nm, qty, a0, a1, sel, to_ua, dist, slot_c, slot_w, where, drain=None):
        L = a1 - a0
        pt = Part(pid, nm, "sm", kt, qty, L, fw, where, view="outside face, flange folds away at the top")
        pt.bends.append({"u0": 0, "v0": blf, "u1": L, "v1": blf, "dir": "DOWN", "R": bk["R"], "ang": 90})
        for c in slot_c:
            u = to_ua(c)
            pt.cuts.append(dict(rrect(u - slot_w / 2, sz0 - SK["floor_gap"], u + slot_w / 2, sz1 - SK["floor_gap"],
                                      SM["slot_r"]), use="air slot"))
        vflange = fw - (fl - dist)                           # hole row: dist from the face, measured on the flange
        for h in fh:
            if sel(h):
                u = to_ua(h["p"][0] if pid in ("SK1", "SK2") else h["p"][1])
                if 0 <= u <= L:
                    pt.hole(u, vflange, fs, "M6 screw up into base-rail rivnut", h["key"])
        if drain is not None:
            pt.hole(to_ua(drain[0]), drain[1] - SK["floor_gap"], SK["drain_d"], "drain barb bulkhead")
        return pt
    dist = (s + D["frame"] / 2.0) - SK["inset"]              # rail centreline from the skirt face
    dox = D["drain_out_x"]
    parts.append(skirt("SK1", "Plinth skirt, front", 1, xa, xb,
                       lambda h: h["use"] == "skirt" and h["k"] == 2 and h["member"]["name"] == "Rail Base front",
                       lambda x: x - xa, dist, slots(xa, xb, SK["pitch_fr"], SK["slot_fr"]), SK["slot_fr"],
                       "front, under the base rail between the castor pads"))
    parts.append(skirt("SK2", "Plinth skirt, rear (drain outlet)", 1, xa, xb,
                       lambda h: h["use"] == "skirt" and h["k"] == 2 and h["member"]["name"] == "Rail Base rear",
                       lambda x: xb - x, dist, slots(xa, xb, SK["pitch_fr"], SK["slot_fr"], skip=dox),
                       SK["slot_fr"], "rear, under the base rail (seen from behind)", drain=(dox, D["drain_out_z"])))
    ss = slots(ya, yb, SK["pitch_side"], SK["slot_side"])
    parts += merge_twins(
        skirt("SK3", "Plinth skirt, side (right: same part turned round)", 1, ya, yb,
              lambda h: h["use"] == "skirt" and h["k"] == 2 and h["member"]["name"] == "Rail Base left",
              lambda y: yb - y, dist, ss, SK["slot_side"], "left and right, under the side base rails"),
        skirt("SK3", "Plinth skirt, side (right: same part turned round)", 1, ya, yb,
              lambda h: h["use"] == "skirt" and h["k"] == 2 and h["member"]["name"] == "Rail Base right",
              lambda y: y - ya, dist, ss, SK["slot_side"], "left and right, under the side base rails"))

    # ---------------------------------------------------------------- drip tray (stainless pan, TIG corners)
    X0, X1, Y0, Y1 = D["x_in0"], D["x_in1"], D["y_in0"], D["y_in1"]
    tt = 1.2
    bt = bend_math(tt)
    hgt = D["tray_t"] + D["tray_lip"]                       # outside height of the upstand
    Wt, Dt = (X1 - X0) + 2 * hgt - 2 * bt["BD"], (Y1 - Y0) + 2 * hgt - 2 * bt["BD"]
    pt = Part("DT1", "Drip tray (304 stainless pan)", "ss12", tt, 1, Wt, Dt, "bay floor, inside the frame",
              view="seen from above, front at the bottom")
    n = hgt - bt["OSSB"] + bt["BA"] / 2.0                   # bend line (and corner notch) from each edge
    pt.outline = {"pts": [(n, 0), (Wt - n, 0), (Wt - n, n), (Wt, n), (Wt, Dt - n), (Wt - n, Dt - n), (Wt - n, Dt),
                          (n, Dt), (n, Dt - n), (0, Dt - n), (0, n), (n, n)], "bulge": [0.0] * 12}
    for (u0, v0, u1, v1) in ((n, n, Wt - n, n), (n, Dt - n, Wt - n, Dt - n), (n, n, n, Dt - n), (Wt - n, n, Wt - n, Dt - n)):
        pt.bends.append({"u0": u0, "v0": v0, "u1": u1, "v1": v1, "dir": "UP", "R": bt["R"], "ang": 90})
    sh = hgt - bt["BD"]                                     # floor point -> blank: shift by upstand - BD
    inlet = (X0 + 57, D["inlet_y0"], X1 - 57, D["inlet_y1"])
    pt.cuts.append(dict(rrect(inlet[0] - X0 + sh, inlet[1] - Y0 + sh, inlet[2] - X0 + sh, inlet[3] - Y0 + sh, 5.0),
                        use="room-air inlet (riser)"))
    pt.hole(D["drain_x"] - X0 + sh, D["drain_y_out"] - Y0 + sh, 34.0, "25 mm tank bulkhead (drain)")
    pt.notes.append("Corners: fold the four upstands, TIG the corner seams, leak-test with water.")
    parts.append(pt)

    # ---------------------------------------------------------------- castor pads, post caps
    pw, ptk = D["pad_w"], D["pad_t"]
    pt = Part("PD1", "Castor pad (weld pack mark PL1)", "pl8", ptk, 4, pw, pw, "under each frame corner, welded")
    c, hq = pw / 2.0, WM.FAB["castor_pcd"] / 2.0
    for du in (-hq, hq):
        for dv in (-hq, hq):
            pt.hole(c + du, c + dv, SM["tap_m8"], "tap M8 through (castor bolts)")
    parts.append(pt)
    f = D["frame"]
    parts.append(Part("PC1", "Post top cap (weld pack mark %s)" % wm["cap_mark"], "pl3", WM.FAB["cap_t"], 4, f, f,
                      "top of each post, welded"))

    # ---------------------------------------------------------------- 19in rails (folded L, 2 mm)
    t2 = 2.0
    b2 = bend_math(t2)
    Lr = D["rail_z1"] - D["rail_z0"]                       # 16U plus an end margin each end
    fB = D["x_rail_in_l"] - D["x_rail_out_l"]               # hole flange (equipment ears bolt to it)
    fA = D["frame"]                                         # flange against the rail spacer
    rw = fB + fA - b2["BD"]
    pt = Part("RR1", "19in rail, %dU (EIA-310 square holes)" % D["ru_count"], "s20", t2, 4, Lr, rw,
              "on the rail spacers RS1, front and rear, both sides (bend 2 up, 2 down)", view="flat blank")
    pt.min_edge = 2.5                                       # EIA-310 fixes the hole-to-opening web at 2.8 mm
    pt.notes.append("Square holes 2.8 mm from the inner edge: EIA-310 geometry (450 opening, 465.1 centres).")
    blr = fB - b2["OSSB"] + b2["BA"] / 2.0
    pt.bends.append({"u0": 0, "v0": blr, "u1": Lr, "v1": blr, "dir": "UP (2 off) / DOWN (2 off)", "R": b2["R"],
                     "ang": 90})
    hole_col = fB - (D["x_mid"] - 232.55 - D["x_rail_out_l"])  # from the hole flange's free edge
    for u in range(D["ru_count"]):
        for dz in (6.35, 22.225, 38.1):
            pt.squares.append({"u": D["z_rack0"] - D["rail_z0"] + u * D["ru_pitch"] + dz, "v": hole_col,
                               "a": SM["sq_hole"], "use": "cage nut"})
    zr0 = D["rail_z0"]
    up = [m for m in wm["members"] if m["name"] == "Upright front left"][0]
    for i, h in enumerate(up["holes"]):
        if h["use"] == "spacer":
            pt.hole(h["p"][2] - zr0, rw - fA / 2.0, SM["rail_bolt"], "M6 bolt through rail spacer into upright rivnut",
                    ("Upright *", i))
    parts.append(pt)
    return {"P": P, "D": D, "wm": wm, "parts": parts, "frame_holes": fh}


def window_bolts(D):
    gx, gz = (D["win_w"] + 40) / 2.0 - 10.0, (D["win_h"] + 40) / 2.0 - 10.0
    return [(-gx, -gz), (0, -gz), (gx, -gz), (gx, 0), (gx, gz), (0, gz), (-gx, gz), (-gx, 0)]


def tape_hold(P=None, key="ac_split_z", dz=30.0):
    """IDs of the parts whose flat pattern moves when a measured AC dimension changes by +-dz. The default is
    M3, the grille split that sets the mid rail (frame hold point H1): cut these only after the tape check."""
    P = RL.resolve(P)

    def sig(p):
        return (round(p.w, 1), round(p.h, 1),
                sorted((round(h["u"], 1), round(h["v"], 1), h["d"]) for h in p.holes),
                [(round(x, 1), round(y, 1)) for x, y in p.outline["pts"]],
                sorted(sorted((round(x, 1), round(y, 1)) for x, y in c["pts"]) for c in p.cuts),
                sorted((round(q["u"], 1), round(q["v"], 1)) for q in p.squares))
    base = {p.id: sig(p) for p in build(P)["parts"]}
    out = set()
    for s in (-1, 1):
        Q = dict(P)
        Q[key] = P[key] + s * dz
        out |= {p.id for p in build(Q)["parts"] if base.get(p.id) != sig(p)}
    return sorted(out)


# ---------------------------------------------------------------- checks
def check(sm):
    """Problems: blank too big, holes too close to an edge / bend / each other, frame rivnuts not picked up."""
    D = sm["D"]
    L, S = D["sheet_max_l"], D["sheet_max_w"]
    probs = []
    for p in sm["parts"]:
        if not (max(p.w, p.h) <= L + 1e-6 and min(p.w, p.h) <= S + 1e-6):
            probs.append("%s blank %.1f x %.1f exceeds %.0f x %.0f" % (p.id, p.w, p.h, L, S))
        emin = p.min_edge if p.min_edge is not None else max(SM["min_edge"], 1.5 * p.t)
        # features as (u, v, half-size, use, square?); edges and bends are axis-aligned, so a square's
        # clearance is centre distance minus half its side
        feats = [(h["u"], h["v"], h["d"] / 2.0, h["use"], False) for h in p.holes] + \
                [(q["u"], q["v"], q["a"] / 2.0, q["use"], True) for q in p.squares]
        for c in p.cuts:
            us, vs = [x for x, _ in c["pts"]], [y for _, y in c["pts"]]
            feats.append(((min(us) + max(us)) / 2, (min(vs) + max(vs)) / 2, None, c["use"], (min(us), min(vs),
                                                                                           max(us), max(vs))))
        pts = loop_pts(p.outline)
        for u, v, r, use, sq in feats:
            if not point_in_poly(u, v, pts):
                probs.append("%s: %s at (%.1f, %.1f) outside the blank" % (p.id, use, u, v))
                continue
            box_ = sq if isinstance(sq, tuple) else (u - r, v - r, u + r, v + r)
            corners = [(box_[0], box_[1]), (box_[2], box_[1]), (box_[2], box_[3]), (box_[0], box_[3])]
            if r is not None and not sq:                      # round hole
                dmin = min(seg_dist(u, v, pts[i - 1], pts[i]) for i in range(len(pts))) - r
            else:                                             # square hole / cut-out: nearest corner or edge
                dmin = min(min(seg_dist(x, y, pts[i - 1], pts[i]) for i in range(len(pts))) for x, y in corners)
                if not all(point_in_poly(x, y, pts) for x, y in corners):
                    dmin = -1.0
            if dmin < emin - 1e-6:
                probs.append("%s: %s at (%.1f, %.1f) only %.1f from an edge" % (p.id, use, u, v, dmin))
            for b in p.bends:
                bm = bend_math(p.t, b["R"])
                need = bm["BA"] / 2.0 + 1.5 * p.t             # clear of the bend zone by 1.5 t
                if r is not None and not sq:
                    db = seg_dist(u, v, (b["u0"], b["v0"]), (b["u1"], b["v1"])) - r
                else:
                    db = min(seg_dist(x, y, (b["u0"], b["v0"]), (b["u1"], b["v1"])) for x, y in corners)
                if db < need - 1e-6:
                    probs.append("%s: %s at (%.1f, %.1f) %.1f from a bend line (min %.1f)" % (p.id, use, u, v, db, need))
        rnd = [f for f in feats if f[2] is not None]
        for i in range(len(rnd)):
            for j in range(i + 1, len(rnd)):
                a, b = rnd[i], rnd[j]
                if a[4] or b[4]:                              # square involved: axis-aligned box gap
                    gap = max(abs(a[0] - b[0]) - a[2] - b[2], abs(a[1] - b[1]) - a[2] - b[2])
                else:
                    gap = math.dist(a[:2], b[:2]) - a[2] - b[2]
                if gap < p.t:
                    probs.append("%s: holes at (%.1f, %.1f) and (%.1f, %.1f) only %.1f apart" % (
                        p.id, a[0], a[1], b[0], b[1], gap))
    # the touchscreen pod sits clear of the upper door's stiffener frame, handle, hinges and latches
    pd = SM["pod"]
    px0, px1 = pd["xc"] - pd["w"] / 2, pd["xc"] + pd["w"] / 2
    pz0, pz1 = pd["zc"] - pd["h"] / 2, pd["zc"] + pd["h"] / 2
    ds = D["door_stiff"]
    keep_out = [(D["stiff_x0"] - 5, D["stiff_x0"] + ds + 5, -1e9, 1e9, "left door stiffener"),
                (D["stiff_x1"] - ds - 5, D["stiff_x1"] + 5, -1e9, 1e9, "right door stiffener")]
    for zc in D["hinge_z_upper"] + D["latch_z_upper"]:
        keep_out.append((-1e9, 1e9, zc - 60, zc + 60, "hinge/latch at z %.0f" % zc))
    dz0, dz1 = D["door_up_z"]
    if not (dz0 + 40 < pz0 and pz1 < dz1 - 40):
        probs.append("touchscreen pod z %.0f-%.0f not inside the upper door" % (pz0, pz1))
    for x0, x1, z0, z1, what in keep_out:
        if px0 < x1 and x0 < px1 and pz0 < z1 and z0 < pz1:
            probs.append("touchscreen pod overlaps the %s" % what)
    used = set()
    for p in sm["parts"]:
        used.update(h["src"] for h in p.holes if h["src"])
        used.update(p.also)
    rr = [p for p in sm["parts"] if p.id == "RR1"]
    rr_z = sorted(round(h["u"], 1) for h in rr[0].holes) if rr else []
    for m in sm["wm"]["members"]:                      # every upright's spacer rivnuts match the RR1 bolt holes
        if m["kind"] == "upright":
            zs = sorted(round(h["p"][2] - D["rail_z0"], 1) for h in m["holes"] if h["use"] == "spacer")
            if zs != rr_z:
                probs.append("%s spacer rivnuts %s do not match RR1 bolt holes %s" % (m["name"], zs, rr_z))
    for h in sm["frame_holes"]:
        if h["use"] == "spacer":
            continue
        if h["key"] not in used:
            probs.append("frame rivnut %s #%d (%s) not picked up by any sheet part" % (h["key"][0], h["key"][1], h["use"]))
    return probs


def point_in_poly(x, y, pts):
    inside = False
    for i in range(len(pts)):
        (x1, y1), (x2, y2) = pts[i - 1], pts[i]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            inside = not inside
    return inside


def seg_dist(x, y, a, b):
    (x1, y1), (x2, y2) = a, b
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((x - x1) * dx + (y - y1) * dy) / L2))
    return math.hypot(x - (x1 + t * dx), y - (y1 + t * dy))


if __name__ == "__main__":
    sm = build()
    for p in sm["parts"]:
        print("%-4s %-58s %-4s t%.1f x%d  %7.1f x %6.1f  holes %3d  cuts %d  sq %d  bends %d  %.2f kg" % (
            p.id, p.name[:58], p.mat, p.t, p.qty, p.w, p.h, len(p.holes), len(p.cuts), len(p.squares), len(p.bends),
            p.mass()))
    pr = check(sm)
    print("PROBLEMS:" if pr else "check OK", *pr, sep="\n  ")
