# -------------------------------------------------------------------------------- #
import numpy as np

from meshlab.core.mesh import Mesh
from meshlab.core.front import Front

# -------------------------------------------------------------------------------- #
def compute_normals(
        mesh: Mesh,
        front: Front,
        method: str = "central",
    ) -> np.ndarray:
    """Compute right-hand unit normals at the vertices of a planar front.

    Parameters
    ----------
    mesh : Mesh
        Two-dimensional mesh containing the front vertices.
    front : Front
        Consistently oriented edges of nonbranching curves.
    method : {"central", "bisector"}, default="central"
        Sum incident edge vectors for central tangents, or incident unit
        edge vectors for bisector tangents.

    Returns
    -------
    ndarray, shape (N, 2)
        Normals in mesh.float_dtype, ordered by np.unique(front.entities.edge).
        advance_front uses the same ascending vertex-index order.

    Notes
    -----
    The convention is tangent cross ez: (tx, ty) becomes (ty, -tx).
    Open endpoints use their single incident edge. No guide constraints are
    applied. The caller ensures dim=2, nonzero edges and nonzero vertex
    tangents. No input checks, smoothing or collision detection are performed.
    """
    # ------------------------------------------------------------------------ #
    # Identify unique vertices and local edge connectivity
    indices, inverse = np.unique(front.entities.edge, return_inverse=True)
    edges = inverse.reshape(-1, 2)
    points = mesh.points[indices]
    vectors = points[edges[:, 1]] - points[edges[:, 0]]

    # ------------------------------------------------------------------------ #
    # Weight incident edges according to the tangent method
    weights = {
        "central": lambda: np.ones(len(edges), dtype=mesh.float_dtype),
        "bisector": lambda: np.linalg.norm(vectors, axis=1),
    }[method]()
    vectors = vectors / weights[:, None]
    tangents = np.zeros((len(indices), 2), dtype=mesh.float_dtype)
    np.add.at(tangents, edges[:, 0], vectors)
    np.add.at(tangents, edges[:, 1], vectors)
    tangents /= np.linalg.norm(tangents, axis=1)[:, None]

    # ------------------------------------------------------------------------ #
    # Rotate tangents clockwise to obtain unit normals
    normals = np.empty_like(tangents)
    normals[:, 0] = tangents[:, 1]
    normals[:, 1] = -tangents[:, 0]

    # ------------------------------------------------------------------------ #
    return normals

# -------------------------------------------------------------------------------- #
