# Research notes

Researched 2026-09-07. Extend this file instead of opening a new search tab for the same questions.

## Scale and SfM

Image-only structure-from-motion recovers a scene **up to a similarity transform**. Global scale is not observable. COLMAP’s FAQ/issues state this repeatedly: you need a known 3D distance, known camera poses (metric), or GPS/control points (`model_aligner`, `pose_prior_mapper`). GPS is the wrong prior indoors.

Practical indoor scale priors: LiDAR/depth, ARKit/ARCore camera translations, a measured door, a taped wall, ceiling height + vertical vanishing line, a reference object (less reliable).

Vanishing points give direction and, with a known length, metric structure in Manhattan scenes. They do not magically give scale alone.

## Apple RoomPlan

`CapturedRoom` (Codable) contains `walls`, `doors`, `windows`, `openings`, `objects`. Surfaces have dimensions (length/height/width in **metres**), a 4×4 transform, confidence, identifier. Export: JSON/Plist via encode, USDZ via `export(to:)`. iOS 17: `StructureBuilder` merges rooms into `CapturedStructure`; export can include a UUID↔USDZ node map.

Linux agents should prefer the JSON. USDZ is a fallback if someone only airdrops a file.

Docs: https://developer.apple.com/documentation/roomplan/capturedroom  
WWDC 2022 session 10127; WWDC 2023 session 10192.

### T6 format check (2026-09-08)

Apple documents RoomPlan walls as `CapturedRoom.Surface` values; surfaces expose metric dimensions and a 4×4 transform. T6 therefore normalizes those fields into the explicit portable contract in `docs/formats/roomplan-json.md` rather than depending on an undocumented JSONEncoder layout. Sources: [CapturedRoom walls](https://developer.apple.com/documentation/roomplan/capturedroom/walls), [surface/object positioning fields](https://developer.apple.com/documentation/roomplan/capturedroom/object/dimensions).

Record3D's official streaming API exposes a float depth frame, confidence frame, camera intrinsics `(fx, fy, tx, ty)`, and pose `(qx, qy, qz, qw, tx, ty, tz)`. The project owner also confirms that `.r3d` metadata contains poses and uses a right-handed OpenGL coordinate system. Sources: [official Python demo](https://github.com/marek-simonik/record3d/blob/master/demo-main.py), [official structs](https://github.com/marek-simonik/record3d/blob/master/include/record3d/Record3DStructs.h), [format clarification](https://github.com/marek-simonik/record3d/issues/59).

Three September 9 captures established the on-disk contract: `.r3d` is a ZIP
with JSON `metadata`, matched `rgbd/<index>.jpg/.depth/.conf`, float32-metre
depth compressed with LZFSE, uint8 confidence compressed with LZFSE, and one
pose/intrinsic/timestamp row per frame. T6a decodes and validates this; T6b must
still fuse the points and fit planes.

### T6b1 coordinate check (2026-09-09)

The official structs order pose values as XYZW quaternion then XYZ position and
label the intrinsics as RGB coefficients. The maintainer confirms an OpenGL
right-handed frame whose viewing direction is negative Z; the official stream
header defines confidence as low=0, medium=1, high=2. T6b1 therefore scales RGB
intrinsics to the depth resolution, back-projects forward depth on negative Z,
and applies the pose as camera-to-world. On all three real captures this
convention produces strong paired horizontal floor/ceiling bands; reversing Z
does not. Sources: [official structs](https://github.com/marek-simonik/record3d/blob/master/include/record3d/Record3DStructs.h), [maintainer coordinate answer](https://github.com/marek-simonik/record3d/issues/59), [official confidence buffer](https://github.com/marek-simonik/record3d/blob/master/include/record3d/Record3DStream.h).

## Libraries (Python, Cloud-Agent friendly first)

| Library | Use | Weight |
| --- | --- | --- |
| numpy / scipy | geometry | light |
| opencv-python-headless | features, SfM building blocks, video frames | light |
| shapely | 2D polygons, wall unions | light |
| matplotlib | debug plots | light |
| pillow | images | light |
| pyyaml / jsonschema | job + IR | light |
| ffmpeg (system) | video sample | medium |
| open3d | planes, clouds | heavy |
| COLMAP / pycolmap | photos SfM | heavy |
| trimesh | USDZ/mesh if needed | medium |

Avoid pulling PyTorch unless the prompt forces a detector. Classical walls + RoomPlan will outperform a rushed YOLO-on-three-photos story for this problem.

## Related products (know them, do not clone)

- **magicplan** — LiDAR auto-scan, Xactimate ESX export. This is the incumbent a restoration franchise already pays for.
- **Matterport / Polycam / KIRI / CamPlan** — capture apps with various LiDAR/photogrammetry paths.
- **Apple RoomPlan sample** — the SDK we ingest.

The take-home is not “beat magicplan in a week.” It is “show you can build the backend primitive magicplan-class data would flow through.”

## Floor-plan from images (academic keywords)

If you need papers later: FloorNet, CubiCasa5K, raster-to-vector (Liu et al.), LayoutNet, HorizonNet, Atlanta/Manhattan world. For a take-home, **do not reimplement FloorNet**. Use geometric priors.

## Xactimate / ESX

Estimates travel as `.esx` (zip-ish containers). magicplan emails an ESX. Sketch templates use `.skx`. There is no blessed public “floorplan.json” from Verisk. Third-party converters exist (e.g. ESX → Symbility FML). Writing ESX without a spec is a time sink. IR → (optional later) ESX.

## Cozmo vision

https://www.hellocozmo.ai/see — they already sell visual understanding of damage photos and video. A floor-plan stack is adjacent: geometry + evidence, not a separate company.
