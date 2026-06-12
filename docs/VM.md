# Running on a VM (long unattended hunts)

The machine is 100% CPU-bound, single-core per hunt, ~tens of MB RAM,
stdlib + SymPy only — it coexists politely with anything else on the box
when niced. Standing practice: **every long VM run gets the read-only
dashboard, firewalled to Sumit's IP.**

## Bring-up

```bash
git clone https://github.com/sumit7194/ansatz-machine.git && cd ansatz-machine
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
nice -n 19 setsid bash -c './verify.sh >> gate.log 2>&1' & disown   # prove green first
```

## Long runs

```bash
# always: nice (lowest priority — other workloads keep their cores),
# setsid/disown (survives SSH drops), -u + logfile in repo root
# (the dashboard tails *.log here; /tmp does not survive reboots)
nice -n 19 setsid bash -c \
  '.venv/bin/python -u scripts/07_expedition.py >> expedition.log 2>&1' & disown
```

Parallel seeds/rungs are separate single-core processes — with N idle
cores, run N hunts (`xargs -P`), still niced.

## Dashboard (the standing practice)

```bash
nice -n 19 setsid bash -c \
  '.venv/bin/python scripts/dashboard.py >> dashboard.log 2>&1' & disown
```

Serves `http://<VM_EXTERNAL_IP>:8080` — running hunts, log tails, the
discovery catalog, latest journal entry. Read-only by construction (no
exec endpoints); still, scope the firewall to one IP:

```bash
# one-time, from any gcloud-authed shell; find your IP: curl ifconfig.me
gcloud compute firewall-rules create ansatz-dashboard \
  --allow=tcp:8080 --direction=INGRESS \
  --source-ranges=<YOUR_IP>/32 \
  --target-tags=<VM_TAG>          # and: gcloud compute instances add-tags <VM> --tags=<VM_TAG>
# IP changed? update instead of recreate:
gcloud compute firewall-rules update ansatz-dashboard --source-ranges=<NEW_IP>/32
```

Never use `--source-ranges=0.0.0.0/0`.

## Division of labor

Mac = dev/edit host (push from here). VM = run host (pull + run + serve
dashboard). The repo is the only transport: code, catalog memory, docs
all travel through git.

## The pkill self-match trap (measured 2026-06-12)

Much of the "flaky ssh, exit 255" history was not the network: a
`pkill -f <script>.py` inside a `gcloud compute ssh --command='...'`
matches the remote wrapper shell's OWN command line (the pattern — or a
relaunch line mentioning the same script — appears in it literally),
kills it, and the connection drops with 255. This is what killed
`auto_pipeline.sh`'s expedition launch.

Rules:
- Long jobs run in **named tmux sessions** (`tmux new-session -d -s NAME
  '...'`) — they survive drops AND are killable by session name, no
  pkill needed.
- If pkill is unavoidable, put kill and launch in SEPARATE ssh calls and
  assemble the pattern at runtime so it never appears literally:
  `P="dash"; P="${P}board.py"; pkill -f "$P"`.
