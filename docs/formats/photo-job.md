# Photo job layout

The photo tier uses one subfolder per room. Each room must contain **2 to 8** decodable images; the benchmark capture should use all 8. Folder names become stable room identifiers later in reconstruction.

```text
job/
  manifest.yaml
  photos/
    kitchen/
      01.jpg
      02.jpg
    hallway/
      01.jpg
      02.jpg
```

Supported ingest extensions are JPEG, PNG, and WebP. Use JPEG for the submitted iPhone route. Hidden folders and unrelated files are ignored; corrupt images, undersized images, empty room folders, and counts outside 2–8 return a structured `incomplete_scan` failure.

## Overlap graph

T8b first bounds each image to 900 px and extracts up to 1,800 ORB features.
T8b2 adds a bounded 1,200 px, 3,000-feature CLAHE+SIFT fallback for indoor
images whose useful texture is too low-contrast or viewpoint-sensitive for
ORB. Each method retains mutual ratio matches and runs seeded homography and
fundamental-matrix RANSAC. The acceptance counts, ratios, and normalized
convex-hull coverage gates are unchanged; SIFT's 2.5 px threshold at 1,200 px
is tighter in normalized image coordinates than ORB's 2 px at 900 px.
Within-room edges build named connected components; stricter cross-room edges
produce connector candidates, not automatic adjacency.

Current private result:

| Room | Eligible/possible edges | Components | Connected |
| --- | ---: | ---: | --- |
| connector | 3/10 | 2 | no |
| drawing-room | 6/28 | 2 | no |
| my-room | 3/28 | 5 | no |
| pooja-room | 6/28 | 3 | no |

The ensemble finds conservative connector candidates for connector↔my-room and
connector↔pooja-room, but no room graph is fully connected. The CLI therefore
still returns `insufficient_overlap`, now naming isolated images where possible.
These are graph diagnostics, not metric accuracy.

Current boundary: a connected overlap graph with recoverable parallax runs
incremental SfM, a disclosed 1.45 m handheld-height prior, and a Manhattan
envelope. Planar overlap without parallax returns `low_confidence`. The current
private rooms remain disconnected, so they still return `insufficient_overlap`.
Cross-room photo rooms are independently placed; they are not overlaid.
