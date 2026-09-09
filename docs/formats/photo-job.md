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

Current boundary: T8a validates the complete per-room evidence layout. It does not yet infer walls, adjacency, or metric scale. Until SfM/Manhattan reconstruction and an explicit scale source are available, the CLI returns `unsupported_tier` rather than printing invented centimetres.
