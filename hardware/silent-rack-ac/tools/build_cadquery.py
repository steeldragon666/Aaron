#!/usr/bin/env python3
"""
Build the SRA-16 Silent AC Rack from rack_layout.py with CadQuery/OpenCascade.

Outputs (relative to hardware/silent-rack-ac/):
  cad/exports/SilentRackAC.step        named + coloured STEP assembly (opens in Fusion)
  cad/exports/SilentRackAC.glb         glTF binary for the web viewer / renders
  cad/fusion/SilentRackAC/expected_volumes.json   cross-kernel check for the Fusion script
  cad/exports/build_report.json        interference + clearance report

Usage:  python3 tools/build_cadquery.py [--no-export] [key=value ...]
        e.g. python3 tools/build_cadquery.py ru_count=17
"""
import json
import os
import sys
import time
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LAYOUT_DIR = os.path.join(ROOT, "cad", "fusion", "SilentRackAC")
sys.path.insert(0, LAYOUT_DIR)

import cadquery as cq  # noqa: E402
import rack_layout as RL  # noqa: E402


def make_prim(p):
    k = p["kind"]
    if k == "box":
        (x0, y0, z0), (x1, y1, z1) = p["min"], p["max"]
        return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, pnt=cq.Vector(x0, y0, z0))
    if k == "cyl":
        p0, p1 = cq.Vector(*p["p0"]), cq.Vector(*p["p1"])
        d = p1 - p0
        return cq.Solid.makeCylinder(p["r"], d.Length, pnt=p0, dir=d.normalized())
    if k == "elbow":
        tor = cq.Solid.makeTorus(p["R"], p["r"], pnt=cq.Vector(*p["c"]), dir=cq.Vector(*p["axis"]))
        return tor.intersect(make_prim(RL.elbow_clip_box(p)))
    raise ValueError(k)


def make_part(part):
    adds = [make_prim(p) for p in part["add"]]
    shape = adds[0]
    for a in adds[1:]:
        shape = shape.fuse(a)
    for c in part["cut"]:
        shape = shape.cut(make_prim(c))
    shape = shape.clean()
    solids = shape.Solids()
    if len(solids) == 1:
        return solids[0]
    return cq.Compound.makeCompound(solids)


def bbox_overlap(a, b, tol=0.05):
    return (a.xmin < b.xmax - tol and b.xmin < a.xmax - tol and
            a.ymin < b.ymax - tol and b.ymin < a.ymax - tol and
            a.zmin < b.zmax - tol and b.zmin < a.zmax - tol)


def main(argv):
    overrides, export = {}, True
    for a in argv:
        if a == "--no-export":
            export = False
        elif "=" in a:
            k, v = a.split("=", 1)
            overrides[k] = float(v)
    P = RL.resolve(overrides)
    t0 = time.time()
    parts, D = RL.build_parts(P)
    warnings = RL.validate(D)
    print("layout v%s: %d parts, %s" % (RL.VERSION, len(parts), "OK" if not warnings else warnings))

    shapes = {}
    for part in parts:
        shapes[part["name"]] = make_part(part)
    names = [p["name"] for p in parts]
    assert len(set(names)) == len(names), "duplicate part names"
    print("built %d solids in %.1fs" % (len(shapes), time.time() - t0))

    # ---------------------------------------------------------------- checks
    bbs = {n: shapes[n].BoundingBox() for n in names}
    clashes = []
    for a, b in combinations(names, 2):
        if not bbox_overlap(bbs[a], bbs[b]):
            continue
        v = shapes[a].intersect(shapes[b]).Volume()
        if v > 1.0:
            clashes.append((a, b, round(v, 1)))
    print("interference check: %d clash(es)" % len(clashes))
    for c in clashes:
        print("   CLASH %-40s x %-40s %10.1f mm3" % c)

    vols = {n: shapes[n].Volume() for n in names}
    groups = {}
    for p in parts:
        g = groups.setdefault(p["group"], {"parts": 0, "volume_mm3": 0.0})
        g["parts"] += 1
        g["volume_mm3"] += vols[p["name"]]
    allbb = shapes[names[0]].BoundingBox()
    for n in names[1:]:
        allbb = allbb.add(bbs[n])
    ext = (round(allbb.xmin, 1), round(allbb.ymin, 1), round(allbb.zmin, 1),
           round(allbb.xmax, 1), round(allbb.ymax, 1), round(allbb.zmax, 1))
    print("overall bbox (incl. handles/spigot):", ext)

    report = {
        "layout_version": RL.VERSION,
        "params": P,
        "summary": RL.summary(D),
        "warnings": warnings,
        "clashes": clashes,
        "overall_bbox_mm": ext,
        "groups": {g: {"parts": v["parts"], "volume_mm3": round(v["volume_mm3"], 0)} for g, v in groups.items()},
    }
    expected = {
        "layout_version": RL.VERSION,
        "params": P,
        "part_count": len(parts),
        "volumes_mm3": {n: round(vols[n], 1) for n in names},
    }

    if export:
        exp_dir = os.path.join(ROOT, "cad", "exports")
        os.makedirs(exp_dir, exist_ok=True)
        with open(os.path.join(LAYOUT_DIR, "expected_volumes.json"), "w") as fh:
            json.dump(expected, fh, indent=1)
        with open(os.path.join(exp_dir, "build_report.json"), "w") as fh:
            json.dump(report, fh, indent=1)
        assy = cq.Assembly(name="SRA-16 Silent AC Rack")
        for g in RL.GROUPS:
            sub = cq.Assembly(name=g)
            for p in parts:
                if p["group"] != g:
                    continue
                r, gg, b = p["color"]
                sub.add(shapes[p["name"]], name=p["name"], color=cq.Color(r, gg, b, p.get("opacity", 1.0)))
            assy.add(sub, name=g)
        t1 = time.time()
        assy.export(os.path.join(exp_dir, "SilentRackAC.step"), exportType="STEP")
        assy.export(os.path.join(exp_dir, "SilentRackAC.glb"), exportType="GLTF", tolerance=0.2, angularTolerance=0.2)
        print("exported STEP + GLB in %.1fs -> %s" % (time.time() - t1, exp_dir))
    return 0 if not clashes else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
