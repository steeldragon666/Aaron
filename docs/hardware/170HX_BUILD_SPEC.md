# 8× CMP 170HX — Host Platform and Fan-Out Build Spec

**Prepared:** 15 August 2026
**Given:** EPYC 7763 in hand, Bykski N-TESLA-A100-X-V2 water blocks, 8 × CMP 170HX
**Companion to:** `claude/170HX_HARDWARE_BRIEF.md`

---

## 0 · The short answer

| Question | Answer |
|---|---|
| **Motherboard** | **ASRock Rack ROMED8-2T** — 7 × true Gen4 ×16 + 2 × OCuLink ×4. ~US$700–900. |
| **"Board to plug them all into"** | **Don't buy one.** You need *connectors*, not a switch. 2 × quad-OCuLink host cards + 8 cables + 8 OCuLink→×16 device adapters ≈ **US$642 / ~A$1,000**. |
| **PCIe switch?** | **No.** No P2P, no bandwidth pressure, no lane shortage. €1,250 buys ~A$1,000/link against A$125/link for OCuLink. |
| **Can 8 water-blocked cards sit in the board?** | **No.** Open frame, all 8 remoted on 50–75 cm cables. |
| **The alternative you should at least price** | **Gigabyte G292-Z20 barebones, ~US$1,280** — *is* the 8×x16 board you're describing, plus chassis and 2 × 2200W. But it's 2U air, jet-engine loud, and makes the Bykski blocks pointless. |

### The lane arithmetic that drives all of it

Stock, each 170HX negotiates **PCIe Gen1 ×4** (Gen2 ×4 after the free software unlock). Eight cards = **32 lanes** of a 128-lane budget, and **~13.6 GB/s aggregate** against a single Gen4 ×16 uplink's ~32 GB/s.

You are not lane-starved. You are not bandwidth-starved. You are **connector-starved and space-starved.** Every expensive option on the market solves the first two problems.

> If you ever do the capacitor mod, 8 × ×16 = 128 lanes = 100% of the single-socket budget with nothing left for NIC, boot NVMe or SATA. **No single-socket SP3 board can do 8 × ×16.** That would mean a dual-socket ROME2D32GM-2T or a PEX 88096 switch — four figures to chase the ~2% the mod actually delivers. Don't.

---

## 1 · Motherboard

### Recommended: ASRock Rack ROMED8-2T

ATX 305 × 244 mm · **7 × PCIe 4.0 ×16 (all electrically ×16)** · 2 × OCuLink Gen4 ×4 · 2 × miniSAS HD · 8 DIMM (1DPC, 8-channel) · AST2500 IPMI · dual 10GbE X550-AT2

**The clean 8-link trick — no bifurcation needed at all.** The manual's `PE16_SEL`/`PE8_SEL` jumper table shows PCIE2's ×16 group is a mux:

```
PCIE2 x16  – M2_1/SATA_4_7/OCU1/OCU2 Disabled   (default)
PCIE2 x8   – M2_1/SATA_4_7 Enabled  – OCU1/OCU2 Disabled
PCIE2 off  – M2_1/SATA_4_7 Disabled – OCU1/OCU2 Enabled
PCIE2 off  – M2_1/SATA_4_7/OCU1/OCU2 Enabled     ← use this one
```

State 4 gives you **slots 1, 3, 4, 5, 6, 7 (six ×16) + OCU1 + OCU2 = 8 independent CPU root ports**, and you keep M.2 boot, SATA, 10GbE and IPMI. Clean 1:1 IOMMU groups, no bifurcation, no switch.

⚠️ **Two caveats, both manageable:**

| Issue | Detail | Fix |
|---|---|---|
| **280W TDP** | ServeTheHome's review states ROMED8-2T has a **225W maximum TDP**. ASRock publishes no figure and lists >225W parts as supported — unresolved. | The 7763's **cTDP is configurable 225–280W**. Set 225W in BIOS. Your CPU is idle anyway (2 cores per GPU). Costs you nothing. |
| **×4×4×4×4 bifurcation** | Not documented on ROMED8-2T. The manual shows only a per-slot "Link Width" cap. | You don't need it for the 6-slot + 2-OCuLink route. If you want it for the frame build, **verify in BIOS before ordering adapters.** |

### Alternatives

| Board | Why you'd pick it | Why you wouldn't |
|---|---|---|
| **Supermicro H12SSL-i** (~US$875 open-box) | **Documented** per-slot bifurcation: ×16 slots offer `Auto/×16/×8×8/×4×4×8/×4×4×4×4`, ×8 slots offer `×4×4`. Up to 24 independent ×4 links from 7 slots. Often cheaper used. | Only 5 × ×16 + 2 × ×8. Milan-X wants BIOS 2.3+. |
| **Gigabyte MZ32-AR0 r3.x** (~US$649 used) | **Only board here that publishes 280W TDP support.** **16 DIMM slots (2DPC)** — a genuine RAM upgrade path, which matters enormously at 2026 DDR4 prices. Cheapest. | E-ATX 305×330. Only 4 × Gen4 ×16 + 1 ×8 + Gen3 slots. Fine for the frame build, useless if you ever want 7 × ×16. |
| ~~Tyan S8030~~ | — | **240W max — rules out the 7763.** |
| ~~ASUS KRPA-U16~~ | — | EOL. |

**Pick:** ROMED8-2T at ≤US$900. If TDP headroom bothers you or you want the 16-DIMM upgrade path, **MZ32-AR0** — and given the RAM situation in §4, that's a stronger argument than it looks.

---

## 2 · The fan-out layer

### What you're actually buying

With water blocks on, all 8 cards live on an open frame, not in the board. So the board's slots become *host adapter* sockets, and you need 8 cabled links out.

**OCuLink is the community's answer and it's cheapest.** Independent measured evidence: an RTX 3090 benchmarked three ways across 11 llama.cpp models — direct slot (Gen4 ×16), ribbon riser (**fell back to Gen1** ×16), and **OCuLink (full Gen4 signalling at ×4)**. Spread across all three: **under 1–2%.** The ribbon riser degraded the *generation*; OCuLink did not.

### Bill of materials — fan-out

| Qty | Part | Unit USD | Total |
|---|---|---|---|
| 2 | RIITOP PCIe ×16 → **Quad OCuLink SFF-8612** host card *(needs ×4×4×4×4)* | $32.99 | $66 |
| 8 | RIITOP OCuLink 4i M–M cable, 50 cm | $21.99 | $176 |
| 8 | RIITOP **OCuLink → PCIe ×16** device adapter — **6-pin/ATX powered** | $49.99 | $400 |
| | **Total** | | **US$642 ≈ A$1,000 landed** |

⚠️ **Buy 6-pin/ATX-powered device adapters, never SATA-powered.** A SATA-powered adapter in the referenced test dropped the GPU out of Linux entirely. The AU-stocked Cablecc unit on Amazon.com.au is a SATA-power design — avoid it.

⚠️ **Buy passive. No redrivers, no retimers.** Gen4 passive copper reaches ~30–50 cm; **Gen2 reaches well past 1 m and Gen1 past 1.5 m.** A 50–75 cm Gen4-rated cable running Gen1/Gen2 has 2–3× the loss budget it needs. C-Payne's REDRIVER host adapter is €80 vs €30 passive, and MCIO/Gen5 retimers are €240. That's the single biggest free saving in this build.

### If the BIOS won't do ×4×4×4×4

Three fallbacks, in order of preference:

1. **ROMED8-2T state-4 route** — 6 slots + 2 OCuLink, zero bifurcation. Two of the eight cards go in slots (or on short host adapters), six get cabled. Cost of the extra links: ~€170 / A$290 in C-Payne SlimSAS gear.
2. **×8×8 instead** — 4 × C-Payne SlimSAS passive host adapters (€30 ea) + 8 cables (€30) + 8 device adapters (€40) ≈ €680 / A$1,150. ×8×8 is far more commonly supported than ×4×4×4×4.
3. **PEX 88096 "free-splitting" board** (~US$400 on eBay/AliExpress) — no bifurcation required at all. This is insurance, not a design choice.

### C-Payne reference prices (Germany, [c-payne.com](https://c-payne.com/))

| Part | Price |
|---|---|
| SlimSAS PCIe gen3(4) Host Adapter ×16 **PASSIVE** (→ 2× SFF-8654 8i; supports ×16/×8×8/×8×4×4/×4×4×8/×4×4×4×4) | **€30** |
| SlimSAS PCIe gen4 **Device Adapter ×4** (×4 electrical / **×16 mechanical**) | **€40** |
| SlimSAS PCIe gen4 Device Adapter ×8/×16 | €40 |
| SFF-8654 8i cable, 45 or 75 cm, 85 Ω | €30 |

⚠️ C-Payne does **not** stock an 8i → 2× 4i breakout cable — you'd need a third-party (10Gtek make one, PCIe 4.0, 85 Ω, 0.3 m).
⚠️ Every C-Payne device adapter carries a mandatory 12V input and a blunt warning: *"DO NOT connect the wrong power connector, it will destroy the Adapter and your Device."*

---

## 3 · Why not a PCIe switch

Three independent reasons, any one of which is sufficient:

1. **P2P tests False on all pairs.** A switch's headline feature — GPU-to-GPU DMA that never touches the root complex — is dead silicon on this card. You'd be paying for a capability the fuse map disabled.
2. **There is no bandwidth to multiplex.** 8 × 1.7 GB/s = 13.6 GB/s against a Gen4 ×16 uplink's ~32 GB/s.
3. **You have 128 lanes and need 32.**

**Availability is also poor.** The bare Broadcom **PEX 8796** (Gen3, 96-lane) at Mouser: **US$593 @ 1, stock 0, next inbound 18 August 2027.** The Gen5 PEX 89000-series (which includes PEX 88096) isn't stocked by any franchise distributor — AliExpress/eBay only. The only genuinely retail switch boards are C-Payne's Microchip Switchtec units, and all three are **sold out**:

| Board | Config | Price |
|---|---|---|
| Switchtec PM40084 | Gen4, 4 × ×16 | €1,250 |
| Switchtec PM40100 | Gen4, 5 × ×16 | €1,550 |
| PM50100 | Gen5, 100-lane | €2,000 |

€1,250 for four links = **~A$1,000 per GPU** against **A$125** for OCuLink. Plus 15–25W of heat, a firmware surface, and a single point of failure that takes out four GPUs.

> Digital Universe runs 2 × PEX 88096 per 8-GPU unit because he's building **4–5 identical units toward 37 cards** and wants a replicable cabled backplane. That's a fleet decision. You're building one unit.

---

## 4 · The rest of the platform

### RAM — read this before you budget anything else

**All 8 channels must be populated.** Milan bandwidth scales near-linearly with populated channels; the reference 170HX build measured ~150 GB/s real with 8 × DDR4-3200, which is what a properly populated 8-channel Milan delivers.

**Target: 8 × 64 GB 2Rx4 DDR4-3200 RDIMM = 512 GB.** Dual-rank (2Rx4) not 1Rx8 — ~5–10% more bandwidth at 1DPC. RDIMM not LRDIMM. Set **NPS1** (single flat NUMA node).

Why 512 GB: it matches VRAM 1:1, the GLM-5.2 W4A16 quant is 388 GB and vLLM streams safetensors through host memory on load, and page-caching the model directory means restarts don't re-read 388 GB from disk.

⚠️ **DDR4 RDIMM is in a shortage-driven price spike.** Median **US$8.28/GB**; 64 GB DDR4-3200 modules at **US$599 (Hynix) – US$721 (Samsung)** each. **512 GB new ≈ US$4,800 / ~A$7,400** — very plausibly more than your entire GPU spend. 32 GB modules run US$240–277.

**Buy used/pulled server RAM.** And note the trap: ROMED8-2T and H12SSL-i are **8 slots, 1DPC** — there is no "add 8 more later", only "replace all 8". **MZ32-AR0's 16 slots is the only genuine upgrade path here**, letting you start at 8 × 32 GB and add a bank later (dropping to 2933 MT/s at 2DPC with some DIMMs). At current prices that flexibility is worth real money.

**Pragmatic floor: 256 GB (8 × 32 GB).** It works. You'll feel it on every model load.

### CPU water block

SP3 needs **no special ILM or aftermarket bracket** — the socket ships with its own retention frame and the cooler mounts to threaded standoffs in it. **SP3 and TR4/sTRX4 are the same LGA4094 package with the same hole pattern**, so TR4 blocks fit. The only difference is fin orientation, which is irrelevant for water.

| Part | Notes |
|---|---|
| **Bykski CPU-SP3-SR** ⭐ | All-metal, TR4/SP3/SP6, 0.3 mm microfins, **~US$104**. Same vendor as your GPU blocks — one fitting standard, one thread pitch, one supplier. All-metal means no POM creep on a 24/7 loop. |
| Bykski CPU-SRSP3-X | LGA4094 EPYC server block, nickel-plated |
| Alphacool Eisblock XPX Pro 1U | Enterprise/1U height |
| Alphacool Eisblock XPX Pro Aurora | Needs mounting kit **12875** |
| EK-Pro CPU WB sTR / sTR Rack | Nickel + acetal |

**Check the cold plate covers the full SP3 IHS (~58 × 75 mm).** Threadripper-class plates do; AM4/LGA-115x plates do not, and a partial plate on a 64-core Milan is a throttling machine.

### GPU water blocks — fitment confirmed

**Bykski N-TESLA-A100-X-V2** is listed explicitly for *"Nvidia Tesla A100 40GB / **Nvidia CMP 170HX** / Nvidia Tesla A30 24G"* — metal + POM with backplate. There's also a **B-FRD-TESLA-A100** AIO variant naming the 170HX. Historically US$120–180 each, so **~A$1,500–2,200 for eight** (current pricing not retrievable — FormulaMod blocks fetching, PrimoChill's listing 404s).

⚠️ **Before mounting: cover every unpopulated IC footprint with thermal pad.** The block's metal pillars short across exposed copper pads and permanently kill the card. Pad the DrMOS and PMICs.

### Power

**The problem is connector count, not wattage.** 8 GPUs × 1 **EPS 8-pin** each. A flagship consumer PSU — Super Flower Leadex Titanium 1600W — ships with **1× EPS 8-pin + 1× 4+4** and *fourteen* PCIe connectors. Two of them still give you 4 native EPS.

⚠️ **PCIe 8-pin is 3×12V/5×GND. EPS 8-pin is 4×12V/4×GND. The 12V and ground positions are swapped. Plugging a PCIe cable into the card destroys it.** Use proper adapters (MODDIY, COMeap, or the eBay DE cable listed specifically for "CMP 100-210 oder 170hx").

⚠️ **Current density: 250W ÷ 12V = 20.8A.** Spread over a PCIe cable's 3 × 12V conductors ≈ 7A each — marginal at 18AWG. **Insist on 16AWG adapters.** At `-pl 160` you're at 13.3A, comfortable. Another independent argument for 160–200W.

| Item | Part | AUD |
|---|---|---|
| PSU × 2 | **Seasonic PRIME TX-1600 Titanium** — A$889 ea, in stock at PC Case Gear, full 1600W at 230V | $1,778 |
| Sync | Add2PSU 24-pin dual-PSU adapter | ~$15 |
| Adapters × 8 | PCIe 8-pin → EPS 8-pin, **16AWG** | ~$150 |
| | **Total** | **~$1,950** |

**Split: PSU-A takes host board + GPUs 1–4. PSU-B takes GPUs 5–8.** Never feed one card from two PSUs. Common chassis ground.

*Cheaper, riskier:* HP 1200W Platinum server PSUs + breakout board (the mining standard) — 2 units ≈ A$400 for 2400W. Catch: breakout boards output *PCIe* 6-pin, so you're doing 6-pin → EPS conversion on every card and must verify pinout with a multimeter eight times before connecting A$2,000 GPUs. Loud (40mm server fans). Only if you're comfortable with that.

### Australian mains

| Config | GPUs | System | Current @ 240V |
|---|---|---|---|
| Stock `-pl 250` | 2,000 W | ~2,400 W | **10.0 A** |
| **Recommended `-pl 160`** | 1,280 W | ~1,700 W | **7.1 A** |

A standard 10A GPO tops out at 2,400W and AS/NZS practice derates continuous loads to ~80% (**1,920W**). **Stock power limits sit exactly at — arguably over — the limit for 24/7 operation.**

1. **Run `-pl 160–200`.** 250→300W buys +2.8%, so the derate is nearly free, and it halves the current through every EPS adapter.
2. **If you want stock TDP, have an electrician fit a dedicated 15A or 20A circuit.** Not optional.
3. **Two PSUs on one circuit gains no headroom** — the breaker sees the sum. Dual PSU solves connector count, not supply capacity.
4. Budget ~30W/card idle (~240W, ~A$60/mo doing nothing) and a **3.5 kW split minimum** to dump the heat.

---

## 5 · Physical build

**8 water-blocked cards will not go in the board.** Not just 7 < 8:

- The block is single-slot but the **loop** isn't — G1/4 terminals and fittings add 15–25 mm past the block face, and you need bend radius for 8 parallel inlet/outlet pairs. ATX slot pitch is 20.32 mm.
- 2 kW of passive cards packed back-to-back with no air movement is a bad thermal environment for the *board*.
- 8 cards + blocks + filled loop is 12–15 kg cantilevered off PCIe slot retention.

**What to build:**

- Open mining frame (A$100–250), cards mounted vertically at **~40–50 mm pitch** — loop clearance, and you can revert to air later
- Host board mounted separately at the base
- 8 × OCuLink links, 50–75 cm (length is free at Gen2)
- Radiators on the frame, not in a case
- **Loop sizing: ~1.5 L/min per GPU → ~6 L/min for the unit.** Two GPUs in series max, four parallel pairs. Never eight in series.

### The alternative worth pricing honestly

**Gigabyte G292-Z20 barebones — US$1,280 on eBay** (2U, single SP3, **8 × PCIe 4.0 ×16 GPU slots**, 2 × 2200W, free FedEx, import fees included).

This *is* the board you were asking for. It replaces the motherboard, chassis, PSUs, risers, cables, water blocks, pump and radiators — call it **A$4,000–6,000 of avoided spend against ~A$2,000**. It's also the only 8-card configuration anyone has actually validated with these cards (60°C @ 254W on stock passive).

The costs: **2U air, described as "louder than a jet engine"**, and it makes your Bykski blocks redundant. If the noise is tolerable where this will live, it is strictly the better engineering decision. If it isn't — and in a home or office it usually isn't — the frame-and-water build is the right call and you already own the blocks.

---

## 6 · BIOS and firmware — the settings that actually matter

| Setting | Value | Why |
|---|---|---|
| **Above 4G Decoding** | **Enabled** | Non-negotiable. 8 GPUs will not all enumerate without it. |
| **CSM** | **Disabled — UEFI only** | Eight VBIOSes blow past the 128 KB legacy option-ROM shadow region. *You have an advantage: the 170HX has no display outputs, so no VGA option ROM to shadow.* Set AST2500 as primary VGA. |
| **PCIe Link Speed (all slots)** | **Auto** | Do **not** force Gen4 — it may break the Gen1→Gen2 retrain. |
| **Resizable BAR** | **Off** | It's a P2P/host-mapping optimisation and there is no P2P. Pure enumeration risk, zero gain. |
| **IOMMU** | `pt` or off | Bare metal, no SR-IOV. DMA translation on 8 devices is pure overhead. (Also: Gen2 never trains in a guest — the retrain must be driven from the upstream bridge, which a VM doesn't own. **Run bare metal.**) |
| **cTDP** | **225W** | Keeps the 7763 inside ROMED8-2T's disputed TDP ceiling at no real cost. |
| **NPS** | **NPS1** | One flat NUMA node. Simplest for vLLM under PP. |

### ⚠️ Do this before you buy eight sets of risers: measure BAR1

This is the one genuine unknown. On NVIDIA's open-kernel-modules tracker an **A100 80GB was allocated a 128GB BAR1**, with the reported failure mode being exactly yours — the big card "hogging all the available space" so other GPUs can't allocate BARs. **If the unlocked 170HX scales BAR1 with its new 64GB geometry, 8 cards could request 512GB–1TB of above-4G MMIO.** EPYC's address space handles it, but the firmware has to place the window.

```bash
# unlock ONE card, then:
sudo lspci -vvv -s <bdf> | grep -i "Region 1"
```

If BAR1 stays at the stock 8GB tier, non-issue. If it scales, the escape hatch is `NVreg_EnableResizableBar=0`, and you may need to raise MMIOHBase.

### ROMED8-2T BIOS

Latest is **4.30 (29 June 2026)** — AGESA MilanPI-SP3-1.0.0.J. Milan floor is around BIOS 3.2. **You can flash without a CPU installed** — the AST2500 runs on standby power, so plug the dedicated IPMI LAN, find its DHCP address, and flash from the web UI. There's no USB flashback button; the BMC *is* the flashback mechanism.

⚠️ **Flash BIOS and BMC as a matched set.** A 45HomeLab thread reports BIOS 4.10 + BMC 2.08.00 misbehaving while 4.10 + 2.02 was fine, resolved only with an unpublished pair from support. Note what you came from.

---

## 7 · Bill of materials

Assumes frame + water, cards already owned.

| Item | Part | USD | AUD approx |
|---|---|---|---|
| Motherboard | ASRock Rack ROMED8-2T | $700–900 | $1,100–1,400 |
| CPU | EPYC 7763 | — | *owned* |
| RAM | 8 × 64 GB 2Rx4 DDR4-3200 RDIMM (used) | $2,500–4,800 | **$3,900–7,400** |
| Fan-out | 2 × quad-OCuLink host + 8 cables + 8 device adapters | $642 | $1,000 |
| GPU blocks | 8 × Bykski N-TESLA-A100-X-V2 | $960–1,440 | $1,500–2,200 |
| CPU block | Bykski CPU-SP3-SR | $104 | $160 |
| Loop | 2 × 360 rad, D5-class pump ×2 in series, res, fittings, tubing, coolant | $600–1,000 | $950–1,550 |
| PSU | 2 × Seasonic PRIME TX-1600 + Add2PSU + 8 × 16AWG EPS adapters | — | $1,950 |
| Frame | Open 8-GPU frame + brackets | $100–160 | $150–250 |
| Boot | 2 TB NVMe (model store — 388 GB per quant) | $150 | $230 |
| **Total ex-cards** | | | **~A$10,900–16,100** |

**RAM is 35–50% of it.** If that's the blocker, start at **8 × 32 GB = 256 GB (~A$1,700)** and take the MZ32-AR0 with its 16 slots so you can add a second bank when DDR4 normalises.

*Comparison:* G292-Z20 barebones + same RAM ≈ **A$5,600–9,400** all-in, air-cooled, loud, validated.

---

## 8 · Order of operations

1. **Confirm the SKU** — `lspci -nn | grep 20c2` (8GB Hynix → 64GB) vs `2082` (10GB Samsung → 40GB only). Everything downstream depends on this.
2. **Unlock one card on a scratch host.** Verify 65536 MiB, count `POST-WRITE` lines, check `HW Power Brake Slowdown` is Not Active, and **read BAR1 with `lspci -vvv`**.
3. **48h `gpu-burn` + your own checksum validation** on that card — this is your only error-rate baseline, and there is no ECC to fall back on.
4. **Buy the board. Boot it bare. Check the BIOS bifurcation menu** for ×4×4×4×4 before ordering any fan-out hardware.
5. Buy fan-out to match what the BIOS actually offers.
6. **Loop and blocks in place before first multi-card power-on.** Brief overheating permanently degrades HBM. Targets ≤70°C core / ≤75°C memory; throttle 95, shutdown 98. Standard stress tests only draw ~60–75W because FP32 is throttled — **you cannot validate cooling with `gpu-burn`.** Validate under a real diffusion load.
7. Assemble, `-pl 160`, verify all 8 enumerate at 64 GB, then reproduce the GLM-5.2 W4A16 run.

---

## Sources

**Boards & platform:** [ASRock Rack ROMED8-2T](https://www.asrockrack.com/general/productdetail.asp?Model=ROMED8-2T) · [ROMED8-2T manual (PDF)](https://download.asrock.com/Manual/ROMED8-2T.pdf) · [STH ROMED8-2T review](https://www.servethehome.com/asrock-rack-romed8-2t-review-an-atx-amd-epyc-platform/) · [STH review p2 — 225W claim](https://www.servethehome.com/asrock-rack-romed8-2t-review-an-atx-amd-epyc-platform/2/) · [ASRock forum: BIOS flash without CPU](https://forum.asrock.com/forum_posts.asp?TID=19815&OB=ASC) · [45HomeLab BIOS/BMC pairing](https://forum.45homelab.com/t/romed8-2t-bios-l4-11-and-bmc-3-04-00/3723) · [Supermicro H12SSL manual MNL-2314 (PDF)](https://www.supermicro.com/manuals/motherboard/EPYC7000/MNL-2314.pdf) · [Gigabyte MZ32-AR0 rev 3.x](https://www.gigabyte.com/us/Enterprise/Server-Motherboard/MZ32-AR0-rev-3x) · [ASRock ROME2D32GM-2T](https://www.asrockrack.com/general/productdetail.asp?Model=ROME2D32GM-2T) · [AMD EPYC 7763](https://www.amd.com/en/products/processors/server/epyc/7003-series/amd-epyc-7763.html) · [STH EPYC lane budget](https://www.servethehome.com/why-amd-epyc-rome-2p-will-have-128-160-pcie-gen4-lanes-and-a-bonus/2/) · [L1T bifurcation thread](https://forum.level1techs.com/t/romed8u-2t-board-bifurcation/207122)

**Fan-out:** [C-Payne host adapters](https://c-payne.com/collections/slimline-pcie-adapters-host-adapters) · [device adapters](https://c-payne.com/collections/slimline-pcie-adapters-device-adapters) · [cables](https://c-payne.com/collections/slimsas-pcie-cables) · [switches](https://c-payne.com/collections/pcie-packet-switch-adapters-gen4) · [RIITOP OCuLink range](https://www.riitop.com/collections/oculink-adapter-cable) · [RIITOP quad-OCuLink host card](https://www.riitop.com/products/pcie-oculink-adapter-card-riitop-pci-e-express-16x-to-quad-oculink-sff-8612-sff-8611-internal-vroc-raid0-adapter-for-u-2-ssd-egpu-external-graphics-card-dock) · [ADT-Link F9G](https://www.adt.link/product/F9GV4.html) · [ahelpme OCuLink vs riser benchmark](https://ahelpme.com/ai/llm-inference-using-riser-extender-cable-and-oculink-cable/) · [Mouser PEX8796 — 2027 lead time](https://www.mouser.com/ProductDetail/Broadcom-Avago/PEX8796-AB80BI-G?qs=XzL5RgerQmjtO4gUOdi40g%3D%3D) · [eBay PEX88096 board](https://www.ebay.com/itm/136874311697)

**Cooling & power:** [FormulaMod Bykski N-TESLA-A100-X-V2 (lists CMP 170HX)](https://www.formulamod.com/Bykski-GPU-Block-For-Nvidia-Tesla-A100-40GB-Nvidia-CMP-170HX-High-Heat-Resistance-Material-POM-With-Backplate-Full-Cover-GPU-Water-Cooling-Cooler-Radiator-Block-N-TESLA-A100-X-V2-p3765067.html) · [Bykski CPU-SP3-SR](https://www.bykski.us/products/bykski-cpu-sp3-sr-durable-metal-pom-cpu-water-block-for-amd-epyc-socket-sp3-lga-4094-continuous-usage) · [watercooled.net SP3 block list](https://watercooled.net/finder/cpu/SP3) · [L1T TR4 vs SP3 mounting](https://forum.level1techs.com/t/tr4-vs-sp3-cooler-mounting-options-threadripper-vs-epyc/200240) · [Seasonic PRIME TX-1600 @ PC Case Gear](https://www.pccasegear.com/products/63806/seasonic-prime-tx-1600-titanium-1600w-power-supply) · [Exxact — PCIe 8-pin vs EPS 12V](https://support.exxactcorp.com/hc/en-us/articles/20180443940119-PCIe-8-pin-vs-EPS-12V-8-pin-power-connections) · [MODDIY PCIe→EPS adapter](https://www.moddiy.com/products/5575/PCIE-8-Pin-to-ATX-CPU-EPS-8-Pin-Adapter-Cable-10cm.html)

**Chassis & MMIO:** [eBay G292-Z20 barebones US$1,280](https://www.ebay.com/itm/395580978367) · [Gigabyte G292-Z20](https://www.gigabyte.com/Enterprise/GPU-Server/G292-Z20-rev-A00) · [NVIDIA open-gpu-kernel-modules BAR1 discussion](https://github.com/NVIDIA/open-gpu-kernel-modules/discussions/579) · [NVIDIA MMIO BIOS KB](https://nvidia.custhelp.com/app/answers/detail/a_id/4119/~/incorrect-bios-settings-on-a-server-when-used-with-a-hypervisor-can-cause-mmio) · [DDR4 RDIMM price tracker](https://datacenterdisk.com/server-ram/ddr4)

**Unverified — check before spending:** ROMED8-2T ×4×4×4×4 bifurcation support · ROMED8-2T 280W support (STH says 225W; ASRock publishes nothing) · ROMED8-2T onboard OCuLink usability for GPUs · 170HX BAR1 size after unlock · current Bykski block pricing · AliExpress PEX88096 pricing · all used-market prices are asking prices, not sold medians.
