package com.example.boltrifle;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;

import java.util.List;

/**
 * A magazine. Right click to fill it from the rounds in your inventory,
 * sneak + right click to empty it back into your inventory. Holds one kind of round at a time.
 */
public class MagItem extends Item {
	public final MagType type;

	public MagItem(Properties properties, MagType type) {
		super(properties);
		this.type = type;
	}

	public static int rounds(ItemStack s) {
		return s.getOrDefault(BoltRifleMod.LOADED.get(), 0);
	}

	public static Cartridge ammo(ItemStack s) {
		return Cartridge.byId(s.get(BoltRifleMod.AMMO.get()), null);
	}

	public static ItemStack make(MagType type, int rounds, Cartridge c) {
		ItemStack s = new ItemStack(BoltRifleMod.MAGS.get(type).get());
		if (rounds > 0 && c != null) {
			s.set(BoltRifleMod.LOADED.get(), rounds);
			s.set(BoltRifleMod.AMMO.get(), c.itemId);
		}
		return s;
	}

	public static void giveOrDrop(Player player, ItemStack stack) {
		if (!stack.isEmpty() && !player.getInventory().add(stack)) {
			player.drop(stack, false);
		}
	}

	@Override
	public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
		ItemStack stack = player.getItemInHand(hand);
		if (level.isClientSide) {
			return InteractionResultHolder.sidedSuccess(stack, true);
		}
		int have = rounds(stack);
		Cartridge loaded = have > 0 ? ammo(stack) : null;
		Inventory inv = player.getInventory();

		if (player.isShiftKeyDown()) {                       // unload
			if (loaded == null) {
				player.displayClientMessage(Component.literal("Magazine is empty").withStyle(ChatFormatting.GRAY), true);
				return InteractionResultHolder.sidedSuccess(stack, false);
			}
			ItemStack one = stack.getCount() > 1 ? stack.split(1) : stack;
			one.remove(BoltRifleMod.LOADED.get());
			one.remove(BoltRifleMod.AMMO.get());
			giveAmmo(player, loaded, have);
			if (one != stack) {
				giveOrDrop(player, one);
			}
			level.playSound(null, player.getX(), player.getY(), player.getZ(), SoundEvents.LEVER_CLICK,
					SoundSource.PLAYERS, 0.8f, 1.5f);
			player.getCooldowns().addCooldown(this, 8);
			return InteractionResultHolder.sidedSuccess(stack, false);
		}

		if (have >= type.capacity) {
			player.displayClientMessage(Component.literal("Magazine is full").withStyle(ChatFormatting.GRAY), true);
			return InteractionResultHolder.sidedSuccess(stack, false);
		}
		Cartridge pick = loaded;                             // load
		if (pick == null) {
			for (int i = 0; i < inv.getContainerSize() && pick == null; i++) {
				if (inv.getItem(i).getItem() instanceof AmmoItem a && type.accepts.contains(a.cartridge)) {
					pick = a.cartridge;
				}
			}
		}
		if (pick == null && player.isCreative()) {
			pick = type.accepts.iterator().next();
		}
		if (pick == null) {
			player.displayClientMessage(Component.literal("No matching rounds in your inventory")
					.withStyle(ChatFormatting.RED), true);
			return InteractionResultHolder.sidedSuccess(stack, false);
		}
		int want = type.capacity - have, taken = 0;
		if (player.isCreative()) {
			taken = want;
		} else {
			for (int i = 0; i < inv.getContainerSize() && taken < want; i++) {
				ItemStack s = inv.getItem(i);
				if (s.getItem() instanceof AmmoItem a && a.cartridge == pick) {
					int use = Math.min(s.getCount(), want - taken);
					s.shrink(use);
					taken += use;
				}
			}
		}
		ItemStack one = stack.getCount() > 1 ? stack.split(1) : stack;
		one.set(BoltRifleMod.LOADED.get(), have + taken);
		one.set(BoltRifleMod.AMMO.get(), pick.itemId);
		if (one != stack) {
			giveOrDrop(player, one);
		}
		level.playSound(null, player.getX(), player.getY(), player.getZ(), SoundEvents.CROSSBOW_LOADING_MIDDLE.value(),
				SoundSource.PLAYERS, 0.7f, 1.6f);
		player.getCooldowns().addCooldown(this, 8);
		return InteractionResultHolder.sidedSuccess(stack, false);
	}

	private static void giveAmmo(Player player, Cartridge c, int count) {
		Item item = BoltRifleMod.AMMO_ITEMS.get(c).get();
		while (count > 0) {
			int n = Math.min(count, item.getDefaultMaxStackSize());
			giveOrDrop(player, new ItemStack(item, n));
			count -= n;
		}
	}

	@Override
	public boolean isBarVisible(ItemStack stack) {
		return rounds(stack) > 0;
	}

	@Override
	public int getBarWidth(ItemStack stack) {
		return Mth.clamp(Math.round(13.0f * rounds(stack) / type.capacity), 0, 13);
	}

	@Override
	public int getBarColor(ItemStack stack) {
		return 0xE0A030;
	}

	@Override
	public void appendHoverText(ItemStack stack, Item.TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
		int r = rounds(stack);
		Cartridge c = ammo(stack);
		tooltip.add(Component.literal(r + "/" + type.capacity + (r > 0 && c != null ? "  " + c.display : "  (empty)"))
				.withStyle(ChatFormatting.GRAY));
		StringBuilder fits = new StringBuilder();
		for (Cartridge a : type.accepts) {
			fits.append(fits.length() > 0 ? ", " : "").append(a.display);
		}
		tooltip.add(Component.literal("Takes: " + fits).withStyle(ChatFormatting.DARK_GRAY));
		tooltip.add(Component.literal("Right click: fill from inventory   Sneak + right click: empty")
				.withStyle(ChatFormatting.DARK_GRAY));
	}
}
