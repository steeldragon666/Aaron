#!/usr/bin/env bash
# Render the full image set. Requires HDRI_DIR with the Poly Haven (CC0) HDRIs:
#   aarfontein_dirt_road, qwantani_night_puresky, qwantani_dusk_2  (4k .hdr)
set -euo pipefail
cd "$(dirname "$0")"
PY=${PY:-python}
OUT=../renders
RES=${RES:-1600x900}
SPP=${SPP:-64}
mkdir -p "$OUT"
r() { echo "-> $*"; $PY render.py --res "$RES" --samples "$SPP" "$@" > /dev/null 2>&1; }
for D in A_AeroGT B_Expedition C_Sentinel; do
  r --variant ${D}_closed --hdri aarfontein_dirt_road_4k.hdr --hdri-rot 120 --cam front34 --mode day --out $OUT/${D}_01_hero_day.png
  r --variant ${D}_open   --hdri aarfontein_dirt_road_4k.hdr --hdri-rot 120 --cam top34   --mode day --out $OUT/${D}_02_deck_detail.png
  r --variant ${D}_open   --hdri aarfontein_dirt_road_4k.hdr --hdri-rot 300 --cam rear34 --mode day --out $OUT/${D}_03_drone_launch.png
  r --variant ${D}_closed --hdri qwantani_dusk_2_4k.hdr --cam side --mode dusk --hdri-strength 0.6 --out $OUT/${D}_04_dusk_scene_lights.png
  r --variant ${D}_closed --hdri qwantani_night_puresky_4k.hdr --hdri-strength 0.25 --exposure 0.5 --cam night_front --mode night --out $OUT/${D}_05_night.png
done
r --variant C_Sentinel_xray --hdri aarfontein_dirt_road_4k.hdr --hdri-rot 120 --cam top34 --mode xray --out $OUT/C_Sentinel_06_rf_radome_xray.png
echo done
