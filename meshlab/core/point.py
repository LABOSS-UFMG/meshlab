# -------------------------------------------------------------------------------- #
import numpy as np

from collections.abc import Sequence
from numpy.typing import DTypeLike

from meshlab.utils import validation

# -------------------------------------------------------------------------------- #
class Point():
    """Store a named geometric point independently of mesh vertices.

    Attributes
    ----------
    name : str
        Geometry identifier; not automatically registered as a boundary.
    coordinates : ndarray
        Writable vector containing two or three coordinates.
    float_dtype : numpy.dtype
        Floating-point type used for coordinate storage.
    """

    # ---------------------------------------------------------------------------- #
    def __init__(
            self,
            name: str,
            coordinates: Sequence[float] | np.ndarray,
            float_dtype: DTypeLike = np.float64,
        ) -> None:
        """
        Parameters
        ----------
        name : str
            Point identifier.
        coordinates : array_like, shape (2,) or (3,)
            Finite coordinates, copied independently of the input.
        float_dtype : numpy dtype-like, default=numpy.float64
            Coordinate storage type: float32 or float64.
        """
        # ------------------------------------------------------------------------ #
        # Validate constructor arguments and copy coordinates
        validation.is_float_dtype(float_dtype)
        coordinates = np.array(coordinates, dtype=float_dtype, copy=True)
        validation.is_point_coordinates(coordinates)

        # ------------------------------------------------------------------------ #
        # Store constructor arguments
        self._name = name
        self._float_dtype = np.dtype(float_dtype)
        self._coordinates = coordinates

        # ------------------------------------------------------------------------ #
        return None

    # ---------------------------------------------------------------------------- #
    @property
    def name(self) -> str:
        """Identifier of the geometric point."""
        return self._name

    @property
    def coordinates(self) -> np.ndarray:
        """Writable coordinates; edits are not validated automatically."""
        return self._coordinates

    @property
    def float_dtype(self) -> np.dtype:
        """Floating-point dtype used for coordinates."""
        return self._float_dtype

# -------------------------------------------------------------------------------- #
