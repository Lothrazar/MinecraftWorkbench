#!/usr/bin/env python3
"""
sync_tmpl.py — Push canonical template files from tmpl/ into every mod subproject.

A subproject is any direct subfolder that contains a mod.properties file.
Files in tmpl/ are copied verbatim; nothing in tmpl/ is ever generated or
modified by this script — edit the source there, then run this to propagate.

Usage:
    python sync_tmpl.py                  # sync everything
    python sync_tmpl.py --dry-run        # preview without writing
    python sync_tmpl.py AntiBonemeal     # limit to one or more mods
    python sync_tmpl.py --check          # exit 1 if anything is out of date (CI use)
"""

import argparse
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
TMPL = os.path.join(ROOT, 'tmpl')

# Top-level dirs that are not mod subprojects
SKIP_DIRS = {'build', 'gradle', 'tmpl', '.gradle', '.idea', '.git', '__pycache__'}

# Per-mod files that sync should never overwrite (relative paths, as yielded by iter_tmpl_files)
SKIP_FILES = {
    'AutoRun': {
        os.path.join('src', 'main', 'templates', 'META-INF', 'neoforge.mods.toml'),
        os.path.join('build.gradle'),
    },
}


def iter_mods(only=None):
    """Yield (name, abs_path) for every mod subfolder."""
    for name in sorted(os.listdir(ROOT)):
        if name in SKIP_DIRS or name.startswith('.'):
            continue
        path = os.path.join(ROOT, name)
        if not os.path.isdir(path):
            continue
        if not os.path.isfile(os.path.join(path, 'mod.properties')):
            continue
        if only and name not in only:
            continue
        yield name, path


def iter_tmpl_files():
    """Yield (rel_path, abs_src) for every file under tmpl/."""
    for dirpath, _dirs, filenames in os.walk(TMPL):
        for fname in sorted(filenames):
            src = os.path.join(dirpath, fname)
            rel = os.path.relpath(src, TMPL)
            yield rel, src


UTF8_BOM = b'\xef\xbb\xbf'


def _read_no_bom(path):
    with open(path, 'rb') as f:
        data = f.read()
    return data[len(UTF8_BOM):] if data.startswith(UTF8_BOM) else data


def _cmp_strip_bom(src, dst):
    """Return True if dst already matches what we would write (src with BOM stripped)."""
    with open(dst, 'rb') as f:
        dst_data = f.read()
    return _read_no_bom(src) == dst_data


def _copy_strip_bom(src, dst):
    """Copy src to dst, stripping a leading UTF-8 BOM if present."""
    with open(dst, 'wb') as f:
        f.write(_read_no_bom(src))
    shutil.copystat(src, dst)


def sync(dry_run=False, only=None, check=False):
    mods = list(iter_mods(only))
    if not mods:
        print("No mod subprojects found.")
        return 0

    changed = 0
    unchanged = 0

    for mod_name, mod_path in mods:
        for rel, src in iter_tmpl_files():
            if rel in SKIP_FILES.get(mod_name, set()):
                print(f"  SKIP    {mod_name}/{rel}")
                continue
            dst = os.path.join(mod_path, rel)
            if os.path.isfile(dst) and _cmp_strip_bom(src, dst):
                unchanged += 1
                continue
            status = 'ADD   ' if not os.path.isfile(dst) else 'UPDATE'
            print(f"  {status}  {mod_name}/{rel}")
            if not dry_run and not check:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                _copy_strip_bom(src, dst)
            changed += 1

    verb = 'Would change' if (dry_run or check) else 'Changed'
    print(f"\n{verb}: {changed}  |  Already up-to-date: {unchanged}")
    return changed


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would change without writing anything')
    parser.add_argument('--check', action='store_true',
                        help='Exit with code 1 if any file is out of date (for CI)')
    parser.add_argument('mods', nargs='*', metavar='MOD',
                        help='Limit sync to these mod folder names')
    args = parser.parse_args()

    n = sync(dry_run=args.dry_run, only=set(args.mods) or None, check=args.check)
    if args.check and n > 0:
        sys.exit(1)
