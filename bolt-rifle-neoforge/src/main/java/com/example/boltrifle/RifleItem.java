package com.example.boltrifle;

import net.minecraft.ChatFormatting;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

import java.util.List;

/**
 * Bolt-action rifle.
 *
 * Right-click          : fire (if loaded), otherwise reload.
 * Sneak + right-click  : reload (tops the magazine up to 5 rounds from your inventory).
 */
public class RifleItem extends Item {
	public static final int MAGAZINE_SIZE = 5;
	public static final float DAMAGE = 14.0f;            // 7 hearts
	public static final double RANGE = 64.0;
	public static final int BOLT_COOLDOWN_TICKS = 25;    // time to work the bolt between shots
	public static final int RELOAD_COOLDOWN_TICKS = 40;  // time to reload

	public RifleItem(Properties properties) {
		super(properties);
	}

	public static int getLoaded(ItemStack stack) {
		return stack.getOrDefault(BoltRifleMod.LOADED.get(), 0);
	}

	@Override
	public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
		ItemStack stack = player.getItemInHand(hand);

		// The server does the real work; the client just agrees that the click was handled.
		if (level.isClientSide) {
			return InteractionResultHolder.consume(stack);
		}

		int loaded = getLoaded(stack);
		if (player.isShiftKeyDown() || loaded <= 0) {
			return reload(level, player, stack);
		}
		return fire(level, player, stack, loaded);
	}

	private InteractionResultHolder<ItemStack> fire(Level level, Player player, ItemStack stack, int loaded) {
		stack.set(BoltRifleMod.LOADED.get(), loaded - 1);

		play(level, player, SoundEvents.FIREWORK_ROCKET_BLAST, 1.2f, 0.7f);
		play(level, player, SoundEvents.CROSSBOW_SHOOT, 1.0f, 0.6f);

		Vec3 start = player.getEyePosition();
		Vec3 dir = player.getViewVector(1.0f);
		Vec3 end = start.add(dir.scale(RANGE));

		// Stop the shot at the first solid block.
		BlockHitResult blockHit = level.clip(new ClipContext(
				start, end,
				ClipContext.Block.COLLIDER,
				ClipContext.Fluid.NONE,
				player));
		Vec3 limit = blockHit.getType() == HitResult.Type.MISS ? end : blockHit.getLocation();

		// Find the first entity along the line before that block.
		AABB searchBox = player.getBoundingBox().expandTowards(dir.scale(RANGE)).inflate(1.0);
		EntityHitResult entityHit = ProjectileUtil.getEntityHitResult(
				level, player, start, limit, searchBox,
				e -> !e.isSpectator() && e.isAttackable() && e.isPickable());

		Vec3 impact = limit;
		if (entityHit != null) {
			Entity target = entityHit.getEntity();
			impact = entityHit.getLocation();
			target.hurt(level.damageSources().playerAttack(player), DAMAGE);
		}

		// Little tracer so you can see where the shot went.
		if (level instanceof ServerLevel serverLevel) {
			Vec3 path = impact.subtract(start);
			double length = path.length();
			Vec3 step = path.normalize().scale(1.5);
			Vec3 pos = start.add(dir);
			for (double d = 1.0; d < length; d += 1.5) {
				serverLevel.sendParticles(ParticleTypes.CRIT, pos.x, pos.y, pos.z, 1, 0, 0, 0, 0);
				pos = pos.add(step);
			}
			serverLevel.sendParticles(ParticleTypes.SMOKE, impact.x, impact.y, impact.z, 4, 0.05, 0.05, 0.05, 0.01);
		}

		player.getCooldowns().addCooldown(this, BOLT_COOLDOWN_TICKS);

		if (loaded - 1 == 0) {
			player.displayClientMessage(
					Component.literal("Magazine empty - right-click to reload").withStyle(ChatFormatting.YELLOW), true);
		}
		return InteractionResultHolder.success(stack);
	}

	private InteractionResultHolder<ItemStack> reload(Level level, Player player, ItemStack stack) {
		int loaded = getLoaded(stack);
		int needed = MAGAZINE_SIZE - loaded;

		if (needed <= 0) {
			player.displayClientMessage(Component.literal("Magazine is full").withStyle(ChatFormatting.GRAY), true);
			return InteractionResultHolder.fail(stack);
		}

		int taken = 0;
		if (player.isCreative()) {
			taken = needed; // creative players don't need ammo
		} else {
			Inventory inv = player.getInventory();
			for (int i = 0; i < inv.getContainerSize() && taken < needed; i++) {
				ItemStack slot = inv.getItem(i);
				if (slot.is(BoltRifleMod.RIFLE_ROUND.get())) {
					int use = Math.min(slot.getCount(), needed - taken);
					slot.shrink(use);
					taken += use;
				}
			}
		}

		if (taken == 0) {
			play(level, player, SoundEvents.DISPENSER_FAIL, 1.0f, 1.2f);
			player.displayClientMessage(
					Component.literal("No rifle rounds in your inventory").withStyle(ChatFormatting.RED), true);
			return InteractionResultHolder.fail(stack);
		}

		stack.set(BoltRifleMod.LOADED.get(), loaded + taken);
		play(level, player, SoundEvents.IRON_TRAPDOOR_OPEN, 0.8f, 1.4f);
		play(level, player, SoundEvents.IRON_TRAPDOOR_CLOSE, 0.8f, 1.2f);
		player.getCooldowns().addCooldown(this, RELOAD_COOLDOWN_TICKS);
		player.displayClientMessage(
				Component.literal("Loaded " + (loaded + taken) + "/" + MAGAZINE_SIZE).withStyle(ChatFormatting.GREEN), true);
		return InteractionResultHolder.success(stack);
	}

	private static void play(Level level, Player player, SoundEvent sound, float volume, float pitch) {
		level.playSound(null, player.getX(), player.getY(), player.getZ(), sound, SoundSource.PLAYERS, volume, pitch);
	}

	// --- Ammo shown as a bar under the item icon -------------------------------------------

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
		return getLoaded(stack) == 0 ? 0xCC3333 : 0xE0A030;
	}

	@Override
	public void appendHoverText(ItemStack stack, Item.TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
		tooltip.add(Component.literal("Loaded: " + getLoaded(stack) + "/" + MAGAZINE_SIZE).withStyle(ChatFormatting.GRAY));
		tooltip.add(Component.literal("Right-click: fire / reload when empty").withStyle(ChatFormatting.DARK_GRAY));
		tooltip.add(Component.literal("Sneak + right-click: reload").withStyle(ChatFormatting.DARK_GRAY));
	}
}
