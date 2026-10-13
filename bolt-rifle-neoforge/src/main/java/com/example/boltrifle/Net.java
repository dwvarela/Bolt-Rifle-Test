package com.example.boltrifle;

import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.neoforged.neoforge.network.event.RegisterPayloadHandlersEvent;
import net.neoforged.neoforge.network.registration.PayloadRegistrar;

/** Client -> server messages: left click = fire, R = reload. */
public final class Net {
	private Net() {}

	public record FirePayload(boolean aiming) implements CustomPacketPayload {
		public static final Type<FirePayload> TYPE =
				new Type<>(ResourceLocation.fromNamespaceAndPath(BoltRifleMod.MOD_ID, "fire"));
		public static final StreamCodec<ByteBuf, FirePayload> CODEC =
				ByteBufCodecs.BOOL.map(FirePayload::new, FirePayload::aiming);

		@Override
		public Type<? extends CustomPacketPayload> type() {
			return TYPE;
		}
	}

	public record ReloadPayload() implements CustomPacketPayload {
		public static final Type<ReloadPayload> TYPE =
				new Type<>(ResourceLocation.fromNamespaceAndPath(BoltRifleMod.MOD_ID, "reload"));
		public static final StreamCodec<ByteBuf, ReloadPayload> CODEC = StreamCodec.unit(new ReloadPayload());

		@Override
		public Type<? extends CustomPacketPayload> type() {
			return TYPE;
		}
	}

	public static void register(RegisterPayloadHandlersEvent event) {
		PayloadRegistrar registrar = event.registrar("1");
		registrar.playToServer(FirePayload.TYPE, FirePayload.CODEC, (payload, ctx) ->
				ctx.enqueueWork(() -> {
					if (ctx.player() instanceof ServerPlayer sp) {
						RifleItem.handleFire(sp, payload.aiming());
					}
				}));
		registrar.playToServer(ReloadPayload.TYPE, ReloadPayload.CODEC, (payload, ctx) ->
				ctx.enqueueWork(() -> {
					if (ctx.player() instanceof ServerPlayer sp) {
						RifleItem.handleReload(sp);
					}
				}));
	}
}
