package com.example.boltrifle;

import com.example.boltrifle.GunDef.Cue;
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
				{new Cue(0, SoundEvents.LEVER_CLICK, 0.9f, 0.7f)}
		};
		return d;
	}
}
