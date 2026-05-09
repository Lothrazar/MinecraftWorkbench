## Multi project workbench for java mods in IntelliJ

Mods are included in the workspace in settings.gradle using their folder name

Git ignore is set up to ignore them by default and only include workbench files, since each sub-module has its own repository.

In order for java gradle projects using a wrapper to be included in this way, each mod must have a check around the wrapper task to say 

Most default mod SDKs have a wrapper task but do not have this root project check

For example, the wrapper task in the mod gradle must look like this, with the if statement added

```
if (project == rootProject) {
tasks.named('wrapper', Wrapper).configure {
    distributionType = Wrapper.DistributionType.BIN
}}
```

Live example: https://github.com/Lothrazar/AutoRun/blob/trunk/1.21.1/build.gradle#L16

## Scripts

# swap.py

This adds the `if (project == rootProject) {` line for you in existing mod folders, so you can clone them all in.  Do not run twice or it will probably add the if statement twice

# check_changelog.py

The changelog at update.json is used by the automated publishing tasks, which build and upload mods to modrinth and curseforge

This script validates the structure of the update.json changelog, so the current active mod version has an entry in the log.

This is to avoid errors on game startup and errors on the gradle publishing tasks. 


# check_release.py

Check if mods have the ids needed for the release publish tasks.  Does not check if the projects are created remotely (yet)

# git_status.sh

Checks each submodule for its git un-committed changes, and reports the branch name

# sync_tmpl.py

There are some files common to every mod, and so the /tmpl/ folder has these files.  So you can edit once and sync it to all mods. 

Make sure that all mod-specific properties are moved out of the mods.toml file and gradle.properties and build.gradle, these should all be generic

Instead use a standalone "mod.properties" for all unique properties, and this is ignored by the template



# docs

For all My mods that are currently using this system, see https://lothrazar.github.io/MinecraftWorkbench/
