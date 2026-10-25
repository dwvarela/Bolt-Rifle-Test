package com.example.boltrifle;

import com.example.boltrifle.GunDef.Cue;
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
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
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
 * One class for every firearm; {@link GunDef} says how each one behaves.
 *
 * Left click = fire, hold right click = aim, R = swap magazines. The server owns all ammo state and
 * timing; GeckoLib plays the animations. A gun holds one magazine plus one round in the chamber.
 */
public class GunItem extends Item implements GeoItem {
	public static final int ACTION_NONE = 0;
	public static final int ACTION_FIRE = 1;              // recoil + cycling
	public static final int ACTION_RELOAD = 2;            // magazine swap only
	public static final int ACTION_RELOAD_CHAMBER = 3;    // magazine swap + charging the gun
	public static final int ACTION_DRY = 4;               // click
	public static final int ACTION_RELOAD_RELEASE = 5;    // magazine swap with the bolt locked open, then release it

	private static final String CONTROLLER = "main";

	public final GunDef def;
	private final RawAnimation idle, idleOpen, fireAnim, fireAnimB, fireLastAnim, dryAnim, dryAnimB, dryOpenAnim, dryOpenAnimB, reloadAnim, reloadChamberAnim, reloadReleaseAnim;
	private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);

	public GunItem(Properties properties, GunDef def) {
		super(properties);
		this.def = def;
		String p = "animation." + def.id + ".";
		this.idle = RawAnimation.begin().thenLoop(p + "idle");
		this.idleOpen = RawAnimation.begin().thenLoop(p + "idle_open");
		this.fireAnim = RawAnimation.begin().thenPlay(p + "fire");
		this.fireAnimB = RawAnimation.begin().thenPlay(p + "fire_b");
		this.fireLastAnim = RawAnimation.begin().thenPlayAndHold(p + "fire_last");
		this.reloadReleaseAnim = RawAnimation.begin().thenPlay(p + "reload_release");
		this.dryAnim = RawAnimation.begin().thenPlay(p + "dryfire");
		this.dryAnimB = RawAnimation.begin().thenPlay(p + "dryfire_b");
		this.dryOpenAnim = RawAnimation.begin().thenPlay(p + "dryfire_open");
		this.dryOpenAnimB = RawAnimation.begin().thenPlay(p + "dryfire_open_b");
		this.reloadAnim = RawAnimation.begin().thenPlay(p + "reload");
		this.reloadChamberAnim = RawAnimation.begin().thenPlay(p + "reload_chamber");
		SingletonGeoAnimatable.registerSyncedAnimatable(this);
	}

	// ------------------------------------------------------------------ state helpers

	public static int getLoaded(ItemStack stack) {
		return stack.getOrDefault(BoltRifleMod.LOADED.get(), 0);
	}

	public static boolean isChambered(ItemStack stack) {
		return stack.getOrDefault(BoltRifleMod.CHAMBERED.get(), false);
	}

	public static boolean hasMag(ItemStack stack) {
		return stack.getOrDefault(BoltRifleMod.HAS_MAG.get(), false);
	}

	public static int getAction(ItemStack stack) {
		return stack.getOrDefault(BoltRifleMod.ACTION.get(), ACTION_NONE);
	}

	public static boolean isReloading(int action) {
		return action == ACTION_RELOAD || action == ACTION_RELOAD_CHAMBER || action == ACTION_RELOAD_RELEASE;
	}

	public static boolean isBoltOpen(ItemStack stack) {
		return stack.getOrDefault(BoltRifleMod.BOLT_OPEN.get(), false);
	}

	/** True when the selector is on full auto (and the gun can do it). */
	public boolean autoMode(ItemStack stack) {
		return def.auto && stack.getOrDefault(BoltRifleMod.AUTO_MODE.get(), true);
	}

	public static boolean isBusy(ItemStack stack) {
		return getAction(stack) != ACTION_NONE;
	}

	public Cartridge magRound(ItemStack stack) {
		return Cartridge.byId(stack.get(BoltRifleMod.AMMO.get()), def.defaultAmmo);
	}

	public Cartridge chamberRound(ItemStack stack) {
		return Cartridge.byId(stack.get(BoltRifleMod.CHAMBER_AMMO.get()), def.defaultAmmo);
	}

	private int actionLength(ItemStack stack, int action) {
		return stack.getOrDefault(BoltRifleMod.ACTION_LEN.get(), 1);
	}

	private static void clearAction(ItemStack stack) {
		stack.set(BoltRifleMod.ACTION.get(), ACTION_NONE);
		stack.set(BoltRifleMod.PENDING.get(), 0);
	}

	private void startAction(ServerPlayer player, ItemStack stack, int action, String anim, int length) {
		ServerLevel level = player.serverLevel();
		stack.set(BoltRifleMod.ACTION.get(), action);
		stack.set(BoltRifleMod.ACTION_START.get(), level.getGameTime());
		stack.set(BoltRifleMod.ACTION_LEN.get(), length);
		triggerAnim(player, GeoItem.getOrAssignId(stack, level), CONTROLLER, anim);
	}

	/** Vanilla placeholder sounds used in the cue tables -> the loud custom gun sounds. */
	private static SoundEvent custom(SoundEvent s) {
		String n = s == SoundEvents.LEVER_CLICK ? "click"
				: s == SoundEvents.DISPENSER_FAIL ? "click_dry"
				: s == SoundEvents.IRON_TRAPDOOR_OPEN ? "bolt_open"
				: s == SoundEvents.IRON_TRAPDOOR_CLOSE ? "bolt_close"
				: s == SoundEvents.CROSSBOW_LOADING_START.value() ? "mag_out"
				: s == SoundEvents.CROSSBOW_LOADING_MIDDLE.value() ? "mag_in"
				: s == SoundEvents.CROSSBOW_LOADING_END.value() ? "rack"
				: s == SoundEvents.AMETHYST_BLOCK_HIT ? "shell" : null;
		return n == null ? s : BoltRifleMod.SND.get(n).get();
	}

	/** The custom sounds are mastered loud and clean (one copy each, no stacking); a volume above 1 only carries them farther. */
	private static void play(Level level, Entity e, SoundEvent sound, float volume, float pitch) {
		SoundEvent c = custom(sound);
		float vol = c != sound ? 3.0f : volume;
		if (c != sound) pitch = 0.97f + level.random.nextFloat() * 0.06f;        // recorded sounds: no cue pitch-shifting, just a touch of variation
		level.playSound(null, e.getX(), e.getY(), e.getZ(), c, SoundSource.PLAYERS, vol, Math.max(0.5f, Math.min(2.0f, pitch)));
	}

	private static void hint(Player player, Component text) {
		player.displayClientMessage(text, true);
	}

	// ------------------------------------------------------------------ input handlers (server side)

	public static void handleFire(ServerPlayer player, boolean aiming) {
		ItemStack stack = player.getMainHandItem();
		if (stack.getItem() instanceof GunItem gun) {
			gun.fire(player, stack, aiming);
		}
	}

	public static void handleToggle(ServerPlayer player) {
		ItemStack stack = player.getMainHandItem();
		if (stack.getItem() instanceof GunItem gun && gun.def.auto && gun.def.selector) {
			boolean auto = !gun.autoMode(stack);
			stack.set(BoltRifleMod.AUTO_MODE.get(), auto);
			play(player.level(), player, SoundEvents.LEVER_CLICK, 0.8f, auto ? 1.5f : 1.2f);
			hint(player, Component.literal("Fire mode: " + (auto ? "AUTO" : "SEMI")).withStyle(ChatFormatting.YELLOW));
		}
	}

	/** B: fits the attachment held in the off hand, or (empty off hand) removes the optic, then the muzzle device. */
	public static void handleAttach(ServerPlayer player) {
		ItemStack gunStack = player.getMainHandItem();
		if (!(gunStack.getItem() instanceof GunItem gun)) {
			return;
		}
		if (isBusy(gunStack)) {
			hint(player, Component.literal("Wait until the gun is ready").withStyle(ChatFormatting.YELLOW));
			return;
		}
		ItemStack off = player.getOffhandItem();
		if (off.getItem() instanceof AttachmentItem ai) {
			Attachment a = ai.attachment;
			var type = a.slot == Attachment.Slot.OPTIC ? BoltRifleMod.ATTACH_OPTIC : BoltRifleMod.ATTACH_MUZZLE;
			if (a.slot == Attachment.Slot.OPTIC && gun.def.optic == null) {
				hint(player, Component.literal(gun.def.display + " has no rail for an optic").withStyle(ChatFormatting.RED));
				return;
			}
			Attachment old = Attachment.byId(gunStack.get(type.get()));
			gunStack.set(type.get(), a.id);
			off.shrink(1);
			if (old != null) {
				giveBack(player, old);
			}
			play(player.level(), player, SoundEvents.IRON_TRAPDOOR_CLOSE, 0.7f, 1.7f);
			hint(player, Component.literal("Fitted: " + a.display).withStyle(ChatFormatting.GREEN));
			return;
		}
		for (var type : List.of(BoltRifleMod.ATTACH_OPTIC, BoltRifleMod.ATTACH_MUZZLE)) {
			Attachment cur = Attachment.byId(gunStack.get(type.get()));
			if (cur != null) {
				gunStack.remove(type.get());
				giveBack(player, cur);
				play(player.level(), player, SoundEvents.IRON_TRAPDOOR_OPEN, 0.7f, 1.7f);
				hint(player, Component.literal("Removed: " + cur.display).withStyle(ChatFormatting.YELLOW));
				return;
			}
		}
		hint(player, Component.literal("Hold an attachment in the off hand, then press B").withStyle(ChatFormatting.GRAY));
	}

	private static void giveBack(ServerPlayer player, Attachment a) {
		ItemStack st = new ItemStack(BoltRifleMod.ATTACHMENTS.get(a).get());
		if (!player.getInventory().add(st)) {
			player.drop(st, false);
		}
	}

	public static void handleReload(ServerPlayer player) {
		ItemStack stack = player.getMainHandItem();
		if (stack.getItem() instanceof GunItem gun) {
			gun.reload(player, stack);
		}
	}

	/** Finishes the current action if its time is up. Returns true when the gun is free. */
	private boolean settle(ServerPlayer player, ItemStack stack) {
		int action = getAction(stack);
		if (action == ACTION_NONE) {
			return true;
		}
		long elapsed = player.level().getGameTime() - stack.getOrDefault(BoltRifleMod.ACTION_START.get(), 0L);
		if (elapsed >= actionLength(stack, action)) {
			finish(player, stack, action);
			return true;
		}
		return false;
	}

	/** Alternates between twin animations so a new shot always restarts the animation. */
	private boolean flip;

	/**
	 * A shot is allowed when the gun is free or still in its own recoil cycle, and the shot schedule allows it.
	 * The schedule (NEXT_SHOT, in 1/100 tick) advances by exactly one interval per shot, so the long-run rate is
	 * always the gun's rate of fire no matter how the click packets are spaced; two ticks of slack absorb network jitter.
	 */
	private boolean readyToFire(ServerPlayer player, ItemStack stack) {
		int action = getAction(stack);
		if (action != ACTION_NONE && action != ACTION_FIRE && !settle(player, stack)) {
			return false;
		}
		long now = player.level().getGameTime() * 100L;
		return now >= stack.getOrDefault(BoltRifleMod.NEXT_SHOT.get(), 0L) - 200L;
	}

	private void scheduleNextShot(ServerPlayer player, ItemStack stack) {
		long now = player.level().getGameTime() * 100L;
		long base = Math.max(stack.getOrDefault(BoltRifleMod.NEXT_SHOT.get(), 0L), now - 50L);
		stack.set(BoltRifleMod.NEXT_SHOT.get(), base + Math.round(def.interval * 100.0));
	}

	private void fire(ServerPlayer player, ItemStack stack, boolean aiming) {
		if (!readyToFire(player, stack)) {
			return;
		}
		ServerLevel level = player.serverLevel();
		if (!isChambered(stack)) {
			startAction(player, stack, ACTION_DRY, def.holdOpen && isBoltOpen(stack) ? ((flip = !flip) ? "dry_open" : "dry_open_b") : ((flip = !flip) ? "dry" : "dry_b"), def.dryTicks);
			hint(player, Component.literal(getLoaded(stack) > 0 ? "Not chambered"
					: hasMag(stack) ? "Magazine empty - press R" : "No magazine - press R").withStyle(ChatFormatting.YELLOW));
			return;
		}

		Cartridge round = chamberRound(stack);
		Chamber.Fit fit = def.chamber.fit(round);
		boolean mismatch = fit != Chamber.Fit.SAFE;
		if (mismatch && level.random.nextDouble() < GunConfig.UNSAFE_FAILURE_CHANCE.get()) {
			rupture(player, stack);
			return;
		}

		scheduleNextShot(player, stack);
		stack.set(BoltRifleMod.CHAMBERED.get(), false);
		int mag = getLoaded(stack);
		if (mag > 0) {                     // cycling chambers the next round
			stack.set(BoltRifleMod.LOADED.get(), mag - 1);
			stack.set(BoltRifleMod.CHAMBERED.get(), true);
			stack.set(BoltRifleMod.CHAMBER_AMMO.get(), magRound(stack).itemId);
		}
		float acc = stack.getOrDefault(BoltRifleMod.FIRE_ACC.get(), 0.0f) + (float) def.interval;
		int length = Math.max(1, (int) acc);
		stack.set(BoltRifleMod.FIRE_ACC.get(), acc - length);
		boolean last = def.holdOpen && mag == 0;
		if (last) {
			stack.set(BoltRifleMod.BOLT_OPEN.get(), true);
		}
		startAction(player, stack, ACTION_FIRE, last ? "fire_last" : ((flip = !flip) ? "fire" : "fire_b"), length);

		Attachment muzzle = Attachment.muzzle(stack);
		float loud = def.boom * (muzzle == null ? 1.0f : muzzle.boom);
		boolean quiet = loud < 0.5f;                              // suppressed
		String fam = def.boomPitch < 1.07f ? "shot_heavy" : def.boomPitch < 1.2f ? "shot" : "shot_light";
		// suppressed: the same shot, 40% quieter (the _supp samples are mastered at 0.6 amplitude; game gain clamps at 1.0, so the sample carries it)
		SoundEvent shotSound = BoltRifleMod.SND.get(quiet ? fam + "_supp" : fam).get();
		level.playSound(null, player.getX(), player.getY(), player.getZ(), shotSound, SoundSource.PLAYERS, quiet ? 1.8f : 3.0f, 1.0f);
		shoot(level, player, round, aiming, muzzle);
		wear(player, stack, mismatch ? GunConfig.UNSAFE_WEAR.get() : 1);
	}

	private void shoot(ServerLevel level, ServerPlayer player, Cartridge round, boolean aiming, Attachment mz) {
		float spread = aiming ? def.spreadAds : def.spreadHip;
		float dYaw = (float) (level.random.nextGaussian() * spread * 0.5);
		float dPitch = (float) (level.random.nextGaussian() * spread * 0.5);
		Vec3 start = player.getEyePosition();
		Vec3 dir = Vec3.directionFromRotation(player.getXRot() + dPitch, player.getYRot() + dYaw);
		double range = round.maxRange;
		Vec3 end = start.add(dir.scale(range));

		BlockHitResult blockHit = level.clip(new ClipContext(start, end,
				ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, player));
		Vec3 limit = blockHit.getType() == HitResult.Type.MISS ? end : blockHit.getLocation();

		AABB searchBox = player.getBoundingBox().expandTowards(dir.scale(range)).inflate(1.0);
		EntityHitResult entityHit = ProjectileUtil.getEntityHitResult(level, player, start, limit, searchBox,
				e -> !e.isSpectator() && e.isAttackable() && e.isPickable());

		Vec3 impact = limit;
		if (entityHit != null) {
			Entity target = entityHit.getEntity();
			impact = entityHit.getLocation();
			float damage = round.damage * def.damageScale * (mz == null ? 1.0f : mz.damage) * GunConfig.DAMAGE_SCALE.get().floatValue()
					* round.falloff(start.distanceTo(impact));
			if (target instanceof LivingEntity living) {
				int armor = living.getArmorValue();
				if (armor > 0) {
					damage *= 1.0f + round.armorPierce * Math.min(1.0f, armor / 20.0f);
				}
				if (impact.y >= living.getEyeY() - 0.3) {
					damage *= def.headshot;
					hint(player, Component.literal("Headshot!").withStyle(ChatFormatting.GOLD));
				}
			}
			target.hurt(level.damageSources().playerAttack(player), damage);
		} else if (blockHit.getType() == HitResult.Type.BLOCK) {
			BlockState state = level.getBlockState(blockHit.getBlockPos());
			level.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, state),
					impact.x, impact.y, impact.z, 6, 0.08, 0.08, 0.08, 0.04);
		}

		// Effects for everyone EXCEPT the shooter, who sees the model's own muzzle flash at the barrel.
		Vec3 look = player.getLookAngle();
		Vec3 right = look.cross(new Vec3(0, 1, 0)).normalize();
		Vec3 muzzle = start.add(look.scale(1.3)).add(right.scale(0.3)).add(0, -0.3, 0);
		Vec3 path = impact.subtract(start);
		double length = path.length();
		Vec3 step = path.normalize().scale(4.0);
		for (ServerPlayer viewer : level.players()) {
			if (viewer == player || viewer.distanceToSqr(muzzle) > 96.0 * 96.0) {
				continue;
			}
			level.sendParticles(viewer, ParticleTypes.SMOKE, false, muzzle.x, muzzle.y, muzzle.z, 2, 0.03, 0.03, 0.03, 0.01);
			if (mz == null || !mz.hidesFlash) level.sendParticles(viewer, ParticleTypes.FLAME, false, muzzle.x, muzzle.y, muzzle.z, 1, 0.01, 0.01, 0.01, 0.02);
			Vec3 pos = muzzle.add(step);
			for (double d = 4.0; d < length; d += 4.0) {
				level.sendParticles(viewer, ParticleTypes.CRIT, false, pos.x, pos.y, pos.z, 1, 0, 0, 0, 0);
				pos = pos.add(step);
			}
		}
		level.sendParticles(ParticleTypes.SMOKE, impact.x, impact.y, impact.z, 1, 0.03, 0.03, 0.03, 0.005);
	}

	/** Durability loss for a shot; the gun is destroyed when it hits zero. */
	private void wear(ServerPlayer player, ItemStack stack, int amount) {
		int damage = stack.getDamageValue() + amount;
		if (damage >= stack.getMaxDamage()) {
			play(player.level(), player, SoundEvents.ITEM_BREAK, 0.9f, 0.9f);
			hint(player, Component.literal("Your gun is worn out").withStyle(ChatFormatting.RED));
			returnMagazine(player, stack);
			stack.shrink(1);
		} else {
			stack.setDamageValue(damage);
		}
	}

	/** A mismatched round ruptures the chamber: the gun is destroyed and the shooter is hurt. */
	private void rupture(ServerPlayer player, ItemStack stack) {
		ServerLevel level = player.serverLevel();
		play(level, player, SoundEvents.GENERIC_EXPLODE.value(), 1.2f, 1.4f);
		Vec3 p = player.getEyePosition().add(player.getLookAngle().scale(0.8));
		level.sendParticles(ParticleTypes.EXPLOSION, p.x, p.y - 0.2, p.z, 1, 0, 0, 0, 0);
		level.sendParticles(ParticleTypes.LARGE_SMOKE, p.x, p.y - 0.2, p.z, 12, 0.15, 0.15, 0.15, 0.03);
		level.sendParticles(ParticleTypes.FLAME, p.x, p.y - 0.2, p.z, 10, 0.1, 0.1, 0.1, 0.08);
		player.hurt(level.damageSources().explosion(null, null), GunConfig.FAILURE_DAMAGE.get().floatValue());
		hint(player, Component.literal("The wrong round ruptured the chamber!").withStyle(ChatFormatting.DARK_RED));
		returnMagazine(player, stack);
		stack.shrink(1);
	}

	private void returnMagazine(ServerPlayer player, ItemStack stack) {
		if (hasMag(stack)) {
			MagItem.giveOrDrop(player, MagItem.make(def.mag, getLoaded(stack), magRound(stack)));
		}
	}

	private void reload(ServerPlayer player, ItemStack stack) {
		if (!settle(player, stack)) {
			return;
		}
		Inventory inv = player.getInventory();
		int slot = -1, best = 0;
		for (int i = 0; i < inv.getContainerSize(); i++) {
			ItemStack s = inv.getItem(i);
			if (s.getItem() instanceof MagItem m && m.type == def.mag && MagItem.rounds(s) > best
					&& MagItem.ammo(s) != null) {
				best = MagItem.rounds(s);
				slot = i;
			}
		}
		boolean virtual = false;
		if (slot < 0) {
			if (player.isCreative()) {          // creative always has a full magazine of the standard round
				virtual = true;
				best = def.mag.capacity;
			} else {
				play(player.level(), player, SoundEvents.DISPENSER_FAIL, 1.0f, 1.2f);
				hint(player, Component.literal("No loaded " + def.mag.display + " in your inventory")
						.withStyle(ChatFormatting.RED));
				return;
			}
		}
		if (hasMag(stack) && getLoaded(stack) >= best) {
			hint(player, Component.literal(getLoaded(stack) >= def.mag.capacity ? "Magazine is full"
					: "No fuller magazine to swap in").withStyle(ChatFormatting.GRAY));
			return;
		}

		String ammoId = def.defaultAmmo.itemId;
		if (!virtual) {
			ItemStack s = inv.getItem(slot);
			ammoId = MagItem.ammo(s).itemId;
			s.shrink(1);
		}
		stack.set(BoltRifleMod.PENDING.get(), best);
		stack.set(BoltRifleMod.PENDING_AMMO.get(), ammoId);
		if (!isChambered(stack)) {
			if (def.holdOpen && isBoltOpen(stack)) {
				startAction(player, stack, ACTION_RELOAD_RELEASE, "reload_release", def.reloadReleaseTicks);
			} else {
				startAction(player, stack, ACTION_RELOAD_CHAMBER, "reload_chamber", def.reloadChamberTicks);
			}
		} else {
			startAction(player, stack, ACTION_RELOAD, "reload", def.reloadTicks);
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
			if (isReloading(action)) {
				refundPending(player, stack);
			}
			clearAction(stack);
			return;
		}

		for (Cue cue : def.cues[action]) {
			if (cue.tick() == elapsed) {
				play(level, player, cue.sound(), cue.volume(), cue.pitch());
			}
		}
		if (elapsed >= actionLength(stack, action)) {
			finish(player, stack, action);
		}
	}

	private void finish(ServerPlayer player, ItemStack stack, int action) {
		if (isReloading(action)) {
			returnMagazine(player, stack);                   // the old magazine comes out...
			int rounds = stack.getOrDefault(BoltRifleMod.PENDING.get(), 0);
			stack.set(BoltRifleMod.LOADED.get(), rounds);    // ...and the fresh one goes in
			stack.set(BoltRifleMod.AMMO.get(), stack.getOrDefault(BoltRifleMod.PENDING_AMMO.get(), def.defaultAmmo.itemId));
			stack.set(BoltRifleMod.HAS_MAG.get(), true);
			if (action != ACTION_RELOAD && rounds > 0 && !isChambered(stack)) {
				stack.set(BoltRifleMod.BOLT_OPEN.get(), false);
				stack.set(BoltRifleMod.LOADED.get(), rounds - 1);
				stack.set(BoltRifleMod.CHAMBERED.get(), true);
				stack.set(BoltRifleMod.CHAMBER_AMMO.get(), magRound(stack).itemId);
			}
		}
		clearAction(stack);
	}

	/** The reload was cancelled: the magazine taken from the inventory goes back. */
	private void refundPending(ServerPlayer player, ItemStack stack) {
		int pending = stack.getOrDefault(BoltRifleMod.PENDING.get(), 0);
		if (pending > 0 && !player.isCreative()) {
			Cartridge c = Cartridge.byId(stack.get(BoltRifleMod.PENDING_AMMO.get()), def.defaultAmmo);
			MagItem.giveOrDrop(player, MagItem.make(def.mag, pending, c));
		}
	}

	// ------------------------------------------------------------------ vanilla behaviour overrides

	/** Left click is "fire", never melee. */
	@Override
	public boolean onLeftClickEntity(ItemStack stack, Player player, Entity entity) {
		return true;
	}

	/** No digging with a gun (creative would otherwise instantly break blocks). */
	@Override
	public boolean canAttackBlock(BlockState state, Level level, net.minecraft.core.BlockPos pos, Player player) {
		return false;
	}

	@Override
	public float getDestroySpeed(ItemStack stack, BlockState state) {
		return 0.0f;
	}

	/** Ammo and wear changes must not make the gun "re-raise" in first person. */
	@Override
	public boolean shouldCauseReequipAnimation(ItemStack oldStack, ItemStack newStack, boolean slotChanged) {
		return slotChanged || !oldStack.is(newStack.getItem());
	}

	@Override
	public boolean isValidRepairItem(ItemStack stack, ItemStack repairCandidate) {
		return repairCandidate.is(Items.IRON_INGOT);
	}

	// ------------------------------------------------------------------ tooltip

	@Override
	public void appendHoverText(ItemStack stack, Item.TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
		tooltip.add(Component.literal("Chambered in " + def.chamber.label).withStyle(ChatFormatting.GOLD));
		String mag = hasMag(stack)
				? getLoaded(stack) + "/" + def.mag.capacity + "  " + magRound(stack).display
				: "no magazine";
		tooltip.add(Component.literal("Magazine: " + mag + (isChambered(stack) ? "   +1 " + chamberRound(stack).display
				: "   (chamber empty)")).withStyle(ChatFormatting.GRAY));
		tooltip.add(Component.literal("Uses: " + def.mag.display).withStyle(ChatFormatting.DARK_GRAY));
		tooltip.add(Component.literal("Left click: fire   Hold right click: aim   R: swap magazine")
				.withStyle(ChatFormatting.DARK_GRAY));
		if (def.scoped) {
			tooltip.add(Component.literal("Scroll while scoped: zoom").withStyle(ChatFormatting.DARK_GRAY));
		}
		if (def.auto && def.selector) {
			tooltip.add(Component.literal("V: switch semi / auto   (now " + (autoMode(stack) ? "AUTO" : "SEMI") + ")")
					.withStyle(ChatFormatting.DARK_GRAY));
		}
		Attachment optic = Attachment.optic(stack), muz = Attachment.muzzle(stack);
		if (optic != null || muz != null) {
			tooltip.add(Component.literal("Fitted: " + (optic != null ? optic.display : "")
					+ (optic != null && muz != null ? ", " : "") + (muz != null ? muz.display : "")).withStyle(ChatFormatting.AQUA));
		}
		tooltip.add(Component.literal("B: fit off-hand attachment / remove").withStyle(ChatFormatting.DARK_GRAY));
		tooltip.add(Component.literal("Repair: iron ingot on an anvil").withStyle(ChatFormatting.DARK_GRAY));
	}

	// ------------------------------------------------------------------ GeckoLib

	@Override
	public void createGeoRenderer(Consumer<GeoRenderProvider> consumer) {
		final GunDef gun = this.def;
		consumer.accept(new GeoRenderProvider() {
			private GunRenderer renderer;

			@Override
			public BlockEntityWithoutLevelRenderer getGeoItemRenderer() {
				if (this.renderer == null) {
					this.renderer = new GunRenderer(gun);
				}
				return this.renderer;
			}
		});
	}

	@Override
	public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
		controllers.add(new AnimationController<GunItem>(this, CONTROLLER, 0, state -> {
			// bolt locked back (empty magazine): keep showing it open whatever else happens (re-draw, animation end)
			ItemStack st = state.getData(software.bernie.geckolib.constant.DataTickets.ITEMSTACK);
			boolean open = def.holdOpen && st != null && isBoltOpen(st);
			return state.setAndContinue(open ? idleOpen : idle);
		})
				.triggerableAnim("fire", fireAnim)
				.triggerableAnim("fire_b", fireAnimB)
				.triggerableAnim("dry", dryAnim)
				.triggerableAnim("dry_b", dryAnimB)
				.triggerableAnim("dry_open", dryOpenAnim)
				.triggerableAnim("dry_open_b", dryOpenAnimB)
				.triggerableAnim("fire_last", fireLastAnim)
				.triggerableAnim("reload_release", reloadReleaseAnim)
				.triggerableAnim("reload", reloadAnim)
				.triggerableAnim("reload_chamber", reloadChamberAnim));
	}

	@Override
	public AnimatableInstanceCache getAnimatableInstanceCache() {
		return this.cache;
	}
}
