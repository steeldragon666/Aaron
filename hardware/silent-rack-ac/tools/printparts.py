#!/usr/bin/env python3
"""
printparts.py - the 3D-printed parts of the SRA-16 rack (CP-SRA16-PRT-001),
sectioned so every piece fits the printer (default: Bambu Lab X1 Carbon).

The parts are built with CadQuery from the same rack_layout.py model, so they
follow every parameter change.  Interfaces are read from the model parts they
replace or touch (hood box, hood gasket, shelf cold opening, AC spigot, duct,
wall spigot and the rear-skin bolt holes), not retyped here.

  P1  Cold-air hood body   PETG  YZ profile run along X, 4 mm walls, split along X
  P2  Hood drop collar     PETG  slides in the hood floor, seals on the AC top by its own weight
  P3  Collar keeper (x2)   PETG  turn buttons that hold the collar up while the AC is rolled
  P4  Exhaust elbow        ASA   socket over the AC spigot, R150 bend, male spigot into the duct
  P5  Exhaust wall spigot  ASA   flange + inner tube (A), outer tube for the flex hose (B)
  G1  Socket gauge         ASA   print first: must slide over the AC spigot
  G2  Spigot gauge         ASA   print first: the 150 duct must slide over it
  P6  Touchscreen pod      PETG  bezel + shell for the 4.3in panel, on the upper door (CP-SRA16-ELC-001)
  P7  Rack node box        PETG  base + lid for the node carrier, on magnets inside the front plenum
  P8  Probe clips          PETG  magnet clips for the temperature probes

Sections are joined by glued half-laps: the inner half of the wall on one
piece runs LAP_L past the cut into a matching rebate in the next piece, so the
outside stays flush and the joint self-aligns.  Every piece is oriented for
printing without supports (thin walls vertical, openings as windows).

Run:  python3 tools/printparts.py [--printer x1c] [key=value ...]
"""
import math
import os
import sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "cad", "fusion", "SilentRackAC"))
sys.path.insert(0, HERE)

import cadquery as cq  # noqa: E402
import rack_layout as RL  # noqa: E402

DOC_NO = "CP-SRA16-PRT-001"
REV = "B"
V = cq.Vector

# Usable volume: bed less a brim margin each side, height less some headroom.  "exclude" is the
# front-left no-print corner that Bambu Studio's X1/P1 profiles mark; footprints must be placeable clear of it.
PRINTERS = OrderedDict([
    ("x1c", {"name": "Bambu Lab X1 Carbon", "bed": (256.0, 256.0), "z": 256.0, "exclude": (18.0, 28.0)}),
    ("p1s", {"name": "Bambu Lab P1S", "bed": (256.0, 256.0), "z": 256.0, "exclude": (18.0, 28.0)}),
    ("a1", {"name": "Bambu Lab A1", "bed": (256.0, 256.0), "z": 256.0, "exclude": (0.0, 0.0)}),
    ("a1mini", {"name": "Bambu Lab A1 mini", "bed": (180.0, 180.0), "z": 180.0, "exclude": (0.0, 0.0)}),
])
FIT = {"margin": 3.0, "z_margin": 6.0}

# rho g/mm3, indicative AUD/kg (Sept 2026), q = average volumetric rate for a rough time estimate (mm3/s)
MATERIALS = OrderedDict([
    ("PETG", {"rho": 1.27e-3, "aud_kg": 32.0, "q": 9.0, "colour": (0.32, 0.55, 0.85),
              "use": "cold side: hood, collar, keepers (water-resistant, tough; carries 12-18 degC air)"}),
    ("ASA", {"rho": 1.07e-3, "aud_kg": 40.0, "q": 9.0, "colour": (0.90, 0.55, 0.20),
             "use": "hot side: exhaust elbow, wall spigot and their gauges (exhaust air up to about 60 degC)"}),
])

PR = {
    "wall": 4.0,          # printed wall: hood, collar, elbow, spigot
    "lap_l": 10.0,        # half-lap length at every section joint
    "lap_cl": 0.2,        # clearance per face in a lap (glued)
    "slide": 2.0,         # collar running clearance per side; a 3 mm foam wiper on the collar takes it up
    "drop": 3.0,          # the collar hangs this far below its working height when the AC is out
    "lift": 15.0,         # raise the collar this much onto the keepers and the AC rolls under it
    "lip": 6.0,           # collar hanging lip (front and sides), rests on the hood floor
    "lip_t": 4.0,
    "foot_t": 3.0,        # collar foot = seat for the 10x10 EPDM gasket (model part "Hood gasket")
    "screw_d": 4.5,       # hood fixing screws (4 mm, into the shelf ply) and M4 keeper pivots
    "driver_d": 10.0,     # hole in the hood floor under a top screw the floor opening does not reach (taped after)
    "keeper_w": 12.0, "keeper_l": 26.0, "keeper_t": 4.0, "keeper_dx": 155.0,
    "fit_socket": 0.5,    # radial clearance, elbow socket over the AC spigot (taped)
    "fit_spigot": 0.5,    # radial clearance, male spigots inside the 150 duct
    "spigot_l": 40.0,     # male spigot length into the duct (elbow outlet, wall-spigot inner tube)
    "lead_in": 1.0,       # 45 deg chamfer on every slip-fit end (lead-in; no elephant's foot on a plate edge)
    "seat": 3.5,          # conical seat inside the elbow socket: the AC spigot stops on it
    "tongue_b": 5.0,      # wall spigot: tongue on the outer tube into the flange groove
    "bead": 1.5,          # retention bead near the end of the outer tube (flex-hose clamp)
}


# ---------------------------------------------------------------- geometry helpers
def box(x0, y0, z0, x1, y1, z1):
    x0, x1 = min(x0, x1), max(x0, x1)
    y0, y1 = min(y0, y1), max(y0, y1)
    z0, z1 = min(z0, z1), max(z0, z1)
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, pnt=V(x0, y0, z0))


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def prism_yz(pts, x0, x1, inset=0.0):
    """Polygon in the YZ plane (y, z), run along +X from x0 to x1; inset > 0 offsets the polygon inwards."""
    wp = cq.Workplane("YZ", origin=(x0, 0, 0)).polyline(pts).close()
    if inset:
        wp = wp.offset2D(-inset, "intersection")
    return wp.extrude(x1 - x0).val()


def prism_xy(pts, z0, z1, inset=0.0):
    wp = cq.Workplane("XY", origin=(0, 0, z0)).polyline(pts).close()
    if inset:
        wp = wp.offset2D(-inset, "intersection")
    return wp.extrude(z1 - z0).val()


def cyl(p0, p1, r):
    p0, p1 = V(*p0), V(*p1)
    d = p1 - p0
    return cq.Solid.makeCylinder(r, d.Length, pnt=p0, dir=d.normalized())


def _rot_to(sh, src, dst):
    """Rotate a shape about the origin so that direction src ends up along dst."""
    a, b = V(*src).normalized(), V(*dst).normalized()
    d = max(-1.0, min(1.0, a.dot(b)))
    if d > 1 - 1e-12:
        return sh
    if d < -1 + 1e-12:
        perp = a.cross(V(1, 0, 0)) if abs(a.x) < 0.9 else a.cross(V(0, 1, 0))
        return sh.rotate(V(0, 0, 0), perp, 180)
    return sh.rotate(V(0, 0, 0), a.cross(b), math.degrees(math.acos(d)))


def _rot_z_to(sh, a):
    """Rotate a shape built about +Z (through the origin) so that +Z points along a."""
    return _rot_to(sh, (0, 0, 1), a)


def rev(profile, origin, axis):
    """Solid of revolution of an (r, h) profile, h measured along `axis` from `origin`."""
    sh = cq.Workplane("XZ").polyline(profile).close().revolve(360, (0, 0, 0), (0, 1, 0)).val()
    return _rot_z_to(sh, axis).translate(V(*origin))


def slab(o, n, a, b, size=4000.0):
    """Region a <= (p - o).n <= b."""
    sh = cq.Solid.makeBox(2 * size, 2 * size, b - a, pnt=V(-size, -size, a))
    return _rot_z_to(sh, n).translate(V(*o))


def fuse(*shapes):
    out = shapes[0]
    for s in shapes[1:]:
        out = out.fuse(s)
    return out.clean()


def one_solid(sh):
    ss = sh.Solids()
    assert len(ss) == 1, "expected one solid, got %d" % len(ss)
    return ss[0]


def arc_tube(c, u, v, R, r_out, r_in, a0, a1):
    """Tube of radius r_out (bore r_in, 0 = solid) on the R arc c + R(u cos t + v sin t), t from a0 to a1 deg."""
    t0 = math.radians(a0)
    s = c + u * (R * math.cos(t0)) + v * (R * math.sin(t0))
    tan = u * (-math.sin(t0)) + v * math.cos(t0)
    ax = u.cross(v)
    inner = [cq.Wire.makeCircle(r_in, s, tan)] if r_in > 0 else []
    return cq.Solid.revolve(cq.Wire.makeCircle(r_out, s, tan), inner, a1 - a0, c, c + ax)


# ---------------------------------------------------------------- model interfaces
def bx(p):
    assert p["kind"] == "box"
    return tuple(p["min"]) + tuple(p["max"])


def interfaces(P=None):
    """Everything the printed parts fit to, read from the model parts."""
    parts, D = RL.build_parts(P)
    M = {p["name"]: p for p in parts}
    P = RL.resolve(P)
    hood = M["Cold air hood"]
    I = {"P": P, "D": D, "M": M}
    I["hood_box"] = bx(hood["add"][1])                    # x0 y0 z0 x1 y1 z1 (box above the collar)
    I["hood_top_open"] = bx(hood["cut"][2])
    I["cold_open"] = bx(M["Divider shelf"]["cut"][0])     # shelf opening the hood feeds
    g = M["Hood gasket"]
    I["gasket"], I["gasket_hole"] = bx(g["add"][0]), bx(g["cut"][0])
    I["ac_top"] = D["z_ac1"]
    I["ac_outlet"] = (D["out_x0"], D["out_y0"], D["out_x1"], D["out_y1"])
    el = M["Exhaust elbow (insulated)"]
    e, sk = el["add"][0], el["add"][1]
    I["elbow"] = {"c": V(*e["c"]), "u": V(*e["u"]), "v": V(*e["v"]), "R": e["R"], "r_env": e["r"],
                  "ri": el["cut"][0]["r"], "sock0": V(*sk["p0"]), "sock1": V(*sk["p1"])}
    sp = M["AC exhaust spigot"]
    I["ac_spigot"] = {"top": V(*sp["add"][0]["p1"]), "r": sp["add"][0]["r"], "bore": sp["cut"][0]["r"]}
    du = M["Exhaust duct (insulated)"]
    I["duct"] = {"p0": V(*du["add"][0]["p0"]), "p1": V(*du["add"][0]["p1"]), "bore": du["cut"][0]["r"],
                 "r_env": du["add"][0]["r"]}
    ws = M["Exhaust wall spigot"]
    I["wall"] = {"p0": V(*ws["add"][0]["p0"]), "p1": V(*ws["add"][0]["p1"]), "r": ws["add"][0]["r"],
                 "f0": V(*ws["add"][1]["p0"]), "f1": V(*ws["add"][1]["p1"]), "rf": ws["add"][1]["r"]}
    return I


def skin_spigot_holes(P=None):
    """World (x, z, d) of the exhaust-spigot bolt holes in the laser-cut rear skin (CP-SRA16-SMP-001)."""
    import sheetmetal as SMP
    sm = SMP.build(P)
    D = sm["D"]
    out = []
    for p in sm["parts"]:
        if not p.place or p.place[0] != "rear":
            continue
        za = p.place[2] + D["z_base0"]
        for h in p.holes:
            if "exhaust spigot flange" in h["use"]:
                out.append((D["ext_w"] - h["u"], h["v"] + za, h["d"]))
    return sorted(out)


# ---------------------------------------------------------------- the parts (installed position)
def collar_dims(I):
    t = PR["wall"]
    g, gh = I["gasket"], I["gasket_hole"]
    C = {"x0": g[0], "y0": g[1], "x1": g[3], "y1": g[4],          # outer = gasket outline
         "ix0": gh[0], "iy0": gh[1], "ix1": gh[3], "iy1": gh[4],  # foot opening = gasket hole
         "z_seat": g[5]}                                          # collar bottom sits on the gasket
    plate_top = I["hood_box"][2] + t
    C["z_top"] = plate_top + PR["drop"] + PR["lip_t"]             # lip rests on the floor when the AC is out
    C["h"] = C["z_top"] - C["z_seat"]
    C["foot_w"] = min(C["ix0"] - C["x0"], C["x1"] - C["ix1"], C["iy0"] - C["y0"], C["y1"] - C["iy1"]) - t
    assert C["foot_w"] > 0.5
    return C


def hood_body(I, C):
    """P1: box between the collar and the shelf.  Profile in YZ (with a rear bump the collar slides up
    into), run along X.  Returns (solid, core(d), info)."""
    t = PR["wall"]
    x0, y0, z0, x1, y1, z1 = I["hood_box"]
    D = I["D"]
    yb = C["y1"] + PR["slide"] + t                               # rear bump outer face
    top_raised = C["z_top"] + PR["lift"]
    zst = top_raised + 4.0 + t                                   # bump roof clears the raised collar by 4
    assert zst <= D["z_shelf_foam0"] - 2.0, "rear bump hits the shelf lining"
    prof = [(y0, z0), (yb, z0), (yb, zst), (y1, zst), (y1, z1), (y0, z1)]
    body = prism_yz(prof, x0, x1).cut(prism_yz(prof, x0 + t, x1 - t, inset=t))
    to = I["hood_top_open"]
    body = body.cut(box(to[0], to[1], z1 - t - 1, to[3], to[4], z1 + 1))
    s = PR["slide"]
    fo = (C["x0"] - s, C["y0"] - s, C["x1"] + s, C["y1"] + s)           # floor opening, the collar slides in it
    body = body.cut(box(fo[0], fo[1], z0 - 1, fo[2], fo[3], z0 + t + 1))
    xm = (x0 + x1) / 2.0
    # screws up into the shelf ply: in the strips either side of the top opening, at x where a driver
    # coming up through the floor opening lines up; any screw outside it gets a driver hole in the floor
    holes_top = [(x, y) for x in (fo[0] + 8.0, xm, fo[2] - 8.0)
                 for y in ((y0 + t + to[1]) / 2.0, (to[4] + y1 - t) / 2.0)]
    for x, y in holes_top:
        body = body.cut(cyl((x, y, z1 - t - 1), (x, y, z1 + 1), PR["screw_d"] / 2))
    r_drv = PR["driver_d"] / 2.0
    drivers = [(x, y) for x, y in holes_top
               if not (fo[0] + r_drv <= x <= fo[2] - r_drv and fo[1] + r_drv <= y <= fo[3] - r_drv)]
    for x, y in drivers:
        body = body.cut(cyl((x, y, z0 - 1), (x, y, z0 + t + 1), r_drv))
    yk = C["y0"] - PR["keeper_l"] + 2.0
    keepers = [(xm - PR["keeper_dx"], yk), (xm + PR["keeper_dx"], yk)]
    for x, y in keepers:
        body = body.cut(cyl((x, y, z0 - 1), (x, y, z0 + t + 1), PR["screw_d"] / 2))
    # cable port for the electronics harness (CP-SRA16-ELC-001): through the left end wall into the bay,
    # the wall thinned from inside round it so a standard membrane grommet grips
    py, pz, pd, pcb, pwt = EL["hood_port"]
    port = (x0, y0 + py, z1 - pz)
    body = body.cut(cyl((x0 - 1, port[1], port[2]), (x0 + t + 1, port[1], port[2]), pd / 2.0))
    body = body.cut(cyl((x0 + pwt, port[1], port[2]), (x0 + t + 1, port[1], port[2]), pcb / 2.0))
    body = one_solid(body.clean())

    def core(d):
        return body.intersect(prism_yz(prof, x0 + d, x1 - d, inset=d))
    info = {"profile": prof, "x": (x0, x1), "holes_top": holes_top, "drivers": drivers, "keepers": keepers,
            "z_step": zst, "bump_y": yb, "z0": z0, "z1": z1, "floor_open": fo, "port": port}
    return body, core, info


def collar(C, dz=0.0):
    """P2 at working height + dz (dz = -drop: hanging, AC out; +lift: on the keepers)."""
    t = PR["wall"]
    zb, zt = C["z_seat"] + dz, C["z_top"] + dz
    outer = rect(C["x0"], C["y0"], C["x1"], C["y1"])
    wall = prism_xy(outer, zb, zt).cut(prism_xy(outer, zb - 1, zt + 1, inset=t))
    wi = (C["x0"] + t, C["y0"] + t, C["x1"] - t, C["y1"] - t)
    foot = prism_xy(rect(*wi), zb, zb + PR["foot_t"]).cut(
        box(C["ix0"], C["iy0"], zb - 1, C["ix1"], C["iy1"], zb + PR["foot_t"] + 1))
    zf, w = zb + PR["foot_t"], C["foot_w"]
    lo = cq.Wire.makePolygon([V(x, y, zf) for x, y in rect(C["ix0"], C["iy0"], C["ix1"], C["iy1"])], close=True)
    hi = cq.Wire.makePolygon([V(x, y, zf + w) for x, y in rect(*wi)], close=True)
    chamfer = prism_xy(rect(*wi), zf, zf + w).cut(cq.Solid.makeLoft([lo, hi], True))   # 45 deg, prints clean
    L = PR["lip"]
    lip = prism_xy(rect(C["x0"] - L, C["y0"] - L, C["x1"] + L, C["y1"]), zt - PR["lip_t"], zt).cut(
        prism_xy(outer, zt - PR["lip_t"] - 1, zt + 1))
    sol = one_solid(fuse(wall, foot, chamfer, lip))

    def core(d):
        return sol.intersect(prism_xy(outer, zb - 1, zt + 1, inset=d))
    return sol, core


def keeper(x, y, z_plate, z_arm_top, angle=0.0):
    """P3: turn button under the hood floor; angle 0 = arm along +Y (holding the collar)."""
    w, L, t = PR["keeper_w"], PR["keeper_l"], PR["keeper_t"]
    arm = cq.Workplane("XY", origin=(0, 0, z_arm_top - t)).slot2D(L + w, w, angle=90).extrude(t).val()
    arm = arm.translate(V(0, L / 2.0, 0))
    boss = cyl((0, 0, z_arm_top - 0.01), (0, 0, z_plate), w / 2.0)
    sol = fuse(arm, boss).cut(cyl((0, 0, z_arm_top - t - 1), (0, 0, z_plate + 1), PR["screw_d"] / 2))
    sol = one_solid(sol)
    if angle:
        sol = sol.rotate(V(0, 0, 0), V(0, 0, 1), angle)
    return sol.translate(V(x, y, 0))


def elbow(I):
    """P4: socket over the AC spigot + conical seat, R bend, 45 deg cone to a male spigot into the duct."""
    E, t = I["elbow"], PR["wall"]
    c, u, v, R, ri = E["c"], E["u"], E["v"], E["R"], E["ri"]
    ro = ri + t
    rs = I["ac_spigot"]["r"] + PR["fit_socket"]                 # socket bore
    s0 = c + u * R                                               # arc start (top of the socket)
    sock_l = (E["sock1"] - E["sock0"]).Length
    arc = arc_tube(c, u, v, R, ro, ri, 0.0, 90.0)
    c_ = PR["lead_in"]
    sock = rev([(rs + c_, -sock_l), (rs + t, -sock_l), (rs + t, 0.0), (rs, 0.0), (rs, -sock_l + c_)], s0, v)
    a = PR["seat"]
    seat = rev([(rs, 0.0), (ri + 1.0, 0.0), (ri + 1.0, a + 1.5), (rs - a, a + 1.5), (rs - a, a)], s0, v)
    e1 = c + v * R                                               # arc end, axis -u
    ro2 = I["duct"]["bore"] - PR["fit_spigot"]
    k = ro - ro2                                                 # 45 deg transition length
    L_ = k + PR["spigot_l"]
    out = rev([(ri, 0.0), (ro, 0.0), (ro2, k), (ro2, L_ - c_), (ro2 - c_, L_), (ro2 - t, L_), (ro2 - t, k)], e1, -u)
    sol = one_solid(fuse(arc, sock, seat, out))

    def core(d):                                                 # inner part of the wall around the 45 deg joint
        return sol.intersect(arc_tube(c, u, v, R, ro - d, 0.0, 25.0, 65.0))
    info = {"ro": ro, "rs": rs, "ro2": ro2, "bore2": ro2 - t, "sock_l": sock_l, "seat_min": rs - a,
            "outlet_end": e1 + (-u) * (k + PR["spigot_l"]), "cut_o": c,
            "cut_n": (u * (-math.sin(math.pi / 4)) + v * math.cos(math.pi / 4)).normalized()}
    return sol, core, info


def wall_spigot(I, holes):
    """P5: A = flange + inner tube (through the skin, into the duct), B = outer tube for the flex hose."""
    W, t = I["wall"], PR["wall"]
    ax = (W["p1"] - W["p0"]).normalized()                       # +Y, out of the cabinet
    yf0, yf1 = W["f0"].y, W["f1"].y                              # flange faces: skin side, outside
    x, z = W["p0"].x, W["p0"].z
    ro_in = I["duct"]["bore"] - PR["fit_spigot"]                 # inner tube slides into the duct
    y_in0 = W["p0"].y - PR["spigot_l"]
    tg, cl = PR["tongue_b"], PR["lap_cl"]
    r_out = W["r"]                                               # outer tube OD = model spigot (flex hose)
    rb = r_out - t                                               # outer tube bore
    rt0 = (rb + r_out) / 2.0                                     # tongue = outer half of the outer tube
    a = cyl((x, y_in0, z), (x, yf0, z), ro_in).fuse(cyl((x, yf0, z), (x, yf1, z), W["rf"]))
    a = a.cut(cyl((x, y_in0 - 1, z), (x, yf1 + 1, z), ro_in - t))
    c_ = PR["lead_in"]                                           # lead-in on the end that goes into the duct
    a = a.cut(rev([(ro_in - c_ - 1.0, -1.0), (ro_in + 1.0, -1.0), (ro_in + 1.0, c_ + 1.0)], (x, y_in0, z), ax))
    groove = cyl((x, yf1 - tg - cl, z), (x, yf1 + 1, z), r_out + cl).cut(
        cyl((x, yf1 - tg - cl - 1, z), (x, yf1 + 2, z), rt0 - cl))
    a = a.cut(groove)
    for hx, hz, d in holes:
        a = a.cut(cyl((hx, yf0 - 1, hz), (hx, yf1 + 1, hz), d / 2.0))
    A = one_solid(a.clean())
    y_end = W["p1"].y
    bead = PR["bead"]
    prof = [(rb, 0.0), (r_out, 0.0), (r_out, y_end - yf1 - 9.5), (r_out + bead, y_end - yf1 - 8.0),
            (r_out + bead, y_end - yf1 - 5.5), (r_out, y_end - yf1 - 4.0), (r_out, y_end - yf1), (rb, y_end - yf1)]
    b = rev(prof, (x, yf1, z), ax)
    b = b.fuse(rev([(rt0, -tg), (r_out, -tg), (r_out, 0.5), (rt0, 0.5)], (x, yf1, z), ax))
    B = one_solid(b.clean())
    info = {"ro_in": ro_in, "bore_in": ro_in - t, "r_out": r_out, "rb": rb, "y_in0": y_in0, "holes": holes,
            "groove": (rt0 - cl, r_out + cl, tg + cl)}
    return A, B, info


def gauges(I):
    t = PR["wall"]
    rs = I["ac_spigot"]["r"] + PR["fit_socket"]
    ro2 = I["duct"]["bore"] - PR["fit_spigot"]
    c_ = PR["lead_in"]                                           # same lead-in as the real ends
    g1 = rev([(rs + c_, 0.0), (rs + t, 0.0), (rs + t, 12.0), (rs, 12.0), (rs, c_)], (0, 0, 0), (0, 0, 1))
    g2 = rev([(ro2 - t, 0.0), (ro2 - c_, 0.0), (ro2, c_), (ro2, 15.0), (ro2 - t, 15.0)], (0, 0, 0), (0, 0, 1))
    return g1, g2


# ---------------------------------------------------------------- electronics mounts (CP-SRA16-ELC-001)
EL = {
    # Waveshare ESP32-S3-Touch-LCD-4.3B: PCB 112.4 x 75.1 with the cover glass over all of it; the
    # board's depth is not published, so the pod clamps it on 2 mm foam pads (+-1.5 mm)
    "board": (112.4, 75.1), "board_t": 8.0, "window": (106.0, 69.0), "pod_wall": 2.4, "pod_back": 3.0,
    "pod_shell": 26.0, "pod_bezel": 10.0, "pod_r": 8.0, "lip": 2.0,
    # node carrier: 70 x 90 mm prototype board on M2.5 standoffs (holes 2 mm in from the corners)
    "pcb": (70.0, 90.0), "pcb_holes": (66.0, 86.0), "box_wall": 2.0, "box_base": 2.5, "box_in_h": 24.0,
    "box_lid": 2.0, "magnet": (20.4, 5.2), "box_at": (36.5, 125.0, 1215.0),
    "clip_magnet": (10.3, 3.2), "probe_d": 6.3,
    # hood cable port: centre 31 mm behind the hood's front face and 42 mm below its top, D25 for a
    # 25 mm membrane grommet, wall thinned to 2 mm over D35 round it
    "hood_port": (31.0, 42.0, 25.0, 35.0, 2.0),
}


def rrect(w, h, z0, z1, r):
    """Rounded rectangle in local XY, centred, from z0 to z1."""
    sh = cq.Workplane("XY", origin=(0, 0, z0)).rect(w, h).extrude(z1 - z0)
    return (sh.edges("|Z").fillet(r) if r > 0 else sh).val()


def pod_frame():
    """Pod placement: local XY is the door face (x right, y up), local z points out of the door, so
    (x, y, z) -> (xc + x, -z, zc + y).  At the door holes of CP-SRA16-SMP-001 (sheetmetal.SM["pod"])."""
    import sheetmetal as SMP
    pd = SMP.SM["pod"]
    return pd, lambda sh: sh.rotate(V(0, 0, 0), V(1, 0, 0), 90).translate(V(pd["xc"], 0, pd["zc"]))


def touch_pod():
    """P6: shell (on the door) and bezel (holds the panel against its lip).  Local frame, z out of the door."""
    pd, M = pod_frame()
    e = EL
    W, H, R = pd["w"], pd["h"], e["pod_r"]
    t, tb, zs = e["pod_wall"], e["pod_back"], e["pod_shell"]
    zb = zs + e["pod_bezel"]
    shell = rrect(W, H, 0, zs, R).cut(rrect(W - 2 * t, H - 2 * t, tb, zs + 1, R - t))
    corners = [(sx * 59.5, sy * 41.0) for sx in (-1, 1) for sy in (-1, 1)]
    for x, y in corners:                                   # bezel screw bosses, M3 self-tapping
        shell = shell.fuse(cyl((x, y, tb - 0.1), (x, y, zs), 3.5))
    posts = [(sx * 50.0, sy * 32.0) for sx in (-1, 1) for sy in (-1, 1)]
    for x, y in posts:                                     # press the PCB through 2 mm foam pads
        shell = shell.fuse(cyl((x, y, tb - 0.1), (x, y, zs - 2.0), 3.0))
    # room sensor compartment, bottom right, vented through the bottom wall
    cx0, cy1 = 24.0, -H / 2 + t + 14.0
    shell = shell.fuse(box(cx0, -H / 2 + t - 0.1, tb - 0.1, cx0 + 1.6, cy1 + 1.6, zs - 2.0))
    shell = shell.fuse(box(cx0, cy1, tb - 0.1, W / 2 - t + 0.1, cy1 + 1.6, zs - 2.0))
    for x, y in corners:
        shell = shell.cut(cyl((x, y, tb + 2.0), (x, y, zs + 1), 1.25))
    for k in range(4):
        x = cx0 + 6.0 + 6.0 * k
        shell = shell.cut(box(x, -H / 2 - 1, tb + 4.0, x + 1.8, -H / 2 + t + 1, tb + 16.0))
    for du, dv in pd["bolts"]:                             # M4 into the door rivnuts, heads inside
        shell = shell.cut(cyl((du, dv, -1), (du, dv, tb + 1), 2.25))
        shell = shell.cut(cyl((du, dv, tb - 1.5), (du, dv, tb + 1), 4.6))
    cu, cv = pd["cable"]
    shell = shell.cut(cyl((cu, cv, -1), (cu, cv, tb + 1), 8.0))   # over the door's 20 mm grommet
    shell = one_solid(shell.clean())
    # bezel
    bw, bh = e["board"]
    bezel = rrect(W, H, zs, zb, R)
    bezel = bezel.cut(rrect(bw + 1.0, bh + 1.0, zs - 1, zb - e["lip"], 1.0))
    ww, wh = e["window"]
    bezel = bezel.cut(rrect(ww, wh, zb - e["lip"] - 1, zb + 1, 3.0))
    for x, y in corners:
        bezel = bezel.cut(cyl((x, y, zs - 1), (x, y, zb + 1), 1.7))
        bezel = bezel.cut(cq.Solid.makeCone(1.7, 3.4, 1.71, pnt=V(x, y, zb - 1.7), dir=V(0, 0, 1)))
    bezel = one_solid(bezel.clean())
    info = {"frame": M, "corners": corners, "bolts": pd["bolts"], "cable": pd["cable"], "depth": zb,
            "pocket": (bw + 1.0, bh + 1.0, zb - e["lip"] - zs), "window": e["window"]}
    return shell, bezel, info


def node_box():
    """P7: base and lid for the node carrier.  Local frame: board in XY, base plate at z = 0, magnets in
    the +x end wall.  Installed at the left of the front plenum on the front-left rail spacer."""
    e = EL
    pw, ph = e["pcb"]
    t, tb, hin = e["box_wall"], e["box_base"], e["box_in_h"]
    iw, ih = pw + 4.0, ph + 4.0
    W, H, Z = iw + 2 * t, ih + 2 * t, tb + hin
    base = rrect(W, H, 0, Z, 3.0).cut(rrect(iw, ih, tb, Z + 1, 1.0))
    mt = e["magnet"][1] + 1.8                              # thickened end wall for the magnets
    base = base.fuse(box(W / 2 - t - mt, -ih / 2, tb - 0.1, W / 2 - t + 0.1, ih / 2, Z))
    for sy in (-1, 1):
        base = base.cut(cyl((W / 2 + 1, sy * 25.0, Z / 2 + 1.0), (W / 2 - e["magnet"][1], sy * 25.0, Z / 2 + 1.0),
                            e["magnet"][0] / 2))
    hx, hy = e["pcb_holes"]
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * hx / 2, sy * hy / 2
            base = base.fuse(cyl((x, y, tb - 0.1), (x, y, tb + 5.0), 3.0)).cut(cyl((x, y, tb + 1.0), (x, y, tb + 5.1), 1.1))
    lid_pts = [(sx * (iw / 2 - 4.0), sy * (ih / 2 - 4.0)) for sx in (-1, 1) for sy in (-1, 1)]
    for x, y in lid_pts:                                   # lid screws, M3 self-tapping
        base = base.fuse(cyl((x, y, tb - 0.1), (x, y, Z), 3.5)).cut(cyl((x, y, tb + 2.0), (x, y, Z + 1), 1.25))
    for x in (-22.0, 0.0, 22.0):                           # cable slots in the bottom wall, open at the top
        base = base.cut(box(x - 3.5, -H / 2 - 1, Z - 9.0, x + 3.5, -H / 2 + t + 1, Z + 1))
    base = base.cut(box(-W / 2 - 1, ih / 2 - 26.0, Z - 9.0, -W / 2 + t + 1, ih / 2 - 14.0, Z + 1))  # bus cable
    base = one_solid(base.clean())
    lid = rrect(W, H, Z, Z + e["box_lid"], 3.0)
    lid = lid.fuse(rrect(iw - 0.6, ih - 0.6, Z - 3.0, Z + 0.1, 1.0).cut(rrect(iw - 3.0, ih - 3.0, Z - 4.0, Z + 1, 1.0)))
    for x, y in lid_pts:
        lid = lid.cut(box(x - 5.0, y - 5.0, Z - 3.1, x + 5.0, y + 5.0, Z)).cut(cyl((x, y, Z - 1), (x, y, Z + 3), 1.7))
    lid = lid.cut(box(iw / 2 - mt - 0.5, -H / 2, Z - 3.1, W / 2 + 1, H / 2, Z))   # no rim along the magnet wall
    lid = lid.cut(cyl((0.0, -30.0, Z - 4), (0.0, -30.0, Z + 3), 3.5))   # window for the IR receiver (learning)
    lid = one_solid(lid.clean())
    ax, ay, az = e["box_at"]

    def place(sh):                                         # (x, y, z) -> (ax + z, ay + x, az + y)
        return sh.rotate(V(0, 0, 0), V(1, 0, 0), 90).rotate(V(0, 0, 0), V(0, 0, 1), 90).translate(V(ax, ay, az))
    return base, lid, {"frame": place, "outer": (W, H, Z + e["box_lid"]), "magnet_wall": W / 2}


def clip(hole_d, n_holes=1):
    """P8: magnet clip holding a probe (or several side by side) 16 mm off a steel face; back face at z = 0."""
    e = EL
    w = 14.0 + 10.0 * n_holes
    blk = box(-w / 2, -7.0, 0, w / 2, 7.0, 22.0)
    md, mh = e["clip_magnet"]
    blk = blk.cut(cyl((0, 0, -1), (0, 0, mh), md / 2))
    xs = [(-5.0 * (n_holes - 1)) + 10.0 * i for i in range(n_holes)]
    for x in xs:
        blk = blk.cut(cyl((x, -8, 16.0), (x, 8, 16.0), hole_d / 2))
        blk = blk.cut(box(x - hole_d * 0.36, -8, 16.0, x + hole_d * 0.36, 8, 23.0))   # snap-in throat
    return one_solid(blk.clean())


# ---------------------------------------------------------------- sectioning
def lap_split(solid, core, o, n, L=None, cl=None):
    """Cut `solid` by the plane (o, n).  The low side keeps a tongue (inner half of the wall, core(t/2))
    running L past the cut; the high side gets the matching rebate with `cl` clearance."""
    L = PR["lap_l"] if L is None else L
    cl = PR["lap_cl"] if cl is None else cl
    t = PR["wall"]
    lo = solid.intersect(slab(o, n, -4000.0, 0.0))
    hi = solid.intersect(slab(o, n, 0.0, 4000.0))
    tongue = core(t / 2.0).intersect(slab(o, n, 0.0, L))
    rebate = core(t / 2.0 - cl).intersect(slab(o, n, -0.01, L + cl))
    lo = lo.fuse(tongue).clean()
    hi = hi.cut(rebate).clean()
    return lo, hi, solid.Volume() - lo.Volume() - hi.Volume()     # glue clearance left in the lap


def usable(printer):
    pr = PRINTERS[printer]
    m = FIT["margin"]
    return pr["bed"][0] - 2 * m, pr["bed"][1] - 2 * m, pr["z"] - FIT["z_margin"]


def hull2d(shape, tol=0.5):
    """Convex hull (x, y) of a shape's footprint, counter-clockwise (monotone chain)."""
    vs, _ = shape.tessellate(tol)
    pts = sorted({(round(v.x, 3), round(v.y, 3)) for v in vs})

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for q in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], q) <= 0:
            lo.pop()
        lo.append(q)
    for q in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], q) <= 0:
            up.pop()
        up.append(q)
    return lo[:-1] + up[:-1]


def hits_rect(poly, x0, y0, x1, y1):
    """True if the convex polygon overlaps the rectangle (separating-axis test)."""
    rc = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    axes = [(1.0, 0.0), (0.0, 1.0)] + [(b[1] - a[1], a[0] - b[0]) for a, b in zip(poly, poly[1:] + poly[:1])]
    for nx, ny in axes:
        pp = [nx * x + ny * y for x, y in poly]
        pr = [nx * x + ny * y for x, y in rc]
        if max(pp) <= min(pr) + 1e-9 or max(pr) <= min(pp) + 1e-9:
            return False
    return True


def corner_place(printer, dims, hull, rot):
    """Bed position (x, y) of the footprint's lower-left corner with the piece pushed into the back-right
    corner, and whether its real outline (not its bounding box) then clears the no-print corner + margin."""
    pr, m = PRINTERS[printer], FIT["margin"]
    a, b = (dims[0], dims[1]) if not rot else (dims[1], dims[0])
    x, y = pr["bed"][0] - m - a, pr["bed"][1] - m - b
    pts = [(-q[1], q[0]) if rot else q for q in hull]
    mx, my = min(q[0] for q in pts), min(q[1] for q in pts)
    pts = [(q[0] - mx + x, q[1] - my + y) for q in pts]
    ex, ey = pr["exclude"]
    return x, y, not hits_rect(pts, 0.0, 0.0, ex + m, ey + m)


def fits(printer, dims, hull=None):
    """dims = (dx, dy, dz) of a piece in print orientation -> (ok, why).  90 deg spins allowed.  The
    footprint must clear the no-print corner: by its bounding box, or by its real outline (hull) when the
    piece sits in the back-right corner (a disc that fills the bed still clears it)."""
    W, Dp, H = usable(printer)
    ex, ey = PRINTERS[printer]["exclude"]
    dx, dy, dz = dims
    if dz > H + 1e-6:
        return False, "height %.1f > %.0f" % (dz, H)
    inside = False
    for rot, (a, b) in enumerate(((dx, dy), (dy, dx))):
        if a > W + 1e-6 or b > Dp + 1e-6:
            continue
        inside = True
        if not ex or a <= W - ex + 1e-6 or b <= Dp - ey + 1e-6:
            return True, ""
        if hull and corner_place(printer, dims, hull, rot)[2]:
            return True, ""
    if inside:
        return False, "footprint %.1f x %.1f runs into the %gx%g no-print corner" % (dx, dy, ex, ey)
    return False, "footprint %.1f x %.1f > %.0f x %.0f" % (dx, dy, W, Dp)


def best_spin(printer, dz, hull):
    """Whole-degree turn about Z (1..89) that lets a footprint too big square-on fit the bed (the diagonal is
    longer), choosing the most compact; 0 if none does."""
    best = (None, 0)
    for a in range(1, 90):
        c, s_ = math.cos(math.radians(a)), math.sin(math.radians(a))
        h = [(x * c - y * s_, x * s_ + y * c) for x, y in hull]
        xs, ys = [q[0] for q in h], [q[1] for q in h]
        dims = (max(xs) - min(xs), max(ys) - min(ys), dz)
        if fits(printer, dims, h)[0] and (best[0] is None or max(dims[:2]) < best[0] - 1e-9):
            best = (max(dims[:2]), a)
    return best[1]


def sections_along(x0, x1, extra, limit):
    """Fewest equal sections of [x0, x1] whose length + extra (lap) stays within limit."""
    n = 1
    while (x1 - x0) / n + extra > limit + 1e-6:
        n += 1
    return [x0 + (x1 - x0) * i / n for i in range(1, n)]


def orient(sh, down):
    """Rotate so world direction `down` points to -Z, then sit the piece on z = 0, centred on x = y = 0."""
    s = _rot_to(sh, down, (0, 0, -1))
    bb = s.BoundingBox()
    return s.translate(V(-(bb.xmin + bb.xmax) / 2.0, -(bb.ymin + bb.ymax) / 2.0, -bb.zmin))


# ---------------------------------------------------------------- the pack
PART_INFO = OrderedDict([
    ("P1", {"file": "hood", "name": "Cold-air hood body", "mat": "PETG", "replaces": ["Cold air hood"],
            "hardware": ["6 x 4 mm x 20 pan-head wood screws into the shelf ply",
                         "aluminium foil tape over the driver holes in the floor once the screws are in",
                         "3 x 10 mm closed-cell foam tape on the top face (seal to the shelf)",
                         "25 mm membrane grommet in the cable port (left end, CP-SRA16-ELC-001)",
                         "epoxy or PETG-rated CA glue for the laps"]}),
    ("P2", {"file": "collar", "name": "Hood drop collar", "mat": "PETG", "replaces": ["Cold air hood"],
            "hardware": ["10 x 10 EPDM closed-cell strip under the foot (model part 'Hood gasket')",
                         "3 x 10 mm closed-cell foam tape round the outside (wiper seal)",
                         "epoxy or PETG-rated CA glue for the laps"]}),
    ("P3", {"file": "keeper", "name": "Collar keeper", "mat": "PETG", "replaces": [],
            "hardware": ["2 x M4 x 25 button head + 2 x M4 nyloc + 4 washers"]}),
    ("P4", {"file": "elbow", "name": "Exhaust elbow", "mat": "ASA", "replaces": ["Exhaust elbow (insulated)"],
            "hardware": ["acetone (solvent-weld the lap) or ABS/ASA cement", "aluminium foil tape",
                         "6 mm self-adhesive closed-cell insulation, about 0.25 m2",
                         "3 mm closed-cell foam ring on the shoulder (seals on the duct end)",
                         "perforated hanger strap, about 0.4 m, + 2 screws into the shelf ply (holds the duct in line)"]}),
    ("P5", {"file": "wall_spigot", "name": "Exhaust wall spigot", "mat": "ASA", "replaces": ["Exhaust wall spigot"],
            "hardware": ["4 x M5 x 25 button head + 4 x M5 nyloc + 8 washers",
                         "3 mm closed-cell foam ring or silicone under the flange", "acetone or ABS/ASA cement"]}),
    ("G", {"file": "gauge", "name": "Fit gauges", "mat": "ASA", "replaces": [], "hardware": []}),
    ("P6", {"file": "pod", "name": "Touchscreen pod", "mat": "PETG", "replaces": [],
            "hardware": ["2 x M4 rivnut (1.2 mm skin) in the upper door + 2 x M4 x 8 button head",
                         "4 x M3 x 12 self-tapping pan head (bezel)", "20 mm rubber grommet for the cable",
                         "4 x 10 x 10 x 2 mm foam pads (behind the panel)"]}),
    ("P7", {"file": "node_box", "name": "Rack node box", "mat": "PETG", "replaces": [],
            "hardware": ["2 x 20 x 5 mm neodymium disc magnets (glued)", "4 x M2.5 x 6 self-tapping (carrier board)",
                         "4 x M3 x 8 self-tapping (lid)"]}),
    ("P8", {"file": "clip", "name": "Probe clips", "mat": "PETG", "replaces": [],
            "hardware": ["6 x 10 x 3 mm neodymium disc magnets (glued)"]}),
])


def build(P=None, printer="x1c"):
    """All printed pieces, in installed position and print orientation, plus the checks."""
    I = interfaces(P)
    C = collar_dims(I)
    W_, D_, H_ = usable(printer)
    pieces, parts, checks = [], OrderedDict(), []

    def add_piece(pid, part, name, sol, down, qty=1, note=""):
        pieces.append({"id": pid, "part": part, "name": name, "solid": sol, "down": tuple(down), "qty": qty,
                       "mat": PART_INFO[part]["mat"], "note": note})

    # P1 hood body: fewest sections along X so each (with its lap) is no taller than the printer
    body, core, hinfo = hood_body(I, C)
    x0, x1 = hinfo["x"]
    cuts = sections_along(x0, x1, PR["lap_l"], H_)
    parts["P1"] = {"solid": body, "info": hinfo, "cuts": cuts}
    rest, laps = body, []
    secs = []
    for xc in cuts:
        lo, rest, gap = lap_split(rest, core, (xc, 0, 0), (1, 0, 0))
        secs.append(lo)
        laps.append(gap)
    secs.append(rest)
    n = len(secs)
    names = {0: "left end", n - 1: "right end"}
    for i, s in enumerate(secs):
        tag = names.get(i, "middle %d" % i if n > 3 else "middle")
        down = (1, 0, 0) if (i == n - 1 and n > 1) else (-1, 0, 0)
        note = ("end wall on the plate" if (i == 0 or i == n - 1) else "rebate end on the plate") + \
            (", tongue up" if i < n - 1 and down[0] < 0 else "")
        # between the end walls the top and floor openings leave two separate channels (front, rear)
        sol = sorted(s.Solids(), key=lambda q: q.Center().y)
        for j, q in enumerate(sol):
            sub = "" if len(sol) == 1 else ("a", "b", "c", "d")[j]
            ch = "" if len(sol) == 1 else (", front channel" if j == 0 else ", rear channel")
            add_piece("P1-%d%s" % (i + 1, sub), "P1", "Hood body - %s%s" % (tag, ch), q, down, note=note)
    parts["P1"]["gap"] = sum(laps)

    # P2 drop collar: split along X only if it does not fit the plate whole (lip down)
    col, ccore = collar(C)
    parts["P2"] = {"solid": col, "C": C}
    bb = col.BoundingBox()
    whole = fits(printer, (bb.xlen, bb.ylen, bb.zlen))[0]
    ccuts = [] if whole else sections_along(bb.xmin, bb.xmax, PR["lap_l"], max(W_, D_))
    rest, laps, secs = col, [], []
    for xc in ccuts:
        lo, rest, gap = lap_split(rest, ccore, (xc, 0, 0), (1, 0, 0))
        secs.append(lo)
        laps.append(gap)
    secs.append(rest)
    parts["P2"]["cuts"], parts["P2"]["gap"] = ccuts, sum(laps)
    for i, s in enumerate(secs):
        tag = "whole" if len(secs) == 1 else ("left half", "right half")[i] if len(secs) == 2 else "section %d" % (i + 1)
        sol = sorted(s.Solids(), key=lambda q: q.Center().y)      # a middle section is a front and a rear wall
        for j, q in enumerate(sol):
            sub = "" if len(sol) == 1 else ("a", "b")[j]
            ch = "" if len(sol) == 1 else (", front" if j == 0 else ", rear")
            add_piece("P2-%d%s" % (i + 1, sub), "P2", "Drop collar - %s%s" % (tag, ch), q, (0, 0, 1),
                      note="lip on the plate")

    # P3 keepers (installed stowed: arm turned outwards along X)
    zp = I["hood_box"][2]
    z_arm = C["z_seat"] + PR["lift"] - 1.0
    ks = []
    for j, (kx, ky) in enumerate(hinfo["keepers"]):
        ks.append(keeper(kx, ky, zp, z_arm, angle=90.0 if j == 0 else -90.0))
    parts["P3"] = {"solids": ks, "z_arm": z_arm}
    add_piece("P3-1", "P3", "Collar keeper", ks[0], (0, 0, -1), qty=2, note="arm on the plate, print 2")

    # P4 elbow: two 45 deg sections, each printed standing on its straight end
    el, ecore, einfo = elbow(I)
    parts["P4"] = {"solid": el, "info": einfo}
    a_, b_, gap = lap_split(el, ecore, einfo["cut_o"], einfo["cut_n"])
    a_, b_ = one_solid(a_), one_solid(b_)
    parts["P4"]["gap"] = gap
    add_piece("P4-1", "P4", "Exhaust elbow - inlet half (socket)", a_, (0, 0, -1), note="socket on the plate, tongue up")
    add_piece("P4-2", "P4", "Exhaust elbow - outlet half (spigot)", b_, tuple(-I["elbow"]["u"]),
              note="male spigot on the plate, rebate up")

    # P5 wall spigot
    holes = skin_spigot_holes(P)
    A, B, winfo = wall_spigot(I, [(hx, hz, d) for hx, hz, d in holes])
    parts["P5"] = {"solids": (A, B), "info": winfo}
    ax = (I["wall"]["p1"] - I["wall"]["p0"]).normalized()
    add_piece("P5-1", "P5", "Wall spigot - flange + inner tube", A, tuple(ax), note="flange face (outside) on the plate")
    add_piece("P5-2", "P5", "Wall spigot - outer tube", B, tuple(ax), note="hose end on the plate, tongue up")

    # electronics mounts
    shell, bezel, pinfo = touch_pod()
    M = pinfo["frame"]
    parts["P6"] = {"solids": (M(shell), M(bezel)), "info": pinfo,
                   "local": (shell, bezel)}
    add_piece("P6-1", "P6", "Touchscreen pod - shell", parts["P6"]["solids"][0], (0, 1, 0),
              note="door side on the plate")
    add_piece("P6-2", "P6", "Touchscreen pod - bezel", parts["P6"]["solids"][1], (0, -1, 0),
              note="front face on the plate")
    nb, lid, ninfo = node_box()
    M = ninfo["frame"]
    parts["P7"] = {"solids": (M(nb), M(lid)), "info": ninfo}
    add_piece("P7-1", "P7", "Rack node box - base", parts["P7"]["solids"][0], (-1, 0, 0), note="base on the plate")
    add_piece("P7-2", "P7", "Rack node box - lid", parts["P7"]["solids"][1], (1, 0, 0), note="outer face on the plate")
    add_piece("P8-1", "P8", "Clip - temperature probe", clip(EL["probe_d"]), (0, 0, -1), qty=6,
              note="magnet face on the plate, print 6")

    # gauges
    g1, g2 = gauges(I)
    add_piece("G1", "G", "Gauge - elbow socket over the AC spigot", g1, (0, 0, -1), note="print first")
    add_piece("G2", "G", "Gauge - male spigot into the 150 duct", g2, (0, 0, -1), note="print first")

    # print orientation + fit
    for p in pieces:
        p["print"] = orient(p["solid"], p["down"])
        p["spin"] = 0
        bb = p["print"].BoundingBox()
        p["dims"] = (bb.xlen, bb.ylen, bb.zlen)
        p["hull"] = hull2d(p["print"])
        p["fit"], p["why"] = fits(printer, p["dims"], p["hull"])
        if not p["fit"] and p["dims"][2] <= H_ + 1e-6:
            spin = best_spin(printer, p["dims"][2], p["hull"])
            if spin:
                p["print"] = orient(p["print"].rotate(V(0, 0, 0), V(0, 0, 1), spin), (0, 0, -1))
                p["spin"] = spin
                bb = p["print"].BoundingBox()
                p["dims"] = (bb.xlen, bb.ylen, bb.zlen)
                p["hull"] = hull2d(p["print"])
                p["fit"], p["why"] = fits(printer, p["dims"], p["hull"])
                p["note"] += ", turned %d deg on the plate" % spin
        p["volume"] = p["solid"].Volume()
        mat = MATERIALS[p["mat"]]
        p["mass_g"] = p["volume"] * mat["rho"]
        p["hours"] = p["volume"] / mat["q"] / 3600.0 + 0.25
    checks += run_checks(I, C, parts, pieces, printer)
    return {"I": I, "C": C, "parts": parts, "pieces": pieces, "checks": checks, "printer": printer}


def run_checks(I, C, parts, pieces, printer):
    out = []

    def chk(name, ok, detail=""):
        out.append((name, bool(ok), detail))

    pr = PRINTERS[printer]
    W_, D_, H_ = usable(printer)
    bad = [p["id"] + " " + p["why"] for p in pieces if not p["fit"]]
    chk("every piece fits the %s (%.0f x %.0f x %.0f usable, clear of the %gx%g corner)" % (
        pr["name"], W_, D_, H_, pr["exclude"][0], pr["exclude"][1]), not bad, "; ".join(bad))
    inval = [p["id"] for p in pieces if not (p["solid"].isValid() and len(p["solid"].Solids()) == 1)]
    chk("every piece is one valid closed solid", not inval, ", ".join(inval))
    # pieces of a part do not overlap and add back up to the part (less the lap clearances)
    for pid in ("P1", "P2", "P4"):
        ps = [p for p in pieces if p["part"] == pid]
        ov = 0.0
        for i in range(len(ps)):
            for j in range(i + 1, len(ps)):
                ov = max(ov, ps[i]["solid"].intersect(ps[j]["solid"]).Volume())
        vp = parts[pid]["solid"].Volume()
        vs = sum(p["volume"] for p in ps)
        gap = parts[pid].get("gap", 0.0)
        chk("%s sections: no overlap, volume adds up" % pid,
            ov < 0.01 and abs(vp - gap - vs) < 0.5 and 0 <= gap < 0.005 * vp,
            "overlap %.3f mm3, part %.0f, sections %.0f, glue clearance %.0f mm3" % (ov, vp, vs, gap))
    # interfaces
    to, co = I["hood_top_open"], I["cold_open"]
    chk("hood top opening = shelf cold opening", all(abs(to[k] - co[k]) < 1e-6 for k in (0, 1, 3, 4)),
        "%.1f-%.1f x %.1f-%.1f" % (to[0], to[3], to[1], to[4]))
    ax0, ay0, ax1, ay1 = I["ac_outlet"]
    m = min(ax0 - C["ix0"], C["ix1"] - ax1, ay0 - C["iy0"], C["iy1"] - ay1)
    chk("collar foot clears the AC outlet by the hood margin", m >= I["P"]["hood_margin"] - 1e-6,
        "min margin %.1f mm (hood_margin %.0f)" % (m, I["P"]["hood_margin"]))
    chk("collar seats on the model hood gasket (same outline and hole)",
        abs(C["x0"] - I["gasket"][0]) + abs(C["y1"] - I["gasket"][4]) + abs(C["ix0"] - I["gasket_hole"][0]) < 1e-6,
        "gasket %.1f x %.1f, hole %.1f x %.1f" % (C["x1"] - C["x0"], C["y1"] - C["y0"], C["ix1"] - C["ix0"],
                                                 C["iy1"] - C["iy0"]))
    hi = parts["P1"]["info"]
    hb = I["hood_box"]
    blocked = [("(%.0f, %.0f)" % (x, y)) for x, y in hi["holes_top"]
               if parts["P1"]["solid"].intersect(cyl((x, y, hb[2] - 5), (x, y, hb[5] - PR["wall"] - 0.2), 3.0)).Volume() > 0.01]
    chk("every hood screw can be driven straight up from below (floor opening or driver hole)", not blocked,
        ("blocked: " + ", ".join(blocked)) if blocked else "%d screws, %d through driver holes" % (
            len(hi["holes_top"]), len(hi["drivers"])))
    lift_clear = C["z_seat"] + PR["lift"] - 10.0 - I["ac_top"]
    chk("raised collar + gasket clears the AC top", lift_clear >= 10.0, "%.1f mm" % lift_clear)
    ei = parts["P4"]["info"]
    rs_ac = I["ac_spigot"]["r"]
    chk("elbow socket slides over the AC spigot", 0.2 <= ei["rs"] - rs_ac <= 1.0 and ei["seat_min"] < rs_ac,
        "socket bore D%.1f over spigot D%.1f, seat D%.1f" % (2 * ei["rs"], 2 * rs_ac, 2 * ei["seat_min"]))
    db = I["duct"]["bore"]
    chk("elbow outlet spigot fits inside the duct", 0.2 <= db - ei["ro2"] <= 1.0,
        "OD %.1f in duct bore %.1f" % (2 * ei["ro2"], 2 * db))
    end = ei["outlet_end"]
    chk("elbow outlet on the duct axis", abs(end.x - I["duct"]["p0"].x) < 1e-6 and abs(end.z - I["duct"]["p0"].z) < 1e-6,
        "x %.1f z %.1f" % (end.x, end.z))
    wi = parts["P5"]["info"]
    skin_hole = 2 * (I["elbow"]["ri"] + 1.0)
    chk("wall spigot inner tube passes the skin hole and fits the duct",
        2 * wi["ro_in"] < skin_hole - 1.0 and 0.2 <= db - wi["ro_in"] <= 1.0,
        "OD %.1f, skin hole D%.1f, duct bore %.1f" % (2 * wi["ro_in"], skin_hole, 2 * db))
    hs = wi["holes"]
    x, z = I["wall"]["p0"].x, I["wall"]["p0"].z
    pcd = sorted(round(2 * math.hypot(hx - x, hz - z), 2) for hx, hz, _ in hs)
    chk("flange bolt holes = rear-skin M5 holes (DXF)", len(hs) == 4 and max(pcd) - min(pcd) < 0.01 and
        math.hypot(hs[0][0] - x, hs[0][1] - z) + hs[0][2] / 2 + 5.0 < I["wall"]["rf"],
        "%d x D%.1f on PCD %.1f, flange D%.0f" % (len(hs), hs[0][2] if hs else 0, pcd[0] if pcd else 0,
                                                  2 * I["wall"]["rf"]))
    # touchscreen pod against the upper-door holes (CP-SRA16-SMP-001)
    import sheetmetal as SMP
    sm = SMP.build(I["P"])
    du = [p for p in sm["parts"] if p.id == "DU1"][0]
    dz0 = du.place[2] + sm["D"]["z_base0"]
    door = sorted((round(h["u"], 2), round(h["v"] + dz0, 2), h["d"]) for h in du.holes if "ELC-001" in h["use"])
    pi = parts["P6"]["info"]
    pd = SMP.SM["pod"]
    pod = sorted([(round(pd["xc"] + du_, 2), round(pd["zc"] + dv, 2), pd["rivnut_d"]) for du_, dv in pi["bolts"]] +
                 [(round(pd["xc"] + pi["cable"][0], 2), round(pd["zc"] + pi["cable"][1], 2), pd["cable_d"])])
    chk("touchscreen pod holes = upper-door holes (DXF)", door == pod and len(door) == 3,
        "%d holes, pod at x %.0f z %.0f" % (len(door), pd["xc"], pd["zc"]))
    bw, bh = EL["board"]
    pw, ph, pdp = pi["pocket"]
    chk("panel fits the pod pocket, window inside the glass", pw - bw <= 1.2 and ph - bh <= 1.2 and
        pi["window"][0] < bw - 4 and pi["window"][1] < bh - 4, "pocket %.1f x %.1f for %.1f x %.1f board" % (pw, ph, bw, bh))
    return out


def summary(pack):
    pr = PRINTERS[pack["printer"]]
    lines = ["%s rev %s - printed parts for %s (usable %.0f x %.0f x %.0f)" % (
        DOC_NO, REV, pr["name"], *usable(pack["printer"]))]
    for p in pack["pieces"]:
        lines.append("  %-5s %-44s %-4s x%d  %6.1f x %6.1f x %6.1f  %6.0f g  %5.1f h  %s" % (
            p["id"], p["name"], p["mat"], p["qty"], *p["dims"], p["mass_g"] * p["qty"], p["hours"] * p["qty"],
            "fits" if p["fit"] else "DOES NOT FIT: " + p["why"]))
    for name, ok, det in pack["checks"]:
        lines.append("  [%s] %s%s" % ("ok" if ok else "FAIL", name, (" - " + det) if det else ""))
    return "\n".join(lines)


def main(argv):
    printer, overrides = "x1c", {}
    it = iter(argv)
    for a in it:
        if a == "--printer":
            printer = next(it)
        elif "=" in a:
            k, v = a.split("=", 1)
            overrides[k] = float(v)
    pack = build(overrides or None, printer)
    print(summary(pack))
    return 0 if all(ok for _, ok, _ in pack["checks"]) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
