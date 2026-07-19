#!/bin/bash
# Push every mod subproject to its remote.

WORKBENCH="$(cd "$(dirname "$0")" && pwd)"

for dir in "$WORKBENCH"/*/; do
  [ -d "$dir/.git" ] || continue

  name=$(basename "$dir")

  echo "── $name ──"
  git -C "$dir" push
  echo ""
done
