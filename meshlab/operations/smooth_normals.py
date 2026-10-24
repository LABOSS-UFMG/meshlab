# -------------------------------------------------------------------------------- #
import numpy as np

from meshlab.core.mesh import Mesh
from meshlab.core.front import Front

# -------------------------------------------------------------------------------- #
def smooth_normals(
        mesh: Mesh,
        front: Front,
        normals: np.ndarray,
        relaxation: float | np.ndarray = 0.5,
    ) -> tuple[np.ndarray, np.ndarray]:
    """Apply one simultaneous Laplacian smoothing step to planar unit normals.

    Parameters
    ----------
    mesh : Mesh
        Two-dimensional mesh defining the floating-point storage type.
    front : Front
        Nonbranching front whose edges determine the neighboring vertices.
    normals : ndarray, shape (N, 2)
        Unit normals in ascending unique front vertex-index order.
    relaxation : float | ndarray, shape (N,), default=0.5
        Weight in [0, 1], uniform or per vertex in the same order.

    Returns
    -------
    normals, rotation : tuple of ndarray
        New unit normals and signed rotation angles in mesh.float_dtype.
        Positive rotation is counterclockwise; input arrays remain unchanged.

    Notes
    -----
    Uses the mean of incident neighbors, not circular array positions.
    Open endpoints use their single neighbor; no guide or corner constraints
    are imposed. The caller ensures compatible inputs and nonzero weighted
    vectors. No input checks or geometry updates are performed.
    """
    # ------------------------------------------------------------------------ #
    # Accumulate neighbor normals through the edge connectivity
    indices, inverse = np.unique(front.entities.edge, return_inverse=True)
    edges = inverse.reshape(-1, 2)
    normals = np.asarray(normals, dtype=mesh.float_dtype)
    neighbors = np.zeros_like(normals)
    degree = np.zeros(len(indices), dtype=mesh.float_dtype)
    np.add.at(neighbors, edges[:, 0], normals[edges[:, 1]])
    np.add.at(neighbors, edges[:, 1], normals[edges[:, 0]])
    np.add.at(degree, edges.ravel(), 1)
    neighbors /= degree[:, None]

    # ------------------------------------------------------------------------ #
    # Blend simultaneously and normalize the resulting directions
    alpha = np.asarray(relaxation, dtype=mesh.float_dtype)[..., None]
    new_normals = (1.0 - alpha) * normals + alpha * neighbors
    new_normals /= np.linalg.norm(new_normals, axis=1)[:, None]

    # ------------------------------------------------------------------------ #
    # Compute signed rotation relative to the input directions
    cross = normals[:, 0] * new_normals[:, 1] - normals[:, 1] * new_normals[:, 0]
    dot = np.sum(normals * new_normals, axis=1)
    rotation = np.arctan2(cross, dot)

    # ------------------------------------------------------------------------ #
    return new_normals, rotation

# -------------------------------------------------------------------------------- #
