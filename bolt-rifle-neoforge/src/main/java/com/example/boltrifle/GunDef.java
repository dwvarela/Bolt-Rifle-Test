package com.example.boltrifle;

import net.minecraft.sounds.SoundEvent;

/** Everything that makes one gun different from another. Models and animations are named after {@link #id}. */
public final class GunDef {
	/** A sound that plays N ticks after an action starts, synced to the animation. */
	public record Cue(int tick, SoundEvent sound, float volume, float pitch) {}

	/** Item transform: scale, offset (blocks), rotation (degrees). */
	public record Xf(double scale, double x, double y, double z, double rx, double ry, double rz) {}

	public final String id;
	public final String display;
	public final Chamber chamber;
	public final MagType mag;
	public final Cartridge defaultAmmo;

	public int durability = 1500;
	public float damageScale = 1.0f;
	public float headshot = 1.5f;
	/** Fully automatic (hold left click). */
	public boolean auto = false;
	/** Ticks between shots (bolt guns: the whole bolt cycle). Fractions are averaged out. */
	public double interval = 4.0;
	public int reloadTicks = 50, reloadChamberTicks = 70, reloadReleaseTicks = 40, dryTicks = 6;
	/** The bolt/slide locks open on the last round (animations fire_last + reload_release are used). */
	public boolean holdOpen = false;
	/** Has a semi/auto selector (key V). Only meaningful with {@link #auto}. */
	public boolean selector = false;
	/** Red-dot sight: draws a dot while aiming. */
	public boolean dot = false;
	public float spreadHip = 3.0f, spreadAds = 0.3f;
	/** Camera kick upward (degrees) and sideways wobble per shot. */
	public float recoilPitch = 2.0f, recoilYaw = 0.6f;
	/** Scope with a black mask and reticle (otherwise iron sights / red dot: no mask). */
	public boolean scoped = false;
	public double zoomDefault = 1.3, zoomMin = 1.3, zoomMax = 1.3;
	/** Fire sound loudness and pitch (pistols are higher and quieter). */
	public float boom = 1.0f, boomPitch = 1.0f;
	/** How quickly the sights come up, per tick (0-1). */
	public float aimSpeed = 0.16f;

	/** Model pixels per real metre: scales attachments (authored in cm) to this gun. */
	public double pxPerM = 55;
	/** Rail mount for optics: {top of the rail (y px), centre z px}; null = no optic can be fitted (built-in scope / no rail). */
	public double[] optic = null;
	/** Where the barrel ends (z px, bore at y = 0): muzzle devices attach here. */
	public double muzzleZ = -20;
	/** Iron-sight aim parameters used by Guns.aim (model px, scaled size, eye relief) so optics can shift the aim point. */
	public double aimSy, aimSz, aimS, aimRelief;

	public Xf hip = new Xf(0.36, -0.20, 0.14, -0.134, 0, 0, 0);
	public Xf ads = new Xf(0.30, -0.56, 0.43, 0.37, 0, 0, 0);
	public Xf third = new Xf(0.36, 0, 0, 0, 90, 0, 0);
	public Xf gui = new Xf(0.27, 0, 0, 0, 0, -90, 28);
	public Xf ground = new Xf(0.22, 0, 0, 0, 0, 0, 0);
	public Xf fixed = new Xf(0.25, 0, 0, 0, 0, -90, 0);

	/** Sound cues, indexed by GunItem.ACTION_*. */
	public Cue[][] cues = {{}, {}, {}, {}, {}, {}};

	public GunDef(String id, String display, Chamber chamber, MagType mag, Cartridge defaultAmmo) {
		this.id = id;
		this.display = display;
		this.chamber = chamber;
		this.mag = mag;
		this.defaultAmmo = defaultAmmo;
	}

	public double zoomClamp(double z) {
		return Math.max(zoomMin, Math.min(zoomMax, z));
	}
}
