"""
Parametric component library for the Denza B8 roof-rack concepts.

Coordinate system (vehicle frame, millimetres):
    X  forward (+X = front bumper), origin mid-wheelbase
    Y  left (+Y = driver-side in RHD AU market, passenger in LHD)
    Z  up, Z = 0 is the ground plane

Every builder returns a list of Part(name, shape, material) so the
same geometry drives the STEP assembly, the STL render meshes and the BOM.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import cadquery as cq

# --------------------------------------------------------------------------
# Vehicle reference data — Denza B8 (published figures, see docs/README.md)
# --------------------------------------------------------------------------
B8 = dict(
    length=5195.0,
    width=1994.0,
    height=1905.0,          # includes factory raised roof rails
    wheelbase=2920.0,
    track=1670.0,
    front_overhang=1000.0,
    tyre_d=820.0,           # 265/60 R20 ~ 820 mm
    tyre_w=265.0,
    rail_y=575.0,           # rail centreline offset from vehicle centreline (est.)
    rail_top_z=1905.0,
    rail_x=(-2330.0, 560.0),  # rail fore/aft extent (est.)
    roof_z=1845.0,          # roof skin crown height (est.)
)
B8["front_x"] = B8["length"] / 2
B8["rear_x"] = -B8["length"] / 2
B8["front_axle_x"] = B8["front_x"] - B8["front_overhang"]
B8["rear_axle_x"] = B8["front_axle_x"] - B8["wheelbase"]


@dataclass
class Part:
    name: str
    shape: cq.Workplane
    material: str
    meta: dict = field(default_factory=dict)


def safe_fillet(wp: cq.Workplane, selector: str, r: float) -> cq.Workplane:
    try:
        out = wp.edges(selector).fillet(r)
        out.val()  # force evaluation
        return out
    except Exception:
        return wp


def box(cx, cy, cz, lx, ly, lz) -> cq.Workplane:
    """Axis-aligned box centred at (cx, cy, cz)."""
    return cq.Workplane("XY").box(lx, ly, lz).translate((cx, cy, cz))


def rbox(cx, cy, cz, lx, ly, lz, r) -> cq.Workplane:
    b = box(cx, cy, cz, lx, ly, lz)
    return safe_fillet(b, "|Z", r)


def rbox_all(cx, cy, cz, lx, ly, lz, r) -> cq.Workplane:
    b = box(cx, cy, cz, lx, ly, lz)
    try:
        out = b.edges().fillet(r)
        out.val()
        return out
    except Exception:
        return safe_fillet(b, "|Z", r)


def cyl_y(cx, cy, cz, r, length) -> cq.Workplane:
    """Cylinder with axis along Y."""
    return (cq.Workplane("XZ").circle(r).extrude(length / 2, both=True)
            .translate((cx, cy, cz)))


def cyl_z(cx, cy, z0, r, h) -> cq.Workplane:
    return cq.Workplane("XY").circle(r).extrude(h).translate((cx, cy, z0))


def cyl_x(cx, cy, cz, r, length) -> cq.Workplane:
    return (cq.Workplane("YZ").circle(r).extrude(length / 2, both=True)
            .translate((cx, cy, cz)))


def planform(x0, x1, w_rear, w_front, z0, h, r) -> cq.Workplane:
    """Tapered plan-view prism (rear at x0, front at x1) with rounded corners."""
    pts = [(x0, -w_rear / 2), (x1, -w_front / 2), (x1, w_front / 2), (x0, w_rear / 2)]
    wp = cq.Workplane("XY").polyline(pts).close().extrude(h).translate((0, 0, z0))
    return safe_fillet(wp, "|Z", r)


def side_profile(pts, width, spline=True) -> cq.Workplane:
    """Extrude an XZ side profile symmetric about Y=0.

    pts: list of (x, z). If spline, the upper surface is a spline through the
    points and the profile is closed back along the base.
    """
    wp = cq.Workplane("XZ")
    if spline:
        base0, base1 = pts[0], pts[-1]
        wp = wp.moveTo(*base0).spline(pts[1:], includeCurrent=True)
        wp = wp.lineTo(base1[0], min(p[1] for p in pts)).lineTo(base0[0], min(p[1] for p in pts)).close()
    else:
        wp = wp.polyline(pts).close()
    return wp.extrude(width / 2, both=True)


# --------------------------------------------------------------------------
# Mounting hardware
# --------------------------------------------------------------------------
def rail_clamp_feet(xs, height, name="foot") -> list[Part]:
    """Clamp feet for the B8 raised rails. Rubber-lined jaw + aero cover."""
    parts = []
    y = B8["rail_y"]
    z0 = B8["rail_top_z"] - 40  # jaws wrap the rail
    for i, x in enumerate(xs):
        for s in (+1, -1):
            body = rbox_all(x, s * y, z0 + (height + 40) / 2, 110, 70, height + 40, 12)
            parts.append(Part(f"{name}_{i}_{'L' if s > 0 else 'R'}", body, "rack_black"))
            pad = box(x, s * y, z0 + 4, 110, 76, 8)
            parts.append(Part(f"{name}_pad_{i}_{'L' if s > 0 else 'R'}", pad, "rubber"))
    return parts


def aero_crossbar(x, z, span, name, chord=80, thick=26) -> Part:
    """Elliptical aero crossbar spanning Y."""
    bar = (cq.Workplane("XZ").ellipse(chord / 2, thick / 2)
           .extrude(span / 2, both=True).translate((x, 0, z)))
    return Part(name, bar, "anodised_grey")


# --------------------------------------------------------------------------
# Lighting
# --------------------------------------------------------------------------
def led_bar(cx, cy, cz, length, height=60, depth=55, axis="y", name="led_bar",
            lens_mat="led_white", facing=+1, curve=0.0) -> list[Part]:
    """Housing + emissive lens. axis = direction the bar runs along;
    facing = +1/-1 along the perpendicular horizontal axis."""
    if axis == "y":
        housing = rbox_all(cx - facing * 6, cy, cz, depth, length, height, 8)
        lens = rbox(cx + facing * (depth / 2 - 3), cy, cz, 6, length - 24, height - 16, 3)
    else:
        housing = rbox_all(cx, cy - facing * 6, cz, length, depth, height, 8)
        lens = rbox(cx, cy + facing * (depth / 2 - 3), cz, length - 24, 6, height - 16, 3)
    return [Part(f"{name}_housing", housing, "rack_black"),
            Part(f"{name}_lens", lens, lens_mat)]


def led_pod(cx, cy, cz, size=95, depth=70, facing=(1, 0), name="led_pod",
            lens_mat="led_white") -> list[Part]:
    """Square 3"-class LED pod (e.g. 40-60 W). facing is a unit XY vector."""
    fx, fy = facing
    if abs(fx) >= abs(fy):
        housing = rbox_all(cx, cy, cz, depth, size, size, 10)
        lens = rbox(cx + fx * (depth / 2), cy, cz, 6, size - 18, size - 18, 6)
    else:
        housing = rbox_all(cx, cy, cz, size, depth, size, 10)
        lens = rbox(cx, cy + fy * (depth / 2), cz, size - 18, 6, size - 18, 6)
    bracket = box(cx, cy, cz - size / 2 - 12, 30, 30, 24)
    return [Part(f"{name}_housing", housing, "rack_black"),
            Part(f"{name}_lens", lens, lens_mat),
            Part(f"{name}_bracket", bracket, "rack_black")]


# --------------------------------------------------------------------------
# Drone hangar (Lingyuan-class: dock + clamshell lids + pad + charging)
# --------------------------------------------------------------------------
HANGAR = dict(L=700.0, W=640.0, base_h=150.0, lid_h=65.0)


def drone_hangar(cx, cy, z0, open_=False, name="hangar", lid_mat="hangar_shell",
                 base_mat="hangar_shell") -> list[Part]:
    L, W, bh, lh = HANGAR["L"], HANGAR["W"], HANGAR["base_h"], HANGAR["lid_h"]
    parts = []
    base = rbox_all(cx, cy, z0 + bh / 2, L, W, bh, 18)
    # landing well
    well = rbox(cx, cy, z0 + bh - 20, L - 70, W - 70, 40.0 + 0.01, 30)
    base = base.cut(well)
    parts.append(Part(f"{name}_base", base, base_mat))

    pad = rbox(cx, cy, z0 + bh - 38, L - 80, W - 80, 4, 26)
    parts.append(Part(f"{name}_pad", pad, "pad_dark"))
    # landing marker: ring + H
    ring = (cq.Workplane("XY").circle(200).circle(184).extrude(1.5)
            .translate((cx, cy, z0 + bh - 36)))
    h1 = box(cx, cy - 55, z0 + bh - 35.25, 170, 22, 1.5)
    h2 = box(cx, cy + 55, z0 + bh - 35.25, 170, 22, 1.5)
    h3 = box(cx, cy, z0 + bh - 35.25, 22, 110, 1.5)
    parts.append(Part(f"{name}_marker", ring.union(h1).union(h2).union(h3), "marking"))
    # pogo charging contacts (four corners of the centering zone)
    for sx in (-1, 1):
        for sy in (-1, 1):
            c = cyl_z(cx + sx * 120, cy + sy * 140, z0 + bh - 36, 14, 4)
            parts.append(Part(f"{name}_contact_{sx}{sy}", c, "copper"))
    # status light ring on base flanks
    for s in (-1, 1):
        strip = box(cx, cy + s * (W / 2 + 0.5), z0 + 40, L - 160, 3, 10)
        parts.append(Part(f"{name}_status_{'L' if s > 0 else 'R'}", strip, "led_cyan"))

    # clamshell lids hinge along X at the outer top edges (y = +/- W/2)
    for s in (-1, 1):
        lid = rbox_all(0, -s * W / 4, lh / 2, L, W / 2 - 4, lh, 16)
        if open_:
            # local hinge line is the outer bottom edge (y = 0, z = 0); swing outward
            lid = lid.rotate((0, 0, 0), (1, 0, 0), -s * 115)
        lid = lid.translate((cx, cy + s * W / 2, z0 + bh))
        parts.append(Part(f"{name}_lid_{'L' if s > 0 else 'R'}", lid, lid_mat))
    return parts


def drone(cx, cy, cz, yaw_deg=0.0, name="drone", spinning=False) -> list[Part]:
    """Compact folding-class quadcopter (~Air 3S envelope, 258x326x106 unfolded)."""
    parts = []
    body = rbox_all(0, 0, 0, 175, 92, 62, 18)
    nose = rbox_all(95, 0, -6, 30, 70, 46, 12)
    body = body.union(nose)
    parts.append(("body", body, "drone_grey"))
    gimbal = (cq.Workplane("XY").sphere(24).translate((112, 0, -30)))
    lens = cyl_x(134, 0, -30, 11, 8)
    parts.append(("gimbal", gimbal, "drone_dark"))
    parts.append(("lens", lens, "glass_black"))
    for sx in (-1, 1):
        for sy in (-1, 1):
            mx, my = sx * 108, sy * 140
            ax0, ay0 = sx * 40, sy * 30
            alen = math.hypot(mx - ax0, my - ay0)
            ang = math.degrees(math.atan2(my - ay0, mx - ax0))
            arm = (rbox((ax0 + mx) / 2, (ay0 + my) / 2, 11, alen, 18, 14, 6)
                   .rotate(((ax0 + mx) / 2, (ay0 + my) / 2, 0), ((ax0 + mx) / 2, (ay0 + my) / 2, 1), ang))
            motor = cyl_z(mx, my, 2, 16, 24)
            prop = cyl_z(mx, my, 27, 118 if spinning else 10, 1.5)
            parts.append((f"arm_{sx}{sy}", arm, "drone_grey"))
            parts.append((f"motor_{sx}{sy}", motor, "drone_dark"))
            if spinning:
                parts.append((f"prop_{sx}{sy}", prop, "prop_blur"))
            else:
                blade = box(mx, my, 28, 220, 18, 2).rotate((mx, my, 0), (mx, my, 1), 35 * sx * sy)
                parts.append((f"prop_{sx}{sy}", blade, "drone_dark"))
    out = []
    for n, s, m in parts:
        s = s.rotate((0, 0, 0), (0, 0, 1), yaw_deg).translate((cx, cy, cz))
        out.append(Part(f"{name}_{n}", s, m))
    return out


# --------------------------------------------------------------------------
# RF payload: ADS-B, LoRa, Wi-Fi/BLE survey ("wardriving"), GNSS
# --------------------------------------------------------------------------
def whip(cx, cy, z0, length, base_r=22, tip_r=8, name="whip", mat="antenna_white") -> list[Part]:
    base = cyl_z(cx, cy, z0, base_r + 8, 30)
    rod = (cq.Workplane("XY").circle(base_r).workplane(offset=length)
           .circle(tip_r).loft().translate((cx, cy, z0 + 30)))
    cap = cq.Workplane("XY").sphere(tip_r).translate((cx, cy, z0 + 30 + length))
    return [Part(f"{name}_mount", base, "rack_black"),
            Part(f"{name}_radome", rod.union(cap), mat)]


def shark_fin(cx, cy, z0, length=230, height=150, width=60, name="fin",
              mat="antenna_white") -> Part:
    # swept leading edge rising rearward to a near-vertical trailing edge
    xf, xr = cx + length / 2, cx - length / 2
    fin = (cq.Workplane("XZ").moveTo(xf, z0)
           .spline([(cx + length * 0.05, z0 + height * 0.45), (xr + 40, z0 + height)], includeCurrent=True)
           .lineTo(xr + 8, z0 + height - 30).lineTo(xr, z0).close()
           .extrude(width / 2, both=True).translate((0, cy, 0)))
    fin = safe_fillet(fin, "|Y", 6)
    return Part(name, fin, mat)


def puck(cx, cy, z0, r=45, h=22, name="puck", mat="antenna_black") -> Part:
    p = cq.Workplane("XY").circle(r).extrude(h).translate((cx, cy, z0))
    p = safe_fillet(p, ">Z", min(h * 0.45, 10))
    return Part(name, p, mat)


def rf_enclosure(cx, cy, z0, L=360, W=260, H=90, name="rf_bay") -> list[Part]:
    """IP67 payload bay: SDR, SBC, Wi-Fi radios, LoRa gateway, PoE, fusing."""
    b = rbox_all(cx, cy, z0 + H / 2, L, W, H, 14)
    fins = []
    for i in range(7):
        fins.append(box(cx - L / 2 + 50 + i * (L - 100) / 6, cy, z0 + H + 7, 8, W - 60, 14))
    hs = fins[0]
    for f in fins[1:]:
        hs = hs.union(f)
    glands = []
    for i in range(4):
        glands.append(Part(f"{name}_gland_{i}",
                           cyl_x(cx - L / 2 - 8, cy - 90 + i * 60, z0 + 40, 11, 16), "rubber"))
    return [Part(f"{name}_case", b, "anodised_grey"),
            Part(f"{name}_heatsink", hs, "rack_black")] + glands
