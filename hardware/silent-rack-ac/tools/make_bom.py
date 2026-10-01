#!/usr/bin/env python3
"""
Bill of materials, cut list, sheet nesting, mass and indicative cost for the
SRA-16 Silent AC Rack - generated from rack_layout.py so it tracks the CAD.

Outputs: bom/cut_list.csv, bom/BOM.csv, bom/BOM.md
Prices are indicative AUD retail (Sept 2026) for budgeting only - get quotes.
The 3D-printed parts come from cad/print/print_report.json: run tools/make_print_pack.py first.
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
sys.path.insert(0, HERE)
import rack_layout as RL  # noqa: E402
import weldment as WM  # noqa: E402
import make_weld_pack as WP  # noqa: E402
import sheetmetal as SMP  # noqa: E402
import make_sheet_pack as MSP  # noqa: E402

SHEET = (2440.0, 1220.0)   # standard AU sheet (interior ply)
KERF = 4.0
# laser-cut sheet metal (CP-SRA16-SMP-001), indicative AUD Sept 2026 - get a quote with the DXF zip
SM_PRICE = {"blank": {("Steel sheet (Zincanneal or CR4)", 1.2): 45.0, ("Stainless 304 sheet, 2B", 1.2): 145.0},
            "cut_m": 1.10, "pierce": 0.12, "bend": 2.50, "setup": 120.0, "coat_m2": 32.0, "tray_weld": 90.0}
SM_OTHER = {"RR1": "bought as 19in rack strips (Rack)", "PD1": "weld pack PL1, from flat bar (Frame)",
            "PC1": "weld pack PL2, from flat bar (Frame)"}      # in the DXF pack as a make option only
PRT_DOC = "CP-SRA16-PRT-001"           # 3D-printed parts pack (tools/make_print_pack.py)
PRT_WASTE = 1.15                       # filament bought per kg printed: brims, purge, one failed start


def sheet_metal_costs(sm, nests):
    """Purchase rows and a per-material summary for the laser-cut parts (blanks, cutting, folding, coat)."""
    ps = [p for p in sm["parts"] if p.id not in SM_OTHER]
    rows, summ = [], OrderedDict()
    for key, sheets in nests.items():
        ids = {p.id for sh_ in sheets for p, *_ in sh_}
        if not ids - set(SM_OTHER):
            continue
        n = len(sheets)
        price = SM_PRICE["blank"].get(key, 60.0)
        rows.append(["Sheet metal", "%s %g mm, %gx%g blank" % (key[0], key[1], *MSP.BLANK), n, "blank", price,
                     "nest in cad/dxf/nest/"])
        summ[key] = {"blanks": n}
    cut_m = sum(p.qty * p.cut_length() for p in ps) / 1000.0
    pierces = sum(p.qty * p.pierces() for p in ps)
    bends = sum(p.qty * len(p.bends) for p in ps)
    rows.append(["Sheet metal", "Laser cutting: %.0f m cut, %d pierces, + setup" % (cut_m, pierces), 1, "job",
                 round(cut_m * SM_PRICE["cut_m"] + pierces * SM_PRICE["pierce"] + SM_PRICE["setup"], 2),
                 "%d parts, %d pieces" % (len(ps), sum(p.qty for p in ps))])
    rows.append(["Sheet metal", "Folding: %d bends on %d parts" % (bends, sum(1 for p in ps if p.bends)), 1, "job",
                 round(bends * SM_PRICE["bend"], 2), "R = t, K 0.33 flat blanks"])
    coat = sum(p.qty * p.area() * (2 if p.mat == "skin" else 1) for p in ps if p.mat in ("skin", "sm")) / 1e6
    rows.append(["Sheet metal", "Powder coat RAL 7035: %.1f m2 of face (skins both sides)" % coat, 1, "job",
                 round(coat * SM_PRICE["coat_m2"], 2), "coat after folding, before MLV"])
    rows.append(["Sheet metal", "DT1 drip tray: TIG-weld 4 corners, leak test, passivate", 1, "ea",
                 SM_PRICE["tray_weld"], "fabricator"])
    mass = {"steel": sum(p.qty * p.mass() for p in ps if p.mat in ("skin", "sm")),
            "tray": sum(p.qty * p.mass() for p in ps if p.mat == "ss12")}
    return rows, summ, mass, {"cut_m": cut_m, "pierces": pierces, "bends": bends, "coat_m2": coat,
                              "parts": len(ps), "pieces": sum(p.qty for p in ps)}


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
    wm = WM.build()                                   # welded frame: cut list, mass, purchase (CP-SRA16-FRM-001)
    wt = wm["totals"]
    vols = json.load(open(os.path.join(ROOT, "cad", "fusion", "SilentRackAC", "expected_volumes.json")))["volumes_mm3"]
    prt_path = os.path.join(ROOT, "cad", "print", "print_report.json")
    if not os.path.exists(prt_path):
        sys.exit("cad/print/print_report.json missing: run tools/make_print_pack.py first")
    prt = json.load(open(prt_path))

    # ------------------------------------------------------------ cut list
    cut_rows = []
    sheet_groups = defaultdict(list)          # material -> [(L, W)]
    profile_len = defaultdict(float)          # section/material -> total mm
    fab_rows, purchased = [], defaultdict(lambda: {"qty": 0, "len": 0.0, "parts": []})
    sm = SMP.build()
    nests = MSP.nest(sm)
    sm_rows, sm_summ, sm_mass, sm_tot = sheet_metal_costs(sm, nests)
    for p in parts:
        b = p["bom"]
        k = b.get("kind")
        dims = sorted(bbox(p), reverse=True)
        if SMP.DOC_NO in b.get("material", "") or "Joint cover strip" in b.get("material", "") or \
                "Door stiffener" in b.get("material", "") or "stainless, folded" in b.get("material", ""):
            continue                                  # laser-cut parts: bom/sheet_metal_parts.csv
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
        if SMP.DOC_NO.lower() in mat or "joint cover strip" in mat or "door stiffener" in mat or \
                "stainless, folded" in mat:
            continue                                  # from the sheet-metal pack below
        if PRT_DOC.lower() in mat:
            continue                                  # from the print pack below
        if "ply" in mat or "mdf" in mat:
            mass["Plywood (interior: floor, partition, shelf, boxes)"] += v * dens["ply"]
        elif "vinyl" in mat:
            mass["Mass-loaded vinyl"] += v * dens["mvl"]
        elif "acoustic foam" in mat:
            mass["Acoustic foam"] += v * dens["foam"]
        elif "steel shs" in mat or "steel flat bar" in mat or "castor pad" in mat or "rail spacer" in mat:
            continue                                  # from the weldment below
        elif "rack strip" in mat:
            mass["19in rack strips"] += v * 7.85e-6
        elif "castor" in mat:
            mass["Castors"] += 1.4
        elif "polycarbonate" in mat:
            mass["Window glazing"] += v * dens["pc"]
        else:
            mass["Seals, ducts, hardware (est.)"] += 0.0
    mass["Seals, ducts, hardware (est.)"] += 9.0
    mass["Steel skins, doors, strips, skirts (%s)" % SMP.DOC_NO] = sm_mass["steel"]
    mass["Stainless drip tray DT1 (1.2 mm)"] = sm_mass["tray"]
    mass["3D-printed hood, collar, elbow, wall spigot (%s)" % PRT_DOC] = prt["installed_mass_g"] / 1000.0
    mass["Welded steel frame, %s (weldment)" % wm["sec_shs"]] = wt["mass_weldment_kg"]
    mass["Rail spacers RS1 (SHS, bolted)"] = wt["mass_spacers_kg"]
    cabinet_kg = sum(mass.values())

    # ------------------------------------------------------------ purchase BOM (indicative AUD)
    ply_sheets = {m: s["sheets_2440x1220"] for m, s in sheet_summary.items() if "sheets_2440x1220" in s}
    foam_m2 = sum(s.get("buy_m2", 0) for m, s in sheet_summary.items() if "foam" in m.lower())
    mlv_m2 = sum(s.get("buy_m2", 0) for m, s in sheet_summary.items() if "vinyl" in m.lower())
    frame_m = wt["shs_m_welded"] + wt["shs_m_spacers"]
    h_lo = D["z_door_split"] - D["z_base0"]
    h_hi = D["z_toprail1"] - D["z_door_split"]
    door_seal_m = 2 * (2 * (D["ext_w"] + h_lo) + 2 * (D["ext_w"] + h_hi)) / 1000 * 1.1
    gasket_m = (purchased.get("EPDM closed-cell foam gasket 20x10", {"len": 0})["len"] +
                purchased.get("EPDM closed-cell foam 10x10", {"len": 0})["len"]) / 1000 * 1.2 + 2.0
    brush_m = purchased.get("25 mm nylon brush strip in alu carrier", {"len": 0})["len"] / 1000 + 0.3

    bom = []

    def add(cat, item, qty, unit, unit_aud, note=""):
        bom.append([cat, item, qty, unit, unit_aud, round(qty * unit_aud, 2), note])

    for r in sm_rows:
        add(*r)
    for m, n in ply_sheets.items():
        add("Interior ply", m + " - 2440x1220 sheet", n, "sheet", 165.0 if "18" in m else 110.0,
            "floor, partition, shelf, lined boxes")
    add("Acoustic", "Mass-loaded vinyl 5 kg/m2 (3 mm), roll", math.ceil(mlv_m2), "m2", 42.0,
        "bond inside the skins; punch D8 at the frame screws")
    add("Acoustic", "Melamine acoustic foam (FR) %g/25/20 mm panels" % D["frame"], math.ceil(foam_m2), "m2", 55.0,
        "flame-retardant; not PU egg-crate")
    add("Acoustic", "Acoustic sealant (non-hardening) 300 ml", 3, "tube", 28.0, "all panel joints")
    add("Acoustic", "Spray contact adhesive (foam/MLV)", 3, "can", 22.0, "")
    frows, _ = WP.purchase_rows(wm)
    for item, qty, unit, unit_aud, _line in frows:
        q = float(qty)
        add("Frame", item, int(q) if q.is_integer() else q, unit, float(unit_aud), "weld pack %s" % WM.DOC_NO)
    n_scr = int(math.ceil(wt["rivnuts"] * 1.05 / 10.0) * 10)
    add("Frame", "M6 x 20 flanged button-head screw, black (panel fixing)", n_scr, "ea", 0.25,
        "1.2 skin (+ strip) + 3 MLV into rivnut")
    add("Frame", "M6 x 50 bolt + washers + packers (RS1 rail spacers)", 12, "set", 0.80, "3 per spacer")
    add("Base", "Levelling castor, 75 mm wheel, 200 kg, braked, 92 mm, 4-bolt plate", 4, "ea", 38.0,
        "M8 into the tapped pads; match the 60 mm hole square")
    add("Base", "Neoprene/Sorbothane isolation mat 480x360x10", 1, "ea", 45.0, "under AC")
    add("Base", "AC retention bar + 2 toggle clamps", 1, "set", 45.0, "")
    add("Drain", "Tank bulkhead 25 mm + tundish", 1, "ea", 24.0, "")
    add("Drain", "16 mm ID clear PVC hose", 3, "m", 4.5, "fall >= 1:50 to waste")
    add("Drain", "Hose barbs / quick connects", 3, "ea", 6.0, "")
    add("Drain", "Mini condensate pump (only if no floor waste)", 1, "ea", 180.0, "optional")
    for mat, t in prt["totals"].items():
        add("Printed parts", "%s filament, 1 kg spool" % mat, int(math.ceil(t["mass_g"] * PRT_WASTE / 1000.0)), "spool",
            t["aud_kg"], "%d pieces, %.2f kg, about %.0f h: %s" % (t["pieces"], t["mass_g"] / 1000.0, t["hours"],
                                                                   t["use"].split(":")[1].split("(")[0].strip()))
    add("Printed parts", "Fixings: 6 x 4x20 pan-head, 2 x M4x25 + 4 x M5x25 button head, nylocs, washers", 1, "set",
        18.0, "hood to shelf, keepers, wall spigot")
    add("Printed parts", "Two-part epoxy 25 ml + acetone (laps), 3 x 10 closed-cell foam tape 5 m", 1, "set", 30.0,
        "hood and collar laps (epoxy), elbow lap (acetone), seals")
    add("Airflow", "Lined inlet riser + cable gland boxes (12 mm ply)", 1, "set", 0.0, "from ply offcuts")
    add("Airflow", "150 mm galvanised rigid duct, 1 m", 1, "ea", 25.0,
        "cut to %.0f mm (docs/PRINTED_PARTS.md)" % prt["duct"]["length"])
    add("Airflow", "Perforated hanger strap 1 m + screws", 1, "ea", 6.0, "holds the duct in line with the elbow")
    add("Airflow", "10 mm closed-cell duct insulation (self-adhesive)", 1, "m2", 25.0, "internal duct")
    add("Airflow", "6 mm closed-cell insulation (self-adhesive)", 1, "m2", 22.0, "printed elbow P4")
    add("Airflow", "150 mm insulated acoustic flex duct", 3, "m", 32.0, "cabinet -> window/wall vent")
    add("Airflow", "150 mm wall/window vent with backdraft flap", 1, "ea", 65.0, "")
    add("Seals", "EPDM D-profile door/panel seal (double row)", round(door_seal_m, 1), "m", 3.2, "")
    add("Seals", "EPDM closed-cell foam gasket tape 20x10 / 10x10", round(gasket_m, 1), "m", 2.8, "docking + hood")
    add("Seals", "Nylon brush strip 25 mm in alu carrier", round(brush_m, 1), "m", 18.0, "under-AC + cable entry")
    hw = purchased
    n_hinge = hw.get([m for m in hw if m.startswith("Lift-off butt hinge")][0])["qty"]
    n_latch = hw.get("Adjustable toggle latch, stainless, riveted")["qty"]
    n_rivet = sum(1 for p in sm["parts"] for h in p.holes if h["d"] == SMP.SM["rivet"] for _ in range(p.qty))
    add("Doors", "Lift-off butt hinge 100 mm, stainless, 2 mm leaves (drill to suit)", n_hinge, "ea", 14.0,
        "riveted, 3 + 3 per hinge")
    add("Doors", "Adjustable toggle (draw) latch, stainless", n_latch, "ea", 18.0, "hook in the KB1 keeper slot")
    add("Doors", "Blind rivet 4.8 x 8 stainless, dome head (pack 100)", 1, "pack", 28.0, "%d used" % n_rivet)
    add("Doors", "Pull handles 160 mm c/c, M5", 2, "ea", 12.0, "")
    add("Doors", "Polycarbonate 6 mm window panes %gx%g" % (D["win_w"] + 40, D["win_h"] + 40), 2, "ea", 9.0,
        "double glazed, drilled 8 x D5")
    add("Doors", "EPDM 10 mm window spacer frame + 8 x M4 x 35 + nyloc", 1, "set", 12.0, "clamped by WR1")
    add("Rack", "19in rack strips, 2 mm steel, %dU" % D["ru_count"], 4, "ea", 22.0,
        "EIA-310 square hole (or laser-cut RR1 with the pack)")
    add("Rack", "Cage nuts + M6 screws (pack 50)", 1, "pack", 18.0, "")
    add("Rack", "1U tool-less blanking panels", 8, "ea", 7.0, "fill all unused RU")
    add("Rack", "0U / 1U PDU 8-way 10 A", 1, "ea", 120.0, "IT load only - AC on its own GPO")
    add("Controls", "ESP32 + 3x SHT31 + IR LED + leak sensor + 2 reed switches", 1, "kit", 85.0,
        "ESPHome: temps, AC IR restart, alerts")
    add("Consumables", "Screws (M5 handles, M4 grommet), foil tape, cable ties, labels", 1, "lot", 80.0, "")
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
          "| External size | %.1f W x %.1f D x %.1f H mm |" % (D["ext_w"], D["ext_d"], D["ext_h"]),
          "| Rack space | %d RU (EIA-310, %.0f mm rail spacing) |" % (D["ru_count"], D["rail_spacing"]),
          "| Cabinet mass (empty, est.) | %.0f kg |" % cabinet_kg,
          "| + Dimplex GDC14RBA | 31.5 kg |",
          "| Materials (indicative) | AUD %s |" % format(round(total), ","), "",
          "## Sheet goods", "", "| Material | Parts | Net area m2 | Buy |", "|---|---:|---:|---|"]
    for m, s in sheet_summary.items():
        buy = "%d sheets 2440x1220" % s["sheets_2440x1220"] if "sheets_2440x1220" in s else "%.1f m2 (+15%%)" % s["buy_m2"]
        md.append("| %s | %d | %.2f | %s |" % (m, s["parts"], s["area_m2"], buy))
    md += ["", "## Laser-cut sheet metal (%s)" % SMP.DOC_NO, "",
           "Flat patterns, DXFs and nests: `docs/SHEET_METAL.md`, `cad/dxf/`, `drawings/%s.pdf`. No piece is larger "
           "than %.0f x %.0f." % (SMP.DOC_NO, D["sheet_max_l"], D["sheet_max_w"]), "",
           "| Quantity | Value |", "|---|---:|",
           "| Parts / pieces costed | %d / %d |" % (sm_tot["parts"], sm_tot["pieces"])]
    for key, s_ in sm_summ.items():
        md.append("| %s %g mm, %gx%g blanks | %d |" % (key[0], key[1], MSP.BLANK[0], MSP.BLANK[1], s_["blanks"]))
    md += ["| Cut length | %.0f m |" % sm_tot["cut_m"], "| Pierces | %d |" % sm_tot["pierces"],
           "| Bends | %d |" % sm_tot["bends"], "| Powder-coated face | %.1f m2 |" % sm_tot["coat_m2"],
           "| Mass (steel + tray) | %.1f kg |" % (sm_mass["steel"] + sm_mass["tray"]), "",
           "Also in the DXF pack, costed elsewhere: " + "; ".join("%s %s" % kv for kv in SM_OTHER.items()) + "."]
    pl_mats = OrderedDict()
    for pl in prt["plates"]:
        pl_mats[pl["material"]] = pl_mats.get(pl["material"], 0) + 1
    md += ["", "## 3D-printed parts (%s)" % PRT_DOC, "",
           "Cold-air hood, drop collar and keepers in PETG; exhaust elbow and wall spigot in ASA. Sectioned for the "
           "%s, STLs and settings in `cad/print/` and `docs/PRINTED_PARTS.md`." % prt["printer"].upper(), "",
           "| Quantity | Value |", "|---|---:|",
           "| Pieces (incl. 2 fit gauges) | %d |" % sum(t["pieces"] for t in prt["totals"].values()),
           "| Plates | %d (%s) |" % (len(prt["plates"]), ", ".join("%d %s" % (n, m) for m, n in pl_mats.items()))]
    for m, t in prt["totals"].items():
        md.append("| %s printed | %.2f kg, about %.0f h |" % (m, t["mass_g"] / 1000.0, t["hours"]))
    md += ["| Internal duct | cut to %.0f mm |" % prt["duct"]["length"]]
    md += ["", "## Frame and profiles", "",
           "The frame is welded %s: cut list, weld plan and drawings are in `docs/FRAME_WELD_PLAN.md` and "
           "`drawings/%s.pdf` (weldment %.1f kg, %d SHS bars)." % (
               wm["sec_shs"], WM.DOC_NO, wt["mass_weldment_kg"], len(wm["nest_shs"])), "",
           "| Material | Section | Total length m |", "|---|---|---:|"]
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
    print("cabinet %.0f kg, materials AUD %.0f, sheet metal %s blanks, ply sheets %s, foam %.1f m2, MLV %.1f m2, "
          "frame %.1f m" % (cabinet_kg, total, {"%s %g" % k: v["blanks"] for k, v in sm_summ.items()}, ply_sheets,
                            foam_m2, mlv_m2, frame_m))


if __name__ == "__main__":
    main()
