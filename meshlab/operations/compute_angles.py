# -------------------------------------------------------------------------------- #
import numpy as np

from meshlab.core.mesh import Mesh
from meshlab.core.front import Front

# -------------------------------------------------------------------------------- #
def compute_angles(
        mesh: Mesh,
        front: Front,
    ) -> np.ndarray:
    """Compute the smaller angle between incident edges of a planar front.

    Parameters
    ----------
    mesh : Mesh
        Two-dimensional mesh containing the front coordinates.
    front : Front
        Consistently oriented, nonbranching front with nonzero edges.

    Returns
    -------
    ndarray, shape (N,)
        Angles in [0, pi], in mesh.float_dtype and ascending unique vertex-index
        order, matching compute_normals and advance_front.

    Notes
    -----
    Preserves the unsigned arccos convention of the legacy implementation.
    Convex and reflex corners can have the same angle; a straight vertex has
    angle pi. These are not oriented exterior or fluid-side angles.
    Open endpoints receive pi by convention, so their angle-only height
    correction is neutral. This is not a measured corner angle.
    No input checks are performed.
    """
    # ------------------------------------------------------------------------ #
    # Identify vertices and normalized oriented edges
    indices, inverse = np.unique(front.entities.edge, return_inverse=True)
    edges = inverse.reshape(-1, 2)
    points = mesh.points[indices]
    vectors = points[edges[:, 1]] - points[edges[:, 0]]
    vectors /= np.linalg.norm(vectors, axis=1)[:, None]

    # ------------------------------------------------------------------------ #
    # Collect vectors pointing from each vertex to its two neighbors
    previous = np.zeros_like(points)
    following = np.zeros_like(points)
    previous[edges[:, 1]] = -vectors
    following[edges[:, 0]] = vectors

    # ------------------------------------------------------------------------ #
    # Clip roundoff before evaluating the unsigned angle
    dot = np.sum(previous * following, axis=1)
    angles = np.arccos(np.clip(dot, -1.0, 1.0))
    degree = np.bincount(edges.ravel(), minlength=len(indices))
    angles[degree == 1] = np.pi

    # ------------------------------------------------------------------------ #
    return angles

# -------------------------------------------------------------------------------- #
