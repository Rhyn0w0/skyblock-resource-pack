package com.rhyn0w0.piratetoken;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import org.joml.Matrix3x2fStack;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/**
 * Renders the Fortnite Treasure Hunters "YOU FOUND PIRATE SHOP ACCESS!" celebration overlay
 * with rotating golden sunburst, elastic-spring Pirate Token, gold confetti burst, and
 * animated gold-trimmed banner.
 */
public class PirateTokenAnimation {
    private static final Identifier TEX_OFFICIAL = Identifier.fromNamespaceAndPath(PirateTokenMod.MOD_ID, "textures/gui/token_official.png");
    private static final Identifier TEX_PIXEL = Identifier.fromNamespaceAndPath(PirateTokenMod.MOD_ID, "textures/gui/token_pixel.png");
    private static final Identifier TEX_SUNBURST = Identifier.fromNamespaceAndPath(PirateTokenMod.MOD_ID, "textures/gui/sunburst.png");
    private static final Identifier TEX_GLOW = Identifier.fromNamespaceAndPath(PirateTokenMod.MOD_ID, "textures/gui/glow.png");

    private static final float DURATION_SECONDS = 5.4f;
    private static final int PARTICLE_COUNT = 72;

    private static final int[] CONFETTI_COLORS = {
        0xFFE866, // bright gold
        0xFFC41E, // Fortnite treasure gold
        0xFFFAD0, // warm sparkle white
        0xFF9F1C, // amber gold
        0xFFD700, // pure gold
        0x5CE1FF  // rare sprite-dust cyan accent
    };

    private boolean active = false;
    private long startNanos = 0L;
    private String dropTier = "RARE DROP!";
    private String itemDisplay = "Necron's Handle";
    private String magicFindText = "";
    private final List<Particle> particles = new ArrayList<>();
    private final Random random = new Random();

    public void trigger(String tier, String itemName, String magicFind) {
        PirateTokenConfig cfg = PirateTokenMod.getConfig();
        if (!cfg.enabled) {
            return;
        }

        this.dropTier = (tier == null || tier.isBlank()) ? "RARE DROP!" : tier.trim();
        this.itemDisplay = (itemName == null || itemName.isBlank()) ? "Pirate Token" : itemName.trim();
        this.magicFindText = (magicFind == null) ? "" : magicFind.trim();
        this.startNanos = System.nanoTime();
        this.active = true;

        spawnParticles();

        if (cfg.soundEnabled) {
            Minecraft mc = Minecraft.getInstance();
            mc.execute(() -> mc.getSoundManager().play(
                SimpleSoundInstance.forUI(PirateTokenMod.PIRATE_TOKEN_SOUND, 1.0f, cfg.soundVolume)
            ));
        }
    }

    public boolean isActive() {
        return active;
    }

    private void spawnParticles() {
        particles.clear();
        for (int i = 0; i < PARTICLE_COUNT; i++) {
            float angle = (float) (random.nextDouble() * Math.PI * 2.0);
            float speed = 55.0f + random.nextFloat() * 185.0f;
            float vx = (float) Math.cos(angle) * speed;
            float vy = (float) Math.sin(angle) * speed - (40.0f + random.nextFloat() * 65.0f);
            float size = 2.0f + random.nextFloat() * 3.5f;
            float life = 1.6f + random.nextFloat() * 2.4f;
            float delay = random.nextFloat() * 0.22f;
            float flutter = (random.nextFloat() - 0.5f) * 8.0f;
            int color = CONFETTI_COLORS[random.nextInt(CONFETTI_COLORS.length)];
            particles.add(new Particle(vx, vy, size, life, delay, flutter, color));
        }
    }

    public void render(GuiGraphicsExtractor graphics) {
        if (!active) {
            return;
        }

        float elapsed = (System.nanoTime() - startNanos) / 1_000_000_000.0f;
        if (elapsed >= DURATION_SECONDS) {
            active = false;
            return;
        }

        Minecraft mc = Minecraft.getInstance();
        Font font = mc.font;
        PirateTokenConfig cfg = PirateTokenMod.getConfig();

        int sw = graphics.guiWidth();
        int sh = graphics.guiHeight();

        // Global fade-out during the last 0.85s
        float fadeOut = elapsed > (DURATION_SECONDS - 0.85f)
            ? clamp01((DURATION_SECONDS - elapsed) / 0.85f)
            : 1.0f;
        float globalAlpha = easeOutCubic(fadeOut);

        // 1. Initial golden chest-burst flash + warm screen-edge treasure vignette
        if (elapsed < 0.55f) {
            float flash = (1.0f - (elapsed / 0.55f));
            flash = flash * flash * 0.42f;
            graphics.fill(0, 0, sw, sh, argb(flash, 0xFFE680));
        }
        int edgeH = Math.max(24, sh / 7);
        float edgeAlpha = Math.min(1.0f, elapsed / 0.25f) * 0.30f * globalAlpha;
        graphics.fillGradient(0, 0, sw, edgeH, argb(edgeAlpha, 0xFFB81C), argb(0.0f, 0xFFB81C));
        graphics.fillGradient(0, sh - edgeH, sw, sh, argb(0.0f, 0xFFB81C), argb(edgeAlpha, 0xFFB81C));

        // Center anchor in upper-middle third of the screen
        float centerX = sw * 0.5f;
        float tokenCenterY = Math.max(66.0f, sh * 0.27f);

        // Subtle impact shake for the first 0.30s
        float shakeX = 0.0f;
        float shakeY = 0.0f;
        if (elapsed < 0.30f) {
            float decay = 1.0f - (elapsed / 0.30f);
            shakeX = (float) Math.sin(elapsed * 85.0f) * 4.5f * decay;
            shakeY = (float) Math.cos(elapsed * 73.0f) * 3.0f * decay;
        }

        float tx = centerX + shakeX;
        float ty = tokenCenterY + shakeY;

        // 2. Rotating dual-layer golden sunburst + radial bloom behind the Pirate Token
        float burstScale = easeOutBack(clamp01(elapsed / 0.42f));
        float pulse = 1.0f + 0.05f * (float) Math.sin(elapsed * 5.2f);
        float sunburstAlpha = clamp01(elapsed / 0.22f) * 0.88f * globalAlpha;
        int sunburstSize = (int) (188 * burstScale * pulse);
        if (sunburstSize > 4 && sunburstAlpha > 0.01f) {
            Matrix3x2fStack pose = graphics.pose();

            // Soft golden radial halo
            pose.pushMatrix();
            pose.translate(tx, ty);
            int glowSize = (int) (156 * burstScale * (1.0f + 0.08f * (float) Math.sin(elapsed * 4.0f)));
            graphics.blit(
                RenderPipelines.GUI_TEXTURED, TEX_GLOW,
                -glowSize / 2, -glowSize / 2,
                0.0f, 0.0f,
                glowSize, glowSize,
                256, 256, 256, 256,
                argb(sunburstAlpha * 0.85f, 0xFFD94A)
            );
            pose.popMatrix();

            // Primary clockwise golden sunburst rays
            pose.pushMatrix();
            pose.translate(tx, ty);
            pose.rotate(elapsed * 0.58f);
            graphics.blit(
                RenderPipelines.GUI_TEXTURED, TEX_SUNBURST,
                -sunburstSize / 2, -sunburstSize / 2,
                0.0f, 0.0f,
                sunburstSize, sunburstSize,
                256, 256, 256, 256,
                argb(sunburstAlpha, 0xFFFFFF)
            );
            pose.popMatrix();

            // Subtle counter-rotating secondary rays for rich Fortnite treasure depth
            pose.pushMatrix();
            pose.translate(tx, ty);
            pose.rotate(-elapsed * 0.34f + 0.26f);
            int subSize = (int) (sunburstSize * 0.78f);
            graphics.blit(
                RenderPipelines.GUI_TEXTURED, TEX_SUNBURST,
                -subSize / 2, -subSize / 2,
                0.0f, 0.0f,
                subSize, subSize,
                256, 256, 256, 256,
                argb(sunburstAlpha * 0.45f, 0xFFF4A3)
            );
            pose.popMatrix();
        }

        // 3. Bursting golden confetti & sparkle particles
        for (Particle p : particles) {
            float pt = elapsed - p.delay;
            if (pt <= 0.0f || pt >= p.life) {
                continue;
            }
            float progress = pt / p.life;
            float drag = (1.0f - (float) Math.exp(-pt * 1.9f)) / 1.9f;
            float px = tx + p.vx * drag + (float) Math.sin(pt * 6.0f + p.flutter) * 6.0f;
            float py = ty + p.vy * drag + 0.5f * 135.0f * pt * pt;
            float pAlpha = (1.0f - progress * progress) * globalAlpha;
            float twinkle = 0.65f + 0.35f * (float) Math.sin(pt * 18.0f + p.flutter);
            int half = Math.max(1, (int) (p.size * (1.0f - progress * 0.35f) * 0.5f));
            int ix = (int) px;
            int iy = (int) py;
            int col = argb(pAlpha * twinkle, p.color);
            graphics.fill(ix - half, iy - half, ix + half + 1, iy + half + 1, col);
        }

        // 4. Elastic-spring Pirate Token emblem with celebratory wobble & float
        float tokenPop = easeOutBack(clamp01(elapsed / 0.38f));
        float exitScale = elapsed > (DURATION_SECONDS - 0.85f) ? (1.0f + (1.0f - fadeOut) * 0.16f) : 1.0f;
        float bob = (float) Math.sin(elapsed * 4.2f) * 3.0f;
        float wobble = (float) Math.sin(elapsed * 3.4f) * 0.08f * (elapsed < 0.7f ? 2.0f : 1.0f);
        int tokenSize = Math.max(4, (int) (74 * tokenPop * exitScale));
        Identifier tokenTex = "pixel".equals(cfg.tokenStyle) ? TEX_PIXEL : TEX_OFFICIAL;

        Matrix3x2fStack pose = graphics.pose();
        pose.pushMatrix();
        pose.translate(tx, ty + bob);
        pose.rotate(wobble);
        graphics.blit(
            RenderPipelines.GUI_TEXTURED, tokenTex,
            -tokenSize / 2, -tokenSize / 2,
            0.0f, 0.0f,
            tokenSize, tokenSize,
            256, 256, 256, 256,
            argb(globalAlpha, 0xFFFFFF)
        );
        pose.popMatrix();

        // 5. Fortnite-style Golden Banner ("YOU FOUND PIRATE SHOP ACCESS!")
        float bannerT = clamp01((elapsed - 0.16f) / 0.32f);
        if (bannerT > 0.0f) {
            float bannerEase = easeOutBack(bannerT);
            float bannerAlpha = clamp01(bannerT * 1.4f) * globalAlpha;

            String headline = "token".equals(cfg.bannerStyle)
                ? "PIRATE TOKEN FOUND!"
                : "YOU FOUND PIRATE SHOP ACCESS!";

            String subtitle = magicFindText.isEmpty()
                ? itemDisplay
                : itemDisplay + "  " + magicFindText;

            int headWidth = (int) (font.width(headline) * 1.25f);
            int subWidth = font.width(subtitle);
            int tierWidth = font.width(dropTier);
            int contentW = Math.max(Math.max(headWidth, subWidth), tierWidth);
            int bannerW = Math.min(sw - 24, Math.max(230, contentW + 44));
            int bannerH = 48;

            float slideOffset = (1.0f - clamp01(bannerT)) * 18.0f + (1.0f - fadeOut) * 10.0f;
            float bannerCenterY = ty + 62.0f + slideOffset;

            pose.pushMatrix();
            pose.translate(centerX, bannerCenterY);
            float scaleX = 0.75f + 0.25f * bannerEase;
            float scaleY = 0.85f + 0.15f * bannerEase;
            pose.scale(scaleX, scaleY);

            int x0 = -bannerW / 2;
            int x1 = bannerW / 2;
            int y0 = -bannerH / 2;
            int y1 = bannerH / 2;

            // Outer golden glow border
            graphics.fill(x0 - 3, y0 - 3, x1 + 3, y1 + 3, argb(bannerAlpha * 0.45f, 0xFFCC29));
            // Crisp dark-gold frame
            graphics.fill(x0 - 1, y0 - 1, x1 + 1, y1 + 1, argb(bannerAlpha * 0.95f, 0x4A2504));
            // Rich Fortnite pirate navy-to-gold dark backdrop
            graphics.fillGradient(x0, y0, x1, y1, argb(bannerAlpha * 0.92f, 0x26173B), argb(bannerAlpha * 0.95f, 0x120B1F));
            // Top & bottom gleaming gold trim bars
            graphics.fill(x0, y0, x1, y0 + 2, argb(bannerAlpha, 0xFFE866));
            graphics.fill(x0, y1 - 2, x1, y1, argb(bannerAlpha, 0xE6950A));

            // Sweeping metallic shine highlight across the banner
            float sweepCycle = (elapsed - 0.35f) % 2.1f;
            if (sweepCycle > 0.0f && sweepCycle < 0.75f) {
                float p = sweepCycle / 0.75f;
                int sx = (int) (x0 - 24 + (bannerW + 48) * p);
                int shX0 = Math.max(x0, sx - 14);
                int shX1 = Math.min(x1, sx + 14);
                if (shX1 > shX0) {
                    graphics.fill(shX0, y0 + 2, shX1, y1 - 2, argb(bannerAlpha * 0.18f, 0xFFFBE0));
                }
            }

            // Tier eyebrow (small centered text at top)
            graphics.centeredText(font, Component.literal(dropTier.toUpperCase()), 0, y0 + 5, argb(bannerAlpha, 0xFFE57F));

            // Bold scaled Fortnite headline
            pose.pushMatrix();
            pose.translate(0.0f, y0 + 17.0f);
            pose.scale(1.18f, 1.18f);
            graphics.centeredText(font, Component.literal(headline), 0, 0, argb(bannerAlpha, 0xFFD029));
            pose.popMatrix();

            // Dropped item name + Magic Find
            graphics.centeredText(font, Component.literal(subtitle), 0, y1 - 13, argb(bannerAlpha, 0xFFFFFF));

            pose.popMatrix();
        }
    }

    private static float clamp01(float v) {
        return Math.max(0.0f, Math.min(1.0f, v));
    }

    private static float easeOutCubic(float t) {
        float inv = 1.0f - t;
        return 1.0f - inv * inv * inv;
    }

    private static float easeOutBack(float t) {
        float c1 = 1.70158f;
        float c3 = c1 + 1.0f;
        float x = t - 1.0f;
        return 1.0f + c3 * x * x * x + c1 * x * x;
    }

    private static int argb(float alpha, int rgb) {
        int a = Math.max(0, Math.min(255, Math.round(alpha * 255.0f)));
        return (a << 24) | (rgb & 0xFFFFFF);
    }

    private record Particle(float vx, float vy, float size, float life, float delay, float flutter, int color) {}
}
