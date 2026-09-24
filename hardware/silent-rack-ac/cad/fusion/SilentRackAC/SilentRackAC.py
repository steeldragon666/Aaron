"""
SilentRackAC.py - Autodesk Fusion script
Builds the SRA-16 Silent AC Rack (Dimplex GDC14RBA bay + 16RU acoustic rack)
in a NEW design document. Your open documents are never modified.

Install:  Utilities > ADD-INS > Scripts and Add-Ins (Shift+S) > "+" > select this
          SilentRackAC folder > Run.

Geometry comes from rack_layout.py (same folder) - the single source of truth
that also generates the STEP/GLB exports, so Fusion and the exports match.

Changing the design:
  * Edit DEFAULTS in rack_layout.py and run again, or
  * In a design built by this script: Modify > Change Parameters, edit any
    sr_* user parameter, keep that design active and run the script again.
    It reads the sr_* values and builds a fresh design with them.
    (The bodies are base features, so editing parameters alone does not
    move geometry - re-running the script does.)
"""

import adsk.core
import adsk.fusion
import importlib
import json
import math
import os
import sys
import time
import traceback

HERE = os.path.dirname(os.path.realpath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import rack_layout  # noqa: E402

importlib.reload(rack_layout)   # pick up edits between runs in one Fusion session

ORIENTATION = "auto"      # "auto" (follow Preferences), "zup" or "yup"
BUILD_EXAMPLE_IT = True   # example servers/blanks to show the 16RU in use
PARAM_PREFIX = "sr_"
VOLUME_TOL = 0.005        # 0.5 % cross-kernel volume tolerance

_app = None
_ui = None
_base_appearance = None


def _p3(x, y, z):
    return adsk.core.Point3D.create(x / 10.0, y / 10.0, z / 10.0)   # mm -> cm


def _v3(x, y, z):
    return adsk.core.Vector3D.create(float(x), float(y), float(z))


def _prim(tbm, q):
    k = q["kind"]
    if k == "box":
        (x0, y0, z0), (x1, y1, z1) = q["min"], q["max"]
        obb = adsk.core.OrientedBoundingBox3D.create(
            _p3((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0),
            _v3(1, 0, 0), _v3(0, 1, 0),
            (x1 - x0) / 10.0, (y1 - y0) / 10.0, (z1 - z0) / 10.0)
        return tbm.createBox(obb)
    if k == "cyl":
        r = q["r"] / 10.0
        return tbm.createCylinderOrCone(_p3(*q["p0"]), r, _p3(*q["p1"]), r)
    if k == "elbow":
        tor = tbm.createTorus(_p3(*q["c"]), _v3(*q["axis"]), q["R"] / 10.0, q["r"] / 10.0)
        clip = _prim(tbm, rack_layout.elbow_clip_box(q))
        if not tbm.booleanOperation(tor, clip, adsk.fusion.BooleanTypes.IntersectionBooleanType):
            raise RuntimeError("elbow clip failed")
        return tor
    raise ValueError("unknown primitive %s" % k)


def _make_part(tbm, part):
    body = _prim(tbm, part["add"][0])
    for q in part["add"][1:]:
        if not tbm.booleanOperation(body, _prim(tbm, q), adsk.fusion.BooleanTypes.UnionBooleanType):
            raise RuntimeError("union failed")
    for q in part["cut"]:
        if not tbm.booleanOperation(body, _prim(tbm, q), adsk.fusion.BooleanTypes.DifferenceBooleanType):
            raise RuntimeError("cut failed")
    return body


def _find_base_appearance():
    names = ("Plastic - Matte (Yellow)", "Plastic - Glossy (Yellow)", "Paint - Enamel Glossy (Yellow)")
    for i in range(_app.materialLibraries.count):
        lib = _app.materialLibraries.item(i)
        if "ppearance" not in lib.name:
            continue
        for n in names:
            try:
                a = lib.appearances.itemByName(n)
            except Exception:
                a = None
            if a:
                return a
    return None


def _appearance(design, rgb):
    """Design appearance for an (r, g, b) colour, created once per colour."""
    global _base_appearance
    name = "SRA %02X%02X%02X" % tuple(int(round(c * 255)) for c in rgb)
    a = design.appearances.itemByName(name)
    if a:
        return a
    if _base_appearance is None:
        _base_appearance = _find_base_appearance() or False
    if not _base_appearance:
        return None
    a = design.appearances.addByCopy(_base_appearance, name)
    cp = None
    try:
        cp = adsk.core.ColorProperty.cast(a.appearanceProperties.itemById("opaque_albedo"))
    except Exception:
        cp = None
    if not cp:
        for i in range(a.appearanceProperties.count):
            cp = adsk.core.ColorProperty.cast(a.appearanceProperties.item(i))
            if cp:
                break
    if cp:
        cp.value = adsk.core.Color.create(*[int(round(c * 255)) for c in rgb], 255)
    return a


def _read_overrides():
    """sr_* user parameters of the ACTIVE design (read-only), in mm."""
    ov = {}
    try:
        d = adsk.fusion.Design.cast(_app.activeProduct)
        if not d:
            return ov
        um = d.unitsManager
        for i in range(d.userParameters.count):
            p = d.userParameters.item(i)
            if not p.name.startswith(PARAM_PREFIX):
                continue
            key = p.name[len(PARAM_PREFIX):]
            if key not in rack_layout.DEFAULTS:
                continue
            if p.unit:
                ov[key] = um.convert(p.value, um.internalUnits, "mm")
            else:
                ov[key] = p.value
    except Exception:
        pass
    return ov


def _use_y_up():
    if ORIENTATION == "zup":
        return False
    if ORIENTATION == "yup":
        return True
    try:
        o = _app.preferences.generalPreferences.defaultModelingOrientation
        return o == adsk.core.DefaultModelingOrientations.YUpModelingOrientation
    except Exception:
        return False


def _add_user_params(design, P):
    ups = design.userParameters
    for key, (unit, desc) in rack_layout.PARAM_DOC.items():
        val = P[key]
        try:
            if unit == "mm":
                ups.add(PARAM_PREFIX + key, adsk.core.ValueInput.createByString("%g mm" % val), "mm", desc)
            else:
                ups.add(PARAM_PREFIX + key, adsk.core.ValueInput.createByReal(float(val)), "", desc)
        except Exception:
            pass


def run(context):
    global _app, _ui, _base_appearance
    _app = adsk.core.Application.get()
    _ui = _app.userInterface
    _base_appearance = None
    t0 = time.time()
    prog = None
    try:
        overrides = _read_overrides()
        P = rack_layout.resolve(overrides)
        parts, D = rack_layout.build_parts(P)
        if not BUILD_EXAMPLE_IT:
            parts = [p for p in parts if p["group"] != "Example IT (ref)"]
        warnings = rack_layout.validate(D)
        y_up = _use_y_up()

        # ---- safety: always build in a brand-new, empty document ----------
        _app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(_app.activeProduct)
        root = design.rootComponent
        if root.bRepBodies.count or root.occurrences.count:
            raise RuntimeError("New document is not empty - aborting.")
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        try:
            design.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
        except Exception:
            pass
        _add_user_params(design, P)

        tbm = adsk.fusion.TemporaryBRepManager.get()
        xform = None
        if y_up:
            xform = adsk.core.Matrix3D.create()
            xform.setToRotation(-math.pi / 2.0, _v3(1, 0, 0), adsk.core.Point3D.create(0, 0, 0))

        prog = _ui.createProgressDialog()
        prog.isCancelButtonShown = True
        prog.show("SRA-16 Silent AC Rack", "Building part %v of %m", 0, len(parts), 1)

        failures, built, n = [], {}, 0
        for group in rack_layout.GROUPS:
            gparts = [p for p in parts if p["group"] == group]
            if not gparts:
                continue
            occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
            comp = occ.component
            comp.name = group
            bf = comp.features.baseFeatures.add()
            bf.name = "SRA geometry"
            bf.startEdit()
            try:
                for p in gparts:
                    n += 1
                    prog.progressValue = n
                    adsk.doEvents()
                    if prog.wasCancelled:
                        raise KeyboardInterrupt()
                    try:
                        tb = _make_part(tbm, p)
                        if xform:
                            tbm.transform(tb, xform)
                        b = comp.bRepBodies.add(tb, bf)
                        b.name = p["name"]
                        built[p["name"]] = (comp, p)
                    except KeyboardInterrupt:
                        raise
                    except Exception as e:
                        failures.append("%s: %s" % (p["name"], e))
            finally:
                bf.finishEdit()
        prog.hide()
        prog = None

        # ---- appearance, opacity and cross-kernel volume check -------------
        expected = {}
        exp_path = os.path.join(HERE, "expected_volumes.json")
        same_params = False
        if os.path.exists(exp_path):
            with open(exp_path) as fh:
                ej = json.load(fh)
            same_params = all(abs(float(ej["params"].get(k, v)) - float(v)) < 1e-6 for k, v in P.items())
            expected = ej.get("volumes_mm3", {}) if same_params else {}
        vol_ok, vol_bad, vol_report = 0, [], {}
        for name, (comp, p) in built.items():
            body = comp.bRepBodies.itemByName(name)
            if not body:
                continue
            try:
                ap = _appearance(design, p["color"])
                if ap:
                    body.appearance = ap
            except Exception:
                pass
            if p.get("opacity", 1.0) < 1.0:
                try:
                    body.opacity = p["opacity"]
                except Exception:
                    pass
            v = body.volume * 1000.0     # cm3 -> mm3
            vol_report[name] = round(v, 1)
            if name in expected and expected[name] > 0:
                if abs(v - expected[name]) / expected[name] <= VOLUME_TOL:
                    vol_ok += 1
                else:
                    vol_bad.append("%s: %.0f vs %.0f mm3" % (name, v, expected[name]))

        try:
            vp = _app.activeViewport
            cam = vp.camera
            cam.viewOrientation = adsk.core.ViewOrientations.IsoTopRightViewOrientation
            cam.isFitView = True
            vp.camera = cam
            vp.refresh()
        except Exception:
            pass

        s = rack_layout.summary(D)
        report = {
            "layout_version": rack_layout.VERSION,
            "seconds": round(time.time() - t0, 1),
            "y_up": y_up,
            "overrides_from_active_design": overrides,
            "parts_requested": len(parts),
            "bodies_built": len(built),
            "failures": failures,
            "layout_warnings": warnings,
            "volume_check": {"compared": bool(expected), "within_tol": vol_ok, "mismatches": vol_bad},
            "volumes_mm3": vol_report,
            "summary": s,
        }
        try:
            with open(os.path.join(HERE, "fusion_build_report.json"), "w") as fh:
                json.dump(report, fh, indent=1)
        except Exception:
            pass

        ext = s["external_mm"]
        lines = [
            "SRA-16 Silent AC Rack  (layout v%s)" % rack_layout.VERSION,
            "",
            "Bodies built: %d / %d in %.0f s%s" % (len(built), len(parts), time.time() - t0,
                                                   "  (Y-up)" if y_up else ""),
            "External: %.0f W x %.0f D x %.0f H mm" % ext,
            "Rack: %d RU  |  AC bay floor at Z %.0f mm" % (s["rack_units"], s["ac_bay_floor_z_mm"]),
        ]
        if overrides:
            lines.append("Used %d sr_* parameter(s) from the previously active design." % len(overrides))
        if expected:
            lines.append("Volume cross-check vs CadQuery: %d / %d within %.1f%%"
                         % (vol_ok, len(expected), VOLUME_TOL * 100))
        elif not same_params:
            lines.append("Volume cross-check skipped (parameters differ from the export).")
        if failures:
            lines += ["", "FAILED parts (%d):" % len(failures)] + failures[:12]
        if vol_bad:
            lines += ["", "Volume mismatches (%d):" % len(vol_bad)] + vol_bad[:8]
        if warnings:
            lines += ["", "Layout warnings:"] + warnings
        lines += ["", "Report: fusion_build_report.json (script folder).",
                  "Save the new design into your project when happy."]
        _ui.messageBox("\n".join(lines), "SRA-16 build")

    except KeyboardInterrupt:
        if prog:
            prog.hide()
        _ui.messageBox("Build cancelled - the partial design is left open.", "SRA-16 build")
    except Exception:
        if prog:
            prog.hide()
        if _ui:
            _ui.messageBox("SRA-16 build failed:\n{}".format(traceback.format_exc()), "SRA-16 build")


def stop(context):
    pass
