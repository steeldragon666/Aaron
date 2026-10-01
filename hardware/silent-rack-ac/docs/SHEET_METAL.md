# SRA-16 sheet-metal parts (laser cut)

| | |
|---|---|
| Drawing | CP-SRA16-SMP-001, 6 sheets (`drawings/CP-SRA16-SMP-001.pdf`) |
| Generated | `tools/make_sheet_pack.py` from `rack_layout.py` v1.2.0 on 2026-10-01 |
| DXF | `cad/dxf/cut/` (cut geometry only), `cad/dxf/info/` (+ bend lines, ID etch, notes), `cad/dxf/nest/` (nested 1200x800 blanks), all zipped in `cad/dxf/SRA16_sheet_metal_DXF.zip` |
| Size limit | every flat blank fits 1200 x 800 (checked) |
| Skins | 1.2 mm steel, powder coated, 3 mm MLV bonded inside; the welded frame is unchanged |
| Hold point | RP1, SL1, SL2, SR1, SR2 move with the AC grille split: cut them after tape check M3 (`docs/DESIGN.md` §3). The other 23 part types can be cut now. |

## What changed

The 15 mm ply skins are now laser-cut 1.2 mm steel. The frame and the inside of the cabinet are unchanged, so the outside shrinks to 622.4 W x 1072.4 D x 1870.4 H mm.

- **Split skins.** The side skins are split into 3 pieces, on the mid and shelf rails. The rear skin is split into 2, on the shelf rail. Every piece fits 1200 x 800.
- **Joint strips.** Each joint sits on a rail centreline with a 1 mm gap, and both skin edges have R4 notches round each strip screw. A 50 x 1.2 strip covers the joint and is screwed through the notches into the rail's rivnuts (detail J, sheet 5). The MLV behind stays one piece per side.
- **Doors.** The doors are flat skins stiffened by a bonded 20 x 20 angle frame. The hinges and toggle latches are riveted through the skins, so the frame needs **no extra holes**.
- **Acoustics.** 1.2 mm steel plus MLV weighs about as much as 15 mm ply plus MLV. It has no coincidence dip in the speech band, so the insertion loss is the same or slightly better.

## Parts

| ID | Qty | Part | Material | t mm | Flat mm | Holes | Bends | Fits |
|---|---:|---|---|---:|---|---:|---:|---|
| SL1 | 1 | Side skin left - bottom | Steel sheet (Zincanneal or CR4) | 1.2 | 1064.0 x 446.5 | 12 | 0 | left side, frame z 0.0-446.5 above datum A |
| SL2 | 1 | Side skin left - middle | Steel sheet (Zincanneal or CR4) | 1.2 | 1064.0 x 542.0 | 10 | 0 | left side, frame z 447.5-989.5 above datum A |
| SL3 | 1 | Side skin left - top | Steel sheet (Zincanneal or CR4) | 1.2 | 1064.0 x 775.7 | 27 | 0 | left side, frame z 990.5-1766.2 above datum A |
| SR1 | 1 | Side skin right - bottom | Steel sheet (Zincanneal or CR4) | 1.2 | 1064.0 x 446.5 | 13 | 0 | right side, frame z 0.0-446.5 above datum A |
| SR2 | 1 | Side skin right - middle | Steel sheet (Zincanneal or CR4) | 1.2 | 1064.0 x 542.0 | 8 | 0 | right side, frame z 447.5-989.5 above datum A |
| SR3 | 1 | Side skin right - top | Steel sheet (Zincanneal or CR4) | 1.2 | 1064.0 x 775.7 | 29 | 0 | right side, frame z 990.5-1766.2 above datum A |
| JS1 | 2 | Joint strip, side skins - mid rail | Steel sheet (Zincanneal or CR4) | 1.2 | 1064.0 x 50.0 | 5 | 0 | over the side-skin joint on the mid rail (right side: same part, flipped) |
| JS2 | 2 | Joint strip, side skins - shelf rail | Steel sheet (Zincanneal or CR4) | 1.2 | 1064.0 x 50.0 | 7 | 0 | over the side-skin joint on the shelf rail (right side: same part, flipped) |
| RP1 | 1 | Rear skin - bottom | Steel sheet (Zincanneal or CR4) | 1.2 | 622.4 x 989.5 | 19 | 0 | rear, frame z 0.0-989.5 above datum A |
| RP2 | 1 | Rear skin - top | Steel sheet (Zincanneal or CR4) | 1.2 | 622.4 x 775.7 | 13 | 0 | rear, frame z 990.5-1766.2 above datum A |
| JR1 | 1 | Joint strip, rear skin | Steel sheet (Zincanneal or CR4) | 1.2 | 622.4 x 50.0 | 3 | 0 | over the rear-skin joint |
| TP1 | 1 | Top skin | Steel sheet (Zincanneal or CR4) | 1.2 | 622.4 x 1072.4 | 13 | 0 | top, over the top rails and post caps (front at the bottom) |
| DL1 | 1 | Door, lower (AC bay) | Steel sheet (Zincanneal or CR4) | 1.2 | 622.4 x 988.5 | 23 | 0 | front, frame z 0.0-988.5 above datum A |
| DU1 | 1 | Door, upper (rack) | Steel sheet (Zincanneal or CR4) | 1.2 | 622.4 x 772.7 | 15 | 0 | front, frame z 991.5-1764.2 above datum A |
| DA1 | 1 | Door stiffener, lower door, left vertical | Steel sheet (Zincanneal or CR4) | 1.2 | 941.0 x 37.7 | 9 | 1 | inside the lower door, left edge; flat leg bonded to the skin, leg inboard |
| DA2 | 1 | Door stiffener, lower door, right vertical | Steel sheet (Zincanneal or CR4) | 1.2 | 941.0 x 37.7 | 6 | 1 | inside the lower door, right edge; flat leg bonded to the skin, leg inboard |
| DA3 | 1 | Door stiffener, upper door, left vertical | Steel sheet (Zincanneal or CR4) | 1.2 | 727.2 x 37.7 | 6 | 1 | inside the upper door, left edge; flat leg bonded to the skin, leg inboard |
| DA4 | 1 | Door stiffener, upper door, right vertical | Steel sheet (Zincanneal or CR4) | 1.2 | 727.2 x 37.7 | 6 | 1 | inside the upper door, right edge; flat leg bonded to the skin, leg inboard |
| DA5 | 4 | Door stiffener, horizontal (top/bottom, both doors) | Steel sheet (Zincanneal or CR4) | 1.2 | 510.0 x 37.7 | 0 | 1 | inside each door, top and bottom, between the verticals |
| KB1 | 4 | Latch keeper bracket | Steel sheet (Zincanneal or CR4) | 1.2 | 83.3 x 40.0 | 2 | 1 | door front face at the right edge, wraps round to the side |
| WR1 | 1 | Window retainer frame | Steel sheet (Zincanneal or CR4) | 1.2 | 180.0 x 240.0 | 8 | 0 | inside the lower door, clamps the glazing unit |
| SK1 | 1 | Plinth skirt, front | Steel sheet (Zincanneal or CR4) | 1.2 | 410.0 x 115.7 | 3 | 1 | front, under the base rail between the castor pads |
| SK2 | 1 | Plinth skirt, rear (drain outlet) | Steel sheet (Zincanneal or CR4) | 1.2 | 410.0 x 115.7 | 3 | 1 | rear, under the base rail (seen from behind) |
| SK3 | 2 | Plinth skirt, side (right: same part turned round) | Steel sheet (Zincanneal or CR4) | 1.2 | 860.0 x 115.7 | 4 | 1 | left and right, under the side base rails |
| DT1 | 1 | Drip tray (304 stainless pan) | Stainless 304 sheet, 2B | 1.2 | 603.4 x 1053.4 | 1 | 4 | bay floor, inside the frame |
| PD1 | 4 | Castor pad (weld pack mark PL1) | Steel plate (grade 250) | 8 | 100.0 x 100.0 | 4 | 0 | under each frame corner, welded |
| PC1 | 4 | Post top cap (weld pack mark PL2) | Steel plate (grade 250) | 3 | 30.0 x 30.0 | 0 | 0 | top of each post, welded |
| RR1 | 4 | 19in rail, 16U (EIA-310 square holes) | Steel sheet (CR4) | 2 | 721.2 x 46.2 | 51 | 1 | on the rail spacers RS1, front and rear, both sides (bend 2 up, 2 down) |

## Holes

| Hole | Size | For |
|---|---|---|
| Frame screw | D8 | M6 x 20 flanged button head into a frame rivnut. The hole is 2 mm oversize for the frame tolerance. |
| Rivet | D5 | 4.8 mm blind rivet: hinges, latch bases, keepers |
| M5 | D5.5 | pull handles, exhaust spigot flange |
| M4 | D4.5 | window clamp, cable grommet |
| Rail bolt | D7 | M6 through the 19in rail and rail spacer into the upright rivnut |
| Tap M8 | D6.8 | castor pads (tap after cutting) |
| Cage nut | 9.5 square | EIA-310, 3 per U |
| Joint notch | R4 edge notch | split skins, centred 0.5 mm beyond the edge: clearance for the joint strip's M6 screws |

## Hardware (confirm before cutting)

The hardware holes suit the parts below. If yours differ, change `HW` in `rack_layout.py` and re-run.

- **Hinges:** lift-off butt hinges, 5 off. On both leaves the rivets sit **51.2 mm from the knuckle axis**. The axis is on the front-left corner. Drill the hinge leaves to suit if needed.
- **Latches:** adjustable toggle latches, 4 off, riveted to the right-hand side skins. The hook engages the slot in the KB1 keeper on the door.
- **Window:** 2 x 6 mm polycarbonate, 180 x 240, with a 10 mm EPDM spacer frame. Clamp the stack to the lower door with the WR1 frame and 8 x M4 x 35.
- **Rear skin:** a D150 exhaust spigot (4 x M5 on PCD 190) and a 200 x 40 brush cable grommet.

## Nesting (1200 x 800 blanks)

| Material | Blanks | Parts |
|---|---:|---|
| Steel sheet (Zincanneal or CR4) 1.2 mm | 11 | SL3 JR1 DA3 KB1 KB1; SR3 DA4 DA5 KB1 KB1; TP1 SK3 DA5 DA5; RP1 SK3 SK1 WR1; DL1 JS1 JS1 SK2 DA1 DA5; SL2 JS2 JS2 DA2; SR2; RP2; DU1; SL1; SR1 |
| Stainless 304 sheet, 2B 1.2 mm | 1 | DT1 |
| Steel plate (grade 250) 8 mm | 1 | PD1 PD1 PD1 PD1 |
| Steel plate (grade 250) 3 mm | 1 | PC1 PC1 PC1 PC1 |
| Steel sheet (CR4) 2 mm | 1 | RR1 RR1 RR1 RR1 |

## Assembly

1. **Coat, then line.**
   - Powder coat all the parts.
   - Bond the MLV inside the skins and doors. Punch it D8 at the frame screws: it is the gasket over the rivnut flanges. Cut it back 3 mm round rivets, M4/M5 holes and cut-outs.
   - Snug the M6 frame screws (about 3 N m); the MLV must not squeeze out.
2. **Doors.**
   1. Bond the stiffener frame (DA1-DA5): legs inboard, 2 mm inside the frame opening.
   2. Rivet the hinges and the KB1 keepers through the skin and the angle.
   3. Fit the pull handles.
   4. Fit the glazing unit in the lower door.
3. **Side skins.**
   1. Fit the pieces bottom to top.
   2. Fit the JS strips over the joints with acoustic sealant under each strip edge.
4. **Rear skins.**
   1. Fit both pieces and the JR strip.
   2. Fit the exhaust spigot and the cable grommet.
5. **Top skin.** Fit it last; it overlaps the side and rear skins.
6. **Skirts.** Screw SK1-SK3 up into the base-rail rivnuts.
7. **Hang the doors and fit the latches.**
   1. Hang the doors on the lift-off hinges.
   2. Rivet the latches to the pre-cut holes in the right-hand skins.
   3. Adjust each latch so it pulls its door onto the seal (about 3 mm compression).

## Checks built into the generator

- Every flat blank fits 1200 x 800.
- Every frame rivnut used for a skin, strip or skirt is matched by a hole in a sheet part. Mirror twins (joint strips, side skirts) are verified hole-for-hole before they are merged.
- Holes clear the part edges by 1.5 t (minimum 2.5 mm) and clear bend zones by 1.5 t.
- Holes do not overlap, and the rack-rail bolt holes match all four uprights.
- Split skins are notched round every joint-strip screw.

## Files

- `drawings/CP-SRA16-SMP-001.pdf`
- `cad/dxf/SRA16_sheet_metal_DXF.zip`
- `cad/dxf/cut/<ID>.dxf (28 parts)`
- `cad/dxf/info/<ID>.dxf`
- `cad/dxf/nest/*.dxf (15 blanks)`
- `bom/sheet_metal_parts.csv`
- `bom/sheet_metal_nesting.csv`
- `drawings/CP-SRA16-SMP-001_s1..s6.svg`
