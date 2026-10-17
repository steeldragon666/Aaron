"""
Three roof-rack concepts for the Denza B8.

  A  AERO GT     low-profile touring platform, flush drone hangar, fin antennas
  B  EXPEDITION  raised alloy tray, faceted cowl, pod lighting, whip RF mast
  C  SENTINEL    fully enclosed carbon pod, flush hangar, RF radome, 360 LED halo

Each builder takes `open_` (hangar lids open) and `drone_state`
(None | "docked" | "hover") and returns a list of rack_lib.Part.
"""
from __future__ import annotations

import cadquery as cq

from rack_lib import (B8, HANGAR, Part, aero_crossbar, box, cyl_z, drone, drone_hangar,
                      led_bar, led_pod, planform, puck, rail_clamp_feet, rbox, rbox_all,
                      rf_enclosure, safe_fillet, shark_fin, side_profile, whip)

RAIL_Z = B8["rail_top_z"]


def _flush_lens(shell: cq.Workplane, region: cq.Workplane, recess=3.0):
    """Cut `region` out of `shell`, return (shell_cut, lens) with the lens
    following the original outer surface (inset by `recess`)."""
    lens = region.intersect(shell)
    return shell.cut(region), lens


def _drone_parts(hx, hy, hz_pad, state):
    if state == "docked":
        return drone(hx, hy, hz_pad + 40, name="drone")
    if state == "hover":
        return drone(hx - 150, hy + 260, hz_pad + 850, yaw_deg=-35, name="drone", spinning=True)
    return []


# --------------------------------------------------------------------------
# A — AERO GT
# --------------------------------------------------------------------------
def design_a(open_=False, drone_state=None) -> list[Part]:
    P: list[Part] = []
    z_feet_top = RAIL_Z + 55
    P += rail_clamp_feet([380, -800, -1980], 55, name="A_foot")

    x0, x1 = -2050.0, 250.0
    z_deck = z_feet_top
    # perimeter frame
    outer = rbox(0, 0, 0, x1 - x0, 1300, 40, 90).translate(((x0 + x1) / 2, 0, z_deck + 20))
    inner = rbox(0, 0, 0, x1 - x0 - 90, 1210, 60, 60).translate(((x0 + x1) / 2, 0, z_deck + 20))
    P.append(Part("A_frame", outer.cut(inner), "rack_black"))
    # transverse aero slats (skip hangar well + RF bay)
    hx = -1620.0
    for i, x in enumerate(range(150, -2000, -150)):
        if hx - HANGAR["L"] / 2 - 30 < x < hx + HANGAR["L"] / 2 + 30:
            continue
        if -900 < x < -480:
            continue
        P.append(aero_crossbar(x, z_deck + 22, 1210, f"A_slat_{i}", chord=70, thick=18))

    # side aero skirts with integrated scene-light strips
    for s in (1, -1):
        skirt = rbox_all((x0 + x1) / 2 - 20, s * 680, z_deck + 10, x1 - x0 + 40, 46, 80, 16)
        P.append(Part(f"A_skirt_{'L' if s > 0 else 'R'}", skirt, "rack_black"))
        P.append(Part(f"A_scene_{'L' if s > 0 else 'R'}",
                      rbox(-900, s * 704, z_deck - 8, 1700, 4, 16, 2), "led_white"))
        P.append(Part(f"A_amber_{'L' if s > 0 else 'R'}",
                      rbox(-900, s * 704, z_deck + 22, 1700, 4, 6, 2), "led_amber"))

    # aero front cowl with flush 1100 mm light blade
    prof = [(720, RAIL_Z + 25), (620, RAIL_Z + 70), (470, RAIL_Z + 115), (300, RAIL_Z + 135), (200, RAIL_Z + 138)]
    cowl = side_profile(prof, 1440)
    cowl = cowl.intersect(planform(195, 740, 1400, 1180, RAIL_Z, 300, 160))
    slot = box(640, 0, RAIL_Z + 58, 180, 1060, 30)
    cowl, lens = _flush_lens(cowl, slot)
    P.append(Part("A_cowl", cowl, "gloss_black"))
    P.append(Part("A_cowl_lightblade", lens, "led_white"))
    drl = box(560, 0, RAIL_Z + 96, 140, 1180, 6)
    cowl_full = side_profile(prof, 1440).intersect(planform(195, 740, 1400, 1180, RAIL_Z, 300, 160))
    P.append(Part("A_cowl_drl", drl.intersect(cowl_full), "led_amber"))

    # rear reverse/work light under frame tail
    P += led_bar(x0 - 22, 0, z_deck + 10, 800, height=40, depth=40, facing=-1, name="A_rear_bar")

    # drone hangar recessed into the deck
    hz = RAIL_Z + 10
    P += drone_hangar(hx, 0, hz, open_=open_, name="A_hangar")
    P += _drone_parts(hx, 0, hz + HANGAR["base_h"] - 36, drone_state)

    # RF payload
    P += rf_enclosure(-690, 0, RAIL_Z + 5, L=360, W=280, H=80, name="A_rf_bay")
    P.append(shark_fin(-1900, 640, z_deck + 50, length=260, height=175, width=50, name="A_fin_adsb"))
    P.append(shark_fin(-1900, -640, z_deck + 50, length=260, height=150, width=50, name="A_fin_lora"))
    P.append(puck(80, 0, z_deck + 40, r=55, h=20, name="A_gnss"))
    for k, (x, y) in enumerate([(100, 520), (100, -520), (-1100, 540), (-1100, -540)]):
        P.append(puck(x, y, z_deck + 40, r=38, h=26, name=f"A_wifi_{k}"))
    return P


# --------------------------------------------------------------------------
# B — EXPEDITION
# --------------------------------------------------------------------------
def design_b(open_=False, drone_state=None) -> list[Part]:
    P: list[Part] = []
    fh = 110
    P += rail_clamp_feet([400, -800, -2000], fh, name="B_foot")
    z_deck = RAIL_Z + fh
    x0, x1 = -2150.0, 300.0
    cx = (x0 + x1) / 2
    W = 1400.0

    outer = box(cx, 0, z_deck + 20, x1 - x0, W, 40)
    inner = box(cx, 0, z_deck + 20, x1 - x0 - 80, W - 80, 60)
    P.append(Part("B_tray_frame", safe_fillet(outer.cut(inner), "|Z", 18), "rack_black"))
    for i, x in enumerate(range(200, -2100, -165)):
        P.append(aero_crossbar(x, z_deck + 22, W - 80, f"B_slat_{i}", chord=60, thick=22))
    # gallery lip: posts + top rail on sides and rear
    rail_z = z_deck + 85
    for s in (1, -1):
        P.append(Part(f"B_gallery_{s}", rbox_all(cx - 100, s * (W / 2 - 20), rail_z, x1 - x0 - 400, 30, 22, 8), "rack_black"))
        for xp in range(int(x1 - 250), int(x0), -400):
            P.append(Part(f"B_post_{s}_{xp}", box(xp, s * (W / 2 - 20), z_deck + 62, 24, 24, 50), "rack_black"))
    P.append(Part("B_gallery_rear", rbox_all(x0 + 20, 0, rail_z, 30, W - 40, 22, 8), "rack_black"))

    # faceted aero cowl with recessed 40" bar + corner pods
    prof = [(760, RAIL_Z + 60), (520, z_deck + 120), (300, z_deck + 135), (300, RAIL_Z + 60)]
    cowl = side_profile(prof, W + 30, spline=False)
    cowl = cowl.intersect(planform(290, 770, W + 30, W - 160, RAIL_Z, 400, 60))
    slot = box(620, 0, z_deck + 25, 220, 1016, 55)
    full = cowl
    cowl, lens = _flush_lens(cowl, slot)
    P.append(Part("B_cowl", cowl, "satin_black"))
    P.append(Part("B_cowl_bar40", lens, "led_white"))
    bezel = box(620, 0, z_deck + 25, 230, 1040, 70).intersect(full).cut(slot)
    P.append(Part("B_cowl_bezel", bezel, "anodised_grey"))
    for s in (1, -1):
        P += led_pod(300, s * 620, z_deck + 190, facing=(1, 0), name=f"B_front_pod_{s}")
        # scene lights on tray sides
        for j, x in enumerate((-250, -1450)):
            P += led_pod(x, s * (W / 2 + 40), z_deck + 15, size=80, depth=60, facing=(0, s),
                         name=f"B_scene_{s}_{j}")
        P += led_pod(x0 - 40, s * 470, z_deck + 15, size=80, depth=60, facing=(-1, 0),
                     name=f"B_rear_pod_{s}")
    P += led_bar(x0 - 30, 0, z_deck + 15, 500, height=36, depth=36, facing=-1, name="B_rear_amber",
                 lens_mat="led_amber")

    # drone hangar on deck
    hx = -1720.0
    P += drone_hangar(hx, 0, z_deck + 40, open_=open_, name="B_hangar", lid_mat="hangar_shell")
    P += _drone_parts(hx, 0, z_deck + 40 + HANGAR["base_h"] - 36, drone_state)

    # RF: front-corner whips (ADS-B 1090 / LoRa 915) + survey bridge
    P += whip(200, W / 2 - 40, z_deck + 40, 560, name="B_adsb_1090")
    P += whip(200, -(W / 2 - 40), z_deck + 40, 820, base_r=18, tip_r=7, name="B_lora_915")
    bz = z_deck + 150
    P.append(Part("B_bridge", rbox_all(-1240, 0, bz, 60, W - 60, 30, 10), "anodised_grey"))
    for s in (1, -1):
        P.append(Part(f"B_bridge_leg_{s}", box(-1240, s * (W / 2 - 50), z_deck + 85, 40, 40, 110), "anodised_grey"))
    for k, y in enumerate((-450, -150, 150, 450)):
        P += whip(-1240, y, bz + 15, 200, base_r=9, tip_r=6, name=f"B_wifi_{k}", mat="antenna_black")
    P.append(puck(-1240, 0, bz + 15, r=48, h=20, name="B_gnss"))
    P += rf_enclosure(-560, 0, z_deck + 40, L=420, W=300, H=95, name="B_rf_bay")
    return P


# --------------------------------------------------------------------------
# C — SENTINEL
# --------------------------------------------------------------------------
def _sentinel_shell():
    zb = RAIL_Z + 20
    prof = [(730, zb + 10), (620, zb + 95), (420, zb + 190), (60, zb + 232), (-1000, zb + 240),
            (-1900, zb + 232), (-2240, zb + 190), (-2340, zb + 110)]
    side = side_profile(prof, 1440)
    plan = planform(-2345, 735, 1380, 1260, zb - 10, 500, 210)
    sect = (cq.Workplane("YZ").center(0, zb + 125).rect(1420, 250).extrude(1700, both=True).translate((-805, 0, 0)))
    sect = safe_fillet(sect, "|X and >Z", 110)
    sect = safe_fillet(sect, "|X and <Z", 20)
    return side.intersect(plan).intersect(sect), zb


def design_c(open_=False, drone_state=None, xray=False) -> list[Part]:
    P: list[Part] = []
    P += rail_clamp_feet([300, -900, -2000], 22, name="C_foot")
    shell, zb = _sentinel_shell()
    full = shell

    # front light blade + rear work blade (flush, follow shell surface)
    shell, front = _flush_lens(shell, box(680, 0, zb + 52, 160, 1000, 26))
    shell, rear = _flush_lens(shell, box(-2310, 0, zb + 120, 120, 800, 22))
    # 360 halo: thin band around the lower perimeter
    band = box(-800, 0, zb + 18, 3400, 1600, 10)
    core = planform(-2330, 720, 1350, 1230, zb - 20, 100, 200)
    shell, halo = _flush_lens(shell, band.cut(core))

    # flush hangar bay
    hx = -420.0
    bay = rbox(hx, 0, zb + 200, HANGAR["L"] + 24, HANGAR["W"] + 24, 400, 30)
    shell = shell.cut(bay)
    rx = -1700.0
    P.append(Part("C_pod_shell", shell, "carbon"))
    P.append(Part("C_front_blade", front, "led_white"))
    P.append(Part("C_rear_blade", rear, "led_white"))
    P.append(Part("C_halo", halo, "led_halo"))

    P += drone_hangar(hx, 0, zb + 2, open_=open_, name="C_hangar", lid_mat="carbon", base_mat="hangar_shell")
    P += _drone_parts(hx, 0, zb + 2 + HANGAR["base_h"] - 36, drone_state)

    # RF radome (prolate dome) on rear deck + internal array
    top = zb + 236
    dome = (cq.Workplane("XZ").moveTo(0, 0).lineTo(340, 0)
            .spline([(305, 100), (200, 175), (0, 210)], includeCurrent=True)
            .close().revolve(360, (0, 0, 0), (0, 1, 0)))
    dome = dome.translate((rx, 0, top - 30))
    P.append(Part("C_radome", dome, "radome_xray" if xray else "radome_white"))
    P.append(Part("C_radome_ring", cyl_z(rx, 0, top - 34, 352, 14), "anodised_grey"))
    # internal antennas (visible in x-ray render)
    gp = top - 20
    P.append(Part("C_ground_plane", cyl_z(rx, 0, gp, 300, 3), "copper"))
    P += whip(rx + 120, 0, gp, 120, base_r=6, tip_r=5, name="C_adsb_dipole", mat="antenna_white")
    P += whip(rx - 120, 0, gp, 70, base_r=5, tip_r=4, name="C_lora_monopole", mat="antenna_white")
    for k, (dx, dy) in enumerate([(0, 210), (0, -210), (210, 0), (-210, 0)]):
        panel = rbox(rx + dx, dy, gp + 70, 20 if dx else 110, 110 if dx else 20, 110, 6)
        if dx == 0:
            panel = rbox(rx + dx, dy, gp + 70, 110, 20, 110, 6)
        P.append(Part(f"C_wifi_sector_{k}", panel, "pcb"))
    P.append(puck(rx, 0, gp + 150, r=40, h=16, name="C_gnss", mat="antenna_black"))
    P += rf_enclosure(-1050, 0, zb + 5, L=360, W=300, H=90, name="C_rf_bay")
    return P


DESIGNS = {
    "A_AeroGT": design_a,
    "B_Expedition": design_b,
    "C_Sentinel": design_c,
}
