# Interview prep (technical discussion)

The take-home is step 2. This file is for step 3. Fill `Your numbers` after evals exist. Do not memorize a script — memorize the physics and the product.

## Opener (60 seconds)

Cozmo already has to turn field photos into estimate geometry. I treated the assignment as a **platform primitive**: one FloorPlan schema, three capture adapters, stitch through doors, eval in centimetres, provenance on every length. LiDAR is metric from RoomPlan. Video is metric if poses or IMU exist. Photos are similarity-only until a prior shows up — I will not print fake centimetres. That is the same honesty you want in an agent that must not invent scope.

## Whiteboard: why photos cannot do cm alone

- Two scenes that differ by a scale factor look identical in images.
- COLMAP (and any bundle adjustment of 2D correspondences) therefore emits an arbitrary scale.
- You inject scale with depth, metric poses, or one known length.
- Then you still need regularization or the walls will not be walls.

If they push: “Could a VLM read the tape in the photo?” Yes, as a **prior**, with a confidence, eval’d. Not as a replacement for reconstruction.

## Whiteboard: system

Draw: job dir → normalizer → adapters → IR → stitch → SVG/eval.

Talk fallbacks: insufficient overlap, missing LiDAR, non-Manhattan, partial scan.

Talk eval: synthetic fixture proves plumbing; real tape proves physics; RoomPlan is not its own ground truth.

## Product questions they might ask

**Why not just magicplan?**  
You would. In production you’d integrate. The take-home is the backend object you’d still need if magicplan is the capture app: structured rooms, evals, agent-consumable JSON. Cozmo’s JD is reverse-engineer and make programmable, not NIH a capture app.

**How does this become an agent tool?**  
`run_floorplan(job) -> FloorPlan`. The estimate agent calls it, then writes line items. Warnings become HITL (“confirm this 80 cm door”). Provenance is the APE-shaped audit trail.

**Hurricane week, volume triples.**  
Batch jobs, fail closed with structured errors, LiDAR path is cheaper/faster than photos SfM, queue homeowners’ stills, do not block dispatch on a perfect sketch.

**996 / culture.**  
Separate conversation. Do not volunteer a speech. If asked, be literal about whether you will do the schedule. This file is not a culture script.

## Questions worth asking them

- What does the field actually send today (Encircle photos vs LiDAR vs 360)?
- Is the first production path iPhone Pro crews or homeowner FNOL photos?
- Do you want ESX out or your own sketch object in APE state?
- How do you eval visual agents now?

## After the take-home exists

Add:

- Link to eval table
- One failure you are proud of (a job you refused to metric-scale)
- One thing you’d build in week one (probably LiDAR ingest in the real capture stack they already have)
