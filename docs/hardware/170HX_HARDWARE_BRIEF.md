# CMP 170HX — Hardware Reality Check and the 8-Card Path

**Prepared:** 15 August 2026
**Trigger:** Three videos from the *Digital Universe* channel (`@RH-3D-EN`), plus independent verification
**Purpose:** Correct the hardware assumptions in `CONSOLIDATION_BRIEF.md` rev 2/3 and set the build sequence for the 8-card farm

---

## 0 · Executive summary — the four things that changed

1. **It is 64GB per card, not 80GB.** 80GB is a broken register configuration that folds at 40 GiB and kills the GPU. The 8GB SKU is the one you want; the 10GB SKU tops out at 40GB. Every capacity number downstream in the brief needs re-basing on **512GB total**, not 640GB.

2. **The PCIe ×16 solder mod is not worth doing for your workload.** It buys ~2% under pipeline parallelism when the weights are VRAM-resident. It is 192 hand-soldered 0402 capacitors, irreversible, and the failure mode is hard to diagnose. The free software unlock to Gen2 gets you the part that matters.

3. **This farm is a *video* machine that also does reasoning — not the reverse.** Measured: **1.8× an RTX 3090 on LTX-Video and Wan2.1**, and it holds 720p jobs a 3090 OOMs on. Against that, the one published 8-card GLM-5.2 run decodes at **30.2 tok/s single-stream**. The brief's economics were built the other way round.

4. **No ECC, no error telemetry, permanently.** On deliberately factory-disabled memory tiers. This is unfixable and it collides directly with Layer 4 of the operating design — the calibration and prediction-accuracy apparatus that is the stated moat.

---

## 1 · What the three videos actually are

All three are from **Digital Universe** (`youtube.com/@RH-3D-EN`), one builder, real hardware, ~7 months in.

| Video | What it covers |
|---|---|
| `JWH3Sh4mHug` — *Nvidia CMP 170HX upgrade! PCIe 4x to 16x* | The capacitor mod. Lanes 5–16 ship with the AC-coupling caps depopulated. He solders 0402 caps (NVIDIA used ~170nF; he substitutes 220nF), 325°C iron, microscope, multimeter continuity check per pair, verify with `nvidia-smi`/`nvidia-debugdump` link width. If one cap in the 9–16 range fails, the link collapses to ×8 — PCIe only trains at 1/2/4/8/16. |
| `KnJMLw7AL38` — *#001 DIY HOME SUPERCOMPUTER … 2TB VRAM for vLLM* | The system design. EPYC 7763 (64C — deliberately 2 cores per GPU), DDR4-3200 at ~150 GB/s real, fluid at 28°C, ~200W/card at 1290 MHz, 7.8–8.2 kW at the wall for 32 GPUs, driver 610.43, unlocker v0.2.2. |
| `guIMH9qFYL8` — *Building computer with 2.36TB VRAM* | The chassis and topology. Rebuilt 8-GPU mining frame, **2× Broadcom PEX 88096** switches per unit (Gen4 ×16 in, 96 lanes, 4 GPUs each), custom water loop, ~1.5 L/min per GPU, ~6 L/min per 8-card unit. 37 cards, 4–5 units, targeting Kimi K3 at FP8. |

**He is credible on hardware and loose on software.** His measured numbers are honest — he explicitly calls out that Gen1 ×16 gives him **3.28–3.34 GB/s full duplex**, and corrects other YouTubers who claim more. But "we can go pure FP8" is wrong: GA100 has no FP8 tensor hardware. And his 2 TB VRAM target assumes a 32-GPU cluster that has never been driver-validated.

**What he has *not* published:** a single tok/s figure from a running model. Everything is still hardware. Treat the channel as a build reference, not a performance reference.

---

## 2 · What the card actually is

| Spec | Value | Note |
|---|---|---|
| Die | GA100-105F — **same silicon as A100** | 70 SMs of 128 on the full die |
| CUDA cores | **4,480** | ⚠️ Not 8,960. GA100 SMs have 64 FP32 lanes, not 128. TechPowerUp's 8,960 is wrong and is copied everywhere, including the videos. |
| Clock | 1140 base / 1410 boost | |
| Memory (stock) | 8 GB HBM2e, 4096-bit | 10GB SKU is 5120-bit |
| Memory (unlocked) | **64 GB** (8GB SKU) / 40 GB (10GB SKU) | Per-partition capacity tier, 512 MiB → 4096 MiB × 16 |
| Bandwidth | **~1.3–1.6 TB/s measured** | A100-class. This is the card's whole argument. |
| BF16 tensor | **164–193 TFLOPS measured** (202 ceiling) | Unlocked |
| FP32 | 12.63 TFLOPS unlocked (throttled to 1/32 stock) | |
| FP64 | **Not recoverable by any known method** | Any HPC ambition is dead |
| FP8 / FP4 | **None.** sm_80 does FP64/TF32/BF16/FP16/INT8/INT4 | See §4 |
| NVLink | Fuse-disabled | |
| P2P | **False for all pairs.** Tested. | This is the fact that dictates the whole serving architecture |
| ECC | **Fuse-latched off. Permanent.** | No correctable-error counters, no row remapping, no logs |
| PCIe | Gen1 ×4 stock (0.85 GB/s) → Gen2 ×4 software (~1.7) → Gen2 ×16 soldered (5.97–6.67) | **Gen3/Gen4 are structurally impossible** — OTP fuses plus five bytes inside a signed, MAC-protected DevInit image |
| TDP | 250W, **fully passive**, no display outputs | |
| Power connector | **8-pin EPS (CPU-style)** | ⚠️ 12V and ground are swapped vs PCIe 8-pin. Forcing a PCIe cable damages the card. |

### Corrections to `CONSOLIDATION_BRIEF.md`

| Brief says | Reality |
|---|---|
| "80GB unlocked" | **64GB** on the 8GB SKU. The 80GB branch sets CFG1 to an 80GB tier but leaves LMR at `0x0000028A`, which decodes 40 GiB. `nvidia-smi` reports 80; kernels touching >40 GiB cause fatal GPU loss (Xid 154). It never merged. Sellers screenshot it anyway. |
| "PCIe ×16" | ×16 *lanes* are achievable by soldering. The *generation* is capped at Gen2 forever. Best case ~6.6 GB/s, not the "Gen 3/4 ×16 makes tensor parallelism comfortable" the brief hoped for. |
| "Gen 3/4 ×16 makes TP comfortable; Gen 1 ×16 favours pipeline parallelism" | **Pipeline parallelism is the only answer, permanently.** No P2P at any link speed. Confirmed twice: the wiki (TP2 is 2.3–2.8× worse at prefill) and the DeepSeek-V4 project (TP does 86 all-reduces per forward pass; PP moves data 3 times → 6.6× faster prefill). |
| "LTX-2.5 fits with four to five times headroom" | Correct, and better than stated — LTX-Video benchmarks at **1.82× a 3090** on this card at 15.9 GB. This is the strongest thing the farm does. |
| "GLM-5.2 … ~168 tok/s" | That is the model's speed on proper hardware. On 8× 170HX the one published figure is **30.2 tok/s single-stream decode** at 131k context. |

---

## 3 · The 8-card configuration — what is actually known

There is exactly **one** published 8-card GLM-5.2 run. The community wiki's own verdict: *"one report, not two — nobody has reproduced it."* No full launch command was ever published.

| | |
|---|---|
| Quant | `lowbitcoffee/GLM-5.2-W4A16` — **symmetric**, g128, **388 GB** |
| Layout | `--pipeline-parallel-size 8`, TP1 |
| vLLM | `0.20.2` + PR #38476 python files |
| Env | `VLLM_ATTENTION_BACKEND=TRITON_MLA_SPARSE`, `VLLM_MEMORY_PROFILER_ESTIMATE_CUDAGRAPHS=0` |
| `--gpu-memory-utilization` | **0.90** (0.95 crashes vLLM) |
| `--block-size` | 64 |
| KV dtype | BF16 |
| **Prefill** | 665 / 1,497 / 2,342 / **2,675 tok/s** at 4k / 32k / 65k / 131k |
| **Decode** | **30.2 tok/s single stream.** Concurrent not published. |
| Context reached | **131k**, not 1M |
| PCIe | **Gen1 ×4 — stock, no mod** |

**Memory budget:** 388 GB of weights into 512 GB leaves ~80–110 GB for KV. The wiki quotes 438,107 tokens of KV at 0.92 utilisation; that arithmetic doesn't reconcile against its own ~88–100 KB/token MLA figure (which would imply ~830k). Take 438k as the conservative number. **131k context is comfortable. 1M is untested by anyone.**

**Quant repos:**

| Repo | Verdict |
|---|---|
| `lowbitcoffee/GLM-5.2-W4A16` | ✅ symmetric g128, 388 GB — the one that works |
| `QuantTrio/GLM-5.2-Int4-Int8Mix` | ✅ works |
| `cyankiwi/GLM-5.2-AWQ-INT4` | ❌ **fails** — asymmetric g32; vLLM's MoE kernels reject asymmetric quantisation |
| `unsloth/GLM-5.2-UD-IQ2_M` | 239 GB, llama.cpp — but llama.cpp gets **141 tok/s prefill vs vLLM's 2,675**. Not a real option. |

⚠️ **The symmetric-quant requirement is a Marlin MoE kernel constraint, not a 170HX one** — it would bite identically on a real A100. Most published guides get this wrong.

### Does the solder mod change anything? Measured before/after, same rig, same workload:

| Config | Result |
|---|---|
| 1 card, ×4 → ×16 | prefill 439→448, decode 81.9→85.8 — **~+2%** |
| 3 cards, ×4 → ×16 | prefill 441→461, decode 86→89 — **~+2–4%** |
| 3 cards **with CPU offload**, Gen1 ×4 → Gen2 ×4 | prefill 33.4→48.2 — **+44%** |

**The link only bites when the model doesn't fit in VRAM.** At 388 GB in 512 GB under pipeline parallelism, it never bites. Same for diffusion — compute-bound and VRAM-resident.

> **Recommendation: do not solder.** Build stock, apply the free Gen2 software unlock, measure. You would be buying ~2% for ~$400 of shop labour and eight irreversible rework operations on cards you cannot replace.

---

## 4 · The FP8 problem, and why it is smaller than it looks

GA100 has no FP8/FP4 tensor hardware. But:

- **vLLM PR #5975 added FP8 Marlin for sm_80.** FP8 checkpoints load on Ampere as **W8A16 weight-only** — a fused kernel converts 4×FP8 → 4×FP16 with bit arithmetic and runs the MACs on FP16 tensor cores.
- **Marlin MXFP4 MoE likewise works on Ampere** (vLLM's GPT-OSS recipe confirms it).
- **You get the full memory saving and up to ~2× on memory-bound decode — which is exactly where this card is strong at 1.4 TB/s. You get zero compute speedup.** Accuracy is marginally *better* than true W8A8 because activations stay 16-bit.

**For LTX-2.5 specifically: run BF16, ignore the FP8 checkpoints.** LTX-2.5's documented baseline is 32 GB BF16 — half a card. The FP8 builds require Ada or newer for hardware scaling; on sm_80 they emulate and run slower. You have the VRAM, so BF16 is strictly better.

⚠️ No published LTX-2.5-on-170HX result exists. The 1.82× figure is LTX-*Video*, the older model. Treat LTX-2.5 performance as expected-good but unverified.

**TTS:** no benchmarks exist on this card. Open-weights TTS models are tiny and BF16 — low risk. One thing to check: **FlashAttention 3 is Hopper-only**; pin FA2 (which fully supports sm_80) and avoid any repo hard-requiring FA3.

---

## 5 · The build

### Software — the exact sequence

```bash
git clone https://github.com/amoghmunikote/cmpunlocker
cd cmpunlocker
sudo ./install.sh --profile=8gb     # ALWAYS explicit; never rely on detection
sudo shutdown -h now                 # COLD boot. A warm reboot does not work.
```

Then verify **per card**:

```bash
nvidia-smi                                    # expect 8 × 65536 MiB
sudo dmesg | grep SEC2_DEBUG                  # "saved stock signature (4096 bytes)"
sudo dmesg | grep -c POST-WRITE               # MUST equal 8 — one line per GPU
nvidia-smi -q | grep "HW Power Brake Slowdown"   # must be Not Active on all 8
```

**Hard requirements:** `nvidia-open` **610.43.02 or .03** — exact string match, the build hard-fails on anything else. Linux x86-64, root, **Secure Boot off** (unsigned modules), matching kernel headers.

⚠️ **Ignore the `abobasixseven` fork's advice to use 580.173.02.** 610.43.03 is the only combination with broad first-hand confirmation.

⚠️ **`master`'s installer is single-card** — it uses `head -1` on `lspci`. The wiki contradicts itself on whether the geometry write is nonetheless per-device. On a homogeneous 8-card rig it reportedly works, but the failure mode is silent (all cards stay stock, or worse, *some* stay stock). **Count the `POST-WRITE` lines.** Also watch for `depmod` picking stock `nvidia.ko` over the patched one, and stale initramfs.

### Hardware — what is actually validated

| Item | Status |
|---|---|
| Bare-metal PCIe slots | ✅ reference config |
| **Oculink risers** | ✅ works reliably. At Gen1/Gen2 signal integrity is a non-issue — enormous margin. |
| PLX/PEX switches | ⚠️ Fine for slot count; **no P2P benefit whatsoever**. 8 cards × 1.7 GB/s ≈ 13.6 GB/s aggregate, absorbed easily by one Gen4 ×16 uplink. Only buy one if you're short of slots. |
| Thunderbolt eGPU | ❌ total failure |
| VM passthrough | ⚠️ works on Proxmox with **SeaBIOS, not UEFI/OVMF** — but **Gen2 never trains in a guest** (the retrain must be driven from the upstream bridge). Run bare metal. |
| **Motherboard / bifurcation / IOMMU / above-4G / BAR sizing** | ⚠️ **Explicitly unexplored by the community.** This is your integration risk. |

**Cooling — validated parts:**

| Part | Result |
|---|---|
| **Bykski N-TESLA-A100-X-V2** | ✅ **Only confirmed water block.** 45°C after 30 min @180W. **Must be the V2 all-metal revision.** |
| **2× 120mm Arctic P12 Pro feeding 4 cards** | ✅ **under 65°C at `-pl 160`** ← closest analogue to an 8-card air build |
| San Ace B97 (BFB1012VH) blower per card | ✅ below 65°C @250W |
| Level1Techs A-series blower adapter (screw-mounted STL) | ✅ |
| Friction-fit shrouds, single 40mm fans, 3.24W "snail" adapters | ❌ fall off / 90°C hotspots / actually only deliver 150–180W |
| Gigabyte G292-Z20 8-card chassis, stock passive | ✅ 60°C @254W but *"louder than a jet engine"* |

⚠️ **You cannot validate cooling with a stress test.** Because FP32 is throttled, standard burn-in draws only ~60–75W. You will pass `gpu-burn` and then cook under a real diffusion load pulling 250–260W. GA100 has leakage-driven thermal positive feedback. Targets: **≤70°C core, ≤75°C memory.** Throttle at 95°C, shutdown at 98°C. Brief overheating permanently degrades HBM.

⚠️ **Waterblock install:** pad every unpopulated IC footprint before mounting — the block's metal pillars short across exposed copper pads and permanently kill the card. Pad the DrMOS and PMICs.

### Australian power and heat — the constraint nobody mentions

| | Stock (`-pl 250`) | Recommended (`-pl 160`) |
|---|---|---|
| GPUs | 2,000 W | **1,280 W** |
| + host, switches, pumps | ~2,400 W | ~1,700 W |
| **A single 10A/240V GPO delivers 2,400 W** | ⚠️ **at the limit** | ✅ comfortable |
| Electricity @ $0.35/kWh, 24/7 | ~$600/mo | **~$430/mo** |
| Heat to dump into the room | 2.4 kW | 1.7 kW — needs a 3.5 kW split minimum |

`-pl 160` costs almost nothing in throughput (250→300W buys +2.8%). **Run at 160–200W.** Also budget ~30W/card idle — ~240W just sitting there, ~$60/month to do nothing.

⚠️ **Never exceed +300 clock offset @1400 MHz or +350 @1650 MHz — memory corruption is documented.** Clock offset, not power limit, is the stability constraint.

### Estimated build cost, excluding cards *(my estimates — the community sources carry almost no pricing)*

| Item | AUD est. |
|---|---|
| EPYC Rome/Milan board + CPU + 256 GB DDR4, used | $1,800–3,000 |
| Open frame or 4U chassis | $250–600 |
| 2× 1,300–1,600 W PSU (240 V) + **EPS adapters** | $600–1,100 |
| Oculink risers/cables ×8 | $300–750 |
| **Air path** — 8× San Ace B97 + printed shrouds | $400–700 |
| *or* **Water** — 8× Bykski V2 + 2× 360 rad + pump/res | $2,500–4,000 |
| **Total, air** | **~$3,400–6,200** |
| **Total, water** | **~$5,500–9,500** |

Cards are $1,100–2,000 USD each now, up ~10× from $100–200 pre-unlock. If you already hold 8, that's ~$14–24k USD of sunk value that has appreciated. **Worth knowing: these rent on Vast.ai at $0.16–0.21/GPU-hr** — break-even against buying is ~5,500–7,000 GPU-hours per card.

---

## 6 · The risks that should actually drive decisions

**1 · No ECC, no error telemetry, no error-rate data — on factory-disabled memory.** Register `0x00823814` is fuse-latched at power-on and overrides don't survive FLR. There is no before/after error-rate study on an unlocked card, anywhere. Silent bit flips produce *wrong answers*, not crashes.

> This is the one that collides with the business. `AGENT_CHARTERS` Layer 4 sells calibration — *"an agent that's 70% sure should be right 70% of the time."* Calibration data is the asset the brief says cannot be regenerated retrospectively. Generating it on memory with no error visibility is a defensible risk for internal use as tenant zero; it is a harder story the day a client asks what the hardware is. **Mitigation: days of `gpu-burn` plus your own checksum validation per card before trusting any of them, and a periodic re-validation in the runbook.**

**2 · Permanent version pinning to `nvidia-open` 610.43.0x.** The Falcon BootROM bug is in mask ROM — NVIDIA cannot patch it on shipped silicon. But the six patch files are anchored to specific line numbers and struct layouts in `open-gpu-kernel-modules` and break on every upstream release. **The risk isn't a kill switch; it's that you are frozen.** No CUDA upgrades beyond what 610.43 supports, no security patches, and every future vLLM/PyTorch must stay compatible. On a three-year horizon this is what ends the build, not NVIDIA.

**3 · The performance figure most likely to disappoint is decode.** 30.2 tok/s on a 40B-active reasoning model means a multi-thousand-token thinking trace takes minutes. Design the UX around that — batch and async, not interactive chat. Prefill at 2,675 tok/s is fine; the weekly DEEP scan in `CURRENT_AWARENESS_PIPELINE` is a *good* fit. Live conversational agents are not.

**4 · Operational landmines.** `kill -9` on a live CUDA job → Xid 45, wedged host CUDA runtime (`cuInit` returns 999) — Ctrl-C between launches instead. vLLM crashes at `--gpu-memory-utilization 0.95`; stay ≤0.90. **Never `--enforce-eager`** — throughput collapses to 8–10 tok/s. Recovery ladder: FLR → SBR → cold boot.

**5 · PWRBRK# (edge pin B30).** Some boards assert it, forcing a permanent low-power state. It doesn't error — it's just 4× slow. Check every card before benchmarking anything. Fix: Kapton tape over B30.

**6 · Ex-mining failure modes.** Known LDO failures (GS7155NVTD 3.3V, MP1475DJ) cause `PS_5V_PGOOD` shorts and permanent PCIe drop-off. These cards are years into duty cycle, with no warranty and no support. **Assume 1–2 of 8 need repair or replacement over three years and price that in.**

---

## 7 · Recommended path — in order

| # | Step | Why |
|---|---|---|
| **1** | **Confirm which SKU you hold** — `lspci -nn \| grep 20c2` (8GB, Hynix, → 64GB) vs `2082` (10GB, Samsung, → 40GB only) | Determines whether the farm is 512 GB or 320 GB. Everything downstream depends on this. |
| **2** | Unlock **one** card on a scratch host. Verify 65536 MiB, count `POST-WRITE`, check PWRBRK#, run `gpu-burn` + checksum validation for 48h | Establishes the procedure and gives you an error-rate baseline before you commit |
| **3** | Sort cooling **before** first multi-card power-on. Air at `-pl 160` on a dedicated 15A circuit | Brief overheating permanently degrades HBM. Air is $400–700 and gets you under 65°C. |
| **4** | Build 8 cards bare-metal, stock PCIe, Gen2 software unlock. **Skip the solder.** | ~2% for eight irreversible rework operations you cannot undo |
| **5** | Reproduce the GLM-5.2 W4A16 run — `lowbitcoffee/GLM-5.2-W4A16`, PP8, TP1, vLLM 0.20.2 + PR #38476, `TRITON_MLA_SPARSE`, util 0.90, block 64 | Nobody has reproduced this. You'd be the second data point. **Measure decode before designing anything around it.** |
| **6** | **In parallel, benchmark LTX-2.5 in BF16.** This is the layer most likely to exceed expectations | The one workload where this hardware is genuinely strong and the PCIe link is irrelevant |
| **7** | Only then decide the routing/model architecture (D-17, D-18) | The brief's model choices were made against 640 GB and hoped-for Gen3/4. Re-decide against 512 GB, PP-only, 30 tok/s decode, and 1.8×-a-3090 video. |

---

## 8 · The strategic read

The Consolidation Brief treats **self-hosted GLM-5.2 reasoning as the win** and **video as the cost problem that got solved**. The hardware says the opposite.

- **Video is where this farm is excellent** — 1.82× an RTX 3090 on LTX-Video, 64 GB per card against a 32 GB requirement, compute-bound and entirely VRAM-resident so the crippled PCIe link never touches it. The avatar pipeline isn't merely affordable now; it's the thing the machine is *good at*. That is the billable product hiding in plain sight.
- **Large-MoE reasoning decode is where it's mediocre** — 30 tok/s, PP-only forever, no P2P, frozen drivers, no ECC. It works, it's sovereign, and it is genuinely a $14–24k asset doing $200k+ of work. But it is a batch machine, not an interactive one.

The pricing gap flagged as **D-11** — still the most consequential missing artifact — should now be built on: video render at electricity cost, reasoning as batched overnight/weekly work, and interactive latency as the thing you either don't sell or serve from a small fast model on one card.

---

## Sources

- [Consensus-Protocol/cmp170hx wiki](https://github.com/Consensus-Protocol/cmp170hx) — 55 pages, the only source that labels confirmed vs experimental
- [niconiconi — CMP 170HX review and teardown](https://niconiconi.neocities.org/tech-notes/nvidia-cmp-170hx-review/)
- [arXiv 2505.03782 — A Case Study of CMP 170HX](https://arxiv.org/pdf/2505.03782)
- [amoghmunikote/cmpunlocker](https://github.com/amoghmunikote/cmpunlocker) · [d3dx9/cmpunlocker](https://github.com/d3dx9/cmpunlocker) · [170th Street wiki](https://170th-street.gitbook.io/hx/unlock/current-unlock)
- [allover326/deepseek-v4-cmp170hx](https://github.com/allover326/deepseek-v4-cmp170hx) — 4-card DeepSeek-V4-Flash, 98 tok/s decode *with* speculative decoding (50.8 without)
- [vLLM PR #5975 — FP8 Marlin for sm_80](https://github.com/vllm-project/vllm/pull/5975) · [vLLM FP8 docs](https://docs.vllm.ai/en/v0.6.0/quantization/fp8.html) · [vLLM GPT-OSS recipe](https://docs.vllm.ai/projects/recipes/en/stable/OpenAI/GPT-OSS.html)
- [wccftech — prices explode after unlock](https://wccftech.com/nvidia-cmp-170hx-8-10-gb-prices-explode-over-1000-usd-as-tool-unlocks-hidden-64-80gb-vram/) · [kad8](https://www.kad8.com/hardware/nvidia-cmp-170hx-prices-surge-after-80gb-vram-unlock/) · [knightli — buying risk checklist](https://knightli.com/en/2026/07/22/cmp-170hx-80gb-memory-unlock-ai-gpu-buying-risk/) · [gpus.io — rental pricing](https://gpus.io/en/gpus/cmp170hx)
- Videos: [PCIe 4x→16x mod](https://www.youtube.com/watch?v=JWH3Sh4mHug) · [DIY supercomputer / vLLM](https://www.youtube.com/watch?v=KnJMLw7AL38) · [2.36TB VRAM build](https://www.youtube.com/watch?v=guIMH9qFYL8) — all [Digital Universe](https://www.youtube.com/@RH-3D-EN)
