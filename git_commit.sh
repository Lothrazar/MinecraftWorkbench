#!/bin/bash
# Commit all pending changes in every mod subproject with the same message.
# Usage: ./git_commit.sh this is a message

WORKBENCH="$(cd "$(dirname "$0")" && pwd)"
MSG="$*"

if [ -z "$MSG" ]; then
  echo "Usage: $0 <commit message>"
  exit 1
fi

for dir in "$WORKBENCH"/*/; do
  [ -d "$dir/.git" ] || continue

  name=$(basename "$dir")
  status=$(git -C "$dir" status --porcelain 2>/dev/null)

  if [ -z "$status" ]; then
    continue
  fi

  echo "── $name ──"
  git -C "$dir" add -A
  git -C "$dir" commit -m "$MSG"
  echo ""
done
