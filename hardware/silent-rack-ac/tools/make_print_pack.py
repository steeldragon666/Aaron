#!/usr/bin/env python3
"""
make_print_pack.py - export the 3D-printed parts (CP-SRA16-PRT-001) ready to slice.

Outputs (relative to hardware/silent-rack-ac/):
  cad/print/stl/<piece>_<name>.stl      one STL per piece, already in print orientation, sitting on z = 0
  cad/print/SRA16_print_<printer>.zip   the STLs + PRINT_README.txt (fixed timestamps, reproducible)
  cad/print/SRA16_printed_parts.step    every piece in its installed position (load with the rack STEP)
  cad/print/print_report.json           checks, plates, masses
  bom/printed_parts.csv                 piece list: material, print size, mass, time, plate, orientation
  renders/print_plates.png              every plate on the printer bed (fit at a glance)
  renders/print_exploded.png            the printed parts exploded and labelled
  docs/PRINTED_PARTS.md                 print settings, plates, assembly, checks

Usage:  python3 tools/make_print_pack.py [--printer x1c] [key=value ...]
The X1C pack is the one kept in the repo; another printer writes its own set to cad/print/<printer>/.
"""
import csv
import json
import math
import os
import re
import sys
import zipfile
from collections import OrderedDict

import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import cadquery as cq  # noqa: E402
import printparts as PP  # noqa: E402
import build_cadquery as BC  # noqa: E402

OUT = os.path.join(ROOT, "cad", "print")
DEFAULT_PRINTER = "x1c"                # its pack is the one in the repo; other printers go to cad/print/<printer>/
STL_TOL, STL_ANG = 0.03, 0.15          # mm chord, rad: smooth enough for a 0.4 nozzle
OVERHANG_MAX = 50.0                    # deg from vertical a face may lean before it needs support
OK_WIDTH = 6.0                         # an overhang strip this narrow prints anyway (short bridge / ledge)
GAP = 6.0                              # spacing between parts on a shared plate
PLATE_MAX_G = 700.0                    # a fresh 1 kg spool always finishes a plate (brim, purge, a restart)
PRINT_ORDER = ("G", "P2", "P1", "P3", "P4", "P5", "P6", "P7", "P8")   # plates are numbered in this order
LOOSE = ("G", "P8")                    # parts with no fixed installed position (gauges, clips)
OWN_PLATES = ("P6", "P7", "P8")        # electronics mounts: their own plates (print them when convenient)
DUCT = "Exhaust duct (insulated)"
FOAM_RING = 3.0                        # closed-cell foam ring on the elbow shoulder, compressed to half by the duct
ZIP_DATE = (2026, 1, 1, 0, 0, 0)

SETTINGS = OrderedDict([
    ("PETG", [("Filament", "Bambu PETG HF (or any PETG), dried"),
              ("Nozzle / layer", "0.4 mm / 0.20 mm (0.6 mm / 0.30 mm halves the hood time)"),
              ("Walls", "4 wall loops, 5 top + 5 bottom layers: the 4 mm walls print solid"),
              ("Infill", "15% gyroid (only the thick spots use it)"),
              ("Plate", "Textured PEI, no glue"),
              ("Brim", "5 mm on the hood ends and the collar; 8 mm on the two middle channels (tall, narrow)"),
              ("Supports", "none - every piece is oriented to print without them"),
              ("Cooling", "profile default; open the top glass on a hot day (PETG clogs in a warm chamber)")]),
    ("ASA", [("Filament", "Bambu ASA (or any ASA), dried"),
             ("Nozzle / layer", "0.4 mm / 0.20 mm"),
             ("Walls", "4 wall loops, 5 top + 5 bottom layers"),
             ("Infill", "15% gyroid"),
             ("Plate", "Textured PEI + glue stick"),
             ("Brim", "5 mm on everything except the gauges"),
             ("Supports", "none"),
             ("Chamber", "door and lid closed, chamber warm before starting (warps less)")]),
])


# ---------------------------------------------------------------- meshes
def mesh_of(shape, tol=STL_TOL, ang=STL_ANG):
    vs, ts = shape.tessellate(tol, ang)
    m = trimesh.Trimesh(np.array([(p.x, p.y, p.z) for p in vs]), np.array(ts), process=True)
    m.merge_vertices()
    if m.volume < 0:
        m.invert()
    return m


def overhangs(m):
    """Downward faces steeper than OVERHANG_MAX off the plate, grouped; width = 2 * area / boundary."""
    n = m.face_normals
    tri = m.triangles
    flag = (n[:, 2] < -math.sin(math.radians(OVERHANG_MAX))) & (tri[:, :, 2].max(axis=1) > 0.05)
    idx = np.nonzero(flag)[0]
    if not len(idx):
        return []
    adj = m.face_adjacency
    both = flag[adj[:, 0]] & flag[adj[:, 1]]
    comps = trimesh.graph.connected_components(adj[both], nodes=idx, min_len=1)
    es = m.edges_sorted.reshape(-1, 3, 2)
    out = []
    for c in comps:
        c = np.asarray(c)
        area = float(m.area_faces[c].sum())
        e = es[c].reshape(-1, 2)
        u, cnt = np.unique(e, axis=0, return_counts=True)
        b = u[cnt == 1]
        per = float(np.linalg.norm(m.vertices[b[:, 0]] - m.vertices[b[:, 1]], axis=1).sum())
        w = 2 * area / per if per else 0.0
        out.append({"area": round(area, 1), "width": round(w, 2), "z": round(float(tri[c][:, :, 2].min()), 1),
                    "ok": w <= OK_WIDTH})
    return sorted(out, key=lambda o: -o["area"])


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


# ---------------------------------------------------------------- plates
def pack_plates(pieces, printer):
    """Lay the pieces (qty expanded) out on plates, one material per plate.  A piece covering more than
    45% of the bed gets a plate of its own; the rest are shelf-packed onto the lightest plate that takes them
    (so the plates come out even), keeping every plate under PLATE_MAX_G.  A piece alone on a plate is centred.  Plates are numbered in print order (PRINT_ORDER).
    Coordinates are bed coordinates (0..bed), front-left origin."""
    pr = PP.PRINTERS[printer]
    m = PP.FIT["margin"]
    W, D, _ = PP.usable(printer)
    ex, ey = pr["exclude"]
    items = []
    for p in pieces:
        for k in range(p["qty"]):
            items.append({"piece": p, "k": k, "w": p["dims"][0], "d": p["dims"][1], "h": p["dims"][2]})
    plates = []
    for mat, own in [(m, o) for m in PP.MATERIALS for o in (False, True)]:
        its = sorted([i for i in items if i["piece"]["mat"] == mat and (i["piece"]["part"] in OWN_PLATES) == own],
                     key=lambda i: (-round(i["w"] * i["d"]), i["piece"]["id"], i["k"]))
        shared = []
        for it in its:
            if it["w"] * it["d"] > 0.45 * W * D:
                plates.append({"mat": mat, "items": [it]})
                continue
            g = it["piece"]["mass_g"]
            for pl in sorted(shared, key=lambda q: q["g"]):
                if pl["g"] + g <= PLATE_MAX_G and _shelf_place(pl, it, W, D, m, ex, ey):
                    break
            else:
                pl = {"mat": mat, "items": [], "shelves": [], "g": 0.0}
                assert _shelf_place(pl, it, W, D, m, ex, ey), "piece does not fit an empty plate"
                shared.append(pl)
                plates.append(pl)
            pl["g"] += g
    for pl in plates:
        if len(pl["items"]) == 1:
            pl["items"] = [_alone(pl["items"][0], printer)]
    plates.sort(key=lambda pl: min((PRINT_ORDER.index(it["piece"]["part"]), it["piece"]["id"]) for it in pl["items"]))
    for i, pl in enumerate(plates):
        pl["no"] = i + 1
        pl.pop("shelves", None)
        pl.pop("g", None)
        pl["height"] = max(it["h"] for it in pl["items"])
        pl["hours"] = sum(it["piece"]["hours"] for it in pl["items"])
        pl["mass_g"] = sum(it["piece"]["mass_g"] for it in pl["items"])
        for it in pl["items"]:
            it["piece"].setdefault("plates", []).append(pl["no"])
    return plates


def _shelf_place(pl, it, W, D, m, ex, ey):
    for rot in (0, 1):
        w, d = (it["w"], it["d"]) if not rot else (it["d"], it["w"])
        for sh in pl["shelves"]:
            x0 = sh["x"] + (GAP if sh["x"] > 0 else 0.0)
            if x0 + w <= W + 1e-6 and d <= sh["h"] + 1e-6:
                _put(pl, it, sh, x0, w, d, m, rot)
                return True
        y0 = sum(s["h"] for s in pl["shelves"]) + GAP * len(pl["shelves"])
        if y0 + d <= D + 1e-6:
            sh = {"y": y0, "h": d, "x": (ex + GAP - m) if (ex and y0 < ey) else 0.0}
            if sh["x"] + w <= W + 1e-6:
                pl["shelves"].append(sh)
                _put(pl, it, sh, sh["x"], w, d, m, rot)
                return True
    return False


def _put(pl, it, sh, x0, w, d, m, rot):
    pl["items"].append(dict(it, x=m + x0, y=m + sh["y"], rot=rot, w=w, d=d))
    sh["x"] = x0 + w


def _alone(it, printer):
    """A piece alone on a plate: centred, then moved clear of the no-print corner (to the right, to the
    back, or into the back-right corner where printparts.fits proved that its outline clears it)."""
    pr = PP.PRINTERS[printer]
    BW, BD = pr["bed"]
    m = PP.FIT["margin"]
    ex, ey = pr["exclude"]
    p = it["piece"]
    w, d = p["dims"][0], p["dims"][1]
    x, y = (BW - w) / 2.0, (BD - d) / 2.0
    if ex and x < ex + m and y < ey + m:
        if ex + m + w <= BW - m:
            x = ex + m
        elif ey + m + d <= BD - m:
            y = ey + m
        else:
            for rot in (0, 1):
                cx, cy, ok = PP.corner_place(printer, p["dims"], p["hull"], rot)
                if ok:
                    return dict(it, x=cx, y=cy, rot=rot, w=(w, d)[rot], d=(d, w)[rot])
    return dict(it, x=x, y=y, rot=0, w=w, d=d)


# ---------------------------------------------------------------- clash check against the rack model
def clash_check(pack):
    I = pack["I"]
    replaced = {n for pi in PP.PART_INFO.values() for n in pi["replaces"]}
    model = {}
    for name, p in I["M"].items():
        if name in replaced:
            continue
        model[name] = BC.make_part(p)
    # The model's straight duct starts where its bend ends.  The printed elbow carries on with a 45 deg
    # shoulder down to its male spigot, and the duct is cut on site to butt against that shoulder.
    ei = pack["parts"]["P4"]["info"]
    trim = ei["ro"] - ei["ro2"]
    du = I["duct"]
    model[DUCT] = model[DUCT].cut(PP.slab(du["p0"], (du["p1"] - du["p0"]).normalized(), -1.0, trim))
    bbs = {n: s.BoundingBox() for n, s in model.items()}
    C = pack["C"]
    hb = I["hood_box"]
    hinfo = pack["parts"]["P1"]["info"]
    z_arm = pack["parts"]["P3"]["z_arm"]
    fixed = [p for p in pack["pieces"] if p["part"] in ("P1", "P4", "P5", "P6", "P7")]
    configs = OrderedDict()
    k_stow = pack["parts"]["P3"]["solids"]
    k_hold = [PP.keeper(x, y, hb[2], z_arm, 0.0) for x, y in hinfo["keepers"]]
    configs["running (collar on the AC)"] = ([("P2", PP.collar(C, 0.0)[0])] + [("P3", k) for k in k_stow], set())
    configs["service (collar on the keepers)"] = ([("P2", PP.collar(C, PP.PR["lift"])[0])] +
                                                  [("P3", k) for k in k_hold], {"Hood gasket"})
    ac = {n for n in model if n.startswith("AC ")}
    configs["AC out (collar hanging)"] = ([("P2", PP.collar(C, -PP.PR["drop"])[0])] + [("P3", k) for k in k_stow],
                                          {"Hood gasket"} | ac)
    res = OrderedDict()
    for cname, (moving, skip) in configs.items():
        sols = [(p["id"], p["solid"]) for p in fixed] + moving
        clashes = []
        for pid, s in sols:
            sb = s.BoundingBox()
            for n, ms in model.items():
                if n in skip or not BC.bbox_overlap(sb, bbs[n]):
                    continue
                v = s.intersect(ms).Volume()
                if v > 0.5:
                    clashes.append((pid, n, round(v, 1)))
        for i in range(len(sols)):                    # printed parts against each other
            for j in range(i + 1, len(sols)):
                a, b = sols[i], sols[j]
                if BC.bbox_overlap(a[1].BoundingBox(), b[1].BoundingBox()):
                    v = a[1].intersect(b[1]).Volume()
                    if v > 0.5:
                        clashes.append((a[0], b[0], round(v, 1)))
        res[cname] = clashes
    run = (du["p1"] - du["p0"]).Length
    return res, len(model), {"trim": trim, "ring": FOAM_RING, "length": run - trim - FOAM_RING / 2.0,
                             "model_length": run}


# ---------------------------------------------------------------- figures
def plates_figure(plates, meshes, printer, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    from matplotlib.patches import Rectangle
    pr = PP.PRINTERS[printer]
    BW, BD = pr["bed"]
    m = PP.FIT["margin"]
    ex, ey = pr["exclude"]
    n = len(plates)
    cols = 4
    rows = int(math.ceil(n / float(cols)))
    fig, axs = plt.subplots(rows, cols, figsize=(4.0 * cols, 4.5 * rows))
    axs = np.atleast_1d(axs).ravel()
    for ax in axs[n:]:
        ax.axis("off")
    for ax, pl in zip(axs, plates):
        ax.add_patch(Rectangle((0, 0), BW, BD, fc="#f4f4f2", ec="#555", lw=1.2))
        ax.add_patch(Rectangle((m, m), BW - 2 * m, BD - 2 * m, fc="none", ec="#999", lw=0.6, ls="--"))
        if ex:
            ax.add_patch(Rectangle((0, 0), ex, ey, fc="none", ec="#c33", hatch="////", lw=0.6))
        col = PP.MATERIALS[pl["mat"]]["colour"]
        for it in pl["items"]:
            mesh = meshes[it["piece"]["id"]]
            v = mesh.vertices[:, :2].copy()
            if it["rot"]:                                   # quarter turn, as printparts.corner_place
                v = np.column_stack([-v[:, 1], v[:, 0]])
            v -= v.min(axis=0)
            v += np.array([it["x"], it["y"]])
            tris = v[mesh.faces]
            ax.add_collection(PolyCollection(tris, facecolors=[col], edgecolors="none", alpha=0.9))
            ax.text(it["x"] + it["w"] / 2, it["y"] + it["d"] / 2, "%s\nh %.0f" % (it["piece"]["id"], it["h"]),
                    ha="center", va="center", fontsize=8, color="#111",
                    bbox=dict(fc="white", ec="none", alpha=0.7, pad=1.0))
        ax.set_xlim(-6, BW + 6)
        ax.set_ylim(-6, BD + 6)
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title("Plate %d - %s - %.0f g, ~%.0f h" % (pl["no"], pl["mat"], pl["mass_g"], pl["hours"]), fontsize=9)
    fig.suptitle("%s - pieces on the %s bed (%g x %g, dashed = %g mm brim margin, hatched = no-print corner)" % (
        PP.DOC_NO, pr["name"], BW, BD, m), fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.96), h_pad=2.0)
    fig.savefig(path, dpi=110)
    plt.close(fig)


def exploded_figure(pack, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    groups = [("Cold-air hood: body sections, drop collar, keepers", ("P1", "P2", "P3"), (-60.0, 28.0), 1.15),
              ("Exhaust: elbow halves, wall spigot", ("P4", "P5"), (-35.0, 22.0), 1.15),
              ("Electronics: touchscreen pod, node box", ("P6", "P7"), (-62.0, 18.0), 0.9)]
    fig = plt.figure(figsize=(20, 7.6))
    light = np.array([-0.4, -0.6, 0.7])
    light /= np.linalg.norm(light)
    for gi, (title, pids, (az, el), zoom) in enumerate(groups):
        a, e = math.radians(az), math.radians(el)
        eye = np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)])
        ax = fig.add_subplot(1, len(groups), gi + 1, projection="3d")
        ax.computed_zorder = False
        tris, fcs, labels = [], [], []
        for p in pack["pieces"]:
            if p["part"] not in pids:
                continue
            sols = [p["solid"]] if p["part"] != "P3" else pack["parts"]["P3"]["solids"]
            off = _explode(p, pack)
            if p["part"] in ("P6", "P7"):                   # the two are far apart in the rack: show side by side
                off = off + _bring(p, pack)
            col = np.array(PP.MATERIALS[p["mat"]]["colour"])
            for s in sols:
                m = mesh_of(s, 0.3, 0.3)
                # small faces, back faces dropped: matplotlib sorts whole faces, so this keeps them in order
                vs, fs = trimesh.remesh.subdivide_to_size(m.vertices, m.faces, max_edge=20.0)
                m = trimesh.Trimesh(vs, fs, process=False)
                front = m.face_normals @ eye > 1e-3
                v = m.vertices + off
                tris.append(v[m.faces[front]])
                sh = 0.45 + 0.55 * np.clip(m.face_normals[front] @ light, 0, 1)
                fcs.append(np.clip(col[None, :] * sh[:, None], 0, 1))
                labels.append((p["id"], v, p["part"] in ("P2", "P3")))
        # one collection, so faces of different pieces are depth-sorted against each other
        fc = np.vstack(fcs)
        ax.add_collection3d(Poly3DCollection(np.vstack(tris), facecolors=fc, edgecolors=fc, linewidths=0.4))
        pts = np.vstack([v for _, v, _ in labels])
        lo, hi = pts.min(axis=0), pts.max(axis=0)
        lo[2] -= 30.0
        hi[2] += 30.0
        for pid, v, below in labels:
            c = (v.min(axis=0) + v.max(axis=0)) / 2
            z = v[:, 2].min() - 18 if below else v[:, 2].max() + 14
            ax.text(c[0], c[1], z, pid, fontsize=9, ha="center", va="center", zorder=10,
                    bbox=dict(fc="white", ec="#777", alpha=0.85, pad=1.5))
        ax.set_xlim(lo[0], hi[0])
        ax.set_ylim(lo[1], hi[1])
        ax.set_zlim(lo[2], hi[2])
        ax.set_box_aspect(tuple(hi - lo), zoom=zoom)
        ax.view_init(elev=el, azim=az)
        ax.set_axis_off()
        ax.set_title(title, fontsize=11)
    fig.suptitle("%s - printed parts, exploded (installed orientation; X right, Y to the rear, Z up)" % PP.DOC_NO,
                 fontsize=12)
    fig.subplots_adjust(left=0.0, right=1.0, bottom=0.0, top=0.92, wspace=0.0)
    fig.savefig(path, dpi=110)
    plt.close(fig)


def _bring(p, pack):
    """The pod (on the door) and the node box (in the plenum) are 300 mm apart: bring the box next to
    the pod for the picture."""
    if p["part"] != "P7":
        return np.zeros(3)
    pod = pack["parts"]["P6"]["solids"][0].BoundingBox()
    nb = pack["parts"]["P7"]["solids"][0].BoundingBox()
    return np.array([pod.xmax + 60.0 - nb.xmin, pod.ymin - nb.ymin, pod.zmin - nb.zmin])


def _explode(p, pack):
    """Offset for the exploded view, by piece."""
    cuts = pack["parts"]["P1"]["cuts"]
    if p["part"] == "P1":
        bb = p["solid"].BoundingBox()
        k = sum(1 for c in cuts if (bb.xmin + bb.xmax) / 2 > c)
        dy = -45.0 if p["id"].endswith("a") else (45.0 if p["id"].endswith("b") else 0.0)
        return np.array([60.0 * k, dy, 0.0])
    if p["part"] == "P2":
        cc = pack["parts"]["P2"]["cuts"]
        bb = p["solid"].BoundingBox()
        k = sum(1 for c in cc if (bb.xmin + bb.xmax) / 2 > c)
        dy = -25.0 if p["id"].endswith("a") else (25.0 if p["id"].endswith("b") else 0.0)
        return np.array([80.0 * k - 40.0 * len(cc) + 60.0, dy, -110.0])
    if p["part"] == "P3":
        return np.array([60.0, -60.0, -170.0])
    if p["part"] == "P4":
        return np.array([0.0, 0.0, 0.0]) if p["id"].endswith("-1") else np.array([0.0, 60.0, 60.0])
    if p["part"] == "P6":                       # bezel forward of the shell
        return np.array([0.0, -40.0, 0.0]) if p["id"].endswith("-2") else np.zeros(3)
    if p["part"] == "P7":                       # lid off to the side
        return np.array([45.0, 0.0, 0.0]) if p["id"].endswith("-2") else np.zeros(3)
    if p["part"] == "P5":                       # pulled in from the rear wall to sit just past the elbow
        ei, wi = pack["parts"]["P4"]["info"], pack["parts"]["P5"]["info"]
        dy = ei["outlet_end"].y + 60.0 + 90.0 - wi["y_in0"]
        return np.array([0.0, dy + (0.0 if p["id"].endswith("-1") else 60.0), 60.0])
    return np.zeros(3)


# ---------------------------------------------------------------- outputs
def write_step(pack, path):
    assy = cq.Assembly(name="%s printed parts" % PP.DOC_NO)
    for p in pack["pieces"]:
        r, g, b = PP.MATERIALS[p["mat"]]["colour"]
        sols = [p["solid"]] if p["part"] != "P3" else pack["parts"]["P3"]["solids"]
        for j, s in enumerate(sols):
            if p["part"] in LOOSE:
                continue                                    # no installed position
            nm = "%s %s" % (p["id"], p["name"]) + (" (%d)" % (j + 1) if len(sols) > 1 else "")
            assy.add(s, name=nm, color=cq.Color(r, g, b, 1.0))
    assy.export(path, exportType="STEP")
    txt = open(path).read()
    txt = re.sub(r"(FILE_NAME\('[^']*',')[0-9T:\-\.]+(')", r"\g<1>2026-01-01T00:00:00\g<2>", txt, count=1)
    open(path, "w").write(txt)


def readme_txt(pack, plates):
    pr = PP.PRINTERS[pack["printer"]]
    L = ["%s rev %s - SRA-16 printed parts, STL set for the %s" % (PP.DOC_NO, PP.REV, pr["name"]), "",
         "Every STL is already oriented for printing (flat face on the plate, no supports needed) and sits",
         "on z = 0. Units: mm. Import, keep the orientation, add the brim below, slice. Full notes:",
         "hardware/silent-rack-ac/docs/PRINTED_PARTS.md", "",
         "PRINT G1 AND G2 FIRST. G1 must slide over the AC exhaust spigot with light friction; the 150 mm",
         "duct must slide over G2. If not, fix the fit before printing the elbow and spigot.",
         "Plates are numbered in print order.", ""]
    for mat, rows in SETTINGS.items():
        L.append("%s - %s" % (mat, PP.MATERIALS[mat]["use"]))
        for k, v in rows:
            L.append("  %-15s %s" % (k, v))
        L.append("")
    L.append("Plates:")
    for pl in plates:
        L.append("  %2d  %-4s  %s  (~%.0f g, ~%.0f h)" % (
            pl["no"], pl["mat"], ", ".join(it["piece"]["id"] for it in pl["items"]), pl["mass_g"], pl["hours"]))
    L.append("")
    L.append("Pieces:")
    for p in pack["pieces"]:
        L.append("  %-6s x%d  %-4s  %-46s %5.0f x %5.0f x %5.0f mm   %s" % (
            p["id"], p["qty"], p["mat"], p["name"], p["dims"][0], p["dims"][1], p["dims"][2],
            p["note"] if p["fit"] else "DOES NOT FIT: " + p["why"]))
    return "\n".join(L) + "\n"


def doc_md(pack, plates, report):
    pr = PP.PRINTERS[pack["printer"]]
    W, D, H = PP.usable(pack["printer"])
    pcs = pack["pieces"]
    tot = OrderedDict()
    for p in pcs:
        t = tot.setdefault(p["mat"], {"g": 0.0, "h": 0.0, "n": 0})
        t["g"] += p["mass_g"] * p["qty"]
        t["h"] += p["hours"] * p["qty"]
        t["n"] += p["qty"]
    md = ["# SRA-16 - 3D-printed parts (%s rev %s)" % (PP.DOC_NO, PP.REV), "",
          "Generated by `tools/make_print_pack.py` from `rack_layout.py` v%s for the **%s**: %g x %g x %g mm build "
          "volume, used as %g x %g x %g so there is room for a brim and some headroom." % (
              PP.RL.VERSION, pr["name"], pr["bed"][0], pr["bed"][1], pr["z"], W, D, H), "",
          "Every piece is split to fit, oriented to print **without supports**, and exported as an STL that already "
          "sits on the plate. The parts are built from the same model as the rest of the rack, so they follow any "
          "parameter change (re-run the tool after the tape checks).", "",
          "| File | Use |", "|---|---|",
          "| `cad/print/stl/*.stl` | one STL per piece, print orientation |",
          "| `cad/print/SRA16_print_%s.zip` | the STLs + `PRINT_README.txt` (settings and plates) |" % pack["printer"],
          "| `cad/print/SRA16_printed_parts.step` | every piece in its installed position; open with `SilentRackAC.step` |",
          "| `bom/printed_parts.csv` | piece list with size, mass, time and plate |",
          "| `cad/print/print_report.json` | all checks below |", "",
          "![Plates](../renders/print_plates.png)", "",
          "![Exploded](../renders/print_exploded.png)", "",
          "## What is printed", "",
          "| Part | Material | Pieces | Replaces | Why print it |", "|---|---|---|---|---|"]
    why = {"P1": "The design already allowed a printed hood. Split into end sections and two middle channels.",
           "P2": "The model shows the drop collar fused to the hood; printed, it is a separate part that slides in the "
                 "hood floor and rests on the AC top under its own weight.",
           "P3": "Turn buttons under the hood floor: lift the collar onto them to roll the AC in or out.",
           "P4": "The socket that fits over the AC spigot and the male outlet are custom; a stock elbow needs adapters.",
           "P5": "The flange is drilled to the laser-cut rear-skin pattern; the outer tube carries a hose bead.",
           "G": "Ten-minute prints that prove the two critical fits before the long prints.",
           "P6": "Holds the 4.3 inch touchscreen on the upper door; bolts to two rivnuts and covers the cable grommet "
                 "(see `docs/ELECTRONICS.md`).",
           "P7": "Holds the rack node's carrier board inside the front plenum, on magnets.",
           "P8": "Hold the temperature probes (and the humidity sensor's lead) in the air stream, on magnets."}
    for pid, pi in PP.PART_INFO.items():
        ps = [p for p in pcs if p["part"] == pid]
        md.append("| %s %s | %s | %s | %s | %s |" % (
            pid, pi["name"], pi["mat"], ", ".join("%s%s" % (p["id"], " x%d" % p["qty"] if p["qty"] > 1 else "")
                                                for p in ps),
            ", ".join(pi["replaces"]) or "-", why[pid]))
    md += ["", "The cold side is PETG: it carries 12-18 degC air and copes with condensation. The hot side is ASA: "
           "the exhaust runs at up to about 60 degC, which is too close to PETG's softening point. "
           "Totals: " + "; ".join("%s %d pieces, about %.2f kg and %.0f h" % (m, t["n"], t["g"] / 1000, t["h"])
                                for m, t in tot.items()) + " (solid-wall estimate, 0.4 mm nozzle).", "",
           "## Pieces", "",
           "| Piece | Qty | Material | Print size X x Y x Z mm | Mass g | Time h | Plate | On the plate |",
           "|---|---:|---|---|---:|---:|---|---|"]
    for p in pcs:
        md.append("| %s %s | %d | %s | %.0f x %.0f x %.0f | %.0f | %.1f | %s | %s |" % (
            p["id"], p["name"], p["qty"], p["mat"], *p["dims"], p["mass_g"], p["hours"],
            ", ".join(str(n) for n in sorted(set(p.get("plates", [])))), p["note"]))
    md += ["", "## Bambu Studio settings", ""]
    for mat, rows in SETTINGS.items():
        md += ["**%s** - %s" % (mat, PP.MATERIALS[mat]["use"]), "", "| Setting | Value |", "|---|---|"]
        md += ["| %s | %s |" % r for r in rows]
        md.append("")
    md += ["Import the STLs as they are: they are already the right way up. Keep the filament's shrinkage "
           "compensation at its default and use the gauges (below) to confirm the fits.", "",
           "## Plates", "", "| Plate | Material | Pieces | Tallest mm | Mass g | Time h |", "|---:|---|---|---:|---:|---:|"]
    for pl in plates:
        md.append("| %d | %s | %s | %.0f | %.0f | %.1f |" % (
            pl["no"], pl["mat"], ", ".join(it["piece"]["id"] for it in pl["items"]), pl["height"], pl["mass_g"],
            pl["hours"]))
    C = pack["C"]
    hi = pack["parts"]["P1"]["info"]
    def pls(*parts):
        ns = sorted({pl["no"] for pl in plates for it in pl["items"] if it["piece"]["part"] in parts})
        return "plate%s %s" % ("s" if len(ns) > 1 else "", ", ".join(str(n) for n in ns))
    md += ["", "## Print order", "",
           "Plates are numbered in print order. Before printing anything, do the tape check (`DESIGN.md` section 3) "
           "and re-run this tool: **M1** (spigot OD) changes the elbow, the wall spigot and the gauges, and **M6** "
           "(louvre opening) changes the hood body and the collar. M2-M5 and hold point H1 only move the parts, "
           "so they do not change any STL.", "",
           "1. **Gauges first (%s).** G1 must slide over the AC exhaust spigot (M1, D%.0f) with light friction. "
           "The 150 mm duct must slide over G2. If either is off, change `fit_socket` or `fit_spigot` in "
           "`tools/printparts.py` and re-run, or set the slicer's XY compensation, before the long prints." % (
               pls("G"), 2 * pack["I"]["ac_spigot"]["r"]),
           "2. **Collar (%s).** Glue the halves; check the outline against the AC louvres." % pls("P2"),
           "3. **Hood and keepers (%s).** Dry-fit the sections and check that the collar slides in the floor "
           "opening before gluing." % pls("P1", "P3"),
           "4. **Elbow and wall spigot (%s)** in ASA." % pls("P4", "P5"),
           "5. **Electronics mounts (%s):** the touchscreen pod, the node box and the clips, any time before the "
           "electronics go in." % pls("P6", "P7", "P8"), "",
           "## Assembly", "",
           "**Hood body (P1).** Dry-fit first. The tongue on each section (inner half of the wall, %.0f mm long) slides "
           "into the rebate on the next one with %.1f mm clearance per face. Glue with two-part epoxy or a "
           "PETG-rated CA; the outside stays flush. Order: left end P1-1, then the two middle channels P1-2a and "
           "P1-2b on its tongues, then the right end P1-3 over both. Stick 3 x 10 mm closed-cell foam tape round "
           "the top face, offer the hood up under the shelf so the top opening lines up with the shelf opening, and "
           "screw it up into the ply with 6 x 4 mm x 20 pan-head screws through the holes in the top. Drive them "
           "from below with the AC out: the rear row through the floor opening, the front row through the %d mm "
           "driver holes in the floor; then tape over the driver holes. The round port in the left end (P1-1) "
           "takes a %.0f mm membrane grommet: the electronics cables pass through it from the front plenum into "
           "the bay (`docs/ELECTRONICS.md`)." % (
               PP.PR["lap_l"], PP.PR["lap_cl"], PP.PR["driver_d"], PP.EL["hood_port"][2]),
           "",
           "**Drop collar (P2).** Glue the two halves the same way. Bond the 10 x 10 EPDM gasket under the foot and "
           "run 3 x 10 mm closed-cell foam tape round the outside of the wall as a wiper. Drop it into the hood floor "
           "opening from below. It hangs on its lip (front and sides) when the AC is out and rests on the AC top "
           "under its own weight when the AC is in; the hood's rear bump gives it room to rise.",
           "",
           "**Keepers (P3).** M4 x 25 up through each keeper and the hood floor, nyloc nut inside, snug enough that "
           "the keeper stays where it is turned. To roll the AC out: lift the collar %.0f mm, turn both keepers "
           "under its front wall, roll the AC out (the elbow comes with it). To refit: roll the AC in, turn the "
           "keepers out, the collar drops onto the AC." % PP.PR["lift"],
           "",
           "**Exhaust elbow (P4).** Slide the two halves together along the bend; the tongue on P4-1 goes into the "
           "rebate on P4-2. Solvent-weld with acetone (brush both faces, hold 1 minute) or ASA/ABS cement, then "
           "wrap the joint in aluminium tape. Wrap the elbow in 6 mm closed-cell insulation (the model allows "
           "%.0f mm over the wall) and stick a %.0f mm closed-cell foam ring on the 45 degree shoulder." % (
               pack["I"]["elbow"]["r_env"] - pack["parts"]["P4"]["info"]["ro"], FOAM_RING),
           "",
           "The elbow travels with the AC, because nobody can reach the duct joint once the AC is home. With the AC "
           "out, push the socket down over the AC spigot to the conical seat and tape it. Cut the internal 150 duct "
           "to **%.0f mm** (the model's %.0f mm run, less the %.1f mm shoulder, less half the foam ring), slide it "
           "onto the wall spigot's inner tube, and hang its front end from the shelf ply with a strap so that it "
           "lines up with the elbow outlet. As the AC is pushed home, the outlet slides %.0f mm into the duct (the "
           "%.0f mm chamfers lead it in) and the shoulder seals on the duct end." % (
               pack["duct"]["length"], pack["duct"]["model_length"], pack["duct"]["trim"], PP.PR["spigot_l"],
               PP.PR["lead_in"]),
           "",
           "**Touchscreen pod (P6).** Fit the two M4 rivnuts in the upper door and the rubber grommet in the cable "
           "hole, cut the door foam back round the grommet, then screw the shell to the rivnuts (heads inside). Feed "
           "the cable through, wire the panel (`docs/ELECTRONICS.md`), stick the foam pads on the four posts, sit "
           "the panel in the bezel and screw the bezel on with 4 x M3 x 12. The room sensor sits in the vented "
           "compartment at the bottom right. Print it in black PETG if you have it.",
           "",
           "**Node box and clips (P7, P8).** Glue the magnets in with epoxy, flush, all the same way up. The node "
           "box sticks to the front face of the left front rail spacer just above the shelf; the clips stick to "
           "the rail spacers and hold each probe about 16 mm off the steel, in the moving air (positions: sheet 4 "
           "of `drawings/CP-SRA16-ELC-001.pdf`).",
           "",
           "**Wall spigot (P5).** Glue the outer tube P5-2 into the flange groove of P5-1 (its tongue). Put a 3 mm "
           "foam ring or a bead of silicone on the flange face, push the inner tube through the rear skin from "
           "outside, and bolt it with 4 x M5 x 25 through the skin holes (nyloc nuts inside; trim the foam lining "
           "round each nut). The internal duct slides over the inner tube; the external flex hose clamps behind "
           "the bead.", "",
           "## Hardware for the printed parts", "", "| Part | Item |", "|---|---|"]
    for pid, pi in PP.PART_INFO.items():
        for h in pi["hardware"]:
            md.append("| %s | %s |" % (pid, h))
    md += ["", "## Checks", "", "| Check | Result |", "|---|---|"]
    for name, ok, det in report["checks"]:
        md.append("| %s | %s%s |" % (name, "OK" if ok else "**FAIL**", (" - " + det) if det else ""))
    md += ["", "## Design notes", "",
           "- **Walls** %.0f mm (the model's hood is 6 mm PP). Laps are half the wall, %.0f mm long; clearance %.1f mm "
           "per face leaves room for glue." % (PP.PR["wall"], PP.PR["lap_l"], PP.PR["lap_cl"]),
           "- **Sections.** The hood body is a profile run along X, so it prints standing on end and every wall is "
           "vertical. Between the end walls the top and floor openings split it into a front and a rear channel, so "
           "the middle section is two prints.",
           "- **Collar.** Outer %.0f x %.0f mm, the same outline as the model's hood gasket; the foot opening "
           "(%.0f x %.0f) clears the AC outlet by the full hood margin. Running clearance %.0f mm per side, taken "
           "up by the foam wiper. It drops %.0f mm when the AC is out and lifts %.0f mm onto the keepers." % (
               C["x1"] - C["x0"], C["y1"] - C["y0"], C["ix1"] - C["ix0"], C["iy1"] - C["iy0"], PP.PR["slide"],
               PP.PR["drop"], PP.PR["lift"]),
           "- **Hood rear bump.** The hood's rear wall steps out %.0f mm below z %.0f so the collar can rise past "
           "it; above that the wall stays in front of the shelf's foam lining." % (
               hi["bump_y"] - pack["I"]["hood_box"][4], hi["z_step"]),
           "- **Elbow.** Split at 45 degrees so each half stands on a straight end and leans at most 45 degrees. "
           "The AC spigot stops on a conical seat at the top of the socket.",
           "- **Overhangs.** The check flags every face that leans more than %g degrees from vertical. The only ones "
           "are narrow strips (lap steps, small horizontal holes, the flange groove), at most %.1f mm wide, which "
           "print as short bridges." % (OVERHANG_MAX, max(p["overhang"]["widest_ok_mm"] for p in pcs)),
           "- **Other printers.** `--printer p1s` or `--printer a1` gives the same pieces (same 256 mm bed). The "
           "A1 mini (180 mm) is too small for the hood profile, the elbow halves and the flange; "
           "`--printer a1mini` lists what does not fit. Printers known: %s." % ", ".join(
               "%s (%s)" % (k, v["name"]) for k, v in PP.PRINTERS.items()),
           ""]
    return "\n".join(md)


def main(argv):
    printer, overrides = "x1c", {}
    it = iter(argv)
    for a in it:
        if a == "--printer":
            printer = next(it)
        elif "=" in a:
            k, v = a.split("=", 1)
            overrides[k] = float(v)
    pack = PP.build(overrides or None, printer)
    print(PP.summary(pack))
    main_pack = printer == DEFAULT_PRINTER
    out = OUT if main_pack else os.path.join(OUT, printer)
    rend = os.path.join(ROOT, "renders") if main_pack else out
    os.makedirs(os.path.join(out, "stl"), exist_ok=True)
    for f in os.listdir(os.path.join(out, "stl")):
        if f.endswith(".stl"):
            os.remove(os.path.join(out, "stl", f))

    checks = list(pack["checks"])
    meshes, files, mesh_bad, oh_bad = {}, {}, [], []
    for p in pack["pieces"]:
        m = mesh_of(p["print"])
        meshes[p["id"]] = m
        dv = abs(m.volume - p["volume"]) / p["volume"]
        if not (m.is_watertight and m.is_winding_consistent and dv < 0.01 and abs(m.bounds[0][2]) < 1e-6):
            mesh_bad.append("%s (watertight %s, volume %.2f%%)" % (p["id"], m.is_watertight, 100 * dv))
        oh = overhangs(m)
        p["overhang"] = {"faces_area_mm2": round(sum(o["area"] for o in oh), 1),
                         "unsupported_mm2": round(sum(o["area"] for o in oh if not o["ok"]), 1),
                         "widest_ok_mm": max([o["width"] for o in oh if o["ok"]] or [0.0])}
        if p["overhang"]["unsupported_mm2"] > 0:
            oh_bad.append("%s %.0f mm2 (%s)" % (p["id"], p["overhang"]["unsupported_mm2"],
                                                ", ".join("w %.1f at z %.0f" % (o["width"], o["z"])
                                                          for o in oh if not o["ok"])))
        tail = p["name"].split(" - ", 1)[1] if " - " in p["name"] else ""
        fn = "%s_%s%s%s.stl" % (p["id"], PP.PART_INFO[p["part"]]["file"], "_" + slug(tail) if tail else "",
                                "_x%d" % p["qty"] if p["qty"] > 1 else "")
        m.export(os.path.join(out, "stl", fn))
        files[p["id"]] = fn
        p["stl"] = fn
    checks.append(("every STL is closed, consistently wound and matches its solid (<1% volume)", not mesh_bad,
                   "; ".join(mesh_bad)))
    checks.append(("no overhang steeper than %g deg off vertical wider than %g mm (prints without supports)" % (
        OVERHANG_MAX, OK_WIDTH), not oh_bad, "; ".join(oh_bad)))

    clashes, nmodel, duct = clash_check(pack)
    pack["duct"] = duct
    for cname, cl in clashes.items():
        checks.append(("no clash with the %d other rack parts or each other - %s" % (nmodel, cname), not cl,
                       "; ".join("%s x %s %.0f mm3" % c for c in cl) or
                       "internal duct cut to %.0f mm, sealing on the elbow shoulder" % duct["length"]))
    plates = pack_plates([p for p in pack["pieces"] if p["fit"]], printer)
    for p in pack["pieces"]:
        p.setdefault("plates", [])

    # ---- files
    write_step(pack, os.path.join(out, "SRA16_printed_parts.step"))
    zpath = os.path.join(out, "SRA16_print_%s.zip" % printer)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for p in pack["pieces"]:
            zi = zipfile.ZipInfo("SRA16_print/" + files[p["id"]], ZIP_DATE)
            zi.external_attr = 0o644 << 16
            zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, open(os.path.join(out, "stl", files[p["id"]]), "rb").read())
        zi = zipfile.ZipInfo("SRA16_print/PRINT_README.txt", ZIP_DATE)
        zi.external_attr = 0o644 << 16
        zi.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(zi, readme_txt(pack, plates))
    csv_path = os.path.join(ROOT, "bom", "printed_parts.csv") if main_pack else os.path.join(out, "printed_parts.csv")
    with open(csv_path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["piece", "part", "name", "material", "qty", "print_x_mm", "print_y_mm", "print_z_mm",
                    "volume_cm3", "mass_g_each", "est_hours_each", "plates", "orientation", "stl"])
        for p in pack["pieces"]:
            w.writerow([p["id"], p["part"], p["name"], p["mat"], p["qty"]] + [round(d, 1) for d in p["dims"]] +
                       [round(p["volume"] / 1000, 1), round(p["mass_g"], 0), round(p["hours"], 1),
                        " ".join(str(n) for n in sorted(set(p["plates"]))), p["note"],
                        os.path.relpath(os.path.join(out, "stl", p["stl"]), ROOT)])
    report = OrderedDict([
        ("doc", PP.DOC_NO), ("rev", PP.REV), ("layout_version", PP.RL.VERSION), ("printer", printer),
        ("usable_mm", PP.usable(printer)), ("design", PP.PR),
        ("checks", [(n, ok, d) for n, ok, d in checks]),
        ("pieces", [OrderedDict([("id", p["id"]), ("name", p["name"]), ("material", p["mat"]), ("qty", p["qty"]),
                                 ("print_mm", [round(d, 2) for d in p["dims"]]),
                                 ("volume_mm3", round(p["volume"], 0)), ("mass_g", round(p["mass_g"], 1)),
                                 ("hours", round(p["hours"], 2)), ("overhang", p["overhang"]),
                                 ("plates", sorted(set(p["plates"]))), ("stl", p["stl"])]) for p in pack["pieces"]]),
        ("plates", [OrderedDict([("no", pl["no"]), ("material", pl["mat"]),
                                 ("items", [[it["piece"]["id"], round(it["x"], 1), round(it["y"], 1), it["rot"]]
                                            for it in pl["items"]]),
                                 ("height_mm", round(pl["height"], 1)), ("mass_g", round(pl["mass_g"], 0)),
                                 ("hours", round(pl["hours"], 1))]) for pl in plates]),
        ("totals", OrderedDict((m, OrderedDict([
            ("pieces", sum(p["qty"] for p in pack["pieces"] if p["mat"] == m)),
            ("mass_g", round(sum(p["mass_g"] * p["qty"] for p in pack["pieces"] if p["mat"] == m), 0)),
            ("hours", round(sum(p["hours"] * p["qty"] for p in pack["pieces"] if p["mat"] == m), 1)),
            ("aud", round(sum(p["mass_g"] * p["qty"] for p in pack["pieces"] if p["mat"] == m) / 1000 *
                          PP.MATERIALS[m]["aud_kg"], 2)),
            ("aud_kg", PP.MATERIALS[m]["aud_kg"]), ("use", PP.MATERIALS[m]["use"])])) for m in PP.MATERIALS)),
        ("installed_mass_g", round(sum(p["mass_g"] * p["qty"] for p in pack["pieces"] if p["part"] != "G"), 0)),
        ("duct", OrderedDict((k, round(v, 1)) for k, v in pack["duct"].items())),
        ("hardware", OrderedDict((pid, pi["hardware"]) for pid, pi in PP.PART_INFO.items() if pi["hardware"])),
    ])
    with open(os.path.join(out, "print_report.json"), "w") as fh:
        json.dump(report, fh, indent=1)
    os.makedirs(rend, exist_ok=True)
    plates_figure(plates, meshes, printer, os.path.join(rend, "print_plates.png"))
    exploded_figure(pack, os.path.join(rend, "print_exploded.png"))
    if main_pack:
        with open(os.path.join(ROOT, "docs", "PRINTED_PARTS.md"), "w") as fh:
            fh.write(doc_md(pack, plates, report))

    print("plates:")
    for pl in plates:
        print("  %2d %-4s %-40s h %.0f  %.0f g  %.1f h" % (pl["no"], pl["mat"], ", ".join(
            it["piece"]["id"] for it in pl["items"]), pl["height"], pl["mass_g"], pl["hours"]))
    for p in pack["pieces"]:
        print("  %-6s overhang faces %7.1f mm2, unsupported %6.1f mm2, widest narrow strip %.1f mm" % (
            p["id"], p["overhang"]["faces_area_mm2"], p["overhang"]["unsupported_mm2"], p["overhang"]["widest_ok_mm"]))
    for name, ok, det in checks[len(pack["checks"]):]:
        print("  [%s] %s%s" % ("ok" if ok else "FAIL", name, (" - " + det) if det else ""))
    print("wrote %d STLs, zip, STEP, CSV, report and 2 renders%s to %s" % (
        len(files), " + docs/PRINTED_PARTS.md" if main_pack else "", os.path.relpath(out, ROOT)))
    return 0 if all(ok for _, ok, _ in checks) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
