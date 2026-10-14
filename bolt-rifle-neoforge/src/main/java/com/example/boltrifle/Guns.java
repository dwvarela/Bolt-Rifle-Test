package com.example.boltrifle;

import com.example.boltrifle.GunDef.Cue;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;

import java.util.ArrayList;
import java.util.List;

/** The gun list. To add a gun: add a GunDef here, plus its model, animations, texture and recipe. */
public final class Guns {
	private Guns() {}

	public static final List<GunDef> ALL = new ArrayList<>();

	private static GunDef add(GunDef d) {
		ALL.add(d);
		return d;
	}

	public static final GunDef M700 = add(m700());
	public static final GunDef SKS = add(sks());
	public static final GunDef AK47 = add(ak47());
	public static final GunDef M14 = add(m14());
	public static final GunDef M4A1 = add(m4a1());
	public static final GunDef AR15 = add(ar15());
	public static final GunDef MP7 = add(mp7());
	public static final GunDef P90 = add(p90());
	public static final GunDef G45 = add(g45());

	private static Cue c(double ticks, SoundEvent s, float vol, float pitch) {
		return new Cue((int) Math.round(ticks), s, vol, pitch);
	}

	/**
	 * Sound cues for a semi/auto rifle, timed from the animation generator (tools/gunanim.py):
	 * magazine swap fractions of d (seconds), then charging or bolt release.
	 *
	 * @param kind "right" = right-hand handle, "left" = left-hand charging handle
	 */
	private static Cue[][] rifleCues(double d, String kind, boolean handleRelease) {
		double t = d * 20;
		java.util.List<Cue> mag = new java.util.ArrayList<>(java.util.List.of(
				c(t * 0.27, SoundEvents.LEVER_CLICK, 0.8f, 1.4f),
				c(t * 0.40, SoundEvents.CROSSBOW_LOADING_START.value(), 0.8f, 1.2f),
				c(t * 0.80, SoundEvents.CROSSBOW_LOADING_MIDDLE.value(), 0.9f, 1.1f),
				c(t * 0.86, SoundEvents.IRON_TRAPDOOR_CLOSE, 0.9f, 1.3f)));
		java.util.List<Cue> chamber = new java.util.ArrayList<>(mag);
		double back = kind.equals("left") ? 0.34 : 0.29, fwd = kind.equals("left") ? 0.46 : 0.50;
		chamber.add(c(t + back * 20, SoundEvents.IRON_TRAPDOOR_OPEN, 0.7f, 1.7f));
		chamber.add(c(t + fwd * 20, SoundEvents.CROSSBOW_LOADING_END.value(), 0.9f, 0.8f));
		chamber.add(c(t + fwd * 20 + 2, SoundEvents.IRON_TRAPDOOR_CLOSE, 0.7f, 1.6f));
		java.util.List<Cue> release = new java.util.ArrayList<>(mag);
		double rel = handleRelease ? 0.37 : 0.24;
		release.add(c(t + rel * 20, SoundEvents.CROSSBOW_LOADING_END.value(), 0.9f, 0.8f));
		release.add(c(t + rel * 20 + 2, SoundEvents.IRON_TRAPDOOR_CLOSE, 0.7f, 1.6f));
		return new Cue[][]{
				{},
				{new Cue(6, SoundEvents.AMETHYST_BLOCK_HIT, 0.35f, 2.0f)},      // spent case hits the ground
				mag.toArray(new Cue[0]),
				chamber.toArray(new Cue[0]),
				{new Cue(0, SoundEvents.LEVER_CLICK, 0.9f, 0.7f)},
				release.toArray(new Cue[0])
		};
	}

	private static void setHip(GunDef d, double butt) {
		d.hip = new GunDef.Xf(0.36, -0.20, 0.14, 0.37 - butt * 0.0225, 0, 0, 0);
	}

	private static GunDef m700() {
		GunDef d = new GunDef("bolt_rifle", "Remington 700", Chamber.C308, MagType.M700_5, Cartridge.WIN_308);
		d.durability = 1800;
		d.interval = 32;                  // the whole bolt cycle
		d.reloadTicks = 58;
		d.reloadChamberTicks = 80;
		d.spreadHip = 2.8f;
		d.spreadAds = 0.10f;
		d.recoilPitch = 2.2f;
		d.recoilYaw = 0.7f;
		setHip(d, 22.4);
		d.scoped = true;
		d.zoomDefault = 6;
		d.zoomMin = 3;
		d.zoomMax = 12;
		d.cues = new Cue[][]{
				{},
				{ // fire: handle up, bolt back, bolt forward, handle down
						new Cue(10, SoundEvents.IRON_TRAPDOOR_OPEN, 0.7f, 1.7f),
						new Cue(19, SoundEvents.CROSSBOW_LOADING_MIDDLE.value(), 0.9f, 0.9f),
						new Cue(22, SoundEvents.CROSSBOW_LOADING_END.value(), 0.9f, 0.8f),
						new Cue(28, SoundEvents.IRON_TRAPDOOR_CLOSE, 0.7f, 1.6f)},
				{ // reload: release, mag out, mag in, seat
						new Cue(9, SoundEvents.LEVER_CLICK, 0.8f, 1.4f),
						new Cue(19, SoundEvents.CROSSBOW_LOADING_START.value(), 0.8f, 1.2f),
						new Cue(44, SoundEvents.CROSSBOW_LOADING_MIDDLE.value(), 0.9f, 1.1f),
						new Cue(46, SoundEvents.IRON_TRAPDOOR_CLOSE, 0.9f, 1.3f)},
				{ // reload + chamber
						new Cue(9, SoundEvents.LEVER_CLICK, 0.8f, 1.4f),
						new Cue(19, SoundEvents.CROSSBOW_LOADING_START.value(), 0.8f, 1.2f),
						new Cue(44, SoundEvents.CROSSBOW_LOADING_MIDDLE.value(), 0.9f, 1.1f),
						new Cue(46, SoundEvents.IRON_TRAPDOOR_CLOSE, 0.9f, 1.3f),
						new Cue(60, SoundEvents.IRON_TRAPDOOR_OPEN, 0.7f, 1.7f),
						new Cue(64, SoundEvents.CROSSBOW_LOADING_MIDDLE.value(), 0.9f, 0.9f),
						new Cue(70, SoundEvents.CROSSBOW_LOADING_END.value(), 0.9f, 0.8f),
						new Cue(76, SoundEvents.IRON_TRAPDOOR_CLOSE, 0.7f, 1.6f)},
				{new Cue(0, SoundEvents.LEVER_CLICK, 0.9f, 0.7f)},
				{}
		};
		return d;
	}

	private static GunDef sks() {
		GunDef d = new GunDef("sks", "SKS", Chamber.C762X39, MagType.SKS_10, Cartridge.R762X39);
		d.durability = 1500;
		d.interval = 3.0;
		d.reloadTicks = 44; d.reloadChamberTicks = 63; d.reloadReleaseTicks = 58;
		d.holdOpen = true;
		d.spreadHip = 3.2f; d.spreadAds = 0.22f;
		d.recoilPitch = 1.9f; d.recoilYaw = 0.55f;
		d.zoomDefault = d.zoomMin = d.zoomMax = 1.25;
		d.boom = 0.95f; d.boomPitch = 1.05f;
		setHip(d, 20.6);
		d.ads = new GunDef.Xf(0.30, -0.56, 0.448, 0.599, 0, 0, 0);
		d.cues = rifleCues(2.2, "right", true);
		return d;
	}

	private static GunDef ak47() {
		GunDef d = new GunDef("ak47", "AK-47", Chamber.C762X39, MagType.AK_30, Cartridge.R762X39);
		d.durability = 1700;
		d.auto = true; d.selector = true;
		d.interval = 2.0;                      // 600 rpm
		d.reloadTicks = 46; d.reloadChamberTicks = 65;
		d.spreadHip = 3.6f; d.spreadAds = 0.35f;
		d.recoilPitch = 1.15f; d.recoilYaw = 0.45f;
		d.zoomDefault = d.zoomMin = d.zoomMax = 1.2;
		d.boom = 0.95f; d.boomPitch = 1.05f;
		setHip(d, 19.9);
		d.ads = new GunDef.Xf(0.30, -0.56, 0.448, 0.577, 0, 0, 0);
		d.cues = rifleCues(2.3, "right", true);
		return d;
	}

	private static GunDef m14() {
		GunDef d = new GunDef("m14ebr", "M14 EBR", Chamber.C762_NATO, MagType.M14_20, Cartridge.NATO_762);
		d.durability = 1600;
		d.interval = 3.0;
		d.reloadTicks = 46; d.reloadChamberTicks = 65; d.reloadReleaseTicks = 60;
		d.holdOpen = true;
		d.spreadHip = 3.0f; d.spreadAds = 0.12f;
		d.recoilPitch = 2.1f; d.recoilYaw = 0.5f;
		d.scoped = true;
		d.zoomDefault = 4; d.zoomMin = 2.5; d.zoomMax = 8;
		setHip(d, 22.9);
		d.ads = new GunDef.Xf(0.30, -0.56, 0.430, 0.370, 0, 0, 0);
		d.cues = rifleCues(2.3, "right", true);
		return d;
	}

	private static GunDef m4a1() {
		GunDef d = new GunDef("m4a1", "M4A1", Chamber.C556_NATO, MagType.STANAG_30, Cartridge.NATO_556);
		d.durability = 1800;
		d.auto = true; d.selector = true;
		d.interval = 1.5;                      // ~800 rpm
		d.reloadTicks = 40; d.reloadChamberTicks = 59; d.reloadReleaseTicks = 52;
		d.holdOpen = true;
		d.spreadHip = 3.0f; d.spreadAds = 0.25f;
		d.recoilPitch = 0.85f; d.recoilYaw = 0.3f;
		d.dot = true;
		d.zoomDefault = d.zoomMin = d.zoomMax = 1.3;
		d.boom = 0.85f; d.boomPitch = 1.1f;
		setHip(d, 20.0);
		d.ads = new GunDef.Xf(0.30, -0.56, 0.450, 0.378, 0, 0, 0);
		d.cues = rifleCues(2.0, "left", false);
		return d;
	}

	private static GunDef ar15() {
		GunDef d = new GunDef("ar15", "AR-15", Chamber.C223, MagType.STANAG_30, Cartridge.REM_223);
		d.durability = 1500;
		d.interval = 2.5;
		d.reloadTicks = 40; d.reloadChamberTicks = 59; d.reloadReleaseTicks = 52;
		d.holdOpen = true;
		d.spreadHip = 2.8f; d.spreadAds = 0.18f;
		d.recoilPitch = 0.9f; d.recoilYaw = 0.3f;
		d.zoomDefault = d.zoomMin = d.zoomMax = 1.2;
		d.boom = 0.85f; d.boomPitch = 1.1f;
		setHip(d, 24.6);
		d.ads = new GunDef.Xf(0.30, -0.56, 0.445, 0.363, 0, 0, 0);
		d.cues = rifleCues(2.0, "left", false);
		return d;
	}

	private static GunDef mp7() {
		GunDef d = new GunDef("mp7", "HK MP7A1", Chamber.C46, MagType.MP7_40, Cartridge.HK_46);
		d.durability = 1400;
		d.auto = true; d.selector = true;
		d.interval = 1.33;                     // ~950 rpm
		d.reloadTicks = 38; d.reloadChamberTicks = 57; d.reloadReleaseTicks = 49;
		d.holdOpen = true;
		d.spreadHip = 3.4f; d.spreadAds = 0.4f;
		d.recoilPitch = 0.55f; d.recoilYaw = 0.25f;
		d.dot = true;
		d.zoomDefault = d.zoomMin = d.zoomMax = 1.25;
		d.boom = 0.7f; d.boomPitch = 1.35f;
		d.aimSpeed = 0.2f;
		setHip(d, 14.8);
		d.ads = new GunDef.Xf(0.30, -0.56, 0.438, 0.438, 0, 0, 0);
		d.cues = rifleCues(1.9, "left", false);
		return d;
	}

	private static GunDef p90() {
		GunDef d = new GunDef("p90", "FN P90", Chamber.C57, MagType.P90_50, Cartridge.FN_57);
		d.durability = 1600;
		d.auto = true; d.selector = true;
		d.interval = 1.33;                     // ~900 rpm
		d.reloadTicks = 44; d.reloadChamberTicks = 63; d.reloadReleaseTicks = 55;
		d.holdOpen = true;
		d.spreadHip = 3.2f; d.spreadAds = 0.35f;
		d.recoilPitch = 0.45f; d.recoilYaw = 0.2f;
		d.dot = true;
		d.zoomDefault = d.zoomMin = d.zoomMax = 1.3;
		d.boom = 0.7f; d.boomPitch = 1.3f;
		d.aimSpeed = 0.2f;
		setHip(d, 14.9);
		d.ads = new GunDef.Xf(0.30, -0.56, 0.445, 0.489, 0, 0, 0);
		d.cues = rifleCues(2.2, "left", false);
		return d;
	}

	private static GunDef g45() {
		GunDef d = new GunDef("g45", "Glock G45 Gen 7", Chamber.C9, MagType.G45_17, Cartridge.P_9X19);
		d.durability = 1200;
		d.interval = 2.0;                      // as fast as you can pull the trigger
		d.reloadTicks = 34; d.reloadChamberTicks = 52; d.reloadReleaseTicks = 44;
		d.holdOpen = true;
		d.spreadHip = 2.6f; d.spreadAds = 0.3f;
		d.recoilPitch = 1.1f; d.recoilYaw = 0.35f;
		d.zoomDefault = d.zoomMin = d.zoomMax = 1.1;
		d.boom = 0.65f; d.boomPitch = 1.45f;
		d.aimSpeed = 0.24f;
		d.hip = new GunDef.Xf(0.36, -0.17, 0.14, 0.09, 0, 0, 0);
		d.ads = new GunDef.Xf(0.30, -0.56, 0.483, 0.399, 0, 0, 0);
		d.cues = rifleCues(1.7, "left", false);
		return d;
	}
}
