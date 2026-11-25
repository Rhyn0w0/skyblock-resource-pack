package com.rhyn0w0.piratetoken;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.core.component.DataComponents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.CustomData;

import java.util.Locale;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Detects Hypixel SkyBlock rare drops from:
 * 1) System chat messages (RARE DROP!, CRAZY RARE DROP!, INSANE DROP!, PRAY TO RNGESUS, PET DROP!, DYE DROP!, RARE REWARD!, etc.)
 * 2) Opened Catacombs Dungeon Reward Chest GUIs (instant trigger the second you see Necron's Handle, Wither Scrolls, Claymore, etc.)
 */
public class RareDropDetector {
    private static final Pattern FORMATTING_CODES = Pattern.compile("§.");

    // Standard Hypixel SkyBlock RNG drop system messages (start of stripped line -> avoids player chat spam!)
    private static final Pattern SKYBLOCK_DROP_PATTERN = Pattern.compile(
        "^(RARE DROP!|VERY RARE DROP!|CRAZY RARE DROP!|INSANE DROP!|PRAY TO RNGESUS DROP!|RNGESUS INCARNATE!|EXTRAORDINARY DROP!|PET DROP!|DYE DROP!|INCREDIBLE DROP!)\\s*(.+)$",
        Pattern.CASE_INSENSITIVE
    );

    // Dungeon reward chest broadcast: "RARE REWARD! Player found a Necron's Handle in their Bedrock Chest!"
    private static final Pattern DUNGEON_REWARD_PATTERN = Pattern.compile(
        "^(?:WOW!|RARE REWARD!)\\s+([A-Za-z0-9_]{1,16})\\s+found\\s+(?:an?\\s+)?(.+?)\\s+(?:in|from)\\b.*$",
        Pattern.CASE_INSENSITIVE
    );

    // Magic find / Pet luck suffix inside drop lines: "(+215% ✯ Magic Find)"
    private static final Pattern MAGIC_FIND_PATTERN = Pattern.compile("(\\([^)]*(?:Magic Find|Pet Luck)[^)]*\\))", Pattern.CASE_INSENSITIVE);

    private static final Set<String> F7_RARE_IDS = Set.of(
        "NECRON_HANDLE",
        "IMPLOSION_SCROLL",
        "SHADOW_WARP_SCROLL",
        "WITHER_SHIELD_SCROLL",
        "AUTO_RECOMBOBULATOR",
        "WITHER_CHESTPLATE",
        "DARK_CLAYMORE",
        "FIFTH_MASTER_STAR",
        "DYE_NECRON"
    );

    private static final Set<String> ALL_DUNGEON_CHEST_RARE_IDS = Set.of(
        "NECRON_HANDLE",
        "IMPLOSION_SCROLL",
        "SHADOW_WARP_SCROLL",
        "WITHER_SHIELD_SCROLL",
        "AUTO_RECOMBOBULATOR",
        "DARK_CLAYMORE",
        "GIANTS_SWORD",
        "SHADOW_FURY",
        "PRECURSOR_EYE",
        "SUMMONING_RING",
        "NECROMANCER_LORD_CHESTPLATE",
        "WITHER_CHESTPLATE",
        "FIRST_MASTER_STAR",
        "SECOND_MASTER_STAR",
        "THIRD_MASTER_STAR",
        "FOURTH_MASTER_STAR",
        "FIFTH_MASTER_STAR",
        "DYE_NECRON",
        "DYE_LIVID",
        "THUNDERLORD_7"
    );

    private static final Set<String> DUNGEON_CHEST_TITLES = Set.of(
        "wood chest",
        "gold chest",
        "diamond chest",
        "emerald chest",
        "obsidian chest",
        "bedrock chest"
    );

    private Screen lastCheckedChestScreen = null;
    private boolean chestTriggeredForScreen = false;
    private long lastTriggerMillis = 0L;
    private String lastTriggerItem = "";

    public void onGameMessage(Component message, boolean overlay) {
        if (overlay) {
            return;
        }
        PirateTokenConfig cfg = PirateTokenMod.getConfig();
        if (!cfg.enabled) {
            return;
        }

        String plain = stripFormatting(message.getString()).trim();
        if (plain.isEmpty()) {
            return;
        }

        // 1. Standard SkyBlock rare drop messages
        Matcher dropMatcher = SKYBLOCK_DROP_PATTERN.matcher(plain);
        if (dropMatcher.matches()) {
            String tier = dropMatcher.group(1).trim();
            String rest = dropMatcher.group(2).trim();

            String magicFind = "";
            Matcher mfMatcher = MAGIC_FIND_PATTERN.matcher(rest);
            if (mfMatcher.find()) {
                magicFind = mfMatcher.group(1).trim();
                rest = (rest.substring(0, mfMatcher.start()) + rest.substring(mfMatcher.end())).trim();
            }

            // Strip surrounding parentheses if Hypixel formatted item as "(Necron's Handle)"
            if (rest.startsWith("(") && rest.endsWith(")") && rest.length() > 2) {
                rest = rest.substring(1, rest.length() - 1).trim();
            }

            if (matchesTriggerMode(cfg.triggerMode, rest, null)) {
                fireWithCooldown(tier, rest, magicFind);
            }
            return;
        }

        // 2. Dungeon boss reward chest announcement
        Matcher dungeonMatcher = DUNGEON_REWARD_PATTERN.matcher(plain);
        if (dungeonMatcher.matches()) {
            String player = dungeonMatcher.group(1).trim();
            String item = dungeonMatcher.group(2).trim();

            Minecraft mc = Minecraft.getInstance();
            String selfName = mc.getUser() != null ? mc.getUser().getName() : "";
            boolean isSelf = !selfName.isEmpty() && selfName.equalsIgnoreCase(player);
            if (!isSelf && !cfg.triggerOnOtherPlayers) {
                return;
            }

            if (matchesTriggerMode(cfg.triggerMode, item, null)) {
                String tier = isSelf ? "RARE REWARD!" : (player + "'s RARE REWARD!");
                fireWithCooldown(tier, item, "");
            }
        }
    }

    public void onScreenTick(Screen current) {
        PirateTokenConfig cfg = PirateTokenMod.getConfig();
        if (!cfg.enabled || !cfg.triggerOnDungeonChestOpen) {
            return;
        }

        if (!(current instanceof AbstractContainerScreen<?> container)) {
            return;
        }

        if (current != lastCheckedChestScreen) {
            lastCheckedChestScreen = current;
            chestTriggeredForScreen = false;
        }
        if (chestTriggeredForScreen) {
            return;
        }

        String title = stripFormatting(current.getTitle().getString()).trim().toLowerCase(Locale.ROOT);
        if (!DUNGEON_CHEST_TITLES.contains(title)) {
            return;
        }

        // Scan chest slots (exclude player's own bottom 36 inventory slots)
        var slots = container.getMenu().slots;
        int chestSlotCount = Math.max(0, slots.size() - 36);
        for (int i = 0; i < chestSlotCount; i++) {
            Slot slot = slots.get(i);
            ItemStack stack = slot.getItem();
            if (stack.isEmpty()) {
                continue;
            }

            String sbId = extractSkyBlockId(stack);
            String cleanName = stripFormatting(stack.getHoverName().getString()).trim();

            if (sbId != null && isRareChestId(cfg.triggerMode, sbId)) {
                chestTriggeredForScreen = true;
                String display = "NECRON_HANDLE".equals(sbId) ? "Necron's Handle" : cleanName;
                fireWithCooldown(title.toUpperCase(Locale.ROOT) + " DROP!", display, "");
                return;
            }
        }
    }

    public void onScreenClosed(Screen closed) {
        if (closed == lastCheckedChestScreen) {
            lastCheckedChestScreen = null;
            chestTriggeredForScreen = false;
        }
    }

    private boolean isRareChestId(String mode, String sbId) {
        return switch (mode) {
            case "handle" -> "NECRON_HANDLE".equals(sbId);
            case "f7" -> F7_RARE_IDS.contains(sbId);
            default -> ALL_DUNGEON_CHEST_RARE_IDS.contains(sbId);
        };
    }

    private boolean matchesTriggerMode(String mode, String itemName, String sbId) {
        String lower = itemName.toLowerCase(Locale.ROOT);
        return switch (mode) {
            case "handle" -> "NECRON_HANDLE".equals(sbId) || lower.contains("necron's handle") || lower.contains("pirate token");
            case "f7" -> (sbId != null && F7_RARE_IDS.contains(sbId))
                || lower.contains("necron's handle")
                || lower.contains("pirate token")
                || lower.contains("implosion")
                || lower.contains("shadow warp")
                || lower.contains("wither shield")
                || lower.contains("auto recombobulator")
                || lower.contains("wither chestplate")
                || lower.contains("dark claymore")
                || lower.contains("fifth master star")
                || lower.contains("necron dye");
            default -> true;
        };
    }

    private void fireWithCooldown(String tier, String item, String magicFind) {
        long now = System.currentTimeMillis();
        // Avoid double-triggering if both chest GUI detection and purchase chat fire back-to-back for the same item
        if (now - lastTriggerMillis < 10_000L && item.equalsIgnoreCase(lastTriggerItem)) {
            return;
        }
        lastTriggerMillis = now;
        lastTriggerItem = item;
        PirateTokenMod.getAnimation().trigger(tier, item, magicFind);
    }

    private static String extractSkyBlockId(ItemStack stack) {
        CustomData customData = stack.get(DataComponents.CUSTOM_DATA);
        if (customData == null || customData.isEmpty()) {
            return null;
        }
        CompoundTag tag = customData.copyTag();
        String direct = tag.getStringOr("id", "");
        if (!direct.isEmpty()) {
            return direct;
        }
        return tag.getCompound("ExtraAttributes")
            .map(ea -> ea.getStringOr("id", ""))
            .filter(s -> !s.isEmpty())
            .orElse(null);
    }

    public static String stripFormatting(String s) {
        return s == null ? "" : FORMATTING_CODES.matcher(s).replaceAll("");
    }
}
