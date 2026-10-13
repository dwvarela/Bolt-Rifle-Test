package com.example.boltrifle;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import software.bernie.geckolib.model.DefaultedItemGeoModel;
import software.bernie.geckolib.renderer.GeoItemRenderer;

/**
 * Draws the animated rifle. Position/rotation per view comes from the live client config, and the
 * first-person view blends toward the "aiming" transform as the scope is raised.
 */
public class RifleRenderer extends GeoItemRenderer<RifleItem> {
	public RifleRenderer() {
		super(new DefaultedItemGeoModel<>(ResourceLocation.fromNamespaceAndPath(BoltRifleMod.MOD_ID, "bolt_rifle")));
	}

	@Override
	public void renderByItem(ItemStack stack, ItemDisplayContext context, PoseStack poseStack,
							 MultiBufferSource bufferSource, int packedLight, int packedOverlay) {
		ClientConfig.Values v = ClientConfig.forContext(context);
		if (context == ItemDisplayContext.FIRST_PERSON_RIGHT_HAND || context == ItemDisplayContext.FIRST_PERSON_LEFT_HAND) {
			float aim = ClientEvents.aimProgress(net.minecraft.client.Minecraft.getInstance().getTimer()
					.getGameTimeDeltaPartialTick(false));
			float eased = Mth.clamp(aim * aim * (3.0f - 2.0f * aim), 0.0f, 1.0f); // smoothstep
			v = ClientConfig.Values.lerp(v, ClientConfig.aiming(), eased);
		}

		poseStack.pushPose();
		poseStack.translate(0.5, 0.5, 0.5);
		poseStack.translate(v.tx(), v.ty(), v.tz());
		poseStack.mulPose(Axis.YP.rotationDegrees((float) v.ry()));
		poseStack.mulPose(Axis.XP.rotationDegrees((float) v.rx()));
		poseStack.mulPose(Axis.ZP.rotationDegrees((float) v.rz()));
		poseStack.scale((float) v.scale(), (float) v.scale(), (float) v.scale());
		poseStack.translate(-0.5, -0.5, -0.5);
		super.renderByItem(stack, context, poseStack, bufferSource, packedLight, packedOverlay);
		poseStack.popPose();
	}
}
