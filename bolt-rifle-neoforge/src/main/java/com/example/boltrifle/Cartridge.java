package com.example.boltrifle;

import java.util.Locale;

/** Every round in the mod, modelled on its real-world counterpart. */
public enum Cartridge {
	//          item id            display name           dmg   effRange maxRange armorPierce
	WIN_308("ammo_308_win", ".308 Winchester", 16.0f, 100, 160, 0.10f),
	NATO_762("ammo_762x51_nato", "7.62x51mm NATO", 16.0f, 100, 160, 0.14f),
	R762X39("ammo_762x39", "7.62x39mm", 12.0f, 80, 128, 0.10f),
	NATO_556("ammo_556x45_nato", "5.56x45mm NATO", 10.0f, 90, 144, 0.16f),
	REM_223("ammo_223_rem", ".223 Remington", 9.5f, 85, 140, 0.08f),
	FN_57("ammo_57x28", "5.7x28mm", 7.5f, 55, 96, 0.35f),
	HK_46("ammo_46x30", "HK 4.6x30mm", 7.0f, 55, 96, 0.40f),
	P_9X19("ammo_9x19", "9x19mm Parabellum", 6.5f, 30, 64, 0.04f);

	public final String itemId;
	public final String display;
	/** Base damage (20 = a full player health bar). */
	public final float damage;
	/** Distance (blocks) up to which the round does full damage. */
	public final double effectiveRange;
	public final double maxRange;
	/** Bonus damage against armoured targets (0.4 = up to +40 % against full armour). */
	public final float armorPierce;

	Cartridge(String itemId, String display, float damage, double effectiveRange, double maxRange, float armorPierce) {
		this.itemId = itemId;
		this.display = display;
		this.damage = damage;
		this.effectiveRange = effectiveRange;
		this.maxRange = maxRange;
		this.armorPierce = armorPierce;
	}

	/** Damage multiplier for a hit at the given distance: full inside effective range, tapering beyond it. */
	public float falloff(double distance) {
		if (distance <= effectiveRange) {
			return 1.0f;
		}
		return (float) Math.max(0.45, 1.0 - (distance - effectiveRange) / (effectiveRange * 1.8));
	}

	public static Cartridge byId(String id, Cartridge fallback) {
		if (id != null) {
			String key = id.toLowerCase(Locale.ROOT);
			for (Cartridge c : values()) {
				if (c.itemId.equals(key)) {
					return c;
				}
			}
		}
		return fallback;
	}
}
