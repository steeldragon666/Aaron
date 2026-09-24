#!/usr/bin/env python3
"""
Airflow-zone verification for the SRA-16 Silent AC Rack.

Voxelises every part from rack_layout.py (2.5 mm grid), flood-fills the air
spaces and proves that:
  * the COLD supply (hood -> front plenum) is sealed from everything else,
  * the HOT RETURN (rear plenum -> shelf -> upper bay -> AC evaporator grille)
    is sealed from the room and from the condenser zone,
  * the CONDENSER zone (under the partition) is fed with room air via the
    plinth labyrinth, and
  * the EXHAUST duct interior is sealed from the return zone and vents out.
The AC and the IT equipment are the only intended links between zones.

Writes renders/zones_*.png section maps and cad/exports/zone_report.json.
Usage: python3 tools/zone_check.py [voxel_mm]
"""
import json
import os
import sys

import numpy as np
import scipy.ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "cad", "fusion", "SilentRackAC"))
import rack_layout as RL  # noqa: E402


def prim_mask(p, xs, ys, zs):
    """Boolean mask of primitive p on the grid defined by 1-D centre coords."""
    k = p["kind"]
    if k == "box":
        (x0, y0, z0), (x1, y1, z1) = p["min"], p["max"]
        bx = (xs >= x0) & (xs <= x1)
        by = (ys >= y0) & (ys <= y1)
        bz = (zs >= z0) & (zs <= z1)
        return bx[:, None, None] & by[None, :, None] & bz[None, None, :]
    if k == "cyl":
        p0, p1, r = np.array(p["p0"]), np.array(p["p1"]), p["r"]
        ax = int(np.argmax(np.abs(p1 - p0)))
        lo, hi = min(p0[ax], p1[ax]), max(p0[ax], p1[ax])
        coords = [xs, ys, zs]
        along = (coords[ax] >= lo) & (coords[ax] <= hi)
        o = [i for i in range(3) if i != ax]
        da = (coords[o[0]] - p0[o[0]]) ** 2
        db = (coords[o[1]] - p0[o[1]]) ** 2
        disk = (da[:, None] + db[None, :]) <= r * r
        shape = [1, 1, 1]
        shape[ax] = len(coords[ax])
        along = along.reshape(shape)
        dshape = [len(xs), len(ys), len(zs)]
        dshape[ax] = 1
        return along & disk.reshape(dshape)
    if k == "elbow":
        clip = prim_mask(RL.elbow_clip_box(p), xs, ys, zs)
        c, a = np.array(p["c"]), np.array(p["axis"], float)
        X, Y, Z = np.meshgrid(xs - c[0], ys - c[1], zs - c[2], indexing="ij")
        along = X * a[0] + Y * a[1] + Z * a[2]
        rho = np.sqrt(np.maximum(X * X + Y * Y + Z * Z - along * along, 0.0))
        return clip & ((rho - p["R"]) ** 2 + along ** 2 <= p["r"] ** 2)
    raise ValueError(k)


def main(argv):
    h = float(argv[0]) if argv else 2.5
    parts, D = RL.build_parts()
    W, DP, EH = D["ext_w"], D["ext_d"], D["ext_h"]
    nx, ny, nz = int(np.ceil(W / h)), int(np.ceil(DP / h)), int(np.ceil(EH / h))
    gx, gy, gz = (np.arange(nx) + 0.5) * h, (np.arange(ny) + 0.5) * h, (np.arange(nz) + 0.5) * h
    owner = np.full((nx, ny, nz), -1, dtype=np.int16)

    def idx(lo, hi, g, n):
        a = max(int(np.floor(lo / h - 0.5)), 0)
        b = min(int(np.ceil(hi / h + 0.5)), n)
        return a, b

    for pi, part in enumerate(parts):
        mins = np.min([RL.prim_bbox(q)[0] for q in part["add"]], axis=0)
        maxs = np.max([RL.prim_bbox(q)[1] for q in part["add"]], axis=0)
        ia, ib = idx(mins[0], maxs[0], gx, nx)
        ja, jb = idx(mins[1], maxs[1], gy, ny)
        ka, kb = idx(mins[2], maxs[2], gz, nz)
        if ia >= ib or ja >= jb or ka >= kb:
            continue
        xs, ys, zs = gx[ia:ib], gy[ja:jb], gz[ka:kb]
        m = np.zeros((ib - ia, jb - ja, kb - ka), bool)
        for q in part["add"]:
            m |= prim_mask(q, xs, ys, zs)
        for q in part["cut"]:
            m &= ~prim_mask(q, xs, ys, zs)
        sub = owner[ia:ib, ja:jb, ka:kb]
        sub[m] = pi

    air = owner < 0
    labels, nlab = ndi.label(air)
    faces = [labels[0], labels[-1], labels[:, 0], labels[:, -1], labels[:, :, 0], labels[:, :, -1]]
    boundary = set(np.unique(np.concatenate([f.ravel() for f in faces]))) - {0}

    def lab(pt):
        i, j, k = (int(pt[0] / h), int(pt[1] / h), int(pt[2] / h))
        return int(labels[i, j, k])

    xm = D["x_mid"]
    seeds = {
        "cold_hood": (xm, (D["y_in0"] + D["out_y1"]) / 2, (D["z_ac1"] + 30 + D["z_shelf0"]) / 2),
        "cold_front_plenum": (xm, (D["y_in0"] + D["y_frail"]) / 2, (D["z_rack0"] + D["z_rack1"]) / 2),
        "hot_rear_plenum": (xm, (D["y_rrail"] + D["y_in1"]) / 2, (D["z_rack0"] + D["z_rack1"]) / 2),
        "hot_upper_bay": (xm, (D["y_dock"] + D["y_in1"]) / 2, (D["z_split"] + D["z_shelf_foam0"]) / 2 + 150),
        "hot_ac_side_gap": (D["x_in0"] + 12, (D["y_ac0"] + D["y_ac1"]) / 2, 700.0),
        "hot_ac_notch": (D["exh_x"] + 96, D["exh_y"], D["exh_z1"] + 20),
        "condenser_zone": (xm, (D["y_dock"] + D["inlet_y0"]) / 2 - 60, (D["z_tray1"] + D["z_part0"]) / 2),
        "inlet_riser": (xm, (D["inlet_y0"] + D["inlet_y1"]) / 2, D["z_tray1"] + 150),
        "plinth_void": (xm, D["ext_d"] / 2, 50.0),
        "exhaust_duct": (D["exh_x"], (D["exh_run_y0"] + D["y_in1"]) / 2, D["exh_run_z"]),
    }
    res = {}
    for k, pt in seeds.items():
        L = lab(pt)
        res[k] = {"label": L, "air": L != 0, "vents_to_room": L in boundary,
                  "volume_L": round(float((labels == L).sum()) * h ** 3 / 1e6, 1) if L else 0.0}

    cold, hot = res["cold_hood"]["label"], res["hot_rear_plenum"]["label"]
    cond, exh = res["condenser_zone"]["label"], res["exhaust_duct"]["label"]
    checks = {
        "seed voxels are air": all(v["air"] for v in res.values()),
        "cold hood feeds front plenum": res["cold_front_plenum"]["label"] == cold,
        "cold zone sealed from room": not res["cold_hood"]["vents_to_room"],
        "hot return is one connected loop": all(res[s]["label"] == hot for s in
                                                ("hot_upper_bay", "hot_ac_side_gap", "hot_ac_notch")),
        "hot return sealed from room": not res["hot_rear_plenum"]["vents_to_room"],
        "cold and hot zones separated": cold != hot,
        "condenser zone separated from hot return": cond != hot and cond != cold,
        "condenser zone draws room air (labyrinth)": res["condenser_zone"]["vents_to_room"]
                                                      and res["inlet_riser"]["label"] == cond
                                                      and res["plinth_void"]["label"] == cond,
        "exhaust duct sealed from hot return": exh != hot and exh != cond,
        "exhaust duct vents out through rear spigot": res["exhaust_duct"]["vents_to_room"],
    }
    ok = all(checks.values())
    print("voxel %.1f mm grid %dx%dx%d, %d air regions" % (h, nx, ny, nz, nlab))
    for k, v in res.items():
        print("  %-20s label %-5d room=%-5s %8.1f L" % (k, v["label"], v["vents_to_room"], v["volume_L"]))
    for k, v in checks.items():
        print("  [%s] %s" % ("PASS" if v else "FAIL", k))

    # ------------------------------------------------------------ section maps
    zone_rgb = {cold: (0.30, 0.60, 0.98), hot: (0.95, 0.42, 0.25),
                cond: (0.35, 0.78, 0.42), exh: (1.00, 0.72, 0.10)}
    cols = np.array([p["color"] for p in parts] + [(1, 1, 1)])

    def section(axis, pos):
        i = int(pos / h)
        if axis == "x":
            own, lb = owner[i, :, :], labels[i, :, :]
        elif axis == "y":
            own, lb = owner[:, i, :], labels[:, i, :]
        else:
            own, lb = owner[:, :, i], labels[:, :, i]
        img = np.ones(own.shape + (3,))
        solid = own >= 0
        img[solid] = cols[own[solid]] * 0.55 + 0.45 * 0.62      # muted solids
        for L, c in zone_rgb.items():
            img[lb == L] = c
        other = (~solid) & ~np.isin(lb, list(zone_rgb)) & ~np.isin(lb, list(boundary))
        img[other] = (0.85, 0.80, 0.95)                          # sealed voids
        room = (~solid) & np.isin(lb, list(boundary)) & ~np.isin(lb, list(zone_rgb))
        img[room] = (1.0, 1.0, 1.0)
        return img

    out = {}
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.patches import Patch
        rdir = os.path.join(ROOT, "renders")
        os.makedirs(rdir, exist_ok=True)
        legend = [Patch(color=zone_rgb[cold], label="Cold supply (AC -> servers)"),
                  Patch(color=zone_rgb[hot], label="Hot return (servers -> AC)"),
                  Patch(color=zone_rgb[cond], label="Room air to condenser"),
                  Patch(color=zone_rgb[exh], label="Condenser exhaust (to outdoors)"),
                  Patch(color=(0.85, 0.80, 0.95), label="Sealed void")]
        for axis, pos, title in (("x", D["x_mid"], "Section A-A: centreline (X = %.0f)" % D["x_mid"]),
                                 ("x", D["exh_x"], "Section B-B: exhaust plane (X = %.1f)" % D["exh_x"])):
            img = section(axis, pos)
            fig, ax = plt.subplots(figsize=(7.2, 11))
            ax.imshow(np.flipud(np.transpose(img, (1, 0, 2))), extent=(0, DP, 0, EH), interpolation="nearest")
            ax.set_xlabel("Depth Y (mm)  front -> rear")
            ax.set_ylabel("Height Z (mm)")
            ax.set_title(title, fontsize=11)
            ax.legend(handles=legend, loc="upper center", bbox_to_anchor=(0.5, -0.06), ncol=2, fontsize=8, frameon=False)
            fig.tight_layout()
            fn = os.path.join(rdir, "zones_%s_%d.png" % (axis, int(pos)))
            fig.savefig(fn, dpi=130)
            plt.close(fig)
            out[title] = os.path.relpath(fn, ROOT)
        img = section("z", 700.0)
        fig, ax = plt.subplots(figsize=(7.2, 11))
        ax.imshow(np.transpose(img, (1, 0, 2)), extent=(0, W, DP, 0), interpolation="nearest")
        ax.set_xlabel("Width X (mm)")
        ax.set_ylabel("Depth Y (mm)  front (top) -> rear")
        ax.set_title("Section C-C: plan through AC bay (Z = 700)", fontsize=11)
        ax.legend(handles=legend, loc="upper center", bbox_to_anchor=(0.5, -0.06), ncol=2, fontsize=8, frameon=False)
        fig.tight_layout()
        fn = os.path.join(rdir, "zones_z_700.png")
        fig.savefig(fn, dpi=130)
        plt.close(fig)
        out["Section C-C"] = os.path.relpath(fn, ROOT)
    except Exception as e:  # images are optional
        print("  (section images skipped: %s)" % e)

    rep = {"voxel_mm": h, "seeds": res, "checks": checks, "all_pass": ok, "images": out}
    with open(os.path.join(ROOT, "cad", "exports", "zone_report.json"), "w") as fh:
        json.dump(rep, fh, indent=1)
    print("ALL PASS" if ok else "SOME CHECKS FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
