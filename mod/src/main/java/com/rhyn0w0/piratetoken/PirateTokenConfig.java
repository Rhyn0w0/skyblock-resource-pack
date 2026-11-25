package com.rhyn0w0.piratetoken;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import net.fabricmc.loader.api.FabricLoader;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

public class PirateTokenConfig {
    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();
    private static final Path CONFIG_PATH = FabricLoader.getInstance().getConfigDir().resolve("piratetoken.json");

    public boolean enabled = true;
    public boolean soundEnabled = true;
    public float soundVolume = 0.9f;
    /** "official" or "pixel" */
    public String tokenStyle = "official";
    /** "access" ("YOU FOUND PIRATE SHOP ACCESS!") or "token" ("PIRATE TOKEN FOUND!") */
    public String bannerStyle = "access";
    /** "all", "f7", or "handle" */
    public String triggerMode = "all";
    public boolean triggerOnDungeonChestOpen = true;
    public boolean triggerOnOtherPlayers = false;

    public static PirateTokenConfig load() {
        if (Files.exists(CONFIG_PATH)) {
            try {
                PirateTokenConfig loaded = GSON.fromJson(Files.readString(CONFIG_PATH), PirateTokenConfig.class);
                if (loaded != null) {
                    loaded.sanitize();
                    return loaded;
                }
            } catch (Exception ignored) {
            }
        }
        PirateTokenConfig cfg = new PirateTokenConfig();
        cfg.save();
        return cfg;
    }

    private void sanitize() {
        if (!"official".equals(tokenStyle) && !"pixel".equals(tokenStyle)) {
            tokenStyle = "official";
        }
        if (!"access".equals(bannerStyle) && !"token".equals(bannerStyle)) {
            bannerStyle = "access";
        }
        if (!"all".equals(triggerMode) && !"f7".equals(triggerMode) && !"handle".equals(triggerMode)) {
            triggerMode = "all";
        }
        soundVolume = Math.max(0.0f, Math.min(1.5f, soundVolume));
    }

    public void save() {
        sanitize();
        try {
            Files.createDirectories(CONFIG_PATH.getParent());
            Files.writeString(CONFIG_PATH, GSON.toJson(this) + "\n");
        } catch (IOException ignored) {
        }
    }
}
