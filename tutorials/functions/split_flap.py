# -------------------------------------------------------------------------------- #
import numpy as np

# -------------------------------------------------------------------------------- #
def split_flap(points, cut_length, radius, spacing=0.002):
    """Split a CCW airfoil using a horizontal segment, quarter circle and ray.

    Input starts at the upper trailing-edge corner, without repeating the
    first point. The lower corner is the strongest turn among the remaining
    points in the aft 5% of the chord; closure subdivision points are omitted.
    This assumes a finite straight trailing-edge closure, as in the tutorial
    data. The cut starts at the midpoint of the two trailing-edge corners,
    travels left, turns down through 90 degrees, then intersects the lower
    surface vertically. Coordinates use the original horizontal chord frame.
    Return closed main/flap polygons and the shared cut before translation.
    The caller chooses a radius keeping the arc inside the original airfoil.
    """
    points = np.asarray(points)
    # Locate the lower corner rather than the last subdivision of the closure.
    tangents = np.roll(points, -1, axis=0) - points
    tangents /= np.linalg.norm(tangents, axis=1)[:, None]
    turns = np.arccos(np.clip(np.sum(np.roll(tangents, 1, axis=0) * tangents, axis=1), -1, 1))
    aft = np.flatnonzero(points[:, 0] > points[:, 0].max() - 0.05 * np.ptp(points[:, 0]))
    aft = aft[aft != 0]
    lower_corner = aft[np.argmax(turns[aft])]
    points = points[:lower_corner + 1]
    start = (points[0] + points[-1]) / 2
    tangent_point = start - [cut_length, 0.0]
    center = tangent_point - [0.0, radius]
    angles = np.linspace(np.pi / 2, np.pi,
                         max(2, int(np.ceil(np.pi * radius / (2 * spacing)))) + 1)
    arc = center + radius * np.column_stack((np.cos(angles), np.sin(angles)))
    arc[0] = tangent_point
    arc[-1] = center - [radius, 0.0]

    # First intersection below the arc endpoint along its downward tangent.
    intersections = []
    for i, (a, b) in enumerate(zip(points[:-1], points[1:])):
        if b[0] != a[0]:
            fraction = (arc[-1, 0] - a[0]) / (b[0] - a[0])
            if 0 <= fraction <= 1:
                hit = a + fraction * (b - a)
                if hit[1] < arc[-1, 1]:
                    intersections.append((hit[1], i, hit))
    _, index, end = max(intersections, key=lambda item: item[0])

    count = max(1, int(np.ceil(cut_length / spacing)))
    horizontal = np.linspace(start, tangent_point, count, endpoint=False)
    count = max(1, int(np.ceil(np.linalg.norm(end - arc[-1]) / spacing)))
    vertical = np.linspace(arc[-1], end, count + 1)
    cut = np.vstack((horizontal, arc[:-1], vertical))

    # Opposite cut traversals preserve the counter-clockwise body orientation.
    main = np.vstack((start, points[:index + 1], cut[::-1]))
    flap = np.vstack((cut, points[index + 1:], start))
    return main, flap, cut

# -------------------------------------------------------------------------------- #
