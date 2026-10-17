#!/usr/bin/env python3
"""
make_master_step.py - everything in one STEP: the whole SRA-16 as it will be built, for Fusion.

  cad/exports/SRA16_complete_assembly.step   (+ .glb; `SRA_RENDER=complete node tools/render/render.mjs`
                                             renders renders/complete_*.png from it)

One assembly, grouped like the rack model, with:
  - the rack model (rack_layout.py): skins, lining, base, airflow parts, 19in rack, AC and example IT;
  - the welded frame as built (true 30x30 SHS with radii, rivnut holes, pads and caps, CP-SRA16-FRM-001)
    in place of the model's solid frame bars;
  - the 3D-printed parts in their installed positions (CP-SRA16-PRT-001) in place of the model parts
    they replace (hood, elbow, wall spigot, office adaptors and grilles), both office ports and both
    office wall grilles, the exhaust duct cut to length at the elbow's shoulder;
  - the control electronics (CP-SRA16-ELC-001): probes, sensors, switches and the IR emitter as simple
    stand-ins at their mounting points (the pod, node box and clips are printed parts).

Usage: python3 tools/make_master_step.py
Run after build_cadquery.py, make_weld_pack.py and make_print_pack.py (it rebuilds from the same code).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import cadquery as cq  # noqa: E402

import build_cadquery as BC  # noqa: E402
import make_electronics as ELC  # noqa: E402
import make_print_pack as MPP  # noqa: E402
import make_weld_pack as MWP  # noqa: E402
import printparts as PP  # noqa: E402
import weldment as WM  # noqa: E402

RL = PP.RL
OUT = os.path.join(ROOT, "cad", "exports", "SRA16_complete_assembly.step")
STEEL, SS = (0.42, 0.45, 0.48), (0.78, 0.79, 0.80)
ELC_COL = {"probe": SS, "sensor": (0.10, 0.45, 0.25), "switch": (0.15, 0.15, 0.17), "ir": (0.12, 0.12, 0.12)}
# electronics stand-ins: spot id -> (kind, shape) at the SPOTS coordinates of make_electronics
STANDIN = {"T1": "probe", "T2": "probe", "T3": "probe", "T4": "probe", "T5": "probe", "T6": "probe",
           "RH": "sensor", "LK": "switch", "DL": "switch", "DU": "switch", "IR": "ir"}


def place(sid, x, y, z, shapes):
    """Stand-in position: the SPOTS point, moved onto the surface the item is fixed to where needed."""
    if sid == "IR":                                         # on the face of the AC's display bezel
        y = shapes["AC display bezel"].BoundingBox().ymin
    if sid == "DU":                                         # on the upper door lining's inner face
        y = shapes["Foam door upper"].BoundingBox().ymax + 6.0
    return x, y, z


def standin(kind, x, y, z):
    if kind == "probe":                                     # 6 x 50 stainless probe, tip into the air stream
        return cq.Solid.makeCylinder(3.0, 50.0, cq.Vector(x, y, z), cq.Vector(1, 0, 0))
    if kind == "sensor":                                    # SHT41 breakout
        return cq.Solid.makeBox(4.0, 20.0, 25.0, pnt=cq.Vector(x, y - 10.0, z - 12.5))
    if kind == "ir":                                        # stick-on IR emitter
        return cq.Solid.makeCylinder(4.0, 6.0, cq.Vector(x, y, z), cq.Vector(0, -1, 0))
    return cq.Solid.makeBox(25.0, 12.0, 8.0, pnt=cq.Vector(x - 12.5, y - 6.0, z - 4.0))  # reed / float switch


def main():
    parts, D = RL.build_parts(RL.resolve(None))
    pack = PP.build(None, "x1c")
    I = pack["I"]
    replaced = {n for pi in PP.PART_INFO.values() for n in pi["replaces"]}

    # rack model, less the solid frame bars (the weldment replaces them) and the parts printed instead
    shapes = {}
    for p in parts:
        if p["group"] == "Frame" or p["name"].startswith("Rail spacer") or p["name"] in replaced:
            continue                                        # the weldment carries frame bars and rail spacers
        shapes[p["name"]] = BC.make_part(p)
    ei = pack["parts"]["P4"]["info"]                        # exhaust duct cut on site at the elbow's shoulder
    du = I["duct"]
    shapes[MPP.DUCT] = shapes[MPP.DUCT].cut(
        PP.slab(du["p0"], (du["p1"] - du["p0"]).normalized(), -1.0, ei["ro"] - ei["ro2"]))
    for op in I["office"]:                                  # the flex ducts stretch over the spigots' clamp bead
        p0, p1, ro = op["spigot"]
        k = [k for k in shapes if k.startswith("Office %s duct" % op["name"])][0]
        shapes[k] = shapes[k].cut(PP.cyl(tuple(p0), tuple(p1), ro + PP.PR["bead"] + 0.5))

    assy = cq.Assembly(name="SRA-16 Silent AC Rack - complete (layout v%s)" % RL.VERSION)
    n = 0

    # welded frame as built
    wm = WM.build(None)
    sub = cq.Assembly(name="Frame (welded 30x30 SHS, %s)" % WM.DOC_NO)
    names = {}
    for m, s in MWP.build_solids(wm):
        nm = "%s %s" % (m["mark"], WM.location(m) if m["kind"] != "cap" else m["name"].replace("Cap Post ", "cap "))
        names[nm] = names.get(nm, 0) + 1
        nm += " (%d)" % names[nm] if names[nm] > 1 else ""
        sub.add(s, name=nm, color=cq.Color(*STEEL, 1.0))
        n += 1
    assy.add(sub, name=sub.name)

    for g in RL.GROUPS:
        if g == "Frame":
            continue
        sub = cq.Assembly(name=g)
        for p in parts:
            if p["group"] != g or p["name"] not in shapes:
                continue
            r, gg, b = p["color"]
            sub.add(shapes[p["name"]], name=p["name"], color=cq.Color(r, gg, b, p.get("opacity", 1.0)))
            n += 1
        assy.add(sub, name=g)

    # printed parts in place
    sub = cq.Assembly(name="3D-printed parts (%s rev %s)" % (PP.DOC_NO, PP.REV))
    for p in pack["pieces"]:
        if p["part"] in ("G", "P8"):                        # gauges and loose clips: no installed position
            continue
        r, g, b = PP.MATERIALS[p["mat"]]["colour"]
        sols = list(MPP.installed(p, pack))
        if p["part"] == "P12" and len(I["office"]) > 1:      # office wall grille: one per duct
            dy = I["office"][1]["y"] - I["office"][0]["y"]
            sols.append(sols[0].translate(cq.Vector(0, dy, 0)))
        for j, s in enumerate(sols):
            tag = ""
            if p["part"] in ("P9", "P10", "P12") and len(sols) > 1:
                tag = " (%s)" % I["office"][j]["name"]
            elif len(sols) > 1:
                tag = " (%d)" % (j + 1)
            sub.add(s, name="%s %s%s" % (p["id"], p["name"], tag), color=cq.Color(r, g, b, 1.0))
            n += 1
    assy.add(sub, name=sub.name)

    # control electronics stand-ins
    sub = cq.Assembly(name="Control electronics (%s)" % ELC.DOC_NO)
    for sid, what, x, y, z, _how in ELC.SPOTS:
        kind = STANDIN.get(sid)
        if not kind:
            continue
        sub.add(standin(kind, *place(sid, x, y, z, shapes)), name="%s %s" % (sid, what), color=cq.Color(*ELC_COL[kind], 1.0))
        n += 1
    if len(I["office"]) > 1:                                # T7: in the return wall grille's probe channel
        wi = pack["parts"]["P12"]["info"]
        op = I["office"][1]
        x_wall = I["office"][0]["spigot"][1].x + RL.OFFICE["duct_stub"] + 60.0
        yp, zc0, zc1 = wi["probe"]
        t7 = cq.Solid.makeCylinder(3.0, 50.0, cq.Vector(x_wall - zc0, op["y"], op["z"] + yp), cq.Vector(-1, 0, 0))
        sub.add(t7, name="T7 Office (return wall grille)", color=cq.Color(*ELC_COL["probe"], 1.0))
        n += 1
    assy.add(sub, name=sub.name)

    assy.export(OUT, exportType="STEP")
    assy.export(OUT.replace(".step", ".glb"), exportType="GLTF", tolerance=0.2, angularTolerance=0.2)
    txt = open(OUT).read()                                  # reproducible: fixed timestamp
    txt = re.sub(r"(FILE_NAME\('[^']*',')[0-9T:\-\.]+(')", r"\g<1>2026-01-01T00:00:00\g<2>", txt, count=1)
    open(OUT, "w").write(txt)
    print("complete assembly: %d bodies -> %s (%.1f MB)" % (n, OUT, os.path.getsize(OUT) / 1e6))


if __name__ == "__main__":
    main()
