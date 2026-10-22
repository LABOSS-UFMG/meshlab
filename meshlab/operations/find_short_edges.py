# -------------------------------------------------------------------------------- #
import numpy as np

from meshlab.data.mesh import Mesh
from meshlab.data.contour import Contour

# -------------------------------------------------------------------------------- #
def find_short_edges(
        mesh: Mesh,
        front: Contour,
        min_length: float,
    ) -> list[tuple[int, int]]:
    """
    Find front edges strictly shorter than min_length, shortest first.

    Parameters
    ----------
    mesh : Mesh
        Mesh containing the vertex coordinates.
    front : Contour
        Closed front, including its last-to-first edge.
    min_length : float
        Finite, nonnegative length threshold.

    Returns
    -------
    list[tuple[int, int]]
        Directed pairs of mesh vertex indices, without modifying either input.
        Adjacent pairs may share vertices. Equal lengths retain traversal order.
    """
    # ------------------------------------------------------------------------ #
    if not np.isfinite(min_length) or min_length < 0:
        raise ValueError("min_length must be finite and nonnegative.")
    indices = front.indices[:front.num_indices].tolist()
    candidates = []
    for a, b in zip(indices, indices[1:] + indices[:1]):
        length = np.linalg.norm(mesh.vertices[a] - mesh.vertices[b])
        if length < min_length:
            candidates.append((length, (a, b)))

    return [edge for _, edge in sorted(candidates, key=lambda item: item[0])]

# -------------------------------------------------------------------------------- #
