package com.example.boltrifle;

import net.minecraft.world.item.ItemStack;

/**
 * Things that can be fitted to a gun. Sizes are real-world centimetres (the models are authored in cm and scaled to each
 * gun by {@link GunDef#pxPerM}). Optics sit on the gun's rail ({@link GunDef#optic}); muzzle devices screw onto the barrel end.
 */
public enum Attachment {
	RED_DOT("red_dot", "Red Dot Sight", Slot.OPTIC, 4.05, 11.7, 1.2, 1.2, 1.2, Reticle.DOT, false, 1f, 1f, 1f, false),
	HOLO("holo", "Holographic Sight", Slot.OPTIC, 5.10, 11.0, 1.25, 1.25, 1.25, Reticle.RING, false, 1f, 1f, 1f, false),
	ACOG("acog", "ACOG 4x32 Scope", Slot.OPTIC, 4.70, 17.0, 4.0, 4.0, 4.0, Reticle.CHEVRON, true, 1f, 1f, 1f, false),
	SCOPE("scope", "1-6x Variable Scope", Slot.OPTIC, 4.33, 25.0, 3.0, 1.5, 6.0, Reticle.DUPLEX, true, 1f, 1f, 1f, false),
	FLASH_HIDER("flash_hider", "Flash Hider", Slot.MUZZLE, 0, 9.0, 0, 0, 0, Reticle.NONE, false, 0.95f, 0.9f, 1f, true),
	BRAKE("muzzle_brake", "Muzzle Brake", Slot.MUZZLE, 0, 8.0, 0, 0, 0, Reticle.NONE, false, 0.72f, 1.3f, 1f, false),
	SUPPRESSOR("suppressor", "Suppressor", Slot.MUZZLE, 0, 20.0, 0, 0, 0, Reticle.NONE, false, 0.88f, 0.22f, 0.94f, true);

	/** Drawn size relative to the baked model (the red dot is drawn 30% larger; axisCm/lengthCm already include it). */
	public double visScale() {
		return this == RED_DOT ? 1.3 : 1.0;
	}

	public enum Slot { OPTIC, MUZZLE }

	public enum Reticle { NONE, DOT, RING, CHEVRON, DUPLEX }

	public final String id, display;
	public final Slot slot;
	/** Optics: height of the line of sight above the rail (cm). */
	public final double axisCm;
	/** Overall length (cm). Optics are centred on the mount point; muzzle devices extend forward from the muzzle. */
	public final double lengthCm;
	public final double zoomDefault, zoomMin, zoomMax;
	public final Reticle reticle;
	/** Magnified optic: black mask with the reticle drawn inside a round field of view. */
	public final boolean mask;
	/** Muzzle devices: camera recoil, fire-sound loudness and damage multipliers; hides the model's muzzle flash. */
	public final float recoil, boom, damage;
	public final boolean hidesFlash;

	Attachment(String id, String display, Slot slot, double axisCm, double lengthCm, double zoomDefault, double zoomMin,
			   double zoomMax, Reticle reticle, boolean mask, float recoil, float boom, float damage, boolean hidesFlash) {
		this.id = id;
		this.display = display;
		this.slot = slot;
		this.axisCm = axisCm;
		this.lengthCm = lengthCm;
		this.zoomDefault = zoomDefault;
		this.zoomMin = zoomMin;
		this.zoomMax = zoomMax;
		this.reticle = reticle;
		this.mask = mask;
		this.recoil = recoil;
		this.boom = boom;
		this.damage = damage;
		this.hidesFlash = hidesFlash;
	}

	public static Attachment byId(String id) {
		if (id != null) {
			for (Attachment a : values()) {
				if (a.id.equals(id)) {
					return a;
				}
			}
		}
		return null;
	}

	public static Attachment optic(ItemStack gun) {
		return byId(gun.get(BoltRifleMod.ATTACH_OPTIC.get()));
	}

	public static Attachment muzzle(ItemStack gun) {
		return byId(gun.get(BoltRifleMod.ATTACH_MUZZLE.get()));
	}

	public static float recoilMul(ItemStack gun) {
		Attachment m = muzzle(gun);
		return m == null ? 1.0f : m.recoil;
	}
}
