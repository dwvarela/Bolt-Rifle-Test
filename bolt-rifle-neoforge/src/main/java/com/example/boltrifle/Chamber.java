package com.example.boltrifle;

import java.util.EnumSet;
import java.util.Set;

/**
 * A gun's chamber and which rounds it may fire.
 *
 * SAFE   = designed for it.
 * UNSAFE = it fits, but the pressure or dimensions don't match the chamber:
 *          extra wear on the gun and a small chance the gun fails outright.
 *
 * Edit the table below to change what is compatible with what.
 */
public enum Chamber {
	// .308 Win chambers also take 7.62 NATO.
	C308(".308 Winchester", EnumSet.of(Cartridge.WIN_308, Cartridge.NATO_762), EnumSet.noneOf(Cartridge.class)),
	// 7.62 NATO chambers should not fire .308 Win (different pressure measurement and headspace tolerances).
	C762_NATO("7.62x51mm NATO", EnumSet.of(Cartridge.NATO_762), EnumSet.of(Cartridge.WIN_308)),
	C762X39("7.62x39mm", EnumSet.of(Cartridge.R762X39), EnumSet.noneOf(Cartridge.class)),
	// 5.56 NATO chambers (longer leade, higher pressure) take .223 Rem without trouble.
	C556_NATO("5.56x45mm NATO", EnumSet.of(Cartridge.NATO_556, Cartridge.REM_223), EnumSet.noneOf(Cartridge.class)),
	// .223 Rem chambers must not fire hotter 5.56 NATO loads.
	C223("Remington .223", EnumSet.of(Cartridge.REM_223), EnumSet.of(Cartridge.NATO_556)),
	C57("5.7x28mm", EnumSet.of(Cartridge.FN_57), EnumSet.noneOf(Cartridge.class)),
	C46("HK 4.6x30mm", EnumSet.of(Cartridge.HK_46), EnumSet.noneOf(Cartridge.class)),
	C9("9x19mm", EnumSet.of(Cartridge.P_9X19), EnumSet.noneOf(Cartridge.class));

	public enum Fit { SAFE, UNSAFE, NONE }

	public final String label;
	private final Set<Cartridge> safe;
	private final Set<Cartridge> unsafe;

	Chamber(String label, Set<Cartridge> safe, Set<Cartridge> unsafe) {
		this.label = label;
		this.safe = safe;
		this.unsafe = unsafe;
	}

	public Fit fit(Cartridge c) {
		return safe.contains(c) ? Fit.SAFE : unsafe.contains(c) ? Fit.UNSAFE : Fit.NONE;
	}

	/** Everything that physically fits (safe or not). */
	public Set<Cartridge> accepted() {
		EnumSet<Cartridge> all = EnumSet.noneOf(Cartridge.class);
		all.addAll(safe);
		all.addAll(unsafe);
		return all;
	}
}
