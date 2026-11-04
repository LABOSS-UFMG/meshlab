# -------------------------------------------------------------------------------- #
import numpy as np
import gmsh

# -------------------------------------------------------------------------------- #
def collect_cells(mesh) -> list[np.ndarray]:
    """Copy valid planar cells without changing the caller's mesh."""
    return [cell.copy() for block in (mesh.cells.triangle, mesh.cells.quadrilateral)
            for cell in block.connectivity]

# -------------------------------------------------------------------------------- #
def boundary_edges(cells) -> dict[tuple[int, int], tuple[int, int]]:
    """Return singly incident cell edges, keyed without orientation."""
    edges = {}
    counts = {}
    for cell in cells:
        for a, b in zip(cell, np.roll(cell, -1)):
            key = tuple(sorted((int(a), int(b))))
            edges[key] = (int(a), int(b))
            counts[key] = counts.get(key, 0) + 1
    return {key: edge for key, edge in edges.items() if counts[key] == 1}

# -------------------------------------------------------------------------------- #
def import_surfaces(points, cells) -> list[int]:
    """Import connected planar cell components as discrete Gmsh surfaces.

    Coordinates have three columns. Element and node tags are global; only
    valid triangles and quadrilaterals are imported. Components are assembled
    by shared vertices, matching the previous exporter's partitioning.
    """
    # ------------------------------------------------------------------------ #
    # Partition cells by shared vertices
    parent = list(range(len(cells)))
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    owners = {}
    for i, cell in enumerate(cells):
        for vertex in cell:
            if int(vertex) in owners:
                parent[find(i)] = find(owners[int(vertex)])
            else:
                owners[int(vertex)] = i
    groups = {}
    for i in range(len(cells)):
        groups.setdefault(find(i), []).append(i)

    # ------------------------------------------------------------------------ #
    # Preserve node identities and import both element types
    surfaces = []
    for group in groups.values():
        surface = gmsh.model.addDiscreteEntity(2)
        vertices = np.unique(np.concatenate([cells[i] for i in group]))
        gmsh.model.mesh.addNodes(2, surface, vertices + 1, points[vertices].ravel())
        for width, element_type in [(3, 2), (4, 3)]:
            selected = [i for i in group if len(cells[i]) == width]
            if selected:
                gmsh.model.mesh.addElementsByType(
                    surface, element_type, np.asarray(selected) + 1,
                    np.asarray([cells[i] for i in selected]).ravel() + 1,
                )
        surfaces.append(surface)
    gmsh.model.mesh.createTopology()
    gmsh.model.geo.synchronize()
    return surfaces

# -------------------------------------------------------------------------------- #
