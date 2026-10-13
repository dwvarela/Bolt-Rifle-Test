package com.example.boltrifle;

import com.mojang.serialization.Codec;
import net.minecraft.core.component.DataComponentType;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.Item;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.config.ModConfig;
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

	private static <T> DeferredHolder<DataComponentType<?>, DataComponentType<T>> component(
			String name, Codec<T> codec, StreamCodec<? super RegistryFriendlyByteBuf, T> stream) {
		return COMPONENTS.register(name, () -> DataComponentType.<T>builder()
				.persistent(codec).networkSynchronized(stream).build());
	}

	/** Rounds in the magazine (0-5). */
	public static final DeferredHolder<DataComponentType<?>, DataComponentType<Integer>> LOADED =
			component("loaded", Codec.intRange(0, RifleItem.MAGAZINE_SIZE), ByteBufCodecs.VAR_INT);
	/** True when a round is in the chamber. */
	public static final DeferredHolder<DataComponentType<?>, DataComponentType<Boolean>> CHAMBERED =
			component("chambered", Codec.BOOL, ByteBufCodecs.BOOL);
	/** Current timed action (see RifleItem.ACTION_*), 0 = idle. */
	public static final DeferredHolder<DataComponentType<?>, DataComponentType<Integer>> ACTION =
			component("action", Codec.INT, ByteBufCodecs.VAR_INT);
	/** Game time (ticks) the current action started. */
	public static final DeferredHolder<DataComponentType<?>, DataComponentType<Long>> ACTION_START =
			component("action_start", Codec.LONG, ByteBufCodecs.VAR_LONG);
	/** Rounds taken from the inventory for an in-progress reload. */
	public static final DeferredHolder<DataComponentType<?>, DataComponentType<Integer>> PENDING =
			component("pending", Codec.INT, ByteBufCodecs.VAR_INT);

	public static final DeferredItem<Item> RIFLE_ROUND =
			ITEMS.register("rifle_round", () -> new Item(new Item.Properties()));

	public static final DeferredItem<Item> BOLT_RIFLE =
			ITEMS.register("bolt_rifle", () -> new RifleItem(new Item.Properties().stacksTo(1)));

	public BoltRifleMod(IEventBus modEventBus, ModContainer container) {
		ITEMS.register(modEventBus);
		COMPONENTS.register(modEventBus);
		modEventBus.addListener(this::addToCreativeTab);
		modEventBus.addListener(Net::register);
		container.registerConfig(ModConfig.Type.CLIENT, ClientConfig.SPEC);
	}

	private void addToCreativeTab(BuildCreativeModeTabContentsEvent event) {
		if (event.getTabKey() == CreativeModeTabs.COMBAT) {
			event.accept(BOLT_RIFLE.get());
			event.accept(RIFLE_ROUND.get());
		}
	}
}
