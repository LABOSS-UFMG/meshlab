# -------------------------------------------------------------------------------- #
import numpy as np

from meshlab.core.mesh import Mesh
from meshlab.core.front import Front

# -------------------------------------------------------------------------------- #
def compute_angles(
        mesh: Mesh,
        front: Front,
    ) -> np.ndarray:
    """Compute the sector angle on the right of an oriented planar front.

    Parameters
    ----------
    mesh : Mesh
        Two-dimensional mesh containing the front coordinates.
    front : Front
        Consistently oriented, nonbranching front with nonzero edges.

    Returns
    -------
    ndarray, shape (N,)
        Angles in [0, 2*pi), in mesh.float_dtype and ascending unique vertex-index
        order, matching compute_normals and advance_front.

    Notes
    -----
    A left turn has a right-side angle above pi, a right turn below pi.
    A straight vertex has angle pi; coincident neighbor rays give zero.
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
    # Measure counterclockwise from the ray to the previous vertex to the next ray
    dot = np.sum(previous * following, axis=1)
    cross = previous[:, 0] * following[:, 1] - previous[:, 1] * following[:, 0]
    angles = np.arctan2(cross, dot) % (2 * np.pi)
    degree = np.bincount(edges.ravel(), minlength=len(indices))
    angles[degree == 1] = np.pi

    # ------------------------------------------------------------------------ #
    return angles

# -------------------------------------------------------------------------------- #
