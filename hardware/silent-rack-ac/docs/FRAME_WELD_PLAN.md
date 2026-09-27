# SRA-16 welded frame - cut list and weld plan

| | |
|---|---|
| Drawing | CP-SRA16-FRM-001, 6 sheets (`drawings/CP-SRA16-FRM-001.pdf`) |
| Generated | `tools/make_weld_pack.py` from `rack_layout.py` v1.1.0 on 2026-09-27 |
| Frame | 30x30x2.0 SHS C350L0 to AS/NZS 1163, welded; outside 614 W x 1064 D x 1766.2 H mm |
| Mass | 43.1 kg weldment + 4.9 kg loose rail spacers |
| Welds | 38 SHS joints all round + 10 ledge stitch runs + 4 caps + 4 pads, about 8.1 m |
| Holes | 152 x D9.0 for M6 rivnuts, 16 x M8 tapped (castor pads) |

> **Hold point H1.** The mid rails (S2 at the mid level, C3 mid rear) and the partition ledges carry the partition at the AC's grille split, **M3 = 462 mm above datum A** (562 mm above the floor). Tape-check M3 (`docs/DESIGN.md` §3), update `ac_split_z` if needed and re-run `tools/make_weld_pack.py` before cutting those parts. Everything else can be cut now.

## 1. Why 30 x 30 and what changed in the design

The frame was bolted 40 x 40 aluminium T-slot. It is now welded 30x30 steel SHS. Because the frame depth is also the acoustic lining depth, the model now uses 30 mm melamine in the frame bays (was 40). The outside stays 650 x 1100, so the inside grows to 554 x 1004 mm and the height drops to 1884.2 mm.

- **Ledges:** 20 x 3 flat bar, edge-welded, carries the floor, partition and shelf ply. A 20 mm angle does not fit under the ply inside a 30 mm rail.
- **Castor pads:** 8 mm plate under each corner, 4 x M8 tapped. The castors are 92 mm high (`caster_h` 100 minus the pad).
- **Rear panel:** one piece. A 30 mm rail has no room to screw two panel edges at a split.
- **19-inch rail spacers (RS1):** cut from the same SHS but **bolted**, not welded. That way the rack width can be packed out after welding distortion.

## 2. Datums

- **A:** underside of the base rails (height 0). The castor pads sit 8 mm below A.
- **B:** front face of the frame (depth 0).
- **C:** left face of the frame, seen from the front (width 0).

Every cut length and hole position is measured from a member's **datum end**:

- posts and uprights: bottom end;
- side rails S: front end;
- cross rails C: left end.

## 3. Cut list

| Mark | Qty | Description | Section | Cut mm | Holes | kg each | Where |
|---|---:|---|---|---:|---:|---:|---|
| P1 | 2 | Post | 30x30x2.0 SHS | 1763.2 | 8 | 2.96 | post FL; post FR |
| P2 | 1 | Post | 30x30x2.0 SHS | 1763.2 | 15 | 2.96 | post RL |
| P3 | 1 | Post | 30x30x2.0 SHS | 1763.2 | 15 | 2.96 | post RR |
| S1 | 4 | Side rail | 30x30x2.0 SHS | 1004.0 | 9 | 1.68 | Base left; Base right; Top left; Top right |
| S2 | 4 | Side rail | 30x30x2.0 SHS | 1004.0 | 5 | 1.68 | Mid left; Mid right; Shelf left; Shelf right |
| C1 | 1 | Cross rail | 30x30x2.0 SHS | 554.0 | 3 | 0.93 | Base front |
| C2 | 2 | Cross rail | 30x30x2.0 SHS | 554.0 | 5 | 0.93 | Base rear; Top rear |
| C3 | 3 | Cross rail | 30x30x2.0 SHS | 554.0 | 3 | 0.93 | Mid rear; Shelf rear; Top front |
| C4 | 1 | Cross rail | 30x30x2.0 SHS | 554.0 | 0 | 0.93 | Shelf front |
| U1 | 4 | Rack upright | 30x30x2.0 SHS | 731.2 | 7 | 1.23 | upright front left; upright front right; upright rear left; upright rear right |
| RS1 | 4 | Rail spacer (LOOSE - bolted, not welded) | 30x30x2.0 SHS | 731.2 | 0 | 1.23 | spacer front left; spacer front right; spacer rear left; spacer rear right |
| F1 | 4 | Ledge (flat bar) | 20x3 FB | 1004.0 | 0 | 0.47 | floor left; floor right; shelf left; shelf right |
| F2 | 2 | Ledge (flat bar) | 20x3 FB | 611.0 | 0 | 0.29 | partition left; partition right |
| F3 | 4 | Ledge (flat bar) | 20x3 FB | 514.0 | 0 | 0.24 | floor front; floor rear; partition rear; shelf rear |
| PL1 | 4 | Castor pad, 4x M8 tapped | PL 100x100x8 | - | 4 x M8 | 0.63 | corner FL; corner FR; corner RL; corner RR |
| PL2 | 4 | Post top cap | PL 30x30x3 | - | - | 0.021 | top of each post |

- The posts are cut 3 mm short of the frame height; the cap PL2 makes up the difference.
- **P2 and P3 are a handed pair:** they have holes on two adjacent faces. All other left/right parts are identical.
- **Accuracy:** cut each mark as a matched set against a stop (±0.5 mm).

## 4. Stock and nesting

| Stock | Bar | Pieces (mark length) | Offcut mm |
|---|---:|---|---:|
| SHS 30x30x2.0 SHS x 6.5 m | 1 | P1 1763.2, P1 1763.2, P2 1763.2, S1 1004.0 | 184 |
| SHS 30x30x2.0 SHS x 6.5 m | 2 | P3 1763.2, S1 1004.0, S2 1004.0, S2 1004.0, S2 1004.0, C1 554.0 | 139 |
| SHS 30x30x2.0 SHS x 6.5 m | 3 | S2 1004.0, S1 1004.0, S1 1004.0, U1 731.2, U1 731.2, U1 731.2, U1 731.2 | 532 |
| SHS 30x30x2.0 SHS x 6.5 m | 4 | RS1 731.2, RS1 731.2, RS1 731.2, RS1 731.2, C2 554.0, C3 554.0, C4 554.0, C3 554.0, C3 554.0, C2 554.0 | 211 |
| FB 20x3 x 6.0 m | 1 | F1 1004.0, F1 1004.0, F1 1004.0, F1 1004.0, F2 611.0, F2 611.0, F3 514.0 | 217 |
| FB 20x3 x 6.0 m | 2 | F3 514.0, F3 514.0, F3 514.0 | 4439 |

Nesting allows a 3 mm kerf and a 10 mm squaring cut at the start of each bar. Most suppliers will cut the lengths in half for transport; if so, re-nest (it still fits in the same number of bars).

## 5. Drilling (before welding)

Drill Ø9.0 for M6 steel rivnuts, flat head, grip 0.5-3 mm, on the centreline of each face. Install the rivnuts **after coating**. `bom/frame_drilling.csv` gives every position; here are the rules:

- **Pitch and end distance:** at most 250 mm apart, first and last 40 mm from the member ends.
- **Faces:**
  - side panel face of every side-frame member;
  - rear face of the rear posts and rear cross rails;
  - top face of the top rails;
  - bottom face of the base rails, for the skirts, kept 30 mm clear of the castor pads.
- **Members drilled on two faces:** the second face's holes fall midway between the first face's, so the rivnut bodies (about 14 mm long) never meet inside the 26 mm bore.
- **One piece, two positions:** S1, C2 and C3 are each used at two levels. As a base rail, the second face points down for the plinth skirt. As a top rail, the same holes point up for the top panel. The pieces are interchangeable until a bench ledge is welded on.
- **Panel screws:** M6 x 35 flanged button head through 15 mm ply and 3 mm MLV (sheet 4, detail F). Check at least 6 mm of thread engagement in the rivnut you buy.
- **Rack uprights U1:** the inner face gets 3 rivnuts for the RS1 spacer bolts.
- **Castor pads PL1:** 4 x M8 tapped through on a 60 mm square.
  - Match the pattern to the castor you buy.
  - Bolt length is castor plate thickness + 8 mm at most. The bolt must not come through the pad, because two of the holes sit under rail walls.

## 6. Welding procedure (WPS-lite)

| | |
|---|---|
| Process | GMAW (MIG), short-circuit transfer |
| Wire | ER70S-6 (AWS A5.18), ISO 14341-A G 42 4 M21 3Si1, 0.8 mm |
| Gas | Ar + 15-18 % CO2, 12-15 L/min |
| Starting settings | 17-18.5 V, 4.5-6 m/min wire (about 70-100 A), 8-10 mm stick-out, 10-15° push. Prove them on an offcut of the same SHS first. |
| Fillet | 3 mm leg on the 2 mm wall. Tacks 6-8 mm long. |
| Positions | Flat and horizontal. Short vertical-up runs are fine. **Never overhead:** roll the work instead. |
| Preheat / PWHT | None |
| Quality | AS/NZS 1554.1 category GP, 100 % visual inspection. |
| Acceptance | No cracks, burn-through or lack of fusion. Undercut 0.5 mm max. No visible porosity on ground faces. |
| Galvanised (DuraGal) stock | Grind the zinc back 25 mm each side of the joint and use fume extraction. |

**Every SHS T-joint is welded all round** (sheet 4, details A and B):

- faces that are **not flush** get a 3 mm fillet;
- **flush faces** form a flare groove between the rounded corners. Fill it;
- flush faces on the **outside of the frame** (marked `*`) carry panels, door seals or pads. **Grind them flat.**
- the **top rails** stand 3 mm above the post tubes, level with the cap. Their top seam is closed when the cap is welded (T1-T4), so weld only their bottom fillet and side seams in the frame stages.

## 7. Build sequence

1. **Prepare.**
   - Cut all marks.
   - Drill and deburr (section 5). Tap the pads.
   - Weld the F3 ledges onto C1 (base front), C2 (base rear) and C3 (mid rear, shelf rear) on the bench. Clamp each rail to a straight-edge and stitch from the centre out.
   - Put each ledge on the face opposite the rear-panel holes, with its top 18 mm below the rail top (12 mm on the mid rear). The rail top is the face opposite the skirt holes.
   - A ledge fixes the piece to one position, so paint-mark it (C2 BASE REAR and so on).
2. **Side frame SA-L (sheet 2), built flat.**
   1. Lay P1 and P2 down with the drilled outer faces underneath, against a straight stop, 1064 mm outside to outside.
   2. Fit S1 (base, top) and S2 (mid, shelf). The base S1 sits flush with the post bottoms.
   3. Stand U1 on the shelf rail at 160 and 830 from datum B.
   4. Square every joint.
   5. Check the diagonals: 2061.9 mm each, equal within 1.5 mm.
   6. Tack.
   7. Weld joints L01-L12 in order.
   8. Turn the frame over, weld the outer seams and grind them flush.
   9. Turn it back, inner face up, and stitch the F1/F2 ledges, underside only.
      - Set the ledge heights with an offcut of the real ply on the rail: floor and shelf 18 mm, partition 12 mm.
3. **Side frame SA-R:** the same process, **opposite hand**.
   - The rear post is P3.
   - Joints R01-R12 mirror L01-L12.
4. **Box (sheet 3), built on its side.**
   1. Lay SA-L flat, inner face up.
   2. Stand the seven C rails in place and clamp them square to the posts.
   3. Lower SA-R on top and tack all 14 joints.
   4. Check the face and body diagonals (table below) and twist.
   5. Weld B01-B14 in order. Roll the box so every joint is flat or horizontal, and let each joint cool.
5. **Pads and caps.**
   1. Turn the frame upside down on the flat table.
   2. Grind the bottom seams flush.
   3. Clamp the four PL1 pads to the table so they are coplanar, then weld PW1-PW4.
   4. Weld the PL2 caps (T1-T4).
   5. Grind all external faces flush.
6. **Inspect, then finish.**
   1. Measure and record the checks.
   2. Blast (Sa 2½), apply zinc-rich primer, then powder coat.
   3. Fit the rivnuts, castors (M8) and RS1 spacers.
   4. Bond the frame to protective earth.

## 8. Weld schedule and sequence

| Joint | Member end | Welded to | Weld (`*` = grind flush) |
|---|---|---|---|
| L01 | U1 upright rear left | S2 Shelf left | fillet 3: front+rear; flush: outer*, inner |
| L02 | S1 Base left | P1 post FL | fillet 3: top; flush: outer*, inner, bottom* |
| L03 | S1 Top left | P1 post FL | fillet 3: bottom; flush: outer*, inner; top: with cap |
| L04 | S2 Shelf left | P2 post RL | fillet 3: bottom+top; flush: outer*, inner |
| L05 | S2 Mid left | P1 post FL | fillet 3: bottom+top; flush: outer*, inner |
| L06 | U1 upright front left | S1 Top left | fillet 3: front+rear; flush: outer*, inner |
| L07 | S1 Base left | P2 post RL | fillet 3: top; flush: outer*, inner, bottom* |
| L08 | S1 Top left | P2 post RL | fillet 3: bottom; flush: outer*, inner; top: with cap |
| L09 | S2 Shelf left | P1 post FL | fillet 3: bottom+top; flush: outer*, inner |
| L10 | S2 Mid left | P2 post RL | fillet 3: bottom+top; flush: outer*, inner |
| L11 | U1 upright rear left | S1 Top left | fillet 3: front+rear; flush: outer*, inner |
| L12 | U1 upright front left | S2 Shelf left | fillet 3: front+rear; flush: outer*, inner |
| R01 | U1 upright rear right | S2 Shelf right | fillet 3: front+rear; flush: inner, outer* |
| R02 | S1 Base right | P1 post FR | fillet 3: top; flush: inner, outer*, bottom* |
| R03 | S1 Top right | P1 post FR | fillet 3: bottom; flush: inner, outer*; top: with cap |
| R04 | S2 Shelf right | P3 post RR | fillet 3: bottom+top; flush: inner, outer* |
| R05 | S2 Mid right | P1 post FR | fillet 3: bottom+top; flush: inner, outer* |
| R06 | U1 upright front right | S1 Top right | fillet 3: front+rear; flush: inner, outer* |
| R07 | S1 Base right | P3 post RR | fillet 3: top; flush: inner, outer*, bottom* |
| R08 | S1 Top right | P3 post RR | fillet 3: bottom; flush: inner, outer*; top: with cap |
| R09 | S2 Shelf right | P1 post FR | fillet 3: bottom+top; flush: inner, outer* |
| R10 | S2 Mid right | P3 post RR | fillet 3: bottom+top; flush: inner, outer* |
| R11 | U1 upright rear right | S1 Top right | fillet 3: front+rear; flush: inner, outer* |
| R12 | U1 upright front right | S2 Shelf right | fillet 3: front+rear; flush: inner, outer* |
| B01 | C3 Shelf rear | P2 post RL | fillet 3: bottom+top; flush: inner, rear* |
| B02 | C1 Base front | P1 post FR | fillet 3: top; flush: front*, inner, bottom* |
| B03 | C3 Top front | P1 post FR | fillet 3: bottom; flush: front*, inner; top: with cap |
| B04 | C3 Shelf rear | P3 post RR | fillet 3: bottom+top; flush: inner, rear* |
| B05 | C1 Base front | P1 post FL | fillet 3: top; flush: front*, inner, bottom* |
| B06 | C3 Top front | P1 post FL | fillet 3: bottom; flush: front*, inner; top: with cap |
| B07 | C3 Mid rear | P3 post RR | fillet 3: bottom+top; flush: inner, rear* |
| B08 | C2 Top rear | P3 post RR | fillet 3: bottom; flush: inner, rear*; top: with cap |
| B09 | C4 Shelf front | P1 post FL | fillet 3: bottom+top; flush: front*, inner |
| B10 | C2 Base rear | P3 post RR | fillet 3: top; flush: inner, rear*, bottom* |
| B11 | C2 Top rear | P2 post RL | fillet 3: bottom; flush: inner, rear*; top: with cap |
| B12 | C4 Shelf front | P1 post FR | fillet 3: bottom+top; flush: front*, inner |
| B13 | C2 Base rear | P2 post RL | fillet 3: top; flush: inner, rear*, bottom* |
| B14 | C3 Mid rear | P2 post RL | fillet 3: bottom+top; flush: inner, rear* |
| K01 | F1 floor left | S1 Base left | 3 fillet x 25 @ 150 c/c underside, 8 stitches + 20 returns |
| K02 | F1 floor right | S1 Base right | 3 fillet x 25 @ 150 c/c underside, 8 stitches + 20 returns |
| K03 | F3 floor front | C1 Base front | 3 fillet x 25 @ 150 c/c underside, 5 stitches + 20 returns |
| K04 | F3 floor rear | C2 Base rear | 3 fillet x 25 @ 150 c/c underside, 5 stitches + 20 returns |
| K05 | F2 partition left | S2 Mid left | 3 fillet x 25 @ 150 c/c underside, 5 stitches + 20 returns |
| K06 | F2 partition right | S2 Mid right | 3 fillet x 25 @ 150 c/c underside, 5 stitches + 20 returns |
| K07 | F3 partition rear | C3 Mid rear | 3 fillet x 25 @ 150 c/c underside, 5 stitches + 20 returns |
| K08 | F1 shelf left | S2 Shelf left | 3 fillet x 25 @ 150 c/c underside, 8 stitches + 20 returns |
| K09 | F1 shelf right | S2 Shelf right | 3 fillet x 25 @ 150 c/c underside, 8 stitches + 20 returns |
| K10 | F3 shelf rear | C3 Shelf rear | 3 fillet x 25 @ 150 c/c underside, 5 stitches + 20 returns |
| T1-T4 | PL2 caps | posts | Seal weld all round (the cap is flush with the tube), including the 3 mm of each top-rail end that stands above the tube. Grind flush. |
| PW1-PW4 | PL1 pads | post + two base rails | 3 fillet on the inner edges; seal the outer edges and grind flush |

The order alternates between diagonally opposite joints, which balances the heat input. Let each joint cool to hand-warm before welding the next one on the same member.

## 9. Checks

| Check | Target mm | Tolerance |
|---|---:|---|
| Side frame diagonals (each) | 2061.9 | equal ±1.5 |
| Front/rear face diagonals | 1869.9 | equal ±2 |
| Top/base diagonals | 1228.5 | equal ±1.5 |
| Body diagonals | 2151.4 | equal ±3 |
| Outside W x D x H | 614 x 1064 x 1766.2 | ±1.5 |
| Rail levels from datum A | per sheet 2 | ±1 |
| Panel faces flat | - | ≤ 2 |
| Pads coplanar (rock test) | - | ≤ 1 |
| Front-rear upright spacing (19-inch rails) | 700 | ±1 |

## 10. Estimate (indicative, Sept 2026)

Materials are indicative AUD excluding GST. Get quotes.

| Item | Qty | Unit | AUD |
|---|---:|---|---:|
| 30x30x2.0 SHS C350L0, 6.5 m length (incl. RS1 spacers) | 4 | len | 208 |
| Flat bar 20x3, 6.0 m length (ledges) | 2 | len | 44 |
| Flat bar 100x8 (castor pads, 4 x 100 + saw) | 0.45 | m | 14 |
| Flat bar 30x3 (post caps) | 0.2 | m | 1 |
| M6 steel rivnut, flat head, grip 0.5-3 (+10%) | 170 | ea | 59 |
| M8 x 12 set screw 8.8 + spring washer (castors) | 16 | ea | 6 |
| Welding wire, gas, discs, primer (share) | 1 | lot | 60 |
| Blast + zinc primer + powder coat (frame) | 1 | job | 320 |
| **Materials** | | | **714** |

Labour, for a one-off built by hand:

| Task | Hours |
|---|---:|
| Cut + deburr 27 SHS + 10 FB pieces, plates | 3.5 |
| Drill 152 rivnut holes, tap 16 x M8 | 3.4 |
| Fit + tack SA-L, SA-R | 2.5 |
| Fit + tack box, checks | 2.0 |
| Ledges (10), pads, caps | 1.5 |
| Weld 8.1 m (repositioning, cooling) | 2.4 |
| Grind external faces flush, dress | 3.0 |
| Final inspection, measure, record | 0.8 |
| **Total** | **19** |

**Faster options:**

- Send the per-member STEP files to a tube-laser service. That saves about 6 h of cutting, marking and drilling.
- For batches, a welding jig built from the side-frame drawing brings fit-up to minutes.
- Either option makes the welded frame far cheaper than T-slot: the T-slot frame used about AUD 700 of extrusion and brackets.

## 11. Files

- `drawings/CP-SRA16-FRM-001.pdf`
- `bom/frame_cut_list.csv`
- `bom/frame_drilling.csv`
- `bom/frame_weld_schedule.csv`
- `bom/frame_nesting.csv`
- `cad/exports/SRA16_frame_weldment.step`
- `cad/exports/frame_members/*.step (one per mark)`
- `drawings/CP-SRA16-FRM-001_s1..s6.svg`
