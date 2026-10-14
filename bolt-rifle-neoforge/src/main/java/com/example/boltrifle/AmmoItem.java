package com.example.boltrifle;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;

import java.util.ArrayList;
import java.util.List;

public class AmmoItem extends Item {
	public final Cartridge cartridge;

	public AmmoItem(Properties properties, Cartridge cartridge) {
		super(properties);
		this.cartridge = cartridge;
	}

	@Override
	public void appendHoverText(ItemStack stack, Item.TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
		tooltip.add(Component.literal("Damage " + cartridge.damage + "   Effective range " + (int) cartridge.effectiveRange + " m")
				.withStyle(ChatFormatting.GRAY));
		List<String> safe = new ArrayList<>(), unsafe = new ArrayList<>();
		for (Chamber ch : Chamber.values()) {
			switch (ch.fit(cartridge)) {
				case SAFE -> safe.add(ch.label);
				case UNSAFE -> unsafe.add(ch.label);
				default -> { }
			}
		}
		tooltip.add(Component.literal("Safe in: " + String.join(", ", safe)).withStyle(ChatFormatting.GREEN));
		if (!unsafe.isEmpty()) {
			tooltip.add(Component.literal("Overpressure in: " + String.join(", ", unsafe)).withStyle(ChatFormatting.RED));
			tooltip.add(Component.literal("(fast wear, small chance the gun fails)").withStyle(ChatFormatting.DARK_RED));
		}
	}
}
