#!/bin/bash
# PreToolUse hook for SendMessage: block a message citing a commit hash that resolves in no fleet repo (tools/hash_check.py).
DIR="$(cd "$(dirname "$0")" && pwd)"
IN="$(cat)"
MSG="$(printf '%s' "$IN" | /usr/bin/jq -r '.tool_input.message // empty')"
[ -z "$MSG" ] && exit 0
OUT="$(printf '%s' "$MSG" | /usr/bin/python3 "$DIR/hash_check.py" - 2>&1)"
if [ $? -ne 0 ]; then
  echo "$(date '+%F %T') HASH-BLOCKED" >> "$HOME/.claude/blind_hook.log"
  printf 'Hash guard (tools/hash_check.py) blocked this message.\n%s\nQuote a hash only after git has printed it.\n' "$OUT" >&2
  exit 2
fi
exit 0
