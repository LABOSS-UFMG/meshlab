# -------------------------------------------------------------------------------- #
import numpy as np

# -------------------------------------------------------------------------------- #
def crop_airfoil(points, xmin, xmax, max_spacing=0.01):
    """Clip a counter-clockwise airfoil polygon to an x interval and close it.

    Intersections with the two cut planes are interpolated on the original
    edges. Straight segments close the cuts. Resample by polygonal arc length
    between corners turning more than 30 degrees, retaining those corners.
    Spacing along each span does not exceed max_spacing. Input points
    describe a simple polygon without a repeated closing point. Returns an
    independent closed array; the input is not modified.
    """
    polygon = np.asarray(points).copy()
    for cut, sign in ((xmin, 1), (xmax, -1)):
        clipped = []
        for start, end in zip(polygon, np.roll(polygon, -1, axis=0)):
            inside_start = sign * (start[0] - cut) >= 0
            inside_end = sign * (end[0] - cut) >= 0
            if inside_start != inside_end:
                fraction = (cut - start[0]) / (end[0] - start[0])
                clipped.append(start + fraction * (end - start))
            if inside_end:
                clipped.append(end)
        polygon = np.asarray(clipped)

    # Remove duplicate cut vertices before measuring tangents.
    length = np.linalg.norm(np.roll(polygon, -1, axis=0) - polygon, axis=1)
    polygon = polygon[length > 0]
    tangent = np.roll(polygon, -1, axis=0) - polygon
    tangent /= np.linalg.norm(tangent, axis=1)[:, None]
    turning = np.arccos(np.clip(np.sum(np.roll(tangent, 1, axis=0) * tangent, axis=1), -1, 1))
    corners = np.flatnonzero(turning > np.pi / 6)
    if not len(corners):
        corners = np.array([0])

    # Uniform arc-length spacing within each span keeps the cut corners exact.
    segments = []
    for i, start in enumerate(corners):
        end = corners[(i + 1) % len(corners)]
        if end <= start:
            end += len(polygon)
        span = polygon[np.arange(start, end + 1) % len(polygon)]
        distance = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(span, axis=0), axis=1))]
        count = max(1, int(np.ceil(distance[-1] / max_spacing)))
        samples = np.linspace(0.0, distance[-1], count, endpoint=False)
        segments.append(np.column_stack([np.interp(samples, distance, span[:, axis])
                                         for axis in range(2)]))
    result = np.vstack(segments)
    return np.vstack((result, result[0]))

# -------------------------------------------------------------------------------- #
