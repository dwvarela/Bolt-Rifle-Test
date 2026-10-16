package com.example.boltrifle;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;

import java.util.List;

/** An optic or muzzle device. Hold it in the off hand with a gun in the main hand and press B to fit it. */
public class AttachmentItem extends Item {
	public final Attachment attachment;

	public AttachmentItem(Properties properties, Attachment attachment) {
		super(properties);
		this.attachment = attachment;
	}

	@Override
	public void appendHoverText(ItemStack stack, Item.TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
		Attachment a = attachment;
		if (a.slot == Attachment.Slot.OPTIC) {
			String zoom = a.zoomMax > a.zoomMin ? String.format("%.1f-%.0fx", a.zoomMin, a.zoomMax) : String.format("%.1fx", a.zoomDefault);
			tooltip.add(Component.literal("Optic   Magnification " + zoom).withStyle(ChatFormatting.GRAY));
		} else {
			tooltip.add(Component.literal("Muzzle device   Recoil " + Math.round(a.recoil * 100) + "%   Noise "
					+ Math.round(a.boom * 100) + "%" + (a.hidesFlash ? "   No muzzle flash" : "")).withStyle(ChatFormatting.GRAY));
		}
		tooltip.add(Component.literal("Off hand + gun in main hand, then press B to fit. B with an empty off hand removes it.")
				.withStyle(ChatFormatting.DARK_GRAY));
	}
}
