# Claims domain (why the numbers matter)

Read this before writing the submission README or the technical-discussion opener.

## The desk problem

A water loss is not “a photo of a ceiling.” It is rooms, affected surfaces, and quantities:

- Floor area → extraction, drying, flooring
- Wall area → drywall, paint, baseboard
- Perimeter → cove base, quarter round
- Openings → deducts, door resets
- Height → waste factors, two-coat vs one

Those quantities are typed into **Xactimate** (Verisk) or **Cotality** / Symbility-class tools. The sketch is the source of truth for many line items. Wrong sketch → supplement fights with the carrier.

Cozmo’s JD says agents already “draft the carrier-ready estimate from field photos.” A dimensioned FloorPlan is the missing structured object between pixels and line items.

## Field reality

- Crews are wet, in a hurry, at 2am, on SLA clocks measured in minutes.
- Not every contractor has iPhone Pro LiDAR. Homeowners send random photos.
- Overlap is bad. Bathrooms are shiny. Mirrors exist.
- Franchise SOPs may require a sketch even when “everyone can see the room.”

A backend that only works on a perfect RoomPlan demo is a toy. A backend that **emits LiDAR-quality JSON when LiDAR exists, and a warned, wide-interval plan when a homeowner sends six photos**, is a Cozmo primitive.

## What to emit even if they never mention claims

- Room ids and names (Bedroom 1, Hall) if guessable; else `room_0`
- Wall lengths in cm
- Door/window widths
- Area
- Confidence and warnings
- Provenance (which capture, which algorithm)

That is closer to an estimate agent’s tool output than a PNG.

## What not to fake

- Xactimate item codes (WTR, DRY, PNT, HMR)
- Depreciation
- Cause of loss
- Moisture meter readings

Geometry only, unless the official prompt adds damage understanding.
