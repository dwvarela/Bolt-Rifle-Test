package com.example.boltrifle;

import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.ThrowableItemProjectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;

/** A thrown fragmentation grenade: bounces off blocks, fuse counts down, then explodes. */
public class GrenadeEntity extends ThrowableItemProjectile {
	private int fuse = GunConfig.GRENADE_FUSE.get();

	public GrenadeEntity(EntityType<? extends GrenadeEntity> type, Level level) {
		super(type, level);
	}

	public GrenadeEntity(Level level, LivingEntity owner) {
		super(BoltRifleMod.GRENADE_ENTITY.get(), owner, level);
	}

	@Override
	protected Item getDefaultItem() {
		return BoltRifleMod.GRENADE.get();
	}

	@Override
	protected boolean canHitEntity(Entity entity) {
		return false;                                   // rolls past players and mobs, only the fuse hurts
	}

	@Override
	protected void onHitBlock(BlockHitResult hit) {
		Direction d = hit.getDirection();
		Vec3 n = new Vec3(d.getStepX(), d.getStepY(), d.getStepZ());
		Vec3 v = getDeltaMovement();
		Vec3 r = v.subtract(n.scale(2 * v.dot(n))).scale(0.45);
		if (r.lengthSqr() < 0.0025) {
			r = Vec3.ZERO;
		} else if (v.length() > 0.2) {
			level().playSound(null, getX(), getY(), getZ(), SoundEvents.CHAIN_PLACE, SoundSource.NEUTRAL, 0.8f, 0.7f);
		}
		setDeltaMovement(r);
		setPos(hit.getLocation().add(n.scale(0.06)));
	}

	@Override
	public void tick() {
		super.tick();
		if (onGround()) {
			setDeltaMovement(getDeltaMovement().multiply(0.7, 1.0, 0.7));
		}
		if (level().isClientSide) {
			level().addParticle(ParticleTypes.SMOKE, getX(), getY() + 0.2, getZ(), 0, 0.02, 0);
			if (fuse % 4 == 0) {
				level().addParticle(ParticleTypes.FLAME, getX(), getY() + 0.22, getZ(), 0, 0.01, 0);
			}
			return;
		}
		if (--fuse <= 0) {
			boolean blocks = GunConfig.GRENADE_BLOCK_DAMAGE.get();
			level().explode(this, getX(), getY(0.0625), getZ(), GunConfig.GRENADE_POWER.get().floatValue(),
					blocks ? Level.ExplosionInteraction.TNT : Level.ExplosionInteraction.NONE);
			discard();
		}
	}
}
