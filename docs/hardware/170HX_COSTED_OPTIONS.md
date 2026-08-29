# 8× CMP 170HX — Three Costed Build Options

**Prepared:** 15 August 2026 · Sydney, AUD
**Owned already:** 8 × CMP 170HX · AMD EPYC 7763
**FX used:** USD 1 = A$1.414 (AUD/USD 0.7072, 14 Aug 2026) · EUR 1 = A$1.633 (13 Aug 2026)
**Landed method:** (item + international shipping) × 1.10 GST. Computer hardware is duty-free under the AU tariff; consignments over A$1,000 attract GST at the border. Add 2–3% for your card's FX spread.

---

## 0 · Recommendation

**Buy the Gigabyte G292-Z20 — but only revision A00.** It is the cheapest of the three, it is the *only* 8-card configuration anyone has actually measured with these cards, and since you haven't bought water blocks there's no sunk cost pulling you the other way.

Three findings moved this from "worth pricing" to "clearly right":

1. **The Bykski GPU blocks are US$312 each, not the US$120–180 I estimated.** Eight is **A$4,069**, and the US warehouse shows *low inventory* — you will not get eight without a China lead time. Water just became the single most expensive line in the build after RAM.
2. **The watercooling parts channel has thinned out badly.** At PC Case Gear the EK-XTOP Revo D5 pump, Alphacool G1/4 fittings and EK Ekoolant EVO are all discontinued or out of stock. This is now a scavenger hunt, not a shopping list.
3. **The ROMED8-2T is out of stock at every Australian source I could find**, and there's no live used listing at any price. That's a hard blocker on both DIY paths.

Meanwhile the chassis route deletes the motherboard, PSUs, PSU sync, EPS adapters, fan-out hardware, frame, risers, blocks, pump, radiators and coolant in one purchase.

> ⚠️ **The single most important thing on this page: rev 100 is Rome-only. Your 7763 is Milan and will not POST in it.** Most cheap listings — including the US$1,280 one — are titled "EPYC 7001/7002". Get the revision **in writing** before paying.

---

## 1 · The three options

### Common to all three

| Item | AUD | Note |
|---|---|---|
| 8 × 32 GB DDR4-3200 2Rx4 RDIMM (refurb) = **256 GB** | **$2,190–3,220** | Widest uncertainty in the build — see §3 |
| 4 TB NVMe (Samsung 990 Pro, PCCG, in stock) | **$1,599** | All the A$799–899 4TB drives are OOS/discontinued |
| **Subtotal** | **$3,790–4,820** | |

---

### Option A — ROMED8-2T + open frame + water

| Item | AUD |
|---|---|
| ASRock Rack ROMED8-2T | $850–1,413 ⚠️ **OOS everywhere** |
| Bykski CPU-SP3-SR block | $216 |
| **8 × Bykski N-TESLA-A100-X-V2 @ US$312** | **$4,069** ⚠️ low inventory |
| 2 × 360 rad + 2 pumps + res + 16 fittings + tubing + coolant | $1,100–1,600 ⚠️ several SKUs discontinued |
| Fan-out: 2 × quad-OCuLink host + 8 cables + 8 ATX-powered adapters | $1,182 |
| 2 × Seasonic PRIME TX-1600 + Add2PSU + 8 × PCIe→EPS | $1,944 |
| Open 8-GPU frame + risers/brackets | $180–500 |
| Dedicated 15A circuit (1 × at `-pl 160`) | $470–1,215 |
| **Subtotal** | **$10,011–12,239** |
| **+ common** | |
| **TOTAL** | **~$13,800–17,060** |

---

### Option B — ROMED8-2T + open frame + blower air

| Item | AUD |
|---|---|
| ASRock Rack ROMED8-2T | $850–1,413 ⚠️ **OOS everywhere** |
| Noctua NH-U14S TR4-SP3 (Centre Com, in stock) | $189 |
| **4 × Arctic P12 Pro** (5-pack) — the *validated* config: 2 × 120 mm per 4 cards, **under 65 °C at `-pl 160`** | **$49** |
| Ducting/shrouds — self-printed (Bambu A1 ≈ $450) or cardboard-and-tape prototype first | $0–510 |
| *Alternative:* 8 × San Ace B97 blowers + printed shrouds | *($320 + $510–3,600)* |
| Brackets/hardware | $150 |
| Fan-out | $1,182 |
| 2 × Seasonic PRIME TX-1600 + Add2PSU + 8 × PCIe→EPS | $1,944 |
| Open 8-GPU frame + risers | $180–500 |
| Dedicated 15A circuit | $470–1,215 |
| **Subtotal** | **$5,014–7,152** |
| **+ common** | |
| **TOTAL** | **~$8,800–11,970** |

> The Arctic P12 Pro line is not a compromise — it's the closest analogue in the community data to an 8-card open build, and it came in **under 65 °C at `-pl 160`**, which is inside the ≤70 °C target. Blowers and printed shrouds are the *expensive* air path; two 120 mm fans per four cards is the cheap one, and it's the one with a measurement behind it.

---

### Option C — Gigabyte G292-Z20 rev A00 ⭐

| Item | AUD |
|---|---|
| **G292-Z20 barebones, rev A00** — verified listing titled "for AMD 7002/**7003**", US$1,663 + US$188 ship | **$2,880** |
| *(the US$1,280 listing = **$1,810** — but titled "7001/7002", almost certainly rev 100. **Ask.**)* | *($1,810 if rev A00)* |
| 8 × MODDIY "GPU 8-pin → 8-pin **CPU/EPS**" cables for Gigabyte servers, €18.59 ea | $245 |
| 8 × Arctic S8038-10K fans (noise fix — optional but budget it) | $250–350 |
| Motherboard | **$0** — MZ22-G20 included |
| CPU heatsink | **$0** — 25ST1-44320I-A0R included, rated for 280 W |
| PSUs | **$0** — 2 × Delta DPS-2200AB-2 included |
| Fan-out / risers / frame / blocks / pump / rads | **$0** — all included or unnecessary |
| 2 × dedicated circuits + C19 cordsets (PSUs are **2+0, not redundant**) | $940–2,430 |
| **Subtotal** | **$4,315–5,905** |
| **+ common** | |
| **TOTAL** | **~$8,100–10,730** |

---

## 2 · Side by side

| | **A — Water** | **B — Air, frame** | **C — G292-Z20** |
|---|---|---|---|
| **Total** | **$13,800–17,060** | **$8,800–11,970** | **$8,100–10,730** |
| Sourcing risk | 🔴 board OOS, blocks low stock, loop SKUs discontinued | 🟠 board OOS | 🟡 must confirm rev A00 |
| Validated by anyone? | ❌ no 8-card water build published | 🟠 4-card analogue only | ✅ **8 cards, 60 °C @ 254 W, measured** |
| Noise | 🟢 near-silent | 🟠 moderate | 🔴 *"louder than a jet engine"* — 8 × 80 mm @ 16,300 rpm |
| Build labour | 🔴 weeks | 🟠 days | 🟢 hours |
| Leak risk | 🔴 real, over A$20k of hardware | 🟢 none | 🟢 none |
| Where it lives | anywhere | anywhere | 800 mm deep, 30 kg, 300 mm clear each end, needs its own room |
| Reversible? | ❌ blocks are card-specific | ✅ | ✅ resells at close to cost |
| Time to first token | 🔴 longest | 🟠 medium | 🟢 **fastest** |

---

## 3 · What actually drives the cost, in order

**1 · RAM — a 3× spread, and it's the largest line either way.** 8 × 32 GB refurb runs **A$2,190 to A$5,310** depending purely on which listing you catch; 8 × 64 GB runs **A$3,730 refurb to A$9,070 new**. Server DRAM contract prices jumped 50% with only ~70% of orders being filled, and refurb DDR4 is up 30–50% off late-2025 lows. **Buy RAM first, everything else second.** Take 8 × 32 = 256 GB; per the last note, 512 GB buys you restart speed and nothing else.

**2 · Electrical — A$470 to A$2,430**, entirely dependent on switchboard distance and spare ways. Sydney sparky rates are A$92–170/hr, A$470–1,215 per dedicated outlet. This is load-bearing, not an afterthought — Seasonic's own TX-1600 page states it "requires a 15 amp power input", and the G292's 2+0 PSUs want two circuits.

**3 · Water blocks — A$4,069** and the reason Option A is A$5,000 clear of the others.

**4 · Shrouds, if you go the blower route — a 7× spread.** A$960–3,600 at a service bureau versus ~A$510 to buy a Bambu A1 and print them yourself. At eight parts, buying the printer wins decisively. Or skip both and use the Arctic P12 Pro config.

---

## 4 · What the G292-Z20 research settled

**Good news that de-risks the whole project:**

- **BAR1 on the 170HX is 64 MiB.** (BAR0 16 MB, BAR1 64 MB, BAR3 32 MB, Resizable BAR unavailable.) The MMIO exhaustion worry from the build spec is **dead** — unlike A100s with 32–64 GB BARs, eight of these will not hit the 8-GPU BAR wall. Enable Above 4G Decoding anyway, but this was the biggest unknown and it resolved in your favour.
- **CPU is covered.** Rev A00 spec: "AMD EPYC 7003 Series… up to 64-core", "cTDP up to 280W", "Fully support 280W". Your 7763 is exactly 64C/280W. Heatsink included (25ST1-44320I-A0R). *Flagged: I could not retrieve Gigabyte's per-SKU validated CPU list naming the 7763, nor a minimum BIOS. Ask the seller for the BIOS version.*
- **The card fits.** Chassis limit 285 × 111.5 × 39.5 mm; the 170HX PCB is 270 mm. *Minor flag: it's ~290 mm with the EPS connector plugged, but Gigabyte's limit measures the card and the chassis was built for A100 PCIe, which uses the identical rear-facing EPS connector. Bring a tape measure.*
- **Thermals are proven.** The community wiki's cooling table, verbatim: *"Stock passive heatsink in a datacenter chassis (Gigabyte G292-Z20, 80 mm fans) | peak 60 C at 254 W | 8-card rental; 'louder than a jet engine' | medium [confidence]."* That's 8 cards, stock passive heatsinks, stock chassis fans, comfortably under the 70 °C target.

**Things to handle:**

- **GPU power cables.** The backplane presents a proprietary **Gigabyte 8-pin**; the *cable* decides the GPU end. MODDIY sells both a **"GPU 8 Pin → 8 Pin CPU"** (EPS — the one you want, listed for V100/A100/A30/A40) and a PCIe variant. **Assume the used chassis arrives with the wrong ones.** Order 8 × EPS variant (€18.59 ea ≈ A$245) before the chassis lands, and physically check the keying against one card before powering anything. The card's own dual-PCIe→EPS Y adapter often won't fit — most PSU-integrated EPS cables have oversized retention clips.
- **PSUs are 2+0, not 1+1.** Delta DPS-2200AB-2, **200–240 V / 12.6 A → ~2159 W each** (only ~1159 W on 110 V — irrelevant here, and Australia's 240 V is an advantage for once). **C20 inlet, needs C19 cordsets.** Both must be live. Two separate circuits.
- **The fans are a real load.** 8 × Delta PFM0812HE-01BFY at 16,300 rpm; Level1Techs users report up to 7 A each at full tilt. That's why the 2 × 2200 W budget exists.
- **Noise is the genuine cost of this option.** There are no BIOS fan settings — control is via the **BMC web UI** (default admin / chassis serial): custom fan policies, initialise GPU fans at ~20% duty and hold, constrain curves to 80 °C. Two working fixes reported: 4-pin **dummy fan plugs** to suppress critical alerts (a missing GPU fan forces 100% duty), and **replacing all 8 fans with ARCTIC S8038-10K** — significantly quieter *and* lower power. Note that `freeipmi` sensor-disabling does **not** survive BMC warm resets.
- **The 8 GPU slots sit behind Microchip Switchtec Gen4 switches** (risers CRSG421 ×2, CRSG422 ×2, plus CRSG01A ×2 for two low-profile x16). Irrelevant here — the cards negotiate Gen1 x4 and have no P2P, so switch oversubscription cannot bite.
- **Physical:** 2U, **448 × 87.5 × 800 mm**, 22.5 kg bare / ~30 kg loaded, L-shape rails included. It runs fine on a bench — it's self-supporting — but needs ~300 mm clear front and rear. Most home racks are too shallow; you want 900 mm+ external.

**Alternatives checked, none better:** G292-Z40 (dual socket, **240 W CPU cap — kills the 7763**), G292-Z22 (Rome only), G292-Z43 (16 × *single*-slot — your cards are dual-slot), Supermicro AS-4124GS-TNR (dual socket). **There is no single-socket 4U 8-GPU AMD server from Supermicro** — a 4U would be much quieter with 92 mm fans, but the option doesn't exist.

---

## 5 · Recommended sequence

**Phase 1 — de-risk, ~A$1,000, do this before committing to anything**

1. **Confirm the SKU.** `lspci -nn | grep 20c2` (8 GB Hynix → 64 GB) vs `2082` (10 GB Samsung → 40 GB only). Everything depends on this and it costs nothing.
2. Unlock **one** card on any spare host. Verify 65536 MiB, count `POST-WRITE` lines in dmesg, check `HW Power Brake Slowdown` is Not Active.
3. **48 h `gpu-burn` + your own checksum validation.** There is no ECC and no error telemetry — this is the only error-rate baseline you will ever have, and it's the risk that decides whether this hardware is appropriate for calibration work at all.
4. **Buy RAM now**, ahead of everything else. Prices are moving the wrong way and only ~70% of orders are being filled.

**Phase 2 — the chassis**

5. Message both eBay sellers: *"Please confirm the revision — rev 100 or rev A00 — and the current BIOS version."* If the **US$1,280 unit is rev A00**, that's the deal of the build (A$1,810 landed, free FedEx, import fees prepaid). If not, take the US$1,663 unit at A$2,880.
6. Order 8 × MODDIY Gigabyte-8-pin → **CPU/EPS** cables at the same time. They'll arrive before the chassis.
7. Have the electrician in while it ships — two dedicated circuits, C19 cordsets.

**Phase 3 — bring-up**

8. Unlock all 8: `sudo ./install.sh --profile=8gb`, then **cold** shutdown (warm reboot fails). Verify `dmesg | grep -c POST-WRITE` **equals 8**.
9. BIOS: Above 4G Decoding **on**, CSM **off**, PCIe link speed **Auto** everywhere, ReBAR **off**, IOMMU `pt`, cTDP as you like (280 W is supported here).
10. `-pl 160`, then tune BMC fan curves. Swap to Arctic S8038-10K if it's unbearable.
11. Reproduce the GLM-5.2 W4A16 run — `lowbitcoffee/GLM-5.2-W4A16`, PP8, TP1, vLLM 0.20.2 + PR #38476, `TRITON_MLA_SPARSE`, util 0.90, block 64. **Measure decode.**
12. In parallel, benchmark **LTX-2.5 in BF16**. This is the layer most likely to exceed expectations and the one with a billable product attached.

**Phase 4 — only if noise forces it**

13. Move the cards to water later. The chassis resells at close to what you paid, the blocks were always the expensive part, and by then you'll know from real workloads whether the machine earns them. **Deferring A$5,000 until you have a measured decode number is the whole argument for this path.**

---

## 6 · The one thing to decide before ordering

**Where does it live?** *"Louder than a jet engine"* is not hyperbole for eight 80 mm fans at 16,300 rpm, and it's the only material downside of the recommended option. If there's a garage, shed, plant room or comms cupboard with 240 V and ventilation, Option C wins outright. If this has to sit anywhere near people even after the Arctic fan swap, **Option B** — frame, four Arctic P12 Pros, `-pl 160` — is the fallback at roughly A$700–1,200 more, and it keeps the door open to water later. Option A only makes sense once you have measured revenue coming off the machine.

---

## Sources

**Chassis:** [Gigabyte G292-Z20 rev A00](https://www.gigabyte.com/Enterprise/GPU-Server/G292-Z20-rev-A00) · [rev 100](https://www.gigabyte.com/Enterprise/GPU-Server/G292-Z20-rev-100) · [datasheet v1.0 (PDF)](https://download.gigabyte.com/FileList/DataSheet/G292-Z20_datasheet_v1.0.pdf) · [IT Creations](https://www.itcreations.com/gigabyte/gigabyte-g292-z20-gpu-server) · [Happyware rev A00 new €4,119](https://happyware.com/uk-en/gigabyte-6ng292z20mr-00-g292-z20) · [eBay US$1,280 (verify revision)](https://www.ebay.com/itm/395580978367) · [eBay US$1,663 "7002/7003"](https://www.ebay.com/itm/317431247078) · [L1T fan/BMC thread](https://forum.level1techs.com/t/homelab-gigabyte-g292-z20-issues-disabling-fans/206933)

**170HX wiki:** [cooling](https://raw.githubusercontent.com/Consensus-Protocol/cmp170hx/main/docs/operations/cooling.md) · [power-and-psu](https://raw.githubusercontent.com/Consensus-Protocol/cmp170hx/main/docs/operations/power-and-psu.md) · [board-and-variants](https://raw.githubusercontent.com/Consensus-Protocol/cmp170hx/main/docs/hardware/board-and-variants.md) · [physical-mods](https://raw.githubusercontent.com/Consensus-Protocol/cmp170hx/main/docs/operations/physical-mods.md) · [multi-gpu](https://raw.githubusercontent.com/Consensus-Protocol/cmp170hx/main/docs/procedures/multi-gpu.md)

**Parts & pricing:** [MODDIY Gigabyte GPU→CPU/EPS cable](https://www.moddiy.com/products/GPU-8-Pin-to-8-Pin-CPU-Power-Cable-for-Gigabyte-GPU-Servers.html) · [MODDIY PCIe→EPS adapter](https://www.moddiy.com/products/5575/PCIE-8-Pin-to-ATX-CPU-EPS-8-Pin-Adapter-Cable-10cm.html) · [Bykski N-TESLA-A100-X-V2 US$311.99](https://www.bykski.us/products/bykski-metal-pom-gpu-water-block-and-backplate-for-nvidia-tesla-a100-40gb) · [Bykski CPU-SP3-SR](https://www.bykski.us/products/bykski-cpu-sp3-sr-durable-metal-pom-cpu-water-block-for-amd-epyc-socket-sp3-lga-4094-continuous-usage) · [PCCG Seasonic PRIME TX-1600 A$889](https://www.pccasegear.com/products/63806/seasonic-prime-tx-1600-titanium-1600w-power-supply) · [PCCG Arctic P12 Pro 5-pack A$49](https://www.pccasegear.com/products/69958/arctic-p12-pro-pwm-pst-120mm-fan-black-5-pack) · [PCCG Samsung 990 Pro 4TB A$1,599](https://www.pccasegear.com/products/63766/samsung-990-pro-nvme-pcie-gen4-ssd-4tb) · [Centre Com Noctua NH-U14S TR4-SP3 A$189](https://www.centrecom.com.au/noctua-nh-u14s-tr4-sp3-cpu-cooler) · [RIITOP quad-OCuLink](https://www.riitop.com/products/riitop-pcie-to-oculink-adapter-4-port-pcie-4-0-x16-to-sff-8612-sff-8611-female-full-speed-64gbps-4port-for-egpupci-e-x4x4x4x4-bifurcation-required) · [C-Payne](https://c-payne.com/) · [ASRock Rack ROMED8-2T](https://www.asrockrack.com/general/productdetail.asp?Model=ROMED8-2T) · [WISP.net.au ROMED8-2T A$1,413 (OOS)](https://wisp.net.au/asrock-rack-romed8-2t-motherboard.html)

**Market conditions:** [Server DRAM +50%, 70% fill rate](https://www.techpowerup.com/342331/server-dram-pricing-jumps-50-only-70-of-orders-getting-filled) · [datacenterdisk DDR4 live pricing](https://datacenterdisk.com/server-ram/ddr4) · [Trading Economics AUD](https://tradingeconomics.com/australia/currency) · [Powertech Electrical Sydney rates](https://powertechelectrical.com.au/electrician-cost/power-point-installation-cost/)

**Flagged unverified:** Gigabyte's validated CPU list naming the 7763 · minimum BIOS for Milan on rev A00 · thermal rating of heatsink 25ST1-44320I-A0R · used ROMED8-2T pricing (no live listing) · HP 1200W PSU option (listing 404'd) · G292-Z20 dB(A) figure (all noise claims are community-anecdotal) · whether the US$1,280 chassis is rev 100 or A00.
