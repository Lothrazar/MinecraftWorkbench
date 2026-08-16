#!/usr/bin/env python3
"""
check_published.py - Compare local mod versions against CurseForge and Modrinth.
API keys are read from ~/.gradle/gradle.properties and are never printed or committed.

CurseForge/Modrinth lookups are filtered to each mod's local `minecraft_version` (from its
gradle.properties) - a mod with no published build for that exact game version shows "-" on that
platform rather than falling back to some other version's latest.

Example output:

Mod Name               Local           CurseForge      Modrinth
---------------------  --------------  --------------  -------------
Absent by Design       1.21.1-1.9.2    1.21.1-1.9.2    1.21.1-1.9.2
AntiBonemeal           1.21.1-1.0.2    1.21.1-1.0.2    -
autoplant              1.21.1-1.0.2    1.21.1-1.0.2    1.21.1-1.0.2
AutoRun                1.21.1-1.1.2    1.21.1-1.1.2    -
blocklayering          1.21.1-1.0.3    1.21.1-1.0.3    -
blockydoors            1.21.1-1.0.1*   -               -
cobblestoney           1.21.1-1.0.1*   -               -
colouredstuff          1.21.1-1.3.4*   -               -

"""


import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def load_properties(path):
  """Parse a Java-style .properties file into a dict (skips comments/blank lines)."""
  props = {}
  with open(path, "r", encoding="utf-8") as f:
    for line in f:
      line = line.strip()
      if not line or line.startswith("#") or line.startswith("!"):
        continue
      if "=" in line:
        k, _, v = line.partition("=")
        props[k.strip()] = v.strip()
  return props


def http_get(url, headers=None):
  req = urllib.request.Request(url, headers=headers or {})
  try:
    with urllib.request.urlopen(req, timeout=10) as resp:
      return json.loads(resp.read().decode("utf-8"))
  except urllib.error.HTTPError as e:
    if e.code != 404:
      print(f"  HTTP {e.code} for {url}", file=sys.stderr)
    return None
  except Exception as e:
    print(f"  Error: {e}", file=sys.stderr)
    return None


def get_curse_latest(curse_id, cf_key, mod_name, mc_version):
  qs = urllib.parse.urlencode({"gameVersion": mc_version}) if mc_version else ""
  url = f"https://api.curseforge.com/v1/mods/{curse_id}/files"
  if qs:
    url += f"?{qs}"
  data = http_get(url, {"x-api-key": cf_key, "Accept": "application/json"})
  if not data or not data.get("data"):
    return ""
  files = sorted(data["data"], key=lambda f: f.get("fileDate", ""), reverse=True)
  return files[0].get("displayName", "") or files[0].get("fileName", "")


def curse_version_normalized(display, mod_name, mod_id):
  """Extract the bare version string from a CurseForge displayName or fileName.

  Handles two common formats:
    "ModName 1.21.1-1.0.2"        → "1.21.1-1.0.2"
    "modid-1.21.1-1.0.2.jar"      → "1.21.1-1.0.2"
  """
  s = display.strip()
  # "ModName 1.21.1-1.0.2" style - case-insensitive prefix strip
  for prefix in [mod_name + " ", mod_id + " "]:
    if s.lower().startswith(prefix.lower()):
      return s[len(prefix):]
  # "modid-1.21.1-1.0.2.jar" style
  if s.lower().endswith(".jar"):
    s = s[:-4]
    for prefix in [mod_name + "-", mod_id + "-"]:
      if s.lower().startswith(prefix.lower()):
        return s[len(prefix):]
  return s


def get_modrinth_latest(modrinth_id, mr_token, mc_version):
  if not modrinth_id:
    return ""
  qs = urllib.parse.urlencode({"game_versions": json.dumps([mc_version])}) if mc_version else ""
  url = f"https://api.modrinth.com/v2/project/{modrinth_id}/version"
  if qs:
    url += f"?{qs}"
  headers = {"Authorization": mr_token} if mr_token else {}
  data = http_get(url, headers)
  if not isinstance(data, list) or not data:
    return ""
  data.sort(key=lambda v: v.get("date_published", ""), reverse=True)
  return data[0].get("version_number", "")


def find_mod_dirs(root):
  return sorted(
    d for d in root.iterdir()
    if d.is_dir()
    and not d.name.startswith(".")
    and (d / "mod.properties").exists()
  )


def main():
  root = Path(__file__).parent

  gradle_home = Path.home() / ".gradle" / "gradle.properties"
  if not gradle_home.exists():
    print(f"ERROR: {gradle_home} not found", file=sys.stderr)
    sys.exit(1)

  secrets = load_properties(gradle_home)
  cf_key = secrets.get("curseforge_core_api_key", "").strip()
  mr_token = secrets.get("modrinth_token", "").strip()

  if not cf_key:
    print("WARNING: curseforge_core_api_key missing from gradle.properties", file=sys.stderr)
  if not mr_token:
    print("WARNING: modrinth_token missing from gradle.properties", file=sys.stderr)

  mod_dirs = find_mod_dirs(root)
  print(f"Checking {len(mod_dirs)} mods...\n", flush=True)

  rows = []
  for mod_dir in mod_dirs:
    mod_props = load_properties(mod_dir / "mod.properties")
    gradle_props_path = mod_dir / "gradle.properties"
    gradle_props = load_properties(gradle_props_path) if gradle_props_path.exists() else {}

    mod_name = mod_props.get("mod_name", mod_dir.name)
    mod_id = mod_props.get("mod_id", mod_dir.name)
    mod_version = mod_props.get("mod_version", "?")
    mc_version = gradle_props.get("minecraft_version", "")
    local_ver = f"{mc_version}-{mod_version}" if mc_version else mod_version

    curse_id = mod_props.get("curse_id", "").strip()
    modrinth_id = mod_props.get("modrinth_id", "").strip()

    print(f"  {mod_name}...", end="", flush=True)
    curse_ver = get_curse_latest(curse_id, cf_key, mod_name, mc_version) if curse_id else ""
    mr_ver = get_modrinth_latest(modrinth_id, mr_token, mc_version)
    print(" done")

    curse_display = curse_version_normalized(curse_ver, mod_name, mod_id) if curse_ver else ""

    # Star the local version if it doesn't match what's on CurseForge
    local_display = local_ver
    if curse_display and local_ver != curse_display:
      local_display = local_ver + "*"

    rows.append((mod_name, local_display, curse_display or "-", mr_ver or "-"))

  headers = ("Mod Name", "Local", "CurseForge", "Modrinth")
  widths = [len(h) for h in headers]
  for row in rows:
    for i, cell in enumerate(row):
      widths[i] = max(widths[i], len(cell))

  sep = "  ".join("-" * w for w in widths)
  fmt = "  ".join(f"{{:<{w}}}" for w in widths)

  print()
  print(fmt.format(*headers))
  print(sep)
  for row in rows:
    print(fmt.format(*row))


if __name__ == "__main__":
  main()
