# Container Workshop — procurement package (rev C)

RFQ **RFQ-CW-2026-001** · issued 2026-08-28 · quotations due 2026-09-25

Procurement documents for the Container Workshop (rev C, 2026-08-24 design
package): a workshop built from three 40 ft high-cube containers under a
portal-framed PIR envelope, with a 2 t overhead crane, four in-ground 6 t
vehicle lifts, a 52.08 kW roof array with battery storage and EV charging,
and a fully sensor-driven control installation.

## Deliverables (send these to tenderers)

| File | Purpose |
| --- | --- |
| `Container-Workshop_RFQ-Brief_RevC.pdf` | The RFQ / procurement brief — scope packages, technical requirements, Australian standards and certification interface, QA/inspection, packing & shipping (incl. BMSB/biosecurity), commercial terms, submission checklist. Bilingual cover and headings (EN governs). |
| `Container-Workshop_RFQ-Brief_RevC.docx` | Same document, editable. |
| `Container-Workshop_BOM_RevC.xlsx` | The pricing document: 244 items in 25 groups (A–Y) with quantities, nominal masses and scope codes. Tenderers complete the yellow rate cells; amounts and rollups calculate automatically. Sheets: Cover, BOM, Group summary, Sensor schedule, Dimensions. |

Rate and amount columns are deliberately empty: no prices are invented
anywhere in this package — they come from supplier quotes.

## Regenerating

Everything regenerates from two scripts (mirroring the design package's
one-input philosophy):

```bash
pip install openpyxl        # once
python3 generate_bom.py     # -> Container-Workshop_BOM_RevC.xlsx + bom_summary.json
                            #    asserts: 244 items, 25 groups, groups C–F steel = 20.7 t,
                            #    61 sensor points across 15 types

npm install docx            # once (or set NODE_PATH to an existing install)
node generate_brief.js      # -> Container-Workshop_RFQ-Brief_RevC.docx
                            #    reads bom_summary.json + views/*.jpeg
soffice --headless --convert-to pdf Container-Workshop_RFQ-Brief_RevC.docx
```

`views/` holds the six renders (V01–V06) exported from the rev C design page
("Container Workshop" artifact); four are embedded in the brief.

## Scope codes used throughout

- **CN** — China supply, base scope (quote required)
- **CN-OPT** — priced option, excluded from base totals
- **LOCAL** — Australian supply / site works (concrete, erection, licensed
  electrical, certification) — info only, not quoted

## Key facts carried from the rev C design package

- BOM: 244 items / 25 groups; scheduled structural steel (groups C–F) 20.7 t;
  nominal China-scope cargo ≈ 74 t including the three containers, which ship
  as shipper-owned containers carrying the kit.
- Design status: **for engineering, not certified**. 15 Australian sign-off
  items are tabulated in the brief; the vehicle-hoist design-registration
  dossier is on the critical path (before lift pits are poured).
- Connected load 84.9 kW vs 71.9 kVA supply — dynamic load management is
  core scope. No wall switches; five life-safety functions stay hardwired.
