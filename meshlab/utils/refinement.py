# -------------------------------------------------------------------------------- #
import numpy as np

from collections.abc import Callable
from scipy.interpolate import interp1d

# -------------------------------------------------------------------------------- #
def _arc_parameter(points):
    """Return normalized cumulative polyline length."""
    distance = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(points, axis=0), axis=1))]
    return distance / distance[-1]

# -------------------------------------------------------------------------------- #
def monitor_start(points: np.ndarray, strength: float = 5.0,
                  width: float = 0.1) -> np.ndarray:
    """Return one positive density per point, concentrated at the start.

    Uses ``1 + strength * exp(-s / width)``, where s is normalized arc
    length. strength must be nonnegative and width positive. Points form
    a nonzero 2D/3D polyline without consecutive duplicate coordinates.
    """
    # ------------------------------------------------------------------------ #
    s = _arc_parameter(np.asarray(points, dtype=float))
    return 1.0 + strength * np.exp(-s / width)

# -------------------------------------------------------------------------------- #
def monitor_end(points: np.ndarray, strength: float = 5.0,
                width: float = 0.1) -> np.ndarray:
    """Return one positive density per point, concentrated at the end.

    Uses ``1 + strength * exp(-(1-s) / width)``. Parameters and geometric
    preconditions are the same as monitor_start; inputs are not modified.
    """
    # ------------------------------------------------------------------------ #
    s = _arc_parameter(np.asarray(points, dtype=float))
    return 1.0 + strength * np.exp(-(1.0 - s) / width)

# -------------------------------------------------------------------------------- #
def monitor_curvature(points: np.ndarray, strength: float = 5.0) -> np.ndarray:
    """Return density from normalized unsigned discrete curvature.

    Turning angle divided by mean incident edge length estimates curvature.
    Open endpoints inherit their nearest interior estimate. Explicitly
    closed curves use periodic neighbors and repeat the first weight.
    Straight curves return ones; otherwise density is ``1 + strength*k/max(k)``.
    strength must be nonnegative. Points follow the monitor_start contract.
    Corners are treated as turning angles, not as smooth analytic curvature.
    """
    # ------------------------------------------------------------------------ #
    # Compute unit edge tangents and their unsigned turning angles
    points = np.asarray(points, dtype=float)
    closed = np.array_equal(points[0], points[-1])
    edges = np.diff(points, axis=0)
    lengths = np.linalg.norm(edges, axis=1)
    tangents = edges / lengths[:, None]
    if closed:
        incoming, outgoing = np.roll(tangents, 1, axis=0), tangents
        spacing = (np.roll(lengths, 1) + lengths) / 2.0
    elif len(points) > 2:
        incoming, outgoing = tangents[:-1], tangents[1:]
        spacing = (lengths[:-1] + lengths[1:]) / 2.0
    else:
        return np.ones(len(points))
    angle = 2.0 * np.arctan2(np.linalg.norm(outgoing - incoming, axis=1),
                            np.linalg.norm(outgoing + incoming, axis=1))
    curvature = angle / spacing
    if closed:
        curvature = np.r_[curvature, curvature[0]]
    else:
        curvature = np.r_[curvature[0], curvature, curvature[-1]]

    # ------------------------------------------------------------------------ #
    # Avoid amplifying roundoff on straight polylines
    maximum = curvature.max()
    if maximum * lengths.sum() <= 64 * np.finfo(float).eps:
        return np.ones(len(points))
    return 1.0 + strength * curvature / maximum

# -------------------------------------------------------------------------------- #
def monitor_corners(points: np.ndarray, strength: float = 10.0,
                    min_angle: float = np.pi / 6) -> np.ndarray:
    """Return density from turning angles above an angular threshold.

    Points follow the monitor_start contract, in 2D or 3D. min_angle is in
    radians, with 0 <= min_angle < pi; strength must be nonnegative.
    Straight edges have zero turning angle. Density is
    ``1 + strength * clip((angle-min_angle)/(pi-min_angle), 0, 1)``.
    Open endpoints receive unit weights. Explicitly closed curves use
    periodic neighbors and repeat the first weight at the closing point.
    Unlike monitor_curvature, angles are not divided by local edge lengths.
    Inputs are not modified. This monitor concentrates samples near corners
    but does not guarantee that their original vertices remain in the output.
    """
    # ------------------------------------------------------------------------ #
    # Measure turning angles between consistently oriented unit tangents
    points = np.asarray(points, dtype=float)
    edges = np.diff(points, axis=0)
    tangents = edges / np.linalg.norm(edges, axis=1)[:, None]
    closed = np.array_equal(points[0], points[-1])
    if closed:
        incoming, outgoing = np.roll(tangents, 1, axis=0), tangents
    else:
        incoming, outgoing = tangents[:-1], tangents[1:]
    angle = 2.0 * np.arctan2(np.linalg.norm(outgoing - incoming, axis=1),
                            np.linalg.norm(outgoing + incoming, axis=1))

    # ------------------------------------------------------------------------ #
    # Threshold angles and restore one weight per input point
    weights = 1.0 + strength * np.clip((angle - min_angle) / (np.pi - min_angle), 0, 1)
    if closed:
        return np.r_[weights, weights[0]]
    return np.r_[1.0, weights, 1.0]

# -------------------------------------------------------------------------------- #
def redistribute_points(
        points: np.ndarray,
        num_points: int,
        monitor: Callable[[np.ndarray], np.ndarray] | None = None,
        steps: int = 0,
        kind: str = "cubic",
    ) -> np.ndarray:
    """Redistribute a polyline by equidistributing a sampled density monitor.

    Parameters
    ----------
    points : array_like, shape (N, 2) or (N, 3)
        Ordered finite coordinates, at least two, without consecutive
        duplicates. Closed curves repeat their first point at the end.
        Inputs are not modified. Corners to retain must delimit separate curves.
    num_points : int
        Output count, at least two (four for a closed curve), including both
        endpoints and the repeated closing point when present.
    monitor : callable or None
        Receives the original coordinate samples as a floating-point copy;
        returns a finite, strictly positive array of shape (N,). None means
        uniform arc spacing. Functions can be combined by weighted sums.
        Input sampling must resolve narrow peaks in custom monitors.
    steps : int, default=0
        Nonnegative number of simultaneous smoothing passes on the weights.
        Each pass blends one half of the current weight with one quarter
        of each neighbor. Open endpoints stay fixed; closed curves are periodic.

    Returns
    -------
    numpy.ndarray
        New coordinates, with exact input endpoints. float32/float64 input
        precision is preserved; other inputs produce float64 coordinates.

    Notes
    -----
    Integrates the piecewise-linear monitor by trapezoids and analytically
    inverts its cumulative integral in each interval. Geometry uses linear
    interpolation in normalized polyline arc length. Sampling and smoothing
    do not change the input geometry, but reconnecting samples across omitted
    corners can cut those corners. No explicit argument validation is performed.
    """
    # ------------------------------------------------------------------------ #
    # Sample the monitor without exposing the caller's coordinate buffer
    original = np.asarray(points)
    dtype = original.dtype
    points = np.array(original, dtype=float, copy=True)
    s = _arc_parameter(points)
    closed = np.array_equal(points[0], points[-1])
    weights = np.ones(len(points)) if monitor is None else np.array(monitor(points.copy()), dtype=float, copy=True)

    # ------------------------------------------------------------------------ #
    # Smooth densities; periodic endpoints represent the same physical point
    if closed:
        weights[0] = weights[-1] = (weights[0] + weights[-1]) / 2.0
    for _ in range(steps):
        if closed:
            unique = weights[:-1]
            unique = 0.5 * unique + 0.25 * (np.roll(unique, 1) + np.roll(unique, -1))
            weights = np.r_[unique, unique[0]]
        else:
            weights[1:-1] = 0.5 * weights[1:-1] + 0.25 * (weights[:-2] + weights[2:])

    # ------------------------------------------------------------------------ #
    # Integrate density and invert each linear-density interval exactly
    weights /= weights.max()
    ds = np.diff(s)
    cumulative = np.r_[0.0, np.cumsum(ds * (weights[:-1] + weights[1:]) / 2.0)]
    targets = np.linspace(0.0, cumulative[-1], num_points)
    indices = np.clip(np.searchsorted(cumulative, targets, side="right") - 1,
                      0, len(s) - 2)
    area = targets - cumulative[indices]
    slope = np.diff(weights)[indices] / ds[indices]
    left = weights[indices]
    offset = 2.0 * area / (left + np.sqrt(np.maximum(0.0, left**2 + 2.0*slope*area)))
    parameters = s[indices] + np.clip(offset, 0.0, ds[indices])

    # ------------------------------------------------------------------------ #
    # Interpolate every coordinate and preserve exact endpoints
    result = np.column_stack([interp1d(s, coordinate, kind=kind)(parameters) for coordinate in points.T])
    result = result.astype(dtype)
    result[0], result[-1] = original[0], original[-1]
    return result

# -------------------------------------------------------------------------------- #
