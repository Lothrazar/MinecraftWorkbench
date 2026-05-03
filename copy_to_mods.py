import shutil
import os

ROOT = r"C:\Users\USER\eclipse-workspace\mc121\FLib"
MODS_BASE = r"C:\Users\USER\MyFiles\mc121"

TARGETS = [
    "AbsentByDesign",
    "AntiBonemeal",
    "AutoPlant",
    "AutoRun",
    "BlockLayers",
    "BlockyDoors",
    "ColouredStuff",
    "CreeperHeal",
    "ElementaryOres",
    "EnchantingRunes",
    "FragileTorches",
    "GardenTools",
    "GlassCutter",
    "HeartBalance",
    "LetThemGrow",
    "MountedPearl",
    "NoLogPunch",
    "OceanFloorControl",
    "PhantomMinecart",
    "pickybags",
    "PotatoBread",
    "Scraps",
    "StonecutterLikesWood",
    "StrongerFarmland",
    "stupidHorseStandStill",
]

FILES_TO_COPY = [
    os.path.join(".github", "workflows", "release.yml"),
    os.path.join("gradle", "deploy.gradle"),
    "build.gradle",
]

def copy_files():
    success = 0
    errors = 0

    for mod in TARGETS:
        target_dir = os.path.join(MODS_BASE, mod)

        if not os.path.isdir(target_dir):
            print(f"[SKIP]  {mod} — target folder not found: {target_dir}")
            errors += 1
            continue

        for rel_path in FILES_TO_COPY:
            src = os.path.join(ROOT, rel_path)
            dst = os.path.join(target_dir, rel_path)

            if not os.path.isfile(src):
                print(f"[WARN]  Source not found, skipping: {src}")
                continue

            # Create intermediate directories if needed (e.g. .github/workflows/)
            os.makedirs(os.path.dirname(dst), exist_ok=True)

            shutil.copy2(src, dst)
            print(f"[OK]    {mod}\\{rel_path}")

        success += 1

    print(f"\nDone. {success} mods processed, {errors} skipped.")

if __name__ == "__main__":
    copy_files()