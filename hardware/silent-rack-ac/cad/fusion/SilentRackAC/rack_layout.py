"""
rack_layout.py - single source of truth for the SRA-16 Silent AC Rack.

Pure Python (no CAD imports), so the *same* part list drives:
  * SilentRackAC.py              - Autodesk Fusion script (native bodies)
  * tools/build_cadquery.py      - CadQuery/OCC build -> STEP, GLB, checks, BOM

Units: millimetres.  Axes, viewed from the front of the cabinet:
  X = width,  left -> right   (X = 0 on the left outer face)
  Y = depth,  front -> rear   (Y = 0 on the front door outer face)
  Z = height, up              (Z = 0 on the floor)

Every Part is  union(add primitives) - union(cut primitives).
Primitives: axis-aligned boxes, cylinders between two points, and
90-degree elbows (quarter tori).

The AC reference geometry is the Dimplex GDC14RBA (476 W x 358 D x 840 H,
exhaust spigot on the floor of the rear-right notch, pointing UP).  Values
marked (VERIFY) in PARAM_DOC were estimated from photos + the Dimplex
manual and should be tape-checked before cutting panels.
"""

import math

VERSION = "1.0.0"

DEFAULTS = {
    # --- rack / envelope -------------------------------------------------
    "ru_count": 16,          # rack units above the AC bay
    "ru_pitch": 44.45,       # EIA-310 rack unit
    "ext_w": 650.0,          # external width
    "ext_d": 1100.0,         # external depth
    "front_plenum": 130.0,   # front liner -> front 19in mounting face (cold aisle)
    "rail_spacing": 700.0,   # front -> rear 19in mounting faces
    # --- wall build-up (outside -> in) -------------------------------------
    "ply_t": 15.0,           # birch ply skin
    "mlv_t": 3.0,            # mass-loaded vinyl (5 kg/m2)
    "frame": 40.0,           # 40x40 frame section = acoustic foam depth
    # --- base ------------------------------------------------------------
    "caster_h": 100.0,       # floor -> underside of base frame
    "floor_t": 18.0,         # bay floor ply
    "cleat": 20.0,           # 20x20x2 aluminium angle cleats
    "tray_t": 2.0,           # stainless drip tray base
    "tray_lip": 25.0,        # drip tray upstand
    "iso_t": 10.0,           # anti-vibration mat under the AC
    "underfloor_foam": 20.0, # lining on the underside of the bay floor (within base rail depth)
    # --- AC bay ----------------------------------------------------------
    "ac_front_gap": 25.0,    # door liner -> AC front face
    "hood_h": 80.0,          # AC top -> underside of shelf lining (louvre room)
    "shelf_t": 18.0,         # divider shelf ply
    "shelf_foam": 25.0,      # lining under the divider shelf
    "top_clear": 15.0,       # top of rack units -> top lining
    "rack_bottom_gap": 5.0,  # shelf top -> first rack unit
    "partition_t": 12.0,     # condenser/return partition ply
    "partition_foam": 25.0,  # lining under the partition
    "dock_gap": 10.0,        # AC back -> docking frame (compressed gasket)
    # --- Dimplex GDC14RBA (label + photos + manual) -------------------------
    "ac_w": 476.0,
    "ac_d": 358.0,
    "ac_h": 840.0,
    "ac_body_z": 45.0,       # underside of body (caster height)
    "ac_notch_w": 215.0,     # rear-right exhaust notch width  (VERIFY)
    "ac_notch_d": 178.0,     # rear-right exhaust notch depth  (VERIFY)
    "ac_split_z": 420.0,     # notch floor = upper/lower grille split (VERIFY)
    "ac_notch_top_z": 751.0, # underside of the top box over the notch (VERIFY)
    "ac_exh_od": 150.0,      # exhaust spigot OD (measured ~150)
    "ac_exh_collar_h": 40.0, # spigot height above notch floor (VERIFY)
    "ac_out_w": 340.0,       # top cold-air outlet (louvres) width  (VERIFY)
    "ac_out_d": 110.0,       # top cold-air outlet depth            (VERIFY)
    "ac_out_y": 70.0,        # outlet front edge from AC front face (VERIFY)
    "ac_drain_x": 30.0,      # drain plug centre from AC left side  (VERIFY)
    "ac_drain_z": 40.0,      # drain plug centre above floor (measured ~40)
    "ac_disp_x": 200.0,      # display centre from AC left side     (VERIFY)
    "ac_disp_z": 690.0,      # display centre above floor           (VERIFY)
    # --- ducts / window ----------------------------------------------------
    "exh_insul": 10.0,       # closed-cell insulation on the exhaust elbow/duct
    "exh_bend_r": 150.0,     # exhaust elbow centreline radius (1.0 D)
    "win_w": 140.0,          # lower-door viewing window (AC display + IR remote)
    "win_h": 200.0,
}

# name -> (unit, description) ; unit "mm" or "" (count)
PARAM_DOC = {
    "ru_count": ("", "Rack units above the AC bay"),
    "ru_pitch": ("mm", "Rack unit pitch (EIA-310)"),
    "ext_w": ("mm", "External width"),
    "ext_d": ("mm", "External depth"),
    "front_plenum": ("mm", "Cold plenum: door lining to front 19in face"),
    "rail_spacing": ("mm", "Front to rear 19in mounting faces"),
    "ply_t": ("mm", "Ply skin thickness"),
    "mlv_t": ("mm", "Mass-loaded vinyl thickness"),
    "frame": ("mm", "Frame section / acoustic foam depth"),
    "caster_h": ("mm", "Castor height (floor to base frame)"),
    "floor_t": ("mm", "Bay floor ply"),
    "cleat": ("mm", "Angle cleat leg"),
    "tray_t": ("mm", "Drip tray base"),
    "tray_lip": ("mm", "Drip tray upstand"),
    "iso_t": ("mm", "Anti-vibration mat"),
    "underfloor_foam": ("mm", "Under-floor lining"),
    "ac_front_gap": ("mm", "Door lining to AC front"),
    "hood_h": ("mm", "AC top to shelf lining"),
    "shelf_t": ("mm", "Divider shelf ply"),
    "shelf_foam": ("mm", "Divider shelf lining"),
    "top_clear": ("mm", "Top of rack units to top lining"),
    "rack_bottom_gap": ("mm", "Shelf to first rack unit"),
    "partition_t": ("mm", "Partition ply"),
    "partition_foam": ("mm", "Partition lining"),
    "dock_gap": ("mm", "AC back to docking frame"),
    "ac_w": ("mm", "AC width (label)"),
    "ac_d": ("mm", "AC depth (label)"),
    "ac_h": ("mm", "AC height incl. castors (label)"),
    "ac_body_z": ("mm", "AC body underside above floor"),
    "ac_notch_w": ("mm", "AC exhaust notch width (VERIFY)"),
    "ac_notch_d": ("mm", "AC exhaust notch depth (VERIFY)"),
    "ac_split_z": ("mm", "AC notch floor / grille split height (VERIFY)"),
    "ac_notch_top_z": ("mm", "AC top box underside (VERIFY)"),
    "ac_exh_od": ("mm", "AC exhaust spigot OD"),
    "ac_exh_collar_h": ("mm", "AC exhaust spigot height (VERIFY)"),
    "ac_out_w": ("mm", "AC top outlet width (VERIFY)"),
    "ac_out_d": ("mm", "AC top outlet depth (VERIFY)"),
    "ac_out_y": ("mm", "AC top outlet front edge (VERIFY)"),
    "ac_drain_x": ("mm", "AC drain plug from left side (VERIFY)"),
    "ac_drain_z": ("mm", "AC drain plug height"),
    "ac_disp_x": ("mm", "AC display centre from left (VERIFY)"),
    "ac_disp_z": ("mm", "AC display centre height (VERIFY)"),
    "exh_insul": ("mm", "Exhaust duct insulation"),
    "exh_bend_r": ("mm", "Exhaust elbow centreline radius"),
    "win_w": ("mm", "Viewing window width"),
    "win_h": ("mm", "Viewing window height"),
}

GROUPS = [
    "Frame",
    "Panels & Doors",
    "Acoustic Lining",
    "Base, Tray & Drain",
    "Airflow & Seals",
    "19in Rack",
    "AC Dimplex GDC14RBA (ref)",
    "Example IT (ref)",
]

# colours (r, g, b) 0..1
C = {
    "alu": (0.78, 0.80, 0.83),
    "angle": (0.66, 0.68, 0.71),
    "ply": (0.86, 0.73, 0.55),
    "mlv": (0.20, 0.20, 0.22),
    "foam": (0.33, 0.34, 0.37),
    "tray": (0.74, 0.76, 0.78),
    "rubber": (0.07, 0.07, 0.07),
    "caster": (0.12, 0.12, 0.13),
    "plate": (0.50, 0.50, 0.52),
    "skirt": (0.16, 0.16, 0.18),
    "pvc": (0.92, 0.92, 0.90),
    "cold": (0.36, 0.64, 0.95),
    "hot": (0.93, 0.45, 0.18),
    "room": (0.42, 0.72, 0.45),
    "gasket": (0.05, 0.05, 0.05),
    "steel": (0.13, 0.13, 0.15),
    "glass": (0.75, 0.88, 0.95),
    "ac_body": (0.05, 0.05, 0.06),
    "ac_grey": (0.78, 0.79, 0.80),
    "ac_grille": (0.17, 0.17, 0.18),
    "ac_collar": (0.26, 0.26, 0.28),
    "ac_led": (0.85, 0.12, 0.10),
    "it_body": (0.23, 0.24, 0.26),
    "it_blank": (0.10, 0.10, 0.11),
}


# ---------------------------------------------------------------- primitives
def box(x0, y0, z0, x1, y1, z1):
    return {"kind": "box",
            "min": (min(x0, x1), min(y0, y1), min(z0, z1)),
            "max": (max(x0, x1), max(y0, y1), max(z0, z1))}


def cyl(p0, p1, r):
    return {"kind": "cyl", "p0": tuple(p0), "p1": tuple(p1), "r": float(r)}


def elbow(c, axis, u, v, R, r, pad=0.0):
    """Quarter torus: centre c, torus axis, arc from c+R*u to c+R*v (90 deg).
    pad > 0 extends the sector past both end faces (use for cut tools)."""
    return {"kind": "elbow", "c": tuple(c), "axis": tuple(axis), "u": tuple(u),
            "v": tuple(v), "R": float(R), "r": float(r), "pad": float(pad)}


def elbow_clip_box(e):
    """Axis-aligned box that clips a full torus down to the elbow sector."""
    c, a, u, v = e["c"], e["axis"], e["u"], e["v"]
    R, r, pad = e["R"], e["r"], e["pad"]
    lo_a, hi_a = -pad, R + r + pad
    lo_c, hi_c = -(r + pad), r + pad
    pts = []
    for s in (lo_a, hi_a):
        for t in (lo_a, hi_a):
            for w in (lo_c, hi_c):
                pts.append(tuple(c[i] + s * u[i] + t * v[i] + w * a[i] for i in range(3)))
    mn = tuple(min(p[i] for p in pts) for i in range(3))
    mx = tuple(max(p[i] for p in pts) for i in range(3))
    return box(mn[0], mn[1], mn[2], mx[0], mx[1], mx[2])


def prim_bbox(p):
    k = p["kind"]
    if k == "box":
        return p["min"], p["max"]
    if k == "cyl":
        p0, p1, r = p["p0"], p["p1"], p["r"]
        mn, mx = [], []
        for i in range(3):
            if abs(p0[i] - p1[i]) > 1e-9:          # axis direction (axis-aligned use)
                mn.append(min(p0[i], p1[i]))
                mx.append(max(p0[i], p1[i]))
            else:
                mn.append(p0[i] - r)
                mx.append(p0[i] + r)
        return tuple(mn), tuple(mx)
    if k == "elbow":
        b = elbow_clip_box(dict(p, pad=0.0))
        return b["min"], b["max"]
    raise ValueError(k)


def prim_volume(p):
    """Exact volume of a single primitive (mm3)."""
    k = p["kind"]
    if k == "box":
        return (p["max"][0] - p["min"][0]) * (p["max"][1] - p["min"][1]) * (p["max"][2] - p["min"][2])
    if k == "cyl":
        L = math.dist(p["p0"], p["p1"])
        return math.pi * p["r"] ** 2 * L
    if k == "elbow":
        return (math.pi * p["r"] ** 2) * (2 * math.pi * p["R"]) / 4.0
    raise ValueError(k)


# ---------------------------------------------------------------- parameters
def resolve(overrides=None):
    P = dict(DEFAULTS)
    for k, v in (overrides or {}).items():
        if k in P:
            P[k] = type(DEFAULTS[k])(v) if not isinstance(DEFAULTS[k], int) else int(round(v))
    return P


def derive(P):
    D = dict(P)
    D["skin"] = P["ply_t"] + P["mlv_t"]
    D["wall"] = D["skin"] + P["frame"]
    D["x_in0"] = D["wall"]
    D["x_in1"] = P["ext_w"] - D["wall"]
    D["int_w"] = D["x_in1"] - D["x_in0"]
    D["x_mid"] = P["ext_w"] / 2.0
    D["y_in0"] = D["wall"]
    D["y_in1"] = P["ext_d"] - D["wall"]
    D["int_d"] = D["y_in1"] - D["y_in0"]
    D["y_frail"] = D["y_in0"] + P["front_plenum"]
    D["y_rrail"] = D["y_frail"] + P["rail_spacing"]
    D["rear_plenum"] = D["y_in1"] - D["y_rrail"]
    # heights
    D["z_base0"] = P["caster_h"]
    D["z_base1"] = P["caster_h"] + P["frame"]
    D["z_floor1"] = D["z_base1"]
    D["z_floor0"] = D["z_floor1"] - P["floor_t"]
    D["z_tray1"] = D["z_floor1"] + P["tray_t"]
    D["z_ac0"] = D["z_tray1"] + P["iso_t"]
    D["z_ac1"] = D["z_ac0"] + P["ac_h"]
    D["z_shelf_foam0"] = D["z_ac1"] + P["hood_h"]
    D["z_shelf0"] = D["z_shelf_foam0"] + P["shelf_foam"]
    D["z_shelf1"] = D["z_shelf0"] + P["shelf_t"]
    D["z_srail1"] = D["z_shelf1"]
    D["z_srail0"] = D["z_shelf1"] - P["frame"]
    D["z_rack0"] = D["z_shelf1"] + P["rack_bottom_gap"]
    D["z_rack1"] = D["z_rack0"] + P["ru_count"] * P["ru_pitch"]
    D["z_toprail0"] = D["z_rack1"] + P["top_clear"]
    D["z_toprail1"] = D["z_toprail0"] + P["frame"]
    D["ext_h"] = D["z_toprail1"] + P["mlv_t"] + P["ply_t"]
    D["z_split"] = D["z_ac0"] + P["ac_split_z"]          # partition top = notch floor
    D["z_part0"] = D["z_split"] - P["partition_t"]
    D["z_midrail1"] = D["z_split"]
    D["z_midrail0"] = D["z_split"] - P["frame"]
    D["z_door_split"] = (D["z_srail0"] + D["z_srail1"]) / 2.0
    # AC placement (centred across the bay, pushed to the front)
    D["x_ac0"] = D["x_in0"] + (D["int_w"] - P["ac_w"]) / 2.0
    D["x_ac1"] = D["x_ac0"] + P["ac_w"]
    D["y_ac0"] = D["y_in0"] + P["ac_front_gap"]
    D["y_ac1"] = D["y_ac0"] + P["ac_d"]
    D["y_dock"] = D["y_ac1"] + P["dock_gap"]
    D["ac_side_gap"] = (D["int_w"] - P["ac_w"]) / 2.0
    # 19in geometry (EIA-310: 450 opening, 465.1 hole centres, 482.6 panel)
    D["x_rail_in_l"] = D["x_mid"] - 225.0
    D["x_rail_out_l"] = D["x_mid"] - 245.0
    D["x_rail_in_r"] = D["x_mid"] + 225.0
    D["x_rail_out_r"] = D["x_mid"] + 245.0
    # exhaust
    D["exh_x"] = D["x_ac1"] - P["ac_notch_w"] / 2.0
    D["exh_y"] = D["y_ac1"] - P["ac_notch_d"] / 2.0
    D["exh_z0"] = D["z_split"]
    D["exh_z1"] = D["z_split"] + P["ac_exh_collar_h"]
    D["exh_ro"] = P["ac_exh_od"] / 2.0 + P["exh_insul"]
    D["exh_ri"] = P["ac_exh_od"] / 2.0
    D["exh_run_y0"] = D["exh_y"] + P["exh_bend_r"]
    D["exh_run_z"] = D["exh_z1"] + P["exh_bend_r"]
    # top outlet
    D["out_x0"] = D["x_ac0"] + (P["ac_w"] - P["ac_out_w"]) / 2.0
    D["out_x1"] = D["out_x0"] + P["ac_out_w"]
    D["out_y0"] = D["y_ac0"] + P["ac_out_y"]
    D["out_y1"] = D["out_y0"] + P["ac_out_d"]
    # drain
    D["drain_x"] = D["x_ac0"] + P["ac_drain_x"]
    D["drain_z"] = D["z_ac0"] + P["ac_drain_z"]
    D["drain_y_out"] = D["y_dock"] + 44.0          # tundish centre (lower zone)
    # window
    D["win_xc"] = D["x_ac0"] + P["ac_disp_x"]
    D["win_zc"] = D["z_ac0"] + P["ac_disp_z"]
    # room-air inlet (floor opening under the riser box)
    D["inlet_y0"] = D["y_in1"] - 172.0
    D["inlet_y1"] = D["y_in1"] - 12.0
    return D


def validate(D):
    """Return a list of human-readable warnings (empty = all good)."""
    w = []
    if D["ac_side_gap"] < 15:
        w.append("AC side gap %.0f mm < 15 mm - widen ext_w" % D["ac_side_gap"])
    if D["ru_count"] < 16:
        w.append("Only %d RU - brief asks for >= 16" % D["ru_count"])
    if D["hood_h"] < 60:
        w.append("hood_h %.0f mm leaves no room for the louvres" % D["hood_h"])
    top_box_underside = D["z_ac0"] + D["ac_notch_top_z"]
    # highest point of the insulated elbow while still under the AC top box
    dy = D["y_ac1"] - D["exh_run_y0"]
    zc = D["exh_z1"] + math.sqrt(max(D["exh_bend_r"] ** 2 - dy ** 2, 0.0)) + D["exh_ro"]
    if zc >= top_box_underside:
        w.append("Exhaust elbow (%.0f) hits AC top box (%.0f)" % (zc, top_box_underside))
    if D["exh_run_y0"] <= D["y_ac1"]:
        w.append("Exhaust elbow outlet is not behind the AC - increase exh_bend_r")
    if D["exh_run_z"] - D["exh_ro"] <= D["z_split"]:
        w.append("Exhaust duct clips the partition")
    if D["exh_run_z"] + D["exh_ro"] >= D["z_srail0"]:
        w.append("Exhaust duct clips the shelf rail")
    if D["front_plenum"] < 100:
        w.append("Front (cold) plenum < 100 mm")
    if D["rear_plenum"] < 100:
        w.append("Rear (hot) plenum %.0f mm < 100 mm" % D["rear_plenum"])
    if D["inlet_y0"] - D["y_dock"] < 250:
        w.append("Lower (condenser) zone too shallow for the inlet labyrinth")
    if D["ext_h"] > 2000:
        w.append("External height %.0f mm > 2000 mm (doorways)" % D["ext_h"])
    if D["y_ac1"] + 10 > D["inlet_y0"]:
        w.append("AC overlaps inlet riser")
    return w


# ---------------------------------------------------------------- helpers
def _angle_y(xface, inward, y0, y1, ztop, leg, t=2.0):
    """20x20 angle along Y: vertical leg on the wall at xface, flat leg under ztop."""
    if inward > 0:
        return [box(xface, y0, ztop - leg, xface + t, y1, ztop),
                box(xface, y0, ztop - t, xface + leg, y1, ztop)]
    return [box(xface - t, y0, ztop - leg, xface, y1, ztop),
            box(xface - leg, y0, ztop - t, xface, y1, ztop)]


def _angle_x(yface, inward, x0, x1, ztop, leg, t=2.0):
    if inward > 0:
        return [box(x0, yface, ztop - leg, x1, yface + t, ztop),
                box(x0, yface, ztop - t, x1, yface + leg, ztop)]
    return [box(x0, yface - t, ztop - leg, x1, yface, ztop),
            box(x0, yface - leg, ztop - t, x1, yface, ztop)]


# ---------------------------------------------------------------- the model
def build_parts(P=None):
    """Return (parts, D).  Each part: dict(name, group, color, opacity, add, cut, bom)."""
    P = resolve(P)
    D = derive(P)
    parts = []

    def part(name, group, color, add, cut=(), bom=None, opacity=1.0):
        parts.append({"name": name, "group": group, "color": C[color] if isinstance(color, str) else color,
                      "opacity": opacity, "add": list(add), "cut": list(cut),
                      "bom": bom or {"kind": "ref"}})

    W, DP = P["ext_w"], P["ext_d"]
    s, f, ply, mlv = D["skin"], P["frame"], P["ply_t"], P["mlv_t"]
    X0, X1, Y0, Y1 = D["x_in0"], D["x_in1"], D["y_in0"], D["y_in1"]
    cl = P["cleat"]
    zb0, zb1 = D["z_base0"], D["z_base1"]
    zt0, zt1 = D["z_toprail0"], D["z_toprail1"]
    zs0, zs1 = D["z_srail0"], D["z_srail1"]
    zm0, zm1 = D["z_midrail0"], D["z_midrail1"]
    zds = D["z_door_split"]

    FR = {"kind": "profile", "material": "Aluminium 4040 T-slot (alt. 40x40x2 SHS)", "section": "40x40"}
    ANG = {"kind": "profile", "material": "Aluminium angle 20x20x2", "section": "20x20x2 L"}

    # ======================================================== FRAME
    posts = [("FL", (s, X0), (s, Y0)), ("FR", (X1, W - s), (s, Y0)),
             ("RL", (s, X0), (Y1, DP - s)), ("RR", (X1, W - s), (Y1, DP - s))]
    for tag, (xa, xb), (ya, yb) in posts:
        part("Post %s" % tag, "Frame", "alu", [box(xa, ya, zb0, xb, yb, zt1)], bom=FR)
    levels = [("Base", zb0, zb1, ("front", "rear", "left", "right")),
              ("Mid", zm0, zm1, ("rear", "left", "right")),
              ("Shelf", zs0, zs1, ("front", "rear", "left", "right")),
              ("Top", zt0, zt1, ("front", "rear", "left", "right"))]
    for lvl, za, zb, sides in levels:
        for sd in sides:
            if sd == "front":
                b = box(X0, s, za, X1, Y0, zb)
            elif sd == "rear":
                b = box(X0, Y1, za, X1, DP - s, zb)
            elif sd == "left":
                b = box(s, Y0, za, X0, Y1, zb)
            else:
                b = box(X1, Y0, za, W - s, Y1, zb)
            part("Rail %s %s" % (lvl, sd), "Frame", "alu", [b], bom=FR)
    for tag, (ya, yb) in (("front", (D["y_frail"], D["y_frail"] + f)),
                          ("rear", (D["y_rrail"] - f, D["y_rrail"]))):
        part("Upright %s left" % tag, "Frame", "alu", [box(s, ya, zs1, X0, yb, zt0)], bom=FR)
        part("Upright %s right" % tag, "Frame", "alu", [box(X1, ya, zs1, W - s, yb, zt0)], bom=FR)

    # cleats: floor, partition, shelf
    zc_floor, zc_part, zc_shelf = D["z_floor0"], D["z_part0"], D["z_shelf0"]
    part("Cleat floor left", "Frame", "angle", _angle_y(X0, +1, Y0, Y1, zc_floor, cl), bom=ANG)
    part("Cleat floor right", "Frame", "angle", _angle_y(X1, -1, Y0, Y1, zc_floor, cl), bom=ANG)
    part("Cleat floor front", "Frame", "angle", _angle_x(Y0, +1, X0 + cl, X1 - cl, zc_floor, cl), bom=ANG)
    part("Cleat floor rear", "Frame", "angle", _angle_x(Y1, -1, X0 + cl, X1 - cl, zc_floor, cl), bom=ANG)
    part("Cleat partition left", "Frame", "angle", _angle_y(X0, +1, D["y_dock"], Y1, zc_part, cl), bom=ANG)
    part("Cleat partition right", "Frame", "angle", _angle_y(X1, -1, D["y_dock"], Y1, zc_part, cl), bom=ANG)
    part("Cleat partition rear", "Frame", "angle", _angle_x(Y1, -1, X0 + cl, X1 - cl, zc_part, cl), bom=ANG)
    part("Cleat shelf left", "Frame", "angle", _angle_y(X0, +1, Y0, Y1, zc_shelf, cl), bom=ANG)
    part("Cleat shelf right", "Frame", "angle", _angle_y(X1, -1, Y0, Y1, zc_shelf, cl), bom=ANG)
    part("Cleat shelf rear", "Frame", "angle", _angle_x(Y1, -1, X0 + cl, X1 - cl, zc_shelf, cl), bom=ANG)

    # ======================================================== PANELS & DOORS
    PLY = {"kind": "sheet", "material": "Birch ply 15 mm (alt. 16 mm MDF)", "t": ply}
    MLV = {"kind": "sheet", "material": "Mass-loaded vinyl 5 kg/m2 (3 mm)", "t": mlv}
    # openings through the skins
    wx0, wx1 = D["win_xc"] - P["win_w"] / 2, D["win_xc"] + P["win_w"] / 2
    wz0, wz1 = D["win_zc"] - P["win_h"] / 2, D["win_zc"] + P["win_h"] / 2
    ex, ez = D["exh_x"], D["exh_run_z"]
    exh_hole_skin = cyl((ex, DP - s - 1, ez), (ex, DP + 1, ez), D["exh_ri"] + 1)
    slot = (D["x_mid"] - 100, D["x_mid"] + 100, zt0 - 146, zt0 - 106)   # cable entry slot x0,x1,z0,z1
    slot_cut = lambda y0, y1: box(slot[0], y0, slot[2], slot[1], y1, slot[3])

    part("Side panel left", "Panels & Doors", "ply", [box(0, s, zb0, ply, DP - s, zt1)], bom=PLY)
    part("Side panel left MLV", "Panels & Doors", "mlv", [box(ply, s, zb0, s, DP - s, zt1)], bom=MLV)
    part("Side panel right", "Panels & Doors", "ply", [box(W - ply, s, zb0, W, DP - s, zt1)], bom=PLY)
    part("Side panel right MLV", "Panels & Doors", "mlv", [box(W - s, s, zb0, W - ply, DP - s, zt1)], bom=MLV)
    part("Top panel MLV", "Panels & Doors", "mlv", [box(0, 0, zt1, W, DP, zt1 + mlv)], bom=MLV)
    part("Top panel", "Panels & Doors", "ply", [box(0, 0, zt1 + mlv, W, DP, D["ext_h"])], bom=PLY)
    win_skin = box(wx0, -1, wz0, wx1, s + 1, wz1)
    part("Door lower (AC bay)", "Panels & Doors", "ply", [box(0, 0, zb0, W, ply, zds - 1.5)], [win_skin], bom=PLY)
    part("Door lower MLV", "Panels & Doors", "mlv", [box(0, ply, zb0, W, s, zds - 1.5)], [win_skin], bom=MLV)
    part("Door upper (rack)", "Panels & Doors", "ply", [box(0, 0, zds + 1.5, W, ply, zt1)], bom=PLY)
    part("Door upper MLV", "Panels & Doors", "mlv", [box(0, ply, zds + 1.5, W, s, zt1)], bom=MLV)
    part("Rear panel lower", "Panels & Doors", "ply", [box(0, DP - ply, zb0, W, DP, zds - 1.5)], [exh_hole_skin], bom=PLY)
    part("Rear panel lower MLV", "Panels & Doors", "mlv", [box(0, DP - s, zb0, W, DP - ply, zds - 1.5)], [exh_hole_skin], bom=MLV)
    part("Rear panel upper", "Panels & Doors", "ply", [box(0, DP - ply, zds + 1.5, W, DP, zt1)],
         [slot_cut(DP - s - 1, DP + 1)], bom=PLY)
    part("Rear panel upper MLV", "Panels & Doors", "mlv", [box(0, DP - s, zds + 1.5, W, DP - ply, zt1)],
         [slot_cut(DP - s - 1, DP + 1)], bom=MLV)
    GL = {"kind": "purchased", "material": "Polycarbonate 6 mm (double glazed window)"}
    part("Window pane outer", "Panels & Doors", "glass", [box(wx0, 3, wz0, wx1, 9, wz1)], bom=GL, opacity=0.35)
    part("Window pane inner", "Panels & Doors", "glass", [box(wx0, Y0 - 8, wz0, wx1, Y0 - 2, wz1)], bom=GL, opacity=0.35)
    HD = {"kind": "purchased", "material": "Pull handle 160 mm c/c"}
    for nm, h0 in (("Handle upper door", zds + 300), ("Handle lower door", zb0 + 380)):
        hx0, hx1 = W - 52, W - 38
        part(nm, "Panels & Doors", "steel",
             [box(hx0, -36, h0, hx1, -26, h0 + 180), box(hx0, -27, h0, hx1, 0, h0 + 20),
              box(hx0, -27, h0 + 160, hx1, 0, h0 + 180)], bom=HD)

    # ======================================================== ACOUSTIC LINING
    F40 = {"kind": "sheet", "material": "Melamine acoustic foam 40 mm (FR, Class 0)", "t": P["frame"]}
    F25 = {"kind": "sheet", "material": "Melamine acoustic foam 25 mm (FR, Class 0)", "t": 25.0}
    yf0, yf1 = D["y_frail"], D["y_frail"] + f
    yr0, yr1 = D["y_rrail"] - f, D["y_rrail"]
    for side, (xa, xb) in (("left", (s, X0)), ("right", (X1, W - s))):
        bays = [("lower", Y0, Y1, zb1, zm0), ("mid", Y0, Y1, zm1, zs0),
                ("rack front", Y0, yf0, zs1, zt0), ("rack middle", yf1, yr0, zs1, zt0),
                ("rack rear", yr1, Y1, zs1, zt0)]
        for bn, ya, yb, za, zb in bays:
            part("Foam side %s %s" % (side, bn), "Acoustic Lining", "foam", [box(xa, ya, za, xb, yb, zb)], bom=F40)
    exh_hole_foam = cyl((ex, Y1 - 1, ez), (ex, DP - s + 1, ez), D["exh_ro"] + 2)
    part("Foam rear lower", "Acoustic Lining", "foam", [box(X0, Y1, zb1, X1, DP - s, zm0)], bom=F40)
    part("Foam rear mid", "Acoustic Lining", "foam", [box(X0, Y1, zm1, X1, DP - s, zs0)], [exh_hole_foam], bom=F40)
    part("Foam rear rack", "Acoustic Lining", "foam", [box(X0, Y1, zs1, X1, DP - s, zt0)],
         [slot_cut(Y1 - 1, DP - s + 1)], bom=F40)
    part("Foam top", "Acoustic Lining", "foam", [box(X0, Y0, zt0, X1, Y1, zt1)], bom=F40)
    part("Foam door lower", "Acoustic Lining", "foam", [box(X0, s, zb1, X1, Y0, zs0)],
         [box(wx0, s - 1, wz0, wx1, Y0 + 1, wz1)], bom=F40)
    part("Foam door upper", "Acoustic Lining", "foam", [box(X0, s, zs1, X1, Y0, zt0)], bom=F40)
    # openings in the divider shelf (cold supply at front, hot return at rear)
    cold_open = (X0 + cl + 12, Y0 + cl, X1 - cl - 12, D["y_frail"] - 5)       # cold supply -> front plenum
    ret_open = (X0 + cl + 2, D["y_rrail"] + 10, X1 - cl - 2, Y1 - cl - 2)     # hot return <- rear plenum
    zsf0 = D["z_shelf_foam0"]
    hood_y1 = D["out_y1"] + 10                                               # rear face of the cold hood
    part("Foam shelf underside", "Acoustic Lining", "foam",
         [box(X0 + cl, hood_y1, zsf0, X1 - cl, ret_open[1], D["z_shelf0"])], bom=F25)
    part("Foam partition underside", "Acoustic Lining", "foam",
         [box(X0 + cl, D["y_dock"], D["z_part0"] - P["partition_foam"], X1 - cl, Y1 - cl, D["z_part0"])], bom=F25)
    inlet = (X0 + 57, D["inlet_y0"], X1 - 57, D["inlet_y1"])
    dx, dyo = D["drain_x"], D["drain_y_out"]
    zuf0 = D["z_floor0"] - P["underfloor_foam"]
    part("Foam under floor", "Acoustic Lining", "foam",
         [box(X0 + cl, Y0 + cl, zuf0, X1 - cl, Y1 - cl, D["z_floor0"])],
         [box(inlet[0], inlet[1], zuf0 - 1, inlet[2], inlet[3], D["z_floor0"] + 1),
          cyl((dx, dyo, zuf0 - 1), (dx, dyo, D["z_floor0"] + 1), 17)],
         bom={"kind": "sheet", "material": "Melamine acoustic foam 20 mm (FR, Class 0)", "t": P["underfloor_foam"]})

    # ======================================================== BASE, TRAY & DRAIN
    ztr = D["z_tray1"]
    part("Bay floor", "Base, Tray & Drain", "ply", [box(X0, Y0, D["z_floor0"], X1, Y1, D["z_floor1"])],
         [box(inlet[0], inlet[1], D["z_floor0"] - 1, inlet[2], inlet[3], D["z_floor1"] + 1),
          cyl((dx, dyo, D["z_floor0"] - 1), (dx, dyo, D["z_floor1"] + 1), 17)],
         bom={"kind": "sheet", "material": "Birch ply 18 mm", "t": P["floor_t"]})
    zl = ztr + P["tray_lip"]
    part("Drip tray", "Base, Tray & Drain", "tray",
         [box(X0, Y0, D["z_floor1"], X1, Y1, ztr),
          box(X0, Y0, ztr - 1, X1, Y0 + 2, zl), box(X0, Y1 - 2, ztr - 1, X1, Y1, zl),
          box(X0, Y0 + 1, ztr - 1, X0 + 2, Y1 - 1, zl), box(X1 - 2, Y0 + 1, ztr - 1, X1, Y1 - 1, zl)],
         [box(inlet[0], inlet[1], D["z_floor1"] - 1, inlet[2], inlet[3], ztr + 1),
          cyl((dx, dyo, D["z_floor1"] - 1), (dx, dyo, ztr + 1), 17)],
         bom={"kind": "fab", "material": "1.2 mm 304 stainless, folded + TIG corners"})
    part("Anti-vibration mat", "Base, Tray & Drain", "rubber",
         [box(D["x_ac0"], D["y_ac0"], ztr, D["x_ac1"], D["y_ac1"], D["z_ac0"])],
         bom={"kind": "purchased", "material": "10 mm neoprene/Sorbothane isolation mat"})
    CAS = {"kind": "purchased", "material": "100 mm levelling castor, 200 kg, braked"}
    for tag, (cx, cy) in (("FL", (X0, Y0)), ("FR", (X1, Y0)), ("RL", (X0, Y1)), ("RR", (X1, Y1))):
        part("Castor %s" % tag, "Base, Tray & Drain", "caster",
             [box(cx - 40, cy - 40, zb0 - 6, cx + 40, cy + 40, zb0),
              box(cx - 25, cy - 18, 60, cx + 25, cy + 18, zb0 - 5),
              cyl((cx - 16, cy, 37.5), (cx + 16, cy, 37.5), 37.5)], bom=CAS)
    SK = {"kind": "fab", "material": "1.5 mm perforated steel skirt, powder coat"}
    slots_f = [box(115 + i * 72, 9, 35, 165 + i * 72, 17, 75) for i in range(6)]
    part("Skirt front", "Base, Tray & Drain", "skirt", [box(100, 10, 10, W - 100, 16, zb0)], slots_f, bom=SK)
    slots_r = [box(115 + i * 72, DP - 17, 35, 165 + i * 72, DP - 9, 75) for i in range(1, 6)]
    part("Skirt rear", "Base, Tray & Drain", "skirt", [box(100, DP - 16, 10, W - 100, DP - 10, zb0)],
         slots_r + [cyl((dx, DP - 20, 60), (dx, DP - 5, 60), 10)], bom=SK)
    for side, (xa, xb) in (("left", (10, 16)), ("right", (W - 16, W - 10))):
        sl = [box(xa - 1, 130 + i * 85, 35, xb + 1, 190 + i * 85, 75) for i in range(10)]
        part("Skirt %s" % side, "Base, Tray & Drain", "skirt", [box(xa, 100, 10, xb, DP - 100, zb0)], sl, bom=SK)
    DR = {"kind": "purchased", "material": "16 mm ID clear PVC drain hose"}
    ya1 = D["y_ac1"] + 15
    part("Drain tundish + bulkhead", "Base, Tray & Drain", "pvc",
         [cyl((dx, dyo, ztr), (dx, dyo, ztr + 18), 20), cyl((dx, dyo, 90), (dx, dyo, ztr + 1), 15)],
         bom={"kind": "purchased", "material": "25 mm tank bulkhead + tundish"})
    part("Drain hose AC", "Base, Tray & Drain", "pvc",
         [cyl((dx, ya1, D["drain_z"]), (dx, dyo + 4, D["drain_z"]), 8),
          cyl((dx, dyo, D["drain_z"] + 4), (dx, dyo, ztr + 18), 8)], bom=DR)
    part("Drain hose under floor", "Base, Tray & Drain", "pvc",
         [cyl((dx, dyo, 90), (dx, dyo, 56), 8), cyl((dx, dyo - 4, 60), (dx, DP, 60), 8)], bom=DR)
    part("Drain outlet coupling", "Base, Tray & Drain", "pvc", [cyl((dx, DP, 60), (dx, DP + 25, 60), 11)],
         bom={"kind": "purchased", "material": "16 mm hose barb / quick-connect"})
    part("AC retention bar", "Base, Tray & Drain", "steel",
         [box(X0 + 12, D["y_ac0"] - 19, zl + 1, X1 - 12, D["y_ac0"] - 4, zl + 21)],
         bom={"kind": "fab", "material": "25x15 steel bar + 2 toggle clamps"})

    # ======================================================== AIRFLOW & SEALS
    part("Divider shelf", "Airflow & Seals", "ply", [box(X0, Y0, D["z_shelf0"], X1, Y1, D["z_shelf1"])],
         [box(cold_open[0], cold_open[1], D["z_shelf0"] - 1, cold_open[2], cold_open[3], D["z_shelf1"] + 1),
          box(ret_open[0], ret_open[1], D["z_shelf0"] - 1, ret_open[2], ret_open[3], D["z_shelf1"] + 1)],
         bom={"kind": "sheet", "material": "Birch ply 18 mm", "t": P["shelf_t"]})
    # cold hood: collar over the louvres + plenum box up into the shelf opening
    ox0, ox1, oy0, oy1 = D["out_x0"], D["out_x1"], D["out_y0"], D["out_y1"]
    za1 = D["z_ac1"]
    hz_col0, hz_col1, hz_top = za1 + 10, za1 + 30, D["z_shelf0"]          # hood seals to shelf ply
    hb = (X0 + cl, Y0 + 5, X1 - cl, hood_y1)                                 # hood box footprint
    part("Cold air hood", "Airflow & Seals", "cold",
         [box(ox0 - 10, oy0 - 10, hz_col0, ox1 + 10, oy1 + 10, hz_col1 + 1),
          box(hb[0], hb[1], hz_col1, hb[2], hb[3], hz_top)],
         [box(hb[0] + 6, hb[1] + 6, hz_col1 + 6, hb[2] - 6, hb[3] - 6, hz_top - 6),
          box(ox0, oy0, hz_col0 - 1, ox1, oy1, hz_col1 + 7),
          box(cold_open[0], cold_open[1], hz_top - 7, cold_open[2], cold_open[3], hz_top + 1)],
         bom={"kind": "fab", "material": "6 mm PP sheet / 3D-printed PETG, drop-collar"})
    part("Hood gasket", "Airflow & Seals", "gasket",
         [box(ox0 - 10, oy0 - 10, za1, ox1 + 10, oy1 + 10, hz_col0)],
         [box(ox0, oy0, za1 - 1, ox1, oy1, hz_col0 + 1)],
         bom={"kind": "purchased", "material": "EPDM closed-cell foam 10x10"})
    part("Partition", "Airflow & Seals", "ply", [box(X0, D["y_dock"], D["z_part0"], X1, Y1, D["z_split"])],
         bom={"kind": "sheet", "material": "Birch ply 12 mm", "t": P["partition_t"]})
    zpf = D["z_part0"] - P["partition_foam"]
    GK = {"kind": "purchased", "material": "EPDM closed-cell foam gasket 20x10"}
    part("Dock post left", "Airflow & Seals", "steel",
         [box(X0 + 2, D["y_dock"], ztr, D["x_ac0"] + 10, D["y_dock"] + 20, zpf)],
         bom={"kind": "fab", "material": "20x40 alu box section"})
    part("Dock post right", "Airflow & Seals", "steel",
         [box(D["x_ac1"] - 10, D["y_dock"], ztr, X1 - 2, D["y_dock"] + 20, zpf)],
         bom={"kind": "fab", "material": "20x40 alu box section"})
    zg = D["z_split"] - 20
    part("Dock gasket left", "Airflow & Seals", "gasket",
         [box(X0 + 2, D["y_ac1"], ztr, D["x_ac0"] + 10, D["y_dock"], zg),
          box(X0, D["y_ac1"], zl, X0 + 3, D["y_dock"], zg)], bom=GK)
    part("Dock gasket right", "Airflow & Seals", "gasket",
         [box(D["x_ac1"] - 10, D["y_ac1"], ztr, X1 - 2, D["y_dock"], zg),
          box(X1 - 3, D["y_ac1"], zl, X1, D["y_dock"], zg)], bom=GK)
    part("Partition gasket", "Airflow & Seals", "gasket",
         [box(X0, D["y_ac1"], zg, X1, D["y_dock"], D["z_split"])], bom=GK)
    part("Brush seal under AC", "Airflow & Seals", "rubber",
         [box(D["x_ac0"] + 10, D["y_ac1"], ztr, D["x_ac1"] - 10, D["y_dock"], D["z_ac0"] + P["ac_body_z"])],
         [cyl((dx, D["y_ac1"] - 1, D["drain_z"]), (dx, D["y_dock"] + 1, D["drain_z"]), 15)],
         bom={"kind": "purchased", "material": "25 mm nylon brush strip in alu carrier"})
    # condenser (room-air) inlet riser: lined box over the floor opening
    rx0, rx1, ry0 = X0 + 37, X1 - 37, D["inlet_y0"] - 20
    rz1 = ztr + 258
    part("Inlet riser box", "Airflow & Seals", "room",
         [box(rx0 + 11, ry0, ztr, rx1 - 11, ry0 + 12, rz1 - 11),
          box(rx0, ry0, ztr, rx0 + 12, Y1 - 2, rz1), box(rx1 - 12, ry0, ztr, rx1, Y1 - 2, rz1),
          box(rx0, ry0, rz1 - 12, rx1, Y1 - 2, rz1)],
         [box(rx0 + 20, ry0 - 1, ztr + 98, rx1 - 20, ry0 + 13, rz1 - 40)],
         bom={"kind": "fab", "material": "12 mm ply lined box (inlet labyrinth)"})
    part("Foam inlet riser", "Acoustic Lining", "foam",
         [box(rx0 + 12, ry0 + 12, rz1 - 37, rx1 - 12, Y1 - 2, rz1 - 12)], bom=F25)
    # exhaust: 90 deg elbow on the spigot -> straight run -> rear spigot + flange
    ezc = D["exh_z1"]
    ro, ri, Rb = D["exh_ro"], D["exh_ri"], P["exh_bend_r"]
    ec = (ex, D["exh_y"] + Rb, ezc)
    part("Exhaust elbow (insulated)", "Airflow & Seals", "hot",
         [elbow(ec, (1, 0, 0), (0, -1, 0), (0, 0, 1), Rb, ro)],
         [elbow(ec, (1, 0, 0), (0, -1, 0), (0, 0, 1), Rb, ri, pad=1.0)],
         bom={"kind": "purchased", "material": "150 mm 90deg rigid elbow + 10 mm insulation"})
    y_run0 = D["exh_run_y0"]
    part("Exhaust duct (insulated)", "Airflow & Seals", "hot",
         [cyl((ex, y_run0, ez), (ex, DP - s, ez), ro)],
         [cyl((ex, y_run0 - 1, ez), (ex, DP - s + 1, ez), ri)],
         bom={"kind": "purchased", "material": "150 mm rigid duct + 10 mm insulation"})
    part("Exhaust wall spigot", "Airflow & Seals", "hot",
         [cyl((ex, DP - s, ez), (ex, DP + 60, ez), ri), cyl((ex, DP, ez), (ex, DP + 6, ez), ri + 40)],
         [cyl((ex, DP - s - 1, ez), (ex, DP + 61, ez), ri - 3)],
         bom={"kind": "purchased", "material": "150 mm flanged wall spigot"})
    # cable entry: lined chamber behind the rear-panel slot
    cb = (D["x_mid"] - 150, Y1 - 80, zt0 - 166, D["x_mid"] + 150, Y1, zt0 - 20)
    part("Cable gland box", "Airflow & Seals", "steel",
         [box(cb[0], cb[1], cb[2], cb[3], cb[4], cb[5])],
         [box(cb[0] + 12, cb[1] + 12, cb[2] + 12, cb[3] - 12, cb[4] + 1, cb[5] - 12),
          box(cb[0] + 25, cb[1] - 1, cb[5] - 56, cb[3] - 25, cb[1] + 13, cb[5] - 16)],
         bom={"kind": "fab", "material": "12 mm ply lined cable box + brush strip"})

    part("Cable entry brush", "Airflow & Seals", "rubber",
         [box(slot[0], DP - s, slot[2], slot[1], DP, slot[3])],
         bom={"kind": "purchased", "material": "Brush-strip cable grommet 200x40"})

    # ======================================================== 19in RACK
    RL = {"kind": "purchased", "material": "19in rack strip, 2 mm steel, %dU" % P["ru_count"]}
    zr0, zr1 = D["z_rack0"], D["z_rack1"]
    yfr, yrr = D["y_frail"], D["y_rrail"]
    xl0, xl1 = D["x_rail_out_l"], D["x_rail_in_l"]
    xr0, xr1 = D["x_rail_in_r"], D["x_rail_out_r"]
    part("19in rail front left", "19in Rack", "steel",
         [box(xl0, yfr, zr0, xl1, yfr + 2, zr1), box(xl0, yfr + 1, zr0, xl0 + 2, yfr + f, zr1)], bom=RL)
    part("19in rail front right", "19in Rack", "steel",
         [box(xr0, yfr, zr0, xr1, yfr + 2, zr1), box(xr1 - 2, yfr + 1, zr0, xr1, yfr + f, zr1)], bom=RL)
    part("19in rail rear left", "19in Rack", "steel",
         [box(xl0, yrr, zr0, xl1, yrr + 2, zr1), box(xl0, yrr - f, zr0, xl0 + 2, yrr + 1, zr1)], bom=RL)
    part("19in rail rear right", "19in Rack", "steel",
         [box(xr0, yrr, zr0, xr1, yrr + 2, zr1), box(xr1 - 2, yrr - f, zr0, xr1, yrr + 1, zr1)], bom=RL)
    SP = {"kind": "profile", "material": "20x40 alu box, rail spacer / air dam", "section": "22x40 (20x40 + shim)"}
    for tag, (ya, yb) in (("front", (yfr, yfr + f)), ("rear", (yrr - f, yrr))):
        part("Rail spacer %s left" % tag, "19in Rack", "steel", [box(X0, ya, zs1, xl0, yb, zt0)], bom=SP)
        part("Rail spacer %s right" % tag, "19in Rack", "steel", [box(xr1, ya, zs1, X1, yb, zt0)], bom=SP)
    part("Top air dam", "19in Rack", "steel", [box(xl0, yfr, zr1, xr1, yfr + 12, zt0)],
         bom={"kind": "fab", "material": "12 mm foam-faced strip"})
    part("Bottom air dam", "19in Rack", "steel", [box(xl0, yfr, zs1, xr1, yfr + 12, zr0)],
         bom={"kind": "fab", "material": "12 mm foam-faced strip"})

    # ======================================================== AC (reference)
    ax, ay, az = D["x_ac0"], D["y_ac0"], D["z_ac0"]
    Wac, Dac = P["ac_w"], P["ac_d"]

    def L(x0, y0, z0, x1, y1, z1):
        return box(ax + x0, ay + y0, az + z0, ax + x1, ay + y1, az + z1)

    ACG = "AC Dimplex GDC14RBA (ref)"
    nw, nd = P["ac_notch_w"], P["ac_notch_d"]
    sz, ntz = P["ac_split_z"], P["ac_notch_top_z"]
    g7 = (40, sz + 5, Wac - nw - 6, ntz - 6)                # upper (evaporator) grille x0,z0,x1,z1
    g9 = (10, 60, Wac - 170, sz - 5)                        # lower (condenser) grille
    part("AC body", ACG, "ac_body", [L(0, 0, P["ac_body_z"], Wac, Dac, 780)],
         [L(Wac - nw, Dac - nd, sz, Wac + 1, Dac + 1, ntz),
          L(g7[0], Dac - 3, g7[1], g7[2], Dac + 1, g7[3]),
          L(g9[0], Dac - 3, g9[1], g9[2], Dac + 1, g9[3])])
    ob = (P["ac_out_y"], P["ac_out_y"] + P["ac_out_d"])
    oxl = (Wac - P["ac_out_w"]) / 2.0
    part("AC top cover", ACG, "ac_grey", [L(0, 0, 780, Wac, 262, P["ac_h"])],
         [L(oxl, ob[0], P["ac_h"] - 14, oxl + P["ac_out_w"], ob[1], P["ac_h"] + 1)])
    part("AC top box", ACG, "ac_body", [L(0, 262, 780, Wac, Dac, P["ac_h"])])
    part("AC outlet louvres", ACG, "ac_grille",
         [L(oxl, ob[0], P["ac_h"] - 14, oxl + P["ac_out_w"], ob[1], P["ac_h"] - 10)])
    part("AC evaporator grille (cool inlet)", ACG, "ac_grille", [L(g7[0], Dac - 2, g7[1], g7[2], Dac, g7[3])])
    part("AC condenser grille (hot inlet)", ACG, "ac_grille", [L(g9[0], Dac - 2, g9[1], g9[2], Dac, g9[3])])
    dxl = P["ac_disp_x"]
    part("AC display bezel", ACG, "ac_grey", [L(dxl - 60, -3, P["ac_disp_z"] - 130, dxl + 60, 0, P["ac_disp_z"] + 100)])
    part("AC display", ACG, "ac_led", [L(dxl - 30, -4, P["ac_disp_z"] - 40, dxl + 30, -3, P["ac_disp_z"] + 50)])
    part("AC exhaust spigot", ACG, "ac_collar",
         [cyl((D["exh_x"], D["exh_y"], D["exh_z0"]), (D["exh_x"], D["exh_y"], D["exh_z1"]), ri)],
         [cyl((D["exh_x"], D["exh_y"], D["exh_z0"] - 1), (D["exh_x"], D["exh_y"], D["exh_z1"] + 1), ri - 5)])
    part("AC drain plug", ACG, "rubber",
         [cyl((D["drain_x"], D["y_ac1"], D["drain_z"]), (D["drain_x"], D["y_ac1"] + 15, D["drain_z"]), 15)])
    for tag, (cx, cy) in (("FL", (40, 40)), ("FR", (Wac - 40, 40)), ("RL", (40, Dac - 40)), ("RR", (Wac - 40, Dac - 40))):
        part("AC castor %s" % tag, ACG, "caster",
             [cyl((ax + cx - 10, ay + cy, az + 20), (ax + cx + 10, ay + cy, az + 20), 20),
              L(cx - 8, cy - 8, 38, cx + 8, cy + 8, P["ac_body_z"])])

    # ======================================================== EXAMPLE IT (reference)
    ITG = "Example IT (ref)"
    pitch = P["ru_pitch"]

    def u_z(u):
        return zr0 + (u - 1) * pitch

    def unit(name, u0, n, depth, blank=False):
        z0, z1 = u_z(u0), u_z(u0 + n)
        ears = box(D["x_mid"] - 241.3, yfr - 2, z0, D["x_mid"] + 241.3, yfr, z1)
        if blank:
            part(name, ITG, "it_blank", [ears])
        else:
            part(name, ITG, "it_body", [ears, box(xl1 + 5, yfr - 1, z0, xr0 - 5, yfr + depth, z1)])

    n = P["ru_count"]
    if n >= 16:
        unit("1U switch (U%d)" % n, n, 1, 300)
        unit("Blank (U%d)" % (n - 1), n - 1, 1, 0, blank=True)
        unit("2U server A (U%d-%d)" % (n - 3, n - 2), n - 3, 2, 700)
        unit("2U server B (U%d-%d)" % (n - 5, n - 4), n - 5, 2, 700)
        unit("Blank 2U (U%d-%d)" % (n - 7, n - 6), n - 7, 2, 0, blank=True)
        unit("4U storage (U5-8)", 5, 4, 650)
        if n > 16:
            unit("Blank (U9-U%d)" % (n - 8), 9, n - 16, 0, blank=True)
        unit("Blank 2U (U3-4)", 3, 2, 0, blank=True)
        unit("2U UPS (U1-2)", 1, 2, 600)

    return parts, D


def summary(D):
    """Key numbers for docs / message boxes."""
    return {
        "external_mm": (D["ext_w"], D["ext_d"], round(D["ext_h"], 1)),
        "internal_width_mm": D["int_w"],
        "internal_depth_mm": D["int_d"],
        "rack_units": D["ru_count"],
        "rack_zone_z_mm": (round(D["z_rack0"], 1), round(D["z_rack1"], 1)),
        "ac_bay_floor_z_mm": D["z_ac0"],
        "ac_side_gap_mm": D["ac_side_gap"],
        "front_plenum_mm": D["front_plenum"],
        "rail_spacing_mm": D["rail_spacing"],
        "rear_plenum_mm": D["rear_plenum"],
        "exhaust_outlet_xyz_mm": (D["exh_x"], D["ext_d"], D["exh_run_z"]),
        "drain_outlet_xyz_mm": (D["drain_x"], D["ext_d"] + 25, 60.0),
        "partition_z_mm": D["z_split"],
    }


if __name__ == "__main__":
    parts, D = build_parts()
    print("SRA layout v%s: %d parts" % (VERSION, len(parts)))
    for k, v in summary(D).items():
        print("  %-24s %s" % (k, v))
    for msg in validate(D) or ["validate(): OK"]:
        print("  !", msg)
