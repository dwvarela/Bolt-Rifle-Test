package com.example.boltrifle;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.texture.OverlayTexture;
import com.mojang.math.Axis;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import software.bernie.geckolib.model.DefaultedItemGeoModel;
import software.bernie.geckolib.renderer.GeoItemRenderer;
import software.bernie.geckolib.renderer.layer.AutoGlowingGeoLayer;

/**
 * Draws an animated gun. Position/rotation per view comes from the live client config, and the
 * first-person view blends toward the "aiming" transform as the sights are raised.
 */
public class GunRenderer extends GeoItemRenderer<GunItem> {
	private final GunDef def;
	private final ResourceLocation icon;

	public GunRenderer(GunDef def) {
		super(new DefaultedItemGeoModel<>(ResourceLocation.fromNamespaceAndPath(BoltRifleMod.MOD_ID, def.id)));
		this.def = def;
		this.icon = ResourceLocation.fromNamespaceAndPath(BoltRifleMod.MOD_ID, "textures/item/icon_" + def.id + ".png");
		// full-bright layer: the muzzle flash glows regardless of lighting (uses <id>_glowmask.png)
		addRenderLayer(new AutoGlowingGeoLayer<>(this));
	}

	@Override
	public void renderByItem(ItemStack stack, ItemDisplayContext context, PoseStack poseStack,
							 MultiBufferSource bufferSource, int packedLight, int packedOverlay) {
		if (context == ItemDisplayContext.GUI) {            // inventory/hotbar: a clean flat side-view icon instead of a tiny 3D model
			VertexConsumer vc = bufferSource.getBuffer(RenderType.entityCutoutNoCull(icon));
			PoseStack.Pose p = poseStack.last();
			int light = LightTexture.FULL_BRIGHT;
			float z = 0.5f;
			vc.addVertex(p, 0f, 0f, z).setColor(-1).setUv(0f, 1f).setOverlay(OverlayTexture.NO_OVERLAY).setLight(light).setNormal(p, 0f, 0f, 1f);
			vc.addVertex(p, 1f, 0f, z).setColor(-1).setUv(1f, 1f).setOverlay(OverlayTexture.NO_OVERLAY).setLight(light).setNormal(p, 0f, 0f, 1f);
			vc.addVertex(p, 1f, 1f, z).setColor(-1).setUv(1f, 0f).setOverlay(OverlayTexture.NO_OVERLAY).setLight(light).setNormal(p, 0f, 0f, 1f);
			vc.addVertex(p, 0f, 1f, z).setColor(-1).setUv(0f, 0f).setOverlay(OverlayTexture.NO_OVERLAY).setLight(light).setNormal(p, 0f, 0f, 1f);
			return;
		}
		ClientConfig.Values v = ClientConfig.forContext(def, context);
		if (context == ItemDisplayContext.FIRST_PERSON_RIGHT_HAND || context == ItemDisplayContext.FIRST_PERSON_LEFT_HAND) {
			float aim = ClientEvents.aimProgress(net.minecraft.client.Minecraft.getInstance().getTimer()
					.getGameTimeDeltaPartialTick(false));
			float eased = Mth.clamp(aim * aim * (3.0f - 2.0f * aim), 0.0f, 1.0f); // smoothstep
			v = ClientConfig.Values.lerp(v, ClientConfig.aiming(def), eased);
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
