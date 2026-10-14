package com.example.boltrifle;

import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

/** Right click throws it (the fuse is already running); sneak for a soft underhand toss. */
public class GrenadeItem extends Item {
	public GrenadeItem(Properties props) {
		super(props);
	}

	@Override
	public InteractionResultHolder<ItemStack> use(Level level, Player player, net.minecraft.world.InteractionHand hand) {
		ItemStack stack = player.getItemInHand(hand);
		level.playSound(null, player.getX(), player.getY(), player.getZ(), SoundEvents.LEVER_CLICK,
				SoundSource.PLAYERS, 0.8f, 0.6f);
		level.playSound(null, player.getX(), player.getY(), player.getZ(), SoundEvents.SNOWBALL_THROW,
				SoundSource.PLAYERS, 0.6f, 0.5f);
		if (!level.isClientSide) {
			GrenadeEntity g = new GrenadeEntity(level, player);
			g.setItem(stack);
			g.shootFromRotation(player, player.getXRot() - 4.0f, player.getYRot(), 0.0f,
					player.isShiftKeyDown() ? 0.55f : 1.35f, 0.6f);
			level.addFreshEntity(g);
		}
		player.awardStat(net.minecraft.stats.Stats.ITEM_USED.get(this));
		if (!player.getAbilities().instabuild) {
			stack.shrink(1);
		}
		player.getCooldowns().addCooldown(this, 20);
		return InteractionResultHolder.sidedSuccess(stack, level.isClientSide());
	}
}
