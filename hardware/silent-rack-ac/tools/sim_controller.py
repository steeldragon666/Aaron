#!/usr/bin/env python3
"""
sim_controller.py - drives the real rack controller (firmware/components/sra_control/sra_control.h,
compiled for this PC and loaded through ctypes) with a lumped thermal model of the SRA-16 closed
air loop and the Dimplex AC, and checks how it behaves in the situations that matter.

Model (1 s steps):
  cold volume (hood + front plenum)  C_c dTc/dt = m (T_sup - Tc) + UA_c (T_room - Tc)
  hot volume (rear plenum + bay, IT) C_h dTh/dt = m (T_x - Th) + UA_h (T_room - Th)
  server exhaust                     T_x = Tc + Q_it / m
  AC supply                          T_sup = Th - (Q_ac - Q_fan) / m,  Q_ac = eps m (Th - T_evap)
  m = loop air flow (W/K): the AC fan when it runs, else the server fans.
  The AC has its own thermostat on its return air (Th) with hysteresis and a 3-minute restart
  delay, accepts IR frames only while powered, and comes back from a power cut in standby.

Usage:  python3 tools/sim_controller.py [--plot renders/controls_sim.png] [--json firmware/test/sim_report.json]
Exit code 1 if any scenario check fails.
"""
import argparse
import ctypes as C
import json
import os
import random
import subprocess
import sys
import tempfile
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FW = os.path.join(ROOT, "firmware")

# ---------------------------------------------------------------- the controller, through ctypes
MODE = {"AUTO": 0, "ON": 1, "OFF": 2}
FAN_AUTO, FAN_LOW, FAN_HIGH = 0, 1, 2
STATES = ["Starting", "Cooling", "Idle", "On", "Eco off", "Off", "Not cooling", "No AC power", "CRITICAL"]
ALARMS = ["cold warn", "cold critical", "hot warn", "not cooling", "leak", "door", "sensor", "condensation",
          "override", "shutdown", "no AC power", "link"]


class Settings(C.Structure):
    _fields_ = [("mode", C.c_uint8), ("fan", C.c_uint8), ("eco", C.c_bool), ("target", C.c_float),
                ("warn_cold", C.c_float), ("crit_cold", C.c_float), ("warn_hot", C.c_float),
                ("eco_dt", C.c_float), ("eco_band", C.c_float), ("eco_hot_on", C.c_float),
                ("min_on_s", C.c_uint32), ("min_off_s", C.c_uint32),
                ("sp_min", C.c_float), ("sp_max", C.c_float), ("sp_offset", C.c_float), ("avg_s", C.c_uint32),
                ("trim_s", C.c_uint32), ("trim_fast_s", C.c_uint32), ("trim_band", C.c_float),
                ("verify_s", C.c_uint32), ("verify_hot_s", C.c_uint32), ("max_retries", C.c_uint8),
                ("door_alarm_s", C.c_uint32), ("crit_delay_s", C.c_uint32), ("mains_delay_s", C.c_uint32),
                ("min_send_gap_s", C.c_uint32)]


class Inputs(C.Structure):
    _fields_ = [("cold", C.c_float), ("hot", C.c_float), ("supply", C.c_float), ("ret", C.c_float),
                ("exhaust", C.c_float), ("room", C.c_float), ("rh_cold", C.c_float),
                ("door_open", C.c_bool), ("leak", C.c_bool), ("mains", C.c_bool)]


class Outputs(C.Structure):
    _fields_ = [("ac_on", C.c_bool), ("setpoint", C.c_float), ("fan", C.c_uint8), ("send", C.c_bool),
                ("state", C.c_uint8), ("alarms", C.c_uint16), ("shutdown", C.c_bool), ("cooling", C.c_int8),
                ("eco", C.c_bool), ("retries", C.c_uint8), ("dew_point", C.c_float), ("cold_avg", C.c_float),
                ("load_dt", C.c_float)]


def load_lib():
    out = os.path.join(tempfile.gettempdir(), "libsra_%d.so" % os.getpid())
    src = os.path.join(FW, "test", "sra_capi.cpp")
    subprocess.check_call(["g++", "-std=c++17", "-O2", "-shared", "-fPIC", "-Wall", "-Werror",
                           "-I" + os.path.join(FW, "components", "sra_control"), src, "-o", out])
    lib = C.CDLL(out)
    lib.sra_new.restype = C.c_void_p
    lib.sra_free.argtypes = [C.c_void_p]
    lib.sra_get_settings.argtypes = [C.c_void_p, C.POINTER(Settings)]
    lib.sra_set_settings.argtypes = [C.c_void_p, C.POINTER(Settings)]
    lib.sra_step.argtypes = [C.c_void_p, C.POINTER(Inputs), C.c_uint32, C.POINTER(Outputs)]
    lib.sra_sizeof.restype = C.c_uint
    for i, st in enumerate((Settings, Inputs, Outputs)):
        assert lib.sra_sizeof(i) == C.sizeof(st), "struct layout mismatch: %s" % st.__name__
    os.remove(out)                      # already mapped
    return lib


# ---------------------------------------------------------------- the rack and the AC
P = dict(
    m_hi=134.0, m_lo=100.0,     # AC fan air flow (W/K): about 400 / 300 m3/h
    eps=0.65, t_evap=6.0,       # coil effectiveness and evaporating temperature
    q_fan=60.0,                 # AC fan heat into the loop (W)
    p_comp=1300.0, m_cond=110.0,  # compressor power, condenser air flow (W/K)
    c_cold=25e3, c_hot=60e3,    # heat capacity of the cold and hot volumes incl. IT metal (J/K)
    ua_cold=2.0, ua_hot=5.0,    # lined walls to the room (W/K)
    th_band=0.5, restart_s=180, min_run_s=60,   # the AC's own thermostat
)


class Rack:
    def __init__(self, room, q_it, mains_input=False, resume_on_power=False, seed=1):
        self.room, self.q_it = room, q_it
        self.tc = self.th = self.sup = room + 2.0
        self.tx, self.exh = room + 2.0, room
        self.power, self.on, self.sp, self.fan = True, False, 24, FAN_AUTO
        self.comp, self.t_comp, self.t = False, -1e9, 0
        self.comp_ok, self.ir_ok, self.mains_input, self.resume = True, True, mains_input, resume_on_power
        self.rng = random.Random(seed)

    def set_power(self, on):
        if self.power and not on:
            self.comp, self.t_comp = False, self.t
            self.saved, self.on = self.on, False
        if on and not self.power:
            self.on = self.saved if self.resume else False
        self.power = on

    def receive(self, out):
        if self.power and self.ir_ok:
            self.on, self.sp, self.fan = bool(out.ac_on), int(round(out.setpoint)), int(out.fan)

    def step(self):
        p = P
        fan_runs = self.power and self.on
        m = (p["m_lo"] if self.fan == FAN_LOW else p["m_hi"]) if fan_runs else max(40.0, self.q_it / 12.0)
        if fan_runs and self.comp_ok:
            if self.comp and self.th < self.sp - p["th_band"] and self.t - self.t_comp >= p["min_run_s"]:
                self.comp, self.t_comp = False, self.t
            elif not self.comp and self.th > self.sp + p["th_band"] and self.t - self.t_comp >= p["restart_s"]:
                self.comp, self.t_comp = True, self.t
        elif self.comp:
            self.comp, self.t_comp = False, self.t
        q_ac = max(0.0, p["eps"] * m * (self.th - p["t_evap"])) if self.comp else 0.0
        q_fan = p["q_fan"] if fan_runs else 0.0
        self.tx = self.tc + self.q_it / m
        t_sup = self.th - (q_ac - q_fan) / m
        self.th += (m * (self.tx - self.th) + p["ua_hot"] * (self.room - self.th)) / p["c_hot"]
        self.tc += (m * (t_sup - self.tc) + p["ua_cold"] * (self.room - self.tc)) / p["c_cold"]
        self.sup += (t_sup - self.sup) / 20.0
        ex_target = self.room + ((q_ac + p["p_comp"]) / p["m_cond"] if self.comp else (1.0 if fan_runs else 0.0))
        self.exh += (ex_target - self.exh) / 90.0
        self.t += 1

    def inputs(self):
        n = lambda: self.rng.gauss(0.0, 0.05)
        return Inputs(cold=self.tc + n(), hot=self.tx + n(), supply=self.sup + n(), ret=self.th + n(),
                      exhaust=self.exh + n(), room=self.room, rh_cold=40.0, door_open=False, leak=False,
                      mains=self.power if self.mains_input else True)


# ---------------------------------------------------------------- scenarios
def run(lib, name, hours, room, q_it, events=(), settings=None, **rack_kw):
    rack = Rack(room, q_it, **rack_kw)
    ctl = lib.sra_new()
    s = Settings()
    lib.sra_get_settings(ctl, C.byref(s))
    for k, v in (settings or {}).items():
        setattr(s, k, v)
    lib.sra_set_settings(ctl, C.byref(s))
    out = Outputs()
    ev = sorted(events, key=lambda e: e[0])
    rec = {k: [] for k in ("t", "cold", "hot", "ret", "sup", "sp", "on", "comp", "state", "alarms", "exh",
                           "cold_avg")}
    sends, alarm_first, shutdown_at, shut_it = [], OrderedDict(), None, None
    for t in range(int(hours * 3600)):
        while ev and ev[0][0] * 3600 <= t:
            ev.pop(0)[1](rack)
        if t % 5 == 0:
            inp = rack.inputs()
            lib.sra_step(ctl, C.byref(inp), t, C.byref(out))
            if out.send:
                sends.append(t)
                rack.receive(out)
            for i, a in enumerate(ALARMS):
                if out.alarms & (1 << i) and a not in alarm_first:
                    alarm_first[a] = t
            if out.shutdown and shutdown_at is None:
                shutdown_at = t
        if shutdown_at is not None and shut_it is None and t >= shutdown_at + 120:
            rack.q_it, shut_it = 30.0, t            # the IT shuts down on the request
        rack.step()
        if t % 10 == 0:
            for k, v in (("t", t), ("cold", rack.tc), ("hot", rack.tx), ("ret", rack.th), ("sup", rack.sup),
                         ("sp", out.setpoint), ("on", int(rack.power and rack.on)), ("comp", int(rack.comp)),
                         ("state", out.state), ("alarms", out.alarms), ("exh", rack.exh),
                         ("cold_avg", out.cold_avg)):
                rec[k].append(v)
    lib.sra_free(ctl)
    return {"name": name, "rec": rec, "sends": sends, "alarm_first": alarm_first, "shutdown_at": shutdown_at,
            "settings": s, "room": room}


def window(r, t0, t1, key):
    return [v for t, v in zip(r["rec"]["t"], r["rec"][key]) if t0 <= t <= t1]


def switches(r):
    on = r["rec"]["on"]
    ts = r["rec"]["t"]
    return [ts[i] for i in range(1, len(on)) if on[i] != on[i - 1]]


def scenarios(lib):
    res, checks = [], []

    def chk(scen, name, ok, detail):
        checks.append((scen, name, bool(ok), detail))

    def mean(v):
        return sum(v) / float(len(v))

    # 1 steady load: the AC thermostat cycles the compressor; the cold side swings, its average is held
    r = run(lib, "Steady 1.5 kW, room 26 degC", 8, 26.0, 1500.0)
    c = window(r, 2 * 3600, 8 * 3600, "cold")
    tgt, s = r["settings"].target, r["settings"]
    chk(r["name"], "cold side averages at or below the target", tgt - 4.0 <= mean(c) <= tgt + 1.0,
        "average %.1f degC (target %.0f), swing %.1f-%.1f" % (mean(c), tgt, min(c), max(c)))
    chk(r["name"], "cold side peaks below the warning", max(c) < s.warn_cold, "max %.1f degC" % max(c))
    late = [a for a, t in r["alarm_first"].items() if t > 1800]
    chk(r["name"], "no alarms once settled", not late, ", ".join(late) or "none")
    sp = window(r, 2 * 3600, 8 * 3600, "sp")
    chg = sum(1 for x, y in zip(sp, sp[1:]) if x != y)
    chk(r["name"], "setpoint steady (no hunting)", chg <= 3, "%d setpoint changes in hours 2-8" % chg)
    res.append(r)

    # 2 light load: eco pulls the rack down, switches the AC off and on
    r = run(lib, "Light load 0.2 kW, room 21 degC (eco)", 12, 21.0, 200.0)
    on = window(r, 2 * 3600, 12 * 3600, "on")
    sw = switches(r)
    gaps = [b - a for a, b in zip(sw, sw[1:])]
    c = window(r, 0, 12 * 3600, "cold")
    chk(r["name"], "AC off most of the time", mean(on) < 0.5, "on %.0f%% of hours 2-12" % (100.0 * mean(on)))
    chk(r["name"], "AC cycles, never faster than its minimum times",
        len(sw) >= 3 and min(gaps or [1e9]) >= r["settings"].min_off_s - 10,
        "%d switches, shortest gap %.0f min" % (len(sw), min(gaps or [0]) / 60.0))
    chk(r["name"], "cold side never above the warning", max(c) < r["settings"].warn_cold, "max %.1f degC" % max(c))
    res.append(r)

    # 3 power cut with the IT on its UPS: the AC is dead, the rack heats up; the controller asks for a
    # shutdown, and restarts the AC (in standby after the cut) when the power is back
    for mains in (False, True):
        r = run(lib, "Power cut 20 min, IT on UPS, AC back in standby (%s mains detect)" % (
            "with" if mains else "no"), 5, 26.0, 1500.0,
            events=[(2.0, lambda k: k.set_power(False)), (2.0 + 20 / 60.0, lambda k: k.set_power(True))],
            mains_input=mains)
        cut, back = 2 * 3600, 2 * 3600 + 20 * 60
        on_t = next((t for t, v in zip(r["rec"]["t"], r["rec"]["on"]) if t > back and v), None)
        delay = (on_t - back) if on_t is not None else None
        c = window(r, 0, 5 * 3600, "cold")
        limit = 60 if mains else 20 * 60
        chk(r["name"], "AC restarted after the power returned", delay is not None and delay <= limit,
            "%s after power back (limit %d min)" % ("%.1f min" % (delay / 60.0) if delay is not None else "never",
                                                     max(1, limit // 60)))
        sd = r["shutdown_at"]
        chk(r["name"], "IT shutdown requested while the AC was down", sd is not None and cut < sd < back,
            "%.0f min into the cut" % ((sd - cut) / 60.0) if sd else "never")
        chk(r["name"], "cold side peak held under 40 degC", max(c) < 40.0, "peak %.1f degC" % max(c))
        r["back_delay_s"] = delay
        res.append(r)

    # 4 compressor failure: not-cooling alarm, shutdown request, temperatures stop rising
    def fail(k):
        k.comp_ok = False
    r = run(lib, "Compressor fails at 2 h (IT shuts down on request)", 5, 26.0, 1500.0, events=[(2.0, fail)])
    nc = r["alarm_first"].get("not cooling")
    sd = r["shutdown_at"]
    chk(r["name"], "not-cooling alarm within 20 min", nc is not None and nc - 7200 <= 1200,
        "%.0f min after the failure" % ((nc - 7200) / 60.0) if nc else "no alarm")
    chk(r["name"], "shutdown requested", sd is not None,
        "%.0f min after the failure" % ((sd - 7200) / 60.0) if sd else "never")
    if sd:
        # the IT (modelled) stops 2 min after the request; after that the sealed box only creeps up
        # on the AC fan's own heat, with nothing left running to harm
        c_stop = window(r, sd + 120, sd + 130, "cold")[0]
        chk(r["name"], "IT stopped before the cold side reached 38 degC", c_stop < 38.0,
            "cold side %.1f degC when the IT stopped" % c_stop)
    res.append(r)

    # 5 load step from eco
    def step_up(k):
        k.q_it = 2200.0
    r = run(lib, "Load step 0.3 to 2.2 kW at 3 h, room 28 degC", 6, 28.0, 300.0, events=[(3.0, step_up)])
    on_t = next((t for t, v in zip(r["rec"]["t"], r["rec"]["on"]) if t >= 3 * 3600 and v), None)
    c = window(r, 3 * 3600, 6 * 3600, "cold")
    chk(r["name"], "AC on within 5 min of the step", on_t is not None and on_t - 3 * 3600 <= 300,
        "%.1f min" % ((on_t - 3 * 3600) / 60.0) if on_t is not None else "never")
    chk(r["name"], "cold side peak below the warning", max(c) < r["settings"].warn_cold, "peak %.1f degC" % max(c))
    res.append(r)
    return res, checks


# ---------------------------------------------------------------- plot
def plot(res, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    n = len(res)
    fig, axs = plt.subplots(n, 1, figsize=(13, 2.7 * n), sharex=False)
    for ax, r in zip(axs, res):
        rec = r["rec"]
        h = [t / 3600.0 for t in rec["t"]]
        for i in range(1, len(h)):
            if rec["comp"][i]:
                ax.axvspan(h[i - 1], h[i], color="#d8e9f7", lw=0)
            elif not rec["on"][i]:
                ax.axvspan(h[i - 1], h[i], color="#ececec", lw=0)
        ax.plot(h, rec["hot"], color="#c8442f", lw=1.2, label="hot side (server exhaust)")
        ax.plot(h, rec["ret"], color="#e39a7d", lw=0.9, label="AC return")
        ax.plot(h, rec["cold"], color="#2f6fb5", lw=1.3, label="cold side (server intake)")
        ax.plot(h, rec["cold_avg"], color="#14365e", lw=1.2, label="cold side, 10-min average")
        ax.plot(h, rec["sup"], color="#56b4c9", lw=0.8, ls="--", label="AC supply")
        ax.step(h, rec["sp"], color="#222", lw=0.9, where="post", label="AC setpoint (sent by IR)")
        s = r["settings"]
        ax.axhline(s.target, color="#2f6fb5", lw=0.6, ls=":")
        ax.axhline(s.warn_cold, color="#d08b00", lw=0.6, ls=":")
        ax.axhline(s.crit_cold, color="#b00020", lw=0.6, ls=":")
        for t in r["sends"]:
            ax.plot([t / 3600.0], [ax.get_ylim()[1] if False else 47.5], marker="v", ms=3.5, color="#555")
        for a, t in r["alarm_first"].items():
            ax.annotate(a, (t / 3600.0, 44.0), fontsize=7, color="#b00020", rotation=90, va="top", ha="right")
        if r.get("shutdown_at"):
            ax.axvline(r["shutdown_at"] / 3600.0, color="#b00020", lw=1.0)
        ax.set_ylim(5, 49)
        ax.set_xlim(0, h[-1])
        ax.set_ylabel("degC")
        ax.set_title(r["name"], fontsize=10, loc="left")
        ax.grid(alpha=0.25)
    axs[0].legend(loc="upper right", fontsize=7, ncol=3)
    axs[-1].set_xlabel("hours   (blue band: compressor running; grey: AC off; triangles: IR sent; red: alarms)")
    fig.suptitle("CP-SRA16-ELC-001 - rack controller in a thermal model of the SRA-16 loop", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.98))
    fig.savefig(path, dpi=100)
    plt.close(fig)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--plot", default=os.path.join(ROOT, "renders", "controls_sim.png"))
    ap.add_argument("--json", default=os.path.join(FW, "test", "sim_report.json"))
    ap.add_argument("--no-plot", action="store_true")
    a = ap.parse_args(argv)
    lib = load_lib()
    res, checks = scenarios(lib)
    for scen, name, ok, det in checks:
        print("[%s] %s: %s - %s" % ("ok" if ok else "FAIL", scen, name, det))
    if not a.no_plot:
        plot(res, a.plot)
    rep = OrderedDict([("model", P), ("checks", [OrderedDict([("scenario", s), ("check", n), ("ok", ok),
                                                              ("detail", d)]) for s, n, ok, d in checks]),
                       ("scenarios", [OrderedDict([("name", r["name"]), ("ir_sends", len(r["sends"])),
                                                   ("alarms_first_s", r["alarm_first"]),
                                                   ("shutdown_at_s", r["shutdown_at"])]) for r in res])])
    with open(a.json, "w") as fh:
        json.dump(rep, fh, indent=1)
    return 0 if all(ok for _, _, ok, _ in checks) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
