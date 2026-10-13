package com.example.boltrifle;

import net.minecraft.ChatFormatting;
import net.minecraft.client.renderer.BlockEntityWithoutLevelRenderer;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.animatable.GeoItem;
import software.bernie.geckolib.animatable.SingletonGeoAnimatable;
import software.bernie.geckolib.animatable.client.GeoRenderProvider;
import software.bernie.geckolib.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.animation.AnimatableManager;
import software.bernie.geckolib.animation.AnimationController;
import software.bernie.geckolib.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

import java.util.List;
import java.util.function.Consumer;

/**
 * M700-style bolt-action rifle.
 *
 * Left click = fire (client sends a packet), right click (hold) = aim down the scope,
 * R = reload.  The server owns all ammo state and timing; GeckoLib plays the animations.
 *
 * Magazine holds 5 rounds. One more can sit in the chamber, so a full load is "5 + 1".
 */
public class RifleItem extends Item implements GeoItem {
	public static final int MAGAZINE_SIZE = 5;
	public static final float DAMAGE = 16.0f;            // 8 hearts
	public static final float HEADSHOT_MULTIPLIER = 1.5f;
	public static final double RANGE = 128.0;
	public static final float SPREAD_HIP_DEGREES = 2.8f;
	public static final float SPREAD_ADS_DEGREES = 0.10f;

	// timed actions (stored on the stack so the client HUD and animations stay in sync)
	public static final int ACTION_NONE = 0;
	public static final int ACTION_FIRE = 1;              // recoil + bolt cycle
	public static final int ACTION_RELOAD = 2;            // magazine swap only
	public static final int ACTION_RELOAD_CHAMBER = 3;    // magazine swap + chambering
	public static final int ACTION_DRY = 4;               // click
	/** Length of each action in ticks. Matches the animation lengths (x20), rounded up. */
	private static final int[] DURATION = {0, 31, 56, 76, 6};

	private static final String CONTROLLER = "main";
	private static final RawAnimation IDLE = RawAnimation.begin().thenLoop("animation.bolt_rifle.idle");
	private static final RawAnimation FIRE = RawAnimation.begin().thenPlay("animation.bolt_rifle.fire");
	private static final RawAnimation DRY = RawAnimation.begin().thenPlay("animation.bolt_rifle.dryfire");
	private static final RawAnimation RELOAD = RawAnimation.begin().thenPlay("animation.bolt_rifle.reload");
	private static final RawAnimation RELOAD_CHAMBER = RawAnimation.begin().thenPlay("animation.bolt_rifle.reload_chamber");

	/** A sound that plays N ticks after an action starts, synced to the animation. */
	private record Cue(int tick, SoundEvent sound, float volume, float pitch) {}

	private static final Cue[][] CUES = {
			{},
			{ // fire: handle up, bolt back, bolt forward, handle down
					new Cue(11, SoundEvents.IRON_TRAPDOOR_OPEN, 0.7f, 1.7f),
					new Cue(18, SoundEvents.CROSSBOW_LOADING_MIDDLE, 0.9f, 0.9f),
					new Cue(22, SoundEvents.CROSSBOW_LOADING_END, 0.9f, 0.8f),
					new Cue(27, SoundEvents.IRON_TRAPDOOR_CLOSE, 0.7f, 1.6f)},
			{ // reload: release, mag out, mag in, seat
					new Cue(9, SoundEvents.LEVER_CLICK, 0.8f, 1.4f),
					new Cue(13, SoundEvents.CROSSBOW_LOADING_START, 0.8f, 1.2f),
					new Cue(40, SoundEvents.CROSSBOW_LOADING_MIDDLE, 0.9f, 1.1f),
					new Cue(43, SoundEvents.IRON_TRAPDOOR_CLOSE, 0.9f, 1.3f)},
			{ // reload + chamber
					new Cue(9, SoundEvents.LEVER_CLICK, 0.8f, 1.4f),
					new Cue(13, SoundEvents.CROSSBOW_LOADING_START, 0.8f, 1.2f),
					new Cue(40, SoundEvents.CROSSBOW_LOADING_MIDDLE, 0.9f, 1.1f),
					new Cue(43, SoundEvents.IRON_TRAPDOOR_CLOSE, 0.9f, 1.3f),
					new Cue(58, SoundEvents.IRON_TRAPDOOR_OPEN, 0.7f, 1.7f),
					new Cue(62, SoundEvents.CROSSBOW_LOADING_MIDDLE, 0.9f, 0.9f),
					new Cue(68, SoundEvents.CROSSBOW_LOADING_END, 0.9f, 0.8f),
					new Cue(74, SoundEvents.IRON_TRAPDOOR_CLOSE, 0.7f, 1.6f)},
			{new Cue(0, SoundEvents.LEVER_CLICK, 0.9f, 0.7f)}
	};

	private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);

	public RifleItem(Properties properties) {
		super(properties);
		SingletonGeoAnimatable.registerSyncedAnimatable(this);
	}

	// ------------------------------------------------------------------ state helpers

	public static int getLoaded(ItemStack stack) {
		return stack.getOrDefault(BoltRifleMod.LOADED.get(), 0);
	}

	public static boolean isChambered(ItemStack stack) {
		return stack.getOrDefault(BoltRifleMod.CHAMBERED.get(), false);
	}

	public static int getAction(ItemStack stack) {
		return stack.getOrDefault(BoltRifleMod.ACTION.get(), ACTION_NONE);
	}

	public static boolean isBusy(ItemStack stack) {
		return getAction(stack) != ACTION_NONE;
	}

	private static void clearAction(ItemStack stack) {
		stack.set(BoltRifleMod.ACTION.get(), ACTION_NONE);
		stack.set(BoltRifleMod.PENDING.get(), 0);
	}

	private void startAction(ServerPlayer player, ItemStack stack, int action, RawAnimationName anim) {
		ServerLevel level = player.serverLevel();
		stack.set(BoltRifleMod.ACTION.get(), action);
		stack.set(BoltRifleMod.ACTION_START.get(), level.getGameTime());
		triggerAnim(player, GeoItem.getOrAssignId(stack, level), CONTROLLER, anim.id);
	}

	private enum RawAnimationName {
		FIRE("fire"), DRY("dry"), RELOAD("reload"), RELOAD_CHAMBER("reload_chamber");
		final String id;
		RawAnimationName(String id) { this.id = id; }
	}

	private static void play(Level level, Entity e, SoundEvent sound, float volume, float pitch) {
		level.playSound(null, e.getX(), e.getY(), e.getZ(), sound, SoundSource.PLAYERS, volume, pitch);
	}

	private static void hint(Player player, Component text) {
		player.displayClientMessage(text, true);
	}

	// ------------------------------------------------------------------ input handlers (server side)

	public static void handleFire(ServerPlayer player, boolean aiming) {
		ItemStack stack = player.getMainHandItem();
		if (stack.getItem() instanceof RifleItem rifle) {
			rifle.fire(player, stack, aiming);
		}
	}

	public static void handleReload(ServerPlayer player) {
		ItemStack stack = player.getMainHandItem();
		if (stack.getItem() instanceof RifleItem rifle) {
			rifle.reload(player, stack);
		}
	}

	private void fire(ServerPlayer player, ItemStack stack, boolean aiming) {
		if (isBusy(stack)) {
			return;
		}
		if (!isChambered(stack)) {
			startAction(player, stack, ACTION_DRY, RawAnimationName.DRY);
			hint(player, Component.literal(getLoaded(stack) > 0 ? "Not chambered" : "Empty - press R to reload")
					.withStyle(ChatFormatting.YELLOW));
			return;
		}

		ServerLevel level = player.serverLevel();
		stack.set(BoltRifleMod.CHAMBERED.get(), false);
		int mag = getLoaded(stack);
		if (mag > 0) { // the bolt cycle that follows the shot chambers the next round
			stack.set(BoltRifleMod.LOADED.get(), mag - 1);
			stack.set(BoltRifleMod.CHAMBERED.get(), true);
		}
		startAction(player, stack, ACTION_FIRE, RawAnimationName.FIRE);

		play(level, player, SoundEvents.FIREWORK_ROCKET_LARGE_BLAST, 3.0f, 0.55f);
		play(level, player, SoundEvents.FIREWORK_ROCKET_BLAST, 2.0f, 0.5f);
		play(level, player, SoundEvents.CROSSBOW_SHOOT, 1.0f, 0.5f);
		shoot(level, player, aiming);
	}

	private void shoot(ServerLevel level, ServerPlayer player, boolean aiming) {
		float spread = aiming ? SPREAD_ADS_DEGREES : SPREAD_HIP_DEGREES;
		float dYaw = (float) (level.random.nextGaussian() * spread * 0.5);
		float dPitch = (float) (level.random.nextGaussian() * spread * 0.5);
		Vec3 start = player.getEyePosition();
		Vec3 dir = Vec3.directionFromRotation(player.getXRot() + dPitch, player.getYRot() + dYaw);
		Vec3 end = start.add(dir.scale(RANGE));

		BlockHitResult blockHit = level.clip(new ClipContext(start, end,
				ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, player));
		Vec3 limit = blockHit.getType() == HitResult.Type.MISS ? end : blockHit.getLocation();

		AABB searchBox = player.getBoundingBox().expandTowards(dir.scale(RANGE)).inflate(1.0);
		EntityHitResult entityHit = ProjectileUtil.getEntityHitResult(level, player, start, limit, searchBox,
				e -> !e.isSpectator() && e.isAttackable() && e.isPickable());

		Vec3 impact = limit;
		if (entityHit != null) {
			Entity target = entityHit.getEntity();
			impact = entityHit.getLocation();
			float damage = DAMAGE;
			if (target instanceof LivingEntity living && impact.y >= living.getEyeY() - 0.3) {
				damage *= HEADSHOT_MULTIPLIER;
				hint(player, Component.literal("Headshot!").withStyle(ChatFormatting.GOLD));
			}
			target.hurt(level.damageSources().playerAttack(player), damage);
		} else if (blockHit.getType() == HitResult.Type.BLOCK) {
			BlockState state = level.getBlockState(blockHit.getBlockPos());
			level.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, state),
					impact.x, impact.y, impact.z, 10, 0.1, 0.1, 0.1, 0.05);
		}

		// tracer + muzzle smoke
		Vec3 path = impact.subtract(start);
		double length = path.length();
		Vec3 step = path.normalize().scale(2.0);
		Vec3 pos = start.add(dir.scale(1.5));
		for (double d = 1.5; d < length; d += 2.0) {
			level.sendParticles(ParticleTypes.CRIT, pos.x, pos.y, pos.z, 1, 0, 0, 0, 0);
			pos = pos.add(step);
		}
		Vec3 muzzle = start.add(dir.scale(1.6));
		level.sendParticles(ParticleTypes.SMOKE, muzzle.x, muzzle.y - 0.15, muzzle.z, 6, 0.05, 0.05, 0.05, 0.02);
		level.sendParticles(ParticleTypes.SMOKE, impact.x, impact.y, impact.z, 3, 0.05, 0.05, 0.05, 0.01);
	}

	private void reload(ServerPlayer player, ItemStack stack) {
		if (isBusy(stack)) {
			return;
		}
		int mag = getLoaded(stack);
		boolean needChamber = !isChambered(stack);
		int space = MAGAZINE_SIZE - mag;
		if (space <= 0 && !needChamber) {
			hint(player, Component.literal("Magazine is full").withStyle(ChatFormatting.GRAY));
			return;
		}

		// A full load from empty is 5 in the mag + 1 chambered, so ask for one extra when chambering.
		int want = space + (needChamber ? 1 : 0);
		int taken = 0;
		if (player.isCreative()) {
			taken = want;
		} else {
			Inventory inv = player.getInventory();
			for (int i = 0; i < inv.getContainerSize() && taken < want; i++) {
				ItemStack slot = inv.getItem(i);
				if (slot.is(BoltRifleMod.RIFLE_ROUND.get())) {
					int use = Math.min(slot.getCount(), want - taken);
					slot.shrink(use);
					taken += use;
				}
			}
		}
		if (taken == 0) {
			play(player.level(), player, SoundEvents.DISPENSER_FAIL, 1.0f, 1.2f);
			hint(player, Component.literal("No rifle rounds in your inventory").withStyle(ChatFormatting.RED));
			return;
		}

		stack.set(BoltRifleMod.PENDING.get(), taken);
		if (needChamber) {
			startAction(player, stack, ACTION_RELOAD_CHAMBER, RawAnimationName.RELOAD_CHAMBER);
		} else {
			startAction(player, stack, ACTION_RELOAD, RawAnimationName.RELOAD);
		}
	}

	// ------------------------------------------------------------------ timed actions

	@Override
	public void inventoryTick(ItemStack stack, Level level, Entity entity, int slot, boolean selected) {
		if (level.isClientSide || !(entity instanceof ServerPlayer player)) {
			return;
		}
		int action = getAction(stack);
		if (action == ACTION_NONE) {
			return;
		}
		long elapsed = level.getGameTime() - stack.getOrDefault(BoltRifleMod.ACTION_START.get(), 0L);

		if (!selected) { // put away mid-action
			if (action == ACTION_RELOAD || action == ACTION_RELOAD_CHAMBER) {
				refundPending(player, stack);
			}
			clearAction(stack);
			return;
		}

		for (Cue cue : CUES[action]) {
			if (cue.tick() == elapsed) {
				play(level, player, cue.sound(), cue.volume(), cue.pitch());
			}
		}
		if (elapsed >= DURATION[action]) {
			finish(stack, action);
		}
	}

	private static void finish(ItemStack stack, int action) {
		if (action == ACTION_RELOAD || action == ACTION_RELOAD_CHAMBER) {
			int total = Math.min(MAGAZINE_SIZE + 1,
					getLoaded(stack) + stack.getOrDefault(BoltRifleMod.PENDING.get(), 0));
			if (action == ACTION_RELOAD_CHAMBER && total > 0) {
				total -= 1;
				stack.set(BoltRifleMod.CHAMBERED.get(), true);
			}
			stack.set(BoltRifleMod.LOADED.get(), Math.min(total, MAGAZINE_SIZE));
		}
		clearAction(stack);
	}

	private static void refundPending(ServerPlayer player, ItemStack stack) {
		int pending = stack.getOrDefault(BoltRifleMod.PENDING.get(), 0);
		if (pending > 0 && !player.isCreative()) {
			ItemStack ammo = new ItemStack(BoltRifleMod.RIFLE_ROUND.get(), pending);
			if (!player.getInventory().add(ammo)) {
				player.drop(ammo, false);
			}
		}
	}

	// ------------------------------------------------------------------ vanilla behaviour overrides

	/** Left click is "fire", never melee. */
	@Override
	public boolean onLeftClickEntity(ItemStack stack, Player player, Entity entity) {
		return true;
	}

	/** No digging with a rifle (creative would otherwise instantly break blocks). */
	@Override
	public boolean canAttackBlock(BlockState state, Level level, net.minecraft.core.BlockPos pos, Player player) {
		return false;
	}

	@Override
	public float getDestroySpeed(ItemStack stack, BlockState state) {
		return 0.0f;
	}

	/** Ammo changes must not make the rifle "re-raise" in first person. */
	@Override
	public boolean shouldCauseReequipAnimation(ItemStack oldStack, ItemStack newStack, boolean slotChanged) {
		return slotChanged || !oldStack.is(newStack.getItem());
	}

	// ------------------------------------------------------------------ item bar + tooltip

	@Override
	public boolean isBarVisible(ItemStack stack) {
		return true;
	}

	@Override
	public int getBarWidth(ItemStack stack) {
		return Mth.clamp(Math.round(13.0f * getLoaded(stack) / MAGAZINE_SIZE), 0, 13);
	}

	@Override
	public int getBarColor(ItemStack stack) {
		return getLoaded(stack) == 0 && !isChambered(stack) ? 0xCC3333 : 0xE0A030;
	}

	@Override
	public void appendHoverText(ItemStack stack, Item.TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
		tooltip.add(Component.literal("Magazine: " + getLoaded(stack) + "/" + MAGAZINE_SIZE
				+ (isChambered(stack) ? "  +1 chambered" : "  (chamber empty)")).withStyle(ChatFormatting.GRAY));
		tooltip.add(Component.literal("Left click: fire   Hold right click: scope").withStyle(ChatFormatting.DARK_GRAY));
		tooltip.add(Component.literal("R: reload   Scroll while scoped: zoom").withStyle(ChatFormatting.DARK_GRAY));
	}

	// ------------------------------------------------------------------ GeckoLib

	@Override
	public void createGeoRenderer(Consumer<GeoRenderProvider> consumer) {
		consumer.accept(new GeoRenderProvider() {
			private RifleRenderer renderer;

			@Override
			public BlockEntityWithoutLevelRenderer getGeoItemRenderer() {
				if (this.renderer == null) {
					this.renderer = new RifleRenderer();
				}
				return this.renderer;
			}
		});
	}

	@Override
	public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
		controllers.add(new AnimationController<RifleItem>(this, CONTROLLER, 0, state -> state.setAndContinue(IDLE))
				.triggerableAnim("fire", FIRE)
				.triggerableAnim("dry", DRY)
				.triggerableAnim("reload", RELOAD)
				.triggerableAnim("reload_chamber", RELOAD_CHAMBER));
	}

	@Override
	public AnimatableInstanceCache getAnimatableInstanceCache() {
		return this.cache;
	}
}
