#!/usr/bin/env python3
"""
office_air.py - how much cold air, and so how much cooling, the office ports deliver (docs/OFFICE_AIR.md).

The office loop: cold plenum -> fan grille P10 -> fan -> plenum adaptor P9 (cone, fan bore to duct bore)
-> its spigot -> flex duct -> office wall grille P12 -> office -> P12 -> flex duct -> P9 spigot -> P9 cone
(now a diffuser) -> P10 -> hot plenum.
Every element is a loss coefficient on its own velocity, converted to the duct's velocity pressure, so
the system curve is dp = K_total * rho v^2 / 2.  The fans are straight lines between their catalogue
maximum static pressure and maximum airflow, derated for a grille and a cone right at the fan; two
fans in push-pull (a second fan on the return adaptor) add their pressures.  The loss coefficients are
handbook values for sharp-edged perforated plates and fittings (Idelchik): take the flows as +-20 %.

The grille open areas come from the printed parts themselves (tools/printparts.py).

Writes renders/office_air.png and cad/exports/office_air_report.json.
Usage: python3 tools/office_air.py
"""
import json
import math
import os
import sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import printparts as PP  # noqa: E402

RL = PP.RL
RHO, CP = 1.2, 1005.0                  # air, kg/m3 and J/kg K
F_DUCT = 0.05                          # Darcy friction factor, corrugated flex duct pulled straight (sagging: x2-3)
DUCT_M = (0.5, 1.0, 2.0)               # duct length each way (cabinet to the office grille), m
DUCT_DEFAULT = 1.0
DERATE = 0.85                          # fan pressure lost to the grille and the cone right at the fan
# catalogue maxima: static pressure mm H2O, airflow m3/h, speed, noise (manufacturer data, Oct 2026)
FANS = OrderedDict([
    ("nf-a8", {"name": "1 x Noctua NF-A8 PWM", "short": "1 x NF-A8", "n": 1, "p_mm": 2.37, "q": 55.5, "rpm": 2200,
               "noise": "17.7 dB(A) at full speed", "note": "standard: silent"}),
    ("nf-a8x2", {"name": "2 x NF-A8 PWM, push-pull", "short": "2 x NF-A8", "n": 2, "p_mm": 2.37, "q": 55.5, "rpm": 2200,
                 "noise": "about 21 dB(A)", "note": "second fan on the return adaptor"}),
    ("p8max", {"name": "1 x Arctic P8 Max", "short": "1 x P8 Max", "n": 1, "p_mm": 5.3, "q": 67.96, "rpm": 5000,
               "noise": "clearly audible above ~3000 rpm", "note": "boost: cap it with 'Office fan max'"}),
    ("p8maxx2", {"name": "2 x Arctic P8 Max, push-pull", "short": "2 x P8 Max", "n": 2, "p_mm": 5.3, "q": 67.96, "rpm": 5000,
                 "noise": "clearly audible above ~3000 rpm", "note": "most air the 60 mm ducts take"}),
])
COLOURS = {"nf-a8": "#2a78d6", "nf-a8x2": "#eb6834", "p8max": "#1baf7a", "p8maxx2": "#eda100"}   # validated set
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"


def plate_in_duct(f):
    """Thin perforated plate in a duct, sharp edges, on the approach velocity (Idelchik diagram 8-1)."""
    return (0.707 * (1.0 - f) ** 0.375 + 1.0 - f) ** 2 / f ** 2


def plate_exit(f):
    """Free discharge through a perforated plate: the jets' velocity head is lost (vena contracta eps)."""
    eps = 0.62 + 0.38 * f ** 3
    return 1.0 / (f * eps) ** 2


def cone_in(half_deg):
    """Conical contraction (confusor) on the outlet velocity, Idelchik diagram 3-7: 0.05 at 10-20 deg
    half-angle (no separation), rising towards a sharp step's 0.5 * (1 - n) at 90."""
    return 0.05 if half_deg <= 20.0 else 0.05 + 0.25 * (half_deg - 20.0) / 70.0


def cone_out(half_deg):
    """Conical diffuser: the fraction of a sudden expansion's loss (Idelchik diagram 5-2), about 0.2 at
    4 deg half-angle, 0.8 at 20 and 1.0 (a plain step) from 30 up."""
    return min(1.0, 0.2 + 0.6 * max(half_deg - 4.0, 0.0) / 16.0) if half_deg < 20.0 else min(1.0, 0.8 + 0.02 * (half_deg - 20.0))


def geometry():
    I = PP.interfaces()
    op = I["office"][0]
    _, gi = PP.office_grille(I, op)
    _, wi = PP.wall_grille(I)
    _, ai = PP.office_adaptor(I, op)
    P = I["P"]
    d = P["office_duct_d"] / 1000.0
    a_d = math.pi * d ** 2 / 4.0                                   # flex duct bore
    a_b = math.pi * (wi["rb"] / 1000.0) ** 2                       # spigot bore
    a_s = math.pi * (ai["rm"] / 1000.0) ** 2                       # adaptor mouth = fan bore
    return {"d": d, "a_d": a_d, "a_b": a_b, "a_s": a_s, "cone_half_deg": ai["half_angle"],
            "f10": gi["open_mm2"] / 1e6 / a_s,                       # fan grille, open / fan bore
            "f12": wi["open_mm2"] / 1e6 / a_b,                       # wall grille, open / bore
            "open10_pct": 100.0 * gi["open_mm2"] / gi["bore_mm2"], "open12_pct": 100.0 * wi["open_mm2"] / wi["bore_mm2"]}


def losses(G, L):
    """Loss coefficients on the duct velocity pressure, duct L metres each way."""
    rd_b, rd_s = (G["a_d"] / G["a_b"]) ** 2, (G["a_d"] / G["a_s"]) ** 2
    duct = F_DUCT * L / G["d"]
    return OrderedDict([
        ("supply: fan grille P10 + entry", (plate_in_duct(G["f10"]) + 0.5) * rd_s),
        ("supply: adaptor cone, fan bore to duct bore", cone_in(G["cone_half_deg"]) * rd_b),
        ("supply: spigot bore into the duct", (1.0 - G["a_b"] / G["a_d"]) ** 2 * rd_b),
        ("supply: flex duct, %.1f m" % L, duct),
        ("supply: office wall grille P12, free outlet", plate_exit(G["f12"]) * rd_b),
        ("return: office wall grille P12 + entry", (plate_in_duct(G["f12"]) + 0.5) * rd_b),
        ("return: flex duct, %.1f m" % L, duct),
        ("return: duct into the spigot bore", 0.5 * (1.0 - G["a_b"] / G["a_d"]) * rd_b),
        ("return: adaptor cone as a diffuser", cone_out(G["cone_half_deg"]) * (1.0 - G["a_b"] / G["a_s"]) ** 2 * rd_b),
        ("return: fan grille P10, free outlet", plate_exit(G["f10"]) * rd_s),
    ])


def operating_point(fan, k_total, G):
    """Flow (m3/h) where n derated straight-line fans meet dp = k * rho v^2 / 2."""
    pmax = fan["n"] * DERATE * fan["p_mm"] * 9.80665
    a = k_total * RHO / 2.0 / (3600.0 * G["a_d"]) ** 2              # dp = a Q^2
    b = pmax / fan["q"]                                            # fan: dp = pmax - b Q
    q = (-b + math.sqrt(b * b + 4.0 * a * pmax)) / (2.0 * a)
    return q, a * q * q


def humidity_ratio(t_dew):
    """g water per kg dry air at a dew point (Magnus), 101.3 kPa."""
    pw = 0.6112 * math.exp(17.62 * t_dew / (243.12 + t_dew))
    return 622.0 * pw / (101.325 - pw)


def main():
    G = geometry()
    rep = OrderedDict([("geometry", OrderedDict((k, round(v, 5)) for k, v in G.items())),
                       ("duct_friction", F_DUCT), ("fan_derate", DERATE), ("systems", OrderedDict())])
    for L in DUCT_M:
        ks = losses(G, L)
        kt = sum(ks.values())
        row = OrderedDict([("k_total", round(kt, 2)), ("elements", OrderedDict((k, round(v, 2)) for k, v in ks.items())),
                           ("fans", OrderedDict())])
        for key, fan in FANS.items():
            q, dp = operating_point(fan, kt, G)
            v = q / 3600.0 / G["a_d"]
            row["fans"][key] = OrderedDict([("m3h", round(q, 1)), ("pa", round(dp, 1)), ("duct_m_s", round(v, 2)),
                                            ("w_per_k", round(RHO * CP * q / 3600.0, 2))])
        rep["systems"]["%.1f m" % L] = row
    base = rep["systems"]["%.1f m" % DUCT_DEFAULT]
    # what it means: sensible cooling at the office - supply difference, and the drying on the AC coil
    office, rh, supply, coil_dew = 26.0, 55.0, 18.0, 10.5
    office_dew = 243.12 * (math.log(rh / 100.0) + 17.62 * office / (243.12 + office)) / (
        17.62 - (math.log(rh / 100.0) + 17.62 * office / (243.12 + office)))
    dw = humidity_ratio(office_dew) - humidity_ratio(coil_dew)
    rep["example"] = OrderedDict([("office_c", office), ("office_rh", rh), ("supply_c", supply),
                                  ("office_dew_c", round(office_dew, 1)), ("loop_dew_c", coil_dew), ("cases", OrderedDict())])
    for key, fan in FANS.items():
        q = base["fans"][key]["m3h"]
        sens = RHO * CP * q / 3600.0 * (office - supply)
        water = RHO * q * dw                                       # g/h
        rep["example"]["cases"][key] = OrderedDict([("m3h", q), ("sensible_w", round(sens)),
                                                    ("water_g_h", round(water)), ("water_l_day", round(water * 24 / 1000, 1)),
                                                    ("latent_w", round(water * 2450.0 / 3600.0))])
    rep["fans"] = FANS
    out = os.path.join(ROOT, "cad", "exports", "office_air_report.json")
    with open(out, "w") as fh:
        json.dump(rep, fh, indent=1)
    plot(rep, G, os.path.join(ROOT, "renders", "office_air.png"))
    print("office air: K %.1f (1 m ducts); " % base["k_total"] + "; ".join(
        "%s %.1f m3/h" % (FANS[k]["name"], v["m3h"]) for k, v in base["fans"].items()))
    for k, c in rep["example"]["cases"].items():
        print("  %-32s %5.1f m3/h  %3d W sensible at %g K  + %3d g/h water (%d W latent)" % (
            FANS[k]["name"], c["m3h"], c["sensible_w"], office - supply, c["water_g_h"], c["latent_w"]))
    return 0


def plot(rep, G, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                         "ytick.color": INK2, "axes.facecolor": SURFACE, "figure.facecolor": SURFACE})
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12.5, 4.8))
    qs = [i * 0.5 for i in range(0, 141)]
    # (a) fan curves against the system curves
    for L in DUCT_M:
        kt = rep["systems"]["%.1f m" % L]["k_total"]
        a = kt * RHO / 2.0 / (3600.0 * G["a_d"]) ** 2
        a1.plot(qs, [a * q * q for q in qs], color=INK2, lw=1.0, ls="-" if L == DUCT_DEFAULT else "--", zorder=2)
    a1.annotate("<- duct system curves:\n    2, 1 and 0.5 m each way", (43.0, 93.0), fontsize=8, color=INK2, va="top")
    nudge = {"nf-a8": 3, "nf-a8x2": -12, "p8max": 3, "p8maxx2": 3}    # two lines start close together
    for key, fan in FANS.items():
        pmax = fan["n"] * DERATE * fan["p_mm"] * 9.80665
        q_ = [q for q in qs if q <= fan["q"]]
        a1.plot(q_, [pmax * (1 - q / fan["q"]) for q in q_], color=COLOURS[key], lw=1.8, zorder=3)
        op = rep["systems"]["%.1f m" % DUCT_DEFAULT]["fans"][key]
        a1.plot([op["m3h"]], [op["pa"]], "o", ms=7, color=COLOURS[key], mec=SURFACE, mew=1.5, zorder=4)
        a1.annotate("%s: %.0f m³/h" % (fan["short"], op["m3h"]), (1.0, pmax), xytext=(0, nudge[key]),
                    textcoords="offset points", fontsize=8, color=INK)
    a1.set_xlim(0, 70)
    a1.set_ylim(0, 95)
    a1.set_xlabel("Air flow (m³/h)")
    a1.set_ylabel("Pressure (Pa)")
    a1.set_title("Fan curves against the duct system (dots: 1 m ducts)", fontsize=10, loc="left", color=INK)
    # (b) sensible cooling against the office - supply difference, 1 m ducts
    dts = [i * 0.5 for i in range(0, 25)]
    for key, fan in FANS.items():
        w = rep["systems"]["%.1f m" % DUCT_DEFAULT]["fans"][key]["w_per_k"]
        a2.plot(dts, [w * t for t in dts], color=COLOURS[key], lw=1.8)
        a2.annotate("%s  %.0f W" % (fan["name"], w * 12.0), (12.0, w * 12.0), xytext=(4, 0), textcoords="offset points",
                    fontsize=8, color=INK, va="center")
    a2.axvline(8.0, color=INK2, lw=0.8, ls=":")
    a2.annotate("office 26 °C, supply 18 °C", (8.0, 3.0), xytext=(3, 0), textcoords="offset points", fontsize=8,
                color=INK2)
    a2.set_xlim(0, 19)
    a2.set_ylim(0, 130)
    a2.set_xlabel("Office minus cold-side temperature (K)")
    a2.set_ylabel("Sensible cooling (W)")
    a2.set_title("Cooling delivered to the office (1 m ducts each way)", fontsize=10, loc="left", color=INK)
    for ax in (a1, a2):
        ax.grid(color=GRID, lw=0.6)
        ax.set_axisbelow(True)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    handles = [plt.Line2D([], [], color=COLOURS[k], lw=1.8, label=f["name"]) for k, f in FANS.items()]
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False, fontsize=8.5)
    fig.suptitle("SRA-16 office air: two %g mm flex ducts (supply and return), %g mm fans" % (
        1000 * G["d"], RL.DEFAULTS["office_fan"]), fontsize=11, color=INK)
    fig.tight_layout(rect=(0, 0.07, 1, 0.95))
    fig.savefig(path, dpi=120)
    plt.close(fig)


if __name__ == "__main__":
    sys.exit(main())
