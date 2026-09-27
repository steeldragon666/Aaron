#!/usr/bin/env python3
"""
weldment.py - fabrication model of the SRA-16 welded steel frame
(drawing CP-SRA16-FRM-001), derived from the Frame group of rack_layout.py.

Pure Python (no CAD imports), so the cut list, drilling schedule, joint list,
weld sequence and stock nesting always follow the layout: change a parameter
(e.g. the AC grille split M3, which sets the mid-rail height), re-run
tools/make_weld_pack.py and every fabrication document updates.

Frame-local datums used on all fabrication documents (mm):
  A = underside of the base rails   (local z = 0)
  B = front face of the frame       (local y = 0)
  C = left face of the frame        (local x = 0)
Model -> local: subtract (skin, skin, z_base0).
"""
import math
import os
import sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "cad", "fusion", "SilentRackAC"))
import rack_layout as RL  # noqa: E402

DOC_NO = "CP-SRA16-FRM-001"
REV = "A"
STEEL = 7.85e-6          # kg/mm3

# Fabrication parameters (not geometry of the assembly - that lives in rack_layout.py)
FAB = {
    "shs_t": 2.0,         # SHS wall (1.6 also works but is harder to MIG without burn-through)
    "shs_ro": 4.0,        # external corner radius (~2t, AS/NZS 1163)
    "grade": "C350L0",
    "std": "AS/NZS 1163",
    "cap_t": 3.0,         # post top cap plate
    "rivnut_hole": 9.0,   # M6 steel rivnut
    "pitch": 250.0,       # max panel-fixing pitch
    "edge": 40.0,         # first/last fixing from a member end
    "skirt_clear": 30.0,  # skirt fixings clear of the castor pads
    "spacer_edge": 60.0,  # rail-spacer bolts on the uprights (placed between the side-panel rivnuts)
    "clash": 22.0,        # min axial gap between rivnuts on different faces (bodies meet inside a 26 mm bore)
    "castor_pcd": 60.0,   # castor top-plate bolt square (to suit the castor bought)
    "stock_shs": 6500.0,  # AU stock length (8.0 m also common)
    "stock_fb": 6000.0,
    "kerf": 3.0,
    "trim": 10.0,         # squaring cut at the start of each bar
    "fillet": 3.0,        # fillet leg on 2 mm wall
    "stitch": 25.0,       # ledge stitch length
    "stitch_pitch": 150.0,
    "stitch_return": 20.0,
}

FACE_USE = OrderedDict([
    ("side", "Side panel fixing"),
    ("rear", "Rear panel fixing"),
    ("top", "Top panel fixing"),
    ("skirt", "Plinth skirt fixing"),
    ("spacer", "19in rail-spacer bolts"),
])


# ---------------------------------------------------------------- helpers
def _bbox(part):
    mins = [min(RL.prim_bbox(q)[0][i] for q in part["add"]) for i in range(3)]
    maxs = [max(RL.prim_bbox(q)[1][i] for q in part["add"]) for i in range(3)]
    return mins, maxs


def shs_props(b, t, ro):
    ri = max(ro - t, 0.0)
    k = 4.0 - math.pi
    area = (b * b - k * ro * ro) - ((b - 2 * t) ** 2 - k * ri * ri)
    return {"area_mm2": area, "kg_m": area * STEEL * 1000.0}


def even_positions(a0, a1, pitch, nmin=2):
    """Evenly spaced positions from a0 to a1 with spacing <= pitch."""
    if a1 <= a0:
        return [(a0 + a1) / 2.0]
    n = max(nmin, int(math.ceil((a1 - a0) / pitch - 1e-9)) + 1)
    return [a0 + i * (a1 - a0) / (n - 1) for i in range(n)]


def _axis_name(a):
    return "XYZ"[a]


# ---------------------------------------------------------------- model
def build(P=None, fab=None):
    """Return the weldment dict: members, joints, marks, nesting, totals."""
    P = RL.resolve(P)
    F = dict(FAB, **(fab or {}))
    parts, D = RL.build_parts(P)
    f, s = D["frame"], D["skin"]
    W, DP = D["ext_w"], D["ext_d"]
    zb0, zt1 = D["z_base0"], D["z_toprail1"]
    org = (s, s, zb0)
    bound = ((s, W - s), (s, DP - s), (zb0, zt1))
    shs = shs_props(f, F["shs_t"], F["shs_ro"])
    sec_shs = "%gx%gx%.1f SHS" % (f, f, F["shs_t"])
    cl, ct, pw, pt = D["cleat"], D["cleat_t"], D["pad_w"], D["pad_t"]

    members = []
    for p in parts:
        is_spacer = p["name"].startswith("Rail spacer")
        if p["group"] != "Frame" and not is_spacer:
            continue
        mn, mx = _bbox(p)
        name = p["name"]
        ext = [mx[i] - mn[i] for i in range(3)]
        m = {"name": name, "min": list(mn), "max": list(mx), "holes": [], "part": p}
        if name.startswith("Castor pad"):
            m.update(kind="pad", section="PL %gx%gx%g" % (pw, pw, pt), cut=pw, axis=None,
                     mass=pw * pw * pt * STEEL, sub="FINAL")
            c = ((mn[0] + mx[0]) / 2.0, (mn[1] + mx[1]) / 2.0)
            h = F["castor_pcd"] / 2.0
            m["taps"] = [(c[0] + dx, c[1] + dy) for dx in (-h, h) for dy in (-h, h)]
        elif name.startswith("Ledge"):
            a = max(range(3), key=lambda i: ext[i])
            m.update(kind="ledge", section="%gx%g FB" % (cl, ct), cut=ext[a], axis=a,
                     mass=ext[a] * cl * ct * STEEL)
        else:
            a = max(range(3), key=lambda i: ext[i])
            kind = ("post" if name.startswith("Post") else "upright" if name.startswith("Upright")
                    else "spacer" if is_spacer else "rail")
            m.update(kind=kind, axis=a, section=sec_shs)
            m["tube_max"] = list(mx)
            if kind == "post":                    # cap plate on top, tube cut short by cap_t
                m["tube_max"][2] = mx[2] - F["cap_t"]
            m["cut"] = m["tube_max"][a] - mn[a]
            m["mass"] = m["cut"] / 1000.0 * shs["kg_m"]
            if kind == "spacer":
                m["sub"] = "LOOSE"
        side = "L" if (mn[0] + mx[0]) / 2.0 < W / 2.0 else "R"
        if m["kind"] in ("post", "upright") or (m["kind"] == "rail" and m["axis"] == 1):
            m["sub"] = "SA-" + side
        elif m["kind"] == "rail":
            m["sub"] = "BOX"
        elif m["kind"] == "ledge":
            m["sub"] = ("SA-" + side) if m["axis"] == 1 else "BENCH"
        members.append(m)

    # ------------------------------------------------------------ rivnut holes
    def face_coord(m, k, sg):
        return (m["max"][k] if sg > 0 else m["min"][k])

    def classify(m, k, sg):
        c = face_coord(m, k, sg)
        if k == 0 and ((sg < 0 and abs(c - bound[0][0]) < .01) or (sg > 0 and abs(c - bound[0][1]) < .01)):
            return "side"
        if k == 1 and sg > 0 and abs(c - bound[1][1]) < .01:
            return "rear"
        if k == 2 and sg > 0 and abs(c - bound[2][1]) < .01 and m["kind"] != "post":
            return "top"
        if k == 2 and sg < 0 and abs(c - bound[2][0]) < .01 and m["kind"] == "rail":
            return "skirt"
        if m["kind"] == "upright" and k == 0:
            inner = (sg > 0) if m["sub"] == "SA-L" else (sg < 0)
            if inner:
                return "spacer"
        return None

    for m in members:
        if m["kind"] not in ("post", "rail", "upright"):
            continue
        a = m["axis"]
        a0, a1 = m["min"][a], m["max"][a]
        faces = []
        for k in range(3):
            if k == a:
                continue
            for sg in (-1, 1):
                use = classify(m, k, sg)
                if use:
                    faces.append((list(FACE_USE).index(use), use, k, sg))
        faces.sort()
        primary = None                           # axial positions on the first (primary) face
        for _, use, k, sg in faces:
            if use == "skirt":
                lo, hi = bound[a][0] + pw + F["skirt_clear"], bound[a][1] - pw - F["skirt_clear"]
            elif use == "spacer":
                lo, hi = a0 + F["spacer_edge"], a1 - F["spacer_edge"]
            else:
                lo, hi = a0 + F["edge"], a1 - F["edge"]
            if primary is None:
                out = even_positions(lo, hi, F["pitch"])
                primary = out
            else:
                # secondary faces: midway between the primary holes, so rivnut bodies never meet
                # inside the tube and the pattern stays symmetric end-for-end
                out = [(primary[i] + primary[i + 1]) / 2.0 for i in range(len(primary) - 1)]
                out = [q for q in out if lo - 0.1 <= q <= hi + 0.1]
                if len(out) < 2:
                    out = even_positions(lo, hi, F["pitch"])
            # across-face centre
            cross = [i for i in range(3) if i not in (a, k)][0]
            vc = (m["min"][cross] + m["max"][cross]) / 2.0
            for q in out:
                pt3 = [0.0, 0.0, 0.0]
                pt3[a], pt3[k], pt3[cross] = q, face_coord(m, k, sg), vc
                m["holes"].append({"use": use, "face": ("+" if sg > 0 else "-") + _axis_name(k), "k": k, "sg": sg,
                                   "s": round(q - a0, 1), "p": tuple(pt3), "d": F["rivnut_hole"]})

    # ------------------------------------------------------------ joints (SHS end -> SHS face)
    tubes = [m for m in members if m["kind"] in ("post", "rail", "upright")]
    joints = []

    def overlap(m, n, k):
        return min(m["tube_max"][k], n["tube_max"][k]) - max(m["min"][k], n["min"][k])

    for m in tubes:
        a = m["axis"]
        for end, c in (("start", m["min"][a]), ("end", m["tube_max"][a])):
            for n in tubes:
                if n is m:
                    continue
                hit = (end == "start" and abs(n["tube_max"][a] - c) < .01) or \
                      (end == "end" and abs(n["min"][a] - c) < .01)
                if not hit or any(overlap(m, n, k) <= 1.0 for k in range(3) if k != a):
                    continue
                seams = []
                for k in range(3):
                    if k == a:
                        continue
                    for sg in (-1, 1):
                        cm = m["tube_max"][k] if sg > 0 else m["min"][k]
                        cn = n["tube_max"][k] if sg > 0 else n["min"][k]
                        flush = abs(cm - cn) < .01
                        proud = (cm - cn) * sg > .01       # member face runs past the neighbour's tube
                        ext = abs(cm - bound[k][0 if sg < 0 else 1]) < .01
                        # a top rail stands cap_t above the post tube: that seam is made with the cap (det. D)
                        typ = "flush" if flush else ("cap" if proud and n["kind"] == "post" and k == 2 else "fillet")
                        seams.append({"face": ("+" if sg > 0 else "-") + _axis_name(k), "type": typ, "external": ext})
                pnt = [(m["min"][i] + m["tube_max"][i]) / 2.0 for i in range(3)]
                pnt[a] = c
                stage = m["sub"] if (m["sub"] == n["sub"] and m["sub"].startswith("SA")) else "BOX"
                joints.append({"stage": stage, "m": m, "n": n, "end": end, "p": tuple(pnt), "seams": seams})

    # ------------------------------------------------------------ weld sequence (balanced)
    def order(js):
        if not js:
            return js
        cx = [sum(j["p"][i] for j in js) / len(js) for i in range(3)]
        rem = list(js)
        first = min(rem, key=lambda j: math.dist(j["p"], cx))
        seq = [first]
        rem.remove(first)
        while rem:
            recent = seq[-2:]
            nxt = max(rem, key=lambda j: (min(math.dist(j["p"], r["p"]) for r in recent), -j["p"][2]))
            seq.append(nxt)
            rem.remove(nxt)
        return seq

    seqd = OrderedDict()
    for stage, pre in (("SA-L", "L"), ("SA-R", "R"), ("BOX", "B")):
        js = order([j for j in joints if j["stage"] == stage])
        for i, j in enumerate(js):
            j["id"] = "%s%02d" % (pre, i + 1)
            j["seq"] = i + 1
        seqd[stage] = js
    joints = [j for st in seqd.values() for j in st]

    b_ro = F["shs_ro"]
    seam_len = f - 2 * b_ro + math.pi * b_ro / 2.0          # one face incl. half of each corner
    for j in joints:
        j["len"] = seam_len * sum(1 for s in j["seams"] if s["type"] != "cap")

    # ------------------------------------------------------------ ledges, caps, pads (other welds)
    rails_by = {m["name"]: m for m in members if m["kind"] == "rail"}
    lvl_of = {"floor": "Base", "partition": "Mid", "shelf": "Shelf"}
    ledge_welds, k = [], 0
    for m in members:
        if m["kind"] != "ledge":
            continue
        _, lvl, sd = m["name"].split()
        rail = rails_by["Rail %s %s" % (lvl_of[lvl], sd)]
        L = m["cut"]
        n = max(2, int(math.ceil((L - F["stitch"]) / F["stitch_pitch"] - 1e-9)) + 1)
        k += 1
        ledge_welds.append({"id": "K%02d" % k, "ledge": m, "rail": rail, "stitches": n,
                            "len": n * F["stitch"] + 2 * F["stitch_return"],
                            "stage": m["sub"], "ply_below_top": rail["max"][2] - m["max"][2]})
    caps = []
    for i, m in enumerate([m for m in members if m["kind"] == "post"]):
        caps.append({"id": "T%d" % (i + 1), "post": m, "len": seam_len * 4})
    pads = []
    for i, m in enumerate([m for m in members if m["kind"] == "pad"]):
        pads.append({"id": "PW%d" % (i + 1), "pad": m, "len": 2 * (pw - f) + 2 * f + 2 * pw})

    # ------------------------------------------------------------ marks (identical parts share a mark)
    def sig(m):
        if m["kind"] in ("pad", "ledge"):
            return (m["kind"], m["section"], round(m["cut"], 1))
        a = m["axis"]
        cross = [i for i in range(3) if i != a]
        b, c = cross if a != 1 else (2, 0)
        if a == 0:
            b, c = 1, 2
        elif a == 2:
            b, c = 0, 1
        idx = {(b, 1): 0, (c, 1): 1, (b, -1): 2, (c, -1): 3}
        L = round(m["cut"], 1)
        hs = [(h["s"], idx[(h["k"], h["sg"])]) for h in m["holes"]]
        best = None
        for flip in (False, True):
            for r in range(4):
                t = sorted((round(L - sx if flip else sx, 1), ((-i if flip else i) + r) % 4) for sx, i in hs)
                t = tuple(t)
                best = t if best is None or t < best else best
        return (m["kind"] if m["kind"] != "rail" else ("rail_y" if a == 1 else "rail_x"), m["section"], L, best)

    prefix = {"post": "P", "rail_y": "S", "rail_x": "C", "upright": "U", "ledge": "F", "pad": "PL", "spacer": "RS"}
    groups = OrderedDict()
    for m in members:
        groups.setdefault(sig(m), []).append(m)
    order_kind = ["post", "rail_y", "rail_x", "upright", "spacer", "ledge", "pad"]

    def gkey(item):
        sg, ms = item
        lvl = min(ms, key=lambda q: q["min"][2])["min"][2]
        return (order_kind.index(sg[0]), -sg[2], lvl, len(sg[3]) if len(sg) > 3 else 0)

    marks = OrderedDict()
    counters = {}
    for sg, ms in sorted(groups.items(), key=gkey):
        pre = prefix[sg[0]]
        counters[pre] = counters.get(pre, 0) + 1
        mark = "%s%d" % (pre, counters[pre])
        for m in ms:
            m["mark"] = mark
        marks[mark] = ms
    marks["PL%d" % (counters.get("PL", 0) + 1)] = []           # post caps (plate, no model part)
    cap_mark = list(marks)[-1]

    # ------------------------------------------------------------ nesting (first-fit decreasing)
    def nest(pieces, stock, kerf, trim):
        bars = []
        for mark, L in sorted(pieces, key=lambda q: -q[1]):
            for b in bars:
                if b["used"] + L + kerf <= stock + 1e-6:
                    b["pieces"].append((mark, L))
                    b["used"] += L + kerf
                    break
            else:
                bars.append({"pieces": [(mark, L)], "used": trim + L + kerf})
        for b in bars:
            b["offcut"] = stock - b["used"]
        return bars

    shs_pieces = [(m["mark"], m["cut"]) for m in members if m["kind"] in ("post", "rail", "upright", "spacer")]
    fb_pieces = [(m["mark"], m["cut"]) for m in members if m["kind"] == "ledge"]
    nest_shs = nest(shs_pieces, F["stock_shs"], F["kerf"], F["trim"])
    nest_fb = nest(fb_pieces, F["stock_fb"], F["kerf"], F["trim"])

    # ------------------------------------------------------------ totals
    welded = [m for m in members if m["kind"] != "spacer"]
    cap_mass = f * f * F["cap_t"] * STEEL
    weld_len = sum(j["len"] for j in joints) + sum(w["len"] for w in ledge_welds) + \
        sum(c["len"] for c in caps) + sum(p["len"] for p in pads)
    weld_metal = weld_len * (F["fillet"] ** 2 / 2.0 * 1.2) * STEEL
    totals = {
        "shs_m_welded": sum(m["cut"] for m in welded if m["section"] == sec_shs) / 1000.0,
        "shs_m_spacers": sum(m["cut"] for m in members if m["kind"] == "spacer") / 1000.0,
        "fb_m": sum(m["cut"] for m in members if m["kind"] == "ledge") / 1000.0,
        "mass_weldment_kg": sum(m["mass"] for m in welded) + 4 * cap_mass + weld_metal,
        "mass_spacers_kg": sum(m["mass"] for m in members if m["kind"] == "spacer"),
        "rivnuts": sum(len(m["holes"]) for m in members),
        "tapped_m8": sum(len(m.get("taps", [])) for m in members),
        "joints_shs": len(joints),
        "weld_len_m": weld_len / 1000.0,
        "weld_metal_kg": weld_metal,
        "cuts_shs": len(shs_pieces),
        "cuts_fb": len(fb_pieces),
    }

    frame_outer = (bound[0][1] - bound[0][0], bound[1][1] - bound[1][0], bound[2][1] - bound[2][0])
    return {"P": P, "D": D, "F": F, "org": org, "bound": bound, "frame_outer": frame_outer,
            "shs": shs, "sec_shs": sec_shs, "members": members, "joints": joints, "seq": seqd,
            "ledges": ledge_welds, "caps": caps, "pads": pads, "marks": marks, "cap_mark": cap_mark,
            "cap_mass": cap_mass, "nest_shs": nest_shs, "nest_fb": nest_fb, "totals": totals}


def local(wm, p):
    """Model point -> frame-local (datums C, B, A)."""
    o = wm["org"]
    return tuple(round(p[i] - o[i], 1) for i in range(3))


def location(m):
    """Human-readable position of a member in the frame."""
    n = m["name"]
    return (n.replace("Post ", "post ").replace("Rail ", "").replace("Upright ", "upright ")
            .replace("Ledge ", "").replace("Castor pad ", "corner ").replace("Rail spacer ", "spacer "))


def check(wm):
    """Sanity checks on the fabrication model; returns a list of problems."""
    probs = []
    for m in wm["members"]:
        hs = sorted(m["holes"], key=lambda h: h["s"])
        for i in range(len(hs)):
            for j in range(i + 1, len(hs)):
                if hs[i]["face"] != hs[j]["face"] and abs(hs[i]["s"] - hs[j]["s"]) < wm["F"]["clash"] - 0.1:
                    probs.append("%s: rivnuts on %s/%s only %.1f mm apart" %
                                 (m["name"], hs[i]["face"], hs[j]["face"], abs(hs[i]["s"] - hs[j]["s"])))
        for h in m["holes"]:
            if not (-0.1 <= h["s"] <= m["max"][m["axis"]] - m["min"][m["axis"]] + 0.1):
                probs.append("%s: hole outside member" % m["name"])
    n_seams = sum(len(j["seams"]) for j in wm["joints"])
    if n_seams != 4 * len(wm["joints"]):
        probs.append("joint seam count mismatch")
    for m in wm["members"]:
        if m["kind"] in ("rail", "upright") and not any(j["m"] is m for j in wm["joints"]):
            probs.append("%s has no welded end" % m["name"])
    return probs


if __name__ == "__main__":
    wm = build()
    t = wm["totals"]
    print("frame %s, outer %.0f x %.0f x %.1f" % ((wm["sec_shs"],) + wm["frame_outer"]))
    for mk, ms in wm["marks"].items():
        if ms:
            print("  %-4s x%-2d %-16s %8.1f  holes %-3d %s" % (mk, len(ms), ms[0]["section"], ms[0]["cut"],
                                                          len(ms[0]["holes"]), ", ".join(location(m) for m in ms)))
    print("joints:", ", ".join("%s(%d)" % (st, len(js)) for st, js in wm["seq"].items()))
    print("SHS bars %d x %.1f m, FB bars %d" % (len(wm["nest_shs"]), wm["F"]["stock_shs"] / 1000, len(wm["nest_fb"])))
    for k, v in t.items():
        print("  %-18s %s" % (k, round(v, 2) if isinstance(v, float) else v))
    print("check:", check(wm) or "OK")
