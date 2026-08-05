# -------------------------------------------------------------------------------- #
from typing import Any
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