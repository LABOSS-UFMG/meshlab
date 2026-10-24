# -------------------------------------------------------------------------------- #
import numpy as np

from meshlab.core.mesh import Mesh
from meshlab.core.contour import Contour

# -------------------------------------------------------------------------------- #
def insert_contour(
        mesh: Mesh,
        contour: Contour,
    ) -> None:
    """Insert a closed contour and register its named boundaries.

    Parameters
    ----------
    mesh : Mesh
        Mesh receiving the vertices and boundary indices.
    contour : Contour
        Ordered curves with matching endpoints, including the closing junction.
        Each curve must have at least two points compatible with mesh.dim.

    Notes
    -----
    Curve names must be unique throughout the mesh; the caller ensures this.
    No input checks are performed. Existing names are overwritten.
    Shared endpoints use a single vertex, retaining the coordinates first
    inserted. The final endpoint references the first vertex of the contour.
    Separate insertions do not merge nearby vertices. No cells or fronts are
    created. A single closed curve must repeat its first point at the end.
    """
    # ------------------------------------------------------------------------ #
    # Insert the first vertex and initialize the shared junction
    first_index = mesh.add_vertex(contour.curves[0].points[0])
    previous_index = first_index

    # ------------------------------------------------------------------------ #
    # Insert curve interiors and share consecutive endpoints
    for position, curve in enumerate(contour.curves):
        indices = np.empty(len(curve.points), dtype=mesh.int_dtype)
        indices[0] = previous_index

        for i, point in enumerate(curve.points[1:-1], start=1):
            indices[i] = mesh.add_vertex(point)

        if position == len(contour.curves) - 1:
            indices[-1] = first_index
        else:
            indices[-1] = mesh.add_vertex(curve.points[-1])

        mesh.boundaries[curve.name] = indices
        previous_index = indices[-1]

    # ------------------------------------------------------------------------ #
    return None

# -------------------------------------------------------------------------------- #
