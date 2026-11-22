<img src="pack.png" width="96" height="96" alt="Fortnite Pirate Token">

# Necron's Handle → Fortnite Pirate Token (Hypixel SkyBlock Resource Pack)

A Hypixel SkyBlock resource pack that turns **Necron's Handle** (`NECRON_HANDLE`) into the **Fortnite Pirate Token**, with built-in **Catharsis settings** to toggle between the custom animated pixel-art coin and the official Fortnite Pirate Token image, and between **"Pirate Token"** and **"Pirate Shop Access Token"** as the visible name.

## Catharsis Settings

Click the cog icon on this pack in **Options → Resource Packs** (or run `/catharsis config necron_handle_pirate_token`):

- **Texture Style:** `Pixel Art` *(custom 32×32 animated gold pirate doubloon)* ↔ `Official Fortnite` *(official 256×256 Fortnite Treasure Hunters Pirate Token image)*
- **Display Name:** `Pirate Token` ↔ `Pirate Shop Access Token`

## Compatibility

| Minecraft Version | Mod | Pack Paths Used |
| --- | --- | --- |
| **1.21.4 – 1.21.11 / 26.1+** | **Catharsis** *(FurfSky Reborn v2.0+)* | `assets/skyblock/items/necron_handle.json`, `config.catharsis.json`, `fabric:overlays`, `catharsis/text_replacements` |
| **1.21.4 – 1.21.11 / 26.1+** | **Vanilla / Hypixel Server Pack** | `assets/hypixel_skyblock/items/necron_handle.json` |
| **1.20.4 – 1.21.11 / 26.1+** | **Firmament** | `assets/firmskyblock/items/necron_handle.json`, `assets/firmskyblock/overrides/texts/necron_handle.json` |
| **1.20.5 – 1.21.1** | **CIT Resewn** | `assets/minecraft/citresewn/cit/necron_handle/necron_handle.properties` |
| **1.13 – 1.20.4** | **OptiFine** | `assets/minecraft/optifine/cit/necron_handle/necron_handle.properties` |
| **1.8.9** | **OptiFine / MCPatcher** | `assets/minecraft/mcpatcher/cit/necron_handle/necron_handle.properties` |

## Installation

1. Download [`dist/NecronHandle-PirateToken.zip`](https://github.com/Rhyn0w0/skyblock-resource-pack/raw/main/dist/NecronHandle-PirateToken.zip) and drop it directly into your Minecraft `resourcepacks/` folder.
2. In Minecraft, go to **Options → Resource Packs** and enable **NecronHandle-PirateToken**.
3. Place this pack **above** FurfSky Reborn (or other full SkyBlock packs) so it overrides Necron's Handle cleanly.
4. Click the cog icon next to the pack to switch Texture Style or Display Name at any time.

## Rebuilding Textures & Zip

```bash
python3 scripts/build_pack.py
```
