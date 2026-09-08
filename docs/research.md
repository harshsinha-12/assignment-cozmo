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
