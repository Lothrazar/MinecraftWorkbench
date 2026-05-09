import os
import json

minecraft_version = "1.21.1"

script_dir = os.path.dirname(os.path.abspath(__file__))

SKIP = {"tmpl", "build", "gradle", "docs"}

results = []

for name in sorted(os.listdir(script_dir)):
  folder = os.path.join(script_dir, name)
  if not os.path.isdir(folder) or name in SKIP or name.startswith("."):
    continue

  props_path = os.path.join(folder, "mod.properties")
  if not os.path.isfile(props_path):
    continue

  # parse mod.properties
  mod_version = None
  with open(props_path, "r", encoding="utf-8") as f:
    for line in f:
      line = line.strip()
      if line.startswith("mod_version="):
        mod_version = line.split("=", 1)[1].strip()
        break

  if mod_version is None:
    results.append((name, "MISSING mod_version in mod.properties"))
    continue

  update_path = os.path.join(folder, "update.json")
  if not os.path.isfile(update_path):
    results.append((name, f"MISSING update.json  (need [{minecraft_version}][{mod_version}])"))
    continue

  try:
    with open(update_path, "r", encoding="utf-8-sig") as f:
      data = json.load(f)
  except json.JSONDecodeError as e:
    results.append((name, f"INVALID JSON: {e}"))
    continue

  if minecraft_version not in data:
    results.append((name, f"MISSING key '{minecraft_version}' in update.json"))
  elif mod_version not in data[minecraft_version]:
    results.append((name, f"MISSING key '{mod_version}' under '{minecraft_version}' in update.json"))
  else:
    results.append((name, f"OK  ({minecraft_version} / {mod_version})"))

pad = max(len(r[0]) for r in results)
for name, status in results:
  print(f"{name:<{pad}}  {status}")
