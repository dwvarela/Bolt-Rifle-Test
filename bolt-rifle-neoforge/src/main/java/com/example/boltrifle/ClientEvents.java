package com.example.boltrifle;

import com.mojang.blaze3d.platform.InputConstants;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.minecraft.client.OptionInstance;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.ClientTickEvent;
import net.neoforged.neoforge.client.event.ComputeFovModifierEvent;
import net.neoforged.neoforge.client.event.InputEvent;
import net.neoforged.neoforge.client.event.RegisterGuiLayersEvent;
import net.neoforged.neoforge.client.event.RegisterKeyMappingsEvent;
import net.neoforged.neoforge.client.event.RenderGuiLayerEvent;
import net.neoforged.neoforge.client.event.RenderHandEvent;
import net.neoforged.neoforge.client.gui.VanillaGuiLayers;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * Client input + presentation: left click fires, hold right click to look through the scope,
 * R reloads, scroll wheel changes zoom while scoped.
 */
public final class ClientEvents {
	private ClientEvents() {}

	public static final KeyMapping RELOAD_KEY =
			new KeyMapping("key.boltrifle.reload", InputConstants.KEY_R, "key.categories.boltrifle");

	private static float aim, aimOld;          // 0 = hip, 1 = fully scoped
	private static boolean wantAim;
	private static double zoom = -1;
	private static Double savedSensitivity;

	public static float aimProgress(float partialTick) {
		return Mth.lerp(partialTick, aimOld, aim);
	}

	private static boolean holdingRifle(Player p) {
		return p != null && p.getMainHandItem().getItem() instanceof RifleItem;
	}

	private static ResourceLocation id(String path) {
		return ResourceLocation.fromNamespaceAndPath(BoltRifleMod.MOD_ID, path);
	}

	// ======================================================================= mod bus (registration)
	@EventBusSubscriber(modid = BoltRifleMod.MOD_ID, bus = EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
	public static final class ModBus {
		@SubscribeEvent
		public static void registerKeys(RegisterKeyMappingsEvent event) {
			event.register(RELOAD_KEY);
		}

		@SubscribeEvent
		public static void registerLayers(RegisterGuiLayersEvent event) {
			event.registerAboveAll(id("scope"), ClientEvents::renderScope);
			event.registerAboveAll(id("ammo_hud"), ClientEvents::renderHud);
		}
	}

	// ======================================================================= game bus (runtime)
	@EventBusSubscriber(modid = BoltRifleMod.MOD_ID, bus = EventBusSubscriber.Bus.GAME, value = Dist.CLIENT)
	public static final class GameBus {

		@SubscribeEvent
		public static void onTick(ClientTickEvent.Post event) {
			Minecraft mc = Minecraft.getInstance();
			LocalPlayer player = mc.player;
			aimOld = aim;
			if (zoom < 0) {
				zoom = ClientConfig.ZOOM_DEFAULT.get();
			}

			boolean holding = holdingRifle(player) && mc.screen == null;
			if (holding) {
				int action = RifleItem.getAction(player.getMainHandItem());
				boolean reloading = action == RifleItem.ACTION_RELOAD || action == RifleItem.ACTION_RELOAD_CHAMBER;
				wantAim = mc.options.keyUse.isDown() && !reloading;
			} else {
				wantAim = false;
			}
			float target = wantAim ? 1.0f : 0.0f;
			aim += Mth.clamp(target - aim, -0.22f, 0.22f);

			while (RELOAD_KEY.consumeClick()) {
				if (holding) {
					PacketDistributor.sendToServer(new Net.ReloadPayload());
				}
			}
			applySensitivity(mc);
		}

		@SubscribeEvent
		public static void onInteract(InputEvent.InteractionKeyMappingTriggered event) {
			LocalPlayer player = Minecraft.getInstance().player;
			if (!holdingRifle(player)) {
				return;
			}
			if (event.isAttack()) {            // left click = fire
				event.setCanceled(true);
				event.setSwingHand(false);
				tryFire(player);
			} else if (event.isUseItem()) {    // right click = scope (handled in tick)
				event.setCanceled(true);
				event.setSwingHand(false);
			}
		}

		@SubscribeEvent
		public static void onScroll(InputEvent.MouseScrollingEvent event) {
			if (wantAim && aim > 0.5f) {
				double step = Math.signum(event.getScrollDeltaY());
				zoom = Mth.clamp(zoom + step, ClientConfig.ZOOM_MIN.get(), ClientConfig.ZOOM_MAX.get());
				event.setCanceled(true);       // don't change hotbar slot while scoped
			}
		}

		@SubscribeEvent
		public static void onFov(ComputeFovModifierEvent event) {
			if (aim > 0.001f) {
				float eased = aim * aim * (3.0f - 2.0f * aim);
				float factor = (float) Mth.lerp(eased, 1.0, 1.0 / zoom);
				event.setNewFovModifier(event.getNewFovModifier() * factor);
			}
		}

		@SubscribeEvent
		public static void onRenderHand(RenderHandEvent event) {
			if (event.getHand() == InteractionHand.MAIN_HAND && aimProgress(event.getPartialTick()) > 0.94f) {
				event.setCanceled(true);
			}
		}

		@SubscribeEvent
		public static void onGuiLayer(RenderGuiLayerEvent.Pre event) {
			if (aim > 0.2f && VanillaGuiLayers.CROSSHAIR.equals(event.getName())) {
				event.setCanceled(true);
			}
		}
	}

	// ======================================================================= helpers
	private static void tryFire(LocalPlayer player) {
		ItemStack stack = player.getMainHandItem();
		if (RifleItem.isBusy(stack)) {
			return;
		}
		boolean aiming = aim > 0.85f;
		PacketDistributor.sendToServer(new Net.FirePayload(aiming));
		if (RifleItem.isChambered(stack)) {   // predicted recoil kick
			float kick = (float) (double) ClientConfig.RECOIL_PITCH.get() * (aiming ? 0.5f : 1.0f);
			player.setXRot(Mth.clamp(player.getXRot() - kick, -90.0f, 90.0f));
			player.setYRot(player.getYRot() + (player.getRandom().nextFloat() - 0.5f) * kick * 0.5f);
		}
	}

	/** Slows mouse look while scoped so high zoom stays controllable. Always restored afterwards. */
	private static void applySensitivity(Minecraft mc) {
		OptionInstance<Double> option = mc.options.sensitivity();
		boolean scoped = wantAim && aim > 0.3f;
		if (scoped) {
			if (savedSensitivity == null) {
				savedSensitivity = option.get();
			}
			double divisor = Math.pow(zoom, ClientConfig.ZOOM_SENSITIVITY_EXPONENT.get());
			option.set(Math.max(0.0, savedSensitivity / Math.max(1.0, divisor)));
		} else if (savedSensitivity != null) {
			option.set(savedSensitivity);
			savedSensitivity = null;
		}
	}

	// ======================================================================= HUD layers
	private static void renderScope(GuiGraphics g, DeltaTracker delta) {
		Minecraft mc = Minecraft.getInstance();
		float p = aimProgress(delta.getGameTimeDeltaPartialTick(false));
		if (p <= 0.6f || !holdingRifle(mc.player)) {
			return;
		}
		float fade = Mth.clamp((p - 0.6f) / 0.4f, 0.0f, 1.0f);
		int black = ((int) (255 * fade)) << 24;
		int w = g.guiWidth(), h = g.guiHeight();
		int cx = w / 2, cy = h / 2;
		int r = (int) (h * 0.46f);

		// black mask with a round opening
		g.fill(0, 0, w, cy - r, black);
		g.fill(0, cy + r, w, h, black);
		for (int y = cy - r; y < cy + r; y++) {
			double dy = y - cy + 0.5;
			int half = (int) Math.sqrt(Math.max(0.0, (double) r * r - dy * dy));
			int left = Math.max(0, cx - half), right = Math.min(w, cx + half);
			if (left > 0) {
				g.fill(0, y, left, y + 1, black);
			}
			if (right < w) {
				g.fill(right, y, w, y + 1, black);
			}
		}

		// duplex reticle: thin lines in the middle, thick posts outside, mil dots between
		int line = ((int) (255 * fade * 0.9f)) << 24;
		int post = (int) (r * 0.45f);
		g.fill(cx - r, cy, cx - 4, cy + 1, line);
		g.fill(cx + 4, cy, cx + r, cy + 1, line);
		g.fill(cx, cy - r, cx + 1, cy - 4, line);
		g.fill(cx, cy + 4, cx + 1, cy + r, line);
		g.fill(cx - r, cy - 1, cx - post, cy + 2, line);
		g.fill(cx + post, cy - 1, cx + r, cy + 2, line);
		g.fill(cx - 1, cy - r, cx + 2, cy - post, line);
		g.fill(cx - 1, cy + post, cx + 2, cy + r, line);
		for (int k = 1; k <= 4; k++) {
			int d = (int) (r * (0.08f * k + 0.04f));
			g.fill(cx - d - 1, cy - 1, cx - d + 1, cy + 1, line);
			g.fill(cx + d - 1, cy - 1, cx + d + 1, cy + 1, line);
			g.fill(cx - 1, cy - d - 1, cx + 1, cy - d + 1, line);
			g.fill(cx - 1, cy + d - 1, cx + 1, cy + d + 1, line);
		}
		g.fill(cx - 1, cy - 1, cx + 1, cy + 1, 0xFFCC2222);

		if (fade > 0.5f) {
			g.drawString(mc.font, String.format("%.0fx", zoom), cx + (int) (r * 0.55f), cy + (int) (r * 0.80f),
					0xFF77DD77, false);
		}
	}

	private static void renderHud(GuiGraphics g, DeltaTracker delta) {
		Minecraft mc = Minecraft.getInstance();
		Player player = mc.player;
		if (!holdingRifle(player) || mc.options.hideGui) {
			return;
		}
		ItemStack stack = player.getMainHandItem();
		int reserve = 0;
		Inventory inv = player.getInventory();
		for (int i = 0; i < inv.getContainerSize(); i++) {
			ItemStack s = inv.getItem(i);
			if (s.is(BoltRifleMod.RIFLE_ROUND.get())) {
				reserve += s.getCount();
			}
		}
		int action = RifleItem.getAction(stack);
		String status = switch (action) {
			case RifleItem.ACTION_RELOAD, RifleItem.ACTION_RELOAD_CHAMBER -> "RELOADING";
			case RifleItem.ACTION_FIRE -> "CYCLING";
			default -> RifleItem.isChambered(stack) ? "READY" : "CHAMBER EMPTY";
		};
		String ammo = RifleItem.getLoaded(stack) + "/" + RifleItem.MAGAZINE_SIZE
				+ (RifleItem.isChambered(stack) ? " +1" : " +0") + "  |  " + (player.isCreative() ? "inf" : reserve);
		int x = g.guiWidth() - 8;
		int y = g.guiHeight() - 40;
		g.drawString(mc.font, ammo, x - mc.font.width(ammo), y, 0xFFFFFFFF, true);
		g.drawString(mc.font, status, x - mc.font.width(status), y + 10, 0xFFE0A030, true);
	}
}
