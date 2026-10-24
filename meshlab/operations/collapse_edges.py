# -------------------------------------------------------------------------------- #
from collections.abc import Sequence

import numpy as np

from meshlab.core import Mesh, Front

# -------------------------------------------------------------------------------- #
def _groups(edges):
    """Collect connected vertex groups in increasing minimum-index order."""
    neighbors = {}
    for a, b in edges:
        neighbors.setdefault(int(a), set()).add(int(b))
        neighbors.setdefault(int(b), set()).add(int(a))
    groups = []
    while neighbors:
        pending = [min(neighbors)]
        group = set()
        while pending:
            vertex = pending.pop()
            if vertex not in group:
                group.add(vertex)
                pending.extend(neighbors.pop(vertex, ()))
        groups.append(sorted(group))
    return groups

# -------------------------------------------------------------------------------- #
def collapse_edges(
        mesh: Mesh,
        front: Front,
        edges: Sequence[tuple[int, int]],
    ) -> np.ndarray:
    """Collapse connected groups of planar front edges to their centroids.

    Parameters
    ----------
    mesh : Mesh
        Planar mesh updated in place, including physical boundary indices.
    front : Front
        Front updated in place. Each component must be a simple open chain
        or closed loop. Physical boundary and guided vertices are protected.
    edges : sequence of (int, int)
        Directed edges of this front, expressed in ORIGINAL mesh indices.
        The caller supplies valid references. Empty input is a no-op.

    Returns
    -------
    ndarray
        Original-to-final vertex map, using mesh.int_dtype. Apply this map
        to other fronts and their guide keys before using them again.

    Notes
    -----
    Groups are processed by minimum original index, independent of input
    order. Each centroid uses distinct original vertices. A group is skipped
    as a whole if it touches a protected vertex, reduces a closed component
    below three vertices (an open one below two), or invalidates an affected
    surviving cell. Cells must remain strictly convex with their original
    orientation. Quads can become triangles; cells reduced below three
    vertices are removed, as in the legacy operation.

    Acceptance checks are geometric algorithm decisions, not input validation.
    Global overlaps, intersections with unrelated cells and collisions between
    fronts are not checked. This is a local planar coarsening operation, not
    a general topologically certified mesh simplifier. Cell indices can change.
    Reacquire array views and recompute normals after calling this function.
    """
    # ------------------------------------------------------------------------ #
    # Stage edits using original indices; compact storage only once at the end
    if mesh.dim != 2:
        raise NotImplementedError("Edge collapse is currently implemented only in 2D.")
    index_map = np.arange(mesh.num_vertices, dtype=mesh.int_dtype)
    if len(edges) == 0:
        return index_map
    points = mesh.points.copy()
    front_edges = front.entities.edge.copy()
    blocks = (mesh.cells.triangle, mesh.cells.quadrilateral)
    cells = [row.copy() for block in blocks for row in block.connectivity]
    protected = {int(i) for indices in mesh.boundaries.values() for i in indices}
    protected.update(front.constraints.get("guides", {}))
    components = _groups(front_edges)
    accepted = False

    for original in _groups(edges):
        if protected.intersection(original):
            continue
        members = np.asarray(original, dtype=mesh.int_dtype)
        representative = members[0]
        component = next(group for group in components if representative in group)
        component_edges = front_edges[np.isin(front_edges[:, 0], component)]
        vertices, counts = np.unique(component_edges, return_counts=True)
        minimum = 3 if np.all(counts == 2) else 2
        if len(vertices) - len(members) + 1 < minimum:
            continue
        midpoint = mesh.points[members].mean(axis=0)
        replacements = {}
        valid = True

        # -------------------------------------------------------------------- #
        # Accept or reject the entire group before changing staged geometry
        for i, old in enumerate(cells):
            if not np.any(np.isin(old, members)):
                continue
            replaced = np.where(np.isin(old, members), representative, old)
            reduced = replaced[replaced != np.roll(replaced, 1)]
            if len(np.unique(reduced)) != len(reduced):
                valid = False
                break
            if len(reduced) < 3:
                replacements[i] = np.empty(0, dtype=mesh.int_dtype)
                continue
            polygon = points[reduced].copy()
            polygon[reduced == representative] = midpoint
            polygon -= polygon[0]
            old_points = points[old] - points[old[0]]
            area = np.sum(old_points[:, 0] * np.roll(old_points[:, 1], -1)
                          - old_points[:, 1] * np.roll(old_points[:, 0], -1))
            directions = np.roll(polygon, -1, axis=0) - polygon
            following = np.roll(directions, -1, axis=0)
            cross = directions[:, 0] * following[:, 1] - directions[:, 1] * following[:, 0]
            tolerance = 64 * np.finfo(mesh.float_dtype).eps * np.max(np.ptp(polygon, axis=0)) ** 2
            if area == 0 or np.any(np.sign(area) * cross <= tolerance):
                valid = False
                break
            replacements[i] = reduced
        if not valid:
            continue

        # -------------------------------------------------------------------- #
        # Merge the group and remove the resulting zero-length front edges
        accepted = True
        points[representative] = midpoint
        index_map[members] = representative
        for i, replacement in replacements.items():
            cells[i] = replacement
        front_edges = np.where(np.isin(front_edges, members), representative, front_edges)
        front_edges = front_edges[front_edges[:, 0] != front_edges[:, 1]]

    # ------------------------------------------------------------------------ #
    # Compact coordinates and rebuild the fixed-width cell blocks
    if not accepted:
        return index_map
    retained = np.flatnonzero(index_map == np.arange(len(index_map)))
    compact = np.empty(len(index_map), dtype=mesh.int_dtype)
    compact[retained] = np.arange(len(retained), dtype=mesh.int_dtype)
    index_map = compact[index_map]
    mesh._points[:len(retained)] = points[retained]
    mesh._num_vertices = len(retained)
    for block in blocks:
        block._num_cells = 0
    for cell in cells:
        if len(cell):
            mesh.add_cell("triangle" if len(cell) == 3 else "quadrilateral", index_map[cell])
    for name, indices in mesh.boundaries.items():
        mesh.boundaries[name] = index_map[indices]
    front.entities.edge = index_map[front_edges].astype(front.int_dtype)
    if "guides" in front.constraints:
        front.constraints["guides"] = {
            int(index_map[index]): name for index, name in front.constraints["guides"].items()
        }

    # ------------------------------------------------------------------------ #
    return index_map

# -------------------------------------------------------------------------------- #
