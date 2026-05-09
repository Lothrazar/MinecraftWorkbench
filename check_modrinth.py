import os

ROOT = os.path.dirname(os.path.abspath(__file__))
SKIP = {"tmpl", "build", "gradle"}

results = {"filled": [], "blank": [], "missing": []}

entries = sorted(
  d for d in os.listdir(ROOT)
  if os.path.isdir(os.path.join(ROOT, d)) and d not in SKIP and not d.startswith(".")
)

for folder in entries:
  props_path = os.path.join(ROOT, folder, "mod.properties")
  if not os.path.isfile(props_path):
    results["missing"].append((folder, "no mod.properties"))
    continue

  modrinth_line = None
  with open(props_path, encoding="utf-8") as f:
    for line in f:
      if line.startswith("modrinth_id="):
        modrinth_line = line.rstrip("\n")
        break

  if modrinth_line is None:
    results["missing"].append((folder, "key absent"))
  elif modrinth_line == "modrinth_id=":
    results["blank"].append((folder, "key present but blank"))
  else:
    value = modrinth_line[len("modrinth_id="):]
    results["filled"].append((folder, value))

print("=== MISSING ===")
if results["missing"]:
  for folder, reason in results["missing"]:
    print(f"  {folder:30s}  [{reason}]")
else:
  print("  (none)")

print()
print("=== BLANK (present but empty) ===")
if results["blank"]:
  for folder, reason in results["blank"]:
    print(f"  {folder:30s}  [{reason}]")
else:
  print("  (none)")

print()
print("=== FILLED ===")
if results["filled"]:
  for folder, value in results["filled"]:
    print(f"  {folder:30s}  {value}")
else:
  print("  (none)")
