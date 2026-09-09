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

T8b bounds each image to 900 px, extracts up to 1,800 ORB features, retains
mutual Hamming ratio matches, and runs seeded homography and fundamental-matrix
RANSAC. The stronger geometric support model is accepted only with minimum
match, inlier, inlier-ratio, and convex-hull coverage evidence. Within-room
edges build connected components; stricter cross-room edges produce connector
candidates, not automatic adjacency.

Current private result:

| Room | Eligible/possible edges | Components | Connected |
| --- | ---: | ---: | --- |
| drawing-room | 3/21 | 4 | no |
| my-room | 2/28 | 6 | no |
| pooja-room | 2/28 | 6 | no |

No room pair has an eligible cross-room connector image. The CLI therefore
returns `insufficient_overlap` and asks for intermediate views with at least
60% visual overlap. These are graph diagnostics, not metric accuracy.

Current boundary: metric SfM, adjacency verification, walls, and scale are not
implemented. A connected graph would advance to `unsupported_tier`; it would
not cause invented centimetres.
