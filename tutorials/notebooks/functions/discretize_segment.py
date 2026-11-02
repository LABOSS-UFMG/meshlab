# -------------------------------------------------------------------------------- #
import numpy as np

from numpy.typing import ArrayLike
from scipy.optimize import brentq
from scipy.special import logsumexp

# -------------------------------------------------------------------------------- #
def discretize_segment(
        p_init: ArrayLike,
        p_end: ArrayLike,
        ds_init: float,
        ds_end: float | None = None,
    ) -> np.ndarray:
    """Sample a 2D/3D segment with uniform or geometric element lengths.

    Uniform spacing is adjusted to fit an integer number of elements.
    Geometric spacing preserves ds_init; ds_end is a target because the
    number of elements is rounded. Both endpoints are included exactly.
    """

    p_init = np.asarray(p_init, dtype=float)
    p_end = np.asarray(p_end, dtype=float)
    length = np.linalg.norm(p_end - p_init)
    
    if length <= 0 or ds_init <= 0 or (ds_end is not None and ds_end <= 0):
        raise ValueError("Segment length and element sizes must be positive.")

    if ds_end is None or np.isclose(ds_init, ds_end):
        count = max(1, round(length / ds_init))
        s = np.linspace(0.0, length, count + 1)
    else:
        if ds_init + ds_end > length:
            raise ValueError("The endpoint sizes must fit inside the segment.")
        log_ratio = np.log(ds_end / ds_init)

        def residual(count):
            step = log_ratio / (count - 1)
            return ds_init * np.expm1(count * step) / np.expm1(step) - length

        upper = max(10, 2 * length / min(ds_init, ds_end))
        count = max(2, round(brentq(residual, 2, upper)))

        # Solve in log-space to avoid overflow when fitting the geometric sum.
        indices = np.arange(count)
        bound = max(1.0, np.log(length / ds_init))
        log_q = brentq(
            lambda q: logsumexp(indices * q) - np.log(length / ds_init),
            -bound, bound,
        )
        s = np.r_[0.0, np.cumsum(ds_init * np.exp(indices * log_q))]

    points = p_init + (s / length)[:, None] * (p_end - p_init)
    points[0], points[-1] = p_init, p_end

    return points

# -------------------------------------------------------------------------------- #
