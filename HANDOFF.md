# HANDOFF - everything another agent needs to continue (written Sun 2026-10-25)

## Project
NeoForge 21.1.257 / Minecraft 1.21.1 mod "boltrifle" (GeckoLib 4.9.3, Java 21). Repo `dwvarela/Bolt-Rifle-Test`, mod dir `bolt-rifle-neoforge/`.
Branch `v3-realistic` -> CI publishes release `preview` (https://github.com/dwvarela/Bolt-Rifle-Test/releases/download/preview/boltrifle.jar).
Branch `v2-animated-rifle` = stable (`latest`). DO NOT merge to stable until the user confirms.
Guns: M700 (id `bolt_rifle`), SKS, AK-47, M14 EBR (`m14ebr`), M4A1, Mini-14, MP7, P90, Glock 19, M67 grenade.
CI builds ONLY from committed resources (geo/animation/texture JSON under src/main/resources); the Python generators in `tools/` are NOT run in CI,
so after changing a generator you must re-run it and commit the regenerated resources.
The user tests in game; the agent cannot. Always say honestly that things are untested in game. Keep messages short, work in parts, commit+push each part, check CI (`gh run list`), give the preview link.

## Hard rules (see CLAUDE.md, permanent, set by the user)
* Exactly two hands (`left_hand`, `right_hand`) in every animation of every gun; never hide/show/scale hands; no scale keys for hands or magazines.
* A magazine never pops in/out of view: it leaves view carried/dropped and comes back. Spent cases/rounds only toggled while hidden. `tools/animlib.write()` asserts this.
* Models must match the reference photos (Fire_Arm_References.zip, user-provided, `AK 47-*.jpeg` etc). Reference jar (Point Blank) is reference-only: never copy.
* Sounds: user's own recordings in `Gun Sound Effects.zip` via `tools/gen_sounds.py`, never synthesis.
* Reference videos I cannot watch: M14 https://www.youtube.com/watch?v=RT-cUL-6aOo , M700 https://www.youtube.com/watch?v=X2LANjINJzQ - ask the user for timestamps/descriptions.
* The user is demanding; the "10 audits" requirement means each audit must be more rigorous than the last and must read the real numbers from the source.

## Status
DONE+pushed: sounds, hard-rule rebuild, stock hinge, magazine tumble, gloves, M14 op-rod handle/top ejection, rounds in mags, 3-finger grips + trigger finger,
rolled charging hand (M14/AK), AK glove hands, **Part 1 (commit 3903f29): M700/M14 hold pose + SCALE 1.1979 + config fingerprint + raster audits (all 10 pass, jar verified)**.
TODO in order:
 2. DONE (see git log): M700 magazine drop reworked in gen_m700_anim.reload_mag (held visibly 0.40-0.76, released, tumbles out of bottom by ~1.1s).
 3. M14 DONE in code (untested in game): idle_open+dryfire_open poses follow BOLT_OPEN (GunItem predicate via DataTickets.ITEMSTACK), grip fingers raised (gun_m14.hands), charge hand path searched with tools/clip_check.py + search_handle.py (no clipping). STILL OPEN: refine reload vs reference video (needs user timestamps).
    (b) 3 grip fingers higher/more natural; (c) no hand clipping into gun during rechamber after empty reload; (d) refine reload toward the reference video.
 4. Later: AK-47 part 2 (rebuild model from photos), GUI icons stale, rebuild SKS/M4A1/Mini-14/MP7/Glock19 from photos, re-fit their hold poses with the raster metric.
 5. Merge to stable only after user confirms.

## Key technical facts
### Why positions "never changed" (fixed)
ClientConfig writes per-gun hip/ads/third transforms to a TOML; ModConfigSpec ignores new defaults when the file has the keys. File name is now
`boltrifle-client-<hash of all defaults>.toml` (ClientConfig.FILE), so any default change starts fresh.
### First-person camera model (verified; ADS centres the sight at 0.00 px)
camera pos `c = H + t + R*s*(-x/16, y/16+0.01, z/16)`, H=(0.56,-0.52,-0.72), camera looks along -z, vertical FOV 70, frame 960x540, near plane 0.05.
Renderer (GunRenderer.java): translate(.5), translate(t), rotY, rotX, rotZ, scale, translate(-.5); GeckoLib mirrors model x. R = Ry*Rx*Rz (degrees).
`Guns.hold(d,butt,s,dx,dy,dz[,rx,ry,rz])` -> hip Xf(scale s*SCALE, -0.40+0.5s+dx, -0.06+0.5s+dy, 0.95-butt*s/16+dz, rx,ry,rz). Positive dz = closer to camera. SCALE=1.1979.
Current: M700 `hold(d,22.4,0.911,-0.15,-0.17,-0.38, 6.0,21.0,5.4)`; M14 `hold(d,23.6,0.6,-0.05,0.14,-0.32, 3.4,14.9,5.4)`.
Yaw (ry) positive swings the rear stock out of frame; the pure translation approach could not hide the stock (geometry: stock is long and close to the lens).
### Metrics (lessons)
Fraction of sampled points in frame is misleading. Use `tools/fp_cov.py coverage()` (z-buffered raster, near-plane clipped; groups stock/hands/mag/rest/rear - "rear" = stock triangles with model z>13).
`tools/fit_raster4.py <gun> <coreZ> <yawlo> <yawhi> <muzzleXmin> <N> <seed>` random-search fitter (slow; run with setsid nohup in background). `tools/audit_pos.py` parses Guns.java; `tools/audit10.py [jar]` = the 10 audits (run after every position/scale change, and with the CI jar after CI).
### GeckoLib / animation conventions
JSON x = -game x; JSON rotation x negated; pose bone p' = pos + pivot + R(p-pivot); STEP="linear"; dense STEP keys for physics; PCHIP only for smooth keys.
Animation generators: `gunanim.py` (mag_swap, charge_right, charge_right_roll, feed, fire, reload, build) used by gen_guns.py; M700 has its own `gen_m700_anim.py`.
### Models
SDF kit `sdf.py` + `meshbake.py` (MModel extends Model; cube helpers + SDF meshes). Bakes: M14 ~35 min full (H=0.30 previews ~7 min), M700/AK fast. Scripts in `tools/scripts/*.sh`.
Background jobs die at turn boundaries unless started `setsid nohup ... &`; verify the process is alive.
Hands: `gun_m700.glove(h, wrist, v, n, tdir, mat, curls, thumb_pts, sleeve_to, scale, index_curls, index_pts, flen)`; frame v=wrist->fingers, n=palm normal, u=thumb side.
Per-gun files: tools/gun_<name>.py (geometry + cfg dict: mag_grip, hand_frame, handle_grip, charge_roll, hold_open, release_mode, lift_px ...).
### Regenerate
`cd bolt-rifle-neoforge/tools; python3 gen_guns.py ../src/main/resources <gun>` ; `python3 gen_m700_anim.py ../src/main/resources` ; sounds `python3 gen_sounds.py` (needs the user's zip).
### Preview rendering
`tools/fp_render.py <res> <gun> <anim> <times> <out> hip|ads <scale> <tx,ty,tz>` (env RV="rx,ry,rz" for tilt, FULL=1 for 960x540); `pose_render.py`, `render.py` for model views.
### Git/CI
Commit footer: `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Push to `v3-realistic`; `gh run list --repo dwvarela/Bolt-Rifle-Test`.
User-provided inputs NOT in repo: Fire_Arm_References.zip, Gun_Sound_Effects.zip, the Point Blank jar (reference only). Ask the user to re-attach if needed.

## WIP (AK-47 part 2, uncommitted resources)
gun_ak.py now builds stock/grip/handguards as SDF meshes (longer stock, raked grip, butt=22.6) and handle_grip=(-3.5,2.6,-0.2) (found with tools/search_handle2.py + clip_check.py).
The full bake (`/tmp/bake_ak.sh` = `python3 gen_guns.py ../src/main/resources ak47`) was running; until its resources are committed the repo's ak47 geo/texture/animation are still the OLD model.
After the bake: refit the AK hold() in Guns.java (butt changed 19.9 -> 22.6; match the grip hand to the M700's, tools/fit_raster4.py / audit_pos.py), run audit10.py, commit resources, push, check CI.
Note: pose_render.py draws cubes in one flat colour (fixed UV) and ignores cube rotations - only SDF meshes look textured there.

## Credits (required)
AK-47 geometry is derived from GoldbergR's Sketchfab model (https://sketchfab.com/GoldbergR) - see CREDITS.md and `credits` in neoforge.mods.toml. Never remove it.
GLB reader/renderer used to inspect it: tools/glb_view.py (source file is the user's attachment ak-47_low-poly.glb; ask the user to re-attach it).
