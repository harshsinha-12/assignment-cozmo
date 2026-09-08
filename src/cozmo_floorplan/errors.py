"""Domain exceptions that can be converted into structured CLI output."""


class CozmoFloorPlanError(Exception):
    """Base class for expected application errors."""


class JobLoadError(CozmoFloorPlanError):
    """The job folder or manifest cannot be used."""

    def __init__(self, message: str, *, warning_code: str = "incomplete_scan") -> None:
        super().__init__(message)
        self.warning_code = warning_code


class SchemaLocationError(CozmoFloorPlanError):
    """The canonical FloorPlan schema cannot be located."""


class OutputValidationError(CozmoFloorPlanError):
    """Generated output does not satisfy the FloorPlan contract."""


class EvaluationInputError(CozmoFloorPlanError):
    """An evaluation input cannot be read or does not match the schema."""
