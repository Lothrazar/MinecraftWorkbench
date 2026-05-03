#!/bin/bash
# Overview of git state for every mod subproject in the workbench.
# Any directory with a .git folder is treated as a mod — new ones are picked up automatically.

WORKBENCH="$(cd "$(dirname "$0")" && pwd)"

CLEAN=0
DIRTY=0
declare -A BRANCH_COUNT

echo "Fetching remotes..."
for dir in "$WORKBENCH"/*/; do
  [ -d "$dir/.git" ] || continue
  git -C "$dir" fetch --quiet 2>/dev/null &
done
wait
echo "Done."
echo ""

for dir in "$WORKBENCH"/*/; do
  [ -d "$dir/.git" ] || continue

  name=$(basename "$dir")
  branch=$(git -C "$dir" symbolic-ref --short HEAD 2>/dev/null || git -C "$dir" rev-parse --short HEAD 2>/dev/null)
  status=$(git -C "$dir" status --porcelain 2>/dev/null)
  ahead=$(git -C "$dir" rev-list --count @{u}..HEAD 2>/dev/null)
  behind=$(git -C "$dir" rev-list --count HEAD..@{u} 2>/dev/null)

  b="${branch:-???}"
  BRANCH_COUNT["$b"]=$(( ${BRANCH_COUNT["$b"]:-0} + 1 ))

  if [ -z "$status" ] && [ "${ahead:-0}" -eq 0 ] 2>/dev/null; then
    icon="✓"
    CLEAN=$((CLEAN + 1))
  else
    icon="!"
    DIRTY=$((DIRTY + 1))
  fi

  printf "\n%-4s %-26s  branch: %s\n" "$icon" "$name" "$b"

  if [ -n "$status" ]; then
    echo "$status" | while IFS= read -r line; do
      printf "       %s\n" "$line"
    done
  fi

  if [ "${ahead:-0}" -gt 0 ] 2>/dev/null; then
    printf "       ↑ %s commit(s) ahead of remote\n" "$ahead"
  fi
  if [ "${behind:-0}" -gt 0 ] 2>/dev/null; then
    printf "       ↓ %s commit(s) behind remote\n" "$behind"
  fi
done

echo ""
echo "────────────────────────────────────────"
printf "  %d clean   %d need attention\n" "$CLEAN" "$DIRTY"
echo ""

# print branch breakdown, sorted by count descending
for branch in "${!BRANCH_COUNT[@]}"; do
  printf "%d %s\n" "${BRANCH_COUNT[$branch]}" "$branch"
done | sort -rn | while read -r count b; do
  printf "  %-4s repos on %s\n" "$count" "$b"
done

echo "────────────────────────────────────────"
