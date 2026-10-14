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
	private static double zoom = 1;
	private static Double savedSensitivity;
	private static GunDef lastDef;
	private static double fireCooldown;            // client-side shot timer (ticks), mirrors the server's
	private static int reloadBuffer;            // ticks a pressed R key stays queued (e.g. during bolt cycling)
	private static float kickRise, kickRecover, kickYaw;   // camera recoil, spread over several ticks

	public static float aimProgress(float partialTick) {
		return Mth.lerp(partialTick, aimOld, aim);
	}

	private static GunDef heldDef(Player p) {
		return p != null && p.getMainHandItem().getItem() instanceof GunItem g ? g.def : null;
	}

	private static boolean holdingGun(Player p) {
		return heldDef(p) != null;
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
			event.registerAbove(VanillaGuiLayers.CAMERA_OVERLAYS, id("scope"), ClientEvents::renderScope);
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

			GunDef def = mc.screen == null ? heldDef(player) : null;
			boolean holding = def != null;
			if (def != lastDef) {                   // switched guns: reset zoom and timers
				lastDef = def;
				if (def != null) {
					zoom = def.zoomDefault;
				}
				fireCooldown = 0;
			}
			fireCooldown = Math.max(fireCooldown - 1.0, -1.0);

			while (RELOAD_KEY.consumeClick()) {
				if (holding) {
					reloadBuffer = 40;        // remember the press for 2 s so it fires once the gun is free
				}
			}
			if (!holding) {
				reloadBuffer = 0;
			}

			if (holding) {
				ItemStack stack = player.getMainHandItem();
				int action = GunItem.getAction(stack);
				boolean reloading = action == GunItem.ACTION_RELOAD || action == GunItem.ACTION_RELOAD_CHAMBER;
				if (reloadBuffer > 0) {
					reloadBuffer--;
					if (!GunItem.isBusy(stack) || action == GunItem.ACTION_FIRE && def.interval < 4) {
						PacketDistributor.sendToServer(new Net.ReloadPayload());
						reloadBuffer = 0;
					}
				}
				// raising the gun to reload always lowers the sights first, even with right click held
				wantAim = mc.options.keyUse.isDown() && !reloading && reloadBuffer == 0;
				if (def.auto && mc.options.keyAttack.isDown()) {
					tryFire(player, def);
				}
			} else {
				wantAim = false;
			}
			float target = wantAim ? 1.0f : 0.0f;
			float speed = lastDef != null ? lastDef.aimSpeed : 0.16f;
			aim += Mth.clamp(target - aim, -speed, speed);
			applyRecoil(player);

			applySensitivity(mc);
		}

		@SubscribeEvent
		public static void onInteract(InputEvent.InteractionKeyMappingTriggered event) {
			LocalPlayer player = Minecraft.getInstance().player;
			GunDef def = heldDef(player);
			if (def == null) {
				return;
			}
			if (event.isAttack()) {            // left click = fire (automatics fire from the tick handler)
				event.setCanceled(true);
				event.setSwingHand(false);
				if (!def.auto) {
					tryFire(player, def);
				}
			} else if (event.isUseItem()) {    // right click = scope (handled in tick)
				event.setCanceled(true);
				event.setSwingHand(false);
			}
		}

		@SubscribeEvent
		public static void onScroll(InputEvent.MouseScrollingEvent event) {
			if (wantAim && aim > 0.5f && lastDef != null) {
				if (lastDef.zoomMax > lastDef.zoomMin) {
					zoom = lastDef.zoomClamp(zoom + Math.signum(event.getScrollDeltaY()));
				}
				event.setCanceled(true);       // don't change hotbar slot while aiming
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
			if (lastDef != null && lastDef.scoped && event.getHand() == InteractionHand.MAIN_HAND && aimProgress(event.getPartialTick()) > 0.94f) {
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
	private static void tryFire(LocalPlayer player, GunDef def) {
		ItemStack stack = player.getMainHandItem();
		int action = GunItem.getAction(stack);
		if ((action != GunItem.ACTION_NONE && action != GunItem.ACTION_FIRE) || fireCooldown > 0) {
			return;
		}
		boolean aiming = aim > 0.85f;
		PacketDistributor.sendToServer(new Net.FirePayload(aiming));
		if (GunItem.isChambered(stack)) {   // predicted recoil kick, applied smoothly in applyRecoil()
			fireCooldown += def.interval;
			float kick = def.recoilPitch * (float) (double) ClientConfig.RECOIL_SCALE.get() * (aiming ? 0.6f : 1.0f);
			kickRise += kick;
			kickRecover += kick * 0.35f;
			kickYaw += (player.getRandom().nextFloat() - 0.5f) * 2.0f * def.recoilYaw
					* (float) (double) ClientConfig.RECOIL_SCALE.get();
		} else {
			fireCooldown = def.dryTicks;
		}
	}

	/** Camera climbs fast then settles, and a third of the climb comes back down (like real muzzle recovery). */
	private static void applyRecoil(LocalPlayer player) {
		if (player == null) {
			kickRise = kickRecover = kickYaw = 0;
			return;
		}
		if (kickRise > 0.01f) {
			float step = kickRise * 0.45f;
			kickRise -= step;
			player.setXRot(Mth.clamp(player.getXRot() - step, -90.0f, 90.0f));
		} else if (kickRecover > 0.01f) {
			float step = kickRecover * 0.12f;
			kickRecover -= step;
			player.setXRot(Mth.clamp(player.getXRot() + step, -90.0f, 90.0f));
		}
		if (Math.abs(kickYaw) > 0.01f) {
			float step = kickYaw * 0.4f;
			kickYaw -= step;
			player.setYRot(player.getYRot() + step);
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
		if (p <= 0.6f || lastDef == null || !lastDef.scoped || !holdingGun(mc.player)) {
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
		GunDef def = heldDef(player);
		if (def == null || mc.options.hideGui) {
			return;
		}
		ItemStack stack = player.getMainHandItem();
		GunItem gun = (GunItem) stack.getItem();
		int mags = 0, reserve = 0;
		Inventory inv = player.getInventory();
		for (int i = 0; i < inv.getContainerSize(); i++) {
			ItemStack s = inv.getItem(i);
			if (s.getItem() instanceof MagItem m && m.type == def.mag && MagItem.rounds(s) > 0) {
				mags += s.getCount();
				reserve += MagItem.rounds(s) * s.getCount();
			}
		}
		int action = GunItem.getAction(stack);
		String status = switch (action) {
			case GunItem.ACTION_RELOAD, GunItem.ACTION_RELOAD_CHAMBER -> "RELOADING";
			case GunItem.ACTION_FIRE -> def.interval >= 8 ? "CYCLING" : "READY";
			default -> !GunItem.hasMag(stack) ? "NO MAGAZINE" : GunItem.isChambered(stack) ? "READY" : "CHAMBER EMPTY";
		};
		String ammo = GunItem.getLoaded(stack) + (GunItem.isChambered(stack) ? " +1" : " +0") + " / " + def.mag.capacity;
		String type = (GunItem.isChambered(stack) ? gun.chamberRound(stack) : gun.magRound(stack)).display;
		String spare = player.isCreative() ? "mags: inf" : mags + " mags (" + reserve + ")";
		int x = g.guiWidth() - 8;
		int y = g.guiHeight() - 52;
		g.drawString(mc.font, ammo, x - mc.font.width(ammo), y, 0xFFFFFFFF, true);
		g.drawString(mc.font, type, x - mc.font.width(type), y + 10, 0xFFB0B0B0, true);
		g.drawString(mc.font, spare, x - mc.font.width(spare), y + 20, 0xFFB0B0B0, true);
		g.drawString(mc.font, status, x - mc.font.width(status), y + 30, 0xFFE0A030, true);
	}
}
