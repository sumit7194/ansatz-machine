#!/usr/bin/env python3
"""Read-only status dashboard for long unattended runs (VM practice).

Serves one auto-refreshing HTML page on PORT (default 8080) showing:
running hunts, tails of every *.log in the repo root, the discovery
catalog, the latest journal entry, and the last gate verdict.

Security model: READ-ONLY (no exec endpoints, no query handling beyond
GET /), meant to sit behind a GCP firewall rule scoped to one source IP
(see docs/VM.md). Standard library only — no new dependencies.

Run:  nohup .venv/bin/python scripts/dashboard.py >/dev/null 2>&1 &
"""

import glob
import html
import json
import os
import subprocess
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = int(os.environ.get("PORT", "8080"))
TAIL_LINES = 25


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


def _running_hunts():
    try:
        out = subprocess.run(["ps", "axo", "pid,etime,%cpu,command"],
                             capture_output=True, text=True,
                             timeout=5).stdout
    except Exception:
        return []
    return [ln for ln in out.splitlines()
            if "scripts/0" in ln and "python" in ln.lower()
            and "dashboard" not in ln]


def _section(title, body):
    return f"<h2>{html.escape(title)}</h2>\n{body}\n"


def _pre(lines):
    return ("<pre>" + html.escape("\n".join(lines)) + "</pre>") if lines \
        else "<p><em>nothing</em></p>"


def render():
    parts = [
        "<!doctype html><meta charset='utf-8'>",
        "<meta http-equiv='refresh' content='30'>",
        "<title>ansatz-machine status</title>",
        "<style>body{font-family:ui-monospace,monospace;margin:2em;"
        "background:#111;color:#ddd;max-width:1100px}h1,h2{color:#7fd}"
        "pre{background:#1b1b1b;padding:1em;overflow-x:auto;"
        "border-radius:6px}table{border-collapse:collapse}"
        "td,th{border:1px solid #333;padding:4px 10px}</style>",
        f"<h1>ansatz-machine</h1><p>{time.strftime('%Y-%m-%d %H:%M:%S')}"
        f" · host {html.escape(os.uname().nodename)} · refresh 30s</p>",
    ]

    parts.append(_section("running hunts", _pre(_running_hunts())))

    logs = sorted(glob.glob(os.path.join(ROOT, "*.log")),
                  key=os.path.getmtime, reverse=True)
    for lg in logs[:4]:
        age = int(time.time() - os.path.getmtime(lg))
        parts.append(_section(f"{os.path.basename(lg)} (updated {age}s ago)",
                              _pre(_tail(lg))))

    cat_path = os.path.join(ROOT, "catalog_discoveries.json")
    if os.path.exists(cat_path):
        try:
            with open(cat_path) as fh:
                entries = json.load(fh)
            rows = "".join(
                f"<tr><td>{html.escape(e['name'])}</td>"
                f"<td>{html.escape(e.get('provenance', ''))}</td></tr>"
                for e in entries)
            parts.append(_section(
                f"discovery catalog ({len(entries)} families)",
                f"<table><tr><th>family</th><th>provenance</th></tr>"
                f"{rows}</table>"))
        except Exception:
            parts.append(_section("discovery catalog", "<p>unreadable</p>"))

    journal = os.path.join(ROOT, "docs", "JOURNAL.md")
    if os.path.exists(journal):
        with open(journal) as fh:
            text = fh.read()
        chunks = text.split("\n## ")
        latest = ("## " + chunks[1]) if len(chunks) > 1 else text
        parts.append(_section("latest journal entry",
                              _pre(latest.splitlines()[:30])))

    return "".join(parts)


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
    print(f"dashboard on 0.0.0.0:{PORT} (read-only)")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
