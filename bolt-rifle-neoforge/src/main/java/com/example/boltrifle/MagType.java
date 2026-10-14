package com.example.boltrifle;

import java.util.EnumSet;
import java.util.Set;

/** Magazine families. Each holds one kind of round at a time. */
public enum MagType {
	M700_5("mag_m700", "M700 5-Round Magazine", 5, EnumSet.of(Cartridge.WIN_308, Cartridge.NATO_762), 0),
	SKS_10("mag_sks", "SKS 10-Round Magazine", 10, EnumSet.of(Cartridge.R762X39), 1),
	AK_30("mag_ak", "AK 30-Round Magazine", 30, EnumSet.of(Cartridge.R762X39), 2),
	M14_20("mag_m14", "M14 20-Round Magazine", 20, EnumSet.of(Cartridge.NATO_762, Cartridge.WIN_308), 3),
	STANAG_30("mag_stanag", "STANAG 30-Round Magazine", 30, EnumSet.of(Cartridge.NATO_556, Cartridge.REM_223), 4),
	P90_50("mag_p90", "P90 50-Round Magazine", 50, EnumSet.of(Cartridge.FN_57), 5),
	MP7_40("mag_mp7", "MP7 40-Round Magazine", 40, EnumSet.of(Cartridge.HK_46), 6),
	G45_17("mag_g45", "Glock 17-Round Magazine", 17, EnumSet.of(Cartridge.P_9X19), 7);

	public final String itemId;
	public final String display;
	public final int capacity;
	public final Set<Cartridge> accepts;
	/** Texture style (used by the generator script). */
	public final int style;

	MagType(String itemId, String display, int capacity, Set<Cartridge> accepts, int style) {
		this.itemId = itemId;
		this.display = display;
		this.capacity = capacity;
		this.accepts = accepts;
		this.style = style;
	}
}
