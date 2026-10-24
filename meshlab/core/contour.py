# -------------------------------------------------------------------------------- #
from collections.abc import Iterable

from meshlab.core.curve import Curve
from meshlab.utils import validation

# -------------------------------------------------------------------------------- #
class Contour():
    """Store a closed sequence of oriented curves.

    Attributes
    ----------
    name : str
        Name of the composed contour.
    curves : tuple of Curve
        Curves referenced in traversal order, without copying or reversal.
    tolerance : float
        Absolute endpoint matching tolerance, in coordinate units.
    """

    # ---------------------------------------------------------------------------- #
    def __init__(
            self,
            name: str,
            curves: Iterable[Curve],
            tolerance: float = 1e-10,
        ) -> None:
        """
        Parameters
        ----------
        name : str
            Nonempty name of the composed contour.
        curves : iterable of Curve
            Curves in traversal order. The end of each must match the start
            of the next, including the last-to-first junction.
        tolerance : float, default=1e-10
            Finite, nonnegative absolute endpoint matching tolerance.
        """
        # ------------------------------------------------------------------------ #
        # Materialize the ordered sequence
        curves = tuple(curves)

        # ------------------------------------------------------------------------ #
        # Validate constructor arguments
        validation.is_contour(curves, tolerance)

        # ------------------------------------------------------------------------ #
        # Store constructor arguments
        self._name = name
        self._curves = curves
        self._tolerance = float(tolerance)

        # ------------------------------------------------------------------------ #
        return None

    # ---------------------------------------------------------------------------- #
    @property
    def name(self) -> str:
        """Name associated with the composed contour."""
        return self._name

    @property
    def curves(self) -> tuple[Curve, ...]:
        """Ordered references to the curves forming the contour."""
        return self._curves

    @property
    def tolerance(self) -> float:
        """Absolute endpoint matching tolerance used during construction."""
        return self._tolerance

# -------------------------------------------------------------------------------- #
