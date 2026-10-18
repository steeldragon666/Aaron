#!/usr/bin/env python3
"""
render_office_adaptor.py - picture of the office plenum adaptor P9 (CP-SRA16-PRT-001) for docs/OFFICE_AIR.md:
the part as printed, a half-section through the taper, and the supply stack (grille, fan, adaptor) exploded.

Writes renders/office_adaptor.png.
Usage: python3 tools/render_office_adaptor.py
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import printparts as PP  # noqa: E402

cq = PP.cq
V = PP.V
LIGHT = np.array([-0.4, -0.6, 0.7]) / np.linalg.norm([-0.4, -0.6, 0.7])
PETG, FAN, CUT = np.array([0.36, 0.62, 0.86]), np.array([0.32, 0.30, 0.28]), np.array([0.93, 0.55, 0.26])


def tris(shape, tol=0.2):
    vs, fs = shape.tessellate(tol, 0.3)
    v = np.array([(p.x, p.y, p.z) for p in vs])
    return v[np.array(fs)]


def draw(ax, shape, col, offset=(0, 0, 0), cut_x=None):
    t = tris(shape) + np.array(offset)
    n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
    ln = np.linalg.norm(n, axis=1)
    keep = ln > 1e-9
    t, n = t[keep], n[keep] / ln[keep, None]
    shade = 0.5 + 0.5 * np.abs(n @ LIGHT)                    # two-sided: tessellation winding varies
    cols = np.clip(col[None, :] * shade[:, None], 0, 1)
    if cut_x is not None:                                   # faces on the section plane in the cut colour
        on = np.all(np.abs(t[:, :, 1] - cut_x) < 0.05, axis=1)
        cols[on] = np.clip(CUT[None, :] * (0.8 + 0.2 * shade[on, None]), 0, 1)
    ax.add_collection3d(Poly3DCollection(t, facecolors=cols, edgecolors=cols * 0.85, linewidths=0.1))
    return t.reshape(-1, 3)


def frame(ax, pts, elev, azim, title):
    lo, hi = pts.min(0), pts.max(0)
    c, r = (lo + hi) / 2, (hi - lo).max() / 2 * 1.02
    ax.set_xlim(c[0] - r, c[0] + r)
    ax.set_ylim(c[1] - r, c[1] + r)
    ax.set_zlim(c[2] - r, c[2] + r)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    ax.set_facecolor("#fcfcfb")
    ax.set_title(title, fontsize=11, color="#0b0b0b", pad=0)


def main():
    I = PP.interfaces()
    op = I["office"][0]
    ad, ai = PP.office_adaptor(I, op)
    gr, _ = PP.office_grille(I, op)
    y, z = op["y"], op["z"]
    # local frame: fan face at the origin, the duct axis along +Z (as printed)
    to_local = lambda s: s.translate(V(-op["body"][0], -y, -z)).rotate(V(0, 0, 0), V(0, 1, 0), -90)  # noqa: E731
    adl = to_local(ad)
    fb = op["fan_box"]
    fan = PP.box(fb[0], fb[1], fb[2], fb[3], fb[4], fb[5]).cut(
        PP.cyl((fb[0] - 1, y, z), (fb[3] + 1, y, z), I["P"]["office_fan"] / 2.0 - 2.0))
    fan = fan.fuse(PP.cyl((fb[0] + 3, y, z), (fb[3] - 2, y, z), 15.0))
    fanl, grl = to_local(fan), to_local(gr)

    fig = plt.figure(figsize=(15, 5.6), facecolor="#fcfcfb")
    ax = fig.add_subplot(1, 3, 1, projection="3d")
    pts = draw(ax, adl, PETG)
    frame(ax, pts, 24, -58, "P9 plenum adaptor, as printed")

    ax = fig.add_subplot(1, 3, 2, projection="3d")
    half = adl.cut(PP.box(-200, -200, -200, 200, 0, 200))
    pts = draw(ax, half, PETG, cut_x=0.0)
    frame(ax, pts, 8, -90, "Half-section: D%.0f fan bore to D%.1f duct bore, %.0f deg" % (
        2 * ai["rm"], 2 * ai["rb"], ai["half_angle"]))

    ax = fig.add_subplot(1, 3, 3, projection="3d")
    p1 = draw(ax, adl, PETG)
    p2 = draw(ax, fanl, FAN, offset=(0, 0, -45))
    p3 = draw(ax, grl, PETG, offset=(0, 0, -95))
    frame(ax, np.vstack([p1, p2, p3]), 18, -58, "Supply: grille P10, fan, adaptor")
    fig.text(0.5, 0.03, "Spigot (D%g, clamp bead) passes out through a D%g skin hole; 4 x M3 from outside into "
             "inserts in the outer face, fan + grille into inserts in the inner face." % (
                 I["P"]["office_duct_d"], I["D"]["office_hole_d"]), ha="center", fontsize=10, color="#52514e")
    plt.subplots_adjust(left=0.0, right=1.0, top=0.93, bottom=0.07, wspace=0.0)
    out = os.path.join(ROOT, "renders", "office_adaptor.png")
    fig.savefig(out, dpi=110, facecolor=fig.get_facecolor())
    print("wrote", out)


if __name__ == "__main__":
    main()
