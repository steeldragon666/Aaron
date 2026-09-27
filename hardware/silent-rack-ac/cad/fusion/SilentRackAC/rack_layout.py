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

VERSION = "1.2.0"

DEFAULTS = {
    # --- rack / envelope -------------------------------------------------
    "ru_count": 16,          # rack units above the AC bay
    "ru_pitch": 44.45,       # EIA-310 rack unit
    "ext_w": 622.4,          # external width  (= 614 frame + 2 x 4.2 skin)
    "ext_d": 1072.4,         # external depth  (= 1064 frame + 2 x 4.2 skin)
    "front_plenum": 130.0,   # front liner -> front 19in mounting face (cold aisle)
    "rail_spacing": 700.0,   # front -> rear 19in mounting faces
    # --- wall build-up (outside -> in) -------------------------------------
    "skin_t": 1.2,           # laser-cut steel sheet skin (powder coated)
    "mlv_t": 3.0,            # mass-loaded vinyl (5 kg/m2), bonded to the skin
    "frame": 30.0,           # 30x30 welded steel SHS frame; section = acoustic foam depth
    # --- sheet-metal parts ---------------------------------------------------
    "sheet_max_l": 1200.0,   # largest flat blank the cutter takes (long side)
    "sheet_max_w": 800.0,    # ... and short side; skins are split over frame rails to fit
    "strip_w": 50.0,         # cover strip over each skin joint
    "strip_t": 1.2,          # strips, door stiffeners, keepers, skirts (nests in the skin offcuts)
    "door_stiff": 20.0,      # 20x20 folded angle frame (strip_t) bonded inside each door
    # --- base ------------------------------------------------------------
    "caster_h": 100.0,       # floor -> underside of base frame (castor + pad)
    "floor_t": 18.0,         # bay floor ply
    "cleat": 20.0,           # ledge width: 20x3 steel flat bar welded to the rails
    "cleat_t": 3.0,          # ledge thickness
    "pad_t": 8.0,            # castor mounting plate welded under each frame corner
    "pad_w": 100.0,          # castor pad size (square)
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
    "ac_out_w": 350.0,       # top cold-air outlet (louvres) width  (tape: flap ~348)
    "ac_out_d": 110.0,       # top cold-air outlet depth            (VERIFY)
    "ac_out_y": 70.0,        # outlet front edge from AC front face (VERIFY)
    "ac_drain_x": 30.0,      # drain plug centre from AC left side  (VERIFY)
    "ac_drain_z": 40.0,      # drain plug centre above floor (measured ~40)
    "ac_disp_x": 190.0,      # display centre from AC left side     (front photos)
    "ac_disp_z": 690.0,      # display centre above floor           (VERIFY)
    # --- ducts / window ----------------------------------------------------
    "hood_margin": 15.0,     # hood collar clearance around the AC outlet (tolerance)
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
    "skin_t": ("mm", "Steel skin sheet thickness"),
    "mlv_t": ("mm", "Mass-loaded vinyl thickness"),
    "frame": ("mm", "Frame SHS size (square) = acoustic foam depth"),
    "sheet_max_l": ("mm", "Largest flat blank, long side"),
    "sheet_max_w": ("mm", "Largest flat blank, short side"),
    "strip_w": ("mm", "Skin joint cover strip width"),
    "strip_t": ("mm", "Strips, stiffeners, keepers, skirts - sheet thickness"),
    "door_stiff": ("mm", "Door stiffener angle leg"),
    "caster_h": ("mm", "Floor to underside of base frame (castor + pad)"),
    "floor_t": ("mm", "Bay floor ply"),
    "cleat": ("mm", "Ledge flat-bar width"),
    "cleat_t": ("mm", "Ledge flat-bar thickness"),
    "pad_t": ("mm", "Castor pad plate thickness"),
    "pad_w": ("mm", "Castor pad plate size"),
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
    "ac_out_w": ("mm", "AC top outlet width (measured ~348)"),
    "ac_out_d": ("mm", "AC top outlet depth (VERIFY)"),
    "ac_out_y": ("mm", "AC top outlet front edge (VERIFY)"),
    "ac_drain_x": ("mm", "AC drain plug from left side (VERIFY)"),
    "ac_drain_z": ("mm", "AC drain plug height"),
    "ac_disp_x": ("mm", "AC display centre from left (photos)"),
    "ac_disp_z": ("mm", "AC display centre height (VERIFY)"),
    "hood_margin": ("mm", "Hood collar clearance around AC outlet"),
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
    "shs": (0.24, 0.26, 0.29),          # powder-coated steel frame (anthracite)
    "alu": (0.78, 0.80, 0.83),
    "angle": (0.66, 0.68, 0.71),
    "ply": (0.86, 0.73, 0.55),
    "sheet": (0.80, 0.81, 0.80),        # powder-coated steel skins (RAL 7035 light grey)
    "hw": (0.60, 0.62, 0.65),           # stainless hardware
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


# fabrication rules shared with tools/weldment.py and tools/sheetmetal.py
FIX_EDGE = 40.0      # first/last panel fixing from a frame member end
FIX_PITCH = 250.0    # max panel-fixing pitch along a frame member
DOOR_CLEAR = 2.0     # door stiffener frame inset inside the frame opening
RAIL_END = 5.0       # 19in rail beyond the U space at each end
# door hardware (defaults - check against the parts bought, see CP-SRA16-SMP-001)
HW = {
    "edge": 60.0,          # hinge/latch centre from a door edge (min)
    "split_clear": 75.0,   # ... and from a skin joint (cover strip)
    "knuckle_r": 5.0,      # lift-off hinge knuckle radius (axis sits on the front-left corner)
    "hinge_t": 2.0,
    "hinge_len": 100.0,
    "hinge_holes": (-35.0, 0.0, 35.0),   # rivets per leaf, along the hinge
    "leaf_over": 10.0,     # leaf beyond its rivet line
    "latch_holes": ((6.0, -9.0), (6.0, 9.0), (34.0, -9.0), (34.0, 9.0)),  # (from hw line, from centre)
    "keeper_rivets": (-12.0, 12.0),
    "keeper_h": 40.0,
    "keeper_gap": 1.0,     # keeper leg B off the side skin
    "keeper_leg_b": 22.0,  # keeper leg B depth behind the door face
    "catch": (14.0, 6.0, 16.0),          # catch slot centre (behind door face), width, height
    "handle_pitch": 160.0,
}
# plinth skirts (folded L under the base rails, between the castor pads)
SKIRT = {"inset": 6.0, "flange": 28.0, "floor_gap": 10.0, "pad_gap": 2.0, "slot_z": (35.0, 75.0),
         "slot_fr": 50.0, "pitch_fr": 72.0, "slot_side": 60.0, "pitch_side": 85.0, "drain_d": 20.5}


def even_positions(a0, a1, pitch, nmin=2):
    """Evenly spaced positions from a0 to a1 with spacing <= pitch."""
    if a1 <= a0:
        return [(a0 + a1) / 2.0]
    n = max(nmin, int(math.ceil((a1 - a0) / pitch - 1e-9)) + 1)
    return [a0 + i * (a1 - a0) / (n - 1) for i in range(n)]


def piece_limit(width, P):
    """Longest allowed piece length for a skin of this width (blank <= sheet_max_l x sheet_max_w)."""
    return P["sheet_max_w"] if width > P["sheet_max_w"] else P["sheet_max_l"]


def split_positions(z0, z1, cands, limit):
    """Fewest split lines (chosen from cands, frame rail centrelines) so no piece is longer than limit."""
    out, cur = [], z0
    cs = sorted(c for c in cands if z0 < c < z1)
    while z1 - cur > limit + 1e-6:
        ok = [c for c in cs if cur < c <= cur + limit]
        if not ok:
            break                                   # validate() reports it
        cur = max(ok)
        out.append(cur)
    return out


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
    D["skin"] = P["skin_t"] + P["mlv_t"]
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
    D["ext_h"] = D["z_toprail1"] + P["mlv_t"] + P["skin_t"]
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
    D["rail_z0"] = D["z_rack0"] - RAIL_END          # 19in rails run past the U space so the end holes keep a web
    D["rail_z1"] = D["z_rack1"] + RAIL_END
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
    # outlet barb in the rear skirt, clear of the castor corner (hose jogs across under the floor)
    D["drain_out_x"] = max(D["drain_x"], D["skin"] + P["pad_w"] + SKIRT["pad_gap"] + 30.0)
    D["drain_out_z"] = 60.0
    # window
    D["win_xc"] = D["x_ac0"] + P["ac_disp_x"]
    D["win_zc"] = D["z_ac0"] + P["ac_disp_z"]
    # room-air inlet (floor opening under the riser box)
    D["inlet_y0"] = D["y_in1"] - 172.0
    D["inlet_y1"] = D["y_in1"] - 12.0
    # ---- sheet-metal skins: split on frame rail centrelines so every blank fits the cutter
    fz0, fz1 = D["z_base0"], D["z_toprail1"]
    rails = [(D["z_midrail0"] + D["z_midrail1"]) / 2.0, (D["z_srail0"] + D["z_srail1"]) / 2.0]
    D["side_splits"] = split_positions(fz0, fz1, rails, piece_limit(P["ext_d"] - 2 * D["skin"], P))
    D["rear_splits"] = split_positions(fz0, fz1, rails, piece_limit(P["ext_w"], P))
    # doors split on the shelf rail centreline (3 mm gap), 2 mm clear under the top panel
    D["door_lo_z"] = (fz0, D["z_door_split"] - 1.5)
    D["door_up_z"] = (D["z_door_split"] + 1.5, fz1 - 2.0)
    # door stiffener frame and the hardware lines on it (rivets go through skin + angle)
    D["stiff_x0"] = D["x_in0"] + DOOR_CLEAR
    D["stiff_x1"] = D["x_in1"] - DOOR_CLEAR
    D["hw_x_left"] = D["stiff_x0"] + P["door_stiff"] / 2.0     # hinge door-leaf rivets
    D["hw_x_right"] = D["stiff_x1"] - P["door_stiff"] / 2.0    # keeper rivets + handle screws
    D["hw_y_side"] = D["hw_x_left"]                             # hinge frame leaf / latch base on the side skins
    # side-panel screws on the front posts (weld pack rule); hinges and latches sit midway between them
    D["post_fix_z"] = even_positions(fz0 + FIX_EDGE, fz1 - FIX_EDGE, FIX_PITCH)
    mids = [(a + b) / 2.0 for a, b in zip(D["post_fix_z"][:-1], D["post_fix_z"][1:])]

    def hw_z(z0, z1):
        return [m for m in mids if z0 + HW["edge"] <= m <= z1 - HW["edge"]
                and all(abs(m - c) >= HW["split_clear"] for c in D["side_splits"])]
    lo, up = hw_z(*D["door_lo_z"]), hw_z(*D["door_up_z"])
    D["hinge_z_lower"] = lo if len(lo) <= 3 else [lo[0], lo[len(lo) // 2], lo[-1]]
    D["hinge_z_upper"] = up if len(up) <= 2 else [up[0], up[-1]]
    D["latch_z_lower"] = [lo[0], lo[-1]] if len(lo) > 1 else lo
    D["latch_z_upper"] = [up[0], up[-1]] if len(up) > 1 else up
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
    for nm, ply in (("floor", D["floor_t"]), ("partition", D["partition_t"]), ("shelf", D["shelf_t"])):
        if ply + D["cleat_t"] > D["frame"] - 2.0:
            w.append("%s ply + ledge (%.0f) does not fit in the %.0f mm rail" % (nm, ply + D["cleat_t"], D["frame"]))
    if D["pad_w"] < D["frame"] + 40:
        w.append("Castor pad narrower than frame + 40 mm")
    # every skin blank must fit the cutter (sheet_max_l x sheet_max_w)
    L, S = D["sheet_max_l"], D["sheet_max_w"]

    def fits(a, b):
        return max(a, b) <= L + 1e-6 and min(a, b) <= S + 1e-6
    for nm, width, cuts in (("side", D["ext_d"] - 2 * D["skin"], D["side_splits"]),
                            ("rear", D["ext_w"], D["rear_splits"])):
        zs = [D["z_base0"]] + cuts + [D["z_toprail1"]]
        for a, b in zip(zs[:-1], zs[1:]):
            if not fits(width, b - a):
                w.append("%s skin piece %.0f x %.0f exceeds %.0f x %.0f - no rail to split on" % (nm, width, b - a, L, S))
    if not fits(D["ext_w"], D["ext_d"]):
        w.append("Top skin %.0f x %.0f exceeds %.0f x %.0f" % (D["ext_w"], D["ext_d"], L, S))
    for nm, (a, b) in (("lower", D["door_lo_z"]), ("upper", D["door_up_z"])):
        if not fits(D["ext_w"], b - a):
            w.append("%s door %.0f x %.0f exceeds %.0f x %.0f" % (nm, D["ext_w"], b - a, L, S))
    if len(D["hinge_z_lower"]) < 2 or len(D["hinge_z_upper"]) < 2:
        w.append("Fewer than 2 hinge positions on a door")
    gx = (D["win_w"] + 40) / 2.0
    gz = (D["win_h"] + 40) / 2.0
    if not (D["stiff_x0"] + D["door_stiff"] < D["win_xc"] - gx and D["win_xc"] + gx < D["stiff_x1"] - D["door_stiff"]
            and D["z_base1"] + DOOR_CLEAR + D["door_stiff"] < D["win_zc"] - gz
            and D["win_zc"] + gz < D["z_srail0"] - DOOR_CLEAR - D["door_stiff"]):
        w.append("Window glazing unit clashes with the lower-door stiffener frame")
    return w


# ---------------------------------------------------------------- helpers
def _ledge_y(xface, inward, y0, y1, ztop, w, t):
    """Flat-bar ledge along Y, edge-welded to the rail face at xface; top face at ztop."""
    if inward > 0:
        return [box(xface, y0, ztop - t, xface + w, y1, ztop)]
    return [box(xface - w, y0, ztop - t, xface, y1, ztop)]


def _ledge_x(yface, inward, x0, x1, ztop, w, t):
    if inward > 0:
        return [box(x0, yface, ztop - t, x1, yface + w, ztop)]
    return [box(x0, yface - w, ztop - t, x1, yface, ztop)]


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
    s, f, mlv = D["skin"], P["frame"], P["mlv_t"]
    X0, X1, Y0, Y1 = D["x_in0"], D["x_in1"], D["y_in0"], D["y_in1"]
    cl = P["cleat"]
    zb0, zb1 = D["z_base0"], D["z_base1"]
    zt0, zt1 = D["z_toprail0"], D["z_toprail1"]
    zs0, zs1 = D["z_srail0"], D["z_srail1"]
    zm0, zm1 = D["z_midrail0"], D["z_midrail1"]
    zds = D["z_door_split"]

    ct, pt, pw = P["cleat_t"], P["pad_t"], P["pad_w"]
    FR = {"kind": "profile", "material": "Steel SHS %gx%g C350L0, welded (weld pack CP-SRA16-FRM-001)" % (f, f),
          "section": "%gx%g SHS" % (f, f)}
    LED = {"kind": "profile", "material": "Steel flat bar %gx%g, welded ledge" % (cl, ct), "section": "%gx%g FB" % (cl, ct)}

    # ======================================================== FRAME
    posts = [("FL", (s, X0), (s, Y0)), ("FR", (X1, W - s), (s, Y0)),
             ("RL", (s, X0), (Y1, DP - s)), ("RR", (X1, W - s), (Y1, DP - s))]
    for tag, (xa, xb), (ya, yb) in posts:
        part("Post %s" % tag, "Frame", "shs", [box(xa, ya, zb0, xb, yb, zt1)], bom=FR)
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
            part("Rail %s %s" % (lvl, sd), "Frame", "shs", [b], bom=FR)
    for tag, (ya, yb) in (("front", (D["y_frail"], D["y_frail"] + f)),
                          ("rear", (D["y_rrail"] - f, D["y_rrail"]))):
        part("Upright %s left" % tag, "Frame", "shs", [box(s, ya, zs1, X0, yb, zt0)], bom=FR)
        part("Upright %s right" % tag, "Frame", "shs", [box(X1, ya, zs1, W - s, yb, zt0)], bom=FR)

    # ledges (20x3 flat bar, edge-welded to the rail faces) carry the floor, partition and shelf ply
    zc_floor, zc_part, zc_shelf = D["z_floor0"], D["z_part0"], D["z_shelf0"]
    LY, LX = _ledge_y, _ledge_x
    part("Ledge floor left", "Frame", "shs", LY(X0, +1, Y0, Y1, zc_floor, cl, ct), bom=LED)
    part("Ledge floor right", "Frame", "shs", LY(X1, -1, Y0, Y1, zc_floor, cl, ct), bom=LED)
    part("Ledge floor front", "Frame", "shs", LX(Y0, +1, X0 + cl, X1 - cl, zc_floor, cl, ct), bom=LED)
    part("Ledge floor rear", "Frame", "shs", LX(Y1, -1, X0 + cl, X1 - cl, zc_floor, cl, ct), bom=LED)
    part("Ledge partition left", "Frame", "shs", LY(X0, +1, D["y_dock"], Y1, zc_part, cl, ct), bom=LED)
    part("Ledge partition right", "Frame", "shs", LY(X1, -1, D["y_dock"], Y1, zc_part, cl, ct), bom=LED)
    part("Ledge partition rear", "Frame", "shs", LX(Y1, -1, X0 + cl, X1 - cl, zc_part, cl, ct), bom=LED)
    part("Ledge shelf left", "Frame", "shs", LY(X0, +1, Y0, Y1, zc_shelf, cl, ct), bom=LED)
    part("Ledge shelf right", "Frame", "shs", LY(X1, -1, Y0, Y1, zc_shelf, cl, ct), bom=LED)
    part("Ledge shelf rear", "Frame", "shs", LX(Y1, -1, X0 + cl, X1 - cl, zc_shelf, cl, ct), bom=LED)
    # castor pads: plate welded under each corner (post + both base rails), 4x M8 tapped
    PAD = {"kind": "fab", "material": "Steel plate %gx%gx%g, 4x M8 tapped, welded (castor pad)" % (pw, pw, pt)}
    corners = {"FL": (s, s, 1, 1), "FR": (W - s, s, -1, 1), "RL": (s, DP - s, 1, -1), "RR": (W - s, DP - s, -1, -1)}
    for tag, (px, py, sx, sy) in corners.items():
        part("Castor pad %s" % tag, "Frame", "shs", [box(px, py, zb0 - pt, px + sx * pw, py + sy * pw, zb0)], bom=PAD)

    # ======================================================== PANELS & DOORS (laser-cut steel skins)
    sk = P["skin_t"]
    SKIN = {"kind": "sheet", "material": "Steel sheet %g mm, powder coat (laser cut, CP-SRA16-SMP-001)" % sk, "t": sk}
    MLV = {"kind": "sheet", "material": "Mass-loaded vinyl 5 kg/m2 (3 mm)", "t": mlv}
    STRIP = {"kind": "fab", "material": "Joint cover strip %gx%g steel, powder coat" % (P["strip_w"], P["strip_t"])}
    STIFF = {"kind": "fab", "material": "Door stiffener, %gx%gx%g folded steel angle, bonded" % (
        P["door_stiff"], P["door_stiff"], P["strip_t"])}
    # openings through the skins
    wx0, wx1 = D["win_xc"] - P["win_w"] / 2, D["win_xc"] + P["win_w"] / 2
    wz0, wz1 = D["win_zc"] - P["win_h"] / 2, D["win_zc"] + P["win_h"] / 2
    gx0, gx1 = wx0 - 20, wx1 + 20                                       # glazing unit (panes) 40 larger
    gz0, gz1 = wz0 - 20, wz1 + 20
    ex, ez = D["exh_x"], D["exh_run_z"]
    exh_hole_skin = cyl((ex, DP - s - 1, ez), (ex, DP + 1, ez), D["exh_ri"] + 1)
    slot = (D["x_mid"] - 100, D["x_mid"] + 100, zt0 - 146, zt0 - 106)   # cable entry slot x0,x1,z0,z1
    slot_cut = lambda y0, y1: box(slot[0], y0, slot[2], slot[1], y1, slot[3])
    sw2, st = P["strip_w"] / 2.0, P["strip_t"]

    def pieces(cuts):
        zs = [zb0] + list(cuts) + [zt1]
        return [(zs[i] + (0.5 if i else 0.0), zs[i + 1] - (0.5 if i < len(zs) - 2 else 0.0)) for i in range(len(zs) - 1)]
    # side skins: one piece per bay between the split rails, cover strip over each joint
    for side, (xs0, xs1), (xm0, xm1), (xj0, xj1) in (("left", (0, sk), (sk, s), (-st, 0)),
                                                     ("right", (W - sk, W), (W - s, W - sk), (W, W + st))):
        for i, (za, zb) in enumerate(pieces(D["side_splits"])):
            part("Side panel %s %d" % (side, i + 1), "Panels & Doors", "sheet", [box(xs0, s, za, xs1, DP - s, zb)], bom=SKIN)
        part("Side panel %s MLV" % side, "Panels & Doors", "mlv", [box(xm0, s, zb0, xm1, DP - s, zt1)], bom=MLV)
        for j, zj in enumerate(D["side_splits"]):
            part("Joint strip %s %d" % (side, j + 1), "Panels & Doors", "sheet",
                 [box(xj0, s, zj - sw2, xj1, DP - s, zj + sw2)], bom=STRIP)
    part("Top panel MLV", "Panels & Doors", "mlv", [box(0, 0, zt1, W, DP, zt1 + mlv)], bom=MLV)
    part("Top panel", "Panels & Doors", "sheet", [box(0, 0, zt1 + mlv, W, DP, D["ext_h"])], bom=SKIN)
    for i, (za, zb) in enumerate(pieces(D["rear_splits"])):
        part("Rear panel %d" % (i + 1), "Panels & Doors", "sheet", [box(0, DP - sk, za, W, DP, zb)],
             [exh_hole_skin, slot_cut(DP - s - 1, DP + 1)], bom=SKIN)
    part("Rear panel MLV", "Panels & Doors", "mlv", [box(0, DP - s, zb0, W, DP - sk, zt1)],
         [exh_hole_skin, slot_cut(DP - s - 1, DP + 1)], bom=MLV)
    for j, zj in enumerate(D["rear_splits"]):
        part("Joint strip rear %d" % (j + 1), "Panels & Doors", "sheet", [box(0, DP, zj - sw2, W, DP + st, zj + sw2)],
             bom=STRIP)

    # doors: skin + MLV + bonded angle frame (legs inboard) + foam; hardware riveted through skin + angle
    ds, dt = P["door_stiff"], P["strip_t"]
    sx0, sx1 = D["stiff_x0"], D["stiff_x1"]
    win_skin = box(wx0, -1, wz0, wx1, sk + 1, wz1)
    for nm, lab, (dz0, dz1), (oz0, oz1) in (("lower", "Door lower (AC bay)", D["door_lo_z"], (zb1, zs0)),
                                           ("upper", "Door upper (rack)", D["door_up_z"], (zs1, zt0))):
        z0, z1 = oz0 + DOOR_CLEAR, oz1 - DOOR_CLEAR
        win = nm == "lower"
        part(lab, "Panels & Doors", "sheet", [box(0, 0, dz0, W, sk, dz1)], [win_skin] if win else [], bom=SKIN)
        ang = [box(sx0, sk, z0, sx0 + ds, sk + dt, z1), box(sx0 + ds - dt, sk + dt, z0, sx0 + ds, sk + ds, z1),
               box(sx1 - ds, sk, z0, sx1, sk + dt, z1), box(sx1 - ds, sk + dt, z0, sx1 - ds + dt, sk + ds, z1),
               box(sx0 + ds, sk, z0, sx1 - ds, sk + dt, z0 + ds),
               box(sx0 + ds, sk + dt, z0 + ds - dt, sx1 - ds, sk + ds, z0 + ds),
               box(sx0 + ds, sk, z1 - ds, sx1 - ds, sk + dt, z1),
               box(sx0 + ds, sk + dt, z1 - ds, sx1 - ds, sk + ds, z1 - ds + dt)]
        part("Door %s stiffener frame" % nm, "Panels & Doors", "sheet", ang, bom=STIFF)
        bands = [box(sx0 - 0.1, sk - 0.1, z0 - 0.1, sx0 + ds + 0.1, s + 0.1, z1 + 0.1),
                 box(sx1 - ds - 0.1, sk - 0.1, z0 - 0.1, sx1 + 0.1, s + 0.1, z1 + 0.1),
                 box(sx0 - 0.1, sk - 0.1, z0 - 0.1, sx1 + 0.1, s + 0.1, z0 + ds + 0.1),
                 box(sx0 - 0.1, sk - 0.1, z1 - ds - 0.1, sx1 + 0.1, s + 0.1, z1 + 0.1)]
        if win:
            bands.append(box(gx0 - 0.5, sk - 0.1, gz0 - 0.5, gx1 + 0.5, s + 0.1, gz1 + 0.5))
        part("Door %s MLV" % nm, "Panels & Doors", "mlv", [box(0, sk, dz0, W, s, dz1)], bands, bom=MLV)
    # double-glazed window in the lower door: pane, 10 mm EPDM spacer, pane, steel retainer, 8x M4
    GL = {"kind": "purchased", "material": "Polycarbonate 6 mm, %gx%g (double glazed window)" % (gx1 - gx0, gz1 - gz0)}
    part("Window pane outer", "Panels & Doors", "glass", [box(gx0, sk, gz0, gx1, sk + 6, gz1)], bom=GL, opacity=0.35)
    part("Window spacer", "Panels & Doors", "rubber", [box(gx0, sk + 6, gz0, gx1, sk + 16, gz1)],
         [box(wx0, sk + 5, wz0, wx1, sk + 17, wz1)], bom={"kind": "purchased", "material": "EPDM 10 mm spacer frame"})
    part("Window pane inner", "Panels & Doors", "glass", [box(gx0, sk + 16, gz0, gx1, sk + 22, gz1)], bom=GL, opacity=0.35)
    part("Window retainer", "Panels & Doors", "sheet", [box(gx0, sk + 22, gz0, gx1, sk + 22 + st, gz1)],
         [box(wx0, sk + 21, wz0, wx1, sk + 23 + st, wz1)],
         bom={"kind": "fab", "material": "Window retainer %g mm steel (CP-SRA16-SMP-001)" % st})
    # hinges (left) and toggle latches (right), riveted through the skins; pull handles
    HG = {"kind": "purchased", "material": "Lift-off butt hinge %g long, leaves %g, stainless, riveted" % (
        HW["hinge_len"], D["hw_x_left"] + HW["knuckle_r"] + HW["leaf_over"])}
    LT = {"kind": "purchased", "material": "Adjustable toggle latch, stainless, riveted"}
    KP = {"kind": "fab", "material": "Latch keeper bracket %g mm steel, folded (CP-SRA16-SMP-001)" % st}
    kr, ht, hl = HW["knuckle_r"], HW["hinge_t"], HW["hinge_len"]
    leaf = D["hw_x_left"] + HW["leaf_over"]
    for tag, zs_ in (("lower", D["hinge_z_lower"]), ("upper", D["hinge_z_upper"])):
        for i, zc_ in enumerate(zs_):
            part("Hinge %s %d" % (tag, i + 1), "Panels & Doors", "hw",
                 [cyl((-kr, -kr, zc_ - hl / 2), (-kr, -kr, zc_ + hl / 2), kr),
                  box(-kr, -ht, zc_ - hl / 2, leaf, 0, zc_ + hl / 2),
                  box(-ht, -kr, zc_ - hl / 2, 0, leaf, zc_ + hl / 2)], bom=HG)
    yh, kg, kh = D["hw_y_side"], HW["keeper_gap"], HW["keeper_h"] / 2.0
    for tag, zs_ in (("lower", D["latch_z_lower"]), ("upper", D["latch_z_upper"])):
        for i, zc_ in enumerate(zs_):
            part("Latch %s %d" % (tag, i + 1), "Panels & Doors", "hw",
                 [box(W, yh - 6, zc_ - 12, W + 14, yh + 49, zc_ + 12),
                  box(W + 4, HW["keeper_leg_b"] + 2, zc_ - 5, W + 9, yh - 6, zc_ + 5)], bom=LT)
            part("Latch keeper %s %d" % (tag, i + 1), "Panels & Doors", "hw",
                 [box(D["hw_x_right"] - 14, -st, zc_ - kh, W + kg + st, 0, zc_ + kh),
                  box(W + kg, -st, zc_ - kh, W + kg + st, HW["keeper_leg_b"], zc_ + kh)], bom=KP)
    HD = {"kind": "purchased", "material": "Pull handle %g mm c/c, M5" % HW["handle_pitch"]}
    hp = HW["handle_pitch"]
    for nm, h0 in (("Handle upper door", zds + 300), ("Handle lower door", zb0 + 380)):
        hx0, hx1 = D["hw_x_right"] - 7, D["hw_x_right"] + 7
        part(nm, "Panels & Doors", "steel",
             [box(hx0, -36, h0, hx1, -26, h0 + hp + 20), box(hx0, -27, h0, hx1, 0, h0 + 20),
              box(hx0, -27, h0 + hp, hx1, 0, h0 + hp + 20)], bom=HD)

    # ======================================================== ACOUSTIC LINING
    F40 = {"kind": "sheet", "material": "Melamine acoustic foam %g mm (FR, Class 0)" % f, "t": f}
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
    fd0, fd1 = sx0 + ds, sx1 - ds                                   # inside the door stiffener frame
    part("Foam door lower", "Acoustic Lining", "foam",
         [box(fd0, s, zb1 + DOOR_CLEAR + ds, fd1, Y0, zs0 - DOOR_CLEAR - ds)],
         [box(gx0 - 2, s - 1, gz0 - 2, gx1 + 2, Y0 + 1, gz1 + 2)], bom=F40)
    part("Foam door upper", "Acoustic Lining", "foam",
         [box(fd0, s, zs1 + DOOR_CLEAR + ds, fd1, Y0, zt0 - DOOR_CLEAR - ds)], bom=F40)
    # openings in the divider shelf (cold supply at front, hot return at rear)
    cold_open = (X0 + cl + 12, Y0 + cl, X1 - cl - 12, D["y_frail"] - 5)       # cold supply -> front plenum
    ret_open = (X0 + cl + 2, D["y_rrail"] + 10, X1 - cl - 2, Y1 - cl - 2)     # hot return <- rear plenum
    zsf0 = D["z_shelf_foam0"]
    hm = P["hood_margin"]
    hood_y1 = D["out_y1"] + hm + 10                                          # rear face of the cold hood
    part("Foam shelf underside", "Acoustic Lining", "foam",
         [box(X0 + cl, hood_y1, zsf0, X1 - cl, ret_open[1], D["z_shelf0"])], bom=F25)
    part("Foam partition underside", "Acoustic Lining", "foam",
         [box(X0 + cl, D["y_dock"], D["z_part0"] - P["partition_foam"], X1 - cl, Y1 - cl, D["z_part0"])], bom=F25)
    inlet = (X0 + 57, D["inlet_y0"], X1 - 57, D["inlet_y1"])
    dx, dyo = D["drain_x"], D["drain_y_out"]
    zuf0 = D["z_floor0"] - P["underfloor_foam"]
    uf_cut = [box(inlet[0], inlet[1], zuf0 - 1, inlet[2], inlet[3], D["z_floor0"] + 1),
              cyl((dx, dyo, zuf0 - 1), (dx, dyo, D["z_floor0"] + 1), 17)]
    if zuf0 < zb0:
        for px, py, sx, sy in corners.values():
            uf_cut.append(box(px, py, zuf0 - 1, px + sx * (pw + 2), py + sy * (pw + 2), zb0))
    part("Foam under floor", "Acoustic Lining", "foam",
         [box(X0 + cl, Y0 + cl, zuf0, X1 - cl, Y1 - cl, D["z_floor0"])], uf_cut,
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
    zct = zb0 - pt                                                # castor top plate under the pad
    CAS = {"kind": "purchased", "material": "Levelling castor, 75 mm wheel, 200 kg, braked, %g mm high" % zct}
    for tag, (px, py, sx, sy) in corners.items():
        cx, cy = px + sx * pw / 2.0, py + sy * pw / 2.0
        part("Castor %s" % tag, "Base, Tray & Drain", "caster",
             [box(cx - 40, cy - 40, zct - 6, cx + 40, cy + 40, zct),
              box(cx - 25, cy - 18, 60, cx + 25, cy + 18, zct - 5),
              cyl((cx - 16, cy, 37.5), (cx + 16, cy, 37.5), 37.5)], bom=CAS)
    SK = {"kind": "fab", "material": "Plinth skirt %g mm steel, folded L, slotted, powder coat (CP-SRA16-SMP-001)" % st}
    kt, ky, kf, kz0 = st, SKIRT["inset"], SKIRT["flange"], SKIRT["floor_gap"]
    xa, xb = s + pw + SKIRT["pad_gap"], W - s - pw - SKIRT["pad_gap"]
    ya, yb = s + pw + SKIRT["pad_gap"], DP - s - pw - SKIRT["pad_gap"]
    sz0, sz1 = SKIRT["slot_z"]

    def slots(a0, a1, pitch, w, skip=None):
        n = int((a1 - a0 - 50 + (pitch - w)) // pitch)
        c0 = (a0 + a1) / 2.0 - (n - 1) * pitch / 2.0
        out = [c0 + i * pitch for i in range(n)]
        return [c for c in out if skip is None or abs(c - skip) > w / 2 + 20]
    sf = slots(xa, xb, SKIRT["pitch_fr"], SKIRT["slot_fr"])
    dox, doz = D["drain_out_x"], D["drain_out_z"]
    sr = slots(xa, xb, SKIRT["pitch_fr"], SKIRT["slot_fr"], skip=dox)
    ss = slots(ya, yb, SKIRT["pitch_side"], SKIRT["slot_side"])
    hw_ = SKIRT["slot_fr"] / 2.0
    part("Skirt front", "Base, Tray & Drain", "skirt",
         [box(xa, ky, kz0, xb, ky + kt, zb0), box(xa, ky, zb0 - kt, xb, ky + kf, zb0)],
         [box(c - hw_, ky - 1, sz0, c + hw_, ky + kt + 1, sz1) for c in sf], bom=SK)
    part("Skirt rear", "Base, Tray & Drain", "skirt",
         [box(xa, DP - ky - kt, kz0, xb, DP - ky, zb0), box(xa, DP - ky - kf, zb0 - kt, xb, DP - ky, zb0)],
         [box(c - hw_, DP - ky - kt - 1, sz0, c + hw_, DP - ky + 1, sz1) for c in sr] +
         [cyl((dox, DP - ky - kt - 1, doz), (dox, DP - ky + 1, doz), SKIRT["drain_d"] / 2.0)], bom=SK)
    hs = SKIRT["slot_side"] / 2.0
    for side, (xf0, xf1), (xl0_, xl1_) in (("left", (ky, ky + kt), (ky, ky + kf)),
                                           ("right", (W - ky - kt, W - ky), (W - ky - kf, W - ky))):
        part("Skirt %s" % side, "Base, Tray & Drain", "skirt",
             [box(xf0, ya, kz0, xf1, yb, zb0), box(xl0_, ya, zb0 - kt, xl1_, yb, zb0)],
             [box(xf0 - 1, c - hs, sz0, xf1 + 1, c + hs, sz1) for c in ss], bom=SK)
    DR = {"kind": "purchased", "material": "16 mm ID clear PVC drain hose"}
    ya1 = D["y_ac1"] + 15
    part("Drain tundish + bulkhead", "Base, Tray & Drain", "pvc",
         [cyl((dx, dyo, ztr), (dx, dyo, ztr + 18), 20), cyl((dx, dyo, 90), (dx, dyo, ztr + 1), 15)],
         bom={"kind": "purchased", "material": "25 mm tank bulkhead + tundish"})
    part("Drain hose AC", "Base, Tray & Drain", "pvc",
         [cyl((dx, ya1, D["drain_z"]), (dx, dyo + 4, D["drain_z"]), 8),
          cyl((dx, dyo, D["drain_z"] + 4), (dx, dyo, ztr + 18), 8)], bom=DR)
    part("Drain hose under floor", "Base, Tray & Drain", "pvc",
         [cyl((dx, dyo, 90), (dx, dyo, doz - 4), 8), cyl((dx, dyo - 4, doz), (dx, DP - 40, doz), 8)] +
         ([cyl((dx - 4, DP - 40, doz), (dox + 4, DP - 40, doz), 8), cyl((dox, DP - 44, doz), (dox, DP, doz), 8)]
          if dox - dx > 1.0 else [cyl((dx, DP - 44, doz), (dx, DP, doz), 8)]), bom=DR)
    part("Drain outlet coupling", "Base, Tray & Drain", "pvc", [cyl((dox, DP, doz), (dox, DP + 25, doz), 11)],
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
    # collar/gasket opening = AC outlet + hood_margin all round (tolerates louvre offset)
    ox0, ox1, oy0, oy1 = D["out_x0"] - hm, D["out_x1"] + hm, D["out_y0"] - hm, D["out_y1"] + hm
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
    sock = 30.0                                            # elbow socket slides over the AC spigot (taped)
    part("Exhaust elbow (insulated)", "Airflow & Seals", "hot",
         [elbow(ec, (1, 0, 0), (0, -1, 0), (0, 0, 1), Rb, ro),
          cyl((ex, D["exh_y"], ezc - sock), (ex, D["exh_y"], ezc), ro)],
         [elbow(ec, (1, 0, 0), (0, -1, 0), (0, 0, 1), Rb, ri, pad=1.0),
          cyl((ex, D["exh_y"], ezc - sock - 1), (ex, D["exh_y"], ezc + 0.5), ri)],
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
    zr0, zr1 = D["rail_z0"], D["rail_z1"]
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
    spw = D["x_rail_out_l"] - X0
    SP = {"kind": "profile", "material": "Rail spacer / air dam, %gx%g SHS + packers, bolted to upright" % (f, f),
          "section": "%gx%g (%gx%g + %g packer)" % (spw, f, f, f, max(spw - f, 0))}
    for tag, (ya, yb) in (("front", (yfr, yfr + f)), ("rear", (yrr - f, yrr))):
        part("Rail spacer %s left" % tag, "19in Rack", "steel", [box(X0, ya, zs1, xl0, yb, zt0)], bom=SP)
        part("Rail spacer %s right" % tag, "19in Rack", "steel", [box(xr1, ya, zs1, X1, yb, zt0)], bom=SP)
    def dam(za, zb, zc, zd):
        # full width outside the rail ends (za..zb), narrowed round the rails where they overlap (zc..zd)
        out = [box(xl0, yfr, za, xr1, yfr + 12, zb)] if zb > za else []
        if zd > zc:
            out += [box(xl1, yfr, zc, xr0, yfr + 12, zd), box(xl0 + 2, yfr + 2, zc, xl1, yfr + 12, zd),
                    box(xr0, yfr + 2, zc, xr1 - 2, yfr + 12, zd)]
        return out
    part("Top air dam", "19in Rack", "steel", dam(zr1, zt0, D["z_rack1"], zr1),
         bom={"kind": "fab", "material": "12 mm foam-faced strip"})
    part("Bottom air dam", "19in Rack", "steel", dam(zs1, zr0, zr0, D["z_rack0"]),
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
        return D["z_rack0"] + (u - 1) * pitch                 # U1 starts at the rack datum, not the rail end

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
        "frame": "%gx%g steel SHS, welded" % (D["frame"], D["frame"]),
        "frame_outer_mm": (D["ext_w"] - 2 * D["skin"], D["ext_d"] - 2 * D["skin"],
                           round(D["z_toprail1"] - D["z_base0"], 1)),
    }


if __name__ == "__main__":
    parts, D = build_parts()
    print("SRA layout v%s: %d parts" % (VERSION, len(parts)))
    for k, v in summary(D).items():
        print("  %-24s %s" % (k, v))
    for msg in validate(D) or ["validate(): OK"]:
        print("  !", msg)
