# -------------------------------------------------------------------------------- #
import numpy as np

from meshlab.core import Curve

# -------------------------------------------------------------------------------- #
def _cross(a, b):
    """Signed planar cross product, including vectorized inputs."""
    return a[..., 0] * b[..., 1] - a[..., 1] * b[..., 0]

# -------------------------------------------------------------------------------- #
def _check_cut(polygon, cut, tolerance):
    """Reject polygonal cuts touching the boundary except at their endpoints."""
    starts = polygon
    ends = np.roll(polygon, -1, axis=0)
    boundary_vectors = ends - starts
    for i, (a, b) in enumerate(zip(cut[:-1], cut[1:])):
        vector = b - a
        delta = starts - a
        denominator = _cross(vector, boundary_vectors)
        scale = np.linalg.norm(vector) * np.linalg.norm(boundary_vectors, axis=1)
        parallel = np.abs(denominator) <= tolerance * scale
        active = ~parallel
        t = np.zeros(len(polygon))
        u = np.zeros(len(polygon))
        t[active] = _cross(delta[active], boundary_vectors[active]) / denominator[active]
        u[active] = _cross(delta[active], vector) / denominator[active]
        hits = active & (t >= -tolerance) & (t <= 1 + tolerance) & (u >= -tolerance) & (u <= 1 + tolerance)
        allowed = ((i == 0) & (np.abs(t) <= tolerance)) | ((i == len(cut) - 2) & (np.abs(t - 1) <= tolerance))
        if np.any(hits & ~allowed):
            raise ValueError("The cut intersects the contour away from its endpoints.")
        # A cut overlapping the boundary does not split the polygon interior.
        collinear = parallel & (np.abs(_cross(delta, vector)) <= tolerance * np.linalg.norm(vector))
        projection_a = delta @ vector / np.dot(vector, vector)
        projection_b = (ends - a) @ vector / np.dot(vector, vector)
        overlap = np.minimum(1, np.maximum(projection_a, projection_b)) - np.maximum(0, np.minimum(projection_a, projection_b))
        if np.any(collinear & (overlap > tolerance)):
            raise ValueError("The cut overlaps a contour edge.")

        # With boundary crossings excluded, each segment must lie inside.
        x, y = (a + b) / 2
        crossing = (starts[:, 1] > y) != (ends[:, 1] > y)
        intersection = (starts[crossing, 0] + (y - starts[crossing, 1])
                        * boundary_vectors[crossing, 0] / boundary_vectors[crossing, 1])
        if np.count_nonzero(x < intersection) % 2 == 0:
            raise ValueError("The cut must stay inside the contour.")

# -------------------------------------------------------------------------------- #
def split_curve(
        curve: Curve,
        start_index: int,
        end_index: int,
        start_direction,
        end_direction,
        radius: float,
    ) -> tuple[Curve, Curve]:
    """Split a closed planar curve by two rays joined by a circular fillet.

    Both directions point INWARD from their respective surface nodes, and
    need not be unit vectors. Their supporting lines must intersect ahead
    of both nodes. Select the minor arc rounding that intersection inside
    the two rays; parallel rays and radii extending past either node are
    rejected. The end direction is opposite to the final cut traversal.

    The caller supplies a simple, explicitly closed 2D curve, two distinct
    indices in points[:-1], nonzero finite directions and a positive radius.
    Original surface vertices are preserved. Cut spacing uses the mean of
    the four incident edge lengths, with arc steps capped at 10 degrees.
    Tangency is exact for the analytic circle; its stored representation
    is a polyline. Boundary/interior checks concern that stored polyline.

    Return independently stored closed curves named '<name>_1' and
    '<name>_2', with the input orientation and dtype. The first follows
    the original surface from start_index to end_index, then the reversed
    cut; the second follows the complementary surface and the forward cut.
    Input geometry is not modified. No mesh or front is involved.
    """
    # ------------------------------------------------------------------------ #
    # Work locally in float64 and normalize coordinates for geometric decisions
    polygon = curve.points[:-1].astype(np.float64)
    origin = polygon[start_index].copy()
    scale = np.max(np.ptp(polygon, axis=0))
    polygon = (polygon - origin) / scale
    a, b = polygon[[start_index, end_index]]
    u = np.asarray(start_direction, dtype=float)
    v = np.asarray(end_direction, dtype=float)
    u = u / np.linalg.norm(u)
    v = v / np.linalg.norm(v)
    r = radius / scale
    tolerance = 128 * np.finfo(float).eps

    # ------------------------------------------------------------------------ #
    # Intersect inward rays and trim equal distances to their tangent points
    denominator = _cross(u, v)
    if abs(denominator) <= tolerance:
        raise ValueError("Parallel directions do not define a unique circular fillet.")
    s = _cross(b - a, v) / denominator
    t = _cross(b - a, u) / denominator
    angle = np.arccos(np.clip(np.dot(u, v), -1, 1))
    trim = r / np.tan(angle / 2)
    if min(s, t) <= trim + tolerance:
        raise ValueError("The radius does not fit between the surface nodes and the ray intersection.")
    intersection = a + s * u
    first = a + (s - trim) * u
    last = b + (t - trim) * v
    bisector = (u + v) / np.linalg.norm(u + v)
    center = intersection - bisector * r / np.sin(angle / 2)

    # ------------------------------------------------------------------------ #
    # Use local surface spacing and explicitly retain the tangent points
    lengths = []
    for index in (start_index, end_index):
        lengths.extend((np.linalg.norm(polygon[index] - polygon[index - 1]),
                        np.linalg.norm(polygon[(index + 1) % len(polygon)] - polygon[index])))
    spacing = np.mean(lengths)
    theta = np.arctan2(first[1] - center[1], first[0] - center[0])
    sweep = np.arctan2(_cross(first - center, last - center), np.dot(first - center, last - center))
    count = max(1, int(np.ceil(abs(sweep) * r / spacing)), int(np.ceil(abs(sweep) / (np.pi / 18))))
    angles = theta + np.linspace(0, sweep, count + 1)
    arc = center + r * np.column_stack((np.cos(angles), np.sin(angles)))
    arc[0], arc[-1] = first, last
    incoming = np.linspace(a, first, max(1, int(np.ceil((s - trim) / spacing))), endpoint=False)
    outgoing = np.linspace(last, b, max(1, int(np.ceil((t - trim) / spacing))) + 1)
    cut = np.vstack((incoming, arc[:-1], outgoing))
    _check_cut(polygon, cut, tolerance)

    # ------------------------------------------------------------------------ #
    # Reuse exact input coordinates on the surface and an identical shared cut
    cut = (cut * scale + origin).astype(curve.float_dtype)
    cut[0], cut[-1] = curve.points[[start_index, end_index]]
    count = len(polygon)
    first_indices = np.arange(start_index, start_index + (end_index - start_index) % count + 1) % count
    second_indices = np.arange(end_index, end_index + (start_index - end_index) % count + 1) % count
    first_points = np.vstack((curve.points[first_indices], cut[-2::-1]))
    second_points = np.vstack((curve.points[second_indices], cut[1:]))
    return (Curve(curve.name + "_1", first_points, float_dtype=curve.float_dtype),
            Curve(curve.name + "_2", second_points, float_dtype=curve.float_dtype))

# -------------------------------------------------------------------------------- #
