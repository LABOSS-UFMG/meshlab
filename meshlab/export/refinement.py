# -------------------------------------------------------------------------------- #
import numpy as np

from meshlab.core import Point, Contour

# -------------------------------------------------------------------------------- #
def build_size_callback(refinements, base_minimum, base_maximum):
    """Compile geometry snapshots into a Gmsh mesh-size callback.

    No geometry entities are added to Gmsh. Distances are exact for the supplied
    polylines. Polygon interiors use ray-crossing parity, supporting simple
    concave contours independently of orientation. Boundary layers are not
    remeshed. Coordinates are planar, in the same frame as the original mesh.
    """
    # ------------------------------------------------------------------------ #
    # Prepare segment arrays once, outside Gmsh's repeated size evaluations
    regions = []
    for refinement in refinements:
        geometry = refinement.geometry
        if isinstance(geometry, Point):
            points = geometry.coordinates.copy()[None, :]
            starts, vectors = points, np.zeros_like(points)
            polygon = False
        else:
            polygon = isinstance(geometry, Contour)
            if polygon:
                points = np.concatenate([curve.points[:-1] for curve in geometry.curves])
                starts = points.copy()
                vectors = np.roll(points, -1, axis=0) - points
            else:
                starts = geometry.points[:-1].copy()
                vectors = geometry.points[1:] - starts
        lengths2 = np.sum(vectors * vectors, axis=1)
        regions.append((starts, vectors, lengths2, polygon,
                        refinement.size, refinement.distance, refinement.transition))

    # ------------------------------------------------------------------------ #
    # Reduce the existing size only within the requested influence regions
    def size_callback(dim, tag, x, y, z, lc):
        point = np.array([x, y])
        base = np.clip(lc, base_minimum, base_maximum)
        result = base
        for starts, vectors, lengths2, polygon, size, distance, transition in regions:
            delta = point - starts
            parameter = np.divide(np.sum(delta * vectors, axis=1), lengths2,
                                  out=np.zeros_like(lengths2), where=lengths2 > 0)
            closest = starts + np.clip(parameter, 0, 1)[:, None] * vectors
            d = np.min(np.linalg.norm(point - closest, axis=1))
            if polygon:
                ends = starts + vectors
                crossing = (starts[:, 1] > y) != (ends[:, 1] > y)
                selected = np.flatnonzero(crossing)
                intersection = (starts[selected, 0] + (y - starts[selected, 1])
                                * vectors[selected, 0] / vectors[selected, 1])
                if np.count_nonzero(x < intersection) % 2:
                    d = 0.0
            t = np.clip((d - distance) / transition, 0.0, 1.0)
            weight = t * t * (3.0 - 2.0 * t)
            fine = min(size, base)
            result = min(result, fine + (base - fine) * weight)
        return float(result)

    return size_callback

# -------------------------------------------------------------------------------- #
