# -------------------------------------------------------------------------------- #
from typing import Any
from numbers import Number
import math
import numpy as np
from collections.abc import Sequence

# -------------------------------------------------------------------------------- #
def is_int(x: Any) -> None:
    """
    Validate that x is an integer.

    Parameters
    ----------
    x : Any
        The value to validate.
    """
    # ---------------------------------------------------------------------------- #
    if not isinstance(x, int):
        raise TypeError(f"Expected an integer, got '{type(x).__name__}'.")
    # ---------------------------------------------------------------------------- #
    return None

# -------------------------------------------------------------------------------- #
def is_sequence(x: Any, size: int | None, dtype: Any) -> None:
    """
    Validate if x is a Sequence witha given size and contents dtype.

    Parameters
    ----------
    x : Any
        The value to validate.
    size : int | None
        The expected size of the sequence. If None, size is not checked.
    dtype : Any
        The expected type of the elements in the sequence.
    """
    # ---------------------------------------------------------------------------- #
    if not isinstance(x, Sequence):
        raise TypeError(f"Expected a sequence, got '{type(x).__name__}'.")

    if not (size is None):
        if len(x) != size:
            raise ValueError(f"Expected a sequence of length {size}, got {len(x)}.")

    for value in x:
        if not isinstance(value, dtype):
            raise TypeError(
                f"Expected elements of type '{dtype.__name__}', "
                f"got '{type(value).__name__}'."
            )
    # ---------------------------------------------------------------------------- #
    return None

# -------------------------------------------------------------------------------- #
def is_object(x: Any, object: Any) -> None:
    """
    Validate if x is of type object.

    Parameters
    ----------
    x : Any
        The value to validate.
    object : Any
        The expected type of x.
    """
    # ---------------------------------------------------------------------------- #
    if not isinstance(x, object):
        raise TypeError(f"Expected an object of type '{type(object).__name__}'.")

    # ---------------------------------------------------------------------------- #
    return None

# -------------------------------------------------------------------------------- #
def is_union(x: Any, dtypes: Sequence[Any]) -> None:
    """
    Validate if x dtype is one of the types in dtypes.

    Parameters
    ----------
    x : Any
        The value to validate.
    dtypes : Sequence[Any]
        The expected types of x.
    """
    # ---------------------------------------------------------------------------- #
    if not isinstance(x, tuple(dtypes)):
        raise TypeError(f"Expected an object of type '{type(x).__name__}' "
                f"got '{type(x).__name__}'."
        )

    # ---------------------------------------------------------------------------- #
    return None

# -------------------------------------------------------------------------------- #
def is_positive_int(value: Any, name: str = "value") -> None:
    """Require a strictly positive integer, excluding booleans.

    Parameters
    ----------
    value : Any
        Constructor argument to validate; NumPy integer scalars are accepted.
    name : str, default="value"
        Parameter name used in the error message.
    """
    if isinstance(value, bool) or not math.isfinite(value) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} must be a positive integer.")

def is_positive_float(value: Any, name: str = "value") -> None:
    """Require a strictly positive float.

    Parameters
    ----------
    value : Any
        Constructor argument to validate; NumPy float scalars are accepted.
    name : str, default="value"
        Parameter name used in the error message.
    """
    if not isinstance(value, Number) or not math.isfinite(value) or value < 0.0:
        raise ValueError(f"{name} must be a positive integer.")

# -------------------------------------------------------------------------------- #
def is_float_dtype(value: Any) -> None:
    """Require a NumPy dtype-like value identifying float32 or float64."""
    try:
        dtype = np.dtype(value)
    except (TypeError, ValueError):
        raise ValueError("float_dtype must be float32 or float64.") from None
    if value is None or dtype not in (np.dtype(np.float32), np.dtype(np.float64)):
        raise ValueError("float_dtype must be float32 or float64.")


# -------------------------------------------------------------------------------- #
def is_int_dtype(value: Any) -> None:
    """Require a NumPy dtype-like value identifying signed int32 or int64."""
    try:
        dtype = np.dtype(value)
    except (TypeError, ValueError):
        raise ValueError("int_dtype must be int32 or int64.") from None
    if value is None or dtype not in (np.dtype(np.int32), np.dtype(np.int64)):
        raise ValueError("int_dtype must be int32 or int64.")


# -------------------------------------------------------------------------------- #
def is_contour(
        curves: tuple,
        tolerance: float,
    ) -> None:
    """Validate the constructor arguments of an ordered closed contour.

    Parameters
    ----------
    curves : tuple
        Nonempty ordered sequence of curve objects with compatible dimensions.
    tolerance : float
        Finite, nonnegative absolute endpoint matching tolerance.
    """
    for i in range(len(curves) - 1):
        if np.linalg.norm(curves[i].points[-1] - curves[i + 1].points[0]) > tolerance:
            raise ValueError("Curves must form an ordered closed contour.")

    if np.linalg.norm(curves[-1].points[-1] - curves[0].points[0]) > tolerance:
        raise ValueError("Curves must form an ordered closed contour.")

# -------------------------------------------------------------------------------- #
def is_front(
        name: str,
        edge: np.ndarray,
        int_dtype,
    ) -> None:
    """Validate independent front constructor data.

    Parameters
    ----------
    name : str
        Nonempty front identifier.
    edge : ndarray
        Integer edge connectivity of shape (N, 2).
    int_dtype : numpy dtype-like
        Destination integer type; indices must fit without overflow.

    Notes
    -----
    No mesh is required. Vertex existence, adjacency, orientation and
    geometric validity must be handled separately when operating on a mesh.
    """
    if not isinstance(name, str) or not name:
        raise ValueError("name must be a nonempty string.")
    if edge.ndim != 2 or edge.shape[1] != 2 or edge.dtype.kind not in "iu":
        raise ValueError("Edge connectivity must be an integer (N, 2) array.")
    if np.any(edge < 0):
        raise ValueError("Front vertex indices must be nonnegative.")
    if np.any(edge > np.iinfo(int_dtype).max):
        raise ValueError("Front vertex indices exceed the destination integer type.")
    if np.any(edge[:, 0] == edge[:, 1]):
        raise ValueError("Front edges must have distinct vertices.")

# -------------------------------------------------------------------------------- #
def is_point_coordinates(coordinates: np.ndarray) -> None:
    """Require a finite coordinate vector of length two or three."""
    if coordinates.shape not in ((2,), (3,)) or not np.all(np.isfinite(coordinates)):
        raise ValueError("Point coordinates must be a finite vector of length 2 or 3.")

# -------------------------------------------------------------------------------- #
def is_refinement_parameters(size: float, distance: float, transition: float) -> None:
    """Require positive size/transition and nonnegative distance."""
    from numbers import Real

    for name, value in (("size", size), ("distance", distance), ("transition", transition)):
        if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value):
            raise ValueError(f"{name} must be a finite real number.")
        if value < 0 or (name != "distance" and value == 0):
            raise ValueError(f"{name} must be {'nonnegative' if name == 'distance' else 'positive'}.")
