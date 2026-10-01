#!/usr/bin/env python3
"""
Electronics pack CP-SRA16-ELC-001 for the SRA-16 - the control kit: an ESP32-S3 rack node that reads
temperature probes on the cold and hot sides and runs the AC by IR, and a 4.3 inch touchscreen on the
upper door, joined by an RS485 bus.

Outputs (relative to hardware/silent-rack-ac/):
  drawings/CP-SRA16-ELC-001_s1..s5.svg + CP-SRA16-ELC-001.pdf
      1 system, 2 node carrier (schematic, board, parts), 3 touchscreen pod, harness, Modbus map,
      4 placement in the rack and cable routes, 5 control logic, alarms, commissioning
  bom/electronics.csv          kit parts with indicative AUD prices (read by make_bom.py)
  bom/electronics_harness.csv  cables W1-W8
  firmware/test/elc_report.json  checks and totals
  docs/ELECTRONICS.md
  renders/hmi_*.png            with --shots: builds the SDL preview of the touchscreen and captures it

Checks: the control core's unit tests, the thermal simulation (tools/sim_controller.py), node firmware
pins = carrier nets, Modbus map node = touchscreen = this table, power budget, carrier fits the node box.

Usage: python3 tools/make_electronics.py [--no-pdf] [--no-sim] [--shots] [--esphome PATH]
"""
import base64
import csv
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FW = os.path.join(ROOT, "firmware")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "cad", "fusion", "SilentRackAC"))
import rack_layout as RL  # noqa: E402
import sheetmetal as SMP  # noqa: E402
import make_weld_pack as WP  # noqa: E402
from make_weld_pack import Svg, INK, THIN, TODAY, table, heading, paragraph  # noqa: E402

DOC_NO, REV = "CP-SRA16-ELC-001", "A"
N_SHEETS = 5
BLUE, RED, GREEN, AMBER, GREY = "#2f6db5", "#c0392b", "#2e8b57", "#d68910", "#8a9199"
COLD_FILL, HOT_FILL, BAY_FILL = "#e3eefb", "#fbe6e0", "#f3f0e8"

# ======================================================================= the design, as data
# node carrier: GPIO -> net, where it lands, what it does, firmware id (checked against sra16-node.yaml)
GPIO = [
    (4, "IR_TX", "Q1 base (R5)", "IR emitter, 38 kHz carrier (remote_transmitter)", "ir_tx"),
    (5, "IR_RX", "U4 OUT", "IR receiver: learning, protocol check (remote_receiver)", "ir_rx"),
    (6, "OW_COLD", "J5-2", "1-Wire, cold probes T1-T3 (R1 4.7k pull-up)", "ow_cold"),
    (7, "OW_HOT", "J6-2", "1-Wire, hot probes T4-T6 (R2 2.2k pull-up)", "ow_hot"),
    (8, "SDA", "J4-3", "I2C data, SHT41 cold-side humidity", "i2c"),
    (9, "SCL", "J4-4", "I2C clock (50 kHz on the 0.5 m lead)", "i2c"),
    (10, "DOOR_LO", "J9-1 (R11)", "lower door contact, closed when shut", "door_lower"),
    (11, "LEAK", "J8-1 (R9)", "tray float switch, closes on water", "leak"),
    (12, "MAINS", "U5 collector", "AC socket live: optocoupler pulls low", "mains"),
    (13, "SD_RLY", "Q2 base (R8)", "SHUTDOWN relay K1 -> J3", "shutdown_relay"),
    (17, "TXD", "U2 DI/TXD", "RS485 transmit (UART1, 19200 8N1)", "rs485"),
    (18, "RXD", "U2 RO/RXD", "RS485 receive", "rs485"),
]

# connectors on the carrier: ref, type, pins, what plugs in
CONN = [
    ("J1", "2-way terminal 3.5 mm", ["+12V", "0V"], "12 V in: plug pack on the UPS-backed PDU (W8)"),
    ("J2", "4-way terminal 3.5 mm", ["+12V", "0V", "A", "B"], "door bus W1 to the touchscreen"),
    ("J3", "3-way terminal 3.5 mm", ["COM", "NO", "NC"], "SHUTDOWN dry contact (K1) on W2"),
    ("J4", "JST-XH 4-way", ["3V3", "0V", "SDA", "SCL"], "SHT41 cold-side humidity (W7)"),
    ("J5", "3-way terminal 3.5 mm", ["3V3", "DQ", "0V"], "cold probes T1 T2 T3 (W3)"),
    ("J6", "3-way terminal 3.5 mm", ["3V3", "DQ", "0V"], "hot probes T4 T5 T6 on harness W2"),
    ("J7", "2-way terminal 3.5 mm", ["IR+", "IR-"], "IR emitter socket lead W4"),
    ("J8", "2-way terminal 3.5 mm", ["LEAK", "0V"], "tray float switch (W5)"),
    ("J9", "2-way terminal 3.5 mm", ["DOOR", "0V"], "lower door contact (W6)"),
    ("J10", "2-way terminal 3.5 mm", ["5V+", "5V-"], "mains detect, optional (W2)"),
]

# carrier parts: ref, value / part, function
CARRIER = [
    ("U1", "ESP32-S3-DevKitC-1-N8R8", "the controller, on 2 x 22-way sockets"),
    ("U2", "TTL-RS485 module, auto direction, 3.3 V", "SP3485/MAX3485 class, A/B to J2"),
    ("U3", "5 V 1 A step-down, 7-36 V in", "Pololu D24V10F5 or equal"),
    ("U4", "TSOP38238", "IR receiver 38 kHz, under the lid window"),
    ("U5", "PC817", "optocoupler, mains detect"),
    ("K1", "Omron G5V-1-DC12", "SHUTDOWN relay, SPDT 1 A 30 VDC"),
    ("Q1, Q2", "PN2222A", "IR emitter and relay drivers"),
    ("D1", "1N4148", "K1 flyback"),
    ("D2", "1N4148", "U5 LED reverse guard"),
    ("D3", "1N5819", "5 V into U1: blocks back-feed from the USB port"),
    ("F1", "PTC 0.5 A hold", "door bus 12 V"),
    ("R1", "4.7k", "1-Wire cold pull-up"),
    ("R2", "2.2k", "1-Wire hot pull-up (longer bus)"),
    ("R3, R4", "4.7k", "I2C pull-ups"),
    ("R5, R8", "1k", "Q1, Q2 base"),
    ("R6", "150R 0.25 W", "IR emitter current, about 22 mA peak"),
    ("R7", "100R", "U4 supply filter"),
    ("R9, R11, R13", "1k", "input series / U5 LED"),
    ("R10, R12, R14", "10k", "input pull-ups"),
    ("C1", "100uF 25 V", "12 V bulk"),
    ("C2", "100uF 10 V", "5 V bulk"),
    ("C3", "4.7uF", "U4 supply"),
    ("C4-C7", "100nF", "input filters, U2 decoupling"),
]

# board placement, mm, board centre = origin, x along the 70 side (- = box front, towards the door),
# y along the 90 side (+ = up); pads for the terminal row on the bottom edge
BOARD = (70.0, 90.0)
PLACE = [  # ref, x0, y0, x1, y1, label, fill
    ("U1", 7.0, -32.0, 33.0, 31.0, "U1 ESP32-S3-DevKitC-1\n(USB up)", "#dbe7f5"),
    ("U2", -24.0, -26.0, -9.0, 18.0, "U2 RS485", "#e8e1f2"),
    ("U3", -24.0, 22.0, -6.0, 40.0, "U3 5 V", "#e4f2e1"),
    ("J2", -35.0, 17.0, -27.0, 33.0, "J2", "#f6e7c8"),
    ("K1", -5.0, 4.0, 5.0, 17.0, "K1", "#f3dede"),
    ("U4", -3.0, -33.0, 3.0, -27.0, "U4", "#dddddd"),
    ("U5", -7.5, -20.0, -1.0, -14.0, "U5", "#eeeeee"),
    ("J4", -34.0, -35.0, -22.0, -29.0, "J4", "#f6e7c8"),
]
TERM_ROW = ["J5", "J6", "J3", "J7", "J8", "J9", "J10", "J1"]   # bottom edge, left to right, 3.5 mm pitch

# kit parts list: group, ref/where, item, spec / example part, qty, unit AUD (indicative, Sept 2026), optional
KIT = [
    ("Touchscreen", "HMI", "Waveshare ESP32-S3-Touch-LCD-4.3B", "800x480 IPS, GT911 touch, 7-36 V in, RS485, "
     "isolated DI/DO, 16 MB flash, 8 MB PSRAM", 1, 79.0, False),
    ("Touchscreen", "pod", "SHT41 breakout (room)", "Adafruit 5776 or equal, in the pod's vented corner", 1, 12.0, False),
    ("Touchscreen", "pod", "Active buzzer 12 V, 12 mm", "85 dB, on DO0", 1, 2.5, False),
    ("Touchscreen", "pod", "Door contact, upper door", "surface reed contact (MC-38 type), closed when shut", 1, 4.0, False),
    ("Rack node", "U1", "ESP32-S3-DevKitC-1-N8R8", "Espressif, 2 x 22 pins", 1, 25.0, False),
    ("Rack node", "U2", "TTL-RS485 module, automatic direction, 3.3 V", "SP3485 / MAX3485 class", 1, 6.0, False),
    ("Rack node", "U3", "5 V 1 A step-down regulator, 7-36 V in", "Pololu D24V10F5 or equal", 1, 15.0, False),
    ("Rack node", "U4", "IR receiver TSOP38238", "38 kHz", 1, 3.0, False),
    ("Rack node", "K1", "Relay Omron G5V-1-DC12", "SPDT, 1 A 30 VDC", 1, 5.0, False),
    ("Rack node", "U5, Q1-Q2, D1-D3, F1", "PC817, 2 x PN2222A, 2 x 1N4148, 1N5819, PTC 0.5 A", "", 1, 4.0, False),
    ("Rack node", "R, C", "Resistors and capacitors (sheet 2 list)", "1/4 W metal film, ceramic + electrolytic", 1, 4.0,
     False),
    ("Rack node", "PCB", "Prototype board 70 x 90 mm, plated through", "2.54 mm grid", 1, 3.0, False),
    ("Rack node", "J", "Terminals 3.5 mm (6 x 2-way, 3 x 3-way, 1 x 4-way), JST-XH 4, 2 x 22-way sockets",
     "pluggable or fixed", 1, 9.0, False),
    ("Sensors", "T1-T3", "DS18B20 waterproof probe, 6 x 50 mm stainless, 1 m lead", "cold side", 3, 6.0, False),
    ("Sensors", "T4-T6", "DS18B20 waterproof probe, 6 x 50 mm stainless, 3 m lead", "hot side, cut to the harness", 3, 7.0,
     False),
    ("Sensors", "RH", "SHT41 breakout (cold side)", "Adafruit 5776 or equal, on a 0.5 m lead", 1, 12.0, False),
    ("Sensors", "LEAK", "Mini float switch, vertical, normally open", "M8 stem, 52 mm; set to close as it rises", 1, 6.0, False),
    ("Sensors", "DOOR", "Door contact, lower door", "surface reed contact (MC-38 type)", 1, 4.0, False),
    ("AC control", "IR", "IR emitter, stick-on, 3.5 mm mono plug", "AV 'IR blaster' emitter, no built-in resistor", 1, 6.0,
     False),
    ("AC control", "W4", "3.5 mm mono socket on a 1.5 m lead", "socket end in the bay, bare end to J7", 1, 6.0, False),
    ("Cables", "W1", "4-core 0.22 mm2 shielded alarm cable", "door bus", 2, 1.5, False),
    ("Cables", "W1", "GX16-4 aviation connector pair, cable mount", "at the hinge loop: the door lifts off", 1, 6.0, False),
    ("Cables", "W2", "8-core 0.22 mm2 shielded alarm cable", "rear harness", 4, 2.2, False),
    ("Cables", "W5-W7", "2-core and 4-core 0.22 mm2 cable", "leak, lower door, SHT41 leads", 4, 1.0, False),
    ("Cables", "port", "Membrane grommet 25 mm (hood port) + 20 mm spare", "", 1, 4.0, False),
    ("Cables", "loop", "Spiral wrap 10 mm, adhesive cable-tie mounts, ties, heat shrink, ferrules", "", 1, 14.0, False),
    ("Power", "W8", "12 V 2 A regulated plug pack, RCM, 5.5 x 2.1", "on the UPS-backed PDU", 1, 25.0, False),
    ("Power", "W8", "DC 5.5 x 2.1 extension 2 m + socket-to-terminal pigtail", "", 1, 8.0, False),
    ("Options", "J10", "Mains detect: 5 V USB charger (RCM) + USB-A lead to bare ends", "in a double adaptor on the "
     "AC's GPO", 1, 15.0, True),
    ("Options", "DO1", "12 V LED beacon", "on the alarm output", 1, 18.0, True),
]

# cables: id, from, to, cable, length m, route
HARNESS = [
    ("W1", "J2 (node)", "touchscreen terminals", "4-core 0.22 shielded, GX16-4 inline", 1.5,
     "node box front slot - front-left corner of the front plenum - hinge loop 300 mm in spiral wrap at "
     "z 1450 (GX16 on the cabinet side) - upper door grommet - pod"),
    ("W2", "J6, J3, J10 (node)", "T4, T5, T6; UPS contact; mains charger", "8-core 0.22 shielded", 3.5,
     "bottom slot - down the front-left corner - hood port - back along the bay's left wall under the shelf "
     "(T6 on a branch tied along the exhaust duct) - up through the shelf's return opening - rear-left rail "
     "spacer (T5, then T4) - cable entry"),
    ("W3", "J5 (node)", "T1, T2, T3", "probe leads, 1 m", 1.0, "front-left rail spacer face, clipped"),
    ("W4", "J7 (node)", "IR emitter (plugs in)", "3.5 mm socket lead", 1.5,
     "hood port - socket tied in the bay's top-front-left corner - emitter over the AC's IR receiver"),
    ("W5", "J8 (node)", "tray float switch", "2-core 0.22", 1.8, "hood port - down the AC's left side gap - tray, front left"),
    ("W6", "J9 (node)", "lower door contact", "2-core 0.22", 1.0, "hood port - under the hood's front edge"),
    ("W7", "J4 (node)", "SHT41 cold side", "4-core 0.22", 0.5, "up the front-left rail spacer, P8-1 clip at z 1300"),
    ("W8", "J1 (node)", "12 V plug pack", "DC lead + 2 m extension", 3.5,
     "PDU - (rear: down the return opening, bay, hood port) - bottom slot"),
]

# Modbus holding registers on the node (server 1, 19200 8N1): address, name, type, scale/unit, access
MODBUS = [
    (0x00, "Cold side (mean T1, T2)", "S16", "0.1 degC", "R"), (0x01, "Hot side (max T4, T5)", "S16", "0.1 degC", "R"),
    (0x02, "T1 cold top", "S16", "0.1 degC", "R"), (0x03, "T2 cold middle", "S16", "0.1 degC", "R"),
    (0x04, "T3 AC supply", "S16", "0.1 degC", "R"), (0x05, "T4 hot top", "S16", "0.1 degC", "R"),
    (0x06, "T5 AC return", "S16", "0.1 degC", "R"), (0x07, "T6 AC exhaust", "S16", "0.1 degC", "R"),
    (0x08, "Cold side RH", "S16", "0.1 %", "R"), (0x09, "Dew point", "S16", "0.1 degC", "R"),
    (0x0A, "Cold side average", "S16", "0.1 degC", "R"), (0x0B, "Rise across the servers", "S16", "0.1 K", "R"),
    (0x0C, "Setpoint sent", "S16", "0.1 degC", "R"), (0x0D, "State (0-8)", "U16", "enum", "R"),
    (0x0E, "Alarm bits", "U16", "bits 0-11", "R"), (0x0F, "Flags", "U16", "bits 0-8", "R"),
    (0x10, "Retries", "U16", "count", "R"), (0x11, "Uptime", "U16", "min", "R"),
    (0x12, "IR frames sent", "U16", "count", "R"), (0x13, "Firmware version", "U16", "100 = 1.0.0", "R"),
    (0x20, "Mode: 0 auto, 1 on, 2 off", "U16", "enum", "R/W"), (0x21, "Intake target", "S16", "0.1 degC, 18-27", "R/W"),
    (0x22, "Eco allowed", "U16", "0/1", "R/W"), (0x23, "AC fan: 0 auto, 1 low, 2 high", "U16", "enum", "R/W"),
    (0x24, "Intake warning", "S16", "0.1 degC, 24-35", "R/W"), (0x25, "Shutdown limit", "S16", "0.1 degC, 28-40", "R/W"),
    (0x30, "Upper door open (from the screen)", "U16", "0/1", "W"), (0x31, "Room temperature", "S16", "0.1 degC", "W"),
    (0x32, "Command: 1 send IR now, 2 reset alarms", "U16", "", "W"), (0x33, "Heartbeat", "U16", "count", "W"),
]
FLAGS = ["AC on (commanded)", "eco", "shutdown request", "lower door open", "water", "AC socket live",
         "compressor running", "compressor state known", "mains detect fitted"]

STATES = [("Starting", "just switched on, the coil is still cooling down"),
          ("Cooling", "compressor running"), ("Idle", "AC on, its thermostat satisfied"),
          ("On", "AC on, compressor state unknown (no supply / exhaust probe)"),
          ("Eco off", "switched off at low load, back on when it warms"), ("Off", "switched off by the user"),
          ("Not cooling", "should cool, does not after 3 re-sends"), ("No AC power", "mains-detect input dead"),
          ("CRITICAL", "intake above the shutdown limit")]
ALARMS = [("0", "intake warning", "cold side >= warning (27)", "screen, beep"),
          ("1", "intake critical", "cold side >= limit (32)", "beep; shutdown after 120 s"),
          ("2", "hot side warning", "hot side >= 45", "screen"),
          ("3", "AC not cooling", "3 re-sends, still not cooling", "beep"),
          ("4", "water in tray", "float switch closed 5 s", "beep"),
          ("5", "door left open", "a door open 10 min", "screen"),
          ("6", "probe missing", "no reading on the cold or the hot side", "screen; AC forced on"),
          ("7", "condensation risk", "dew point 1 K over supply air for 10 min", "screen"),
          ("8", "user OFF overridden", "off, but intake hit the warning", "screen"),
          ("9", "IT shutdown", "critical for 120 s (latched)", "K1 closes, beep"),
          ("10", "AC socket dead", "mains-detect input low", "beep"),
          ("11", "link", "no screen heartbeat 60 s / node not answering", "screen")]
SETTINGS = [("Intake target", "22.0 degC", "average of the cold side the AC is trimmed to"),
            ("Warning / shutdown limit", "27 / 32 degC", "ASHRAE A1 recommended max / hard limit"),
            ("Eco", "on", "AC off at low load: rise across the servers < 4 K"),
            ("Eco band", "target -2 / +2 K", "off when pulled down, on again when warm (or hot side 32)"),
            ("Min on / off", "15 / 5 min", "compressor-friendly cycling"),
            ("Setpoint range", "17-30 degC", "first guess target + 3, trimmed in whole degrees"),
            ("Trim", "20 min (2 min when 3 K hot)", "on the mean error over the window"),
            ("Not-cooling check", "15 min (3 min when hot)", "then re-send, 3 times, then alarm"),
            ("Shutdown delay", "120 s", "cold side above the limit before K1 closes"),
            ("IR send gap", ">= 10 s", "never floods the AC")]

# where things go in the rack (layout coordinates: x right from the left skin, y back from the front, z up)
SPOTS = [  # id, what, x, y, z, how
    ("T1", "Cold side top", 50, 148, 1790, "P8-1 clip on the front-left rail spacer; probe across the plenum"),
    ("T2", "Cold side middle", 50, 148, 1465, "P8-1 clip, same face"),
    ("T3", "AC supply", 50, 148, 1125, "P8-1 clip just above the shelf, tip over the hood outlet"),
    ("RH", "SHT41 cold side", 50, 148, 1300, "lead in a P8-1 clip, board hanging free in the air"),
    ("T4", "Hot side top", 50, 880, 1790, "P8-1 clip on the rear-left rail spacer, rear face"),
    ("T5", "AC return", 50, 880, 1130, "P8-1 clip on the rear-left rail spacer, just above the return opening"),
    ("T6", "AC exhaust", 442, 455, 700, "6.5 mm hole in the elbow's outer bend, probe 25 mm in, silicone"),
    ("LK", "Tray float switch", 52, 90, 140, "on a small alu angle bonded to the tray, front-left corner"),
    ("DL", "Lower door contact", 90, 50, 1004, "switch under the hood's front edge, magnet on the door lining"),
    ("DU", "Upper door contact", 60, 30, 1620, "switch on the door lining at the hinge side, magnet on the side lining"),
    ("IR", "IR emitter", 300, 59, 832, "stuck on the AC front over its IR receiver (by the display)"),
    ("NB", "Node box (P7)", 51, 125, 1215, "magnets on the front-left rail spacer, front face"),
    ("POD", "Touchscreen (P6)", 135, -30, 1505, "outside the upper door, 2 x M4 rivnuts"),
    ("HP", "Hood port", 54, 70, 1045, "P1-1 left end, 25 mm membrane grommet"),
    ("HL", "Hinge loop + GX16", 40, 50, 1450, "300 mm loop in spiral wrap, between the hinges"),
]

POWER = [  # load, rail, mA typical, mA peak
    ("Touchscreen panel (backlight on)", "12 V", 210, 260),
    ("ESP32-S3 node incl. Wi-Fi", "3.3 V (via 5 V)", 90, 350),
    ("Probes, SHT41, RS485, IR receiver", "3.3 V", 12, 20),
    ("IR emitter (while sending)", "5 V", 0, 22),
    ("Relay K1 (shutdown only)", "12 V", 0, 13),
    ("Buzzer / beacon (alarm only)", "12 V", 0, 30),
]


# ======================================================================= checks
def read(p):
    with open(os.path.join(ROOT, p)) as fh:
        return fh.read()


def run_unit_tests():
    src = os.path.join(FW, "test", "test_sra_control.cpp")
    with tempfile.TemporaryDirectory() as td:
        exe = os.path.join(td, "t")
        r = subprocess.run(["g++", "-std=c++17", "-O1", "-Wall", "-Wextra", "-Werror",
                            "-I" + os.path.join(FW, "components", "sra_control"), src, "-o", exe],
                           capture_output=True, text=True)
        if r.returncode:
            return False, "compile failed: " + r.stderr[-400:]
        r = subprocess.run([exe], capture_output=True, text=True)
        out = (r.stdout + r.stderr).strip().splitlines()
        return r.returncode == 0, out[-1] if out else ""


def run_sim():
    r = subprocess.run([sys.executable, os.path.join(HERE, "sim_controller.py"), "--plot",
                        os.path.join(ROOT, "renders", "controls_sim.png"), "--json",
                        os.path.join(FW, "test", "sim_report.json")], capture_output=True, text=True)
    rep = json.load(open(os.path.join(FW, "test", "sim_report.json")))
    n = len(rep["checks"])
    bad = [c for c in rep["checks"] if not c["ok"]]
    return r.returncode == 0 and not bad, "%d/%d scenario checks" % (n - len(bad), n), rep


def check_pins():
    """Every GPIO the node firmware uses is a carrier net, and the other way round."""
    y = read("firmware/sra16-node.yaml")
    used = sorted({int(g) for g in re.findall(r"GPIO(\d+)", y)})
    ours = sorted(g[0] for g in GPIO)
    return used == ours, "firmware %s, carrier %s" % (used, ours)


def check_modbus():
    """Node registers = this table = the registers the touchscreen reads or writes."""
    node = read("firmware/sra16-node.yaml")
    hmi = read("firmware/sra16-hmi.yaml")
    sec = node.split("modbus_server:", 1)[1]
    n_addr = sorted({int(a, 16) for a in re.findall(r"address: (0x[0-9A-Fa-f]+)", sec)})
    h_addr = sorted({int(a, 16) for a in re.findall(r"address: (0x[0-9A-Fa-f]+)", hmi)} |
                    {int(a, 16) for a in re.findall(r"create_write_single_command\(c, (0x[0-9A-Fa-f]+)", hmi)})
    t_addr = sorted(m[0] for m in MODBUS)
    ok = n_addr == t_addr and set(h_addr) <= set(t_addr)
    missing = sorted(set(t_addr) - set(h_addr))
    return ok, "%d registers; the screen uses %d (not: %s)" % (len(t_addr), len(h_addr),
                                                               ", ".join("0x%02X" % a for a in missing) or "none")


def check_fit():
    """The carrier and its parts sit on the board, the terminal row fits along the bottom edge, and the
    tallest stack (standoff + board + sockets + DevKit + module) clears the lid of box P7."""
    import printparts as PP
    e = PP.EL
    pw, ph = e["pcb"]
    on_board = all(-pw / 2 <= p[1] < p[3] <= pw / 2 and -ph / 2 <= p[2] < p[4] <= ph / 2 for p in PLACE)
    pins_of = dict((c[0], c[2]) for c in CONN)
    row = sum(3.5 * len(pins_of[j]) for j in TERM_ROW)
    stack = e["box_base"] + 5.0 + 1.6 + 8.5 + 1.6 + 3.2
    inside = e["box_base"] + e["box_in_h"]
    ok = on_board and row <= pw - 2.0 and stack <= inside - 3.0 and set(TERM_ROW) | {"J2", "J4"} == set(pins_of)
    return ok, "board %gx%g in P7; terminal row %.1f of %.0f mm; stack %.1f of %.1f mm" % (
        pw, ph, row, pw, stack, inside)


def check_power():
    i12 = sum(p[3] for p in POWER if p[1] == "12 V")
    i5 = sum(p[3] for p in POWER if p[1] != "12 V")        # all of it via U3 (5 V), worst case
    p_in = i12 * 12.0 / 1000 + i5 * 5.0 / 1000 / 0.85
    i_in = p_in / 12.0
    ok = i_in < 2.0 * 0.5 and i5 < 1000 * 0.6
    typ = sum(p[2] for p in POWER if p[1] == "12 V") * 12 / 1000.0 + sum(p[2] for p in POWER if p[1] != "12 V") * 5 / 1000 / 0.85
    return ok, "peak %.2f A at 12 V (plug pack 2 A), 5 V rail %d mA peak (U3 1 A); typical %.1f W" % (
        i_in, i5, typ), typ


# ======================================================================= drawing furniture
def title_block(sh, n, title, scale="NTS"):
    tb = (272, 247, 140, 42)
    sh.rect(*tb, sw=0.5, fill="#ffffff")
    rows = [("PROJECT", "SRA-16 Silent AC Rack - control electronics kit"),
            ("TITLE", title),
            ("DOC NO.", "%s   SHEET %d OF %d   REV %s" % (DOC_NO, n, N_SHEETS, REV)),
            ("SCALE", "%s @ A3   UNITS mm   LAYOUT v%s" % (scale, RL.VERSION)),
            ("DATE", "%s   DRAWN Claude (AI) for Carbon Project" % TODAY),
            ("STATUS", "PROTOTYPE - SELV only (12 V); no mains wiring in the kit")]
    for i, (k, v) in enumerate(rows):
        y = tb[1] + 6.2 + i * 6.3
        sh.text(tb[0] + 2, y, k, size=1.9, weight="bold")
        sh.text(tb[0] + 19, y, v, size=WP.fit_text(v, 118, 2.15))
        if i:
            sh.line(tb[0], y - 4.6, tb[0] + tb[2], y - 4.6, w=0.15)
    sh.line(tb[0] + 17, tb[1], tb[0] + 17, tb[1] + tb[3], w=0.15)


def new_sheet(n, title, scale="NTS"):
    sh = Svg()
    WP.border(sh)
    sh.text(14, 16, "%s  -  %s" % (DOC_NO, title), size=4.0, weight="bold")
    return sh


def mtext(sh, x, y, s, size=2.0, lh=None, **kw):
    """Multi-line text, '\\n' separated; returns the y below the last line."""
    lh = lh or size * 1.35
    for i, t in enumerate(str(s).split("\n")):
        sh.text(x, y + i * lh, t, size=size, **kw)
    return y + len(str(s).split("\n")) * lh


def wrap(s, n):
    out, line = [], ""
    for w in s.split():
        if len(line) + len(w) + 1 > n and line:
            out.append(line)
            line = w
        else:
            line = (line + " " + w).strip()
    if line:
        out.append(line)
    return out


def block(sh, x, y, w, h, title, lines=(), fill="#ffffff", c=INK, tsize=2.4, size=1.9, sw=0.35, rx=1.2):
    """Framed block with a coloured title and text lines; h=None sizes it to the text. Returns its bottom."""
    if h is None:
        h = 4.2 + size * 1.6 + size * 1.4 * len(lines) + 1.2
    sh.rect(x, y, w, h, sw=sw, fill=fill, c=c, rx=rx)
    sh.text(x + 2, y + 4.4, title, size=tsize, weight="bold", c=c)
    yy = y + 4.4 + size * 1.6
    for t in lines:
        sh.text(x + 2.4, yy, t, size=size)
        yy += size * 1.4
    return y + h


def wire(sh, pts, c=INK, w=0.3, dash=None):
    sh.poly(pts, w=w, c=c, dash=dash)


def dot(sh, x, y, c=INK, r=0.55):
    sh.circle(x, y, r, sw=0, fill=c, c=c)


def image(sh, x, y, w, h, path):
    with open(path, "rb") as fh:
        b64 = base64.b64encode(fh.read()).decode()
    sh.add('<image x="%.2f" y="%.2f" width="%.2f" height="%.2f" preserveAspectRatio="xMidYMid meet" '
           'href="data:image/png;base64,%s"/>' % (x, y, w, h, b64))


# ---------------------------------------------------------------- schematic symbols (paper mm)
def resistor(sh, x, y, vertical=True, ref="", val="", L=9.0):
    """Between (x, y) and the returned end point; body 2.2 x 4.6 in the middle."""
    if vertical:
        sh.line(x, y, x, y + L / 2 - 2.3, w=0.25)
        sh.rect(x - 1.1, y + L / 2 - 2.3, 2.2, 4.6, sw=0.25, fill="#ffffff")
        sh.line(x, y + L / 2 + 2.3, x, y + L, w=0.25)
        sh.text(x + 1.8, y + L / 2 - 0.2, ref, size=1.6, weight="bold")
        sh.text(x + 1.8, y + L / 2 + 1.8, val, size=1.6)
        return x, y + L
    sh.line(x, y, x + L / 2 - 2.3, y, w=0.25)
    sh.rect(x + L / 2 - 2.3, y - 1.1, 4.6, 2.2, sw=0.25, fill="#ffffff")
    sh.line(x + L / 2 + 2.3, y, x + L, y, w=0.25)
    sh.text(x + L / 2, y - 1.8, ref + (" " + val if val else ""), size=1.6, anchor="middle")
    return x + L, y


def capacitor(sh, x, y, ref="", val="", L=7.0, polar=False):
    """Vertical, from (x, y) down."""
    m = y + L / 2
    sh.line(x, y, x, m - 0.7, w=0.25)
    sh.line(x - 1.8, m - 0.7, x + 1.8, m - 0.7, w=0.45)
    sh.line(x - 1.8, m + 0.7, x + 1.8, m + 0.7, w=0.45)
    sh.line(x, m + 0.7, x, y + L, w=0.25)
    if polar:
        sh.text(x - 2.6, m - 1.2, "+", size=1.6)
    sh.text(x + 2.4, m - 0.2, ref, size=1.6, weight="bold")
    sh.text(x + 2.4, m + 1.8, val, size=1.6)
    return x, y + L


def diode(sh, x1, y1, x2, y2, ref="", val="", led=False, schottky=False, arrow_side=1):
    """Anode (x1, y1) -> cathode (x2, y2), axis-aligned."""
    import math
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    px, py = -uy, ux
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    a = (mx - ux * 1.3, my - uy * 1.3)
    k = (mx + ux * 1.3, my + uy * 1.3)
    sh.line(x1, y1, a[0], a[1], w=0.25)
    sh.line(k[0], k[1], x2, y2, w=0.25)
    sh.poly([(a[0] + px * 1.4, a[1] + py * 1.4), (a[0] - px * 1.4, a[1] - py * 1.4), k], w=0.25,
            fill="#ffffff" if not led else "#fff3d6", close=True)
    sh.line(k[0] + px * 1.4, k[1] + py * 1.4, k[0] - px * 1.4, k[1] - py * 1.4, w=0.35)
    if schottky:
        sh.line(k[0] + px * 1.4, k[1] + py * 1.4, k[0] + px * 1.4 - ux * 0.6, k[1] + py * 1.4 - uy * 0.6, w=0.3)
        sh.line(k[0] - px * 1.4, k[1] - py * 1.4, k[0] - px * 1.4 + ux * 0.6, k[1] - py * 1.4 + uy * 0.6, w=0.3)
    if led:
        qx, qy = px * arrow_side, py * arrow_side
        for o in (-0.7, 0.7):
            bx, by = mx + qx * 1.9 + ux * o, my + qy * 1.9 + uy * o
            sh.arrow(bx, by, bx + qx * 2.2 + ux * 0.9, by + qy * 2.2 + uy * 0.9, w=0.18)
    tx, ty = mx - px * 3.2, my - py * 3.2
    sh.text(tx, ty + 0.6, ref + (" " + val if val else ""), size=1.6, anchor="middle")


def npn(sh, x, y, ref="", val=""):
    """Base at (x, y) (left); returns (collector, emitter) points above / below the body at x + 4."""
    sh.circle(x + 3.0, y, 3.0, sw=0.25, fill="#ffffff")
    sh.line(x, y, x + 2.0, y, w=0.25)
    sh.line(x + 2.0, y - 1.8, x + 2.0, y + 1.8, w=0.45)
    sh.line(x + 2.0, y - 0.8, x + 4.0, y - 2.6, w=0.25)
    sh.line(x + 2.0, y + 0.8, x + 4.0, y + 2.6, w=0.25)
    sh.arrow(x + 2.9, y + 1.8, x + 3.9, y + 2.55, w=0.2)
    c, e = (x + 4.0, y - 4.4), (x + 4.0, y + 4.4)
    sh.line(x + 4.0, y - 2.6, c[0], c[1], w=0.25)
    sh.line(x + 4.0, y + 2.6, e[0], e[1], w=0.25)
    sh.text(x + 6.6, y - 0.4, ref, size=1.6, weight="bold")
    sh.text(x + 6.6, y + 1.6, val, size=1.5)
    return c, e


def gnd(sh, x, y):
    sh.line(x, y, x, y + 1.4, w=0.25)
    for i, hw in enumerate((1.8, 1.2, 0.6)):
        sh.line(x - hw, y + 1.4 + i * 0.6, x + hw, y + 1.4 + i * 0.6, w=0.3)


def rail(sh, x, y, name, c=RED, up=True):
    """Supply flag at (x, y): a short bar with the rail name."""
    yb = y - 1.6 if up else y + 1.6
    sh.line(x, y, x, yb, w=0.25)
    sh.line(x - 1.6, yb, x + 1.6, yb, w=0.45, c=c)
    sh.text(x, yb - 0.9 if up else yb + 2.2, name, size=1.6, anchor="middle", c=c, weight="bold")


def netflag(sh, x, y, name, right=True, c=BLUE):
    """Net label flag; the wire meets it at (x, y)."""
    w = 1.15 * len(name) + 2.4
    if right:
        pts = [(x, y), (x + 1.2, y - 1.4), (x + w, y - 1.4), (x + w, y + 1.4), (x + 1.2, y + 1.4)]
        tx = x + 1.6
    else:
        pts = [(x, y), (x - 1.2, y - 1.4), (x - w, y - 1.4), (x - w, y + 1.4), (x - 1.2, y + 1.4)]
        tx = x - w + 0.6
    sh.poly(pts, w=0.25, c=c, fill="#eef4fb", close=True)
    sh.text(tx, y + 0.65, name, size=1.6, c=c, weight="bold")


def conn(sh, x, y, ref, pins, side="left", title="", pitch=3.6):
    """Connector box; pins listed top to bottom; wires meet at the returned points on `side`."""
    w, h = 7.0, pitch * len(pins) + 1.6
    sh.rect(x, y, w, h, sw=0.3, fill="#fbf3e2")
    sh.text(x + w / 2, y - 1.0, ref, size=1.8, anchor="middle", weight="bold")
    if title:
        sh.text(x, y + h + 2.6, title, size=1.5, c=THIN)
    pts = []
    for i, p in enumerate(pins):
        yy = y + 1.6 + pitch * (i + 0.5)
        sh.text(x + w / 2, yy + 0.55, str(i + 1), size=1.4, anchor="middle")
        if side == "left":
            sh.line(x - 2.0, yy, x, yy, w=0.25)
            sh.text(x - 2.4, yy - 0.5, p, size=1.4, anchor="end", c=THIN)
            pts.append((x - 2.0, yy))
        else:
            sh.line(x + w, yy, x + w + 2.0, yy, w=0.25)
            sh.text(x + w + 2.4, yy - 0.5, p, size=1.4, c=THIN)
            pts.append((x + w + 2.0, yy))
    return pts


def cell(sh, x, y, w, h, title):
    sh.rect(x, y, w, h, sw=0.2, c="#9aa1a8", dash="1.2 0.8", rx=1.0)
    sh.text(x + 1.5, y + 3.4, title, size=2.0, weight="bold", c=THIN)


# ======================================================================= sheet 1 - system
def sheet1(tot):
    sh = new_sheet(1, "System overview")
    sh.rect(14, 24, 108, 150, sw=0.3, fill="#f7f8fa", c="#9aa1a8", rx=2)
    sh.text(17, 29.5, "UPPER DOOR - outside the steel, so Wi-Fi works", size=2.0, weight="bold", c=THIN)
    sh.rect(158, 24, 248, 150, sw=0.3, fill="#f7f8fa", c="#9aa1a8", rx=2)
    sh.text(161, 29.5, "INSIDE THE RACK", size=2.0, weight="bold", c=THIN)

    # ---- touchscreen
    yb = block(sh, 19, 33, 98, None, "TOUCHSCREEN  Waveshare ESP32-S3-Touch-LCD-4.3B", [
        "4.3 in 800 x 480 IPS, capacitive touch, in the printed pod P6",
        "Shows cold / hot side, AC state, every sensor, alarms",
        "Sets mode (auto / on / off), intake target, eco, fan, limits",
        "Modbus client on RS485: polls the node every 2 s",
        "Wi-Fi: Home Assistant API, web page, over-the-air updates",
        "Room SHT41 in the pod vent; upper door contact on DI0",
        "Buzzer on DO0; alarm output DO1 for a beacon",
        "Real-time clock keeps the time through power cuts"], c=BLUE, size=2.0)
    img = os.path.join(ROOT, "renders", "hmi_status.png")
    if os.path.exists(img):
        sh.rect(22, yb + 5, 92, 55.2, sw=0.6, fill="#0e1116")
        image(sh, 22, yb + 5, 92, 55.2, img)
        sh.text(68, yb + 63.4, "status screen - firmware preview, real size 95 x 57 mm", size=1.6, anchor="middle",
                c=THIN)
    hb = block(sh, 19, yb + 71, 98, None, "HOME ASSISTANT  (optional, over Wi-Fi)", [
        "history, phone alerts, automations; the 'IT shutdown request'",
        "can run NUT / ssh shutdowns of the servers (software path)"], c=GREEN, size=1.9)
    mtext(sh, 19, hb + 5, "Pod P6: 128 x 91 x 36 mm, PETG, on two M4 rivnuts in the upper door;\nthe cable "
          "enters through the door's 20 mm grommet (DXF DU1).", size=1.7, c=THIN)

    # ---- door bus
    ys = [44, 48, 52, 56]
    for (lab, col), yy in zip((("+12 V", RED), ("0 V", INK), ("A", BLUE), ("B", BLUE)), ys):
        sh.line(117, yy, 166, yy, w=0.5, c=col)
        sh.text(124, yy - 0.7, lab, size=1.6, c=col)
    sh.rect(136, 40.5, 8, 19, sw=0.35, fill="#fbf3e2")
    sh.text(140, 50, "GX16-4", size=1.4, anchor="middle", rot=-90)
    sh.text(140, 37.5, "W1  door bus", size=2.1, anchor="middle", weight="bold")
    mtext(sh, 140, 64, "4-core shielded, 1.5 m\nRS485 Modbus RTU\n19 200 baud 8N1\nthrough a hinge loop;\n"
          "the GX16 plug lets\nthe door lift off", size=1.6, anchor="middle")

    # ---- node
    nb = block(sh, 166, 33, 98, None, "RACK NODE  ESP32-S3-DevKitC-1 on a carrier, box P7", [
        "Runs the cooling on its own: needs neither the screen nor",
        "the network to keep the rack cool. Modbus server 1.",
        "Reads 6 DS18B20 probes + an SHT41 every 10 s",
        "Decides every 5 s: AC on / off, setpoint, fan, eco",
        "Sends the AC's own remote frames by IR (coolix / midea)",
        "Alarms; closes the SHUTDOWN relay K1 when critical",
        "12 V in, 5 V buck, 3.3 V on the DevKit; about 1 W",
        "Fail-safe: anything unknown means AC on"], c=BLUE, size=2.0)
    sh.text(215, nb + 3.6, "pins, schematic and board: sheet 2   -   where it all goes: sheet 4", size=1.6,
            anchor="middle", c=THIN)
    io = [("T1 T2  cold side top / middle", "J5", BLUE, "front plenum: server intake"),
          ("T3  AC supply air", "J5", BLUE, "hood outlet"),
          ("SHT41  cold-side humidity", "J4", BLUE, "dew point: condensation watch"),
          ("T4  hot side top", "J6", RED, "rear plenum: server exhaust"),
          ("T5  AC return air", "J6", RED, "rear plenum, above the return opening"),
          ("T6  AC exhaust", "J6", RED, "condenser elbow: is the compressor on?"),
          ("IR emitter -> AC receiver", "J7", AMBER, "on / off, setpoint, fan"),
          ("Tray float switch", "J8", AMBER, "water in the drip tray"),
          ("Lower door contact", "J9", AMBER, "door left open"),
          ("Mains detect (option)", "J10", GREY, "AC socket live: faster restart"),
          ("SHUTDOWN contact K1", "J3", GREEN, "to the UPS / server signal input")]
    for i, (lab, j, col, sub) in enumerate(io):
        yy = 36 + i * 12.2
        ya = 37 + i * (nb - 41) / (len(io) - 1)
        sh.line(264, ya, 300, yy + 2, w=0.35, c=col)
        sh.rect(300, yy - 2.0, 9, 8, sw=0.3, fill="#fbf3e2")
        sh.text(304.5, yy + 3.2, j, size=1.7, anchor="middle", weight="bold")
        sh.text(311.5, yy + 1.4, lab, size=2.1, weight="bold", c=col)
        sh.text(311.5, yy + 4.6, sub, size=1.7, c=THIN)

    # ---- AC, power
    ab = block(sh, 166, nb + 10, 98, None, "AIR CONDITIONER  Dimplex GDC14RBA", [
        "keeps its own thermostat and compressor timer: the node",
        "sends only what its remote would. The stick-on emitter sits",
        "on its IR window; the AC still rolls out (unplug the lead)"], c=AMBER, size=2.0)
    pb = block(sh, 166, ab + 6, 98, None, "POWER  12 V 2 A plug pack on the UPS-backed PDU", [
        "node + screen about %.1f W typical; everything is SELV" % tot["power_w"],
        "on the UPS, so the node can still ask for a clean shutdown",
        "the AC stays on its own wall socket"], c=RED, size=2.0)
    block(sh, 166, pb + 6, 98, None, "WHEN SOMETHING FAILS", [
        "screen or Wi-Fi down: the node keeps cooling, unchanged",
        "node down: the screen shows 'Rack link' red and beeps",
        "probe lost: alarm, and the AC is kept on",
        "too hot 120 s: K1 + Home Assistant ask for an IT shutdown"], c=GREEN, size=2.0)

    # ---- bottom: why ESP32, cost, files, decisions, key figures
    x0, y0 = 14, 183
    heading(sh, x0, y0, "Why ESP32 and not a Raspberry Pi 5")
    rows = [("Boot after a power cut", "about 1 s, nothing to corrupt", "20-40 s, SD card at risk"),
            ("Heat inside a sealed rack", "about 1 W", "5-10 W plus a fan"),
            ("IR timing", "hardware (RMT peripheral)", "needs a driver or helper chip"),
            ("12 V from the UPS", "direct (buck / 7-36 V panel)", "5 V 5 A supply"),
            ("Touchscreen", "panel with RS485 + isolated I/O", "DSI panel + USB adapters"),
            ("Home Assistant", "native ESPHome API", "MQTT / custom code"),
            ("Parts cost", "about AUD %.0f for the kit" % tot["kit"], "about AUD 250 more")]
    yb = table(sh, x0, y0 + 3, [(40, "l"), (52, "l"), (50, "l")], rows, head=("", "ESP32-S3 kit", "Pi 5 instead"),
               size=1.8, rh=3.6)
    sh.text(x0, yb + 3.4, "A Pi 5 is still a fine Home Assistant host - outside the rack, on the network.",
            size=1.7, c=THIN)
    heading(sh, x0, 231, "Kit cost (bom/electronics.csv, indicative AUD)")
    groups = OrderedDict()
    for g, ref, item, spec, q, u, opt in KIT:
        groups[g] = groups.get(g, 0.0) + q * u
    rows = [(g, "%.0f" % v) for g, v in groups.items() if g != "Options"]
    rows.append(("Kit total", "%.0f" % tot["kit"]))
    rows.append(("Options: mains detect, beacon", "%.0f" % tot["opt"]))
    table(sh, x0, 234, [(60, "l"), (20, "r")], rows, size=1.8, rh=3.4)

    x1 = 166
    heading(sh, x1, y0, "What is where")
    rows = [("firmware/sra16-node.yaml", "rack node (ESPHome 2026.6)"),
            ("firmware/sra16-hmi.yaml, hmi/ui.yaml", "touchscreen and its screens"),
            ("firmware/components/sra_control/", "control core (C++, header only)"),
            ("firmware/test/", "unit tests, simulation report"),
            ("tools/sim_controller.py", "thermal model, drives the real core"),
            ("cad/print P6 P7 P8, P1-1 port", "pod, node box, clips, hood port"),
            ("bom/electronics*.csv", "kit parts, harness"),
            ("docs/ELECTRONICS.md", "build, install, commissioning")]
    table(sh, x1, y0 + 3, [(52, "l"), (50, "l")], rows, size=1.8, rh=3.6)
    heading(sh, x1, 231, "One decision, every 5 s")
    steps = ["1  read the probes (every 10 s); 10-minute averages smooth the",
             "   compressor's own cycling",
             "2  choose AC on / off, setpoint and fan (sheet 5)",
             "3  send by IR only if something changed (at most every 10 s)",
             "4  check it worked: supply air below return, exhaust above room",
             "5  not cooling: re-send 3 times, then alarm; critical: ask for",
             "   the IT to shut down (K1 + Home Assistant)"]
    for i, t in enumerate(steps):
        sh.text(x1, 235.5 + i * 3.0, t, size=1.75)

    x2 = 276
    heading(sh, x2, y0, "Key figures")
    rows = [("Probes", "6 x DS18B20 (0.5 K) + 2 x SHT41"),
            ("Decision cycle", "5 s; IR at most every 10 s"),
            ("Bus", "RS485, 1.5 m, 19 200 baud"),
            ("Supply", "12 V, %.1f W typical" % tot["power_w"]),
            ("Simulation", tot["sim"]),
            ("Unit tests", tot["tests"]),
            ("Firmware size", "node 48 % flash, screen 17 %")]
    table(sh, x2, y0 + 3, [(30, "l"), (100, "l")], rows, size=1.8, rh=3.6)
    heading(sh, x2, 220, "Typical sources (Australia)")
    rows = [("Panel, DevKit, SHT41, buck", "Core Electronics, DigiKey, Mouser"),
            ("Probes, float, reeds, GX16, IR", "Altronics, Jaycar, AliExpress"),
            ("Terminals, board, R / C, relay", "Altronics, Element14, DigiKey"),
            ("Plug pack (RCM approved)", "Jaycar, Altronics")]
    table(sh, x2, 223, [(46, "l"), (84, "l")], rows, size=1.7, rh=3.4)
    title_block(sh, 1, "System overview, why ESP32, files")
    return sh


# ======================================================================= sheet 2 - node carrier
def sheet2():
    sh = new_sheet(2, "Rack node carrier")
    # ---------------- U1 (column B) with its nets
    ux, uy, uw = 120, 30, 28
    pins_l = [(4, "IR_TX"), (5, "IR_RX"), (6, "OW_COLD"), (7, "OW_HOT"), (8, "SDA"), (9, "SCL"),
              (10, "DOOR_LO"), (11, "LEAK"), (12, "MAINS"), (13, "SD_RLY")]
    pins_r = [("5V", "+5V_U1"), ("3V3", "+3V3"), ("GND", "0V"), ("GPIO17", "TXD"), ("GPIO18", "RXD")]
    uh = 6.0 * len(pins_l) + 6
    sh.rect(ux, uy, uw, uh, sw=0.45, fill="#dbe7f5")
    sh.text(ux + uw / 2, uy - 4.2, "U1  ESP32-S3-DevKitC-1", size=2.0, anchor="middle", weight="bold")
    sh.text(ux + uw / 2, uy - 1.4, "N8R8: GPIO35-37 are the PSRAM's", size=1.4, anchor="middle", c=THIN)
    for i, (g, net) in enumerate(pins_l):
        yy = uy + 5 + i * 6.0
        sh.line(ux - 6, yy, ux, yy, w=0.25)
        sh.text(ux + 1.2, yy + 0.6, "GPIO%d" % g, size=1.6)
        netflag(sh, ux - 6, yy, net, right=False)
    for i, (p, net) in enumerate(pins_r):
        yy = uy + 5 + i * 6.0
        sh.line(ux + uw, yy, ux + uw + 6, yy, w=0.25)
        sh.text(ux + uw - 1.2, yy + 0.6, p, size=1.6, anchor="end")
        if net == "0V":
            gnd(sh, ux + uw + 6, yy)
        else:
            netflag(sh, ux + uw + 6, yy, net, c=RED if net.startswith("+") else BLUE)
    mtext(sh, ux + uw / 2, uy + uh + 4, "3.3 V logic: never 5 V\non a GPIO", size=1.5, anchor="middle", c=RED)
    mtext(sh, ux - 4, uy + uh + 12, "2 x 22-way sockets\nUSB-C ports up (lid side)\nfor the first flash", size=1.5,
          c=THIN)

    # ---------------- POWER (column A top)
    cell(sh, 12, 20, 89, 40, "POWER")
    j1 = conn(sh, 16, 30, "J1", ["+12V", "0V"], side="right", title="12 V in (W8)")
    x, y = j1[0]
    wire(sh, [(x, y), (x + 5, y)])
    resistor(sh, x + 5, y, vertical=False, ref="F1", val="PTC", L=10)
    wire(sh, [(x + 15, y), (x + 31, y)])
    dot(sh, x + 21, y)
    rail(sh, x + 21, y, "+12V")
    capacitor(sh, x + 21, y, "C1", "100u", L=11, polar=True)
    gnd(sh, x + 21, y + 11)
    wire(sh, [j1[1], (j1[1][0] + 3, j1[1][1])])
    gnd(sh, j1[1][0] + 3, j1[1][1])
    sh.rect(x + 31, y - 4, 16, 13, sw=0.35, fill="#e4f2e1")
    sh.text(x + 39, y + 2.2, "U3", size=1.8, anchor="middle", weight="bold")
    sh.text(x + 39, y + 4.8, "5 V buck", size=1.3, anchor="middle")
    sh.text(x + 32, y - 0.8, "IN", size=1.2)
    sh.text(x + 46, y - 0.8, "OUT", size=1.2, anchor="end")
    wire(sh, [(x + 39, y + 9), (x + 39, y + 11)])
    gnd(sh, x + 39, y + 11)
    wire(sh, [(x + 47, y), (x + 51, y)])
    dot(sh, x + 51, y)
    rail(sh, x + 51, y, "+5V")
    capacitor(sh, x + 51, y, "C2", "100u", L=11, polar=True)
    gnd(sh, x + 51, y + 11)
    diode(sh, x + 51, y, x + 60, y, "D3", "", schottky=True)
    netflag(sh, x + 60, y, "+5V_U1", c=RED)
    sh.text(15, 57.6, "+12V also feeds J2 (door bus, after F1) and K1. U1's own LDO makes +3V3.", size=1.4,
            c=THIN)

    # ---------------- PROBES + I2C (column A middle)
    cell(sh, 12, 63, 89, 58, "PROBES (1-Wire)  +  HUMIDITY (I2C)")
    for k, (jr, net, rr, rv, lab) in enumerate((("J5", "OW_COLD", "R1", "4.7k", "T1 T2 T3"),
                                                 ("J6", "OW_HOT", "R2", "2.2k", "T4 T5 T6 (W2)"))):
        bx = 16 + k * 44
        pts = conn(sh, bx, 78, jr, ["3V3", "DQ", "0V"], side="right", title=lab)
        wire(sh, [pts[0], (bx + 15, pts[0][1])], c=RED)
        rail(sh, bx + 15, pts[0][1], "+3V3")
        wire(sh, [pts[1], (bx + 25, pts[1][1])])
        dot(sh, bx + 19, pts[1][1])
        resistor(sh, bx + 19, pts[1][1] - 11, vertical=True, ref=rr, val=rv, L=11)
        rail(sh, bx + 19, pts[1][1] - 11, "")
        netflag(sh, bx + 25, pts[1][1], net)
        wire(sh, [pts[2], (bx + 11, pts[2][1]), (bx + 11, pts[2][1] + 0.5)])
        gnd(sh, bx + 11, pts[2][1] + 0.5)
    pts = conn(sh, 16, 100, "J4", ["3V3", "0V", "SDA", "SCL"], side="right", title="")
    sh.text(16, 119.2, "SHT41 cold side (W7)", size=1.5, c=THIN)
    wire(sh, [pts[0], (29, pts[0][1])], c=RED)
    rail(sh, 29, pts[0][1], "+3V3")
    wire(sh, [pts[1], (33, pts[1][1]), (33, pts[1][1] + 0.5)])
    gnd(sh, 33, pts[1][1] + 0.5)
    for i, (net, rr, xx, fx) in enumerate((("SDA", "R3", 40, 46), ("SCL", "R4", 56, 62))):
        p = pts[2 + i]
        wire(sh, [p, (fx, p[1])])
        dot(sh, xx, p[1])
        resistor(sh, xx, p[1] - 10, vertical=True, ref=rr, val="4.7k", L=10)
        rail(sh, xx, p[1] - 10, "")
        netflag(sh, fx, p[1], net)

    # ---------------- INPUTS (column A bottom)
    cell(sh, 12, 124, 89, 40, "INPUTS  (contact to 0 V)")
    for k, (jr, net, rs, ru, cc, lab) in enumerate((("J8", "LEAK", "R9", "R10", "C4", "float switch"),
                                                     ("J9", "DOOR_LO", "R11", "R12", "C5", "lower door"))):
        bx = 15 + k * 43
        pts = conn(sh, bx, 138, jr, ["IN", "0V"], side="right", title=lab)
        x0_, y0_ = pts[0]
        resistor(sh, x0_, y0_, vertical=False, ref=rs, val="1k", L=9)
        wire(sh, [(x0_ + 9, y0_), (x0_ + 20, y0_)])
        dot(sh, x0_ + 12, y0_)
        resistor(sh, x0_ + 12, y0_ - 9.5, vertical=True, ref=ru, val="10k", L=9.5)
        rail(sh, x0_ + 12, y0_ - 9.5, "")
        dot(sh, x0_ + 16, y0_)
        capacitor(sh, x0_ + 16, y0_, cc, "100n", L=8)
        gnd(sh, x0_ + 16, y0_ + 8)
        netflag(sh, x0_ + 20, y0_, net)
        wire(sh, [pts[1], (pts[1][0] + 3, pts[1][1]), (pts[1][0] + 3, pts[1][1] + 0.5)])
        gnd(sh, pts[1][0] + 3, pts[1][1] + 0.5)
    sh.text(15, 161.6, "Polarity is set in the firmware; rails without a name are +3V3.", size=1.4, c=THIN)

    # ---------------- MAINS DETECT (column B bottom)
    cell(sh, 104, 124, 64, 62, "MAINS DETECT (option)")
    pts = conn(sh, 108, 140, "J10", ["5V+", "5V-"], side="right", title="")
    mtext(sh, 108, 156, "W2: 5 V from a\ncharger in the\nAC's GPO", size=1.4, c=THIN)
    wire(sh, [pts[0], (122, pts[0][1]), (122, 141)])
    resistor(sh, 122, 141, vertical=False, ref="R13", val="1k", L=8)
    wire(sh, [(130, 141), (139, 141)])
    wire(sh, [pts[1], (124, pts[1][1]), (124, 151), (139, 151)])
    diode(sh, 133.5, 151, 133.5, 141)
    dot(sh, 133.5, 141)
    dot(sh, 133.5, 151)
    sh.text(131.9, 146.6, "D2", size=1.4, anchor="end")
    sh.rect(136, 136.5, 22, 19, sw=0.3, fill="#f7f7f7", dash="1 0.6")
    sh.text(147, 135.5, "U5 PC817", size=1.5, anchor="middle", weight="bold")
    diode(sh, 139, 141, 139, 151, led=True, arrow_side=-1)
    sh.line(147, 139.5, 147, 152.5, w=0.45)
    sh.line(147, 143, 152, 140.5, w=0.25)
    sh.line(147, 149, 152, 151.5, w=0.25)
    sh.arrow(150.2, 150.6, 151.8, 151.4, w=0.2)
    wire(sh, [(152, 140.5), (160, 140.5)])
    wire(sh, [(152, 151.5), (152, 158)])
    gnd(sh, 152, 158)
    dot(sh, 160, 140.5)
    resistor(sh, 160, 131.0, vertical=True, ref="", val="", L=9.5)
    sh.text(161.8, 134.4, "R14", size=1.4, weight="bold")
    sh.text(161.8, 136.6, "10k", size=1.4)
    rail(sh, 160, 131.0, "")
    wire(sh, [(160, 140.5), (160, 145.5)])
    netflag(sh, 160, 145.5, "MAINS")
    mtext(sh, 107, 170, "Isolated: the charger only lights U5's LED.\nC6 100n from MAINS to 0 V. Firmware:\n"
          "mains_fitted: \"true\" once wired.", size=1.4, c=THIN)

    # ---------------- RS485 (column C top)
    cell(sh, 170, 20, 90, 40, "RS485 TO THE TOUCHSCREEN")
    sh.rect(188, 27, 26, 27, sw=0.35, fill="#e8e1f2")
    sh.text(201, 31.2, "U2", size=1.8, anchor="middle", weight="bold")
    sh.text(201, 33.8, "RS485 module", size=1.3, anchor="middle")
    sh.text(201, 36.0, "auto direction", size=1.3, anchor="middle")
    for i, (p, net) in enumerate((("VCC", "+3V3"), ("DI/TXD", "TXD"), ("RO/RXD", "RXD"), ("GND", "0V"))):
        yy = 40 + i * 3.6
        sh.text(189, yy + 0.5, p, size=1.3)
        sh.line(182, yy, 188, yy, w=0.25)
        if net == "0V":
            gnd(sh, 182, yy)
        else:
            netflag(sh, 182, yy, net, right=False, c=RED if net.startswith("+") else BLUE)
    j2 = conn(sh, 242, 30, "J2", ["+12V", "0V", "A", "B"], side="left", title="")
    sh.text(242, 51.5, "door bus W1", size=1.4, c=THIN)
    for i, p in enumerate(("A", "B")):
        yy = j2[2 + i][1]
        sh.text(213.4, yy + 0.5, p, size=1.3, anchor="end")
        wire(sh, [(214, yy), j2[2 + i]], c=BLUE)
    wire(sh, [j2[0], (228, j2[0][1])], c=RED)
    rail(sh, 228, j2[0][1], "+12V")
    wire(sh, [j2[1], (234, j2[1][1]), (234, j2[1][1] + 0.5)])
    gnd(sh, 234, j2[1][1] + 0.5)
    sh.text(173, 57.6, "C7 100n at U2's VCC. 120R at each end (module + panel).", size=1.4, c=THIN)

    # ---------------- IR (column C middle)
    cell(sh, 170, 63, 90, 58, "IR: EMITTER TO THE AC, RECEIVER FOR LEARNING")
    rail(sh, 202, 72, "+5V")
    resistor(sh, 202, 72, vertical=True, ref="R6", val="150R", L=9)
    j7 = conn(sh, 209, 82, "J7", ["IR+", "IR-"], side="left", title="")
    sh.text(209, 94.6, "emitter lead W4", size=1.4, c=THIN)
    wire(sh, [(202, 81), (202, j7[0][1]), j7[0]])
    wire(sh, [j7[1], (198, j7[1][1]), (198, 95.0), (194, 95.0)])
    c, e = npn(sh, 190, 99.4, "Q1", "PN2222A")
    gnd(sh, e[0], e[1])
    resistor(sh, 180, 99.4, vertical=False, ref="R5", val="1k", L=10)
    netflag(sh, 180, 99.4, "IR_TX", right=False)
    sh.text(173, 117.6, "Emitter: tip +, sleeve -. About 22 mA peaks.", size=1.4, c=THIN)
    sh.rect(228, 100, 12, 14, sw=0.35, fill="#dddddd")
    sh.text(234, 105, "U4", size=1.7, anchor="middle", weight="bold")
    sh.text(234, 107.4, "TSOP", size=1.2, anchor="middle")
    sh.text(234, 109.4, "38238", size=1.2, anchor="middle")
    sh.line(223, 107, 228, 107, w=0.25)
    sh.text(228.6, 106.4, "", size=1.2)
    netflag(sh, 223, 107, "IR_RX", right=False)
    for p, yy in (("VS", 102.5), ("GND", 111.5)):
        sh.text(239.4, yy - 0.5, p, size=1.2, anchor="end")
        sh.line(240, yy, 243, yy, w=0.25)
    resistor(sh, 243, 102.5, vertical=False, ref="R7", val="", L=8)
    rail(sh, 251, 102.5, "+3V3")
    dot(sh, 243, 102.5)
    capacitor(sh, 243, 102.5, "C3", "4.7u", L=9)
    gnd(sh, 243, 111.5)

    # ---------------- SHUTDOWN relay (column C bottom)
    cell(sh, 170, 124, 90, 62, "SHUTDOWN RELAY  (dry contact)")
    dy = 5.0
    netflag(sh, 182, 152.9 + dy, "SD_RLY", right=False)
    resistor(sh, 182, 152.9 + dy, vertical=False, ref="R8", val="1k", L=10)
    c, e = npn(sh, 192, 152.9 + dy, "Q2", "PN2222A")
    gnd(sh, e[0], e[1])
    rail(sh, 202, 131 + dy, "+12V")
    sh.rect(198, 134 + dy, 8, 10, sw=0.35, fill="#f3dede")
    sh.line(198, 144 + dy, 206, 134 + dy, w=0.25)
    sh.text(197, 139.6 + dy, "K1", size=1.8, weight="bold", anchor="end")
    wire(sh, [(202, 131 + dy), (202, 134 + dy)])
    diode(sh, 212, 144 + dy, 212, 134 + dy, "", "")
    sh.text(214.4, 139.6 + dy, "D1", size=1.4)
    wire(sh, [(202, 132.5 + dy), (212, 132.5 + dy), (212, 134 + dy)])
    wire(sh, [(202, 144 + dy), (202, 148.5 + dy), (196, 148.5 + dy)])
    wire(sh, [(212, 144 + dy), (212, 148.5 + dy), (202, 148.5 + dy)])
    dot(sh, 202, 148.5 + dy)
    dot(sh, 202, 132.5 + dy)
    cx, cy = 222, 141 + dy
    sh.circle(cx, cy, 0.7, sw=0.25, fill="#ffffff")
    sh.circle(cx + 9, cy - 4, 0.7, sw=0.25, fill="#ffffff")
    sh.circle(cx + 9, cy + 4, 0.7, sw=0.25, fill="#ffffff")
    sh.line(cx + 0.6, cy, cx + 8.4, cy + 3.4, w=0.35)
    sh.text(cx + 4.5, cy + 8.4, "contact shown", size=1.2, anchor="middle", c=THIN)
    sh.text(cx + 4.5, cy + 10.2, "de-energised", size=1.2, anchor="middle", c=THIN)
    j3 = conn(sh, 244, 134 + dy, "J3", ["COM", "NO", "NC"], side="left", title="")
    sh.text(244, 148.9 + dy, "via W2", size=1.4, c=THIN)
    wire(sh, [(cx - 0.7, cy), (cx - 3, cy), (cx - 3, 132 + dy), (237, 132 + dy), (237, j3[0][1]), j3[0]])
    wire(sh, [(cx + 9.7, cy - 4), (235, cy - 4), (235, j3[1][1]), j3[1]])
    wire(sh, [(cx + 9.7, cy + 4), (238.5, cy + 4), (238.5, j3[2][1]), j3[2]])
    mtext(sh, 173, 174, "COM-NO closes while the node asks for the IT to shut\ndown (latched until 'Reset alarms'). "
          "For UPS / server\nsignal inputs only: 1 A, 30 V DC.", size=1.4, c=THIN)

    # ---------------- board layout (right)
    k = 1.25
    heading(sh, 268, 24, "BOARD  70 x 90, component side, 1.25 : 1", size=2.3)
    bw, bh = BOARD[0] * k, BOARD[1] * k
    ox, oy = 268 + 18 + bw / 2, 30 + bh / 2              # board centre on paper

    def P(x, y):
        return ox + x * k, oy - y * k
    sh.rect(ox - bw / 2, oy - bh / 2, bw, bh, sw=0.5, fill="#f4efe1")
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx_, cy_ = P(sx * 33, sy * 43)
            sh.circle(cx_, cy_, 1.4 * k, sw=0.25, fill="#ffffff")
    for ref, x0, y0, x1, y1, lab, fill in PLACE:
        a, b = P(x0, y1)
        c_, d = P(x1, y0)
        sh.rect(a, b, c_ - a, d - b, sw=0.3, fill=fill)
        lines = lab.split("\n")
        tall = (c_ - a) < 14
        for i, t in enumerate(lines):
            if tall and len(t) > 3:
                sh.text((a + c_) / 2 + 0.6, (b + d) / 2, t, size=1.5, anchor="middle", weight="bold", rot=-90)
            else:
                sh.text((a + c_) / 2, (b + d) / 2 + (i - (len(lines) - 1) / 2) * 2.6 + 0.6, t,
                        size=1.6 if i == 0 else 1.4, anchor="middle", weight="bold" if i == 0 else "normal")
    xx = -34.0
    pins_of = dict((c_[0], c_[2]) for c_ in CONN)
    for j in TERM_ROW:
        n = len(pins_of[j])
        a, b = P(xx, -37.0)
        c_, d = P(xx + 3.5 * n, -45.0)
        sh.rect(a, b, c_ - a, d - b, sw=0.3, fill="#8fbf8f" if j != "J1" else "#e0a090")
        sh.text((a + c_) / 2, b + 6.3, j, size=1.3 if len(j) > 2 else 1.5, anchor="middle", weight="bold")
        xx += 3.5 * n
    a, b = P(-35, -45)
    sh.text(ox, b + 4.0, "terminal row: wires enter from below (box slots at x -22, 0, +22)", size=1.4,
            anchor="middle", c=THIN)
    a, b = P(-35, 27)
    sh.text(a - 1.2, b + 0.6, "bus", size=1.3, anchor="end", c=THIN)
    sh.text(a - 1.2, b + 2.6, "slot", size=1.3, anchor="end", c=THIN)
    a, b = P(-3, -30)
    sh.text(a - 1.0, b - 0.4, "lid", size=1.2, anchor="end", c=THIN)
    sh.text(a - 1.0, b + 1.4, "window", size=1.2, anchor="end", c=THIN)
    a, b = P(-35, 45)
    sh.text(a - 1.2, b + 3, "door", size=1.3, anchor="end", c=THIN)
    sh.text(a - 1.2, b + 5, "side", size=1.3, anchor="end", c=THIN)
    sh.text(ox, oy + bh / 2 + 7.6, "upright in box P7, magnets at the right-hand end", size=1.4, anchor="middle",
            c=THIN)
    # stack height
    mtext(sh, 380, 34, "Height in P7\n(26.5 inside):\nstandoff 5\nboard 1.6\nsockets 8.5\nDevKit 1.6\n"
          "module 3.2\n= 19.9 + base\n2.5 = 22.4\nK1 10, U3 3", size=1.4, c=THIN)

    # ---------------- parts list (right, under the board)
    table(sh, 268, 157, [(18, "l"), (44, "l"), (80, "l")], CARRIER, head=("Ref", "Part", "Use"), size=1.5,
          rh=2.8)
    # ---------------- tables (bottom left)
    rows = [("GPIO%d" % g, n, w, f) for g, n, w, f, _ in GPIO]
    table(sh, 12, 192, [(14, "l"), (18, "l"), (24, "l"), (70, "l")], rows, head=("Pin", "Net", "Goes to", "Function"),
          size=1.5, rh=3.0)
    rows = [(r, t, " / ".join(p), u) for r, t, p, u in CONN]
    table(sh, 142, 192, [(9, "l"), (27, "l"), (29, "l"), (50, "l")], rows, head=("Conn", "Type", "Pins 1..n", "To"),
          size=1.4, rh=3.0)
    sh.text(12, 237, "Build: sockets for U1, then U3 and U2, then the terminal row. With U1 out, power J1: +5 V, "
            "+12 V on J2; fit U1: +3V3.", size=1.6)
    sh.text(12, 240.4, "Keep the 12 V wiring on the board's door-side half; 1-Wire and I2C short and away from "
            "K1. Pull-ups and filters as drawn.", size=1.6)
    title_block(sh, 2, "Node carrier: schematic, board, parts")
    return sh


# ======================================================================= sheet 3 - pod, harness, modbus
HA_ENTITIES = [
    ("sensor", "cold / hot side, T1-T6, room, RH, dew point, cold average, rise across the servers, setpoint "
               "sent, alarm bits, IR frames, uptime"),
    ("binary_sensor", "8 alarms (intake warning / critical, not cooling, water, door, probe, condensation, "
                      "AC socket), upper door, rack link, IT shutdown request"),
    ("select", "cooling mode (auto / on / off), AC fan (auto / low / high)"),
    ("number", "intake target, intake warning, shutdown limit"),
    ("switch", "eco (quiet at low load)"),
    ("button", "re-send state to the AC, reset alarms"),
    ("text_sensor", "cooling state, IP address"),
]


def sheet3():
    sh = new_sheet(3, "Touchscreen pod, harness, Modbus map")
    # ---------------- pod wiring
    cell(sh, 12, 22, 148, 90, "TOUCHSCREEN POD P6  (on the upper door)")
    bx0, by0 = 60, 30
    sh.rect(bx0, by0, 62, 48, sw=0.5, fill="#dbe7f5", rx=1.5)
    sh.text(bx0 + 34, by0 + 5, "Waveshare ESP32-S3-Touch-LCD-4.3B", size=1.8, anchor="middle", weight="bold")
    sh.text(bx0 + 34, by0 + 7.8, "rear view; terminal names as printed", size=1.4, anchor="middle", c=THIN)
    terms = [("VIN 7-36V", RED), ("GND", INK), ("RS485 A", BLUE), ("RS485 B", BLUE),
             ("DI0", AMBER), ("DI COM", AMBER), ("DO0", AMBER), ("DO1", AMBER), ("DO COM", AMBER)]
    tp = {}
    for i, (t, col) in enumerate(terms):
        yy = by0 + 13 + i * 3.6
        sh.rect(bx0, yy - 1.4, 4, 2.8, sw=0.25, fill="#fbf3e2")
        sh.text(bx0 + 5, yy + 0.6, t, size=1.5, c=col)
        tp[t] = (bx0, yy)
    sh.rect(bx0 + 42, by0 + 26, 17, 9, sw=0.3, fill="#ffffff")
    sh.text(bx0 + 50.5, by0 + 29.8, "I2C", size=1.5, anchor="middle", weight="bold")
    sh.text(bx0 + 50.5, by0 + 32.6, "3V3 GND SDA SCL", size=1.1, anchor="middle")
    sh.rect(bx0 + 42, by0 + 38, 17, 6, sw=0.3, fill="#ffffff")
    sh.text(bx0 + 50.5, by0 + 41.8, "USB-C (flash)", size=1.2, anchor="middle")
    # GX16 and W1
    gx, gy = 22, 30
    sh.rect(gx, gy, 9, 15, sw=0.35, fill="#fbf3e2")
    sh.text(gx + 4.5, gy - 1.5, "GX16-4", size=1.5, anchor="middle", weight="bold")
    for i, (lab, col, t) in enumerate((("1 +12V", RED, "VIN 7-36V"), ("2 0V", INK, "GND"),
                                        ("3 A", BLUE, "RS485 A"), ("4 B", BLUE, "RS485 B"))):
        yy = gy + 2.5 + i * 3.4
        xv = 52 - 2.4 * i
        sh.text(gx - 0.8, yy + 0.5, lab, size=1.4, anchor="end", c=col)
        wire(sh, [(gx + 9, yy), (xv, yy), (xv, tp[t][1]), tp[t]], c=col)
    mtext(sh, 15, 50, "W1 from the node,\nthrough the door\ngrommet", size=1.5, c=THIN)
    # door contact on DI0, 0 V on DI COM
    y_di = tp["DI0"][1]
    sh.text(19.5, y_di + 0.6, "+12V", size=1.5, anchor="end", c=RED)
    wire(sh, [(20, y_di), (24, y_di)], c=RED)
    sh.circle(24.6, y_di, 0.6, sw=0.25, fill="#ffffff")
    sh.circle(31.4, y_di, 0.6, sw=0.25, fill="#ffffff")
    sh.line(25.1, y_di - 0.3, 30.8, y_di - 2.4, w=0.3)
    sh.text(28, y_di + 3.4, "upper door contact", size=1.4, anchor="middle")
    sh.text(28, y_di + 5.6, "closed = shut", size=1.3, anchor="middle", c=THIN)
    wire(sh, [(32, y_di), tp["DI0"]], c=AMBER)
    for t in ("DI COM", "DO COM"):
        wire(sh, [tp[t], (bx0 - 6, tp[t][1])])
        sh.text(bx0 - 6.5, tp[t][1] + 0.6, "0V", size=1.5, anchor="end")
    # buzzer, beacon
    for i, (t, sym, lab, yy, xv) in enumerate((("DO0", "BZ", "buzzer 12 V", 92, bx0 - 15),
                                               ("DO1", "BC", "beacon 12 V (option)", 102, bx0 - 10))):
        wire(sh, [tp[t], (xv, tp[t][1]), (xv, yy), (34.5, yy)], c=AMBER)
        sh.circle(32, yy, 2.5, sw=0.3, fill="#ffffff")
        sh.text(32, yy + 0.6, sym, size=1.3, anchor="middle", weight="bold")
        wire(sh, [(29.5, yy), (24, yy)], c=RED)
        sh.text(23.5, yy + 0.6, "+12V", size=1.5, anchor="end", c=RED)
        sh.text(37, yy - 1.4, lab, size=1.4)
    # SHT41 room
    sh.rect(bx0 + 70, by0 + 25, 16, 11, sw=0.3, fill="#e4f2e1")
    sh.text(bx0 + 78, by0 + 29.6, "SHT41", size=1.5, anchor="middle", weight="bold")
    sh.text(bx0 + 78, by0 + 32.4, "room, vented", size=1.2, anchor="middle")
    wire(sh, [(bx0 + 59, by0 + 30.5), (bx0 + 70, by0 + 30.5)], c=GREEN, w=0.5)
    mtext(sh, 64, 86, "DO0 / DO1 are open-drain and sink to DO COM.\nDI0 is isolated and needs 5-36 V: the door "
          "contact\nswitches +12 V into it. All loads 12 V, <= 450 mA.\nCheck the polarity of each at "
          "commissioning (sheet 5).", size=1.5, c=THIN)

    # ---------------- screenshots
    shots = [("hmi_status.png", "Status"), ("hmi_sensors.png", "Sensors"), ("hmi_alarm.png", "Alarm"),
             ("hmi_settings.png", "Settings")]
    have = [s_ for s_ in shots if os.path.exists(os.path.join(ROOT, "renders", s_[0]))]
    for i, (f, lab) in enumerate(have):
        x = 166 + (i % 2) * 64
        y = 22 + (i // 2) * 44
        sh.rect(x, y, 60, 36, sw=0.5, fill="#0e1116")
        image(sh, x, y, 60, 36, os.path.join(ROOT, "renders", f))
        sh.text(x + 30, y + 39.4, lab + " screen", size=1.6, anchor="middle", c=THIN)
    if not have:
        sh.text(166, 40, "(run make_electronics.py --shots for the screen captures)", size=1.8, c=THIN)

    # ---------------- GX16, power budget (right)
    x0 = 300
    heading(sh, x0, 25, "W1 door bus, GX16-4", size=2.4)
    rows = [("1", "+12V", "red"), ("2", "0V", "black"), ("3", "A", "white / green"), ("4", "B", "green / white")]
    table(sh, x0, 28, [(8, "c"), (14, "l"), (30, "l")], rows, head=("Pin", "Signal", "Core"), size=1.7, rh=3.3)
    mtext(sh, x0 + 56, 31, "Shield: 0 V at the\nnode end only.\nThe plug sits on the\ncabinet side of the\n"
          "hinge loop: unplug\nit before lifting\nthe door off.", size=1.6, c=THIN)
    heading(sh, x0, 56, "Power budget", size=2.4)
    rows = [(a_, b_, "%d" % c_, "%d" % d_) for a_, b_, c_, d_ in POWER]
    table(sh, x0, 59, [(50, "l"), (26, "l"), (13, "r"), (13, "r")], rows, head=("Load", "Rail", "mA", "peak"),
          size=1.5, rh=3.0)
    ok, d, typ = check_power()
    mtext(sh, x0, 84.5, "%s.\nPlug pack 12 V 2 A, regulated, RCM approved." % d.replace("; typical", ";\ntypical"),
          size=1.5, c=THIN)

    # ---------------- harness schedule (full width)
    heading(sh, 12, 118, "HARNESS SCHEDULE  (bom/electronics_harness.csv; routes on sheet 4)", size=2.4)
    rows = []
    for w, a_, b_, c_, L, route in HARNESS:
        lines = wrap(route, 150)
        rows.append((w, a_, b_, c_, "%.1f" % L, lines[0]))
        for extra in lines[1:]:
            rows.append(("", "", "", "", "", extra))
    yb = table(sh, 12, 121, [(9, "l"), (28, "l"), (42, "l"), (42, "l"), (9, "r"), (268, "l")], rows,
               head=("W", "From", "To", "Cable", "m", "Route"), size=1.5, rh=2.9)

    # ---------------- modbus map (bottom)
    y0 = yb + 7
    heading(sh, 12, y0, "MODBUS MAP  node = server 1, holding registers, 19 200 8N1; -32768 = no reading",
            size=2.4)
    half = (len(MODBUS) + 1) // 2
    for c_, chunk in enumerate((MODBUS[:half], MODBUS[half:])):
        rows = [("0x%02X" % a_, n, t, s_, rw) for a_, n, t, s_, rw in chunk]
        table(sh, 12 + c_ * 128, y0 + 3, [(11, "l"), (54, "l"), (10, "l"), (34, "l"), (12, "c")], rows,
              head=("Reg", "Name", "Type", "Scale", "R/W"), size=1.45, rh=2.7)
    yf = y0 + 3 + 2.7 * (half + 1) + 3.6
    sh.text(12, yf, "Flags 0x0F: " + ", ".join("b%d %s" % (i, f) for i, f in enumerate(FLAGS[:5])) + ",",
            size=1.45)
    sh.text(12, yf + 2.6, "          " + ", ".join("b%d %s" % (i + 5, f) for i, f in enumerate(FLAGS[5:])) + ".",
            size=1.45)

    # ---------------- Home Assistant entities (bottom right)
    xh = 276
    heading(sh, xh, y0, "HOME ASSISTANT  (from the screen, sra16-hmi)", size=2.4)
    rows = []
    for kind, what in HA_ENTITIES:
        lines = wrap(what, 62)
        rows.append((kind, lines[0]))
        for extra in lines[1:]:
            rows.append(("", extra))
    table(sh, xh, y0 + 3, [(20, "l"), (114, "l")], rows, size=1.45, rh=2.7)
    title_block(sh, 3, "Touchscreen pod wiring, harness, Modbus map")
    return sh


# ======================================================================= sheet 4 - placement
def spot(sid):
    return [x for x in SPOTS if x[0] == sid][0]


def zone_col(sid):
    return RED if sid in ("T4", "T5", "T6") else (BLUE if sid in ("T1", "T2", "T3", "RH", "DU") else AMBER)


def marker(sh, cx, cy, sid, col):
    sh.circle(cx, cy, 1.6, sw=0.3, fill="#ffffff", c=col)
    sh.text(cx, cy + 0.55, sid, size=1.1 if len(sid) <= 2 else 0.9, anchor="middle", weight="bold", c=col)


def sheet4():
    sh = new_sheet(4, "Placement in the rack, cable routes")
    D = RL.derive(RL.resolve())
    pd = SMP.SM["pod"]
    k = 0.125                                   # 1:8
    hp = PP_hood_port()
    # ---------------- front elevation (doors off): x right, z up
    fx, fz = 20.0, 262.0

    def F(x, z):
        return fx + x * k, fz - z * k
    W, H = D["ext_w"], D["ext_h"]
    sh.rect(*F(0, H), W * k, H * k, sw=0.5, fill="#ffffff")
    x0, x1 = D["x_in0"], D["x_in1"]
    a, b = F(x0, D["z_shelf_foam0"])
    sh.rect(a, b, (x1 - x0) * k, (D["z_shelf_foam0"] - D["z_floor1"]) * k, sw=0.2, fill=BAY_FILL)
    a, b = F(x0, D["z_toprail0"])
    sh.rect(a, b, (x1 - x0) * k, (D["z_toprail0"] - D["z_shelf1"]) * k, sw=0.2, fill=COLD_FILL)
    a, b = F(x0, D["z_shelf1"])
    sh.rect(a, b, (x1 - x0) * k, (D["z_shelf1"] - D["z_shelf_foam0"]) * k, sw=0.2, fill="#c9b48a")
    a, b = F(D["x_ac0"], D["z_ac1"])
    sh.rect(a, b, (D["x_ac1"] - D["x_ac0"]) * k, (D["z_ac1"] - D["z_ac0"]) * k, sw=0.35, fill="#eceff3")
    sh.text(*F(311, 480), "AC", size=2.6, anchor="middle", weight="bold", c=THIN)
    a, b = F(D["win_xc"] - 45, D["win_zc"] + 30)
    sh.rect(a, b, 90 * k, 60 * k, sw=0.2, fill="#ffffff")
    sh.text(*F(D["win_xc"], D["win_zc"] - 4), "display", size=1.3, anchor="middle", c=THIN)
    a, b = F(54.2, 1087)
    sh.rect(a, b, (568.2 - 54.2) * k, (1087 - 1012) * k, sw=0.3, fill="#dbe9f7")
    sh.text(*F(330, 1042), "cold hood P1", size=1.4, anchor="middle", c=BLUE)
    for xs0, xs1 in ((x0, D["x_rail_out_l"]), (D["x_rail_out_r"], x1)):
        a, b = F(xs0, D["z_toprail0"])
        sh.rect(a, b, (xs1 - xs0) * k, (D["z_toprail0"] - D["z_shelf1"]) * k, sw=0.25, fill="#c3cad2")
    for xs0, xs1 in ((D["x_rail_out_l"], D["x_rail_in_l"]), (D["x_rail_in_r"], D["x_rail_out_r"])):
        a, b = F(xs0, D["rail_z1"])
        sh.rect(a, b, (xs1 - xs0) * k, (D["rail_z1"] - D["rail_z0"]) * k, sw=0.2, fill="#9aa4ae")
    for i in range(D["ru_count"] + 1):
        zz = D["z_rack0"] + i * D["ru_pitch"]
        sh.line(*F(D["x_rail_in_l"], zz), *F(D["x_rail_in_r"], zz), w=0.08, c="#b9c1c9")
    sh.text(*F(420, 1300), "16 RU", size=2.2, anchor="middle", c=THIN)
    a, b = F(36.5, 1264)
    sh.rect(a, b, 28.5 * k, 98 * k, sw=0.35, fill="#f6e7c8")
    a, b = F(pd["xc"] - pd["w"] / 2, pd["zc"] + pd["h"] / 2)
    sh.rect(a, b, pd["w"] * k, pd["h"] * k, sw=0.35, fill="none", c=BLUE, dash="1.2 0.7", rx=1)
    sh.text(*F(pd["xc"] - pd["w"] / 2 + 4, pd["zc"] + pd["h"] / 2 + 20), "pod P6 (on the door)", size=1.4, c=BLUE)
    for pts, col, dash in (
            ([(52, 1250), (52, 1450), (105, pd["zc"] - 22)], BLUE, None),
            ([(48, 1166), (48, 1100), (60, hp[2] + 10), (hp[0], hp[2])], AMBER, None),
            ([(hp[0], hp[2]), (44, hp[2] - 20), (44, 160), (52, 140)], AMBER, None),
            ([(hp[0], hp[2]), (46, 1000), (60, 900), (250, 850), (300, 832)], AMBER, "1 0.6"),
            ([(hp[0], hp[2]), (90, 1005)], AMBER, None)):
        sh.poly([F(*p_) for p_ in pts], w=0.45, c=col, dash=dash)
    for sid in ("T1", "T2", "T3", "RH", "DU", "DL", "IR", "LK"):
        _, _, x, y, z, _ = spot(sid)
        marker(sh, *F(x, z), sid, zone_col(sid))
    cx, cy = F(hp[0], hp[2])
    sh.circle(cx, cy, 1.0, sw=0.4, fill=AMBER, c=AMBER)
    sh.text(cx + 2.0, cy + 3.6, "HP", size=1.5, weight="bold", c=AMBER)
    cx, cy = F(50, 1215)
    sh.text(cx + 3.6, cy + 0.6, "NB", size=1.5, weight="bold")
    cx, cy = F(40, 1450)
    sh.text(cx - 1.5, cy + 0.6, "HL", size=1.5, anchor="end", weight="bold", c=BLUE)
    sh.text(fx + W * k / 2, fz + 5, "FRONT, doors off  1:8", size=2.2, anchor="middle", weight="bold")

    # ---------------- left section: y right (front at left), z up
    sx, sz = 112.0, 262.0

    def S(y, z):
        return sx + y * k, sz - z * k
    Dd = D["ext_d"]
    sh.rect(*S(0, H), Dd * k, H * k, sw=0.5, fill="#ffffff")
    y0, y1 = D["y_in0"], D["y_in1"]
    a, b = S(y0, D["z_shelf_foam0"])
    sh.rect(a, b, (y1 - y0) * k, (D["z_shelf_foam0"] - D["z_floor1"]) * k, sw=0.2, fill=BAY_FILL)
    for ya, yb_, fill in ((y0, D["y_frail"], COLD_FILL), (D["y_frail"] + 30, D["y_rrail"] - 30, "#f1f2f4"),
                          (D["y_rrail"], y1, HOT_FILL)):
        a, b = S(ya, D["z_toprail0"])
        sh.rect(a, b, (yb_ - ya) * k, (D["z_toprail0"] - D["z_shelf1"]) * k, sw=0.2, fill=fill)
    sh.text(*S(515, 1480), "IT", size=2.6, anchor="middle", weight="bold", c=THIN)
    for ya, yb_ in ((y0, 54.2), (159.2, 874.2), (1016.2, y1)):
        a, b = S(ya, D["z_shelf1"])
        sh.rect(a, b, (yb_ - ya) * k, (D["z_shelf1"] - D["z_shelf_foam0"]) * k, sw=0.2, fill="#c9b48a")
    for ya in (D["y_frail"], D["y_rrail"] - 30):
        a, b = S(ya, D["z_toprail0"])
        sh.rect(a, b, 30 * k, (D["z_toprail0"] - D["z_shelf1"]) * k, sw=0.25, fill="#c3cad2")
    # exhaust behind the AC first, so the AC hides the part inside its rear notch
    ex_y, ez0, ez1 = D["exh_y"], D["exh_z0"], D["exh_run_z"]
    sh.poly([S(ex_y, ez0), S(ex_y, ez1 - 60), S(ex_y + 60, ez1), S(y1, ez1)], w=170 * k, c="#f3cdbf")
    sh.text(*S(760, ez1 - 3), "exhaust duct", size=1.4, anchor="middle", c=RED)
    a, b = S(D["y_ac0"], D["z_ac1"])
    sh.rect(a, b, (D["y_ac1"] - D["y_ac0"]) * k, (D["z_ac1"] - D["z_ac0"]) * k, sw=0.35, fill="#eceff3")
    sh.text(*S(238, 480), "AC", size=2.6, anchor="middle", weight="bold", c=THIN)
    a, b = S(39.2, 1087)
    sh.rect(a, b, (264.2 - 39.2) * k, 75 * k, sw=0.3, fill="#dbe9f7")
    a, b = S(D["y_dock"], D["z_split"])
    sh.rect(a, b, (y1 - D["y_dock"]) * k, 12 * k, sw=0.2, fill="#c9b48a")
    sh.text(*S(760, D["z_split"] - 40), "partition", size=1.4, anchor="middle", c=THIN)
    sh.text(*S(760, 300), "condenser intake (room air)", size=1.4, anchor="middle", c=THIN)
    sh.text(*S(650, 950), "return air to the AC", size=1.4, anchor="middle", c=RED)
    a, b = S(D["y_dock"], 525)
    sh.rect(a, b, 20 * k, 380 * k, sw=0.2, fill="#d7dbe0")
    for (za, zb_) in (D["door_lo_z"], D["door_up_z"]):
        a, b = S(-4, zb_)
        sh.rect(a, b, 4 * k, (zb_ - za) * k, sw=0.2, fill="#aeb6bf")
    a, b = S(-36, pd["zc"] + pd["h"] / 2)
    sh.rect(a, b, 32 * k, pd["h"] * k, sw=0.35, fill="#dbe7f5", c=BLUE)
    a, b = S(86, 1264)
    sh.rect(a, b, 78 * k, 98 * k, sw=0.35, fill="#f6e7c8")
    hp_s = (hp[1], hp[2])
    for pts, col, dash in (
            ([(10, pd["zc"] - 22), (35, 1440), (60, 1420), (86, 1245)], BLUE, None),
            ([(100, 1166), (90, 1100), hp_s], AMBER, None),
            ([hp_s, (300, 1052), (900, 1052), (900, 1110), (880, 1130), (880, 1790)], RED, None),
            ([(470, 1052), (520, 760), (455, 700)], RED, None),
            ([hp_s, (62, 950), (59, 832)], AMBER, "1 0.6"), ([hp_s, (48, 400), (90, 140)], AMBER, None),
            ([hp_s, (50, 1004)], AMBER, None)):
        sh.poly([S(*p_) for p_ in pts], w=0.45, c=col, dash=dash)
    for sid in ("T1", "T2", "T3", "RH", "T4", "T5", "T6", "LK", "DL", "DU", "IR"):
        _, _, x, y, z, _ = spot(sid)
        marker(sh, *S(y, z), sid, zone_col(sid))
    cx, cy = S(*hp_s)
    sh.circle(cx, cy, 1.0, sw=0.4, fill=AMBER, c=AMBER)
    sh.text(cx + 2.0, cy + 3.6, "HP", size=1.5, weight="bold", c=AMBER)
    cx, cy = S(35, 1440)
    sh.text(cx - 0.8, cy - 2.2, "HL", size=1.5, anchor="end", weight="bold", c=BLUE)
    sh.text(*S(125, 1208), "NB", size=1.5, anchor="middle", weight="bold")
    sh.text(sx + Dd * k / 2, sz + 5, "LEFT SECTION, looking at the left wall  1:8", size=2.2, anchor="middle",
            weight="bold")

    # ---------------- table + notes (right)
    tx = 262
    heading(sh, tx, 25, "WHERE EVERYTHING GOES", size=2.4)
    rows = [(sid, what, "%d / %d / %d" % (x, y, z), how) for sid, what, x, y, z, how in SPOTS]
    yb = table(sh, tx, 28, [(9, "l"), (25, "l"), (22, "l"), (92, "l")], rows, head=("Id", "What", "x / y / z", "How"),
               size=1.45, rh=2.8)
    yb = paragraph(sh, tx, yb + 4, [
        "x from the left skin, y back from the front, z up from the floor (rack_layout v%s)." % RL.VERSION,
        "Cold side (blue): front plenum. Hot side (red): rear plenum and the bay above the partition,",
        "which carries the return air down to the AC. Everything that crosses from the front plenum",
        "to the bay goes through the hood port HP; no other holes are needed. Keep probe leads",
        "50 mm from mains cords, tied but not tensioned, and out of the condenser intake."],
        size=1.55, lh=2.6)
    for i, (col, lab) in enumerate(((BLUE, "W1 door bus; cold-side leads"),
                                    (AMBER, "W4 IR, W5 leak, W6 lower door, via HP"),
                                    (RED, "W2 rear harness: T6, T5, T4, UPS, mains"))):
        yy = yb + 2 + i * 3.2
        sh.line(tx, yy, tx + 8, yy, w=0.6, c=col, dash="1 0.6" if False else None)
        sh.text(tx + 10, yy + 0.6, lab, size=1.55)
    yd = yb + 14

    # ---------------- detail A: hood port (P1-1 left end, seen from the left), 1:4
    import printparts as PP
    ka = 0.25
    ax0, ay0 = tx, yd + 6
    heading(sh, ax0, yd + 2, "A  HOOD PORT  1:4", size=2.1)
    hb = (39.2, 1012.0, 264.2, 1087.0)                     # y0 z0 y1 z1 of the hood box
    pw = PP.EL["hood_port"]
    sh.rect(ax0, ay0, (hb[2] - hb[0]) * ka, (hb[3] - hb[1]) * ka, sw=0.35, fill="#dbe9f7")
    pcx, pcy = ax0 + pw[0] * ka, ay0 + pw[1] * ka
    sh.circle(pcx, pcy, pw[3] / 2 * ka, sw=0.2, dash="0.8 0.5")
    sh.circle(pcx, pcy, pw[2] / 2 * ka, sw=0.35, fill="#ffffff")
    WP.hdim(sh, ax0, pcx, ay0 + (hb[3] - hb[1]) * ka, ay0 + (hb[3] - hb[1]) * ka + 4.0, "%g" % pw[0], size=1.5,
            above=False)
    WP.vdim(sh, ay0, pcy, ax0 + (hb[2] - hb[0]) * ka, ax0 + (hb[2] - hb[0]) * ka + 4.0, "%g" % pw[1], size=1.5)
    mtext(sh, ax0, ay0 + (hb[3] - hb[1]) * ka + 9.5, "D%g through, wall thinned to %g mm over D%g\n"
          "inside; %g mm membrane grommet - pierce\none hole per cable. Front face on the left." % (
              pw[2], pw[4], pw[3], pw[2]), size=1.45, c=THIN)

    # ---------------- detail C: probe clip (P8-1 on steel), 2:1
    kc = 2.0
    cx0, cy0 = tx + 74, yd + 8
    heading(sh, tx + 70, yd + 2, "C  PROBE CLIP P8-1  2:1", size=2.1)
    sh.rect(cx0, cy0 + 22 * kc, 30 * kc, 2.5, sw=0.2, fill="url(#hatch)")
    sh.text(cx0 + 30 * kc + 1.0, cy0 + 22 * kc + 2.0, "steel", size=1.4, c=THIN)
    bxl = cx0 + 8 * kc
    sh.rect(bxl, cy0, 14 * kc, 22 * kc, sw=0.35, fill="#f6e7c8")
    sh.rect(bxl + 7 * kc - 5.15 * kc, cy0 + 22 * kc - 3.2 * kc, 10.3 * kc, 3.2 * kc, sw=0.25, fill="#8f99a3")
    pcx, pcy = bxl + 7 * kc, cy0 + 6 * kc
    sh.rect(pcx - 0.36 * 6.3 * kc, cy0 - 0.5, 0.72 * 6.3 * kc, 6 * kc + 0.5, sw=0.0, fill="#ffffff", c="none")
    sh.circle(pcx, pcy, 6.3 / 2 * kc, sw=0.3, fill="#ffffff")
    sh.circle(pcx, pcy, 3.0 * kc, sw=0.25, fill="#c3cad2")
    WP.vdim(sh, pcy, cy0 + 22 * kc, bxl + 14 * kc, bxl + 14 * kc + 4.5, "16", size=1.5)
    mtext(sh, cx0, cy0 + 22 * kc + 6.5, "6 mm probe snaps in from the top;\n10 x 3 magnet glued in the base.",
          size=1.45, c=THIN)

    # ---------------- detail B: hinge loop, plan of the upper door's hinge corner, 1:6
    kb = 1.0 / 6.0
    yb0 = yd + 66
    heading(sh, tx, yb0, "B  HINGE LOOP, PLAN AT z 1450  1:6", size=2.1)
    ox_, oy_ = tx + 14, yb0 + 32                           # cabinet front-left corner on paper

    def Bp(x, y):
        return ox_ + x * kb, oy_ + y * kb
    hx, hy = -6.0, -6.0
    sh.poly([Bp(0, 110), Bp(0, 0)], w=0.6)                                     # left skin
    sh.rect(*Bp(4.2, 4.2), 30 * kb, 30 * kb, sw=0.3, fill="#c3cad2")             # frame post
    sh.rect(*Bp(4.2, 34.2), 30 * kb, 75 * kb, sw=0.2, fill="#efe6cf")            # side lining
    sh.rect(*Bp(-2, -6), 252 * kb, 4.8 * kb, sw=0.3, fill="#aeb6bf")             # door skin, closed
    sh.rect(*Bp(36.2, -1.2), 214 * kb, 35.4 * kb, sw=0.2, fill="#efe6cf")       # door lining
    sh.text(*Bp(205, 20), "door, closed", size=1.3, anchor="middle", c=THIN)
    sh.circle(*Bp(hx, hy), 0.9, sw=0.3, fill="#ffffff")
    sh.text(*Bp(hx - 5, hy + 3), "hinge", size=1.3, anchor="end", c=THIN)
    sh.rect(*Bp(hx, hy - 135), 40.2 * kb, 135 * kb, sw=0.25, fill="none", dash="1 0.6")   # door open 90
    sh.text(*Bp(hx - 4, hy - 100), "door open 90", size=1.3, anchor="end", c=THIN)
    g_closed, g_open = Bp(105, 34.2), Bp(hx + 40.2, hy - 111)
    anchor = Bp(34.2, 80)
    sh.path("M %.2f %.2f C %.2f %.2f %.2f %.2f %.2f %.2f" % (
        g_closed[0], g_closed[1], g_closed[0], g_closed[1] + 16, anchor[0] + 12, anchor[1] + 6,
        anchor[0] + 0.5, anchor[1]), w=0.5, c=BLUE)
    sh.path("M %.2f %.2f C %.2f %.2f %.2f %.2f %.2f %.2f" % (
        g_open[0], g_open[1], g_open[0] + 8, g_open[1] + 6, anchor[0] + 10, anchor[1] - 14,
        anchor[0] + 0.5, anchor[1]), w=0.35, c=BLUE, )
    sh.circle(*g_closed, 0.8, sw=0.0, fill=BLUE, c=BLUE)
    sh.circle(*g_open, 0.6, sw=0.0, fill=BLUE, c=BLUE)
    sh.rect(anchor[0] - 0.2, anchor[1] - 1.5, 3.0, 3.0, sw=0.3, fill="#fbf3e2")
    sh.text(anchor[0] + 16.0, anchor[1] + 1.0, "GX16 on a tie mount", size=1.3)
    sh.line(anchor[0] + 3.0, anchor[1], anchor[0] + 15.4, anchor[1] + 0.6, w=0.15, c=THIN)
    sh.text(g_closed[0] + 1.8, g_closed[1] + 3.4, "door grommet", size=1.3)
    mtext(sh, tx + 66, yb0 + 8, "300 mm of W1 in 10 mm spiral wrap runs\nfrom the door grommet to a tie mount on\n"
          "the side lining, inside the seal line and\nhalf way between the hinges. Open the\ndoor fully before "
          "tying off: no tension\nwhen open, nothing pinched when shut.\nThin line: the cable with the door open.",
          size=1.45, c=THIN)
    title_block(sh, 4, "Placement in the rack, cable routes", "1:8 views, details as noted")
    return sh


def PP_hood_port():
    """Hood cable port centre in layout coordinates (x at the outer face of the left end wall)."""
    import printparts as PP
    hb = PP.interfaces()["hood_box"]
    py, pz = PP.EL["hood_port"][:2]
    return (hb[0], hb[1] + py, hb[5] - pz)


# ======================================================================= sheet 5 - control + commissioning
COMMISSION = [
    "Bench: power the carrier from 12 V with U1 out: +5 V, +12 V on J2. Fit U1: +3V3.",
    "Flash both boards over USB-C (esphome run ...); 'Rack link' turns green.",
    "Probes: the node log lists every DS18B20 per bus at boot. Warm one at a time in",
    "your hand, put each address in sra16-node.yaml, re-flash.",
    "AC protocol: point the AC remote at the node box lid: the log says 'Received",
    "Coolix' (keep coolix) or 'Midea' (set midea_ir). Re-flash.",
    "Press 'Re-send to AC' on the Alarms screen: the AC must go to cool at the setpoint",
    "shown. Try OFF and back to AUTO. Stick the emitter where this always works.",
    "Doors and float: open / lift each; its dot turns amber. Backwards? add",
    "'inverted: true' to that input.",
    "Unplug a probe lead: 'probe missing', 3 beeps a minute, AC kept on.",
    "Shutdown: set the limit to 28, warm T1 and T2: K1 closes 120 s later. Only",
    "then wire J3 to the UPS / server input. Reset with 'Reset alarms'.",
    "Leave it a day: the cold-side average should sit at the target.",
]


def state_diagram(sh, x0, y0):
    """States of the node's supervisor; the exception states hang off an 'any state' bus."""
    bw, bh = 34.0, 9.0
    col = {"Starting": BLUE, "Cooling": BLUE, "Idle": BLUE, "On": BLUE, "Eco off": GREEN, "Off": GREY,
           "No AC power": AMBER, "Not cooling": AMBER, "CRITICAL": RED}
    c1, c2, c3 = x0 + 22, x0 + 74, x0 + 126
    r1, r2, r3 = y0 + 8, y0 + 30, y0 + 56
    pos = {"Starting": (c1, r1), "Cooling": (c2, r1), "Idle": (c3, r1), "Eco off": (c2, r2), "On": (c3, r2)}
    b3 = 32.0
    xs = [x0 + 5 + b3 / 2 + i * (b3 + 3) for i in range(4)]
    for nm, x in zip(("Off", "No AC power", "Not cooling", "CRITICAL"), xs):
        pos[nm] = (x, r3)
    for nm, (x, y) in pos.items():
        w_ = b3 if y == r3 else bw
        sh.rect(x - w_ / 2, y - bh / 2, w_, bh, sw=0.45, fill="#ffffff", c=col[nm], rx=2)
        sh.text(x, y + 0.8, nm, size=2.0, anchor="middle", weight="bold", c=col[nm])
    e = bw / 2
    sh.arrow(c1 + e, r1, c2 - e, r1, w=0.3)
    sh.text((c1 + c2) / 2, r1 - 1.4, "coil cold", size=1.4, anchor="middle", c=THIN)
    sh.arrow(c2 + e, r1 - 1.3, c3 - e, r1 - 1.3, w=0.3)
    sh.arrow(c3 - e, r1 + 1.3, c2 + e, r1 + 1.3, w=0.3)
    sh.text((c2 + c3) / 2, r1 + 4.8, "AC thermostat", size=1.4, anchor="middle", c=THIN)
    sh.arrow(c2 - 5, r1 + bh / 2, c2 - 5, r2 - bh / 2, w=0.3)
    sh.text(c2 - 6.5, (r1 + r2) / 2 + 0.5, "low load, pulled down", size=1.4, anchor="end", c=THIN)
    sh.poly([(c2 - e, r2), (c1, r2), (c1, r1 + bh / 2 + 0.4)], w=0.3)
    sh.arrow(c1, r2 - 3, c1, r1 + bh / 2, w=0.3)
    sh.text(c1 + 2, r2 - 1.2, "warm again: back on", size=1.4, c=THIN)
    sh.text(c3, r2 + bh / 2 + 2.6, "when supply / exhaust probes are missing", size=1.3, anchor="middle", c=THIN)
    yb = r3 - bh / 2 - 6.5
    sh.line(xs[0] - b3 / 2 + 1, yb, xs[-1] + b3 / 2 - 1, yb, w=0.35)
    sh.text(xs[0] - b3 / 2 + 1, yb - 1.4, "from any state:", size=1.5, weight="bold")
    for x, lab in zip(xs, ("mode OFF", "AC socket dead", "3 re-sends failed", "intake >= limit")):
        sh.arrow(x, yb, x, r3 - bh / 2, w=0.3)
        sh.text(x + 1.4, yb + 3.6, lab, size=1.35, c=THIN)
    sh.text(x0 + 5, r3 + bh / 2 + 3.4, "Each returns through Starting once its cause has cleared; the AC's 3-minute restart "
            "delay is respected.", size=1.45, c=THIN)
    return r3 + bh / 2 + 6


def sheet5(rep):
    sh = new_sheet(5, "Control logic, alarms, commissioning")
    # ---------------- left: states and alarms
    heading(sh, 14, 25, "STATES  (rack node, decided every 5 s)", size=2.4)
    yb = state_diagram(sh, 12, 27)
    yb = table(sh, 14, yb, [(22, "l"), (122, "l")], STATES, head=("State", "Meaning"), size=1.55, rh=2.85)
    yb = paragraph(sh, 14, yb + 4, [
        "Normal load: AC on; its setpoint (whole degrees) is trimmed so that the 10-minute average intake",
        "meets the target - the AC's own thermostat cycles the compressor. Low load (the servers warm the",
        "air by less than 4 K): eco pulls the rack down to target - 2, switches the AC off and back on at",
        "target + 2 or a hot side of 32. Unknown readings or over-temperature always mean AC on."],
        size=1.6, lh=2.65)
    heading(sh, 14, yb + 5, "ALARMS  (register 0x0E: bit)", size=2.4)
    table(sh, 14, yb + 8, [(7, "c"), (28, "l"), (62, "l"), (47, "l")], ALARMS, head=("Bit", "Alarm", "When", "Action"),
          size=1.5, rh=2.8)

    # ---------------- middle: settings, simulation, commissioning
    mx = 166
    heading(sh, mx, 25, "SETTINGS  (defaults; screen or Home Assistant)", size=2.4)
    yb = table(sh, mx, 28, [(30, "l"), (32, "l"), (66, "l")], SETTINGS, head=("Setting", "Default", "Notes"),
               size=1.5, rh=2.8)
    heading(sh, mx, yb + 6, "SIMULATION  (the real control core in a thermal model)", size=2.4)
    rows, last = [], None
    for c in rep["checks"]:
        sc = ""
        if c["scenario"] != last:
            sc = re.split(r"[,(]", c["scenario"])[0].strip()
            paren = c["scenario"].rsplit("(", 1)[1].rstrip(")") if "(" in c["scenario"] else ""
            if paren and len(paren) <= 20:
                sc += " (%s)" % paren
        rows.append((sc, c["check"], "OK" if c["ok"] else "FAIL", c["detail"]))
        last = c["scenario"]
    yb = table(sh, mx, yb + 9, [(34, "l"), (50, "l"), (7, "c"), (37, "l")], rows,
               head=("Scenario", "Check", "", "Result"), size=1.4, rh=2.6)
    heading(sh, mx, yb + 6, "COMMISSIONING", size=2.4)
    n = 0
    for i, t in enumerate(COMMISSION):
        first = not t[0].islower() and not t.startswith(("your", "Coolix", "shown", "'inverted", "then"))
        if first:
            n += 1
        sh.text(mx, yb + 9.5 + i * 2.7, ("%d  " % n if first else "    ") + t, size=1.5)

    # ---------------- right: simulation plot
    img = os.path.join(ROOT, "renders", "controls_sim.png")
    rx = 300
    heading(sh, rx, 25, "SIMULATED DAYS  (renders/controls_sim.png)", size=2.2)
    if os.path.exists(img):
        w = 106.0
        h = w * 1620.0 / 1300.0
        sh.rect(rx, 28, w, h, sw=0.3, fill="#ffffff")
        image(sh, rx, 28, w, h, img)
        mtext(sh, rx, 28 + h + 4, "Lines: hot side (red), cold side (blue), AC supply and return.\n"
              "Blue band: compressor running; grey: AC off; triangles: IR\nframes sent; red: alarms. "
              "tools/sim_controller.py compiles\nsra_control.h for the PC and runs it against a lumped model "
              "of\nthe rack and the AC - thermostat and restart delay included.", size=1.5, c=THIN)
    title_block(sh, 5, "Control logic, alarms, simulation, commissioning")
    return sh


# ======================================================================= screenshots (SDL preview)
SHOTS = [(0, "hmi_status"), (1, "hmi_sensors"), (3, "hmi_settings"), (4, "hmi_eco"),
         (8, "hmi_alarm"), (10, "hmi_alarms")]


def capture_shots(esphome):
    prev = os.path.join(FW, "preview")
    r = subprocess.run([esphome, "compile", "sra16-hmi-preview.yaml"], cwd=prev, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError("preview build failed:\n" + r.stdout[-1500:] + r.stderr[-800:])
    prog = os.path.join(prev, ".esphome", "build", "sra16-hmi-preview", ".pioenvs", "sra16-hmi-preview", "program")
    from PIL import ImageGrab
    disp = ":97"
    xv = subprocess.Popen(["Xvfb", disp, "-screen", "0", "800x480x24", "-nolisten", "tcp"],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.5)
    p = subprocess.Popen([prog], env=dict(os.environ, DISPLAY=disp), stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
    t0, out = time.time(), []
    try:
        want = dict(SHOTS)
        for k in range(max(want) + 1):          # the preview steps scene/tab every 4 s
            time.sleep(max(0.0, t0 + 4 * k + 3.2 - time.time()))
            if k in want:
                fn = os.path.join(ROOT, "renders", want[k] + ".png")
                ImageGrab.grab(xdisplay=disp).save(fn)
                out.append(fn)
    finally:
        p.terminate()
        xv.terminate()
    return out


# ======================================================================= CSVs, docs
def write_csvs():
    kit = [r for r in KIT]
    with open(os.path.join(ROOT, "bom", "electronics.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["group", "ref", "item", "spec", "qty", "unit_AUD_indicative", "line_AUD", "optional"])
        for g, ref, item, spec, q, u, opt in kit:
            w.writerow([g, ref, item, spec, q, u, round(q * u, 2), "yes" if opt else ""])
        base = sum(q * u for *_, q, u, o in kit if not o)
        opt = sum(q * u for *_, q, u, o in kit if o)
        w.writerow(["TOTAL", "", "kit (excl. options)", "", "", "", round(base, 2), ""])
        w.writerow(["TOTAL", "", "options", "", "", "", round(opt, 2), "yes"])
    with open(os.path.join(ROOT, "bom", "electronics_harness.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["cable", "from", "to", "type", "length_m", "route"])
        w.writerows(HARNESS)
    return base, opt


def md_table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "|".join("---" for _ in head) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    return out


def write_md(tot, rep, checks, files):
    L = ["# SRA-16 - control electronics (%s)" % DOC_NO, "",
         "| | |", "|---|---|",
         "| Drawing | %s, %d sheets (`drawings/%s.pdf`) |" % (DOC_NO, N_SHEETS, DOC_NO),
         "| Generated | `tools/make_electronics.py` on %s, layout v%s |" % (TODAY, RL.VERSION),
         "| Firmware | `firmware/sra16-node.yaml` (rack node), `firmware/sra16-hmi.yaml` (touchscreen), ESPHome 2026.6 |",
         "| Kit cost | about AUD %.0f (+ AUD %.0f options), indicative - `bom/electronics.csv` |" % (tot["kit"], tot["opt"]),
         "| Power | 12 V, about %.1f W typical, from a plug pack on the UPS-backed PDU |" % tot["power_w"],
         "| Status | prototype; SELV only - nothing in the kit touches mains |", "",
         "## What it does", "",
         "A small ESP32 computer inside the rack (the **rack node**) reads temperature probes on the cold side "
         "(server intakes) and the hot side (server exhausts, the AC's return and exhaust air). Every 5 seconds it "
         "decides whether the AC should run, at what setpoint and fan speed, and sends that to the AC with the "
         "AC's own infrared remote codes - so the AC is never modified. A **4.3 inch touchscreen** on the upper "
         "door shows what is happening and lets you change the settings; it talks to the node over a 4-wire "
         "RS485 cable and is also the kit's link to Wi-Fi and Home Assistant.", "",
         "The node makes every decision itself: if the screen, the network or Home Assistant is down, the rack "
         "stays cooled. Anything it cannot see (a dead probe, an over-temperature) makes it turn the AC on.", ""]
    shots = [("hmi_status.png", "Status: cold side, hot side, AC state, quick controls"),
             ("hmi_eco.png", "Eco: light load, the AC is off and the rack coasts"),
             ("hmi_alarm.png", "Alarm: the AC is not cooling; the node re-sends and beeps"),
             ("hmi_sensors.png", "Sensors: every probe, humidity, dew point, IR count"),
             ("hmi_alarms.png", "Alarms: what is wrong and what to check; silence, reset, re-send to the AC"),
             ("hmi_settings.png", "Settings: AC fan, warning and shutdown limits, system")]
    for f, cap in shots:
        if os.path.exists(os.path.join(ROOT, "renders", f)):
            L += ["![%s](../renders/%s)" % (cap, f), "", "*%s*" % cap, ""]
    L += ["## Why an ESP32 rather than a Raspberry Pi 5", "",
          "Both were considered. For a controller sealed inside a rack the ESP32-S3 wins on every point that "
          "matters: it is running 1 second after power returns (a Pi takes 20-40 s and can corrupt its SD card in "
          "a power cut), it dissipates about 1 W instead of 5-10 W inside the sealed box, its RMT peripheral "
          "generates IR timing in hardware, it runs straight from 12 V, and ESPHome gives native Home Assistant "
          "integration. A Pi 5 remains a good Home Assistant host outside the rack.", "",
          "## Architecture", "",
          "- **Rack node** - ESP32-S3-DevKitC-1 on a 70 x 90 mm carrier board in the printed box P7, stuck by two "
          "magnets to the front face of the left front rail spacer, just above the shelf. Modbus server (address 1).",
          "- **Touchscreen** - Waveshare ESP32-S3-Touch-LCD-4.3B in the printed pod P6 on the upper door (outside "
          "the steel, so Wi-Fi works). Modbus client; also reads the room temperature, the upper door contact, "
          "drives the buzzer and an optional beacon output.",
          "- **Bus W1** - 4-core shielded cable: +12 V, 0 V, RS485 A/B at 19 200 baud, through a hinge loop with "
          "a GX16-4 plug so the lift-off door still lifts off.",
          "- **AC control** - a stick-on IR emitter over the AC's receiver, on a 3.5 mm socket in the bay so the "
          "AC still rolls out for its filters (unplug, roll, plug back).",
          "- **Shutdown** - relay K1 on the node gives a dry contact for a UPS or server input; Home Assistant "
          "sees the same request and can shut servers down over the network (NUT / ssh).", ""]
    L += ["## Kit parts", ""]
    rows = [(g, ref, item, spec, q, "%.2f" % u, "%.2f" % (q * u), "option" if o else "")
            for g, ref, item, spec, q, u, o in KIT]
    L += md_table(["Group", "Ref", "Item", "Spec", "Qty", "AUD each", "AUD", ""], rows)
    L += ["", "**Kit: about AUD %.0f**, options AUD %.0f. Indicative retail, Sept 2026 - the screws and magnets "
          "for P6/P7/P8 are in `docs/PRINTED_PARTS.md`." % (tot["kit"], tot["opt"]), ""]
    L += ["## Rack node carrier (sheet 2)", ""]
    L += md_table(["Pin", "Net", "Goes to", "Function"], [("GPIO%d" % g, n, w, f) for g, n, w, f, _ in GPIO])
    L += [""]
    L += md_table(["Conn", "Type", "Pins", "To"], [(r, t, " / ".join(p), u) for r, t, p, u in CONN])
    L += ["", "Build order: sockets for U1, then U3 and U2, then the terminal row. With U1 out, power J1 from "
          "12 V and check +5 V and the 12 V on J2; then fit U1 and check +3V3. Keep the 12 V wiring on the left "
          "half of the board and the 1-Wire/I2C lines short and away from K1. U1's GPIOs are 3.3 V only.", ""]
    L += md_table(["Ref", "Part", "Use"], CARRIER)
    L += ["", "## Touchscreen pod (sheet 3)", "",
          "- W1 lands on the panel's power and RS485 terminals (VIN 7-36 V, GND, A, B).",
          "- Upper door contact: +12 V through the reed switch into DI0, DI COM to 0 V (the isolated input "
          "needs 5-36 V).",
          "- Buzzer: +12 V to the buzzer, its other lead to DO0. Optional beacon the same way on DO1. DO COM to 0 V.",
          "- Room SHT41 on the panel's I2C connector, in the pod's vented corner.",
          "- USB-C for the first flash; after that, updates go over Wi-Fi.", ""]
    L += ["## Installation (sheet 4)", ""]
    L += md_table(["Id", "What", "x / y / z", "How"], [(s, w, "%d / %d / %d" % (x, y, z), h)
                                                       for s, w, x, y, z, h in SPOTS])
    L += ["", "Coordinates in mm: x from the left skin, y back from the front, z up from the floor.", ""]
    L += md_table(["Cable", "From", "To", "Type", "m", "Route"], [(a, b, c, d, "%.1f" % e, f)
                                                                  for a, b, c, d, e, f in HARNESS])
    L += ["", "Everything that goes from the front plenum into the bay passes through the hood port HP: the round "
          "hole in the left end of the printed cold hood (P1-1), fitted with a 25 mm membrane grommet - pierce "
          "one hole per cable so it stays sealed. From the bay, W2 reaches the rear plenum through the shelf's "
          "open return opening. No other holes are needed except the door's cable grommet (already in the DXF).",
          ""]
    L += ["## Firmware", "",
          "```sh",
          "pip install esphome==2026.6.5          # or the ESPHome add-on in Home Assistant",
          "cd hardware/silent-rack-ac/firmware",
          "cp secrets.example.yaml secrets.yaml  # Wi-Fi, API key, OTA password",
          "esphome run sra16-node.yaml           # USB-C on the DevKit the first time",
          "esphome run sra16-hmi.yaml            # USB-C on the panel the first time",
          "```", "",
          "- `components/sra_control/sra_control.h` is the control core: plain C++ with no ESPHome dependency. "
          "It is unit-tested on a PC (`firmware/test/`, %s) and driven by the thermal simulation." % tot["tests"],
          "- `hmi/ui.yaml` holds the four LVGL screens; `preview/sra16-hmi-preview.yaml` runs them on a PC "
          "(SDL) with demo data - the screenshots above come from it.",
          "- Both devices appear in Home Assistant with every probe, the state, the alarms and the settings.", "",
          "### Home Assistant: shut the servers down", "",
          "Relay K1 covers a UPS or server with a dry-contact input. For the rest, let Home Assistant act on the "
          "same request - for example a NUT primary that then shuts every NUT client down:", "",
          "```yaml",
          "automation:",
          "  - alias: SRA-16 rack too hot - shut the servers down",
          "    triggers:",
          "      - trigger: state",
          "        entity_id: binary_sensor.sra_16_rack_it_shutdown_request",
          "        to: \"on\"",
          "    actions:",
          "      - action: shell_command.sra16_it_shutdown",
          "shell_command:",
          "  sra16_it_shutdown: ssh -i /config/.ssh/sra16 admin@nut-primary sudo upsmon -c fsd",
          "```", "",
          "Test it with the shutdown limit temporarily lowered (commissioning step 8) before you rely on it.", ""]
    L += ["## Control logic (sheet 5)", ""]
    L += md_table(["State", "Meaning"], STATES)
    L += [""]
    L += md_table(["Setting", "Default", "Notes"], SETTINGS)
    L += [""]
    L += md_table(["Bit", "Alarm", "When", "Action"], ALARMS)
    L += ["", "## Modbus map (sheet 3)", "",
          "Node = server 1, holding registers, RS485 19 200 8N1. Temperatures are 0.1 degC signed; -32768 means "
          "no reading. Flags 0x0F: " + ", ".join("bit %d %s" % (i, f) for i, f in enumerate(FLAGS)) + ".", ""]
    L += md_table(["Reg", "Name", "Type", "Scale", "R/W"], [("0x%02X" % a, n, t, s, rw) for a, n, t, s, rw in MODBUS])
    L += ["", "## Commissioning", "",
          "1. On the bench, power the carrier from 12 V with U1 out: +5 V present, +12 V on J2. Fit U1: +3V3.",
          "2. Flash both boards (above). The screen shows 'Rack link' green once the bus works.",
          "3. **Probes.** At boot the node log lists every DS18B20 on each bus. Warm one probe at a time in your "
          "hand to identify it and put its address in `sra16-node.yaml` (`t_cold_top` ... `t_exhaust`).",
          "4. **AC protocol.** Point the AC's remote at the node box lid and press a button: the log says "
          "'Received Coolix' (keep `ac_protocol: coolix`) or 'Received Midea' (set `midea_ir`). Re-flash.",
          "5. **IR.** On the Alarms screen press 'Re-send to AC': the AC must switch to cool at the setpoint shown. "
          "Try mode OFF and back to AUTO. Stick the emitter where this works every time.",
          "6. **Inputs.** Open each door: its dot turns amber within a second. Lift the float: 'Water in tray' after 5 s. "
          "If one reads backwards, add `inverted: true` to that input in the YAML.",
          "7. **Alarms.** Unplug a probe lead: 'probe missing' shows and the AC is forced on.",
          "8. **Shutdown.** Temporarily set the shutdown limit to 28 and warm T1/T2: K1 closes 120 s later. "
          "Only then wire J3 to the UPS or server input; reset with 'Reset alarms'.",
          "9. Leave it running for a day and check that the cold-side average sits at the target.", ""]
    L += ["## Verification", ""]
    L += md_table(["Check", "Result", "Detail"], [(c, "OK" if ok else "**FAIL**", d) for c, ok, d in checks])
    L += ["", "Simulation (`tools/sim_controller.py`, plot `renders/controls_sim.png`):", ""]
    L += md_table(["Scenario", "Check", "", "Result"], [(c["scenario"], c["check"], "OK" if c["ok"] else "FAIL",
                                                        c["detail"]) for c in rep["checks"]])
    L += ["", "![Simulation](../renders/controls_sim.png)", ""]
    L += ["## Safety and limits", "",
          "- The kit is SELV: a 12 V plug pack (RCM approved) feeds everything. Nothing is wired to mains. The "
          "optional mains detect uses a second, approved USB charger plugged into the AC's socket.",
          "- Put the 12 V plug pack on the UPS-backed PDU so the node can still ask for a clean shutdown in a "
          "power cut. The AC stays on its own GPO.",
          "- K1 is a signal relay (1 A, 30 V DC): use it for UPS/server signal inputs only.",
          "- IR control is open loop; the node checks the result through the supply/exhaust probes and re-sends "
          "(3 times) before it alarms. It cannot fix an AC that has tripped or lost power: that is what the "
          "alarms and the shutdown request are for.",
          "- Not certified. A product would need EMC testing (RCM) of the assembled controller.", ""]
    L += ["## Productisation notes", "",
          "- Turn the carrier into a 2-layer PCB with the ESP32-S3 module, buck and RS485 on board (about AUD 15 "
          "a board in 100s); the terminal row and box stay.",
          "- The touchscreen and the firmware need no change for a product run; branding is in `hmi/ui.yaml`.",
          "- The same node firmware runs any rack size: only the probe addresses and the AC protocol change.", ""]
    L += ["## Files", ""] + ["- `%s`" % f for f in files] + [""]
    with open(os.path.join(ROOT, "docs", "ELECTRONICS.md"), "w") as fh:
        fh.write("\n".join(L))


# ======================================================================= main
def main(argv):
    do_pdf, do_sim, do_shots, esphome = True, True, False, os.environ.get("ESPHOME", "esphome")
    it = iter(argv)
    for a in it:
        if a == "--no-pdf":
            do_pdf = False
        elif a == "--no-sim":
            do_sim = False
        elif a == "--shots":
            do_shots = True
        elif a == "--esphome":
            esphome = next(it)
    checks = []
    ok, d = run_unit_tests()
    checks.append(("control-core unit tests (g++ -Wall -Wextra -Werror)", ok, d))
    m = re.search(r"(\d+) checks passed, (\d+) failed", d)
    tests = ("%s checks, all pass" % m.group(1)) if ok and m else "FAILED"
    if do_sim:
        ok, d, rep = run_sim()
    else:
        rep = json.load(open(os.path.join(FW, "test", "sim_report.json")))
        ok = all(c["ok"] for c in rep["checks"])
        d = "%d/%d scenario checks (previous run)" % (sum(c["ok"] for c in rep["checks"]), len(rep["checks"]))
    checks.append(("thermal simulation with the real control core", ok, d))
    checks.append(("node firmware GPIOs = carrier nets",) + check_pins())
    checks.append(("Modbus map: node = this table, screen uses a subset",) + check_modbus())
    checks.append(("carrier fits the node box P7",) + check_fit())
    ok, d, typ_w = check_power()
    checks.append(("power budget within the plug pack and the 5 V buck", ok, d))
    shots = []
    if do_shots:
        shots = capture_shots(esphome)
    base, opt = write_csvs()
    tot = {"kit": base, "opt": opt, "power_w": typ_w, "tests": tests, "sim": d if False else
           "%d/%d checks pass" % (sum(c["ok"] for c in rep["checks"]), len(rep["checks"]))}
    ddir = os.path.join(ROOT, "drawings")
    svgs = []
    for i, fn in enumerate((lambda: sheet1(tot), sheet2, sheet3, sheet4, lambda: sheet5(rep))):
        p = os.path.join(ddir, "%s_s%d.svg" % (DOC_NO, i + 1))
        with open(p, "w") as fh:
            fh.write(fn().svg())
        svgs.append(p)
    files = ["drawings/%s.pdf" % DOC_NO, "drawings/%s_s1..s%d.svg" % (DOC_NO, N_SHEETS), "bom/electronics.csv",
             "bom/electronics_harness.csv", "firmware/ (ESPHome YAML, control core, tests, preview)",
             "firmware/test/elc_report.json", "renders/controls_sim.png"] + \
            ["renders/%s.png" % n for _, n in SHOTS if os.path.exists(os.path.join(ROOT, "renders", n + ".png"))]
    if do_pdf:
        subprocess.run(["node", os.path.join(HERE, "render", "svg2pdf.mjs"), os.path.join(ddir, "%s.pdf" % DOC_NO)]
                       + svgs, check=True, capture_output=True)
    write_md(tot, rep, checks, files)
    with open(os.path.join(FW, "test", "elc_report.json"), "w") as fh:
        json.dump({"doc": DOC_NO, "rev": REV, "kit_aud": round(base, 2), "options_aud": round(opt, 2),
                   "power_w_typ": round(typ_w, 2),
                   "checks": [{"check": c, "ok": bool(o), "detail": d} for c, o, d in checks]}, fh, indent=1)
    for c, o, d in checks:
        print("  [%s] %s - %s" % ("ok" if o else "FAIL", c, d))
    print("electronics: kit AUD %.0f (+%.0f options), %d sheets%s" % (base, opt, len(svgs),
                                                                      ", %d screenshots" % len(shots) if shots else ""))
    return 0 if all(o for _, o, _ in checks) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
