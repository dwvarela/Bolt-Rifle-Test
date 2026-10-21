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
import software.bernie.geckolib.cache.GeckoLibCache;
import software.bernie.geckolib.cache.object.BakedGeoModel;
import software.bernie.geckolib.cache.object.GeoBone;
import software.bernie.geckolib.model.DefaultedItemGeoModel;
import software.bernie.geckolib.util.RenderUtil;
import software.bernie.geckolib.renderer.GeoItemRenderer;
import software.bernie.geckolib.cache.texture.AutoGlowingTexture;

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
		// no glow layer: it re-rendered the whole model a second time every frame. The muzzle flash is drawn full-bright directly instead.
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
			v = ClientConfig.Values.lerp(v, ClientConfig.aiming(def, stack), eased);
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

	/** Per-attachment cached lookups (no per-frame allocation). */
	private static final java.util.Map<Attachment, AttModel> MODELS = new java.util.EnumMap<>(Attachment.class);

	private static final class AttModel {
		final ResourceLocation key, tex;
		final RenderType rt;
		private RenderType glow;
		private boolean glowTried;

		AttModel(Attachment a) {
			key = ResourceLocation.fromNamespaceAndPath(BoltRifleMod.MOD_ID, "geo/item/att_" + a.id + ".geo.json");
			tex = ResourceLocation.fromNamespaceAndPath(BoltRifleMod.MOD_ID, "textures/item/att_" + a.id + ".png");
			rt = RenderType.entityCutoutNoCull(tex);
		}

		RenderType glow() {
			if (!glowTried) {
				glowTried = true;
				try {
					glow = AutoGlowingTexture.getRenderType(tex);
				} catch (RuntimeException e) {
					glow = null;
				}
			}
			return glow;
		}
	}

	private static final String ROOT = "rifle";
	private static boolean attachmentFailed;

	@Override
	public void renderRecursively(PoseStack poseStack, GunItem animatable, GeoBone bone, RenderType renderType,
								  MultiBufferSource bufferSource, VertexConsumer buffer, boolean isReRender, float partialTick,
								  int packedLight, int packedOverlay, int colour) {
		if (bone.getScaleX() == 0.0f && bone.getScaleY() == 0.0f && bone.getScaleZ() == 0.0f) {
			return;                                       // animation-hidden bone (spare hand, casing, flash...): skip it and its children entirely
		}
		if (!isReRender && bone.getName().equals("buttstock") && (this.renderPerspective == ItemDisplayContext.FIRST_PERSON_RIGHT_HAND
				|| this.renderPerspective == ItemDisplayContext.FIRST_PERSON_LEFT_HAND) && ClientEvents.aimProgress(partialTick) > 0.4f) {
			return;                                       // while aiming the rear stock sits right at the eye: hide it so it never clips into view
		}
		ItemStack stack = getCurrentItemStack();
		if (stack != null && bone.getName().startsWith("irons_") && def.optic != null && Attachment.optic(stack) != null) {
			return;                                       // rail iron sights come off while an optic is mounted
		}
		if (stack != null && bone.getName().equals("muzzle_flash")) {
			Attachment m = Attachment.muzzle(stack);
			if (m != null && m.hidesFlash) {
				return;
			}
		}
		if (bone.getName().equals("muzzle_flash")) {
			packedLight = LightTexture.FULL_BRIGHT;       // the flash glows regardless of lighting
		}
		super.renderRecursively(poseStack, animatable, bone, renderType, bufferSource, buffer, isReRender, partialTick,
				packedLight, packedOverlay, colour);
		if (!isReRender && stack != null && bone.getName().equals(ROOT) && !attachmentFailed) {
			try {
				poseStack.pushPose();
				RenderUtil.prepMatrixForBone(poseStack, bone);      // attachments follow the gun's own recoil animation
				Attachment optic = Attachment.optic(stack), muzzle = Attachment.muzzle(stack);
				double k = def.pxPerM / 100.0;
				boolean firstPerson = this.renderPerspective == ItemDisplayContext.FIRST_PERSON_RIGHT_HAND || this.renderPerspective == ItemDisplayContext.FIRST_PERSON_LEFT_HAND;
				boolean lookingThrough = firstPerson && optic != null && optic.mask && ClientEvents.aimProgress(partialTick) > 0.55f;      // magnified scopes are replaced by the on-screen scope view; red dots and holos stay visible (open window)
				if (optic != null && def.optic != null && !lookingThrough) {
					drawAttachment(optic, 0, def.optic[0], def.optic[1], k, poseStack, animatable, bufferSource, partialTick, packedLight, packedOverlay);
				}
				if (muzzle != null) {
					drawAttachment(muzzle, 0, 0, def.muzzleZ, k, poseStack, animatable, bufferSource, partialTick, packedLight, packedOverlay);
				}
				poseStack.popPose();
			} catch (RuntimeException e) {
				attachmentFailed = true;
				com.mojang.logging.LogUtils.getLogger().error("boltrifle: attachment rendering disabled", e);
			}
		}
	}

	/** Draws an attachment model (authored in cm, origin at its mount point, muzzle devices extend toward -Z). */
	private void drawAttachment(Attachment a, double x, double y, double z, double k, PoseStack poseStack, GunItem animatable,
								MultiBufferSource bufferSource, float partialTick, int packedLight, int packedOverlay) {
		AttModel am = MODELS.computeIfAbsent(a, AttModel::new);
		BakedGeoModel model = GeckoLibCache.getBakedModels().get(am.key);
		if (model == null) {
			return;
		}
		RenderType rt = am.rt;
		VertexConsumer vb = bufferSource.getBuffer(rt);
		k *= a.visScale();
		poseStack.pushPose();
		poseStack.translate(x / 16.0, y / 16.0, z / 16.0);
		poseStack.scale((float) k, (float) k, (float) k);
		for (GeoBone b : model.topLevelBones()) {
			super.renderRecursively(poseStack, animatable, b, rt, bufferSource, vb, true, partialTick, packedLight, packedOverlay, 0xFFFFFFFF);
		}
		if (a.slot == Attachment.Slot.OPTIC) {            // lit reticle / dot: a second, full-bright pass of the (small) optic only
			RenderType glow = am.glow();
			if (glow != null) {
				VertexConsumer gv = bufferSource.getBuffer(glow);
				for (GeoBone b : model.topLevelBones()) {
					super.renderRecursively(poseStack, animatable, b, glow, bufferSource, gv, true, partialTick, LightTexture.FULL_BRIGHT, packedOverlay, 0xFFFFFFFF);
				}
			}
		}
		poseStack.popPose();
	}
}
