# Office air: cold air from the rack to the office next door

Two 60 mm flexible ducts run from the cabinet's right-hand side, straight through the office wall:

- **Supply:** from the front **cold** bay, with an 80 mm PWM fan on its plenum adaptor. It blows AC-cooled air into the office.
- **Return:** an equal duct with no fan, from the office back into the rear **hot** bay. The AC's evaporator draws from there.

Each port is a **one-piece printed plenum adaptor (P9)**. It fills the cut in the side lining and tapers smoothly from the 80 mm fan to the 60 mm duct. Its duct spigot carries on out through the skin, ready for your duct and clamp.

![Plenum adaptor](../renders/office_adaptor.png)

![Office ports](../renders/office_ports.png)

**Why there are two ducts.** The cabinet is a sealed loop. If air only went out, the cabinet would draw unfiltered, humid room air in through every gap, and the AC would end up cooling the house. With a return, the office joins the loop. The office air that comes back is a little warmer than the cold side, so the AC simply sees a slightly warmer return.

## What to expect (honest numbers)

![Office air performance](../renders/office_air.png)

`tools/office_air.py` adds up the losses through the circuit: grilles, the adaptor's cone, spigots, 60 mm flex duct and the wall grilles. Each loss uses a coefficient from Idelchik's handbook. The fan curves are derated 15% for the grille and the cone right at the fan. With a 1 m duct each way, the coefficients total K ≈ 9.0. The adaptor's 19° taper cuts the losses by about 13% compared with a flat plate with a hole, which gives about 6% more air:

| Fan (on the supply adaptor) | Air (m³/h) | Cooling at 8 K difference | Drying (26 °C, 55% RH office) | Noise |
|---|---|---|---|---|
| **1 × Noctua NF-A8 PWM** (standard) | 16.4 | **44 W** | 49 W, 1.7 L/day | 17.7 dB(A) flat out, inaudible in the cabinet |
| 2 × NF-A8, push-pull (2nd fan on the return adaptor) | 21.6 | 58 W | 64 W, 2.3 L/day | about 21 dB(A) |
| 1 × Arctic P8 Max | 23.6 | 63 W | 70 W, 2.5 L/day | audible above about 3000 rpm |
| 2 × P8 Max, push-pull | 30.6 | **82 W** | 91 W, 3.2 L/day | audible; cap it with *Office fan maximum* |

Duct length matters little at this size. Going from 0.5 m to 2 m costs about 10%; the grilles and the duct bore set the flow.

**What this means in the room:**

- 45-80 W of sensible cooling plus roughly the same again in drying. That takes the edge off a small office. It **does not replace a split system.** For comparison, a person gives off about 100 W and a laptop and monitor about 60 W.
- In the thermal simulation (an office with 120 W of gains and a 27 °C day, 30 °C when uncooled), the NF-A8 brings the office about **1.5 K** cooler. Two P8 Max fans bring it about **2.5 K** cooler.
- **If you want more:** use bigger ducts, not stronger fans. Flow scales with the duct area. A 100 mm duct pair with 120 mm fans would carry about 3 times the air, around 200 W. The adaptor, its taper and the skin hole are all driven by `office_duct_d` and `office_fan` in `rack_layout.py`, so this is a parameter change and regeneration. The AC has headroom: 4 kW nominal against a 2-2.5 kW design load.

## Rack first

The servers always come first. The controller blocks the office fan, and stops it at once, whenever any of these is true:

- the cold side is more than 1.5 K above its target (released at 0.5 K);
- any rack alarm is active: cold warning or critical, hot warning, leak, sensor fault, condensation or no AC power;
- the AC is not cooling, a shutdown is requested, or the AC mode is Off.

The screen shows **Rack first** while the fan is held off. The simulation includes a case with the AC losing 40% of its capacity. In it, the fan stops whenever the rack runs warm and resumes when it recovers.

## Controls

| Setting (Home Assistant, via the touchscreen; mode and target also on its *Settings* tab) | Default | What it does |
|---|---|---|
| Office air | Auto (when the kit is fitted) | Off / Auto / On. On runs the fan regardless of the office probe, but rack-first still applies. |
| Office target | 24 °C | Calls above 24.5 °C and is satisfied below 23.5 °C. |
| Office supply air | 18 °C | While the office calls, the cold-side target drops to this, but never below the office dew point + 2 K. The setpoint returns afterwards. |
| Office fan maximum | 100% | Caps the fan speed. Use it with the P8 Max for a quieter maximum. |

- The fan only runs when the cold side is at least 1.5 K colder than the office, so it never blows warm air. It ramps from 30% to max over 2 K of call, and runs and rests for at least 2 minutes each time.
- Eco cycling is paused while the office calls.
- The touchscreen sends the room humidity so the node can keep the office supply above the room's dew point. This stops the office grille from sweating.
- **Alarm `office fan`:** the fan reads under 300 rpm for 60 s while it should be running. Check W9 or the fan.
- Home Assistant gets *Office (T7)*, *Office fan speed*, *Office fan* (%) and *Office air state*.

## Electronics (drawing CP-SRA16-ELC-001 rev B)

- **J11:** a 4-pin PC fan header on the carrier.
  - PWM from GPIO14 through Q3 (open collector, 25 kHz).
  - Tach to GPIO15.
  - F2, a 0.5 A PTC, protects the fan's 12 V.
  - R16 holds the fan off while the ESP32 boots.
  - There is no power switch: both specified fans stop at 0% PWM.
- **T7:** a DS18B20 probe in the office return grille's probe channel, on the hot-side 1-Wire bus (spliced at T5). Put its address in the `t_office` substitution in `sra16-node.yaml`.
- **Cables:** W9 is the fan lead; W10 is the T7 lead.
- **Modbus:** the screen reads 0x14-0x18 and reads/writes 0x26-0x29. It writes room RH to 0x34.

## Parts

| Part | Qty | Material | What |
|---|---|---|---|
| **P9 Office plenum adaptor** | 2 | PETG | One piece per port: 86 mm square × 30 mm body in the lining, a cone from Ø76 down to Ø55.2, and a Ø60 spigot with a clamp bead that sticks out 45 mm. It takes 8 heat-set inserts. It prints spigot-up with no supports, about 180 g and 4.6 h each. |
| P10 Office fan grille | 2 | PETG | Finger guard, 74% open. It goes over the fan (supply) or straight onto the adaptor (return). |
| P12 Office wall grille | 2 | PETG | 110 mm square grille plus a 40 mm spigot for the office side, 78% open. It has a T7 probe channel. |
| G3 Duct gauge | 1 | PETG | Check your duct's fit before printing the rest. |
| Noctua NF-A8 PWM | 1 | - | Supply fan, or see the table for options. |
| DS18B20 probe T7 | 1 | - | 3 m lead. |
| M3 × 5.7 brass heat-set inserts | 16 | - | Eight per adaptor: four in each face. |
| M3 × 10 button head A2 + washers | 8 | - | From outside the skin into the adaptor, four per port. |
| M3 × 35 / M3 × 8 socket head A2 | 4 + 4 | - | Supply grille and fan into the adaptor / return grille into the adaptor. |
| Foam tape 2 mm | 1 roll | - | Fan gasket. |
| 60 mm flex duct and hose clamps | 2 runs | - | Owner supplied. |

These lines are all in `bom/BOM.md`, `bom/electronics.csv` and `bom/printed_parts.csv`. The office parts print on plates 13-14. The skin piece **SR3** (sheet-metal pack rev C) has a Ø64 hole per port, for the spigot and its bead. Each port also has 4 × Ø3.4 screw holes on the horizontal and vertical axes, 38 mm from the centre. That puts the screw heads clear of the duct. Both ports sit at 1320 mm above the floor:

| Port | From the front of the cabinet (y) |
|---|---|
| Supply | 99 mm |
| Return | 951 mm |

## Installing

1. **Check your duct.** Print G3 first and push your 60 mm flex duct over it with a clamp. If it is loose or tight, adjust `office_duct_d` and regenerate.
2. **Inserts.** Press eight M3 heat-set inserts into each adaptor with a soldering iron: four in the inner face and four in the outer face.
3. **Cabinet side.** For each port:
   - Cut the 86 mm square out of the side lining and a Ø64 hole in the MLV behind the skin hole.
   - Push the adaptor in from inside the cabinet, spigot first, until it sits on the MLV.
   - Screw it on from outside with 4 × M3 × 10 button heads. The MLV is the gasket: tighten until it just squeezes.
   - **Supply:** put a 2 mm foam ring on the adaptor's inner face. Fit the fan with its airflow arrow pointing **outwards**, then grille P10, and screw them on with 4 × M3 × 35.
   - **Return:** screw grille P10 straight on with 4 × M3 × 8.
4. **Wall.** Mark the two holes level with the ports (1320 mm above the floor).
   - Space them 852 mm apart, matching the ports' centres.
   - Drill them **70-76 mm** with a hole saw so the P12 spigot slides in.
   - In a stud wall, find the studs first: there is about 90 mm between them. Sleeve the cavity with the duct itself.
   - Screw P12 on the office side with wall plugs and 4 mm countersunk screws.
5. **Ducts.** Keep them short and straight, cut to length with a little slack. Clamp them behind the bead on both spigots.
   - Use **insulated flex duct** for the supply. At 18 °C it will sweat on a humid day if it runs through a warm cavity.
   - Leave **at least 150 mm** between the cabinet's right side and the wall for the duct bends.
6. **Probe.** Clip T7 into the channel at the top of the office return grille's bore. It then reads the office air as it leaves the room.
7. **Wire.**
   - Plug W9 into J11.
   - Splice W10 (T7) onto the hot-side bus at T5.
   - Set `t_office` and `office_fitted: "true"` in the substitutions of `sra16-node.yaml`.
8. **Commission.**
   - Warm T7 in your hand. *Office air* should show Waiting, then **Cooling** once the cold side is 1.5 K colder, and the fan speed should appear.
   - Unplug W9 while it runs. The *office fan* alarm should come up within a minute.

## Sealing and noise

- Each port is a hole through the acoustic lining, so seal it well:
  - the adaptor fills the foam cut;
  - its outer face clamps the MLV against the skin, so the MLV is the gasket;
  - the spigot fills the Ø64 skin hole with 0.5 mm all round. Run a bead of silicone there if you want it airtight.
- The duct connects the cabinet to the office, so some server noise will come through it. The fan grille, the duct bend and the wall grille each take some off. Expect a faint hiss in a quiet office. Use lined (insulated) flex duct with one gentle bend if this matters.
- When the office kit is **not** fitted, set `office_ports=0` before cutting. The skin then has no holes. If the holes are already cut, fit the adaptors and cap each spigot.
