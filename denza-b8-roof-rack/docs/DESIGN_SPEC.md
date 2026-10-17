# Denza B8 Roof System: Design Specification (Concept Stage, Rev A)

Status: **concept / pre-prototype**. The geometry fits a B8 *envelope* proxy built from published dimensions. Before any part is tooled, a 3D scan of the roof and rails must replace that proxy (see §8).

---

## 1. Vehicle reference

| Parameter | Value | Source |
|---|---|---|
| Length × width × height | 5,195 × 1,994 × 1,905 mm | carexpert / zigwheels spec sheets |
| Wheelbase / track | 2,920 mm / 1,670 mm | same |
| Roof rails | Raised, factory fitted | electricvehicleweb review |
| Roof load rating | **Not published.** Must be confirmed with Denza Australia | — |
| Rail section and stanchion spacing | **Estimated** (575 mm off centreline; spans X −2,330 to +560) | CAD assumption |

CAD frame: X forward, Y left, Z up, origin at mid-wheelbase on the ground. Units are mm.

## 2. Drone hangar module (Lingyuan-class)

**Reference system.** BYD and DJI co-developed "Lingyuan" (灵鸢), a roof-mounted drone dock. It is offered in China across BYD brands, including a Leopard 8 special edition. Published behaviour:

- ~21.5 cm tall dock with twin electric covers, landing pad and in-dock charging
- Charges 20→80 % in ~30 min
- Launch and recovery up to ~25 km/h; follows the vehicle up to ~54 km/h
- Uses an Air 3S-class drone. One outlet reports a Mavic 3 on the Yangwang battery-swap version.
- Priced at ~CNY 16,000 in China

**This design** reproduces the *function and layout* only. It does not copy DJI or BYD trade dress, logos or proprietary hardware. Envelope (`rack_lib.HANGAR`):

| Item | Spec |
|---|---|
| Envelope, closed | 700 × 640 × 215 mm (matches Lingyuan's ~215 mm height) |
| Lids | Twin clamshells hinged on the outboard edges, opening 115°. Linear actuator or BLDC + worm drive, with closing torque limited for finger safety. |
| Pad | 620 × 560 mm recessed well, high-contrast H/ring fiducial for vision landing |
| Charging | 4 × pogo contacts (24 V, 100 W class) on the centring zone |
| Positioning | Dock RTK GNSS base. The vehicle's speed and heading are passed to the drone for moving landings. |
| Environmental | IP55 target, lid drain channels, PTC heater, fan for >45 °C ambient |
| Status | Cyan side light strips: ready / charging / fault |
| Mass budget | ≤ 18 kg excluding the drone |

**Integration paths, in commercial order:**
1. **DJI Dock-family / DJI SDK.** DJI Dock 3 is marketed as vehicle-mountable. Its envelope and mass need checking against the B8 roof rating before you choose it. This path gives you DJI's flight autonomy and support.
2. **Own dock + DJI consumer drone via MSDK.** Lower cost, but moving-vehicle landing is your own engineering risk.
3. **Own dock + open drone (PX4 / ArduPilot).** Full control, no DJI dependency. This is useful for government, defence and fleet buyers who exclude DJI.

> **IP warning:** BYD and DJI likely hold Chinese patents and design registrations on Lingyuan. Run an Australian and export-market freedom-to-operate search before selling a "Lingyuan-style" product. The CAD here is deliberately generic.

## 3. The three concepts

### A — AERO GT (low-profile touring)
- Three pairs of clamp feet, 55 mm stand-off. The perimeter frame carries elliptical aero slats.
- **Cowl:** spline-profiled gloss-black ASA/PC shell with a 1,060 mm **flush light blade** (follows the cowl surface) and a 1,180 mm amber DRL line above it.
- **Sides:** full-length aero skirts. Each carries a 1.7 m white scene-light strip on the lower edge and an amber marker strip.
- **Rear:** 800 mm reverse/work bar.
- **Hangar** is recessed between the rails to keep overall height at **2.13 m**.
- **RF:** twin shark fins (ADS-B left, LoRa right), 4 low-profile Wi-Fi/BLE MIMO pucks at the deck corners, GNSS puck forward, and an IP67 RF bay under the deck.
- **Buyer:** premium owners who want the drone with no "overlander" look. Best fit for garage height.

### B — EXPEDITION (overland tray)
- 110 mm feet; 2,450 × 1,400 mm tray in 6061-T6 extrusion; 11 aero slats; gallery lip on the sides and rear.
- **Faceted cowl** with a recessed **40" LED bar** in an anodised bezel, plus 2 × 3" pods on the cowl shoulders.
- **Sides:** 4 × scene pods. **Rear:** 2 × work pods + amber bar.
- **RF:** fibreglass collinears at the front corners (ADS-B 1090 MHz, 560 mm; LoRa 915 MHz, 820 mm) on **NMO spring/fold mounts**, because whips raised reach ~2.9 m. A **survey bridge** carries 4 Wi-Fi whips and GNSS.
- Leaves deck space for recovery boards, fuel and water cans.
- **Buyer:** touring and remote-area users, research and survey fleets.

### C — SENTINEL (enclosed pod)
- Carbon-fibre (RTM or prepreg) monocoque pod: 3.07 m long, 1.37 m wide, nose and tail shaped by a spline, low-drag section.
- **Flush hangar** mid-pod with carbon lids that sit flush with the pod surface when closed.
- **Lighting:** 1,000 mm flush nose blade, rear blade, and a **360° perimeter halo** for scene/work light all round.
- **RF radome** (Ø 680 mm, PTFE-glass or polycarbonate): ADS-B ½-wave dipole, LoRa ¼-wave monopole over a ground plane, 4 × Wi-Fi/BLE sector panels (one per quadrant, which gives direction-finding in wardriving), and GNSS on top.
- **Buyer:** security, emergency services, government and ISR-style fleets. Highest margin.

## 4. Lighting specification

| | A | B | C |
|---|---|---|---|
| Front | 1,060 mm blade, ~180 W, combo optic | 40" bar ~240 W + 2 × 40 W pods | 1,000 mm blade ~200 W |
| Sides | 2 × 1.7 m scene strips, ~60 W each | 4 × 25 W flood pods | Halo, ~120 W total |
| Rear | 800 mm bar ~40 W | 2 × 25 W + amber bar | 800 mm blade ~60 W |
| Amber | DRL + side markers | Rear amber bar | (halo can be amber/white bi-colour) |
| Peak draw @ 12 V | ~30 A | ~40 A | ~32 A |

- **Electrical:** dedicated fused 12 V feed from the LV battery or a DC-DC converter (B8 V2L/HV → 12 V, ≥ 600 W). Use a sealed relay/PDM in the RF bay, a Deutsch DT harness, and a single roof pass-through gland.
- **Thermal:** all lenses are PC with hard-coat. Drivers have thermal derating and are potted.

**Road-legality (AU):** Australian Design Rule (ADR) 13/00 and state rules apply. Forward driving lamps must be wired to high beam, with limits on count and position. Scene and work lamps are for stationary use only, and need a separate switch and a "not for use on road" interlock (e.g. below 5 km/h or in park). Amber flashing or rotating lamps need state permits. Market the high-output lights as off-road / stationary, and get a vehicle-modification sign-off (VSB 14 / state engineer) per state.

## 5. RF payload (ADS-B, LoRa, wardriving)

| Function | Hardware (indicative) | Software |
|---|---|---|
| ADS-B 1090 ES (receive) | RTL-SDR v4 or FlightAware Pro Stick Plus (SAW filter + LNA) | readsb + tar1090. Optional feeding to ADS-B Exchange, FlightAware or adsb.fi. Map overlay in the head unit / app. |
| LoRa | RAK2287 concentrator (LoRaWAN gateway, AU915) **and/or** RAK4631 Meshtastic node | ChirpStack / Meshtastic. Off-grid messaging and telemetry. |
| Wi-Fi + BLE survey ("wardriving") | 3–4 monitor-mode adapters (2.4/5/6 GHz, MT7921AU-class) + nRF52840 BLE sniffer | Kismet, WiGLE-format CSV export, heat-maps |
| GNSS | u-blox ZED-F9P (RTK) with a shared L1/L2 antenna | gpsd. Also the drone dock RTK base. |
| Compute | Raspberry Pi 5 / Jetson Orin Nano in the IP67 RF bay, PoE switch, 128 GB+ storage | Edge logging; LTE/satcom uplink optional |

**Antenna layout rules used in the CAD:**
- ADS-B and LoRa antennas are on opposite sides (> 1 m apart) and away from the hangar's drone RC link.
- Wi-Fi survey radios are **receive-only** (monitor mode), so they cannot desense the drone's 2.4/5.8 GHz control link. Do not run active probing.
- GNSS has a clear sky view at the front of the deck (A, B) or the radome apex (C).

**Compliance (AU):**
- ADS-B is receive-only and needs no licence.
- LoRa 915–928 MHz operates under the ACMA LIPD class licence (power/EIRP and duty-cycle limits apply). Use RCM-marked radios.
- Wardriving: logging broadcast beacon metadata (SSID, BSSID, channel, RSSI, location) is generally lawful. Intercepting communication *content* is not (Telecommunications (Interception and Access) Act 1979). MAC addresses linked to a location can be personal information, so get privacy advice before you sell survey data.
- Drone: CASA rules apply. Visual line of sight, 120 m AGL, and the remote pilot must not be the driver. Commercial use needs a ReOC/RePL or the excluded-category notification. Confirm whether CASA permits launching from a moving vehicle before advertising that feature.

## 6. Structure, mass and aero

| | A | B | C |
|---|---|---|---|
| Rack / pod structure | ~32 kg | ~42 kg | ~28 kg (carbon) |
| Lighting + harness | ~6 kg | ~9 kg | ~7 kg |
| RF bay + antennas | ~4 kg | ~5 kg | ~6 kg |
| Hangar (excl. drone) | ~18 kg | ~18 kg | ~16 kg (carbon lids) |
| **Total installed** | **~60 kg** | **~74 kg** | **~57 kg** |

- These are estimates. Production parts are shelled (2.5–3 mm ASA/PC cowls, 2 mm carbon skin), whereas the concept STEP bodies are solid for clarity. Use the BOM volumes for envelope only, not mass.
- The total must stay within the B8's dynamic roof rating, which is unconfirmed (typically 75–100 kg for this class). If the rating is lower, the hangar is the first item to lighten (carbon lids, magnesium base).
- **Aero:** each cowl is cambered to push the stagnation point above the windscreen header and shed flow over the deck. This lowers wind noise and the drag increment. Validate with CFD (OpenFOAM) and a coast-down test, targeting ΔCdA ≤ 0.06 m² for A and C.
- **Feet:** cast A356 aluminium clamp jaws lined with EPDM, 4 × M8 per foot, torque-limited. Test against ISO 11154 (roof load carriers: dynamic, static and city crash).

## 7. Commercial positioning (indicative, AUD)

| | A AERO GT | B EXPEDITION | C SENTINEL |
|---|---|---|---|
| Hardware BOM (rack, lights, RF, excl. hangar) | ~$2.8k | ~$3.4k | ~$6.5k |
| Hangar module BOM (own design, excl. drone) | ~$4–6k | ~$4–6k | ~$5–7k |
| Suggested retail, fitted (excl. drone) | **$11–14k** | **$12–15k** | **$22–30k** |
| Recurring revenue | ADS-B / LoRa / survey data subscription and fleet dashboard, $20–60/vehicle/month | same | same, plus fleet/government support contracts |

**Go-to-market:** start with **B** (fastest to tool from extrusion and sheet; overland buyers already spend at this level). Use **C** as the fleet and government flagship. **A** is the premium aftermarket option for dealers. A modular dock lets one hangar SKU serve all three platforms.

## 8. Fit-check before production
1. 3D-scan the B8 roof, rails and stanchions (Artec / Einscan). Replace `vehicle.py` and update `B8[...]`.
2. Get the static and dynamic roof load and the rail clamp zones in writing from Denza AU.
3. Run a clearance study: tailgate open arc, sunroof, antenna fin, and the factory LiDAR if fitted.
4. Run CFD and wind-noise analysis on the cowl; validate in a tunnel or with coast-down.
5. Run an EMC pre-scan with all radios and LED drivers live (CISPR 25).
6. Complete the freedom-to-operate search (BYD/DJI dock IP) and register designs for A, B and C.
