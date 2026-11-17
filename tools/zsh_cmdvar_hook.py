#!/usr/bin/env python3
"""PreToolUse hook on Bash: refuse a command line whose COMMAND WORD is an unquoted variable ($VAR or ${VAR}).
zsh does not word-split unquoted variables, so `N="nice -n 19"; $N python ...` runs a program literally named
"nice -n 19" and silently does nothing. That slip happened three times (p-sweep $J, set -- $m, the 27.2 check $N),
so per fleet practice 2 it gets a mechanism (user-approved 2026-11-17).
Allowed: ${=VAR} (explicit zsh splitting), arrays "${ARR[@]}", and $(...) command substitution.
Exit 2 blocks the call; stderr is shown to Claude."""
import json, re, sys
try:
    cmd = json.load(sys.stdin).get("tool_input", {}).get("command", "")
except Exception:
    sys.exit(0)
seg_split = re.compile(r"\n|;|&&|\|\||\|(?!\|)|\bthen\b|\bdo\b|\belse\b")
bad = re.compile(r"^\s*(?:\w+=\S*\s+)*(?:(?:nohup|nice(?:\s+-n\s*-?\d+)?|time|exec|command)\s+)*"
                 r"(\$[A-Za-z_]\w*|\$\{(?!=)[A-Za-z_]\w*\})(?=\s|$)")
for seg in seg_split.split(cmd):
    m = bad.match(seg)
    if m:
        print(f"zsh command-in-variable guard: '{m.group(1)}' is used as a command word. zsh does not word-split "
              f"unquoted variables, so this runs a program literally named by the whole string and silently does "
              f"nothing useful. Use ${{={m.group(1).strip('${}')}}} (explicit split), an array \"${{ARR[@]}}\", a function, "
              f"or write the command out.", file=sys.stderr)
        sys.exit(2)
sys.exit(0)
