"""
Build every deliverable from the parametric model.

    python build.py            # STEP + render meshes for all designs
    python build.py --step     # STEP only

Outputs (relative to the project root):
    step/denza_b8_proxy.step                 vehicle envelope (fit-check only)
    step/<design>_rack_assembly.step         rack, hangar closed, no drone
    step/<design>_with_vehicle.step          rack + vehicle proxy, for packaging review
    build/mesh/<variant>/*.stl + manifest.json   render meshes (git-ignored)
    docs/bom_<design>.csv                    part list with material + bounding box
"""
from __future__ import annotations

import csv
import json
import sys
import time
from pathlib import Path

import cadquery as cq

from designs import DESIGNS, design_c
from vehicle import build_vehicle

ROOT = Path(__file__).resolve().parent.parent
STEP_DIR = ROOT / "step"
MESH_DIR = ROOT / "build" / "mesh"
DOCS = ROOT / "docs"

# display colours for the STEP assembly (CAD viewers); render materials live in render/
STEP_COLOURS = {
    "rack_black": (0.08, 0.08, 0.09), "satin_black": (0.1, 0.1, 0.11),
    "gloss_black": (0.03, 0.03, 0.03), "anodised_grey": (0.35, 0.36, 0.38),
    "carbon": (0.12, 0.12, 0.13), "rubber": (0.05, 0.05, 0.05),
    "led_white": (0.95, 0.97, 1.0), "led_amber": (1.0, 0.6, 0.1), "led_cyan": (0.2, 0.9, 1.0),
    "led_halo": (0.9, 0.95, 1.0), "hangar_shell": (0.78, 0.79, 0.8), "pad_dark": (0.15, 0.15, 0.16),
    "marking": (0.95, 0.85, 0.2), "copper": (0.8, 0.5, 0.25), "drone_grey": (0.45, 0.46, 0.47),
    "drone_dark": (0.12, 0.12, 0.12), "glass_black": (0.05, 0.07, 0.08), "prop_blur": (0.2, 0.2, 0.2),
    "antenna_white": (0.92, 0.92, 0.9), "antenna_black": (0.1, 0.1, 0.1),
    "radome_white": (0.93, 0.93, 0.92), "radome_xray": (0.93, 0.93, 0.92), "pcb": (0.1, 0.4, 0.2),
    "body_paint": (0.30, 0.33, 0.30), "cladding": (0.07, 0.07, 0.07), "satin_alu": (0.6, 0.61, 0.62),
    "headlight": (1, 1, 1), "headlamp_lens": (0.7, 0.75, 0.8), "taillight": (0.7, 0.05, 0.05),
    "tyre": (0.04, 0.04, 0.04), "rim": (0.2, 0.2, 0.22), "rotor": (0.4, 0.4, 0.4),
}


def to_assembly(parts, name) -> cq.Assembly:
    asm = cq.Assembly(name=name)
    for p in parts:
        c = STEP_COLOURS.get(p.material, (0.5, 0.5, 0.5))
        asm.add(p.shape, name=p.name, color=cq.Color(*c, 1.0), metadata={"material": p.material})
    return asm


def export_step(parts, path: Path, name: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    to_assembly(parts, name).export(str(path))
    print(f"  STEP  {path.relative_to(ROOT)}  ({path.stat().st_size / 1e6:.1f} MB)")


def export_meshes(parts, variant: str):
    out = MESH_DIR / variant
    out.mkdir(parents=True, exist_ok=True)
    manifest = []
    for p in parts:
        f = out / f"{p.name}.stl"
        cq.exporters.export(p.shape, str(f), tolerance=0.6, angularTolerance=0.15)
        manifest.append({"name": p.name, "material": p.material, "file": f.name})
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1))
    print(f"  MESH  {variant}: {len(manifest)} parts")


def write_bom(parts, design: str):
    DOCS.mkdir(exist_ok=True)
    f = DOCS / f"bom_{design}.csv"
    with f.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["part", "material", "len_x_mm", "len_y_mm", "len_z_mm", "volume_cm3"])
        for p in parts:
            bb = p.shape.val().BoundingBox()
            w.writerow([p.name, p.material, round(bb.xlen), round(bb.ylen), round(bb.zlen),
                        round(p.shape.val().Volume() / 1000, 1)])
    print(f"  BOM   {f.relative_to(ROOT)}")


def main():
    step_only = "--step" in sys.argv
    t0 = time.time()
    vehicle = build_vehicle()
    export_step(vehicle, STEP_DIR / "denza_b8_proxy.step", "Denza_B8_proxy")
    if not step_only:
        export_meshes(vehicle, "vehicle")

    for key, fn in DESIGNS.items():
        print(f"[{key}]")
        closed = fn(open_=False, drone_state=None)
        export_step(closed, STEP_DIR / f"{key}_rack_assembly.step", key)
        export_step(closed + vehicle, STEP_DIR / f"{key}_with_vehicle.step", f"{key}_on_B8")
        write_bom(closed, key)
        if step_only:
            continue
        export_meshes(fn(open_=False, drone_state="docked"), f"{key}_closed")
        export_meshes(fn(open_=True, drone_state="hover"), f"{key}_open")
    if not step_only:
        export_meshes(design_c(open_=True, drone_state="hover", xray=True), "C_Sentinel_xray")
    print(f"done in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
