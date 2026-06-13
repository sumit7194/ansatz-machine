#!/usr/bin/env python3
"""Read-only status panel for long unattended runs (the project dashboard).

Named ansatz_status.py (not dashboard.py) on purpose: other projects on
the same machine run their own dashboard.py, and a cross-project
`pkill -f dashboard.py` was killing ours. The filename here contains no
"dashboard" substring so a generic kill from another project can't match.

Serves one auto-refreshing HTML page on PORT (default 8080): an overview
band (machine state, catalog size, gate verdict, live hunts), a plain-
English "what's happening" card, the running hunts, the parsed gate
batteries, the discovery catalog, recent log tails, latest journal entry.

Security model: READ-ONLY (no exec endpoints, no query handling beyond
GET /), meant to sit behind a GCP firewall rule scoped to one source IP
(see docs/VM.md). Standard library only — no new dependencies.

Run:  nohup .venv/bin/python scripts/ansatz_status.py >/dev/null 2>&1 &
"""

import glob
import html
import json
import os
import re
import subprocess
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = int(os.environ.get("PORT", "8080"))
HOST = os.environ.get("HOST", "0.0.0.0")
TAIL_LINES = 22
REFRESH = 30

# --- data gathering -------------------------------------------------------

_HUNT_RE = re.compile(r"scripts/[A-Za-z0-9_]+\.py")
_GATE_RE = re.compile(r"(PASS|FAIL)\s+(\d+\s+.+?)\s+\((\d+)s\)")
_SECS_RE = re.compile(r"\((\d+(?:\.\d+)?)s\)")
_FRAC_RE = re.compile(r"\[(\d+)/(\d+)\]")  # explicit "i of N" progress

# Long-running jobs the dashboard can narrate in plain English:
# script name -> friendly title, one-line description, log file in ROOT,
# per-step "done" marker, expected total steps.
JOBS = {
    "23_ladder_oracle.py": {
        "title": "Ladder oracle",
        "plain": "proving the predicted formula on each rung directly — "
                 "no searching, each ✅ is a finished theorem",
        "log": "oracle.log",
        "done_re": re.compile(r"^\s*(✅|✓|❌)"),
        "total": 15,
    },
    "98_blind_crosscheck.py": {
        "title": "Blind cross-check",
        "plain": "hunting with catalog memory switched OFF, then grading "
                 "each find against the proved families — a mismatch would "
                 "be big news",
        "log": "blind_crosscheck.log",
        "done_re": re.compile(r"^\s*(MATCH|⚠ UNEXPECTED|NULL)"),
        "total": 15,
    },
    "99_ladder_high.py": {
        "title": "High-ladder hunt",
        "plain": "genetic search across uncharted high-dimension rungs",
        "log": "ladder_high.log",
        "done_re": re.compile(r"^\s*(GREW|KNOWN|NULL|GROWTH FAILED)"),
        "total": 15,
    },
    "cache_profiles.py": {
        "title": "Caching fingerprints",
        "plain": "computing each proved family's curvature fingerprint so "
                 "recognition is instant later — the slow one-time step",
        "log": "cache.log",
        "done_re": re.compile(r"^\s*\[\d+/\d+\]"),
        "total": 15,
    },
}


def _job_progress(spec):
    """(done, total, last_line, eta_s) parsed from the job's log.

    Steps are counted as DISTINCT rung labels (the text between the
    done-marker and the first ':'), so a log that accumulates output
    from restarts — including 'skipping' lines — never double-counts."""
    path = os.path.join(ROOT, spec["log"])
    labels, last, secs = set(), "", []
    frac = None  # explicit "i of N" if the log prints it
    total = spec["total"]
    for ln in _tail(path, 400):
        m = spec["done_re"].match(ln)
        if m:
            labels.add(ln[m.end():].split(":", 1)[0].strip())
            last = ln.strip()
            t = _SECS_RE.search(ln)
            if t:
                secs.append(float(t.group(1)))
            fm = _FRAC_RE.search(ln)
            if fm:
                frac, total = int(fm.group(1)), int(fm.group(2))
    # prefer the explicit counter (robust when every step shares a label);
    # else count distinct labels (robust to restarts re-logging old steps)
    done = frac if frac is not None else len(labels)
    eta = None
    remaining = total - done
    if secs and remaining > 0:
        eta = int(sum(secs[-3:]) / len(secs[-3:]) * remaining)
    return done, total, last, eta


def _tail(path, n=TAIL_LINES):
    try:
        with open(path, "rb") as fh:
            fh.seek(0, os.SEEK_END)
            size = fh.tell()
            fh.seek(max(0, size - 64 * 1024))
            lines = fh.read().decode("utf-8", "replace").splitlines()
        return lines[-n:]
    except OSError:
        return []


def _repo_logs():
    """(path, mtime) for readable *.log files in ROOT, newest first.
    Skips dangling symlinks / vanished files — a log can disappear
    between glob and stat (e.g. a /tmp target wiped by a reboot), and
    one dead file must never crash the whole page."""
    out = []
    for p in glob.glob(os.path.join(ROOT, "*.log")):
        try:
            out.append((p, os.path.getmtime(p)))
        except OSError:
            continue
    return sorted(out, key=lambda x: x[1], reverse=True)


def _running_hunts():
    """Return [(pid, elapsed, cpu, script), ...] for numbered hunt scripts."""
    try:
        out = subprocess.run(["ps", "axo", "pid,etime,%cpu,command"],
                             capture_output=True, text=True,
                             timeout=5).stdout
    except Exception:
        return []
    hunts = []
    for ln in out.splitlines():
        if not _HUNT_RE.search(ln) or "python" not in ln.lower():
            continue
        if "ansatz_status" in ln:  # never list this status server itself
            continue
        parts = ln.split(None, 3)
        if len(parts) < 4:
            continue
        pid, etime, cpu, cmd = parts
        m = re.search(r"scripts/([A-Za-z0-9_]+\.py)", cmd)
        script = m.group(1) if m else cmd[:48]
        # only THIS repo's scripts — other projects also keep numbered
        # scripts in a scripts/ dir and would otherwise be miscounted
        if m and not os.path.exists(os.path.join(ROOT, "scripts", script)):
            continue
        hunts.append((pid, etime, cpu, script))
    return _collapse_workers(hunts)


def _collapse_workers(hunts):
    """One parallel job forks many same-script worker processes; show it
    as a SINGLE hunt (summed CPU, longest elapsed, worker count) instead
    of N identical rows that read as N separate jobs."""
    groups = {}
    for pid, etime, cpu, script in hunts:
        g = groups.setdefault(script, {"pids": [], "etime": etime,
                                       "cpu": 0.0})
        g["pids"].append(pid)
        try:
            g["cpu"] += float(cpu)
        except ValueError:
            pass
        if len(etime) > len(g["etime"]):  # longest elapsed wins
            g["etime"] = etime
    out = []
    for script, g in groups.items():
        n = len(g["pids"])
        cpu = f"{g['cpu']:.0f}" + (f" ×{n}" if n > 1 else "")
        out.append((g["pids"][0], g["etime"], cpu, script))
    return out


def _gate():
    """Parse the newest gate.log into (batteries, verdict, age_s).

    batteries = [(status, label, secs), ...]; verdict in
    {GREEN, FAIL, RUNNING, None}.
    """
    path = os.path.join(ROOT, "gate.log")
    if not os.path.exists(path):
        return [], None, None
    age = int(time.time() - os.path.getmtime(path))
    try:
        text = open(path, "r", encoding="utf-8", errors="replace").read()
    except OSError:
        return [], None, age
    batteries = [(m.group(1), m.group(2).strip(), int(m.group(3)))
                 for m in _GATE_RE.finditer(text)]
    if "ALL GREEN" in text:
        verdict = "GREEN"
    elif "FAIL" in text or "GATE_EXIT" in text and "GATE_EXIT=0" not in text:
        verdict = "FAIL"
    elif batteries:
        verdict = "RUNNING"
    else:
        verdict = None
    return batteries, verdict, age


def _catalog():
    path = os.path.join(ROOT, "catalog_discoveries.json")
    if not os.path.exists(path):
        return []
    try:
        return json.load(open(path))
    except Exception:
        return []


def _latest_journal():
    path = os.path.join(ROOT, "docs", "JOURNAL.md")
    if not os.path.exists(path):
        return []
    text = open(path).read()
    chunks = text.split("\n## ")
    latest = ("## " + chunks[1]) if len(chunks) > 1 else text
    return latest.splitlines()[:26]


# --- rendering helpers ----------------------------------------------------

def _fmt_formula(f):
    """light prettify of a sympy formula string for display."""
    return (f.replace("**", "^").replace("*", "·")
            .replace("Lambda", "Λ").replace("sqrt", "√"))


def _freshness(age_s):
    if age_s is None:
        return "idle", "—"
    if age_s < 90:
        cls = "live"
    elif age_s < 3600:
        cls = "warm"
    else:
        cls = "stale"
    if age_s < 90:
        txt = f"{age_s}s ago"
    elif age_s < 3600:
        txt = f"{age_s // 60}m ago"
    else:
        txt = f"{age_s // 3600}h ago"
    return cls, txt


def _esc(s):
    return html.escape(str(s))


def _card(title, body, sub=""):
    sub = f"<span class='sub'>{sub}</span>" if sub else ""
    return (f"<section class='card'><div class='card-h'>"
            f"<h2>{_esc(title)}</h2>{sub}</div>{body}</section>")


def _empty(msg):
    return f"<p class='empty'>{_esc(msg)}</p>"


# --- page -----------------------------------------------------------------

STYLE = """
:root{
  --bg:#0d0f11; --s1:#14171a; --s2:#1b1f23; --bd:#272d33;
  --tx:#e6e9ec; --tm:#9aa3ab; --tl:#6b747c;
  --ok:#3fb950; --run:#d2a322; --err:#f85149; --idle:#56c7d6;
  --accent:#56c7d6; --r:10px;
  --mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;
  --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
}
*{box-sizing:border-box}
body{font-family:var(--sans);background:var(--bg);color:var(--tx);
  margin:0;padding:28px 24px 64px;line-height:1.5;
  -webkit-font-smoothing:antialiased}
.wrap{max-width:1180px;margin:0 auto}
.top{display:flex;align-items:baseline;justify-content:space-between;
  gap:16px;flex-wrap:wrap;margin-bottom:22px}
.top h1{font-size:20px;margin:0;letter-spacing:.3px;font-weight:650}
.top h1 .dot{color:var(--accent)}
.meta{font-family:var(--mono);font-size:12px;color:var(--tl)}
.meta b{color:var(--tm);font-weight:500}
.live-dot{display:inline-block;width:7px;height:7px;border-radius:50%;
  background:var(--ok);margin-right:5px;vertical-align:middle}

.hero{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));
  gap:14px;margin-bottom:24px}
.stat{background:var(--s1);border:1px solid var(--bd);border-radius:var(--r);
  padding:16px 18px}
.stat .k{font-family:var(--mono);font-size:11px;letter-spacing:.6px;
  text-transform:uppercase;color:var(--tl);margin-bottom:8px}
.stat .v{font-size:26px;font-weight:680;font-variant-numeric:tabular-nums;
  line-height:1.1}
.stat .v small{font-size:13px;font-weight:500;color:var(--tm)}
.stat.accent .v{color:var(--accent)}
.stat.ok .v{color:var(--ok)} .stat.run .v{color:var(--run)}
.stat.err .v{color:var(--err)} .stat.idle .v{color:var(--idle)}

.card{background:var(--s1);border:1px solid var(--bd);border-radius:var(--r);
  padding:18px 20px;margin-bottom:18px}
.card-h{display:flex;align-items:baseline;gap:12px;margin-bottom:14px}
.card-h h2{font-size:13px;letter-spacing:.5px;text-transform:uppercase;
  color:var(--tm);margin:0;font-weight:600}
.card-h .sub{font-family:var(--mono);font-size:12px;color:var(--tl);
  margin-left:auto}
.empty{color:var(--tl);font-style:italic;margin:2px 0;font-size:14px}

table{border-collapse:collapse;width:100%;font-size:13px}
th{text-align:left;font-weight:600;color:var(--tl);font-size:11px;
  letter-spacing:.4px;text-transform:uppercase;padding:0 12px 8px;
  border-bottom:1px solid var(--bd)}
td{padding:9px 12px;border-bottom:1px solid var(--s2);vertical-align:top}
tr:last-child td{border-bottom:none}
.mono{font-family:var(--mono);font-variant-numeric:tabular-nums}
.badge{display:inline-block;font-family:var(--mono);font-size:11px;
  padding:2px 7px;border-radius:5px;background:var(--s2);color:var(--tm);
  border:1px solid var(--bd)}

.gate-grid{display:flex;flex-wrap:wrap;gap:8px}
.batt{display:flex;align-items:center;gap:8px;background:var(--s2);
  border:1px solid var(--bd);border-radius:7px;padding:7px 11px;
  font-size:12.5px}
.batt .s{width:7px;height:7px;border-radius:50%}
.batt.pass .s{background:var(--ok)} .batt.fail .s{background:var(--err)}
.batt .t{font-family:var(--mono);color:var(--tl);font-size:11px}
.batt .n{color:var(--tx)}

.tag{display:inline-block;font-family:var(--mono);font-size:11px;
  padding:1px 7px;border-radius:5px;font-weight:600}
.tag.live{background:rgba(63,185,80,.15);color:var(--ok)}
.tag.warm{background:rgba(210,163,34,.15);color:var(--run)}
.tag.stale{background:rgba(107,116,124,.18);color:var(--tl)}

pre{font-family:var(--mono);font-size:12px;line-height:1.55;
  background:var(--s2);border:1px solid var(--bd);border-radius:8px;
  padding:13px 15px;overflow-x:auto;margin:0;color:var(--tm)}
.logs details{margin-bottom:10px}
.logs summary{cursor:pointer;font-family:var(--mono);font-size:12.5px;
  color:var(--tx);padding:4px 0;list-style:none;display:flex;
  align-items:center;gap:10px}
.logs summary::-webkit-details-marker{display:none}
.logs summary::before{content:"▸";color:var(--tl);font-size:10px}
.logs details[open] summary::before{content:"▾"}
.logs summary .nm{font-weight:600}

.now-item{margin-bottom:14px}
.now-item:last-child{margin-bottom:0}
.now-head{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap}
.now-head b{font-size:14.5px}
.now-meta{margin-left:auto;font-size:11.5px;color:var(--tl)}
.now-plain{color:var(--tm);font-size:13px;margin:3px 0 8px}
.now-last{font-size:11.5px;color:var(--tl);margin-top:7px;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bar{height:8px;background:var(--s2);border:1px solid var(--bd);
  border-radius:5px;overflow:hidden}
.bar-fill{height:100%;background:linear-gradient(90deg,var(--accent),
  var(--ok));border-radius:5px;transition:width .6s}
"""


def _hero(catalog, gate_batt, gate_verdict, hunts):
    nfam = len(catalog)
    npass = sum(1 for b in gate_batt if b[0] == "PASS")
    if hunts:
        state_cls, state_v, state_sub = "run", "RUNNING", \
            f"<small>{len(hunts)} hunt{'s' if len(hunts) != 1 else ''}</small>"
    elif gate_verdict == "GREEN":
        state_cls, state_v, state_sub = "ok", "VERIFIED", "<small>idle</small>"
    elif gate_verdict == "FAIL":
        state_cls, state_v, state_sub = "err", "ATTENTION", \
            "<small>gate red</small>"
    else:
        state_cls, state_v, state_sub = "idle", "IDLE", ""
    if gate_verdict == "GREEN":
        g_cls, g_v = "ok", f"ALL GREEN <small>{npass} batteries</small>"
    elif gate_verdict == "FAIL":
        g_cls, g_v = "err", "FAIL"
    elif gate_verdict == "RUNNING":
        g_cls, g_v = "run", f"RUNNING <small>{npass} done</small>"
    else:
        g_cls, g_v = "idle", "—"
    cards = [
        ("stat " + state_cls, "machine", state_v + (
            f" {state_sub}" if state_sub else "")),
        ("stat accent", "catalog", f"{nfam} <small>families</small>"),
        ("stat " + g_cls, "regression gate", g_v),
        ("stat " + ("run" if hunts else "idle"), "live hunts",
         str(len(hunts)) if hunts else "0 <small>idle</small>"),
    ]
    inner = "".join(
        f"<div class='{c}'><div class='k'>{k}</div>"
        f"<div class='v'>{v}</div></div>" for c, k, v in cards)
    return f"<div class='hero'>{inner}</div>"


def _now_card(hunts):
    """Plain-English 'what is happening right now', with progress bars
    for jobs the dashboard knows how to narrate."""
    items = []
    narrated = set()
    for pid, et, cpu, script in hunts:
        spec = JOBS.get(script)
        if not spec or script in narrated:
            continue
        narrated.add(script)
        done, total, last, eta = _job_progress(spec)
        pct = int(100 * done / total) if total else 0
        eta_txt = ""
        if eta:
            eta_txt = (f" · roughly {eta // 3600}h {eta % 3600 // 60}m left"
                       if eta >= 3600 else f" · roughly {eta // 60}m left")
        last_html = (f"<div class='now-last mono'>latest: {_esc(last)}</div>"
                     if last else "")
        items.append(
            f"<div class='now-item'>"
            f"<div class='now-head'><b>{_esc(spec['title'])}</b>"
            f"<span class='now-meta mono'>{done} of {total} done"
            f"{eta_txt} · running {_esc(et)}</span></div>"
            f"<div class='now-plain'>{_esc(spec['plain'])}</div>"
            f"<div class='bar'><div class='bar-fill' style='width:{pct}%'>"
            f"</div></div>{last_html}</div>")
    for pid, et, cpu, script in hunts:
        if script not in narrated and script not in JOBS:
            items.append(
                f"<div class='now-item'><div class='now-head'>"
                f"<b>{_esc(script)}</b><span class='now-meta mono'>running "
                f"{_esc(et)} · cpu {_esc(cpu)}%</span></div></div>")
    if not items:
        logs = _repo_logs()
        if logs:
            newest, mtime = logs[0]
            _, txt = _freshness(int(time.time() - mtime))
            items.append(f"<div class='now-plain'>Nothing running right "
                         f"now. Last activity: {_esc(os.path.basename(newest))}"
                         f", {txt}.</div>")
        else:
            items.append("<div class='now-plain'>Nothing running right now."
                         "</div>")
    return _card("what's happening", "".join(items))


def _hunts_card(hunts):
    if not hunts:
        body = _empty("machine idle — no hunt dispatched")
    else:
        rows = "".join(
            f"<tr><td class='mono'>{_esc(s)}</td>"
            f"<td class='mono'>{_esc(pid)}</td>"
            f"<td class='mono'>{_esc(et)}</td>"
            f"<td class='mono'>{_esc(cpu)}%</td></tr>"
            for pid, et, cpu, s in hunts)
        body = (f"<table><tr><th>script</th><th>pid</th><th>elapsed</th>"
                f"<th>cpu</th></tr>{rows}</table>")
    return _card("running hunts", body)


def _gate_card(batt, verdict, age):
    cls, txt = _freshness(age)
    sub = f"<span class='tag {cls}'>{txt}</span>" if age is not None else ""
    if not batt:
        return _card("regression gate", _empty("no gate run recorded"), sub)
    chips = "".join(
        f"<div class='batt {st.lower()}'><span class='s'></span>"
        f"<span class='n'>{_esc(lbl)}</span>"
        f"<span class='t'>{secs}s</span></div>"
        for st, lbl, secs in batt)
    return _card("regression gate", f"<div class='gate-grid'>{chips}</div>",
                 sub)


def _catalog_card(catalog):
    if not catalog:
        return _card("discovery catalog", _empty("no families yet"))
    rows = []
    for e in catalog:
        n = e.get("n")
        dim = f"{n - 1}+1" if isinstance(n, int) else "—"
        lam = _esc(e.get("Lambda", "—"))
        f = _esc(_fmt_formula(e.get("f", "")))
        nparams = len(e.get("params", []))
        prov = _esc(e.get("provenance", ""))
        rows.append(
            f"<tr><td><span class='badge'>{dim}</span></td>"
            f"<td class='mono'>Λ={lam}</td>"
            f"<td class='mono'>f = {f}</td>"
            f"<td class='mono'>{nparams}</td>"
            f"<td>{prov}</td></tr>")
    body = (f"<table><tr><th>dim</th><th>sector</th><th>metric</th>"
            f"<th>dof</th><th>provenance</th></tr>{''.join(rows)}</table>")
    return _card("discovery catalog", body,
                 f"{len(catalog)} machine-proved families")


def _logs_card():
    logs = _repo_logs()[:6]
    if not logs:
        return _card("recent logs", _empty("no logs in repo root"))
    items = []
    for i, (lg, mtime) in enumerate(logs):
        age = int(time.time() - mtime)
        cls, txt = _freshness(age)
        name = os.path.basename(lg)
        tail = "\n".join(_tail(lg))
        op = " open" if i == 0 else ""
        items.append(
            f"<details{op}><summary><span class='nm'>{_esc(name)}</span>"
            f"<span class='tag {cls}'>{txt}</span></summary>"
            f"<pre>{_esc(tail)}</pre></details>")
    return _card("recent logs", f"<div class='logs'>{''.join(items)}</div>")


def _journal_card():
    lines = _latest_journal()
    if not lines:
        return _card("latest journal entry", _empty("no journal"))
    head = _esc(lines[0].lstrip("# ").strip())
    rest = _esc("\n".join(lines[1:]))
    body = (f"<p style='font-weight:600;color:var(--tx);margin:0 0 10px'>"
            f"{head}</p><pre>{rest}</pre>")
    return _card("latest journal entry", body)


def render():
    catalog = _catalog()
    batt, verdict, gate_age = _gate()
    hunts = _running_hunts()
    body = [
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>",
        "<meta name='viewport' content='width=device-width,initial-scale=1'>",
        f"<meta http-equiv='refresh' content='{REFRESH}'>",
        "<title>ansatz-machine · status</title>",
        f"<style>{STYLE}</style></head><body><div class='wrap'>",
        "<div class='top'><h1><span class='dot'>◆</span> ansatz-machine"
        "</h1>",
        f"<div class='meta'><span class='live-dot'></span>"
        f"<b>{_esc(os.uname().nodename)}</b> · "
        f"{time.strftime('%Y-%m-%d %H:%M:%S')} · refresh {REFRESH}s</div>"
        "</div>",
        _hero(catalog, batt, verdict, hunts),
        _now_card(hunts),
        _hunts_card(hunts),
        _gate_card(batt, verdict, gate_age),
        _catalog_card(catalog),
        _logs_card(),
        _journal_card(),
        "</div></body></html>",
    ]
    return "".join(body)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = render().encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    print(f"dashboard on {HOST}:{PORT} (read-only)")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
