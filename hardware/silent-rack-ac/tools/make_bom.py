#!/usr/bin/env python3
"""
Bill of materials, cut list, sheet nesting, mass and indicative cost for the
SRA-16 Silent AC Rack - generated from rack_layout.py so it tracks the CAD.

Outputs: bom/cut_list.csv, bom/BOM.csv, bom/BOM.md
Prices are indicative AUD retail (Sept 2026) for budgeting only - get quotes.
"""
import csv
import json
import math
import os
import sys
from collections import OrderedDict, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "cad", "fusion", "SilentRackAC"))
import rack_layout as RL  # noqa: E402

SHEET = (2440.0, 1220.0)   # standard AU sheet
KERF = 4.0


def bbox(part):
    mins = [min(RL.prim_bbox(q)[0][i] for q in part["add"]) for i in range(3)]
    maxs = [max(RL.prim_bbox(q)[1][i] for q in part["add"]) for i in range(3)]
    return [maxs[i] - mins[i] for i in range(3)]


def shelf_nest(rects, sheet=SHEET, kerf=KERF):
    """Very simple shelf (guillotine) nesting -> number of sheets used."""
    W, H = sheet
    items = []
    for (l, w) in rects:
        a, b = max(l, w), min(l, w)
        if a > W:            # cannot fit long side along sheet length
            raise ValueError("part %gx%g larger than sheet" % (l, w))
        items.append((a, b))
    items.sort(key=lambda r: (-r[1], -r[0]))
    sheets = []              # each: list of shelves [y, height, x_used]
    for a, b in items:
        placed = False
        for sh in sheets:
            for shelf in sh["shelves"]:
                if b <= shelf[1] and shelf[2] + a <= W:
                    shelf[2] += a + kerf
                    placed = True
                    break
            if not placed and sh["y"] + b <= H:
                sh["shelves"].append([sh["y"], b, a + kerf])
                sh["y"] += b + kerf
                placed = True
            if placed:
                break
        if not placed:
            sheets.append({"y": b + kerf, "shelves": [[0, b, a + kerf]]})
    return len(sheets)


def main():
    parts, D = RL.build_parts()
    vols = json.load(open(os.path.join(ROOT, "cad", "fusion", "SilentRackAC", "expected_volumes.json")))["volumes_mm3"]

    # ------------------------------------------------------------ cut list
    cut_rows = []
    sheet_groups = defaultdict(list)          # material -> [(L, W)]
    profile_len = defaultdict(float)          # section/material -> total mm
    fab_rows, purchased = [], defaultdict(lambda: {"qty": 0, "len": 0.0, "parts": []})
    for p in parts:
        b = p["bom"]
        k = b.get("kind")
        dims = sorted(bbox(p), reverse=True)
        if k == "sheet":
            L, Wd, T = dims
            note = "cut-outs" if p["cut"] else ""
            cut_rows.append(["sheet", p["name"], b["material"], round(b.get("t", T), 1), round(L, 1), round(Wd, 1), 1, note])
            sheet_groups[b["material"]].append((L, Wd))
        elif k == "profile":
            L = dims[0]
            cut_rows.append(["profile", p["name"], b["material"], b["section"], round(L, 1), "", 1, ""])
            profile_len[(b["material"], b["section"])] += L
        elif k == "fab":
            fab_rows.append([p["name"], b["material"], "%.0f x %.0f x %.0f" % tuple(dims)])
        elif k == "purchased":
            g = purchased[b["material"]]
            g["qty"] += 1
            g["len"] += dims[0]
            g["parts"].append(p["name"])

    os.makedirs(os.path.join(ROOT, "bom"), exist_ok=True)
    with open(os.path.join(ROOT, "bom", "cut_list.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["type", "part", "material", "thickness_or_section", "length_mm", "width_mm", "qty", "notes"])
        for r in sorted(cut_rows, key=lambda r: (r[0], r[2], -r[4])):
            w.writerow(r)

    # ------------------------------------------------------------ nesting + areas
    sheet_summary = OrderedDict()
    for mat, rects in sheet_groups.items():
        area = sum(l * w for l, w in rects) / 1e6
        if "ply" in mat.lower():
            n = shelf_nest(rects)
            sheet_summary[mat] = {"parts": len(rects), "area_m2": round(area, 2), "sheets_2440x1220": n}
        else:
            sheet_summary[mat] = {"parts": len(rects), "area_m2": round(area, 2), "buy_m2": round(area * 1.15, 1)}

    # ------------------------------------------------------------ mass
    dens = {"ply": 680e-9, "mvl": 1667e-9, "foam": 11e-9, "pp": 900e-9, "pc": 1200e-9}
    mass = defaultdict(float)
    for p in parts:
        v = vols.get(p["name"], 0.0)
        mat = p["bom"].get("material", "").lower()
        g = p["group"]
        if g.startswith("AC ") or g.startswith("Example IT"):
            continue
        if "ply" in mat or "mdf" in mat:
            mass["Plywood"] += v * dens["ply"]
        elif "vinyl" in mat:
            mass["Mass-loaded vinyl"] += v * dens["mvl"]
        elif "foam 40" in mat or "foam 25" in mat or "foam 20" in mat:
            mass["Acoustic foam"] += v * dens["foam"]
        elif "4040" in mat:
            mass["Aluminium frame (1.5 kg/m)"] += max(bbox(p)) / 1000 * 1.5
        elif "angle" in mat:
            mass["Angle cleats (0.21 kg/m)"] += max(bbox(p)) / 1000 * 0.21
        elif "rail spacer" in mat:
            mass["Rail spacers (hollow 20x40, 0.6 kg/m)"] += max(bbox(p)) / 1000 * 0.6
        elif "stainless" in mat:
            mass["Stainless drip tray (1.2 mm)"] += v * 7.9e-6 * (1.2 / 2.0)
        elif "rack strip" in mat:
            mass["19in rack strips"] += v * 7.85e-6
        elif "castor" in mat:
            mass["Castors"] += 1.4
        elif "polycarbonate" in mat:
            mass["Window glazing"] += v * dens["pc"]
        elif "pp sheet" in mat:
            mass["Cold hood"] += 1.6
        else:
            mass["Seals, ducts, hardware (est.)"] += 0.0
    mass["Seals, ducts, hardware (est.)"] += 9.0
    cabinet_kg = sum(mass.values())

    # ------------------------------------------------------------ purchase BOM (indicative AUD)
    ply_sheets = {m: s["sheets_2440x1220"] for m, s in sheet_summary.items() if "sheets_2440x1220" in s}
    foam_m2 = sum(s.get("buy_m2", 0) for m, s in sheet_summary.items() if "foam" in m.lower())
    mlv_m2 = sum(s.get("buy_m2", 0) for m, s in sheet_summary.items() if "vinyl" in m.lower())
    frame_m = sum(v for (m, sct), v in profile_len.items() if "4040" in m) / 1000
    angle_m = sum(v for (m, sct), v in profile_len.items() if "angle" in m) / 1000
    spacer_m = sum(v for (m, sct), v in profile_len.items() if "rail spacer" in m) / 1000
    h_lo = D["z_door_split"] - D["z_base0"]
    h_hi = D["z_toprail1"] - D["z_door_split"]
    door_seal_m = 2 * (2 * (D["ext_w"] + h_lo) + 2 * (D["ext_w"] + h_hi)) / 1000 * 1.1
    gasket_m = (purchased.get("EPDM closed-cell foam gasket 20x10", {"len": 0})["len"] +
                purchased.get("EPDM closed-cell foam 10x10", {"len": 0})["len"]) / 1000 * 1.2 + 2.0
    brush_m = purchased.get("25 mm nylon brush strip in alu carrier", {"len": 0})["len"] / 1000 + 0.3

    bom = []

    def add(cat, item, qty, unit, unit_aud, note=""):
        bom.append([cat, item, qty, unit, unit_aud, round(qty * unit_aud, 2), note])

    for m, n in ply_sheets.items():
        add("Panels", m + " - 2440x1220 sheet", n, "sheet", 165.0 if "18" in m else (150.0 if "15" in m else 110.0),
            "shelf-nested, %.0f mm kerf" % KERF)
    add("Acoustic", "Mass-loaded vinyl 5 kg/m2 (3 mm), roll", math.ceil(mlv_m2), "m2", 42.0, "bond to ply inside face")
    add("Acoustic", "Melamine acoustic foam (FR) 40/25/20 mm panels", math.ceil(foam_m2), "m2", 55.0,
        "flame-retardant; not PU egg-crate")
    add("Acoustic", "Acoustic sealant (non-hardening) 300 ml", 3, "tube", 28.0, "all panel joints")
    add("Acoustic", "Spray contact adhesive (foam/MLV)", 3, "can", 22.0, "")
    add("Frame", "Aluminium 4040 T-slot profile, cut to length", round(frame_m, 1), "m", 21.0,
        "or weld 40x40x2 SHS for production")
    add("Frame", "4040 corner brackets + M8 T-nuts/bolts", 80, "set", 2.2, "2 per member end")
    add("Frame", "M5 T-nuts + button-head screws (panel fixing)", 160, "set", 0.45, "")
    add("Frame", "Aluminium angle 20x20x2 (cleats)", round(angle_m + 0.5, 1), "m", 6.5, "")
    add("Frame", "Aluminium box 20x40 (rail spacers / air dams)", round(spacer_m + 0.4, 1), "m", 12.0, "")
    add("Base", "Levelling castor 100 mm, 200 kg, braked", 4, "ea", 38.0, "castor + retractable foot")
    add("Base", "Stainless drip tray 1.2 mm 304 (fabricated)", 1, "ea", 220.0, "full bay floor, 25 upstand")
    add("Base", "Perforated steel skirts 1.5 mm (set of 4, powder coat)", 1, "set", 140.0, "plinth intake")
    add("Base", "Neoprene/Sorbothane isolation mat 480x360x10", 1, "ea", 45.0, "under AC")
    add("Base", "AC retention bar + 2 toggle clamps", 1, "set", 45.0, "")
    add("Drain", "Tank bulkhead 25 mm + tundish", 1, "ea", 24.0, "")
    add("Drain", "16 mm ID clear PVC hose", 3, "m", 4.5, "fall >= 1:50 to waste")
    add("Drain", "Hose barbs / quick connects", 3, "ea", 6.0, "")
    add("Drain", "Mini condensate pump (only if no floor waste)", 1, "ea", 180.0, "optional")
    add("Airflow", "Cold-air hood, 6 mm PP (fab) with drop collar", 1, "ea", 90.0, "or 3D-print PETG")
    add("Airflow", "Lined inlet riser + cable gland boxes (12 mm ply)", 1, "set", 0.0, "from ply offcuts")
    add("Airflow", "150 mm rigid 90deg elbow + 0.6 m duct + flanged wall spigot", 1, "set", 85.0, "")
    add("Airflow", "10 mm closed-cell duct insulation (self-adhesive)", 2, "m2", 25.0, "elbow + duct")
    add("Airflow", "150 mm insulated acoustic flex duct", 3, "m", 32.0, "cabinet -> window/wall vent")
    add("Airflow", "150 mm wall/window vent with backdraft flap", 1, "ea", 65.0, "")
    add("Seals", "EPDM D-profile door/panel seal (double row)", round(door_seal_m, 1), "m", 3.2, "")
    add("Seals", "EPDM closed-cell foam gasket tape 20x10 / 10x10", round(gasket_m, 1), "m", 2.8, "docking + hood")
    add("Seals", "Nylon brush strip 25 mm in alu carrier", round(brush_m, 1), "m", 18.0, "under-AC + cable entry")
    add("Doors", "Lift-off hinges, heavy duty", 6, "ea", 14.0, "3 per door")
    add("Doors", "Compression cam latches (keyed)", 4, "ea", 24.0, "2 per door")
    add("Doors", "Pull handles 160 mm", 2, "ea", 12.0, "")
    add("Doors", "Polycarbonate 6 mm window panes 140x200", 2, "ea", 9.0, "double glazed")
    add("Rack", "19in rack strips, 2 mm steel, %dU" % D["ru_count"], 4, "ea", 22.0, "EIA-310 square hole")
    add("Rack", "Cage nuts + M6 screws (pack 50)", 1, "pack", 18.0, "")
    add("Rack", "1U tool-less blanking panels", 8, "ea", 7.0, "fill all unused RU")
    add("Rack", "0U / 1U PDU 8-way 10 A", 1, "ea", 120.0, "IT load only - AC on its own GPO")
    add("Controls", "ESP32 + 3x SHT31 + IR LED + leak sensor + 2 reed switches", 1, "kit", 85.0,
        "ESPHome: temps, AC IR restart, alerts")
    add("Consumables", "Screws, foil tape, cable ties, labels", 1, "lot", 80.0, "")
    total = sum(r[5] for r in bom)
    with open(os.path.join(ROOT, "bom", "BOM.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["category", "item", "qty", "unit", "unit_AUD_indicative", "line_AUD", "notes"])
        w.writerows(bom)
        w.writerow(["TOTAL", "", "", "", "", round(total, 2), "materials only, excl. AC, IT, GST, labour"])

    # ------------------------------------------------------------ markdown summary
    md = ["# SRA-16 - BOM summary (generated)", "",
          "Generated by `tools/make_bom.py` from `rack_layout.py` v%s. Prices are **indicative AUD retail "
          "(Sept 2026), budgeting only** - get supplier quotes." % RL.VERSION, "",
          "## Headline", "",
          "| Item | Value |", "|---|---|",
          "| External size | %.0f W x %.0f D x %.0f H mm |" % (D["ext_w"], D["ext_d"], D["ext_h"]),
          "| Rack space | %d RU (EIA-310, %.0f mm rail spacing) |" % (D["ru_count"], D["rail_spacing"]),
          "| Cabinet mass (empty, est.) | %.0f kg |" % cabinet_kg,
          "| + Dimplex GDC14RBA | 31.5 kg |",
          "| Materials (indicative) | AUD %s |" % format(round(total), ","), "",
          "## Sheet goods", "", "| Material | Parts | Net area m2 | Buy |", "|---|---:|---:|---|"]
    for m, s in sheet_summary.items():
        buy = "%d sheets 2440x1220" % s["sheets_2440x1220"] if "sheets_2440x1220" in s else "%.1f m2 (+15%%)" % s["buy_m2"]
        md.append("| %s | %d | %.2f | %s |" % (m, s["parts"], s["area_m2"], buy))
    md += ["", "## Frame and profiles", "", "| Material | Section | Total length m |", "|---|---|---:|"]
    for (m, sct), L in profile_len.items():
        md.append("| %s | %s | %.2f |" % (m, sct, L / 1000))
    md += ["", "## Fabricated parts", "", "| Part | Spec | Envelope mm |", "|---|---|---|"]
    for r in fab_rows:
        md.append("| %s | %s | %s |" % tuple(r))
    md += ["", "## Mass breakdown (estimate)", "", "| Group | kg |", "|---|---:|"]
    for k, v in sorted(mass.items(), key=lambda kv: -kv[1]):
        md.append("| %s | %.1f |" % (k, v))
    md += ["| **Total cabinet (empty)** | **%.0f** |" % cabinet_kg, "",
           "## Purchase list", "", "| Category | Item | Qty | Unit | AUD/unit | AUD |", "|---|---|---:|---|---:|---:|"]
    for r in bom:
        md.append("| %s | %s | %s | %s | %.2f | %.0f |" % (r[0], r[1], r[2], r[3], r[4], r[5]))
    md.append("| **Total** | materials, excl. AC/IT/GST/labour | | | | **%s** |" % format(round(total), ","))
    md += ["", "Full part-by-part cut list: `bom/cut_list.csv`."]
    with open(os.path.join(ROOT, "bom", "BOM.md"), "w") as fh:
        fh.write("\n".join(md) + "\n")
    print("cabinet %.0f kg, materials AUD %.0f, ply sheets %s, foam %.1f m2, MLV %.1f m2, frame %.1f m"
          % (cabinet_kg, total, ply_sheets, foam_m2, mlv_m2, frame_m))


if __name__ == "__main__":
    main()
