# Denza B8 Roof Rack: Three Concepts

Parametric CAD, STEP files and photoreal renders for three roof systems on the **Denza B8**. Every concept includes:

- **Drone hangar module.** A clean-sheet equivalent of the BYD × DJI "Lingyuan" (灵鸢) roof drone dock, sold in China on Fangchengbao Leopard 8 / Bao 8 and other BYD models. It has electric clamshell lids, a landing pad with charging contacts, and status lighting.
- **High-power integrated LED lighting** on the front, both sides and the rear.
- **Aero front cowl** with flush-integrated light blades.
- **RF payload:** ADS-B 1090 MHz receive, LoRa 915 MHz (AU915 / Meshtastic), a Wi-Fi + BLE survey array for wardriving, and GNSS.

| | **A: AERO GT** | **B: EXPEDITION** | **C: SENTINEL** |
|---|---|---|---|
| Character | Low, sleek touring platform | Raised alloy tray, overland | Fully enclosed carbon pod |
| Overall vehicle height (lids closed) | 2.13 m (fins 2.21 m) | 2.27 m (whips fold) | 2.31 m (radome 2.34 m) |
| Drone hangar | Recessed, rear | On deck, rear | Flush in pod, mid |
| Front light | 1,060 mm flush light blade + amber DRL | 40" bar recessed in faceted cowl + 2 pods | 1,000 mm flush nose blade |
| Side / rear light | Full-length scene strips + amber markers; rear bar | 4 scene pods; 2 rear pods + amber bar | 360° perimeter halo; rear blade |
| RF antennas | Twin shark fins (ADS-B / LoRa), 4 Wi-Fi pucks, GNSS | Tall whips (ADS-B / LoRa), 4-whip survey bridge | All inside an RF-transparent radome |

Full engineering spec, compliance notes and commercial positioning: **[docs/DESIGN_SPEC.md](docs/DESIGN_SPEC.md)**

## Deliverables

```
step/
  denza_b8_proxy.step                 vehicle envelope (fit-check only, NOT OEM surface)
  A_AeroGT_rack_assembly.step         rack assembly, named + coloured parts
  A_AeroGT_with_vehicle.step          rack positioned on the B8 proxy
  B_Expedition_*.step
  C_Sentinel_*.step
renders/                              Cycles path-traced, 1600x900
  <design>_01_hero_day.png            3/4 front, outback
  <design>_02_deck_detail.png         high 3/4, hangar open, drone airborne
  <design>_03_drone_launch.png        3/4 rear, launch sequence
  <design>_04_dusk_scene_lights.png   side scene lighting at dusk
  <design>_05_night.png               full LED output
  C_Sentinel_06_rf_radome_xray.png    radome made transparent to show the RF array
docs/
  DESIGN_SPEC.md                      engineering + compliance + commercial
  bom_<design>.csv                    part list (material, envelope, volume)
cad/   rack_lib.py  vehicle.py  designs.py  build.py      (CadQuery)
render/ render.py  run_all.sh                             (Blender/bpy, Cycles)
```

## Rebuild

```bash
python -m venv .venv && . .venv/bin/activate
pip install cadquery bpy            # bpy 5.x wheel needs Python 3.13
cd cad && python build.py           # STEP + BOM + render meshes (~30 s)
# HDRIs (CC0) from polyhaven.com: aarfontein_dirt_road, qwantani_dusk_2, qwantani_night_puresky (4k .hdr)
cd ../render && HDRI_DIR=/path/to/hdri PY=python ./run_all.sh
```

All geometry is parametric. Change `B8[...]` in `cad/rack_lib.py` once the roof has been scanned, and every design re-fits.
