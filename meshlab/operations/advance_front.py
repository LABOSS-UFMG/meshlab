# -------------------------------------------------------------------------------- #
import numpy as np

from meshlab.core.mesh import Mesh
from meshlab.core.front import Front

# -------------------------------------------------------------------------------- #
def advance_front(
        mesh: Mesh,
        front: Front,
        normals: np.ndarray,
        height: float | np.ndarray,
    ) -> None:
    """Create one quadrilateral layer and update the supplied planar front.

    Parameters
    ----------
    mesh : Mesh
        Two-dimensional mesh receiving new vertices and quadrilaterals.
    front : Front
        Oriented front updated in place after inserting the layer.
    normals : ndarray, shape (N, 2)
        Unit directions ordered by np.unique(front.entities.edge), as returned
        by compute_normals. Recompute them after each advance.
    height : float | ndarray, shape (N,)
        Positive layer thickness, uniform or per vertex in the same order.

    Notes
    -----
    Each distinct front vertex produces one new vertex; each edge produces
    one quadrilateral. Connectivity is counterclockwise for right-hand
    advancement with positive heights. Wall boundary indices remain unchanged.
    The caller supplies compatible, representable indices and valid geometry.
    Endpoint guides registered by initialize_front must be straight nonzero
    segments. Proposed endpoints are projected onto their supporting lines;
    the caller ensures the projected positions stay inside those segments
    and do not meet another front or an existing guide vertex. New guide vertices are inserted in boundary
    traversal order. Projection can change the effective step length.
    No input checks, quality checks or collision detection are performed. This operation does not generate volumetric 3D layers.
    """
    # ------------------------------------------------------------------------ #
    # Compute all new coordinates before resizing mesh storage
    indices, inverse = np.unique(front.entities.edge, return_inverse=True)
    points = mesh.points[indices] + np.asarray(height, dtype=mesh.float_dtype)[..., None] * normals

    # ------------------------------------------------------------------------ #
    # Project constrained endpoints onto their straight boundary guides
    guides = front.constraints.get("guides", {})
    for index, name in guides.items():
        boundary = mesh.points[mesh.boundaries[name]]
        origin = boundary[0]
        tangent = boundary[-1] - origin
        position = np.searchsorted(indices, index)
        parameter = np.dot(points[position] - origin, tangent) / np.dot(tangent, tangent)
        points[position] = origin + parameter * tangent

    # ------------------------------------------------------------------------ #
    # Insert one vertex per unique front vertex
    new_indices = np.empty(len(indices), dtype=front.int_dtype)
    for i, point in enumerate(points):
        new_indices[i] = mesh.add_vertex(point)
    new_edges = new_indices[inverse].reshape(-1, 2)

    # ------------------------------------------------------------------------ #
    # Insert quadrilaterals on the right side of the oriented edges
    for (start, end), (new_start, new_end) in zip(front.entities.edge, new_edges):
        mesh.add_cell("quadrilateral", [start, new_start, new_end, end])

    # ------------------------------------------------------------------------ #
    # Insert guide nodes into physical boundaries and update endpoint references
    updated_guides = {}
    for index, name in guides.items():
        new_index = new_indices[np.searchsorted(indices, index)]
        existing = mesh.boundaries[name]
        tangent = mesh.points[existing[-1]] - mesh.points[existing[0]]
        boundary_indices = np.append(existing, new_index).astype(mesh.int_dtype)
        boundary = mesh.points[boundary_indices]
        order = np.argsort((boundary - boundary[0]) @ tangent, kind="stable")
        mesh.boundaries[name] = boundary_indices[order]
        updated_guides[int(new_index)] = name
    if guides:
        front.constraints["guides"] = updated_guides

    # ------------------------------------------------------------------------ #
    # Replace moving connectivity while preserving the wall boundaries
    front.entities.edge = new_edges

    # ------------------------------------------------------------------------ #
    return None

# -------------------------------------------------------------------------------- #
