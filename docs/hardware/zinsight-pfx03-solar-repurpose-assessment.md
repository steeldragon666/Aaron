# ZINSIGHT PFX03 — Feasibility Assessment for Repurposing as a Solar PV / Battery Controller

**Status:** Research assessment, pre-teardown
**Date:** 2026-08-16
**Subject:** 6 × ZINSIGHT PFX03 integrated fuel-cell power electronics units
**Objective:** Determine whether the units can be reconfigured as PV MPPT + battery charge controllers, and what to do with the auxiliary inverter outputs.

---

## 1. Executive summary

**Yes — and the core function is a much better match than you'd expect.**

A fuel-cell DC/DC and a PV MPPT charge controller are, at the power-stage level, *the same converter*: a unidirectional boost from a soft, variable-voltage, high-current source into a stiff higher-voltage bus, under current-mode control with a constant-voltage outer limit. Direction, topology, voltage ranges and control structure all map essentially 1:1. You are not fighting the hardware.

The blocker is not the power electronics. It is **firmware and the fuel-cell startup state machine**.

Three findings drive the recommendation:

1. **The DC/DC repurpose is sound.** 100–550 V in → 450–750 V out is exactly a PV-string-to-battery-bus boost. The 600 A input rating means the unit will never be your bottleneck.
2. **MPPT does not need to live inside the box.** If you can command input current over CAN, an external supervisor doing perturb-and-observe at 1–10 Hz is a complete, standard MPPT implementation. This is the key insight that makes the "don't touch the firmware" path viable.
3. **Do not repurpose the compressor inverter for workshop ventilation.** It is the worst value in the project — high effort, poor fit, and a $300 commodity VFD does the job better. Detailed reasoning in §6. There is a much better use for the spare units (§7).

**Recommended approach:** time-box a 3-week black-box CAN investigation on *one* unit (Strategy A). Plan and budget for a control-board transplant (Strategy B) as the path that actually finishes. Cut nothing until Phase 0 is complete.

---

## 2. What the hardware is

**ZINSIGHT Technology (Shanghai) Co., Ltd.** (致瞻科技) — a SiC power-electronics specialist. Their product lines are ZiPACK SiC power modules and SiCTeX drive systems; they are a mass producer of SiC e-compressor controllers on 400 V / 800 V / 1000 V bus platforms, and they build hydrogen fuel-cell controllers, DC/DC converters (e.g. the DM60, a 60 kW liquid-cooled unit) and traction inverters. They have public design wins using Wolfspeed 1200 V SiC MOSFETs (the HS35, a 35 kW ultra-high-speed FCV air-compressor controller) and STMicroelectronics 3rd-gen SiC planar MOSFETs.

`PFX03` is the platform code for this integrated fuel-cell power unit. Boards visible, all dated June 2022:

| Board | Silkscreen | Function (inferred) |
|---|---|---|
| Main control | `PFX03-EB001-0204`, 2022-06-23 | Signal/control board — MCU, sensor conditioning, gate-drive fan-out, contactor drive |
| HV distribution | `PFX03-EB005-0204`, 2022-06-24 | Fuses (F1–F3), precharge, PTC/thermocouple terminals, contactor coil drives |
| Auxiliary supply | `PFX03-EB006-0204`, 2022-06-13 | Isolated LV supply + EMI filter (2 × common-mode chokes, potted) |
| Power stage | (under gate driver PCBs) | SiC modules on liquid cold plate, laminated busbar, gate driver PCB per module |

### 2.1 Main control board connector map (as silkscreened)

| Ref | Label | Inferred function |
|---|---|---|
| J1 | `PRE` | Pressure sensor input (H2 and/or air supply) |
| J2 | `EXT` | External interface — **CAN bus, LV supply, ignition/wake, HVIL** |
| J3 | `TEMP` | Temperature sensor input (stack / coolant) |
| J5 | `VOL` | Voltage sense |
| J6, J8 | `DCL` | DC link sense |
| J7 | `ACP` | ~30-way ribbon → **air compressor** inverter gate drivers (cable tagged `J7-ACP`) |
| J9 | `DCF1-2` | ~26-way ribbon → **DC/DC** gate drivers, phases 1–2 |
| J10 | `FC_RLY` | Fuel cell contactor drive |
| J11 | `DC_RLY` | DC contactor drive |
| — | (unpopulated 10-way white header, top-left) | **Strong JTAG / programming header candidate** |

Also present: a bank of 8 status LEDs (`D5`–`D12`, series resistors `R35`–`R42`) — these will be your first diagnostic signal on power-up. Current-sense shunts marked `R050` (50 mΩ) and `1R00` are on low-current auxiliary rails; the 600 A main path will use a Hall/fluxgate sensor (the ring sensor is visible in the full-unit photo).

Balance-of-plant harness labels are in Chinese and confirm the fuel-cell architecture: 水泵 (water pump), 氢气 (hydrogen), 空气 (air).

### 2.2 Stated ratings

| Port | Rating | PV/battery equivalent |
|---|---|---|
| DC input | 100–550 V, 600 A | PV array input — **direct match** |
| DC output | 450–750 V, up to 180 kW | Battery bus — **direct match** |
| Compressor inverter | 48 kW, 3-phase | See §6 — poor repurpose target |
| Secondary motor drive | 70 A RMS, 3-phase | Coolant pump / radiator fan — **good match** |

> **Note on the "1500 V" figure:** the compressor drive is fed from the 450–750 V DC link, so its voltage class is that bus, not 1500 V. ZINSIGHT's e-compressor platforms are documented at 400 V / 800 V / 1000 V. Worth confirming against the unit's own nameplate — a 1500 V number would have to belong to something else (device blocking voltage, or isolation test voltage).

---

## 3. Why the DC/DC repurpose is a genuinely good fit

| Requirement | Fuel cell DC/DC does | PV MPPT charger needs | Match |
|---|---|---|---|
| Power direction | Unidirectional, source → bus | Unidirectional, array → battery | ✅ Identical |
| Source behaviour | Soft; V droops with I, has a knee | Soft; V collapses past MPP | ✅ Same curve shape |
| Input range | 100–550 V | PV string, designable to suit | ✅ |
| Output | 450–750 V regulated | Battery bus, CC then CV | ✅ Already CC/CV |
| Inner loop | Current-mode | Current-mode | ✅ |
| Outer loop | Power/current command over CAN | MPP tracking | ⚠️ Wrap externally (§5) |
| Protection | OV/UV/OC, insulation monitoring, HVIL, precharge | Same, plus array earth-fault | ✅ Better than most DIY |

The one genuinely structural difference is the outer control law. A fuel-cell controller is *commanded* to a power set-point by a vehicle supervisor; it does not seek a maximum power point. But it already contains the hard part — the fast current regulator and the "don't drag the source past its knee" limit logic. Adding MPP tracking on top is a slow, low-bandwidth outer loop that does not have to live inside the box.

### 3.1 Array design constraint (real, but manageable)

Input maximum is **550 V**. Your string `Voc` at record-low site temperature must sit safely under that — design to ≤ 500 V for margin. With modern modules at 41–50 V `Voc` that is roughly **10–11 modules per string** (~400–450 V `Vmp`).

Consequences:
- Shorter strings than a normal commercial 1000–1500 V design → more parallel strings, more combiner hardware, heavier DC cable, higher I²R loss.
- Not a blocker. Just plan the array around the converter from the start rather than retrofitting.

### 3.2 The oversizing problem — flag this early

180 kW of converter on a workshop roof is a 5–10× oversize. At ~17% load (e.g. 30 kW array), a large SiC boost carries switching, gate-drive, auxiliary-supply and coolant-pump losses that are largely **independent of throughput** — expect a few hundred watts of standing loss plus pumping power. Annualised, that is a meaningful parasitic against a small array.

The fix is **phase shedding** — if the DC/DC stage is interleaved (the power-stage photo strongly suggests multiple parallel legs), dropping to one phase at light load recovers most of it. Phase shedding requires firmware control, which is an argument for Strategy B.

---

## 4. The three real obstacles

**1. Firmware is locked.** The control MCU will almost certainly have read-out protection enabled (TI C2000 CSM/DCSM, Infineon AURIX HSM, or NXP flash protection). Assume no source, no toolchain, no CAN DBC, and no ability to modify OEM behaviour. Plan around this rather than hoping.

**2. The fuel-cell startup state machine.** Even treating the unit as a black box, it will refuse to close contactors until satisfied on: H2 supply pressure, air pressure/flow from the compressor, coolant temperature, insulation resistance, HVIL continuity, and quite possibly stack cell-voltage monitoring (CVM). The `PRE`, `TEMP` and `VOL` connectors on the main board exist precisely for these checks. Spoofing them is feasible — but it must be done with plausible *sequencing and dynamics*, and a single undocumented interlock can stop the whole approach dead.

**3. Cooling is mandatory.** This is a liquid-cooled automotive unit — the cold plate expects roughly 10–15 L/min of water/glycol at 50–65 °C inlet. You need a pump, radiator, fan and thermostat regardless of how lightly you load it. Budget for it as real work, not an afterthought.

---

## 5. Strategy options

### Strategy A — Black-box it (keep OEM firmware, drive over CAN)

Sniff and replay the CAN interface on `J2`, emulate the balance-of-plant sensors, and command the DC/DC as if it were still boosting a stack.

**MPPT without touching firmware.** This is the elegant part. If the unit accepts an input-current or power command and reports input voltage and current in its telemetry, then:

```
loop at 1–10 Hz:
    read V_in, I_in from CAN telemetry
    P = V_in × I_in
    if P > P_previous:  keep perturbing current command in same direction
    else:               reverse direction
    clamp command above the input-undervoltage trip threshold
```

That is a complete, textbook perturb-and-observe MPPT wrapped around a current-commanded converter. It works well, it runs on a Raspberry Pi or small PLC, and it needs nothing from inside the box. The only care required is backing off *before* the array voltage collapses into the converter's own undervoltage trip.

- **Effort:** medium-high. **Outcome:** binary.
- **Risk:** high chance of an unsatisfiable interlock.
- **Verdict:** worth a strictly time-boxed 3-week investigation on one unit, because the payoff is enormous and you have six.

### Strategy B — Control board transplant (recommended to plan for)

Replace `EB001` with your own controller; keep everything else.

**You keep** (~90% of BOM value and all the hard thermal/mechanical engineering): SiC modules, gate driver boards, cold plate, DC-link capacitors, laminated busbars, boost inductor, contactors, precharge circuit, fuses, HV connectors, current sensors, and the `EB006` auxiliary supply.

**You build:** a controller board — TI C2000 (TMS320F28379D class) for a straightforward implementation, or ARM+FPGA (Zynq-7000 class) if you want tight multi-phase interleaved control and phase shedding.

**Reverse-engineering required:**
- `J7` / `J9` ribbon pinouts — gate PWM, desaturation/fault return, ready/enable
- Current-sense and HV-divider scaling on `J5` / `J8`
- Contactor drive and precharge sequencing logic on `J10` / `J11`

All of this is measurable with a scope, a bench supply and patience. The gate driver IC part numbers give you the interface spec directly from their datasheets.

- **Effort:** high but **bounded and deterministic** — 3–6 months part-time for a competent power-electronics engineer.
- **Payoff:** total control. MPPT, phase shedding, custom battery CC/CV profile, your own CAN/Modbus telemetry, no black box, and a design you can maintain.

### Strategy C — Harvest

If A and B both stall, the SiC modules, DC-link film caps, HV contactors, precharge assembly, liquid cold plate and HV connectors are individually valuable and are exactly the expensive, long-lead items in any custom converter build. Six units is a substantial SiC inventory.

---

## 6. The compressor and motor outputs — honest answer

**Recommendation: do not repurpose the 48 kW compressor inverter for workshop ventilation.**

This is the one place where the plan should change. The reasoning:

- **Wrong machine.** That inverter drives an ultra-high-speed centrifugal compressor — ZINSIGHT's HS-series PMSMs run at 90–120 krpm, i.e. fundamental frequencies in the hundreds to >1000 Hz. The sensorless FOC, observer tuning, current-regulator bandwidth, modulation scheme and deadtime compensation are all built for a very specific low-inductance machine. A 4-pole 1450 rpm induction fan motor at 50 Hz is a fundamentally different control problem.
- **SiC dv/dt will destroy a standard motor.** Switching edges of 10–50 kV/µs wreck standard winding insulation and cause bearing currents. You would need an inverter-duty motor *plus* a dv/dt or sine filter.
- **Strategy A gives you no access anyway** — the firmware will only spin that motor as part of a fuel-cell air-supply loop.
- **Strategy B means writing an entire second motor-control firmware stack** for a job worth a few hundred dollars.
- **A commodity 3-phase VFD** for a workshop extraction fan is off-the-shelf, certified, warranted, and costs less than a day of your time.

**What those inverter legs are genuinely good for:** driving the unit's *own* thermal management — the coolant pump and radiator fan for the DC/DC's liquid loop. That is a real, necessary function, the hardware is sized for it, and under Strategy A the existing firmware already knows how to do it. The BOP harness is literally labelled 水泵 (water pump). Keep that capability; don't fight it.

---

## 7. Better use of six units

Rather than extracting different functions from one unit, extract the *same* function from several. Because you have six:

- **Multiple independent MPPT channels** — one unit per array orientation or per roof plane. Independent MPPT per orientation is worth real yield on a non-uniform roof, and every unit after the first is a copy-paste of solved work.
- **N+1 redundancy** on a single array — lose one, keep generating.
- **A DC-DC stage between the HV battery bus and a 48 V house bus** — same topology, same skills, same toolchain.

This turns "six boxes doing nothing" into a modular DC microgrid where all engineering effort compounds instead of fragmenting across six unrelated problems.

---

## 8. Safety and Australian regulatory position

This needs stating plainly once.

- Any PV array is governed by **AS/NZS 5033**; battery storage by **AS/NZS 5139**; the fixed installation as a whole by **AS/NZS 3000**. Above 60 V DC you are in DVC-B/C and treated as hazardous LV. AS/NZS 3000 covers up to 1500 V DC, so all of this is squarely in scope.
- A repurposed automotive converter has **no CEC listing, no AS/NZS 4777.2 certification and no IEC 62109 approval**. It cannot lawfully form part of a grid-connected installation, it will not attract STCs or rebates, an inspector will not issue a Certificate of Electrical Safety for it, and an insurer would have a clean denial in a fire claim.
- **The workable path** is to treat it as **R&D / prototype equipment on a dedicated test array** — its own array, its own isolators and signage, its own battery in a compliant enclosure, feeding a defined test load. Physically and electrically separate from the building's fixed wiring. Not exporting, not backing up the building. Involve a licensed electrician for anything touching fixed wiring.
- **Keep the automotive safety features.** The HVIL, insulation monitoring, precharge sequencing and fusing in that box represent safety engineering well above typical DIY solar practice. They are assets. Do not bypass them for convenience during bring-up.

At 600 A and 750 V this is genuinely dangerous hardware. The DC-link capacitors store lethal energy after power-down — verify discharge before touching anything, every time.

---

## 9. Next steps — Phase 0 (non-destructive, before applying any power)

The single highest-value action is reading part numbers. That alone answers most open questions.

1. **Photograph and identify every IC**, at high resolution and good light:
   - The large central IC on `EB001` (the MCU or FPGA) — *this is the most important single data point in the whole project*
   - Gate driver ICs on the power-stage boards
   - Isolated amplifiers / current-sense front ends
   - The CAN transceiver near `J2`
   - The auxiliary supply controller on `EB006`
2. **Read the SiC module part markings** (under the gate driver PCBs) — Wolfspeed CAB/CAS series or ZINSIGHT ZiPACK. Gives you true voltage/current ratings and a datasheet.
3. **Ring out the HV path**: input terminals → fuses → precharge → contactor → inductor → SiC → output. Confirm whether it is a plain boost, buck-boost, or isolated topology.
4. **Count DC/DC phases** — count inductors and current sensors. Determines whether phase shedding is available.
5. **Pin out `J2` (EXT)** — locate CAN H/L, LV supply, ignition/wake and HVIL loop pins.
6. **Investigate the unpopulated 10-way header** on `EB001` — likely JTAG/SWD. Confirms the MCU family and whether debug access is locked.
7. **Decode the QR/barcode labels** (`PFX03 A00103`, `22030051`) — may map to a catalogue part number worth chasing with ZINSIGHT or the vehicle OEM.

### Phase 1 — LV power only, no HV

8. Apply 12–24 V to the LV supply with **nothing on the HV side**. Watch the 8 status LEDs (`D5`–`D12`). Sniff `J2` with a USB-CAN adapter at 250 kbit/s and 500 kbit/s. Log everything.
9. If the unit transmits heartbeat or status frames unprompted, Strategy A is live. If it is silent or immediately faults, that is early evidence for Strategy B.

### Phase 2 — decision point

Go/no-go on Strategy A based on Phase 1. If no-go, begin scoping the gate driver ribbon interfaces for the control-board transplant.

---

## 10. Open question

**What vehicle or system did these come out of?** If the units are from a known Chinese FCEV platform — a hydrogen bus, truck or forklift — the CAN matrix may exist in service literature or on Chinese technical forums. That would collapse most of the Strategy A investigation from weeks into days. It is the highest-leverage unknown remaining.

---

## Sources

- [Wolfspeed and ZINSIGHT Enhance Efficiency in Fuel Cell Vehicles with Silicon Carbide Technology](https://www.wolfspeed.com/company/news-events/news/wolfspeed-and-zinsight-enhance-efficiency-in-fuel-cell-vehicles-with-silicon-carbide-technology/)
- [ZINSIGHT Boosts Efficiency in EV E-Compressor Controllers with STMicroelectronics' SiC — Power Electronics News](https://www.powerelectronicsnews.com/zinsight-boosts-efficiency-in-ev-e-compressor-controllers-with-stmicroelectronics-sic/)
- [Zinsight to use Wolfspeed SiC MOSFETs for fuel cell vehicles — Compound Semiconductor](https://compoundsemiconductor.net/article/113748/Zinsight_To_Use_Wolfspeed_SiC_Mosfets_For_Fuel_Cell)
- [ZINSIGHT Technology (Shanghai) Co., Ltd. — 致瞻科技](https://www.zinsight-tech.com/)
- [ZINSIGHT DM60 liquid-cooled DC/DC module](https://www.zinsight-tech.com/product_details_1/5.html)
- [Battery Installation Safety Requirements Under AS/NZS 5139:2019](https://ipromiseaustralia.com.au/wp-content/uploads/2025/06/Battery-Installation-Safety-Requirements-Under-ASNZS-51392019-standard.pdf)
- [Battery Location Restrictions from AS/NZS 3000:2018 — GSES](https://www.gses.com.au/battery-location-restrictions-from-as-nzs-30002018/)
- [Australian Solar Standards, Regulations, Rules & Guidelines Explained — SolarQuotes](https://www.solarquotes.com.au/blog/solar-guide-to-regulations/)
