# Capture route (Route 2) — what they follow at the defense

**Status:** draft for submission. This page must stay one printed page. Ambiguity is scored against us.

We submit **one** capture route. This page is Route 2 (always ready). A Route 1 iOS build is a parallel track (`TASKS.md` T21); switch this page only if that build installs in under 10 minutes.

Named tools below are App Store / built-in.

**Apps**

| Tier | Install | What to export |
| --- | --- | --- |
| Photos | iPhone **Camera** (built-in) | JPEG stills, not Live Photos, not Portrait |
| Video | iPhone **Camera** | One `MOV` or `MP4`, 1080p, rear camera |
| LiDAR | **Record3D** (free tier) on iPhone Pro / Pro Max | Depth + poses + intrinsics (their “export for research” / CSV+PNG or `.r3d` as documented in README). If Record3D is unavailable, fallback: **3D Scanner App** USDZ + any pose/depth export the README lists. |

Do **not** use Polycam or magicplan for capture. Those are the Part 3 incumbents we compare against.

**Hardware**

- Photos / video: any iPhone 15 or newer.
- LiDAR: iPhone 15 Pro / 16 Pro / **17 Pro** / Pro Max. If the device has no LiDAR, that tier cannot run; photos and video still must.

**Before walking**

- Turn on lights. No flash. No zoom. Rear camera only.
- Lock orientation landscape for photos.
- Clear people and pets from frames when possible.
- Walk slowly. Pause at every corner and every door.

**Photos (exactly 8 stills per room — protocol max)**

One folder per room, named `photos/<room_label>/`.

For each room, shoot **exactly 8 JPEGs**:

1. Standing in the doorway, facing in (include the full door frame).
2–5. One shot per wall, phone at chest height, both corners of that wall in frame.
6. Through the doorway toward the next room (or hallway).
7. Ceiling–wall junction on the longest wall.
8. Second overlap / corner shot (or damage close-up if this room is damaged).

If a room has more than four walls, keep the door + through-door + ceiling shots and allocate the rest to walls, still **exactly 8**. Never fewer than 8 unless the room physically cannot; then shoot every wall and note it.

**Video (one clip per property)**

- Start at the entry, chest height, 1080p.
- Walk the perimeter of room 1, pause 2 seconds at each corner, walk through the door into the next room, repeat.
- Include the connector (hallway) as its own slow pass.
- Stop after the last room. Target 60–180 seconds. No selfie camera, no running.

**LiDAR (Pro)**

- Open Record3D. Start a new recording in the first room. Cover every wall, floor band at waist height, and each opening. Walk into the next room without stopping the session if the app supports a continuous scan; otherwise start a new scan per room and keep order in the folder names.
- Export the session into `lidar/` as the README specifies (do not email AirDrop previews only).

**Hand-off folder they give us**

```text
job/
  manifest.yaml          # we provide a template; they fill device model + tier
  photos/<room>/         # JPEGs, photo tier
  video/walkthrough.mov  # video tier
  lidar/                 # LiDAR tier export
```

One capture = one tier. Do not mix photos and LiDAR in the same job folder unless `manifest.yaml` says `tier: mixed` (we will not ask for mixed at the walk-in).

**Avoid**

Mirrors dead-on, shooting through glass, wet glossy floors as the only floor evidence, digital zoom, cinematic mode, portrait mode, covering the LiDAR with a case lip.

**If something is unclear**

This page is the spec. If a step is missing, do the conservative thing (more overlap, slower walk) rather than inventing a new app.
