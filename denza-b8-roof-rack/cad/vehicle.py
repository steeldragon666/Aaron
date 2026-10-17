"""
Denza B8 *proxy* body for fit-checking and rendering.

This is NOT a scan or OEM surface — it is an envelope model built from the
published overall dimensions (5195 x 1994 x 1905 mm, 2920 mm wheelbase,
1670 mm track). Before tooling, replace it with a 3D scan of the actual roof
and rails (see docs/README.md -> "Fit-check before production").
"""
from __future__ import annotations

import math

import cadquery as cq

from rack_lib import B8, Part, box, cyl_y, rbox, rbox_all, safe_fillet


def _greenhouse(grow=0.0) -> cq.Workplane:
    z0, z1 = 1180.0, 1842.0
    x0a, x0b = -2560.0 - grow, 1260.0 + grow   # beltline: rear .. windscreen base
    x1a, x1b = -2505.0 - grow, 470.0 + grow    # roofline: rear .. windscreen header
    w0, w1 = 1930.0 + 2 * grow, 1520.0 + 2 * grow
    c0, c1 = (x0a + x0b) / 2, (x1a + x1b) / 2
    gh = (cq.Workplane("XY").workplane(offset=z0).center(c0, 0).rect(x0b - x0a, w0)
          .workplane(offset=z1 - z0).center(c1 - c0, 0).rect(x1b - x1a, w1).loft())
    return safe_fillet(gh, "not(<Z)", 45)


def build_vehicle() -> list[Part]:
    L, W = B8["length"], B8["width"]
    fx, rx = B8["front_axle_x"], B8["rear_axle_x"]
    tr = B8["tyre_d"] / 2 + 10
    parts: list[Part] = []

    # lower body
    body = box(0, 0, (300 + 1180) / 2, L, W, 880)
    body = safe_fillet(body, "|Z", 170)
    # bonnet falls ~80 mm from the scuttle to the leading edge
    wedge = (cq.Workplane("XZ").polyline([(1250, 1181), (L / 2 + 50, 1095), (L / 2 + 50, 1300), (1250, 1300)])
             .close().extrude(W, both=True))
    body = body.cut(wedge)
    body = safe_fillet(body, ">Z or (|Y and >X)", 40)
    for ax in (fx, rx):
        body = body.cut(cyl_y(ax, 0, tr, tr + 50, W + 200))
    parts.append(Part("body_lower", body, "body_paint"))

    # wheel-arch flares + sill cladding
    for ax in (fx, rx):
        flare = cyl_y(ax, 0, tr, tr + 85, W + 24).cut(cyl_y(ax, 0, tr, tr + 50, W + 60))
        flare = flare.intersect(box(ax, 0, tr + 400, 1400, W + 30, 800))
        flare = flare.cut(box(ax, 0, 0, 1400, W - 120, 3000))
        parts.append(Part(f"arch_flare_{int(ax)}", flare, "cladding"))
    sill = box((fx + rx) / 2, 0, 390, fx - rx - 2 * (tr + 85), W + 16, 120)
    parts.append(Part("sill_cladding", sill, "cladding"))
    parts.append(Part("bumper_front", rbox(L / 2 - 60, 0, 470, 140, W - 260, 300, 60), "cladding"))
    parts.append(Part("bumper_rear", rbox(-L / 2 + 60, 0, 520, 140, W - 260, 300, 60), "cladding"))
    parts.append(Part("skid_plate", box(L / 2 - 20, 0, 360, 60, 900, 90), "satin_alu"))

    # front graphics: grille + full-width light blade; rear light blade
    parts.append(Part("grille", rbox(L / 2 + 2, 0, 840, 30, 1250, 300, 20), "gloss_black"))
    parts.append(Part("headlight_blade", box(L / 2 + 6, 0, 1060, 14, 1700, 22), "headlight"))
    for s in (-1, 1):
        parts.append(Part(f"headlamp_{s}", rbox(L / 2 + 4, s * 760, 1000, 20, 300, 80, 20), "headlamp_lens"))
    parts.append(Part("tail_blade", box(-L / 2 - 6, 0, 1080, 14, 1760, 30), "taillight"))

    # grille bars, shut lines, handles
    for k in range(11):
        parts.append(Part(f"grille_bar_{k}", box(L / 2 + 22, -550 + k * 110, 840, 14, 18, 270), "satin_alu"))
    for s in (-1, 1):
        y = s * (W / 2 + 0.6)
        for xl in (1180, -120, -1240):
            parts.append(Part(f"shut_{s}_{xl}", box(xl, y, 790, 5, 2, 760), "gloss_black"))
        for xh in (380, -830):
            parts.append(Part(f"handle_{s}_{xh}", rbox(xh, y + s * 4, 1070, 170, 10, 26, 5), "satin_alu"))
    parts.append(Part("tailgate_line", box(-L / 2 - 1, 0, 760, 2, 1500, 5), "gloss_black"))

    # greenhouse (dark glass) + body-colour pillars + roof
    parts.append(Part("glass", _greenhouse(), "glass_black"))
    big = _greenhouse(grow=6.0)
    for nm, xa, xb in (("pillar_B", 170, 300), ("pillar_C", -1060, -930), ("pillar_D", -2420, -2180)):
        pil = big.intersect(box((xa + xb) / 2, 0, 1510, xb - xa, 2400, 700))
        parts.append(Part(nm, pil, "gloss_black"))
    belt = big.intersect(box(-700, 0, 1195, 3800, 2400, 30))
    parts.append(Part("belt_trim", belt, "satin_alu"))
    roof = rbox(-960, 0, 1846, 3060, 1500, 22, 110)
    roof = safe_fillet(roof, ">Z", 9)
    parts.append(Part("roof_panel", roof, "gloss_black"))

    # factory raised roof rails
    xr0, xr1 = B8["rail_x"]
    for s in (-1, 1):
        y = s * B8["rail_y"]
        bar = rbox_all((xr0 + xr1) / 2, y, 1890, xr1 - xr0, 32, 30, 10)
        parts.append(Part(f"rail_{s}", bar, "satin_alu"))
        for xp in (xr0 + 60, (xr0 + xr1) / 2, xr1 - 60):
            parts.append(Part(f"rail_post_{s}_{int(xp)}", rbox(xp, y, 1866, 90, 34, 30, 8), "gloss_black"))

    # mirrors
    for s in (-1, 1):
        parts.append(Part(f"mirror_{s}", rbox_all(1080, s * (W / 2 + 50), 1290, 120, 140, 130, 30), "gloss_black"))

    # wheels
    for ax in (fx, rx):
        for s in (-1, 1):
            y = s * (B8["track"] / 2)
            tyre = cyl_y(ax, y, tr, tr, B8["tyre_w"])
            tyre = safe_fillet(tyre, "%CIRCLE", 60)
            tyre = tyre.cut(cyl_y(ax, y, tr, 255, B8["tyre_w"] + 10))
            parts.append(Part(f"tyre_{int(ax)}_{s}", tyre, "tyre"))
            rim = cyl_y(ax, y, tr, 256, B8["tyre_w"] - 40)
            face_y = y + s * (B8["tyre_w"] / 2 - 30)
            for k in range(6):
                a = k * math.pi / 3
                hole = cyl_y(ax + 165 * math.cos(a), face_y, tr + 165 * math.sin(a), 55, 80)
                rim = rim.cut(hole)
            parts.append(Part(f"rim_{int(ax)}_{s}", rim, "rim"))
            hub = cyl_y(ax, face_y, tr, 60, 70)
            parts.append(Part(f"hub_{int(ax)}_{s}", hub, "gloss_black"))
            brake = cyl_y(ax, y - s * 20, tr, 200, 30)
            parts.append(Part(f"rotor_{int(ax)}_{s}", brake, "rotor"))
    return parts
