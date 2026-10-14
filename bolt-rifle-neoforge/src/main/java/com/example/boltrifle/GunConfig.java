package com.example.boltrifle;

import net.neoforged.neoforge.common.ModConfigSpec;

/** Server-side gameplay tuning (config/boltrifle-server.toml or the world's serverconfig folder). */
public final class GunConfig {
	public static final ModConfigSpec SPEC;
	public static final ModConfigSpec.DoubleValue DAMAGE_SCALE;
	public static final ModConfigSpec.IntValue UNSAFE_WEAR;
	public static final ModConfigSpec.DoubleValue UNSAFE_FAILURE_CHANCE;
	public static final ModConfigSpec.DoubleValue FAILURE_DAMAGE;
	public static final ModConfigSpec.IntValue GRENADE_FUSE;
	public static final ModConfigSpec.DoubleValue GRENADE_POWER;
	public static final ModConfigSpec.BooleanValue GRENADE_BLOCK_DAMAGE;

	static {
		ModConfigSpec.Builder b = new ModConfigSpec.Builder();
		DAMAGE_SCALE = b.comment("Multiplies all bullet damage.").defineInRange("damageScale", 1.0, 0.0, 10.0);
		b.comment("Firing a round the chamber is not rated for (for example .308 Win in a 7.62 NATO rifle)").push("mismatch");
		UNSAFE_WEAR = b.comment("Durability lost per mismatched shot (a normal shot costs 1).")
				.defineInRange("wearPerShot", 12, 1, 1000);
		UNSAFE_FAILURE_CHANCE = b.comment("Chance per mismatched shot that the gun ruptures and is destroyed. 0 = never.")
				.defineInRange("failureChance", 0.004, 0.0, 1.0);
		FAILURE_DAMAGE = b.comment("Damage to the shooter when a gun ruptures (2 = one heart).")
				.defineInRange("failureDamage", 6.0, 0.0, 40.0);
		b.pop();
		b.comment("Fragmentation grenade").push("grenade");
		GRENADE_FUSE = b.comment("Fuse length in ticks (20 = 1 second), counted from the moment it is thrown.")
				.defineInRange("fuseTicks", 70, 10, 400);
		GRENADE_POWER = b.comment("Explosion power (TNT = 4).").defineInRange("power", 3.2, 0.5, 12.0);
		GRENADE_BLOCK_DAMAGE = b.comment("Whether the blast breaks blocks. Off = damages only entities.")
				.define("breakBlocks", false);
		b.pop();
		SPEC = b.build();
	}

	private GunConfig() {}
}
