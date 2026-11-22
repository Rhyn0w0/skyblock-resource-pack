<img src="pack.png" width="96" height="96" alt="Fortnite Pirate Token">

# Hypixel SkyBlock Floor 7 × Fortnite Treasure Hunters Resource Pack

Turns **Hypixel SkyBlock Floor 7** drops and Dungeon Enchanted Books into **Fortnite Treasure Hunters** items, with built-in **Catharsis settings** so you can customize every piece right inside Minecraft.

## Catharsis Settings

Click the cog icon on this pack in **Options → Resource Packs** (or run `/catharsis config necron_handle_pirate_token`):

- **Texture Style:** `Pixel Art` *(custom 32×32 animated pixel art)* ↔ `Official Fortnite` *(official 256×256 Fortnite Treasure Hunters renders where available)*
- **Handle Display Name:** `Pirate Token` ↔ `Pirate Shop Access Token`
- **Floor 7 Gizmo Drops** *(default: ON)* — Turns Wither Scrolls, Auto Recombobulator, Precursor Gear, and Wither Catalyst into Fortnite Gizmos & Sprite Dust
- **Rename Gizmo Drops** *(default: OFF)* — Optionally renames those Floor 7 drops to their Fortnite Gizmo names
- **Enchanted Book Sprites** *(default: ON)* — Turns Floor 7 & Dungeon Enchanted Books into matching official Fortnite Sprites

## Included Replacements

### Floor 7 Drops → Pirate Token & Gizmos

| SkyBlock Drop | SkyBlock ID | Fortnite Item |
| --- | --- | --- |
| **Necron's Handle** | `necron_handle` | **Pirate Token** *(or Pirate Shop Access Token)* |
| **Implosion** *(Wither Scroll)* | `implosion_scroll` | **Golden Firework** |
| **Shadow Warp** *(Wither Scroll)* | `shadow_warp_scroll` | **Portable Extractor** |
| **Wither Shield** *(Wither Scroll)* | `wither_shield_scroll` | **Extraction Site Booster** |
| **Auto Recombobulator** | `auto_recombobulator` | **Lucky Locator** |
| **Precursor Gear** | `precursor_gear` | **Sprite Locator** |
| **Wither Catalyst** | `wither_catalyst` | **Sprite Dust** |

### Enchanted Books → Official Fortnite Sprites

| Enchanted Book | Catharsis ID | Fortnite Sprite |
| --- | --- | --- |
| **One For All** | `ultimate_one_for_all` | Boss Sprite |
| **Soul Eater** | `ultimate_soul_eater` | Grim Sprite |
| **Feather Falling** | `feather_falling` | Air Sprite |
| **Rejuvenate** | `rejuvenate` | Water Sprite |
| **Infinite Quiver** | `infinite_quiver` | Ranger Sprite |
| **Bank** | `ultimate_bank` | Chester |
| **Ultimate Wise** | `ultimate_wise` | Zero Point Sprite |
| **Wisdom** | `ultimate_wisdom` | Dream Sprite |
| **Ultimate Jerry** | `ultimate_jerry` | Peely Sprite |
| **Combo** | `ultimate_combo` | Striker Sprite |
| **Swarm** | `ultimate_swarm` | Lootin' Llama Sprite |
| **Legion** | `ultimate_legion` | Pirate Captain Sprite |
| **Last Stand** | `ultimate_last_stand` | Earth Sprite |
| **No Pain No Gain** | `ultimate_no_pain_no_gain` | Ghost Hood Sprite |
| **Overload** | `overload` | Cube Lightning Sprite |
| **Thunderlord** | `thunderlord` | Storm Sprite |
| **Lethality** | `lethality` | Demon Sprite |
| **Rend** | `ultimate_rend` | Chomper Sprite |

## Installation

1. Download [`dist/NecronHandle-PirateToken.zip`](https://github.com/Rhyn0w0/skyblock-resource-pack/raw/main/dist/NecronHandle-PirateToken.zip) and drop it directly into your Minecraft `resourcepacks/` folder.
2. In Minecraft, go to **Options → Resource Packs** and enable **NecronHandle-PirateToken**.
3. Place this pack **above** FurfSky Reborn (or other full SkyBlock packs) so it takes priority.
4. Click the cog icon next to the pack to customize Texture Style, Display Name, Gizmos, and Enchanted Book Sprites.

## Rebuilding Textures & Zip

```bash
python3 scripts/build_pack.py
```
