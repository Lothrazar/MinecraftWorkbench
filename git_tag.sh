#!/bin/bash
# Create a release git tag for one mod, based on gradle.properties + mod.properties.
# Tag format matches the version string build.gradle already builds:
#   v${minecraft_version}-${mod_version}
#
# Usage:
#   ./git_tag.sh Cyclic      # tag the named mod folder
#   ./git_tag.sh             # or cd into a mod folder and run with no arg

echo ""
WORKBENCH="$(cd "$(dirname "$0")" && pwd)"
if [ -n "$1" ]; then
  MODDIR="$WORKBENCH/$1"
else
  MODDIR="$(pwd)"
fi
if [ ! -d "$MODDIR/.git" ]; then
  echo "Not a mod repo (no .git found): $MODDIR"
  exit 1
fi


MODNAME=$(basename "$MODDIR")

# commit changes before tag
status=$(git -C "$MODDIR" status --porcelain 2>/dev/null)
if [ -n "$status" ]; then
  echo "Uncommitted changes in $MODNAME - commit or stash before tagging:"
  echo "$status"
  exit 1
fi
# now build the tag

mc_version=$(grep '^minecraft_version=' "$MODDIR/gradle.properties" 2>/dev/null | cut -d= -f2)
mod_version=$(grep '^mod_version=' "$MODDIR/mod.properties" 2>/dev/null | cut -d= -f2)

if [ -z "$mc_version" ]; then
  echo "Could not read minecraft_version from $MODDIR/gradle.properties"
  exit 1
fi
if [ -z "$mod_version" ]; then
  echo "Could not read mod_version from $MODDIR/mod.properties"
  exit 1
fi

tag="v${mc_version}-${mod_version}"

# now create if it does not exist
if git -C "$MODDIR" show-ref --tags --verify --quiet "refs/tags/$tag"; then
  echo "tag $tag already exists in $MODNAME/  "
  exit 0
fi

git -C "$MODDIR" tag "$tag"
echo ""
echo ""
echo "Created tag $tag on $MODNAME"
echo ""
echo ""
echo "Run the release tag to upload artifacts: "
echo "       cd $MODDIR && ./gradlew release "
