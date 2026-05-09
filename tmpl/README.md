
There are some files common to every mod  So you can edit once and use ../sync_tmpl.py to save changes to all mods. 

Make sure that all mod-specific properties are moved out of the mods.toml file and gradle.properties and build.gradle, these should all be generic

Instead use a standalone "mod.properties" for all unique properties, and this is ignored by the template



