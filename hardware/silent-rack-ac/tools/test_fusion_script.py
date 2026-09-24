#!/usr/bin/env python3
"""
Exercise cad/fusion/SilentRackAC/SilentRackAC.py outside Fusion using the
tools/fusion_mock `adsk` stand-in (CadQuery-backed).  Checks:
  1. default Z-up build: every part becomes a body, volumes match the
     CadQuery export within 0.5 %, parameters written as sr_* user params
  2. re-run with an edited sr_ru_count (read from the active design)
  3. Y-up orientation rotates the model so +Y is up
The real Fusion API is not emulated in full - this guards control flow, units
and the cross-check logic.  Run inside Fusion for the final word.
"""
import importlib
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "cad", "fusion", "SilentRackAC")


def load_script(tmp):
    sys.path.insert(0, os.path.join(HERE, "fusion_mock"))
    sys.path.insert(0, tmp)
    for m in ("SilentRackAC", "rack_layout"):
        sys.modules.pop(m, None)
    import SilentRackAC  # noqa: E402
    return SilentRackAC


def main():
    tmp = tempfile.mkdtemp(prefix="sra_fusion_")
    for f in ("SilentRackAC.py", "rack_layout.py", "expected_volumes.json", "SilentRackAC.manifest"):
        shutil.copy(os.path.join(SRC, f), tmp)
    json.load(open(os.path.join(tmp, "SilentRackAC.manifest")))      # manifest is valid JSON
    S = load_script(tmp)
    import adsk.core
    app = adsk.core.Application.get()
    ok = True

    # ---- 1. default build -------------------------------------------------
    S.run(None)
    rep = json.load(open(os.path.join(tmp, "fusion_build_report.json")))
    d1 = app.activeProduct
    n_params = d1.userParameters.count
    c1 = (rep["bodies_built"] == rep["parts_requested"] and not rep["failures"]
          and rep["volume_check"]["compared"] and not rep["volume_check"]["mismatches"]
          and rep["volume_check"]["within_tol"] == rep["parts_requested"])
    print("[%s] run 1: %d/%d bodies, %d volumes within tol, %d user params"
          % ("PASS" if c1 else "FAIL", rep["bodies_built"], rep["parts_requested"],
             rep["volume_check"]["within_tol"], n_params))
    ok &= c1

    # ---- 2. edit sr_ru_count in the active design, run again ---------------
    for i in range(d1.userParameters.count):
        p = d1.userParameters.item(i)
        if p.name == "sr_ru_count":
            p.value = 17.0
    S.run(None)
    rep2 = json.load(open(os.path.join(tmp, "fusion_build_report.json")))
    h2 = rep2["summary"]["external_mm"][2]
    c2 = (rep2["overrides_from_active_design"].get("ru_count") == 17.0 and rep2["summary"]["rack_units"] == 17
          and abs(h2 - (1904.2 + 44.45)) < 0.2 and not rep2["failures"] and not rep2["volume_check"]["compared"])
    print("[%s] run 2: override ru_count=17 -> H %.2f mm, %d bodies" % ("PASS" if c2 else "FAIL", h2, rep2["bodies_built"]))
    ok &= c2

    # ---- 3. Y-up ---------------------------------------------------------
    S.ORIENTATION = "yup"
    app.activeProduct = None          # no active design -> defaults
    S.run(None)
    d3 = app.activeProduct
    comp = [o.component for o in d3.rootComponent.occurrences._o if o.component.name == "Panels & Doors"][0]
    bb = comp.bRepBodies.itemByName("Top panel").bbox()
    # Z-up top panel spans z 188.92..190.42 cm; Y-up maps (x,y,z)->(x,z,-y)
    c3 = abs(bb.ymax - 190.42) < 0.01 and abs(bb.zmin + 110.0) < 0.01 and abs(bb.zmax) < 0.01
    print("[%s] run 3: Y-up top panel bbox y %.2f..%.2f cm, z %.2f..%.2f cm"
          % ("PASS" if c3 else "FAIL", bb.ymin, bb.ymax, bb.zmin, bb.zmax))
    ok &= c3
    shutil.rmtree(tmp, ignore_errors=True)
    print("ALL PASS" if ok else "FAILURES")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
