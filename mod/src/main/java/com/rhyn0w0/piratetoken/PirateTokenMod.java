package com.rhyn0w0.piratetoken;

import com.mojang.brigadier.arguments.StringArgumentType;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.command.v2.ClientCommandRegistrationCallback;
import net.fabricmc.fabric.api.client.command.v2.ClientCommands;
import net.fabricmc.fabric.api.client.command.v2.FabricClientCommandSource;
import net.fabricmc.fabric.api.client.message.v1.ClientReceiveMessageEvents;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElementRegistry;
import net.fabricmc.fabric.api.client.screen.v1.ScreenEvents;
import net.minecraft.ChatFormatting;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.sounds.SoundEvent;

public class PirateTokenMod implements ClientModInitializer {
    public static final String MOD_ID = "piratetoken";

    public static final Identifier SOUND_ID = Identifier.fromNamespaceAndPath(MOD_ID, "pirate_token_drop");
    public static final SoundEvent PIRATE_TOKEN_SOUND = SoundEvent.createVariableRangeEvent(SOUND_ID);

    private static PirateTokenConfig config;
    private static PirateTokenAnimation animation;
    private static RareDropDetector detector;
    private static Screen activeScreen;

    public static PirateTokenConfig getConfig() {
        return config;
    }

    public static PirateTokenAnimation getAnimation() {
        return animation;
    }

    @Override
    public void onInitializeClient() {
        config = PirateTokenConfig.load();
        animation = new PirateTokenAnimation();
        detector = new RareDropDetector();

        Registry.register(BuiltInRegistries.SOUND_EVENT, SOUND_ID, PIRATE_TOKEN_SOUND);

        // Render on main HUD when no screen is open
        HudElementRegistry.addLast(
            Identifier.fromNamespaceAndPath(MOD_ID, "pirate_token_overlay"),
            (graphics, deltaTracker) -> {
                if (activeScreen == null) {
                    animation.render(graphics);
                }
            }
        );

        // Render on top of open screens (e.g., Dungeon Bedrock Chest GUI) & scan dungeon chests
        ScreenEvents.AFTER_INIT.register((client, screen, scaledWidth, scaledHeight) -> {
            activeScreen = screen;
            ScreenEvents.afterExtract(screen).register((scr, graphics, mouseX, mouseY, tickDelta) ->
                animation.render(graphics)
            );
            ScreenEvents.afterTick(screen).register(detector::onScreenTick);
            ScreenEvents.remove(screen).register(scr -> {
                if (activeScreen == scr) {
                    activeScreen = null;
                }
                detector.onScreenClosed(scr);
            });
        });

        // Listen for Hypixel SkyBlock rare drop chat messages
        ClientReceiveMessageEvents.GAME.register(detector::onGameMessage);

        // Register /piratetoken client command
        registerCommands();
    }

    private void registerCommands() {
        ClientCommandRegistrationCallback.EVENT.register((dispatcher, registryAccess) ->
            dispatcher.register(
                ClientCommands.literal("piratetoken")
                    .executes(ctx -> {
                        sendStatus(ctx.getSource());
                        return 1;
                    })
                    .then(ClientCommands.literal("test")
                        .executes(ctx -> {
                            boolean prev = config.enabled;
                            config.enabled = true;
                            animation.trigger("INSANE DROP!", "Necron's Handle", "(+215% ✯ Magic Find)");
                            config.enabled = prev;
                            return 1;
                        })
                        .then(ClientCommands.argument("item", StringArgumentType.greedyString())
                            .executes(ctx -> {
                                String item = StringArgumentType.getString(ctx, "item");
                                boolean prev = config.enabled;
                                config.enabled = true;
                                animation.trigger("RARE DROP!", item, "(+200% ✯ Magic Find)");
                                config.enabled = prev;
                                return 1;
                            })
                        )
                    )
                    .then(ClientCommands.literal("toggle")
                        .executes(ctx -> {
                            config.enabled = !config.enabled;
                            config.save();
                            feedback(ctx.getSource(), "Pirate Token Drop Animation is now " + (config.enabled ? "§aON" : "§cOFF"));
                            return 1;
                        })
                    )
                    .then(ClientCommands.literal("sound")
                        .executes(ctx -> {
                            config.soundEnabled = !config.soundEnabled;
                            config.save();
                            feedback(ctx.getSource(), "Fanfare sound is now " + (config.soundEnabled ? "§aON" : "§cOFF"));
                            return 1;
                        })
                    )
                    .then(ClientCommands.literal("chest")
                        .executes(ctx -> {
                            config.triggerOnDungeonChestOpen = !config.triggerOnDungeonChestOpen;
                            config.save();
                            feedback(ctx.getSource(), "Dungeon Chest instant trigger is now " + (config.triggerOnDungeonChestOpen ? "§aON" : "§cOFF"));
                            return 1;
                        })
                    )
                    .then(ClientCommands.literal("party")
                        .executes(ctx -> {
                            config.triggerOnOtherPlayers = !config.triggerOnOtherPlayers;
                            config.save();
                            feedback(ctx.getSource(), "Other players' dungeon drops trigger is now " + (config.triggerOnOtherPlayers ? "§aON" : "§cOFF"));
                            return 1;
                        })
                    )
                    .then(ClientCommands.literal("style")
                        .then(ClientCommands.literal("official").executes(ctx -> {
                            config.tokenStyle = "official";
                            config.save();
                            feedback(ctx.getSource(), "Token style set to §6Official Fortnite");
                            return 1;
                        }))
                        .then(ClientCommands.literal("pixel").executes(ctx -> {
                            config.tokenStyle = "pixel";
                            config.save();
                            feedback(ctx.getSource(), "Token style set to §6Pixel Art");
                            return 1;
                        }))
                    )
                    .then(ClientCommands.literal("banner")
                        .then(ClientCommands.literal("access").executes(ctx -> {
                            config.bannerStyle = "access";
                            config.save();
                            feedback(ctx.getSource(), "Banner headline set to §6YOU FOUND PIRATE SHOP ACCESS!");
                            return 1;
                        }))
                        .then(ClientCommands.literal("token").executes(ctx -> {
                            config.bannerStyle = "token";
                            config.save();
                            feedback(ctx.getSource(), "Banner headline set to §6PIRATE TOKEN FOUND!");
                            return 1;
                        }))
                    )
                    .then(ClientCommands.literal("mode")
                        .then(ClientCommands.literal("all").executes(ctx -> {
                            config.triggerMode = "all";
                            config.save();
                            feedback(ctx.getSource(), "Trigger mode set to §aAll SkyBlock rare drops");
                            return 1;
                        }))
                        .then(ClientCommands.literal("f7").executes(ctx -> {
                            config.triggerMode = "f7";
                            config.save();
                            feedback(ctx.getSource(), "Trigger mode set to §dFloor 7 / M7 rare drops only");
                            return 1;
                        }))
                        .then(ClientCommands.literal("handle").executes(ctx -> {
                            config.triggerMode = "handle";
                            config.save();
                            feedback(ctx.getSource(), "Trigger mode set to §6Necron's Handle only");
                            return 1;
                        }))
                    )
                    .then(ClientCommands.literal("status")
                        .executes(ctx -> {
                            sendStatus(ctx.getSource());
                            return 1;
                        })
                    )
            )
        );
    }

    private static void sendStatus(FabricClientCommandSource source) {
        feedback(source, "§6§lPirate Token Drop Mod");
        source.sendFeedback(Component.literal(
            "§7Enabled: " + (config.enabled ? "§aON" : "§cOFF")
                + " §8| §7Sound: " + (config.soundEnabled ? "§aON" : "§cOFF")
                + " §8| §7Style: §6" + config.tokenStyle
                + " §8| §7Mode: §e" + config.triggerMode
        ));
        source.sendFeedback(Component.literal(
            "§7Commands: §e/piratetoken test [item]§7, §etoggle§7, §esound§7, §estyle <official|pixel>§7, §ebanner <access|token>§7, §emode <all|f7|handle>§7, §echest§7, §eparty"
        ));
    }

    private static void feedback(FabricClientCommandSource source, String text) {
        source.sendFeedback(
            Component.literal("[PirateToken] ").withStyle(ChatFormatting.GOLD, ChatFormatting.BOLD)
                .append(Component.literal(text).withStyle(ChatFormatting.RESET, ChatFormatting.GRAY))
        );
    }
}
