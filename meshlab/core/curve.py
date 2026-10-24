# -------------------------------------------------------------------------------- #
import numpy as np

from collections.abc import Sequence
from numpy.typing import DTypeLike

from meshlab.utils import validation

# -------------------------------------------------------------------------------- #
class Curve():
    """Store a named curve as ordered points.

    Attributes
    ----------
    name : str
        Boundary name preserved during assembly and export.
    points : ndarray
        Writable coordinate array with shape (num_points, 2) or (num_points, 3).
    float_dtype : numpy.dtype
        Floating-point type used for coordinate storage.

    Notes
    -----
    Point order is preserved, never automatically reversed. In 2D the intended
    normal is tangent cross ez.
    """

    # ---------------------------------------------------------------------------- #
    def __init__(
            self,
            name: str,
            points: Sequence[Sequence[float]] | np.ndarray,
            float_dtype: DTypeLike = np.float64,
        ) -> None:
        """
        Parameters
        ----------
        name : str
            Nonempty boundary name.
        points : array_like, shape (N, 2) or (N, 3)
            At least two finite ordered points. Consecutive coincident points
            are rejected. Coordinates are copied, independently of the input.
        float_dtype : numpy dtype-like, default=numpy.float64
            Coordinate storage type: float32 or float64.
        """
        # ------------------------------------------------------------------------ #
        # Validate constructor arguments
        validation.is_float_dtype(float_dtype)

        # ------------------------------------------------------------------------ #
        # Store constructor arguments
        self._name = name
        self._float_dtype = np.dtype(float_dtype)

        # ------------------------------------------------------------------------ #
        # Copy coordinates and validate the stored representation
        self._points = np.array(points, dtype=self._float_dtype, copy=True)

        # ------------------------------------------------------------------------ #
        return None

    # ---------------------------------------------------------------------------- #
    @property
    def name(self) -> str:
        """Boundary name associated with the curve."""
        return self._name

    @property
    def float_dtype(self) -> np.dtype:
        """Floating-point dtype used for coordinates."""
        return self._float_dtype

    @property
    def points(self) -> np.ndarray:
        """Writable coordinates; edits are not validated automatically."""
        return self._points

# -------------------------------------------------------------------------------- #
