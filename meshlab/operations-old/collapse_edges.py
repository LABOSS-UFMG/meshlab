# -------------------------------------------------------------------------------- #
import numpy as np

from typing import Sequence

from meshlab.data.mesh import Mesh
from meshlab.data.contour import Contour

# -------------------------------------------------------------------------------- #
def collapse_edges(
        mesh: Mesh,
        front: Contour,
        edges: Sequence[tuple[int, int]],
    ) -> tuple[Contour, np.ndarray]:
    """
    Collapse each connected group of supplied edges to its vertex centroid.

    Parameters
    ----------
    mesh : Mesh
        Mesh to update using its vertex and cell mutation methods.
    front : Contour
        Closed front with at least three distinct vertex indices.
    edges : Sequence[tuple[int, int]]
        Directed edges of the input front, expressed in the ORIGINAL mesh
        indices. Edges sharing vertices form one group, including chains
        crossing the last-to-first edge. Input order does not affect the result.

    Returns
    -------
    Contour
        Updated front. The input contour is not modified.
    np.ndarray
        Original-to-final vertex index map. Use it to update other contours
        before reusing them with this mesh. Collapsed endpoints share an index.

    Notes
    -----
    Only supplied edges are considered; no lengths or thresholds are checked.
    Each group becomes one vertex at the arithmetic mean of its distinct
    ORIGINAL vertices. The group is accepted or skipped as a whole: no partial
    collapse occurs if it invalidates neighboring cells or leaves fewer than
    three front vertices. Groups are processed by their smallest original index.
    Quadrilaterals become triangles;
    triangles reduced to two vertices are removed. Affected cells are removed
    and reinserted, so cell indices may change. Unrelated cell overlaps are not
    checked. No Mesh storage arrays or counters are modified directly.
    """
    # ------------------------------------------------------------------------ #
    # Validate all edge references before modifying the mesh
    indices = front.indices[:front.num_indices].copy()
    if len(indices) < 3 or len(np.unique(indices)) != len(indices):
        raise ValueError("The front must contain at least three distinct vertices.")
    if np.any(indices < 0) or np.any(indices >= mesh.num_vertices):
        raise ValueError("The front contains an invalid vertex index.")
    if not np.all(np.isfinite(mesh.vertices[:mesh.num_vertices])):
        raise ValueError("Vertex coordinates must be finite.")
    original_edges = set(zip(indices, np.roll(indices, -1)))
    edges = [tuple(edge) for edge in edges]
    if any(edge not in original_edges for edge in edges):
        raise ValueError("Every supplied pair must be a directed edge of the input front.")
    index_map = np.arange(mesh.num_vertices, dtype=np.int32)

    # ------------------------------------------------------------------------ #
    # Connected components collect all neighboring edges before any mutation
    neighbors = {}
    for a, b in edges:
        neighbors.setdefault(a, set()).add(b)
        neighbors.setdefault(b, set()).add(a)
    groups = []
    while neighbors:
        pending = [min(neighbors)]
        group = set()
        while pending:
            vertex = pending.pop()
            if vertex not in group:
                group.add(vertex)
                pending.extend(neighbors.pop(vertex, ()))
        original = sorted(group)
        groups.append((original, mesh.vertices[original].mean(axis=0)))

    for original, midpoint in groups:
        members = np.sort(index_map[original])
        if len(indices) - len(members) + 1 < 3:
            continue
        a = int(members[0])
        removed = members[1:]
        affected = np.flatnonzero(np.any(
            np.isin(mesh.cells[:mesh.num_cells], members), axis=1,
        ))
        replacements = []
        valid = True

        # Validate the complete group before committing any of its collapses
        for cell_index in affected:
            cell = mesh.cells[cell_index]
            old = cell[cell >= 0]
            replaced = np.where(np.isin(old, members), a, old)
            reduced = replaced[replaced != np.roll(replaced, 1)]
            if len(np.unique(reduced)) != len(reduced):
                valid = False
                break
            if len(reduced) < 3:
                continue

            points = mesh.vertices[reduced].copy()
            points[reduced == a] = midpoint
            old_points = mesh.vertices[old] - mesh.vertices[old[0]]
            points -= points[0]
            old_area = np.sum(old_points[:, 0] * np.roll(old_points[:, 1], -1)
                              - old_points[:, 1] * np.roll(old_points[:, 0], -1))
            directions = np.roll(points, -1, axis=0) - points
            following = np.roll(directions, -1, axis=0)
            cross = directions[:, 0] * following[:, 1] - directions[:, 1] * following[:, 0]
            tolerance = 64 * np.finfo(float).eps * np.max(np.ptp(points, axis=0)) ** 2
            if old_area == 0 or np.any(np.sign(old_area) * cross <= tolerance):
                valid = False
                break
            replacements.append(reduced)

        if not valid:
            continue

        # -------------------------------------------------------------------- #
        # Detach cells first: remove_vertex would otherwise delete them itself
        for cell_index in reversed(affected):
            mesh.remove_cell(int(cell_index))
        mesh.replace_vertex(a, midpoint)
        indices = indices[~np.isin(indices, removed)]
        index_map[np.isin(index_map, members)] = a
        for b in reversed(removed):
            mesh.remove_vertex(int(b))
            for cell in replacements:
                cell[cell > b] -= 1
            indices[indices > b] -= 1
            index_map[index_map > b] -= 1
        for cell in replacements:
            # Write padding too: add_cell can reuse a previously occupied row.
            padded = np.full(mesh.cells_max_dim, -1, dtype=np.int32)
            padded[:len(cell)] = cell
            mesh.add_cell(padded)

    # ------------------------------------------------------------------------ #
    new_front = Contour(name=front.name, capacity=len(indices) + 1,
                        increase_ratio=front.increase_ratio)
    for index in indices:
        new_front.add_index(int(index))

    return new_front, index_map

# -------------------------------------------------------------------------------- #
