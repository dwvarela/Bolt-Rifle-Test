package com.example.boltrifle;

import net.minecraft.world.item.ItemDisplayContext;
import net.neoforged.neoforge.common.ModConfigSpec;

/**
 * Client-side tuning. The file lives at  config/boltrifle-client.toml  and is re-read while the
 * game is running, so you can nudge the rifle's position/rotation and see it change instantly.
 *
 * Offsets are in blocks, rotations in degrees, applied on top of the normal item position.
 */
public final class ClientConfig {
	public static final ModConfigSpec SPEC;

	public static final Xform FIRST_PERSON;
	public static final Xform AIMING;
	public static final Xform THIRD_PERSON;
	public static final Xform GUI;
	public static final Xform GROUND;
	public static final Xform FIXED;

	public static final ModConfigSpec.DoubleValue ZOOM_DEFAULT;
	public static final ModConfigSpec.DoubleValue ZOOM_MIN;
	public static final ModConfigSpec.DoubleValue ZOOM_MAX;
	public static final ModConfigSpec.DoubleValue ZOOM_SENSITIVITY_EXPONENT;
	public static final ModConfigSpec.DoubleValue RECOIL_PITCH;

	public static final class Xform {
		public final ModConfigSpec.DoubleValue scale, tx, ty, tz, rx, ry, rz;

		Xform(ModConfigSpec.Builder b, String name, String comment,
			  double scale, double tx, double ty, double tz, double rx, double ry, double rz) {
			b.comment(comment).push(name);
			this.scale = b.defineInRange("scale", scale, 0.01, 3.0);
			this.tx = b.defineInRange("x", tx, -5.0, 5.0);
			this.ty = b.defineInRange("y", ty, -5.0, 5.0);
			this.tz = b.defineInRange("z", tz, -5.0, 5.0);
			this.rx = b.defineInRange("rotX", rx, -360.0, 360.0);
			this.ry = b.defineInRange("rotY", ry, -360.0, 360.0);
			this.rz = b.defineInRange("rotZ", rz, -360.0, 360.0);
			b.pop();
		}
	}

	/** Plain numbers so two Xforms can be blended for the aim-down-sights transition. */
	public record Values(double scale, double tx, double ty, double tz, double rx, double ry, double rz) {
		static Values of(Xform x) {
			return new Values(x.scale.get(), x.tx.get(), x.ty.get(), x.tz.get(),
					x.rx.get(), x.ry.get(), x.rz.get());
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
		FIRST_PERSON = new Xform(b, "first_person",
				"Rifle position when held (hip). Edit while the game runs to tune it.",
				0.30, -0.20, 0.14, -0.05, 0, 0, 0);
		AIMING = new Xform(b, "aiming",
				"Rifle position while aiming (blended in as you raise the scope).",
				0.30, -0.56, 0.43, 0.37, 0, 0, 0);
		THIRD_PERSON = new Xform(b, "third_person", "Rifle in a player's hand, seen from outside.",
				0.30, 0, 0, 0, 90, 0, 0);
		GUI = new Xform(b, "gui", "Inventory icon.", 0.27, 0, 0, 0, 0, -90, 28);
		GROUND = new Xform(b, "ground", "Dropped on the ground.", 0.22, 0, 0, 0, 0, 0, 0);
		FIXED = new Xform(b, "fixed", "Item frames and similar.", 0.25, 0, 0, 0, 0, -90, 0);

		b.comment("Scope").push("scope");
		ZOOM_DEFAULT = b.defineInRange("defaultZoom", 6.0, 1.5, 20.0);
		ZOOM_MIN = b.defineInRange("minZoom", 3.0, 1.5, 20.0);
		ZOOM_MAX = b.defineInRange("maxZoom", 12.0, 1.5, 30.0);
		ZOOM_SENSITIVITY_EXPONENT = b.comment("Mouse sensitivity is divided by zoom^this while scoped. 0 = unchanged.")
				.defineInRange("sensitivityExponent", 0.85, 0.0, 1.5);
		b.pop();

		RECOIL_PITCH = b.comment("Camera kick (degrees upward) when firing from the hip; aiming uses half.")
				.defineInRange("recoilPitch", 2.2, 0.0, 15.0);
		SPEC = b.build();
	}

	public static Values forContext(ItemDisplayContext ctx) {
		return switch (ctx) {
			case FIRST_PERSON_LEFT_HAND, FIRST_PERSON_RIGHT_HAND -> Values.of(FIRST_PERSON);
			case THIRD_PERSON_LEFT_HAND, THIRD_PERSON_RIGHT_HAND -> Values.of(THIRD_PERSON);
			case GUI -> Values.of(GUI);
			case GROUND -> Values.of(GROUND);
			default -> Values.of(FIXED);
		};
	}

	public static Values aiming() {
		return Values.of(AIMING);
	}

	private ClientConfig() {}
}
