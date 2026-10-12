# Bolt-Action Rifle (NeoForge 21.1.257, Minecraft 1.21.1)

Adds a bolt-action rifle with a 5-round magazine and craftable ammunition.

> **Status:** source project only. It has not been compiled or tested in-game yet.

## Build the jar

Requirements: **JDK 21**, **Gradle 8.8 or newer**, and an internet connection (Gradle downloads
Minecraft + NeoForge the first time). This project doesn't ship a Gradle wrapper, so either run
Gradle directly:

```
gradle build
```

or create the wrapper once and use it from then on:

```
gradle wrapper --gradle-version 8.10
./gradlew build        # Windows: gradlew.bat build
```

The mod jar appears in `build/libs/boltrifle-1.0.0.jar`.

If Gradle can't find the `net.neoforged.moddev` plugin version in `build.gradle`, change it to
the latest 2.0.x listed at https://plugins.gradle.org/plugin/net.neoforged.moddev

## Install

Drop `boltrifle-1.0.0.jar` into the `mods` folder of your NeoForge 21.1.x / Minecraft 1.21.1
instance. No other mods are required.

## Recipes

**Bolt-Action Rifle**
```
I I I      I = Iron Ingot
W T .      W = Any Planks
W . .      T = Tripwire Hook
```

**Rifle Round** (makes 4): shapeless - Iron Nugget + Gunpowder + Copper Ingot

## Using the rifle

- **Right-click** - fire. If the magazine is empty, right-click reloads instead.
- **Sneak + right-click** - reload (pulls rounds from your inventory, tops up to 5).
- Ammo count shows as a bar under the item and in the tooltip.
- Hitscan shot, 64-block range, 14 damage (7 hearts), 25-tick bolt cooldown, 40-tick reload.
- Creative mode players reload without needing ammo.

Tweak the numbers at the top of `RifleItem.java`. Textures are simple placeholders in
`src/main/resources/assets/boltrifle/textures/item/`.
