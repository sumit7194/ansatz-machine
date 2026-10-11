#!/usr/bin/env python3
"""Figures for section 150 (static SVG, no plotting dependency; reference palette validated: blue = TS, orange = Kerr).
  fig150_sections.svg  Poincare sections (x, p_x at y = 0, p_y > 0), from check3.json: the two strongest full-window
                       TS confirmed orbits (300 crossings, largest complex drift) against the two Kerr candidates with
                       the largest S_ex (the Kerr orbits that came closest to fooling the stretching detector).
  fig150_alpha.svg     uncertain fraction f(eps), log-log, per level pair: ours (filled, solid) and the Bridge V12
                       (hollow, dashed; hit counts relayed, K = 2000), with an alpha = 1 guide.
    .venv/bin/python scripts/_ts_chaos_figures.py
"""
import json
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "ts_chaos")
BLUE, ORANGE = "#2a78d6", "#eb6834"
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
FONT = "font-family='Helvetica, Arial, sans-serif'"


def svg_open(w, h):
    return [f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}' viewBox='0 0 {w} {h}' {FONT}>",
            f"<rect width='{w}' height='{h}' fill='{SURF}'/>"]


def text(x, y, s, size=12, fill=INK, anchor="start", weight="normal"):
    s = s.replace("&", "&amp;").replace("<", "&lt;")
    return f"<text x='{x:.1f}' y='{y:.1f}' font-size='{size}' fill='{fill}' text-anchor='{anchor}' font-weight='{weight}'>{s}</text>"


def nice_ticks(lo, hi, n=4):
    span = hi - lo
    step = 10 ** math.floor(math.log10(span / n))
    for m in (1, 2, 5, 10):
        if span / (m * step) <= n:
            step *= m
            break
    t = math.ceil(lo / step) * step
    out = []
    while t <= hi + 1e-12:
        out.append(round(t, 10))
        t += step
    return out


def panel_scatter(out, x0, y0, w, h, xs, ps, color, title, sub):
    lox, hix = min(xs), max(xs)
    lop, hip = min(ps), max(ps)
    padx, padp = 0.06 * (hix - lox or 1), 0.08 * (hip - lop or 1)
    lox, hix, lop, hip = lox - padx, hix + padx, lop - padp, hip + padp
    X = lambda v: x0 + (v - lox) / (hix - lox) * w
    Y = lambda v: y0 + h - (v - lop) / (hip - lop) * h
    for t in nice_ticks(lox, hix):
        out.append(f"<line x1='{X(t):.1f}' y1='{y0}' x2='{X(t):.1f}' y2='{y0 + h}' stroke='{GRID}' stroke-width='1'/>")
        out.append(text(X(t), y0 + h + 14, f"{t:g}", 10, INK2, "middle"))
    for t in nice_ticks(lop, hip):
        out.append(f"<line x1='{x0}' y1='{Y(t):.1f}' x2='{x0 + w}' y2='{Y(t):.1f}' stroke='{GRID}' stroke-width='1'/>")
        out.append(text(x0 - 5, Y(t) + 3, f"{t:g}", 10, INK2, "end"))
    for a, b in zip(xs, ps):
        out.append(f"<circle cx='{X(a):.2f}' cy='{Y(b):.2f}' r='1.6' fill='{color}' fill-opacity='0.85'/>")
    out.append(text(x0, y0 - 22, title, 12, INK, weight="bold"))
    out.append(text(x0, y0 - 8, sub, 10, INK2))
    out.append(text(x0 + w / 2, y0 + h + 28, "x (prolate)", 10, INK2, "middle"))
    out.append(f"<text x='{x0 - 34:.1f}' y='{y0 + h / 2:.1f}' font-size='10' fill='{INK2}' text-anchor='middle' "
               f"transform='rotate(-90 {x0 - 34:.1f} {y0 + h / 2:.1f})'>p_x</text>")


def fig_sections():
    d = json.load(open(os.path.join(D, "check3.json")))
    ts = sorted([o for o in d if o["label"] == "TS-confirmed" and o["n"] == 300], key=lambda o: -o["cdrift"])[:2]
    kc = sorted([o for o in d if o["label"] == "Kerr-candidate" and o["n"] == 300], key=lambda o: -o["sex"])[:2]
    W, H, pw, ph = 900, 690, 330, 210
    out = svg_open(W, H)
    out.append(text(30, 30, "Poincaré sections do NOT discriminate at 300 crossings: chaotic TS and regular Kerr look alike", 15, weight="bold"))
    out.append(text(30, 48, "One orbit per panel, 300 crossings, tol 1e-13. TS (blue): confirmed chaotic by fd + S_ex + complex drift. "
                    "Kerr (orange): regular controls with the largest S_ex.", 11, INK2))
    out.append(text(30, 64, "The chaotic layers are thin, so a 300-crossing section traces a near-curve. This is why sections alone", 11, INK2))
    out.append(text(30, 80, "(as in Dubeibe et al. 2007) read regular. The discriminating views: fig150_fate.svg, fig150_alpha.svg.", 11, INK2))
    for i, o in enumerate(ts + kc):
        col, row = i % 2, i // 2
        x0, y0 = 90 + col * 420, 140 + row * 280
        sysname = {"ts45": "TS p=4/5", "ts35": "TS p=3/5", "kerr45": "Kerr p=4/5", "kerr35": "Kerr p=3/5"}[o["system"]]
        color = BLUE if o["system"].startswith("ts") else ORANGE
        verdict = "confirmed chaotic" if o["system"].startswith("ts") else "regular (control)"
        panel_scatter(out, x0, y0, pw, ph, o["secx"], o["secpx"], color, f"{sysname}: {verdict}",
                      f"E={o['E']}, L={o['L']:.4f}, x0={o['x0']:.5f}; complex drift {o['cdrift']:.4f}, S_ex {o['sex']:.1f}")
    out.append("</svg>")
    open(os.path.join(D, "fig150_sections.svg"), "w").write("\n".join(out))
    return [(o["system"], o["E"], o["L"], o["x0"]) for o in ts + kc]


V12 = {  # relayed by the Bridge (sealed TheBridge e7e0414), hits out of K = 2000 at eps = 3e-3 .. 3e-5; only where all 5 were given
    "L1": {"TS": [1040, 1007, 951, 908, 849], "Kerr": [404, 129, 40, 14, 6]},
}
EPS = [3e-3, 1e-3, 3e-4, 1e-4, 3e-5]


def fig_alpha():
    pairs = [("L1  p=4/5 E=0.97 L=+5.125 (retrograde)", "alpha.json", "L1"),
             ("L2  p=4/5 E=0.97 L=+5.875 (retrograde)", "alpha_p45b.json", "L2"),
             ("L3  p=3/5 E=0.95 L=-5.333 (prograde), W=0.03", "alpha_p35w.json", "L3")]
    W, H, pw, ph = 1040, 460, 270, 260
    out = svg_open(W, H)
    out.append(text(30, 30, "Uncertainty exponent: fraction of start points whose fate flips under a nudge ε", 15, weight="bold"))
    out.append(text(30, 48, "f ∝ ε^α. Smooth boundary (integrable): α = 1 (dotted guide). Fractal boundary (chaotic): α ≪ 1. "
                    "300 crossings, tol 1e-11.", 11, INK2))
    out.append(text(30, 64, "Compare SLOPES, not heights: f scales with 1/(window width), and V12's Kerr window (0.03) is wider "
                    "than ours at L1 (0.0064).", 11, INK2))
    lx0, lx1, ly0, ly1 = math.log10(2e-5), math.log10(5e-3), math.log10(3e-4), 0.0
    for k, (title, fn, lab) in enumerate(pairs):
        x0, y0 = 80 + k * 330, 120
        X = lambda v: x0 + (math.log10(v) - lx0) / (lx1 - lx0) * pw
        Y = lambda v: y0 + ph - (math.log10(v) - ly0) / (ly1 - ly0) * ph
        for e in (1e-4, 1e-3):
            out.append(f"<line x1='{X(e):.1f}' y1='{y0}' x2='{X(e):.1f}' y2='{y0 + ph}' stroke='{GRID}'/>")
            out.append(text(X(e), y0 + ph + 14, f"{e:g}", 10, INK2, "middle"))
        for f in (1e-3, 1e-2, 1e-1, 1):
            out.append(f"<line x1='{x0}' y1='{Y(f):.1f}' x2='{x0 + pw}' y2='{Y(f):.1f}' stroke='{GRID}'/>")
            out.append(text(x0 - 5, Y(f) + 3, f"{f:g}", 10, INK2, "end"))
        # alpha = 1 guide through the Kerr point at eps = 1e-3
        d = json.load(open(os.path.join(D, fn)))
        series = {}
        for s, v in d.items():
            a = v["analysis"]
            series["TS" if s.startswith("ts") else "Kerr"] = (a["hits"], a["n_valid"], a["alpha"], a["ci95"])
        kh, kn = series["Kerr"][0], series["Kerr"][1]
        fk = kh[1] / kn
        e_a, e_b = 2e-5, 5e-3
        out.append(f"<line x1='{X(e_a):.1f}' y1='{Y(max(fk * e_a / 1e-3, 3e-4)):.1f}' x2='{X(e_b):.1f}' y2='{Y(min(fk * e_b / 1e-3, 1)):.1f}' "
                   f"stroke='{INK2}' stroke-width='1' stroke-dasharray='1,3'/>")
        for name, color in (("TS", BLUE), ("Kerr", ORANGE)):
            h, n, al, ci = series[name]
            pts = [(e, c / n) for e, c in zip(EPS, h) if c > 0]
            out.append("<polyline fill='none' stroke='{}' stroke-width='2' points='{}'/>".format(
                color, " ".join(f"{X(e):.1f},{Y(f):.1f}" for e, f in pts)))
            for e, f in pts:
                out.append(f"<circle cx='{X(e):.1f}' cy='{Y(f):.1f}' r='4' fill='{color}' stroke='{SURF}' stroke-width='2'/>")
            if lab in V12:
                vp = [(e, c / 2000) for e, c in zip(EPS, V12[lab][name]) if c > 0]
                out.append("<polyline fill='none' stroke='{}' stroke-width='1.5' stroke-dasharray='4,3' points='{}'/>".format(
                    color, " ".join(f"{X(e):.1f},{Y(f):.1f}" for e, f in vp)))
                for e, f in vp:
                    out.append(f"<circle cx='{X(e):.1f}' cy='{Y(f):.1f}' r='4' fill='{SURF}' stroke='{color}' stroke-width='2'/>")
            lx, ly = pts[-1]
            out.append(text(X(lx) - 6, Y(ly) + (16 if name == "Kerr" else -9), f"{name} α={al:.3f} [{ci[0]:.2f}, {ci[1]:.2f}]",
                            10, INK, "start" if name == "TS" else "start"))
        out.append(text(x0, y0 - 10, title, 11, INK, weight="bold"))
        out.append(text(x0 + pw / 2, y0 + ph + 30, "nudge ε (log)", 10, INK2, "middle"))
        out.append(f"<text x='{x0 - 40:.1f}' y='{y0 + ph / 2:.1f}' font-size='10' fill='{INK2}' text-anchor='middle' "
                   f"transform='rotate(-90 {x0 - 40:.1f} {y0 + ph / 2:.1f})'>uncertain fraction f (log)</text>")
    # legend
    ly = H - 28
    out.append(f"<circle cx='90' cy='{ly}' r='4' fill='{BLUE}'/>" + text(100, ly + 4, "Tomimatsu–Sato δ=2 (this repo)", 11))
    out.append(f"<circle cx='320' cy='{ly}' r='4' fill='{ORANGE}'/>" + text(330, ly + 4, "Kerr, separatrix-matched (this repo)", 11))
    out.append(f"<circle cx='580' cy='{ly}' r='4' fill='{SURF}' stroke='{INK2}' stroke-width='2'/>"
               + text(590, ly + 4, "hollow, dashed: the Bridge V12, independent code (L1; relayed)", 11, INK2))
    out.append("</svg>")
    open(os.path.join(D, "fig150_alpha.svg"), "w").write("\n".join(out))


def fig_fate():
    """Outcome (survive / plunge) of every sampled start point across the window, L1 pair, plus a 10x zoom of TS."""
    d = json.load(open(os.path.join(D, "alpha.json")))
    W, H = 1000, 470
    out = svg_open(W, H)
    out.append(text(30, 30, "Fate map: which start points survive 300 crossings and which plunge (L1, p=4/5, E=0.97)", 15, weight="bold"))
    out.append(text(30, 48, "One tick per sampled start x0 (1500 per window, uniform). Up = survives, down = plunges. "
                    "Kerr: one clean switch. TS: interleaved at every scale shown.", 11, INK2))
    rows = []
    for s_, v in d.items():
        W0, W1 = v["analysis"]["W"]
        pts = sorted((x["x0"], x["c"]) for x in v["samples"] if x["c"] in (0, 1, 2))
        rows.append((s_, W0, W1, pts))
    rows.sort(key=lambda r: 0 if r[0].startswith("kerr") else 1)
    ts = [r for r in rows if r[0].startswith("ts")][0]
    zc = 0.5 * (ts[1] + ts[2]); zw = (ts[2] - ts[1]) / 10
    rows.append(("ts45-zoom", zc - zw / 2, zc + zw / 2, [p for p in ts[3] if zc - zw / 2 <= p[0] <= zc + zw / 2]))
    labels = {"kerr45": ("Kerr p=4/5, matched L=+2.5503", ORANGE), "ts45": ("TS p=4/5, L=+5.125", BLUE),
              "ts45-zoom": ("TS, the central 10% of its window, magnified 10x", BLUE)}
    for i, (s_, a, b, pts) in enumerate(rows):
        x0, y0, w, h = 90, 95 + i * 125, 860, 70
        lab, col = labels[s_]
        X = lambda v: x0 + (v - a) / (b - a) * w
        out.append(f"<line x1='{x0}' y1='{y0 + h / 2}' x2='{x0 + w}' y2='{y0 + h / 2}' stroke='{GRID}'/>")
        for xv, c in pts:
            yy0, yy1 = (y0, y0 + h / 2 - 3) if c == 0 else (y0 + h / 2 + 3, y0 + h)
            out.append(f"<line x1='{X(xv):.2f}' y1='{yy0:.1f}' x2='{X(xv):.2f}' y2='{yy1:.1f}' stroke='{col}' stroke-width='1'/>")
        nsw = sum(1 for p, q in zip(pts, pts[1:]) if p[1] != q[1])
        out.append(text(x0, y0 - 8, f"{lab}   ({len(pts)} start points, {nsw} survive/plunge switches)", 11, INK, weight="bold"))
        out.append(text(x0 - 8, y0 + 12, "survive", 10, INK2, "end"))
        out.append(text(x0 - 8, y0 + h - 2, "plunge", 10, INK2, "end"))
        out.append(text(x0, y0 + h + 14, f"x0 = {a:.5f}", 10, INK2))
        out.append(text(x0 + w, y0 + h + 14, f"{b:.5f}  (width {b - a:.2e})", 10, INK2, "end"))
    out.append("</svg>")
    open(os.path.join(D, "fig150_fate.svg"), "w").write("\n".join(out))


if __name__ == "__main__":
    fig_fate()
    print("sections:", fig_sections())
    fig_alpha()
    print("wrote data/ts_chaos/fig150_sections.svg, fig150_alpha.svg, fig150_fate.svg")
