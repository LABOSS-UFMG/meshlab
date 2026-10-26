import numpy as np

from numpy.typing import ArrayLike

def unit_vector(v: ArrayLike) -> np.ndarray:
    """Return a unit vector based on v"""
    v = np.asarray(v)
    return v / np.linalg.norm(v)