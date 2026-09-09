• Reshooting without WhatsApp is a good idea. Keep the current captures as backups until the new set is validated. Use AirDrop, USB/Image
  Capture, iCloud Drive, or the Files app so the original resolution, orientation metadata, and EXIF remain intact.

  ## Recommended order for tonight

  ### 1. Prepare the rooms

  Use the same three physical rooms:

  - drawing-room
  - my-room
  - pooja-room

  Choose one of them as the damage and repeatability room. I recommend my-room.

  Before recording:

  - Turn on every indoor light.
  - Open curtains if outside light helps.
  - Remove private documents and faces.
  - Keep furniture in the same position for all captures.
  - Clean the camera and LiDAR lenses.
  - Use the rear 1× camera.
  - Do not use digital zoom, Portrait, Cinematic, filters, or WhatsApp.

  Do not shoot in genuinely dark conditions just because it is nighttime. Bright, even artificial lighting is fine.

  ## 2. Create safe staged damage

  A book or photo frame alone is an object, not surface damage. You may include one as context, but create two visible mock damage regions on a
  wall or floor.

  Use my-room and stage:

  ### Damage class A: water stain

  - Paint or draw an irregular brown/yellow stain on paper or cardboard.
  - Approximate size: 20–40 cm.
  - Temporarily tape it flat against the wall.
  - Do not apply water or paint directly to your wall.

  ### Damage class B: tear or puncture

  - Take a separate piece of cardboard.
  - Tear or puncture its centre.
  - Tape it flat against another part of the same wall.
  - Approximate size: 10–25 cm.

  You can place a fallen book or crooked photo frame nearby to suggest the cause, but the visible cardboard/paper region is what represents the
  damage.

  Take separate evidence photos:

  - One wide photo showing both damage regions and the entire wall.
  - One close-up of the water stain.
  - One close-up of the tear/puncture.
  - One photo of each with a ruler or measuring tape beside it.

  Put them here:

  data/private/benchmark-evidence/damage/
    my-room-damage-wide.jpg
    my-room-water-stain-close.jpg
    my-room-water-stain-measurement.jpg
    my-room-puncture-close.jpg
    my-room-puncture-measurement.jpg

  Write their approximate dimensions in:

  data/private/benchmark-evidence/damage/measurements.txt

  For example:

  water-stain:
  wall: my-room wall-b
  width: 32.0 cm
  height: 21.5 cm

  puncture:
  wall: my-room wall-b
  width: 14.2 cm
  height: 11.8 cm

  Leave the staged damage in place while taking the new photos, video and repeat LiDAR scan.

  ## 3. Reshoot the photos

  On the iPhone:

  Settings → Camera → Formats → Most Compatible

  This should preserve ordinary JPEG/H.264-compatible originals. Shoot landscape, at 1×, approximately chest height.

  Create a new job instead of deleting the existing one:

  data/private/benchmark-photos-night/
    manifest.yaml
    photos/
      drawing-room/
      my-room/
      pooja-room/
      connector/

  Take exactly eight geometry photos per room:

  1. From the entrance, with the complete door frame visible.
  2. First wall, showing both corners.
  3. Second wall, showing both corners.
  4. Third wall, showing both corners.
  5. Fourth wall, showing both corners.
  6. Looking through the doorway toward the connected room.
  7. Ceiling-to-wall junction on the longest wall.
  8. An overlapping corner view.

  For my-room, photo 8 may show the staged damage in wider context. Keep the detailed damage close-ups in benchmark-evidence/damage/ so the room
  folder remains exactly eight images.

  Suggested filenames:

  01-doorway.jpg
  02-wall-a.jpg
  03-wall-b.jpg
  04-wall-c.jpg
  05-wall-d.jpg
  06-through-door.jpg
  07-ceiling-wall.jpg
  08-overlap-or-damage.jpg

  Hold still for one second before pressing the shutter. Make sure each wall overlaps with the previous image and that corners are visible.

  ## 4. Handle the “hallway” or connector

  You do not need to invent a fake hallway. The official requirement is really asking for evidence that establishes how rooms connect.

  Use the genuine doorway or transition between two rooms and call it connector.

  For example:

  drawing-room → doorway/transition → my-room

  Take eight connector photographs:

  1. From drawing room toward the doorway.
  2. Full doorway frame from the drawing-room side.
  3. Standing at the doorway looking into my-room.
  4. From my-room looking back into drawing-room.
  5. Left side of the transition.
  6. Right side of the transition.
  7. Floor threshold.
  8. Wide view showing the relationship between both spaces.

  If your rooms do not directly connect, use the real entrance lobby, landing, passage or other small transition area. Document it as an “open
  doorway connector” instead of calling it a hallway.

  ## 5. Reshoot the video

  The strongest video capture is one continuous whole-property walkthrough, rather than isolated room videos.

  Use:

  - Camera app
  - Rear 1× lens
  - Landscape orientation
  - 1080p at 30 fps
  - Normal Video mode
  - No Cinematic mode
  - Approximately chest height
  - Target duration: 60–180 seconds

  Route:

  1. Start outside or at the entrance to the drawing room.
  2. Pause for two seconds while showing the complete doorway.
  3. Slowly walk the perimeter of the drawing room.
  4. Pause at every corner.
  5. Point briefly toward the ceiling and floor.
  6. Walk through the real connector/doorway without stopping the recording.
  7. Walk the perimeter of my-room.
  8. Pause on the staged damage—first a wider view, then closer.
  9. Continue through the next connection.
  10. Walk around pooja-room.
  11. End after showing its doorway again.

  Save the original as:

  data/private/benchmark-video-night/video/whole-property.mov

  You can additionally keep separate videos:

  drawing-room.mov
  my-room.mov
  pooja-room.mov

  But whole-property.mov is the most important because it provides cross-room continuity.

  If you do not want to reshoot everything, at minimum add:

  data/private/benchmark-video/video/drawing-room.mp4

  However, that still provides weaker stitching evidence than a continuous property walkthrough.

  ## 6. Record a continuous LiDAR scan

  Keep the existing three .r3d files.

  Add one new Record3D scan that crosses at least one real doorway:

  data/private/benchmark-lidar/lidar/property-connector.r3d

  During the scan:

  - Cover the floor and ceiling.
  - Cover every wall.
  - Move slowly.
  - Pause at corners and doorways.
  - Walk from one room through the doorway into another.
  - Do not stop the session while crossing the connector.
  - Do not cover the LiDAR sensor with the phone case or your hand.
  - Export the original Shareable/Internal .r3d archive.

  This provides a shared camera coordinate system between rooms, which will help stitching considerably.

  ## 7. Make the repeat LiDAR capture

  Start a completely new Record3D session for my-room.

  Do not duplicate the existing file.

  data/private/benchmark-lidar/lidar/
    my-room.r3d
    my-room-repeat.r3d

  For the repeat:

  - Keep furniture unchanged.
  - Leave the staged damage in place if possible.
  - Follow approximately the same walking route.
  - Cover every wall, doorway, floor and ceiling again.
  - Export the complete original .r3d.

  You do not need to repeat every room. One independently repeated room is the minimum requirement.

  ## 8. Collect tape or laser ground truth

  This is independent of the phone captures. It tells us the real answer.

  Choose a consistent naming convention. Stand at each room entrance and name the walls clockwise:

  wall-a
  wall-b
  wall-c
  wall-d

  Measure in centimetres:

  - Every wall
  - Every door width and height
  - Every window width and height
  - Ceiling height
  - One floor diagonal per room

  Example:

  my-room:
    wall-a: 365.2 cm
    wall-b: 291.4 cm
    wall-c: 364.8 cm
    wall-d: 290.9 cm
    entrance-door-width: 81.2 cm
    entrance-door-height: 209.8 cm
    window-width: 142.5 cm
    window-height: 119.7 cm
    ceiling-height: 274.5 cm
    diagonal: 467.3 cm

  Save your notes here:

  data/private/benchmark-ground-truth/measurements.txt

  Also photograph the tape or laser reading:

  data/private/benchmark-ground-truth/photos/
    my-room-wall-a.jpg
    my-room-wall-b.jpg
    my-room-door-width.jpg
    my-room-door-height.jpg
    my-room-ceiling.jpg
    my-room-diagonal.jpg

  You do not need to prepare JSON. I will turn the notes into the required ground_truth.json.

  ## 9. Make the incumbent-app comparison

  Use either magicplan or Polycam—not both.

  Scan the same two rooms:

  - drawing-room
  - my-room

  Magicplan is preferable if it lets you export a dimensioned PDF and statistics CSV.

  From the incumbent app, collect:

  - Dimensioned floor-plan PDF
  - CSV/statistics export, if available
  - PNG or SVG plan, if available
  - Screenshots showing wall measurements
  - Exact application version
  - Device name
  - Original share link, if provided

  Save under:

  data/private/benchmark-incumbent/
    magicplan-<version>/
      drawing-room-plan.pdf
      drawing-room-statistics.csv
      my-room-plan.pdf
      my-room-statistics.csv
      screenshots/
      notes.txt

  If using Polycam:

  data/private/benchmark-incumbent/
    polycam-<version>/

  If PDF/CSV export requires payment, do not purchase anything just for this without checking first. Save measurement screenshots and the share
  link as a fallback.

  ## 10. Transfer the originals

  Preferred methods:

  - AirDrop directly to the Mac
  - USB with Image Capture
  - Save to iCloud Drive/Files
  - Original-quality cloud storage

  Avoid:

  - WhatsApp
  - Instagram
  - Email clients that resize attachments
  - Screenshots of photos
  - Editing or exporting through another application

  Do not delete the old captures. Put the reshoot in new *-night folders until I validate it.

  ## Final checklist

  Before telling me the upload is ready, confirm:

  - [ ] 8 original JPEGs for drawing room
  - [ ] 8 original JPEGs for my-room
  - [ ] 8 original JPEGs for pooja-room
  - [ ] Connector/doorway photographs
  - [ ] One continuous 1080p whole-property video
  - [ ] Drawing-room video, if retaining separate videos
  - [ ] Existing three .r3d scans preserved
  - [ ] One continuous connector LiDAR scan
  - [ ] One independent repeat LiDAR scan
  - [ ] Two safe staged damage classes
  - [ ] Wide and close-up damage evidence
  - [ ] Damage dimensions
  - [ ] Tape/laser wall measurements
  - [ ] Door, window and ceiling measurements
  - [ ] Measurement evidence photographs
  - [ ] magicplan or Polycam output for two rooms
  - [ ] Exact Record3D and incumbent-app versions
  - [ ] Files transferred without WhatsApp compression

  Once these are uploaded, the next work order should be T6b LiDAR geometry first, followed by video orientation/multi-file handling, photo
  reconstruction, and finally the real benchmark evaluation.