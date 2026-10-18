#!/bin/bash
# PreToolUse hook for SendMessage: block a cross-session message that hits an active embargo (tools/EMBARGOES.json).
# Exit 2 blocks the tool call and shows stderr to Claude. Every invocation is logged (proof the hook fires).
DIR="$(cd "$(dirname "$0")" && pwd)"
IN="$(cat)"
TO="$(printf '%s' "$IN" | /usr/bin/jq -r '.tool_input.to // empty')"
MSG="$(printf '%s' "$IN" | /usr/bin/jq -r '.tool_input.message // empty')"
echo "$(date '+%F %T') to=$TO len=${#MSG}" >> "$HOME/.claude/blind_hook.log"
[ -z "$MSG" ] && exit 0
OUT="$(printf '%s' "$MSG" | /usr/bin/python3 "$DIR/blind_check.py" "$TO" - 2>&1)"
if [ $? -ne 0 ]; then
  echo "$(date '+%F %T') BLOCKED to=$TO" >> "$HOME/.claude/blind_hook.log"
  printf 'Blinding guard (tools/blind_check.py) blocked this message.\n%s\nRemove the embargoed content (or lift the embargo in tools/EMBARGOES.json only if its seal has arrived) and resend.\n' "$OUT" >&2
  exit 2
fi
exit 0
