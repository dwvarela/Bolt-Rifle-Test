package com.example.boltrifle;

import it.unimi.dsi.fastutil.objects.ObjectArrayList;
import net.minecraft.core.Direction;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;
import org.joml.Vector3f;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;
import software.bernie.geckolib.cache.object.BakedGeoModel;
import software.bernie.geckolib.cache.object.GeoBone;
import software.bernie.geckolib.cache.object.GeoCube;
import software.bernie.geckolib.cache.object.GeoQuad;
import software.bernie.geckolib.cache.object.GeoVertex;
import software.bernie.geckolib.loading.json.raw.Bone;
import software.bernie.geckolib.loading.json.raw.Cube;
import software.bernie.geckolib.loading.json.raw.ModelProperties;
import software.bernie.geckolib.loading.json.raw.PolyMesh;
import software.bernie.geckolib.loading.object.BakedModelFactory;
import software.bernie.geckolib.loading.object.BoneStructure;
import software.bernie.geckolib.loading.object.GeometryTree;
import software.bernie.geckolib.util.RenderUtil;

import java.util.List;

/**
 * Model factory for this mod: identical to GeckoLib's built-in one for cubes, and additionally turns a bone's
 * {@code poly_mesh} (triangle lists baked by tools/meshbake.py) into real triangles, so guns can have curved,
 * high-detail geometry instead of boxes. Vertex layout follows the cube convention: x is mirrored, units are 1/16 block.
 */
public class MeshModelFactory implements BakedModelFactory {
	private static final Logger LOG = LogUtils.getLogger();
	private final BakedModelFactory base = BakedModelFactory.DEFAULT_FACTORY;

	@Override
	public BakedGeoModel constructGeoModel(GeometryTree tree) {
		List<GeoBone> bones = new ObjectArrayList<>();
		for (BoneStructure bs : tree.topLevelBones().values()) {
			bones.add(constructBone(bs, tree.properties(), null));
		}
		return new BakedGeoModel(bones, tree.properties());
	}

	@Override
	public GeoBone constructBone(BoneStructure bs, ModelProperties props, @Nullable GeoBone parent) {
		Bone bone = bs.self();
		GeoBone nb = new GeoBone(parent, bone.name(), bone.mirror(), bone.inflate(), bone.neverRender(), bone.reset());
		Vec3 rotation = RenderUtil.arrayToVec(bone.rotation());
		Vec3 pivot = RenderUtil.arrayToVec(bone.pivot());
		nb.updateRotation((float) Math.toRadians(-rotation.x), (float) Math.toRadians(-rotation.y), (float) Math.toRadians(rotation.z));
		nb.updatePivot((float) -pivot.x, (float) pivot.y, (float) pivot.z);
		for (Cube cube : bone.cubes()) {
			nb.getCubes().add(constructCube(cube, props, nb));
		}
		PolyMesh pm = bone.polyMesh();
		if (pm != null) {
			try {
				GeoCube mesh = buildMesh(pm);
				if (mesh != null) {
					nb.getCubes().add(mesh);
				}
			} catch (Throwable t) {
				LOG.error("boltrifle: failed to build poly mesh for bone {}", bone.name(), t);
			}
		}
		for (BoneStructure child : bs.children().values()) {
			nb.getChildBones().add(constructBone(child, props, nb));
		}
		return nb;
	}

	@Override
	public GeoCube constructCube(Cube cube, ModelProperties props, GeoBone bone) {
		return base.constructCube(cube, props, bone);
	}

	private static GeoCube buildMesh(PolyMesh pm) {
		double[] pos = pm.positions();
		double[] nor = pm.normals();
		double[] uv = pm.uvs();
		if (pos == null || nor == null || uv == null || pm.polysUnion() == null) {
			return null;
		}
		double[][][] polys = pm.polysUnion().union();
		GeoQuad[] quads = new GeoQuad[polys.length];
		for (int i = 0; i < polys.length; i++) {
			double[][] poly = polys[i];
			GeoVertex[] vs = new GeoVertex[4];
			for (int k = 0; k < 3; k++) {
				int p = (int) poly[k][0] * 3;
				int u = (int) poly[k][2] * 2;
				vs[k] = new GeoVertex(new Vector3f((float) (-pos[p] / 16.0), (float) (pos[p + 1] / 16.0), (float) (pos[p + 2] / 16.0)),
						(float) uv[u], (float) uv[u + 1]);
			}
			vs[3] = vs[2];                                      // triangle drawn as a degenerate quad
			int n = (int) poly[0][1] * 3;
			Vector3f normal = new Vector3f((float) -nor[n], (float) nor[n + 1], (float) nor[n + 2]);
			quads[i] = new GeoQuad(vs, normal, Direction.UP);
		}
		return new GeoCube(quads, Vec3.ZERO, Vec3.ZERO, new Vec3(1, 1, 1), 0, false);
	}
}
