"""Tiny resumable-sweep checkpoint (power-loss robustness — recurrent Mac outages kill long sweeps).

Long parameter sweeps write one line per computed point to a DURABLE repo-local file (never /tmp,
which is cleared on reboot), flushed per line; on restart, done keys are loaded and skipped, so a
sweep resumes where it died at the cost of at most one point.

    done = ckpt_load("data/my_sweep.txt")            # {key: line}
    for x0 in xs:
        key = f"{x0:.3f}"
        if key in done: continue
        ...compute...
        ckpt_add("data/my_sweep.txt", key, f"{key}  {result}")
"""
import os


def ckpt_load(path):
    """load a checkpoint file -> {key: full_line}; key = first whitespace token of each line."""
    done = {}
    if os.path.exists(path):
        with open(path) as fh:
            for line in fh:
                line = line.rstrip("\n")
                if line.strip():
                    done[line.split()[0]] = line
    return done


def ckpt_add(path, key, line):
    """append one result line (flushed + fsynced so a power cut loses at most this point)."""
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "a") as fh:
        fh.write(line.rstrip("\n") + "\n")
        fh.flush()
        os.fsync(fh.fileno())
