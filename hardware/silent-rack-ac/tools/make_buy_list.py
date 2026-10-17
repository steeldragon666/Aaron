#!/usr/bin/env python3
"""
make_buy_list.py - the shopping list for every electronic part of the SRA-16: screens, boards, modules,
sensors, cables, power, the office air kit, the PoE switch's power and the AVAS bench kit.

  bom/electronics_buy_list.csv      one row per thing to buy (opens in Excel / Sheets)
  bom/ELECTRONICS_BUY_LIST.md       the same, grouped, with what to check on each listing

Temu wherever it is a sensible source.  Not from Temu:
  - anything that plugs into mains (plug packs, the 48 V supply): it must carry the RCM mark, so it comes
    from an Australian electronics retailer or a distributor;
  - parts that are widely counterfeited and matter (Noctua fans, the Waveshare touchscreen): from the maker's
    store or an authorised reseller, unless the exact listing checks out.
Prices are indicative AUD, October 2026, for the pack size a store sells (often more than you need):
check them at checkout.  Every row maps to a ref in drawings/CP-SRA16-ELC-001.pdf or docs/PRINTED_PARTS.md.

Usage: python3 tools/make_buy_list.py
"""
import csv
import os
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

TEMU, LOCAL, MAKER, OWNED = "Temu", "Jaycar / Altronics", "maker / authorised reseller", "owned"
DIST = "Element14 / RS / Core Electronics"
# section, refs, item, spec to match on the listing, qty, source, Temu search, AUD (total for the line), note
ROWS = [
    # ---------------------------------------------------------------- boards and screens
    ("Boards and screens", "HMI", "Touchscreen Waveshare ESP32-S3-Touch-LCD-4.3B", "the **4.3B** version: 800 x 480, "
     "RS485 + isolated DI/DO terminals, 7-36 V in. Not the 4.3 (no RS485)", 1, MAKER,
     "Waveshare ESP32-S3 Touch LCD 4.3B", 85.0, "Temu only if the listing names the 4.3B and shows the terminal "
     "block; otherwise Waveshare's store or Amazon AU"),
    ("Boards and screens", "U1", "ESP32-S3-DevKitC-1 (rack node)", "ESP32-S3-DevKitC-1 layout: 2 x 22 pins, two USB-C ports. "
     "N8R8 or N16R8 both fine. Not the 'mini' / 'zero' / 'super mini' S3 boards (different pinout)", 2, TEMU,
     "ESP32-S3-DevKitC-1 N16R8", 24.0, "buy 2: one spare; clones are fine"),
    ("Boards and screens", "U2", "RS485 module, automatic direction, 3.3 V", "TTL to RS485, **auto direction** "
     "(no DE/RE pin), works at 3.3 V (MAX3485 / SP3485)", 2, TEMU, "TTL to RS485 module automatic flow control 3.3V",
     6.0, ""),
    ("Boards and screens", "U3", "5 V step-down module", "mini MP1584 buck (about 22 x 17 mm; an LM2596 board is too big for the "
     "carrier), input to 24 V, "
     "**set it to 5.0-5.1 V with a meter before fitting**", 2, TEMU, "MP1584 mini buck converter adjustable", 4.0,
     "pack of several"),
    ("Boards and screens", "PCB", "Prototype board 7 x 9 cm, double sided, plated through", "70 x 90 mm, 2.54 mm grid",
     1, TEMU, "PCB prototype board 7x9 double sided", 5.0, "pack"),
    ("Boards and screens", "spare", "ESP32-DevKitC (WROOM-32) on 24 V terminal breakout", "the board in hand: bench "
     "spare, AVAS experiments (docs/AVAS.md)", 1, OWNED, "", 0.0, "not used in the rack node"),
    # ---------------------------------------------------------------- node components
    ("Node components", "U4", "IR receiver 38 kHz", "TSOP38238 or VS1838B (same OUT-GND-VCC pin order)", 1, TEMU,
     "VS1838B IR receiver 38kHz", 3.0, "pack"),
    ("Node components", "K1", "Relay 12 V SPDT, small", "Omron G5V-1-DC12 or HK19F-DC12V (same 7.5 x 12.5 footprint); "
     "not the big blue SRD relays", 1, TEMU, "HK19F DC12V relay", 4.0, "pack"),
    ("Node components", "U5, Q1-Q3, D1-D3", "Semiconductors: PC817, PN2222A x 3, 1N4148 x 2, 1N5819",
     "TO-92 transistors with E-B-C pin order (PN2222A); PC817 DIP-4", 1, TEMU,
     "PC817 2N2222 1N4148 1N5819 assortment", 8.0, "assortment kits"),
    ("Node components", "F1, F2", "Resettable fuses (PTC) 0.5 A hold", "radial PPTC, 16 V or more", 2, TEMU,
     "PPTC resettable fuse kit", 5.0, "kit"),
    ("Node components", "R, C", "Resistor kit 1/4 W + capacitor kit", "1/4 W metal film E12 kit; ceramic 100 nF, "
     "1 nF, 4.7 uF; electrolytic 100 uF 25 V", 1, TEMU, "metal film resistor kit 1/4W + capacitor kit", 16.0,
     "covers sheet 2's list with spares"),
    ("Node components", "J1-J10", "PCB screw terminals 3.5 mm pitch", "7 x 2-way, 3 x 3-way, 1 x 4-way (or a mixed "
     "kit); **3.5 mm**, not 5.0 / 5.08", 1, TEMU, "3.5mm pitch PCB screw terminal block", 7.0, ""),
    ("Node components", "J4, J11", "JST-XH 2.54 kit + 2.54 mm headers", "JST-XH 4-pin socket + plug; 2 x 22-way female "
     "headers for U1; a 4-pin 2.54 fan header", 1, TEMU, "JST XH 2.54 connector kit", 9.0, ""),
    # ---------------------------------------------------------------- sensors
    ("Sensors", "T1-T3", "DS18B20 waterproof probe, 1 m", "6 x 50 mm stainless, 3 wires (red, black, yellow), "
     "not the 2-wire kind", 3, TEMU, "DS18B20 waterproof probe 1m", 9.0, "often a 5-pack: then buy one pack"),
    ("Sensors", "T4-T7", "DS18B20 waterproof probe, 3 m", "as above, 3 m lead (hot side x 3 + office T7)", 4, TEMU,
     "DS18B20 waterproof probe 3m", 18.0, ""),
    ("Sensors", "RH, pod", "SHT40 / SHT41 humidity breakout", "Sensirion SHT40 or SHT41 (or SHT45) on an I2C "
     "breakout, 3.3 V; one cold side, one in the pod", 2, TEMU, "SHT40 temperature humidity sensor module I2C",
     10.0, ""),
    ("Sensors", "LEAK", "Mini float switch, vertical, normally open", "M8 or M10 stem, about 50 mm; closes as it rises "
     "(or flip the float)", 1, TEMU, "mini vertical float switch water level M8", 5.0, ""),
    ("Sensors", "DOOR x 2", "Door reed contacts, surface", "MC-38 type, normally closed when the magnet is near "
     "(lower door + upper door)", 2, TEMU, "MC-38 door magnetic reed switch", 5.0, "pack"),
    ("Sensors", "pod", "Active buzzer 12 V", "12 mm, about 85 dB, 12 V", 1, TEMU, "active buzzer 12V 12mm", 3.0,
     "pack"),
    # ---------------------------------------------------------------- AC control
    ("AC control", "IR", "IR emitter, stick-on, 3.5 mm mono plug", "IR repeater / blaster emitter, single or dual "
     "head, mono 3.5 mm", 1, TEMU, "IR extender emitter 3.5mm", 5.0, ""),
    ("AC control", "W4", "3.5 mm mono socket on a lead", "panel or inline 3.5 mm mono socket, 1-2 m lead to bare ends",
     1, TEMU, "3.5mm mono female jack cable pigtail", 4.0, ""),
    # ---------------------------------------------------------------- cables and wiring
    ("Cables and wiring", "W1", "4-core shielded alarm cable", "4 x 0.22 mm2 + foil shield", "5 m", TEMU,
     "4 core shielded cable 0.22mm 5m", 10.0, "or Jaycar by the metre"),
    ("Cables and wiring", "W2", "8-core shielded alarm cable", "8 x 0.22 mm2 + foil shield", "5 m", TEMU,
     "8 core shielded cable 0.2mm 5m", 15.0, "or Jaycar by the metre"),
    ("Cables and wiring", "W5-W7", "2-core and 4-core hook-up cable", "0.2-0.5 mm2, 5 m each", 1, TEMU,
     "2 core 4 core electrical wire 22AWG", 8.0, ""),
    ("Cables and wiring", "W1", "GX16-4 aviation connector pair", "4-pin, male + female, cable mount", 1, TEMU,
     "GX16 4 pin aviation connector", 4.0, "pack"),
    ("Cables and wiring", "W9", "4-pin PWM fan extension, 1 m", "PC fan 4-pin, male to female", 1, TEMU,
     "4 pin PWM fan extension cable", 4.0, ""),
    ("Cables and wiring", "ports", "Rubber grommets 20 + 25 mm", "membrane / blind grommets (hood port, pod)", 1,
     TEMU, "rubber membrane grommet kit", 6.0, "kit"),
    ("Cables and wiring", "loop", "Spiral wrap 10 mm, adhesive tie mounts, cable ties", "", 1, TEMU,
     "spiral wrap 10mm + adhesive cable tie mounts", 10.0, ""),
    ("Cables and wiring", "", "Heat-shrink kit + bootlace ferrules with crimper", "ferrules 0.25-1.5 mm2", 1, TEMU,
     "ferrule crimper kit + heat shrink tube kit", 28.0, "tool you keep"),
    # ---------------------------------------------------------------- power
    ("Power", "W8", "12 V 2 A plug pack, regulated, 5.5 x 2.1", "**RCM-marked**, regulated 12 V DC", 1, LOCAL, "",
     28.0, "mains-connected: not from Temu"),
    ("Power", "W8", "DC 5.5 x 2.1 extension 2 m + socket-to-terminal pigtail", "", 1, TEMU,
     "DC 5.5x2.1 extension cable 2m + female terminal adapter", 6.0, ""),
    # ---------------------------------------------------------------- office air
    ("Office air", "FAN", "Noctua NF-A8 PWM (80 mm, stops at 0 %)", "the genuine NF-A8 **PWM** (4 wire)", 1, MAKER,
     "", 32.0, "Temu Noctua listings are often fakes"),
    ("Office air", "inserts", "M3 heat-set inserts, M3 x 5.7", "brass, for 4.0 mm holes", 1, TEMU,
     "M3 heat set inserts brass", 8.0, "16 needed: P9 adaptors"),
    ("Office air", "screws", "M3 stainless screw kit", "button head + socket head, lengths 8-35 mm, washers "
     "(8 x M3x10, 4 x M3x35, 4 x M3x8)", 1, TEMU, "M3 stainless screw assortment button head socket head", 12.0,
     "kit"),
    ("Office air", "gasket", "Closed-cell foam tape 2 mm", "", 1, TEMU, "closed cell foam tape 2mm", 5.0, ""),
    ("Office air", "ducts", "60 mm flex duct + 2 hose clamps", "", 2, OWNED, "", 0.0, "in hand"),
    # ---------------------------------------------------------------- mounts (printed parts)
    ("Mounts", "P7", "Neodymium disc magnets 20 x 5 mm", "N35 or better", 2, TEMU, "neodymium magnet 20x5mm", 6.0,
     "pack"),
    ("Mounts", "P8", "Neodymium disc magnets 10 x 3 mm", "N35 or better", 6, TEMU, "neodymium magnet 10x3mm", 5.0,
     "pack"),
    ("Mounts", "P6, P7", "Self-tapping screws M2.5 x 6 and M3 x 8/12, M4 x 8 button heads", "", 1, TEMU,
     "self tapping screw assortment M2 M2.5 M3", 8.0, "kit"),
    ("Mounts", "P6", "Foam pads 10 x 10 x 2 mm", "", 1, TEMU, "foam tape pads", 3.0, ""),
    # ---------------------------------------------------------------- network (the PoE switch)
    ("Network", "SW1", "Industrial PoE switch 16 PoE + 8 GE, L2+ managed", "the switch in hand", 1, OWNED, "", 0.0,
     "check its label: DC input range and PoE budget"),
    ("Network", "PS1", "48-55 V DIN-rail supply for the switch", "Mean Well SDR-240-48 class (240 W, adjustable "
     "to about 53 V for PoE+); size it to the cameras: 16 x 6 W cameras + the switch = about 130 W", 1, DIST, "",
     125.0, "mains-connected: not from Temu"),
    ("Network", "DIN", "DIN rail 35 mm, 300 mm", "steel top-hat rail", 1, TEMU, "DIN rail 35mm 300mm", 5.0, ""),
    ("Network", "leads", "Cat6 patch leads 0.5 m", "**pure copper**, not CCA", 4, TEMU, "cat6 patch cable 0.5m pure "
     "copper", 12.0, "uplink + servers"),
    # ---------------------------------------------------------------- AVAS bench kit
    ("AVAS (bench)", "AVAS", "Arrival AVAS unit, pre-production, unflashed", "the unit in hand", 1, OWNED, "", 0.0,
     "see docs/AVAS.md before powering it"),
    ("AVAS (bench)", "X1", "Deutsch DT 12-way plug kit (mates the unit)", "DT06-12SA plug + W12S wedge + size 16 "
     "sockets (the unit has the DT04-12P receptacle)", 1, TEMU, "Deutsch DT 12 pin connector kit DT06-12S", 10.0,
     "check the key letter (A) matches"),
    # ---------------------------------------------------------------- options
    ("Options", "J10", "Mains detect: 5 V USB charger + USB-A lead", "**RCM-marked** charger", 1, LOCAL, "", 15.0,
     "optional"),
    ("Options", "FAN2", "Second fan (push-pull) + 4-pin Y splitter", "genuine Noctua NF-A8 PWM or Arctic P8 Max", 1,
     MAKER, "", 38.0, "optional"),
    ("Options", "DO1", "12 V LED beacon", "12 V DC, small strobe or steady", 1, TEMU, "12V LED warning beacon", 10.0,
     "optional"),
]


def main():
    out = os.path.join(ROOT, "bom")
    with open(os.path.join(out, "electronics_buy_list.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["section", "refs", "item", "check on the listing", "qty", "where", "Temu search", "AUD (est.)",
                    "note"])
        for r in ROWS:
            w.writerow([x.replace("**", "") if isinstance(x, str) else x for x in r])
    tot = OrderedDict()
    for sec, refs, item, spec, q, src, srch, aud, note in ROWS:
        key = "Options" if sec == "Options" else src
        tot[key] = tot.get(key, 0.0) + aud
    core = sum(v for k, v in tot.items() if k != "Options")
    L = ["# Electronics buy list - SRA-16", "",
         "Everything electronic for the rack: the touchscreen, the rack node, sensors, cables, power, the office "
         "air kit, the PoE switch's power and a bench kit for the AVAS. Generated by `tools/make_buy_list.py` "
         "(CSV: `bom/electronics_buy_list.csv`); the refs match `drawings/CP-SRA16-ELC-001.pdf` and "
         "`docs/PRINTED_PARTS.md`.", "",
         "**Rules used:** Temu wherever it is a sensible source. Anything that plugs into mains (the 12 V plug "
         "pack, the 48 V supply, the USB charger) must carry the **RCM** mark, so it comes from an Australian "
         "retailer or distributor. Parts that are widely faked and matter (Noctua fans, the Waveshare 4.3B screen) "
         "come from the maker or an authorised reseller unless the Temu listing clearly checks out. Prices are "
         "indicative AUD for the pack size usually sold; I could not check live listings, so confirm at checkout.",
         "",
         "| Source | AUD (est.) |", "|---|---:|"]
    for k, v in tot.items():
        if k not in ("Options", OWNED):
            L.append("| %s | %.0f |" % (k, v))
    L += ["| **Total (not counting options)** | **%.0f** |" % core, "| Options | %.0f |" % tot.get("Options", 0), ""]
    secs = OrderedDict()
    for r in ROWS:
        secs.setdefault(r[0], []).append(r)
    for sec, rows in secs.items():
        L += ["## %s" % sec, "", "| Ref | Item | Check on the listing | Qty | Where | Temu search | AUD | Note |",
              "|---|---|---|---:|---|---|---:|---|"]
        for _s, refs, item, spec, q, src, srch, aud, note in rows:
            L.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
                refs, item, spec, q, src, "`%s`" % srch if srch else "", "%.0f" % aud if aud else "-", note))
        L.append("")
    L += ["## Before you order", "",
          "- **Touchscreen:** it must be the **4.3B**: the node talks to it over RS485 and the alarm buzzer hangs "
          "on its isolated output. The plain 4.3 has neither.",
          "- **ESP32-S3-DevKitC-1:** the firmware and the carrier are drawn for this board (2 x 22 pins). The "
          "WROOM-32 breakout you have is a different chip and pinout; keep it as a bench spare.",
          "- **DS18B20 probes:** cheap probes are sometimes clones. They work in this design (3-wire, powered), but "
          "buy a spare and check each one reads within 0.5 degC of the others in a glass of water.",
          "- **Buck module:** the adjustable ones ship at a random voltage. Set 5.0-5.1 V with a meter before you "
          "connect the DevKit.",
          "- **48 V supply:** read the switch's label first (DC input range, PoE budget). Most 16-port industrial "
          "PoE switches want 48-57 V; PoE+ cameras need about 52-54 V at the switch.",
          "- **Mains items:** only RCM-marked plug packs and supplies inside a sealed rack.", ""]
    with open(os.path.join(out, "ELECTRONICS_BUY_LIST.md"), "w") as fh:
        fh.write("\n".join(L))
    print("buy list: %d lines, about AUD %.0f (+ %.0f options): %s" % (
        len(ROWS), core, tot.get("Options", 0), ", ".join("%s %.0f" % kv for kv in tot.items())))


if __name__ == "__main__":
    main()
