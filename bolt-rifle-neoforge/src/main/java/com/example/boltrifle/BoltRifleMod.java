package com.example.boltrifle;

import com.mojang.serialization.Codec;
import net.minecraft.core.component.DataComponentType;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.config.ModConfig;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

import java.util.EnumMap;
import java.util.LinkedHashMap;
import java.util.Map;

@Mod(BoltRifleMod.MOD_ID)
public class BoltRifleMod {
	public static final String MOD_ID = "boltrifle";

	public static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(MOD_ID);
	public static final DeferredRegister<DataComponentType<?>> COMPONENTS =
			DeferredRegister.create(Registries.DATA_COMPONENT_TYPE, MOD_ID);
	public static final DeferredRegister<net.minecraft.world.entity.EntityType<?>> ENTITIES =
			DeferredRegister.create(Registries.ENTITY_TYPE, MOD_ID);
	public static final DeferredRegister<CreativeModeTab> TABS =
			DeferredRegister.create(Registries.CREATIVE_MODE_TAB, MOD_ID);

	private static <T> DeferredHolder<DataComponentType<?>, DataComponentType<T>> component(
			String name, Codec<T> codec, StreamCodec<? super RegistryFriendlyByteBuf, T> stream) {
		return COMPONENTS.register(name, () -> DataComponentType.<T>builder()
				.persistent(codec).networkSynchronized(stream).build());
	}

	// ---- state kept on gun and magazine stacks (guns use all of them, magazines use LOADED + AMMO)
	/** Rounds in the magazine. */
	public static final DeferredHolder<DataComponentType<?>, DataComponentType<Integer>> LOADED =
			component("loaded", Codec.intRange(0, 200), ByteBufCodecs.VAR_INT);
	/** Round type in the magazine (cartridge item id). */
	public static final DeferredHolder<DataComponentType<?>, DataComponentType<String>> AMMO =
			component("ammo", Codec.STRING, ByteBufCodecs.STRING_UTF8);
	/** True when a round is in the chamber. */
	public static final DeferredHolder<DataComponentType<?>, DataComponentType<Boolean>> CHAMBERED =
			component("chambered", Codec.BOOL, ByteBufCodecs.BOOL);
	/** Round type in the chamber. */
	public static final DeferredHolder<DataComponentType<?>, DataComponentType<String>> CHAMBER_AMMO =
			component("chamber_ammo", Codec.STRING, ByteBufCodecs.STRING_UTF8);
	/** True when a magazine is inserted. */
	public static final DeferredHolder<DataComponentType<?>, DataComponentType<Boolean>> HAS_MAG =
			component("has_mag", Codec.BOOL, ByteBufCodecs.BOOL);
	/** Bolt/slide is locked open (after the last round). */
	public static final DeferredHolder<DataComponentType<?>, DataComponentType<Boolean>> BOLT_OPEN =
			component("bolt_open", Codec.BOOL, ByteBufCodecs.BOOL);
	/** Selector: true = full auto (default), false = semi. */
	public static final DeferredHolder<DataComponentType<?>, DataComponentType<Boolean>> AUTO_MODE =
			component("auto_mode", Codec.BOOL, ByteBufCodecs.BOOL);
	/** Current timed action (see GunItem.ACTION_*), 0 = idle. */
	public static final DeferredHolder<DataComponentType<?>, DataComponentType<Integer>> ACTION =
			component("action", Codec.INT, ByteBufCodecs.VAR_INT);
	public static final DeferredHolder<DataComponentType<?>, DataComponentType<Long>> ACTION_START =
			component("action_start", Codec.LONG, ByteBufCodecs.VAR_LONG);
	public static final DeferredHolder<DataComponentType<?>, DataComponentType<Integer>> ACTION_LEN =
			component("action_len", Codec.INT, ByteBufCodecs.VAR_INT);
	/** Averages fractional shot intervals (e.g. 900 rpm = 1.33 ticks). */
	public static final DeferredHolder<DataComponentType<?>, DataComponentType<Float>> FIRE_ACC =
			component("fire_acc", Codec.FLOAT, ByteBufCodecs.FLOAT);
	/** The fresh magazine taken from the inventory during a reload. */
	public static final DeferredHolder<DataComponentType<?>, DataComponentType<Integer>> PENDING =
			component("pending", Codec.INT, ByteBufCodecs.VAR_INT);
	public static final DeferredHolder<DataComponentType<?>, DataComponentType<String>> PENDING_AMMO =
			component("pending_ammo", Codec.STRING, ByteBufCodecs.STRING_UTF8);

	/** Time (1/100 tick) at which the next shot is allowed. */
	public static final DeferredHolder<DataComponentType<?>, DataComponentType<Long>> NEXT_SHOT =
			component("next_shot", Codec.LONG, ByteBufCodecs.VAR_LONG);

	// ---- items
	public static final Map<Cartridge, DeferredItem<AmmoItem>> AMMO_ITEMS = new EnumMap<>(Cartridge.class);
	public static final Map<MagType, DeferredItem<MagItem>> MAGS = new EnumMap<>(MagType.class);
	public static final Map<String, DeferredItem<GunItem>> GUNS = new LinkedHashMap<>();

	public static final DeferredItem<GrenadeItem> GRENADE =
			ITEMS.register("grenade", () -> new GrenadeItem(new Item.Properties().stacksTo(16)));
	public static final DeferredHolder<net.minecraft.world.entity.EntityType<?>,
			net.minecraft.world.entity.EntityType<GrenadeEntity>> GRENADE_ENTITY = ENTITIES.register("grenade",
			() -> net.minecraft.world.entity.EntityType.Builder.<GrenadeEntity>of(GrenadeEntity::new,
					net.minecraft.world.entity.MobCategory.MISC).sized(0.25f, 0.25f).clientTrackingRange(4)
					.updateInterval(10).build("grenade"));

	static {
		for (Cartridge c : Cartridge.values()) {
			AMMO_ITEMS.put(c, ITEMS.register(c.itemId, () -> new AmmoItem(new Item.Properties(), c)));
		}
		for (MagType m : MagType.values()) {
			MAGS.put(m, ITEMS.register(m.itemId, () -> new MagItem(new Item.Properties().stacksTo(16), m)));
		}
		for (GunDef d : Guns.ALL) {
			GUNS.put(d.id, ITEMS.register(d.id, () -> new GunItem(new Item.Properties().durability(d.durability), d)));
		}
	}

	public static final DeferredHolder<CreativeModeTab, CreativeModeTab> TAB = TABS.register("guns", () ->
			CreativeModeTab.builder()
					.title(Component.literal("Firearms"))
					.icon(() -> new ItemStack(GUNS.get(Guns.M700.id).get()))
					.displayItems((params, out) -> {
						GUNS.values().forEach(g -> out.accept(g.get()));
						MAGS.values().forEach(m -> out.accept(m.get()));
						AMMO_ITEMS.values().forEach(a -> out.accept(a.get()));
							out.accept(GRENADE.get());
					}).build());

	public BoltRifleMod(IEventBus modEventBus, ModContainer container) {
		software.bernie.geckolib.util.GeckoLibUtil.addCustomBakedModelFactory(MOD_ID, new MeshModelFactory());
		ITEMS.register(modEventBus);
		ENTITIES.register(modEventBus);
		COMPONENTS.register(modEventBus);
		TABS.register(modEventBus);
		modEventBus.addListener(Net::register);
		container.registerConfig(ModConfig.Type.CLIENT, ClientConfig.SPEC, "boltrifle-client-v3.toml");
		container.registerConfig(ModConfig.Type.SERVER, GunConfig.SPEC);
	}
}
