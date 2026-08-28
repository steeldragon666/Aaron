#!/usr/bin/env node
/* Container Workshop rev C — RFQ / procurement brief generator.
 * Emits Container-Workshop_RFQ-Brief_RevC.docx for issue to prefabrication
 * builders and suppliers. Reads bom_summary.json produced by generate_bom.py.
 * Images view_*.jpeg are the six rendered views exported from the design page.
 */
const fs = require("fs");
const path = require("path");
const {
  AlignmentType, BorderStyle, Document, Footer, Header, HeadingLevel, ImageRun,
  LevelFormat, PageBreak, PageNumber, Packer, Paragraph, ShadingType, Table,
  TableCell, TableRow, TextRun, VerticalAlign, WidthType, TabStopType,
} = require("docx");

const HERE = __dirname;
const SUMMARY = JSON.parse(fs.readFileSync(path.join(HERE, "bom_summary.json"), "utf8"));
const IMG_DIR = process.env.VIEW_DIR ||
  (fs.existsSync(path.join(HERE, "views")) ? path.join(HERE, "views") : HERE);

const INK = "1A1917", ACCENT = "A8402A", MUT = "57534E", BAND = "EDEBE7",
  HEADBG = "1F2937", ZEBRA = "F6F5F2", WARNBG = "F7EEDC";
const CW = 9638; // usable width, DXA (A4, 2 cm margins)
const FONT = { ascii: "Calibri", hAnsi: "Calibri", eastAsia: "Microsoft YaHei" };

const IMGS = {
  exterior: ["view_00.jpeg", 1400, 894],
  leanTo: ["view_01.jpeg", 1400, 797],
  roofPlan: ["view_02.jpeg", 1400, 1307],
  frontElev: ["view_03.jpeg", 1400, 778],
  structure: ["view_04.jpeg", 1400, 894],
  clearance: ["view_05.jpeg", 1400, 894],
};

// ------------------------------------------------------------------ helpers
const run = (text, o = {}) => new TextRun({ text, font: FONT, size: o.size || 20, bold: o.bold, italics: o.italics, color: o.color || INK, ...o.extra });
const p = (children, o = {}) => new Paragraph({
  children: Array.isArray(children) ? children : [run(children, o.runOpts || {})],
  spacing: { after: o.after ?? 120, before: o.before ?? 0, line: o.line ?? 264 },
  alignment: o.align, ...o.extra,
});
const bullet = (text, o = {}) => new Paragraph({
  children: Array.isArray(text) ? text : [run(text, o.runOpts || {})],
  numbering: { reference: "bullets", level: 0 },
  spacing: { after: 60, line: 264 },
});
let sectionNo = 0;
const h1 = (en, zh) => {
  sectionNo += 1;
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 140 },
    children: [
      run(`${sectionNo}`, { size: 26, bold: true, color: ACCENT }),
      run(`   ${en}`, { size: 26, bold: true, color: INK }),
      zh ? run(`   ${zh}`, { size: 22, bold: true, color: MUT }) : null,
    ].filter(Boolean),
  });
};
const hA = (en, zh) => new Paragraph({
  heading: HeadingLevel.HEADING_1,
  spacing: { before: 360, after: 140 },
  children: [run(en, { size: 26, bold: true, color: INK }), zh ? run(`   ${zh}`, { size: 22, bold: true, color: MUT }) : null].filter(Boolean),
});
const h2 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_2,
  spacing: { before: 220, after: 100 },
  children: [run(text, { size: 22, bold: true, color: ACCENT })],
});
const caption = (text) => p([run(text, { size: 16, italics: true, color: MUT })], { after: 200 });

const thin = { style: BorderStyle.SINGLE, size: 4, color: "C4BDB4" };
const tableBorders = { top: thin, bottom: thin, left: thin, right: thin, insideHorizontal: thin, insideVertical: thin };

function cellPara(content, o = {}) {
  const runs = Array.isArray(content) ? content : [run(String(content), { size: o.size || 18, bold: o.bold, color: o.color })];
  return new Paragraph({ children: runs, spacing: { after: 20, line: 240 }, alignment: o.align });
}
function tc(content, width, o = {}) {
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    verticalAlign: VerticalAlign.TOP,
    shading: o.fill ? { type: ShadingType.CLEAR, fill: o.fill } : undefined,
    margins: { top: 57, bottom: 57, left: 85, right: 85 },
    children: Array.isArray(content) && content[0] instanceof Paragraph ? content : [cellPara(content, o)],
  });
}
function mkTable(headers, rows, widths, o = {}) {
  const headRow = new TableRow({
    tableHeader: true,
    children: headers.map((h, i) => tc([cellPara(h, { bold: true, color: "FFFFFF", size: 17 })], widths[i], { fill: HEADBG })),
  });
  const bodyRows = rows.map((r, ri) => new TableRow({
    children: r.map((c, i) => tc(c, widths[i], { fill: o.zebra && ri % 2 ? ZEBRA : undefined, size: o.size })),
  }));
  return new Table({ columnWidths: widths, width: { size: CW, type: WidthType.DXA }, borders: tableBorders, rows: [headRow, ...bodyRows] });
}
function kvTable(pairs, wKey = 2500) {
  const widths = [wKey, CW - wKey];
  return new Table({
    columnWidths: widths, width: { size: CW, type: WidthType.DXA }, borders: tableBorders,
    rows: pairs.map(([k, v]) => new TableRow({
      children: [tc([cellPara(k, { bold: true })], widths[0], { fill: BAND }), tc(String(v), widths[1])],
    })),
  });
}
function box(title, text, fill = WARNBG) {
  return new Table({
    columnWidths: [CW], width: { size: CW, type: WidthType.DXA }, borders: tableBorders,
    rows: [new TableRow({
      children: [tc([
        cellPara(title, { bold: true, size: 19, color: "8A5A00" }),
        ...(Array.isArray(text) ? text : [text]).map((t) => cellPara(t, { size: 18 })),
      ], CW, { fill })],
    })],
  });
}
function img(key, widthPx = 610) {
  const [file, w, h] = IMGS[key];
  const data = fs.readFileSync(path.join(IMG_DIR, file));
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 120, after: 40 },
    children: [new ImageRun({ type: "jpg", data, transformation: { width: widthPx, height: Math.round((widthPx * h) / w) } })],
  });
}
const rule = () => new Paragraph({
  spacing: { before: 60, after: 160 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: ACCENT } },
  children: [],
});

// ------------------------------------------------------------------ content
const cover = [
  p([run("REQUEST FOR QUOTATION  ·  询价书", { size: 18, bold: true, color: ACCENT, extra: { characterSpacing: 40 } })], { before: 120, after: 120 }),
  new Paragraph({ spacing: { after: 40 }, children: [run("CONTAINER WORKSHOP", { size: 56, bold: true, color: INK })] }),
  p([run("集装箱车间 — 预制建筑构件、设备与系统全套采购", { size: 24, color: MUT })], { after: 80 }),
  rule(),
  p([run("A workshop built from three 40 ft high-cube containers meeting at the corners, under a 10.0° portal-framed PIR envelope, with a 2 t overhead crane, four in-ground 6 t vehicle lifts, a 52.08 kW roof array feeding an external battery and charging bay, and the whole building running on sensors with no wall switches.", { size: 20, color: MUT })], { after: 140 }),
  img("exterior", 425),
  caption("V01 — exterior render from the parametric master model: array on both slopes, canopies, service-reel hood, plant lean-to at right."),
  kvTable([
    ["RFQ number", SUMMARY.rfq],
    ["Design revision", "C — 2026-08-24 · status: for engineering (not certified)"],
    ["Issued", "28 August 2026"],
    ["Clarification questions close", "11 September 2026"],
    ["Quotations due", "25 September 2026, 17:00 AEST"],
    ["Buyer", "The Carbon Project (Australia)"],
    ["Contact (sole channel)", "aaron@carbonproject.com.au"],
    ["Quotation basis", "Itemised rates FOB nominated China port, USD, plus freight and insurance lines to CIF Port of Brisbane, Australia"],
    ["Validity required", "90 days from submission"],
  ]),
  p([], { after: 40 }),
  mkTable(
    ["Envelope", "Structure", "Plant", "Bill of materials"],
    [[
      [cellPara("17.068 × 14.630 m"), cellPara("ridge 8.432 m · 607 m² PIR", { color: MUT, size: 16 })],
      [cellPara("20.7 t steel"), cellPara("6 portal frames · 17.420 m span", { color: MUT, size: 16 })],
      [cellPara("2 t crane · 4 × 6 t lifts"), cellPara("52.08 kW PV · 2 × 22 kW EV", { color: MUT, size: 16 })],
      [cellPara("244 items · 25 groups"), cellPara("nominal cargo ≈ 74 t incl. containers", { color: MUT, size: 16 })],
    ]],
    [2410, 2410, 2410, 2408],
  ),
  p([], { after: 60 }),
  p([run("This brief and the accompanying BOM workbook contain a Chinese summary and headings for convenience. If there is any inconsistency, the English text governs.  本文件含中文摘要，仅供参考；如有歧义，以英文版本为准。", { size: 17, color: MUT, italics: true })]),
];

const s1 = [
  h1("Invitation", "邀请函"),
  p("The Carbon Project invites quotations from prefabricated-building manufacturers and equipment suppliers for the complete supply of the Container Workshop: a parametrically engineered workshop building to be erected in Australia. The package covers the three ISO containers and their modification, all structural and secondary steel, the insulated envelope and doors, a 2 t overhead crane, four in-ground 6 t vehicle lifts with hydraulic plant, a 52.08 kW solar array with battery storage and EV charging, and a fully sensor-driven electrical, lighting, control and security installation."),
  p("Tenderers may quote the full kit (preferred) or one or more of the packages defined in Section 3. All rates are entered in the accompanying BOM workbook, which contains 244 items in 25 groups. Rate and amount columns arrive empty by design: no prices are invented anywhere in this design package — they come from supplier quotes."),
  p([run("致：预制建筑制造商及设备供应商 — 澳大利亚 The Carbon Project 现就“集装箱车间”项目进行国际询价。项目由三个 40 英尺高柜集装箱与门式钢架保温围护结构组成，含 2 吨桥式起重机、四台 6 吨地埋式举升机、52.08 kW 屋顶光伏及储能与充电系统、以及全传感器化楼宇控制系统。请按随附 BOM 工作簿（Excel，共 244 项、25 组）逐项报价；可整套报价（优先）或按第 3 节的分包范围报价。报价截止：2026 年 9 月 25 日。所有技术要求以英文版本为准。联系邮箱：aaron@carbonproject.com.au。", { size: 19 })]),
];

const s2 = [
  h1("The building", "项目概述"),
  p("Three 40 ft high-cube containers meet at both rear corners to enclose a clear 12.192 × 12.192 m workshop bay. A portal-framed envelope spans 17.420 m over containers and bay together: six haunched 360 UB 44.7 frames at 2.960 m centres, 10.0° roof pitch, eave 6.896 m, ridge 8.432 m, clad in 100 mm PIR sandwich panel (607 m²). The container tops carry a 3.001 m storage deck served by the crane; the container sides facing the bay are cut into 15 openings of 2.288 × 2.500 m forming 13 workbench bays and a sealed server compartment."),
  p("Principal dimensions are computed, not drawn: one parameter file drives the CAD master, the dimension schedule and the BOM, so the three cannot disagree. The full schedule is at Annex B; headline values below."),
  mkTable(["Element", "Value", "Governing note"], [
    ["Clear workshop bay", "12.192 × 12.192 m", "containers meet at both rear corners"],
    ["Building envelope", "17.068 × 14.630 m", "footprint 249.7 m²; ridge 8.432 m"],
    ["Portal frames", "6 no. at 2.960 m", "span 17.420 m, 360 UB 44.7, haunched"],
    ["Overhead crane", "2 000 kg, span 17.420 m", "hook 5.154 m; 1.914 m reach over each container top"],
    ["Vehicle lifts", "4 × 6 t, 3.0 m stroke", "in-ground 3-stage cassettes on a 4.0 × 3.5 m grid"],
    ["Solar array", "52.08 kW — 84 × 620 W", "7 rows × 6 columns per slope; strings 6 × 14"],
    ["Building control", "61 sensor points, 15 types", "9 cameras, 4 readers, 10 external luminaires — no wall switches"],
    ["Connected load", "84.9 kW vs 71.9 kVA supply", "dynamic load management is mandatory"],
  ], [2600, 2700, 4338], { zebra: true }),
  p([], { after: 100 }),
  img("structure", 620),
  caption("V05 — structure with cladding hidden: 6 haunched portals, 15 purlin lines, crane runways and bridge, goalpost frames in the container openings, deck walkway and racking."),
  box("Design status — read before pricing", [
    "Revision C is coordinated, dimensionally consistent and buildable, but it is NOT a certified design. It is the input to engineering, not the output. Australian certification runs against the successful tenderer's shop drawings and data (Section 7).",
    "Site wind region, terrain category and soil classification are not yet confirmed. Wind-sensitive items (envelope, roller door, PV mounting, structure) are quoted against the stated sections and quantities; if site data changes member sizes, the change is re-priced mechanically from your per-tonne and per-m² rates. Quantities may be adjusted ±10 % at order under the quoted rates.",
    "Two engineering decisions to be aware of: the portal frames sit 4.0 m above the container tops (not 3.0 m) so that the crane, the 3 m lift stroke and the container-top racking can coexist; and the roof physically holds 52.08 kW of the requested 50–100 kW of solar (ceiling 60.9 kW) — expansion beyond that needs a future carport or ground mount, which is excluded from this RFQ.",
  ]),
];

const s3 = [
  h1("Scope of supply", "供货范围"),
  p("The BOM workbook is the definitive scope list. Every line carries a scope code: CN (base scope — quote), CN-OPT (priced option) or LOCAL (Australian supply and site works — information only, do not quote). Lines are grouped A–Y; packages map to groups as follows."),
  mkTable(["Pkg", "BOM groups", "Content"], [
    ["P1", "A B C D E F J K R", "Containers and modification; portal, secondary, bracing and crane-runway steel (20.7 t scheduled); container-top deck, stair and edge protection; racking; plant lean-to"],
    ["P2", "H I", "607 m² of 100 mm PIR envelope, flashings and rainwater; 4.0 × 4.0 m insulated roller shutter; 2 personnel doorsets; canopies"],
    ["P3", "G", "2 000 kg single-girder EOT crane, 17.420 m span, hoist, radio + pendant controls (hold-to-run)"],
    ["P4", "L M N O*", "4 × 6 t in-ground 3-stage telescopic lifts with cast-in pit boxes; 15 kW / 100 L·min⁻¹ HPU; bunded plant-sump fit-out; trench drains (*O-01, O-02 only)"],
    ["P5", "P Q", "84 × 620 W CEC-listed modules; mounting for PIR roof; 2 × 25 kVA AS/NZS 4777.2 inverters; 2 LFP battery cabinets with provision to 100 kWh; 2 × 22 kW EV chargers"],
    ["P6", "S T U", "Main switchboard with dynamic load management; internal, external (10, sensor-driven) and emergency lighting; 61-point sensor layer; CCTV, access control, network"],
    ["P7", "V W", "Five-reel service bank and hood interface; air/water/oil reticulation; 13 workbenches and tool boards; server rack"],
    ["—", "X", "Export packing, marking, lashing — applies to every package pro-rata"],
    ["—", "Y", "Local Australian works (concrete, erection, licensed electrical, certification) — excluded, listed for context"],
  ], [700, 1750, 7188], { zebra: true }),
  h2("Priced options (quote separately, excluded from base total)"),
  bullet("OP-1 — Erection supervision: two supervisors for six weeks on site in Australia (rates, mobilisation, accommodation basis)."),
  bullet("OP-2 — Commissioning support for crane, lifts, hydraulics and controls: two weeks."),
  bullet("OP-3 — Rotary-screw compressor package 11 kW with dryer and receiver (BOM V-08)."),
  bullet("OP-4 — Spare PV modules, same batch (BOM P-11)."),
  bullet("OP-5 — Bench vices (BOM W-03)."),
  bullet("OP-6 — Inverter warranty extension to 10 years."),
];

const s4 = [
  h1("Technical requirements", "技术要求"),
  h2("P1 — Containers, structure, deck"),
  bullet("Containers: one-trip 40 ft high-cube to ISO 668 1AAA, CSC-plated, surveyed top side rails (they carry the deck bearers). The three containers double as shipper-owned freight containers for delivery of this kit."),
  bullet([run("Steel sections are Australian UB/UC and hollow sections to AS/NZS 3679.1 grade 300 / AS/NZS 1163. Substitution by GB/T sections or welded equivalents is "), run("not accepted without written approval", { bold: true }), run(" supported by a documented section-property comparison (A, Ix, Zx, ry, mass) in the deviation register.")]),
  bullet("Fabrication to AS/NZS 5131 construction category CC2; welding to AS/NZS 1554.1 category SP (ISO 3834-2 systems accepted with qualified WPS/PQR mapping); bolts AS/NZS 1252; hot-dip galvanizing to AS/NZS 4680, site touch-up system included."),
  bullet("Container modification: 15 openings 2.288 × 2.500 m (85.8 m² of stressed skin) each reinstated with a welded 150 PFC goalpost frame; cut edges dressed, primed and trimmed. Dimensional record per opening."),
  bullet("Container-top deck: 33 bearers at 1 219 mm centres spanning onto the top side rails, design UDL 2.5 kPa; grating surfaces; edge kerb; guardrail, gate and AS 1657 stair (2 × 8 risers at 188/216 mm). Maximum stored-item envelope 1.903 m — supply the height gauge."),
  bullet("Crane runway: 310 UB 46.2 runway beams on column corbels, machined 50 × 30 rail, stops and buffers; erected alignment tolerances per AS 1418.18 stated on the shop drawings."),
  h2("P2 — Envelope and doors"),
  bullet("100 mm PIR sandwich panel, steel faces nominal 0.5/0.4 BMT, colour to be advised at order; documented fire performance: FM 4880/4881 approval or AS 1530.4 full-scale test evidence — mandatory for Australian building approval of a Class 8 building."),
  bullet("Envelope completeness: ridge, barge, corner, base flashings; high-capacity eaves gutters and 4 downpipes; profile closures and sealed laps. Target U-value ≤ 0.25 W/m²K."),
  bullet("Roller shutter 4.0 × 4.0 m, insulated, motorised 415 V with manual haul-chain backup, monitored safety edge and photocells; wind rating to the site category (to be confirmed — state the rating offered)."),
  bullet("Personnel doorsets with mechanical lever egress. Egress must never depend on power or credentials — electric strikes act on entry only."),
  h2("P3 — Overhead crane"),
  img("clearance", 560),
  caption("V06 — clearance envelopes: four 3 m lift envelopes, a raised vehicle, the crane hook coverage plane at 5.154 m, and the 1.903 m stored-item envelope on the deck."),
  bullet("Single-girder EOT, SWL 2 000 kg, span 17.420 m, duty FEM/ISO M5, dual-speed hoist and travels; girder deflection ≤ span/600 (29 mm; design value 26 mm)."),
  bullet("Hook height 5.154 m with rail top-of-steel at 5.254 m. The governing obstruction is the eave-haunch soffit at 6.082 m — confirm your crane's headroom against it, not against the rafter."),
  bullet("Controls: radio remote plus wired pendant backup, both hold-to-run (life-safety requirement); overload limiter, height and travel limits. 125 % load test is performed in Australia at commissioning — supply the test procedure and certificates template."),
  h2("P4 — Vehicle lifts and hydraulics"),
  bullet("Four in-ground telescopic cassettes, 6 000 kg each, 3 stages (bores 180/140/100 mm), 3.0 m stroke, flush covers, removable cross beams, on a 4.0 × 3.5 m grid. Stage-3 buckling safety factor 4.57 at full extension governs the top-stage bore — pressure alone is not the sizing case."),
  bullet("Hydraulics to ISO 4413: 15 kW HPU at 100 L/min (full lift of all four in 117 s; swept volume 194.8 L), proportional valve sections, hose-burst check valves at every cylinder port."),
  bullet([run("Nine independent safety barriers including a mechanical rack-and-pawl lock per lift: "), run("proportional valves control the load, they never hold it.", { bold: true }), run(" Hold-to-run controls with E-stop and key isolation at each lift.")]),
  bullet("Plant sump 2.4 × 1.6 × 1.8 m supplied as a bunded steel liner for casting-in (holds 6 912 L against 330 L required); trafficable flush covers; mechanical ventilation 83 m³/h (12 ACH); oil-in-water sensor interlocked so the sump pump cannot discharge oil; confined-space access hardware."),
  bullet([run("Design registration: ", { bold: true }), run("vehicle hoists are registrable plant in Australia. The full design dossier (calculations, FMEA, drawings, test reports to AS/NZS 1418.9) is a contract deliverable due 6 weeks from order — pit concrete cannot be poured until the registration pathway is resolved, so this dossier sits on the project critical path.")]),
  h2("P5 — Solar, storage, EV"),
  img("roofPlan", 470),
  caption("V03 — roof plan: 84 modules, 7 rows × 6 columns per slope, with ridge, eave and gable setbacks kept clear; exhaust fans relocated to the rear gable so nothing penetrates the array."),
  bullet("84 × 620 W modules (52.08 kW) in landscape, 7 × 6 per slope; strings 6 × 14, string Voc 577 V at site minimum temperature; added dead load 0.1132 kPa, array mass 3 062 kg. Modules must appear on the Australian CEC approved-product list — state the listing reference."),
  bullet("Mounting system approved by the panel manufacturer for 100 mm PIR roofs, with sealed through-panel fixings to purlins; wind uplift calculations to AS/NZS 1170.2 are a submission deliverable."),
  bullet("Inverters: 2 × 25 kVA three-phase, certified to AS/NZS 4777.2:2020 and CEC-listed (grid application under AS/NZS 4777.1 is by the buyer). Battery: 2 LFP cabinets, CEC-listed, initial 50 kWh (10 × 5 kWh modules) with enclosure and DC bus rated for expansion to 100 kWh; shipping under IMDG Class 9 with UN 38.3 test summaries. EV: 2 × 22 kW Type 2, AS/NZS 61851.1, RCM, OCPP 1.6J."),
  bullet("All P5 equipment mounts in the external 3.0 × 6.0 m lean-to for fire separation; FRL 60/60/60 wall system between lean-to and the main wall is part of P1 group R."),
  h2("P6 — Electrical, lighting, control"),
  bullet("Main switchboard to AS/NZS 61439, 415 V, 100 A supply. Connected load is 84.9 kW against a 71.9 kVA supply: the dynamic load-management controller (sheds EV charging and HPU on priority) is core scope, not an accessory."),
  bullet("The building runs on sensors — there are no wall switches. 61 sensor points across 15 types (schedule in the BOM workbook), 9 cameras, 4 credential readers without keypads, 10 sensor-driven external luminaires. Open protocols only: MQTT and Modbus TCP, integrating into the buyer's existing Home Assistant; no cloud lock-in; every field device lands on one labelled marshalling terminal strip."),
  bullet([run("Five functions are deliberately hardwired and NOT sensor-dependent (life-safety): ", { bold: true }), run("emergency lighting to AS/NZS 2293, main switchboard isolation, a manual lighting override, hold-to-run on crane and lifts, and mechanical lever egress on every door.")]),
  bullet("Electrical equipment must carry RCM marking (EESS registrable where applicable). Luminaires DALI; emergency luminaires self-contained."),
  h2("P7 — Workshop fit-out"),
  bullet("Reel bank of five (air, 240 V, water, oil with metered gun, grease) under the front-wall hood, 0.504 m clear of the roller-door opening; reticulation to bays; 13 steel workbenches with tool boards; 18RU server rack in the sealed compartment."),
];

const s5 = [
  h1("Design data provided", "设计资料"),
  bullet("This brief (PDF/DOCX) — scope, standards, quality, shipping, commercial terms."),
  bullet("BOM workbook (XLSX) — 244 items in 25 groups with quantities, nominal masses and scope codes; Cover, BOM, Group summary, Sensor schedule and Dimensions sheets. This is the pricing document."),
  bullet("Six rendered views of the CAD master (V01–V06), four reproduced in this brief; the full set is issued with the RFQ."),
  bullet("After order: the parametric geometry underlying every quantity (24 components, 392 bodies, 34 user parameters, 18 automated dimension and clash checks) supports your shop detailing — general-arrangement extracts are issued under NDA."),
  p([run("Shop drawings are the tenderer's deliverable.", { bold: true }), run(" Fabrication does not start until the buyer approves shop drawings; approval reviews conformance with this package, it does not transfer design responsibility for fabrication fitness.")]),
];

const s6 = [
  h1("Standards & compliance", "标准与合规"),
  p("The kit is erected and certified in Australia. The table lists the mandatory conformance base per area; certificates and evidence listed in Section 12 must accompany the quotation where marked."),
  mkTable(["Area", "Mandatory requirements"], [
    ["Structural steel", "AS 4100 design basis; AS/NZS 3679.1 G300 / AS/NZS 1163 sections; AS/NZS 5131 CC2; welding AS/NZS 1554.1 SP (ISO 3834-2 accepted); bolts AS/NZS 1252; HDG AS/NZS 4680"],
    ["Cold-formed purlins/girts", "AS/NZS 4600; material AS 1397 G450 Z350"],
    ["Overhead crane", "AS 1418.1; runway interface AS 1418.18; duty FEM/ISO M5; hold-to-run controls"],
    ["Vehicle hoists", "AS/NZS 1418.9; Australian plant design registration (tenderer dossier); hydraulics ISO 4413"],
    ["Access, deck, racking", "AS 1657 stairs, walkways, guardrails; AS 4084 racking"],
    ["Envelope (PIR)", "Fire evidence FM 4880/4881 or AS 1530.4 full-scale; AS 1562.1 metal roofing; wind AS/NZS 1170.2"],
    ["PV modules", "IEC 61215 + IEC 61730 with CEC approved-product listing"],
    ["Inverters", "AS/NZS 4777.2:2020 certificate + CEC listing"],
    ["Battery system", "CEC-listed; data supporting AS/NZS 5139 installation; UN 38.3; IMDG Class 9 shipping"],
    ["EV chargers", "AS/NZS 61851.1; RCM"],
    ["Electrical equipment", "AS/NZS 61439 assemblies; AS/NZS 5000.1 cables; RCM/EESS; AS/NZS 2293 emergency lighting"],
    ["Plumbing products", "WaterMark — supplied locally in Australia; do not quote"],
    ["Packing & biosecurity", "ISPM 15 timber; IMO/ILO CTU Code; BMSB seasonal treatment; DAFF cleanliness (soil-free, insect-free)"],
  ], [2500, 7138], { zebra: true }),
  p([], { before: 120 }),
  p([run("Substitutions. ", { bold: true }), run("Any deviation from a named standard, section, or certified product family goes in the deviation register with equivalence evidence. Unlisted substitutions discovered in fabrication are rejected at the tenderer's cost.")]),
];

const certRows = [
  ["01", "Portal frames — 360 UB 44.7 at 17.420 m span carrying a 2 000 kg crane", "Structural engineer — AS 4100, AS/NZS 1170, AS 1418.18", "Shop drawings, connection details, MTCs (EN 10204 3.1), weld records"],
  ["02", "Vehicle hoist — registrable plant design registration", "Independent verifier + state regulator", "Full design dossier: calcs, FMEA, drawings, test reports (AS/NZS 1418.9) — 6 weeks from PO"],
  ["03", "Container modification — 15 openings, 85.8 m² of stressed skin removed", "Structural engineer", "Cut drawings, goalpost details, container survey reports"],
  ["04", "Container roof loading — 2.5 kPa deck design UDL", "Engineer / container manufacturer data", "Top side-rail section properties, bearer connection details"],
  ["05", "Crane — runway, brackets, commissioning, 125 % load test", "Crane supplier + engineer", "Wheel loads, buffer forces, deflection calc, test procedure + cert template"],
  ["06", "Slab and footings — 90.5 m³, pads 1.2 × 1.2 × 0.7 m", "Engineer + geotechnical (local)", "Pit-box and HD-bolt setting drawings, cast-in tolerances"],
  ["07", "PIR panel fire performance in a Class 8 building", "Building certifier", "FM 4880/4881 certificate or AS 1530.4 report for the exact panel offered"],
  ["08", "Lithium battery store — Class 9 dangerous goods", "Insurer + fire authority", "UN 38.3 summaries, SDS, cabinet fire-test data"],
  ["09", "Trade waste — interceptor discharge", "Water authority (local)", "—"],
  ["10", "Building approval — ridge 8.432 m, footprint 249.7 m²", "Council / certifier (local)", "GA drawings and elevations from the shop model"],
  ["11", "Electrical — 84.9 kW connected vs 71.9 kVA supply", "Licensed electrician — AS/NZS 3000 (local)", "RCM evidence, switchboard type-test data, load-management logic description"],
  ["12", "Solar array uplift — 52.08 kW, 3 062 kg on the roof", "Structural engineer", "Mounting wind calcs (AS/NZS 1170.2) + fixing schedule"],
  ["13", "Grid connection — 50 kVA of inverter", "Network operator — AS/NZS 4777.1 (local)", "AS/NZS 4777.2:2020 certificates, CEC listing references"],
  ["14", "Battery installation — provision to 100 kWh", "Installer + certifier — AS/NZS 5139 (local)", "System certification, clearance and separation data, signage set"],
  ["15", "Egress under no-switch access control", "Building certifier — NCC (local)", "Door hardware datasheets demonstrating mechanical lever egress"],
];
const s7 = [
  h1("Certification interface", "认证接口"),
  p("Fifteen items need an Australian signature before or during the build. None of them is the tenderer's approval to give — but most cannot be signed without tenderer data. The register below states what your submission and contract deliverables must feed."),
  mkTable(["#", "Certification item", "Australian authority", "Tenderer provides"], certRows, [500, 3300, 2500, 3338], { zebra: true, size: 16 }),
  p([], { before: 120 }),
  box("Critical path — resolve before concrete", [
    "Item 02 has a hard sequencing consequence: the vehicle-hoist design-registration pathway must be resolved before the lift pits are poured. Changing pit depth afterwards is expensive. The registration dossier is therefore due 6 weeks from order, ahead of general fabrication.",
    "Site wind region, terrain category and soil classification are being obtained by the buyer; nothing structural can be certified without them. This does not delay quotation — rates carry any resizing.",
  ]),
];

const s8 = [
  h1("Quality, inspection & testing", "质量与检验"),
  bullet("Quality system: ISO 9001 certification (or documented equivalent) stated in the submission; welding quality system ISO 3834-2 or AS/NZS 1554 qualification records."),
  bullet("Inspection and test plan (ITP): tenderer drafts per package against this brief; buyer marks hold (H) and witness (W) points before fabrication starts. Baseline hold points: material verification against MTCs; first-off portal frame dimensional check; trial assembly (below); galvanizing inspection; FAT; packing."),
  bullet("Material traceability: EN 10204 type 3.1 certificates for all structural steel, plate and bolts, mapped to erection marks."),
  bullet("Welding: 100 % visual; MT/UT on butt welds and the crane-runway and haunch welds at 10 % minimum (100 % where the WPS is newly qualified); reports referenced to weld maps."),
  bullet("Trial assembly: one full portal frame (columns + rafters + haunches) and one crane-runway run laid out with brackets and rail — dimensional report witnessed or video-verified before disassembly for packing."),
  bullet("Galvanizing: thickness surveys to AS/NZS 4680 per lot; repair procedure agreed in the ITP."),
  bullet("Factory acceptance tests: crane (function + overload devices), one lift cassette cycled at rated load with the HPU and one proportional section, sump ventilation fan, control panel point-to-point, camera/reader bench test. Buyer's third-party inspector (SGS/BV/TÜV or similar) attends pre-shipment inspection at the buyer's cost; access to be granted."),
  bullet("Photographic record: every packed unit photographed open and closed; packing lists per container/case tied to BOM item codes."),
];

const s9 = [
  h1("Packing, marking & shipping", "包装与运输"),
  bullet([run("Ship the building in the building. ", { bold: true }), run("The three group-A containers travel as shipper-owned containers (SOC) carrying the kit — book them as cargo-carrying SOCs, not as freight-paying cargo. Long members (max fabricated length ≈ 8.9 m rafters) fit inside a 40 ft unit; supplementary flat racks or GP containers as required by your stuffing plan.")]),
  bullet("Destination: CIF Port of Brisbane, Australia (Incoterms 2020). Quote FOB rates per the BOM plus the freight, insurance and inspection lines on the Group summary sheet; a DDP alternative may be offered separately."),
  bullet("Biosecurity: all timber ISPM 15; cargo free of soil, seeds and insect contamination (Australian DAFF inspection standard). Shipments departing 1 September – 30 April fall inside the BMSB (brown marmorated stink bug) season and require offshore treatment by an approved provider with certificates — the target Q1 2027 arrival is inside this window, so include BMSB treatment in your freight line."),
  bullet("Batteries: IMDG Class 9 (UN 3480) documentation, UN 38.3 test summaries and SDS travel with the shipping docs; batteries packed and declared separately from general cargo."),
  bullet("Preservation: machined surfaces VCI-protected; electrical equipment desiccant-packed and sealed; panels edge-protected and strapped on A-frames or bearers; galvanized steel stacked with separators to prevent wet-storage staining."),
  bullet("Securing: lashing to the IMO/ILO CTU Code with a documented, photographed lashing plan per unit."),
  bullet("Marking: every piece carries its erection mark and BOM item code (hard-stamped or riveted tag on steel; labels elsewhere); shipping marks per case with mass, CoG and sling points; packing lists per container reconciled to the BOM."),
  bullet("Documentation: commercial invoice, packing lists, B/L, ISPM 15 and BMSB certificates, marine insurance certificate (110 % CIF), MTC bundle, test and FAT reports — one complete electronic set before vessel arrival."),
];

const s10 = [
  h1("Delivery & programme", "交付进度"),
  mkTable(["Milestone", "Date / duration"], [
    ["RFQ issued", "28 August 2026"],
    ["Clarification questions close (email only)", "11 September 2026"],
    ["Addendum issued if required", "16 September 2026"],
    ["Quotations due", "25 September 2026, 17:00 AEST"],
    ["Evaluation, clarifications, optional factory audit", "October 2026"],
    ["Target purchase order", "early November 2026"],
    ["Shop drawings + certification data package", "4 weeks from PO"],
    ["Vehicle-hoist design-registration dossier (critical path)", "6 weeks from PO"],
    ["Buyer approval cycle", "2 weeks per cycle"],
    ["Fabrication, procurement, FAT", "10–14 weeks from drawing approval"],
    ["Pre-shipment inspection, BMSB treatment, stuffing", "2 weeks"],
    ["Sea freight to Port of Brisbane", "3–4 weeks — target arrival Q1 2027"],
  ], [6200, 3438], { zebra: true }),
  p([], { before: 120 }),
  p("State your own programme against these milestones in the submission; a credible shorter programme is welcome, an unexamined optimistic one is not."),
];

const s11 = [
  h1("Commercial terms", "商务条款"),
  bullet("Currency USD; state any CNY-linked assumptions. Rates fixed for the validity period (90 days) and through delivery for the awarded scope, except documented steel-index escalation if offered as an option."),
  bullet("Quotation basis: itemised FOB unit rates in the BOM workbook; freight, marine insurance (110 % CIF value) and pre-shipment inspection as separate lines; CIF Port of Brisbane total. Optionally add a DDP (nominated Queensland site) alternative."),
  bullet("Payment baseline (state your terms if different): 30 % deposit on PO against proforma; 60 % against successful pre-shipment inspection and clean on-board B/L; 10 % at 30 days after arrival reconciliation against packing lists. Letter of credit at sight is acceptable to the buyer."),
  bullet("Liquidated damages and performance security are settled at PO; nominate your standard positions in the submission."),
  bullet("Spares: itemise commissioning spares included (BOM G-09 etc.) and offer a recommended 2-year operational spares list with prices."),
  p([], { before: 60 }),
  h2("Minimum warranties (from delivery unless stated)"),
  mkTable(["Scope", "Minimum warranty"], [
    ["Structural fabrication and container work", "24 months"],
    ["PIR panels and coatings", "10 years panel/coating (manufacturer-backed)"],
    ["Overhead crane", "24 months"],
    ["Vehicle lifts and hydraulics", "24 months"],
    ["PV modules", "≥ 12 years product / ≥ 25 years performance"],
    ["Inverters", "≥ 5 years (OP-6: 10 years)"],
    ["Battery system", "≥ 10 years or ≥ 6 000 cycles"],
    ["EV chargers, electrical, lighting, controls", "24 months"],
  ], [5600, 4038], { zebra: true }),
];

const s12 = [
  h1("Submission requirements", "投标要求"),
  p("Return by email to the contact on the cover, subject line “RFQ-CW-2026-001 — [company] — [packages]”, before the closing time. A complete submission contains:"),
  bullet("1 · The BOM workbook (.xlsx) with yellow cells completed and remarks in column K."),
  bullet("2 · Deviation and substitution register (or a signed nil-deviation statement)."),
  bullet("3 · Technical datasheets for all catalogued plant: crane, hoist, lift cassettes, HPU, valves, PIR panel system, roller shutter, PV modules, inverters, batteries, EV chargers, switchboard, sensors, cameras, readers."),
  bullet("4 · Certificates and listings: CEC (modules, inverters, batteries), AS/NZS 4777.2:2020, fire evidence for the PIR panel, UN 38.3, RCM, ISO 9001, welding system (ISO 3834-2 / AS/NZS 1554 records)."),
  bullet("5 · Sample shop drawings: one portal frame and one container-opening goalpost from this project or a directly comparable one."),
  bullet("6 · Vehicle-hoist design-registration dossier index from a previous project (or your plan to produce one to AS/NZS 1418.9)."),
  bullet("7 · Reference list: exports to Australia/NZ or comparable regulated markets in the last five years, with contactable references."),
  bullet("8 · Programme against Section 10; state fabrication capacity and current load."),
  bullet("9 · QA plan and draft ITP with proposed hold/witness points."),
  bullet("10 · Container stuffing plan concept for the three SOC boxes plus additional units, with estimated freight volumes/masses."),
  bullet("11 · Company registration, factory locations, and consent to a buyer factory audit (in person or live video)."),
];

const s13 = [
  h1("Evaluation & award", "评标与授标"),
  mkTable(["Criterion", "Weight"], [
    ["Technical compliance and demonstrated capability (incl. references)", "30 %"],
    ["Price — base scope CIF Brisbane", "30 %"],
    ["Completeness of certification and data package", "15 %"],
    ["Programme credibility", "10 %"],
    ["QA plan and inspection accessibility", "10 %"],
    ["Warranty and after-sales support", "5 %"],
  ], [7600, 2038]),
  p([], { before: 120 }),
  p("The buyer may award the full kit to one tenderer or split by package, may negotiate with any tenderer, and is not bound to accept the lowest or any offer."),
];

const s14 = [
  h1("Conditions of this RFQ", "询价条件"),
  bullet("This RFQ is an invitation to quote, not an offer; no contract exists until a purchase order is executed."),
  bullet("Tenderers bear their own costs of responding."),
  bullet("The design package is the buyer's intellectual property, provided solely for quotation and contract execution; no reuse or disclosure. A mutual NDA is available on request before deeper data exchange."),
  bullet("All communications through the contact email on the cover; approaches to the buyer's engineers or partners about this RFQ invalidate the submission."),
  bullet("Quantities may be adjusted ±10 % at PO under quoted rates; the buyer may delete option lines without affecting base pricing."),
  bullet("English governs; Chinese text is a convenience summary. 中文内容仅为摘要，如有歧义以英文版本为准。"),
];

const groupRows = SUMMARY.group_list.map((g) => [
  g.code, g.title, String(g.items),
  g.mass ? g.mass.toLocaleString("en-US") : "—",
  g.local === g.items ? "local — info only" : g.opt ? `CN + ${g.opt} option` : g.local ? `CN + ${g.local} local` : "CN",
]);
const annexA = [
  hA("Annex A — BOM group summary", "附件A · 材料清单分组汇总"),
  p(`${SUMMARY.items} items in ${SUMMARY.groups} groups. Nominal masses are for freight planning only; final masses come from shop detailing. Scheduled structural steel (groups C–F) totals ${(SUMMARY.steel_mass_kg / 1000).toFixed(1)} t; total nominal cargo mass of China-supply scope ≈ ${(SUMMARY.cn_nominal_mass_kg / 1000).toFixed(0)} t including the three containers.`),
  mkTable(["Grp", "Title", "Items", "Nominal mass (kg)", "Scope"], groupRows, [600, 4738, 800, 1700, 1800], { zebra: true, size: 16 }),
];

const annexB = [
  hA("Annex B — Schedule of principal dimensions", "附件B · 主要尺寸表"),
  p("Rev C, 2026-08-24. Every number is computed from one parameter file — the CAD master, this schedule and the BOM cannot disagree with each other."),
  mkTable(["Element", "Value", "Note"], [
    ["Clear workshop bay", "12.192 × 12.192 m", "containers meet at both rear corners"],
    ["Building envelope", "17.068 × 14.630 m", "footprint 249.7 m²"],
    ["Eave / ridge", "6.896 / 8.432 m", "10.0° pitch, equal both slopes"],
    ["Portal frames", "6 at 2.960 m", "17.420 m span, 360 UB 44.7, haunched"],
    ["Envelope", "100 mm PIR", "607 m² roof, wall and gable"],
    ["Roller door", "4.0 × 4.0 m", "2.875 m clear above the head beam"],
    ["Overhead crane", "2 000 kg, 17.420 m span", "hook 5.154 m; 1.914 m reach over each container top"],
    ["Vehicle lift", "4 × 6 t, 3.0 m stroke", "flush pads on a 4.0 × 3.5 m grid, removable cross beams"],
    ["Hydraulic plant", "15 kW in a floor sump", "2.4 × 1.6 × 1.8 m, bunded, flush covered"],
    ["Container storage deck", "3.001 m level", "max craned item 1.903 m tall"],
    ["Container bays", "15 openings at 2.288 m", "13 workbenches + sealed server compartment"],
    ["Solar array", "52.08 kW", "84 modules, 7 rows × 6 columns per slope"],
    ["Plant lean-to", "3.0 × 6.0 m external", "2 inverters, 2 battery cabinets, 2 × 22 kW EV points"],
    ["Building control", "61 sensor points", "9 cameras, 4 readers, 10 external luminaires, no wall switches"],
    ["Structural steel", "20.7 t", "portals, secondary, crane (BOM groups C–F)"],
    ["Concrete", "90.5 m³", "slab, edge beam, 12 pads, pits, sump — local works"],
    ["Connected load", "84.9 kW", "against a 71.9 kVA supply — load management required"],
  ], [2700, 2500, 4438], { zebra: true, size: 16 }),
];

const annexC = [
  hA("Annex C — Abbreviations", "附件C · 缩略语"),
  mkTable(["Term", "Meaning"], [
    ["AS / AS/NZS", "Australian / Australian-New Zealand Standard"],
    ["BMSB", "Brown marmorated stink bug (Australian seasonal biosecurity measure)"],
    ["BMT", "Base metal thickness"],
    ["CEC", "Clean Energy Council (Australian approved-product listings)"],
    ["CTU Code", "IMO/ILO Code of Practice for Packing of Cargo Transport Units"],
    ["DAFF", "Australian Department of Agriculture, Fisheries and Forestry"],
    ["EESS / RCM", "Electrical Equipment Safety System / Regulatory Compliance Mark"],
    ["EOT", "Electric overhead travelling (crane)"],
    ["FAT / PSI", "Factory acceptance test / pre-shipment inspection"],
    ["FRL", "Fire resistance level (structural adequacy/integrity/insulation, minutes)"],
    ["HDG", "Hot-dip galvanized (AS/NZS 4680)"],
    ["HPU", "Hydraulic power unit"],
    ["ITP", "Inspection and test plan"],
    ["MSB / DB", "Main switchboard / distribution board"],
    ["MTC", "Material test certificate (EN 10204 type 3.1)"],
    ["NCC", "National Construction Code (Australia)"],
    ["PIR", "Polyisocyanurate (sandwich-panel core)"],
    ["SOC", "Shipper-owned container"],
    ["UB / PFC / SHS / CHS / RHS", "Universal beam / parallel-flange channel / square, circular, rectangular hollow section"],
  ], [2600, 7038], { size: 16 }),
  p([], { before: 240 }),
  p([run("Container Workshop · RFQ-CW-2026-001 · rev C · issued 2026-08-28 · The Carbon Project · aaron@carbonproject.com.au", { size: 16, color: MUT })], { align: AlignmentType.CENTER }),
];

// ------------------------------------------------------------------ document
const headerP = new Header({
  children: [new Paragraph({
    tabStops: [{ type: TabStopType.RIGHT, position: CW }],
    border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "C4BDB4" } },
    spacing: { after: 120 },
    children: [
      run("CONTAINER WORKSHOP — PROCUREMENT & RFQ BRIEF", { size: 14, color: MUT }),
      new TextRun({ text: "\t", font: FONT }),
      run(SUMMARY.rfq, { size: 14, bold: true, color: ACCENT }),
    ],
  })],
});
const footerP = new Footer({
  children: [new Paragraph({
    tabStops: [{ type: TabStopType.RIGHT, position: CW }],
    border: { top: { style: BorderStyle.SINGLE, size: 4, color: "C4BDB4" } },
    spacing: { before: 60 },
    children: [
      run("The Carbon Project · aaron@carbonproject.com.au", { size: 14, color: MUT }),
      new TextRun({ text: "\t", font: FONT }),
      new TextRun({ children: ["Page ", PageNumber.CURRENT, " of ", PageNumber.TOTAL_PAGES], font: FONT, size: 14, color: MUT }),
    ],
  })],
});

const doc = new Document({
  creator: "The Carbon Project",
  title: "Container Workshop — Procurement & RFQ Brief (rev C)",
  description: "RFQ-CW-2026-001",
  styles: {
    default: { document: { run: { font: "Calibri", size: 20, color: INK } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: "Calibri", size: 26, bold: true, color: INK } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: "Calibri", size: 22, bold: true, color: ACCENT } },
    ],
  },
  numbering: {
    config: [{
      reference: "bullets",
      levels: [{ level: 0, format: LevelFormat.BULLET, text: "–", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 340, hanging: 200 } } } }],
    }],
  },
  sections: [
    { properties: { page: { margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } }, children: cover },
    {
      properties: { page: { margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } },
      headers: { default: headerP },
      footers: { default: footerP },
      children: [
        ...s1, ...s2, ...s3, ...s4, ...s5, ...s6, ...s7, ...s8, ...s9, ...s10,
        ...s11, ...s12, ...s13, ...s14,
        new Paragraph({ children: [new PageBreak()] }),
        ...annexA, ...annexB, ...annexC,
      ],
    },
  ],
});

Packer.toBuffer(doc).then((buf) => {
  const out = path.join(HERE, "Container-Workshop_RFQ-Brief_RevC.docx");
  fs.writeFileSync(out, buf);
  console.log("wrote", out, buf.length, "bytes");
});
