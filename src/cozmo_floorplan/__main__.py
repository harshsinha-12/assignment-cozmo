"""Allow ``python -m cozmo_floorplan`` to invoke the CLI."""

from cozmo_floorplan.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
