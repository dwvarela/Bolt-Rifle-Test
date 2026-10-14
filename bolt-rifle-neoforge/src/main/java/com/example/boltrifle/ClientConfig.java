package com.example.boltrifle;

import net.minecraft.world.item.ItemDisplayContext;
import net.neoforged.neoforge.common.ModConfigSpec;

import java.util.HashMap;
import java.util.Map;

/**
 * Client-side tuning. The file lives at  config/boltrifle-client.toml  and is re-read while the
 * game is running, so you can nudge a gun's position/rotation and see it change instantly.
 * Every gun has its own [id.first_person], [id.aiming] and [id.third_person] section.
 *
 * Offsets are in blocks, rotations in degrees, applied on top of the normal item position.
 */
public final class ClientConfig {
	public static final ModConfigSpec SPEC;

	public static final ModConfigSpec.DoubleValue ZOOM_SENSITIVITY_EXPONENT;
	public static final ModConfigSpec.DoubleValue RECOIL_SCALE;

	public static final class Xform {
		public final ModConfigSpec.DoubleValue scale, tx, ty, tz, rx, ry, rz;

		Xform(ModConfigSpec.Builder b, String name, String comment, GunDef.Xf d) {
			b.comment(comment).push(name);
			this.scale = b.defineInRange("scale", d.scale(), 0.01, 3.0);
			this.tx = b.defineInRange("x", d.x(), -5.0, 5.0);
			this.ty = b.defineInRange("y", d.y(), -5.0, 5.0);
			this.tz = b.defineInRange("z", d.z(), -5.0, 5.0);
			this.rx = b.defineInRange("rotX", d.rx(), -360.0, 360.0);
			this.ry = b.defineInRange("rotY", d.ry(), -360.0, 360.0);
			this.rz = b.defineInRange("rotZ", d.rz(), -360.0, 360.0);
			b.pop();
		}
	}

	private record PerGun(Xform hip, Xform aim, Xform third) {}

	private static final Map<String, PerGun> PER_GUN = new HashMap<>();

	/** Plain numbers so two transforms can be blended for the aim-down-sights transition. */
	public record Values(double scale, double tx, double ty, double tz, double rx, double ry, double rz) {
		static Values of(Xform x) {
			return new Values(x.scale.get(), x.tx.get(), x.ty.get(), x.tz.get(),
					x.rx.get(), x.ry.get(), x.rz.get());
		}

		static Values of(GunDef.Xf x) {
			return new Values(x.scale(), x.x(), x.y(), x.z(), x.rx(), x.ry(), x.rz());
		}

		static Values lerp(Values a, Values b, double t) {
			return new Values(l(a.scale, b.scale, t), l(a.tx, b.tx, t), l(a.ty, b.ty, t), l(a.tz, b.tz, t),
					l(a.rx, b.rx, t), l(a.ry, b.ry, t), l(a.rz, b.rz, t));
		}

		private static double l(double a, double b, double t) {
			return a + (b - a) * t;
		}
	}

	static {
		ModConfigSpec.Builder b = new ModConfigSpec.Builder();
		for (GunDef d : Guns.ALL) {
			b.comment(d.display + ": adjust while the game runs to tune how it sits on screen.").push(d.id);
			PER_GUN.put(d.id, new PerGun(
					new Xform(b, "first_person", "Position when held (hip).", d.hip),
					new Xform(b, "aiming", "Position while aiming (blended in as you raise the sights).", d.ads),
					new Xform(b, "third_person", "In a player's hand, seen from outside.", d.third)));
			b.pop();
		}
		b.comment("General").push("general");
		ZOOM_SENSITIVITY_EXPONENT = b.comment("Mouse sensitivity is divided by zoom^this while aiming. 0 = unchanged.")
				.defineInRange("sensitivityExponent", 0.85, 0.0, 1.5);
		RECOIL_SCALE = b.comment("Multiplies camera recoil for every gun. 0 = none.")
				.defineInRange("recoilScale", 1.0, 0.0, 5.0);
		b.pop();
		SPEC = b.build();
	}

	public static Values forContext(GunDef d, ItemDisplayContext ctx) {
		PerGun g = PER_GUN.get(d.id);
		return switch (ctx) {
			case FIRST_PERSON_LEFT_HAND, FIRST_PERSON_RIGHT_HAND -> Values.of(g.hip);
			case THIRD_PERSON_LEFT_HAND, THIRD_PERSON_RIGHT_HAND -> Values.of(g.third);
			case GUI -> Values.of(d.gui);
			case GROUND -> Values.of(d.ground);
			default -> Values.of(d.fixed);
		};
	}

	public static Values aiming(GunDef d) {
		return Values.of(PER_GUN.get(d.id).aim);
	}

	private ClientConfig() {}
}
