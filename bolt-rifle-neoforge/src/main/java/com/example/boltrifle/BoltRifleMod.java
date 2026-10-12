package com.example.boltrifle;

import com.mojang.serialization.Codec;
import net.minecraft.core.component.DataComponentType;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.Item;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.event.BuildCreativeModeTabContentsEvent;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

@Mod(BoltRifleMod.MOD_ID)
public class BoltRifleMod {
	public static final String MOD_ID = "boltrifle";

	public static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(MOD_ID);
	public static final DeferredRegister<DataComponentType<?>> COMPONENTS =
			DeferredRegister.create(Registries.DATA_COMPONENT_TYPE, MOD_ID);

	/** Number of rounds currently loaded in the rifle's magazine (0-5). */
	public static final DeferredHolder<DataComponentType<?>, DataComponentType<Integer>> LOADED =
			COMPONENTS.register("loaded", () -> DataComponentType.<Integer>builder()
					.persistent(Codec.intRange(0, RifleItem.MAGAZINE_SIZE))
					.networkSynchronized(ByteBufCodecs.VAR_INT)
					.build());

	public static final DeferredItem<Item> RIFLE_ROUND =
			ITEMS.register("rifle_round", () -> new Item(new Item.Properties()));

	public static final DeferredItem<Item> BOLT_RIFLE =
			ITEMS.register("bolt_rifle", () -> new RifleItem(new Item.Properties().stacksTo(1)));

	public BoltRifleMod(IEventBus modEventBus) {
		ITEMS.register(modEventBus);
		COMPONENTS.register(modEventBus);
		modEventBus.addListener(this::addToCreativeTab);
	}

	private void addToCreativeTab(BuildCreativeModeTabContentsEvent event) {
		if (event.getTabKey() == CreativeModeTabs.COMBAT) {
			event.accept(BOLT_RIFLE.get());
			event.accept(RIFLE_ROUND.get());
		}
	}
}
