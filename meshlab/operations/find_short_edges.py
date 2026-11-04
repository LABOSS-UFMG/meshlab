# -------------------------------------------------------------------------------- #
import numpy as np

from meshlab.core import Mesh, Front

# -------------------------------------------------------------------------------- #
def find_short_edges(
        mesh: Mesh,
        front: Front,
        min_length: float,
    ) -> list[tuple[int, int]]:
    """Return directed front edges shorter than min_length, shortest first.

    The caller supplies a finite nonnegative threshold. Connectivity comes
    directly from front.entities.edge, including explicit closing edges.
    Open fronts are supported. Equal lengths retain array order. Neither
    input is modified; neighboring candidates may share vertices.
    """
    # ------------------------------------------------------------------------ #
    # Measure explicit edges and preserve traversal order for equal lengths
    edges = front.entities.edge
    lengths = np.linalg.norm(mesh.points[edges[:, 1]] - mesh.points[edges[:, 0]], axis=1)
    selected = np.flatnonzero(lengths < min_length)
    selected = selected[np.argsort(lengths[selected], kind="stable")]

    # ------------------------------------------------------------------------ #
    return [tuple(map(int, edge)) for edge in edges[selected]]

# -------------------------------------------------------------------------------- #
