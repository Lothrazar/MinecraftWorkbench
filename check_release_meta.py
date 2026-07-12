import os

ROOT = os.path.dirname(os.path.abspath(__file__))
SKIP = {"tmpl", "build", "gradle", "docs"}
BLANK = "!!!"

entries = sorted(
  d for d in os.listdir(ROOT)
  if os.path.isdir(os.path.join(ROOT, d)) and d not in SKIP and not d.startswith(".")
)

def read_prop(props_path, key):
  if not os.path.isfile(props_path):
    return None
  with open(props_path, encoding="utf-8") as f:
    for line in f:
      if line.startswith(key + "="):
        value = line.rstrip("\n")[len(key) + 1:]
        return value if value else BLANK
  return BLANK

rows = []
for folder in entries:
  props_path = os.path.join(ROOT, folder, "mod.properties")
  curse = read_prop(props_path, "curse_id")
  modrinth = read_prop(props_path, "modrinth_id")
  rows.append((folder, curse if curse not in (None, "0") else BLANK, modrinth or BLANK))

col0 = max(len(r[0]) for r in rows) if rows else 8
col1 = max(len(r[1]) for r in rows) if rows else 5
col2 = max(len(r[2]) for r in rows) if rows else 8

header = f"{'':{col0}}    {'CURSEFORGE':{col1}}   {'MODRINTH':{col2}}"
print(header)
print("-" * len(header))
for name, curse, modrinth in rows:
  print(f"{name:{col0}}    {curse:{col1}}      {modrinth:{col2}}")
