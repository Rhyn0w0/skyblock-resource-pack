<img src="pack.png" width="96" height="96" alt="Fortnite Pirate Token">

# Necron's Handle → Fortnite Pirate Token (Hypixel SkyBlock Resource Pack)

A Hypixel SkyBlock resource pack that turns **Necron's Handle** (`NECRON_HANDLE`) into an animated gold **Fortnite Pirate Token** (Pirate Shop Access doubloon) with a diagonal metallic sheen and sparkle glint.

## Compatibility

Works out of the box with **Catharsis** (used by FurfSky Reborn v2.0+) as well as Firmament, CIT Resewn, and OptiFine:

| Minecraft Version | Mod | Pack Paths Used |
| --- | --- | --- |
| **1.21.4 – 1.21.11 / 26.1+** | **Catharsis** *(FurfSky Reborn v2.0+)* | `assets/skyblock/items/necron_handle.json` → `pirate_token:item/necron_handle` (`catharsis:pack/v1`) |
| **1.20.4 – 1.21.11 / 26.1+** | **Firmament** | `assets/firmskyblock/items/necron_handle.json`, `assets/firmskyblock/models/item/necron_handle.json` |
| **1.20.5 – 1.21.1** | **CIT Resewn** | `assets/minecraft/citresewn/cit/necron_handle/necron_handle.properties` |
| **1.13 – 1.20.4** | **OptiFine** | `assets/minecraft/optifine/cit/necron_handle/necron_handle.properties` |
| **1.8.9** | **OptiFine / MCPatcher** | `assets/minecraft/mcpatcher/cit/necron_handle/necron_handle.properties` |

## Installation

1. Download [`dist/NecronHandle-PirateToken.zip`](https://github.com/Rhyn0w0/skyblock-resource-pack/raw/main/dist/NecronHandle-PirateToken.zip) and drop it directly into your Minecraft `resourcepacks/` folder (do **not** use GitHub's "Download ZIP" without extracting the inner folder first, as Minecraft requires `pack.mcmeta` at the pack root).
2. In Minecraft, go to **Options → Resource Packs** and enable **NecronHandle-PirateToken**.
3. Place this pack **above** FurfSky Reborn (or other full SkyBlock packs) so it overrides Necron's Handle cleanly.

## Testing in Singleplayer

- **1.20.5+ / 1.21+ / 26.1+ (with Catharsis, Firmament, or CIT Resewn):**
  ```mcfunction
  /give @s minecraft:stick[minecraft:custom_data={id:"NECRON_HANDLE"},minecraft:enchantment_glint_override=true]
  ```
- **1.8.9 – 1.20.4 (with OptiFine):**
  ```mcfunction
  /give @p minecraft:stick 1 0 {ExtraAttributes:{id:"NECRON_HANDLE"}}
  ```

## Rebuilding Textures & Zip

Run the zero-dependency generator script after tweaking `scripts/build_pack.py`:

```bash
python3 scripts/build_pack.py
```
