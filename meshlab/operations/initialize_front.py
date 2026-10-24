# -------------------------------------------------------------------------------- #
import numpy as np

from collections.abc import Sequence

from meshlab.core.mesh import Mesh
from meshlab.core.front import Front

# -------------------------------------------------------------------------------- #
def initialize_front(
        mesh: Mesh,
        front: Front,
        curves: Sequence[str],
        guides: Sequence[str] = (),
    ) -> None:
    """Initialize a front from named boundaries already inserted in a mesh.

    Parameters
    ----------
    mesh : Mesh
        Mesh containing boundary vertex indices.
    front : Front
        Front whose edge connectivity is replaced using front.int_dtype.
    curves : sequence of str
        Boundary names in traversal order. Consecutive indices in each
        boundary define an edge; no additional connecting edges are created.

    guides : sequence of str, default=()
        Names of straight inlet/outlet boundaries sharing front endpoints.
        Their ordered indices must describe a nonzero straight segment.

    Notes
    -----
    No input checks are performed. The caller supplies existing names, a
    suitable traversal and indices representable by front.int_dtype.
    No vertices or cells are inserted. Connectivity is independent of the
    boundary arrays. An empty selection produces an empty (0, 2) array.
    The guides entry in front.constraints is reset from the selected guides.
    Other constraints remain unchanged. Guide association uses shared indices,
    not coordinate proximity. Guides constrain advance_front, not normals.
    """
    # ------------------------------------------------------------------------ #
    # Collect oriented edges in the supplied curve order
    edges = []
    for name in curves:
        indices = mesh.boundaries[name]
        edges.extend(zip(indices[:-1], indices[1:]))

    # ------------------------------------------------------------------------ #
    # Replace connectivity without changing the mesh or boundary arrays
    front.entities.edge = np.asarray(edges, dtype=front.int_dtype).reshape(-1, 2)

    # ------------------------------------------------------------------------ #
    # Associate open endpoints with the selected straight guides
    indices, degree = np.unique(front.entities.edge, return_counts=True)
    endpoints = indices[degree == 1]
    front.constraints["guides"] = {
        int(index): name
        for name in guides
        for index in np.intersect1d(endpoints, mesh.boundaries[name])
    }

    # ------------------------------------------------------------------------ #
    return None

# -------------------------------------------------------------------------------- #
