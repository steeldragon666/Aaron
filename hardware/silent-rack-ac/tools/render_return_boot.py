#!/usr/bin/env python3
"""
render_return_boot.py - picture of the hot-return boot P13 (CP-SRA16-PRT-001) for docs/RACK_PLENUMS.md:
the assembled boot, and the four printed L-corners exploded.  Writes renders/return_boot.png.
Usage: python3 tools/render_return_boot.py
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

LIGHT = np.array([-0.4, -0.5, 0.75]) / np.linalg.norm([-0.4, -0.5, 0.75])
PETG = np.array([0.90, 0.46, 0.20])
CORN = [np.array(c) for c in [(0.26, 0.52, 0.86), (0.30, 0.66, 0.42), (0.86, 0.68, 0.26), (0.78, 0.33, 0.55)]]


def tris(shape, tol=0.4):
    vs, fs = shape.tessellate(tol, 0.3)
    v = np.array([(p.x, p.y, p.z) for p in vs])
    return v[np.array(fs)]


def draw(ax, shape, col, offset=(0, 0, 0)):
    t = tris(shape) + np.array(offset)
    n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
    ln = np.linalg.norm(n, axis=1)
    keep = ln > 1e-9
    t, n = t[keep], n[keep] / ln[keep, None]
    shade = 0.5 + 0.5 * np.abs(n @ LIGHT)
    cols = np.clip(col[None, :] * shade[:, None], 0, 1)
    ax.add_collection3d(Poly3DCollection(t, facecolors=cols, edgecolors=cols * 0.8, linewidths=0.08))
    return t.reshape(-1, 3)


def frame(ax, pts, elev, azim, title):
    lo, hi = pts.min(0), pts.max(0)
    c, r = (lo + hi) / 2, (hi - lo).max() / 2 * 1.02
    for setlim, k in ((ax.set_xlim, 0), (ax.set_ylim, 1), (ax.set_zlim, 2)):
        setlim(c[k] - r, c[k] + r)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    ax.set_facecolor("#fcfcfb")
    ax.set_title(title, fontsize=11, color="#0b0b0b", pad=0)


def main():
    pack = PP.build(None, "x1c")
    boot = pack["parts"]["P13"]["solid"]
    ri = pack["parts"]["P13"]["info"]
    corners = [p["solid"] for p in pack["pieces"] if p["part"] == "P13"]
    cx = (ri["grille"][0] + ri["grille"][1]) / 2.0
    cz = (ri["grille"][2] + ri["grille"][3]) / 2.0

    fig = plt.figure(figsize=(11, 5.6), facecolor="#fcfcfb")
    ax = fig.add_subplot(1, 2, 1, projection="3d")
    pts = draw(ax, boot, PETG)
    frame(ax, pts, 18, -60, "P13 hot-return boot (assembled)")

    ax = fig.add_subplot(1, 2, 2, projection="3d")
    allp = []
    for k, s in enumerate(corners):
        bb = s.BoundingBox()
        ox = 70.0 * (1 if (bb.xmin+bb.xmax)/2.0 > cx else -1)
        oz = 70.0 * (1 if (bb.zmin+bb.zmax)/2.0 > cz else -1)
        allp.append(draw(ax, s, CORN[k % 4], offset=(ox, 0, oz)))
    frame(ax, np.vstack(allp), 18, -60, "Four printed L-corners (glued at half-laps)")

    fig.text(0.5, 0.045, "Flange (gasket face) seats on the AC's rear return grille; the mouth projects %g mm into "
             "the hot bay. Grille %g x %g mm is a parametric default - check with gauge G4." % (
                 ri["L"], ri["grille"][1] - ri["grille"][0], ri["grille"][3] - ri["grille"][2]),
             ha="center", fontsize=10, color="#52514e")
    plt.subplots_adjust(left=0.0, right=1.0, top=0.93, bottom=0.08, wspace=0.0)
    out = os.path.join(ROOT, "renders", "return_boot.png")
    fig.savefig(out, dpi=110, facecolor=fig.get_facecolor())
    print("wrote", out)


if __name__ == "__main__":
    main()
