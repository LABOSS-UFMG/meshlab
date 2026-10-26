# -------------------------------------------------------------------------------- #
from dataclasses import dataclass

from meshlab.core.point import Point
from meshlab.core.curve import Curve
from meshlab.core.contour import Contour
from meshlab.utils import validation

# -------------------------------------------------------------------------------- #
@dataclass(slots=True, repr=False, eq=False)
class Refinement():
    """Associate geometry with a local mesh size and a smooth transition.

    Parameters
    ----------
    geometry : Point | Curve | Contour
        Reference geometry, not copied or inserted into mesh.boundaries.
        Point selects a neighborhood; Curve selects a band around its
        polyline; Contour selects the interior of its simple closed polygon.
    size : float
        Positive desired element size in the refined region.
    distance : float, default=0.0
        Nonnegative distance around the geometry with constant fine size.
        For Contour, expands the fine region outwards from its perimeter.
    transition : float, default=1.0
        Positive width of the smooth return to the unrefined local size.
    """
    geometry: Point | Curve | Contour
    size: float
    distance: float = 0.0
    transition: float = 1.0

    # ---------------------------------------------------------------------------- #
    def __post_init__(self) -> None:
        """Validate constructor data using the shared validation module."""
        # ------------------------------------------------------------------------ #
        # Validate geometry type and numeric sizing parameters
        validation.is_union(self.geometry, (Point, Curve, Contour))
        validation.is_refinement_parameters(self.size, self.distance, self.transition)

        # ------------------------------------------------------------------------ #
        return None

# -------------------------------------------------------------------------------- #
