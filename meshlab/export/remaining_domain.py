# -------------------------------------------------------------------------------- #
import gmsh
import numpy as np

from meshlab.export.boundary_layer import boundary_edges
from meshlab.export.refinement import build_size_callback

# -------------------------------------------------------------------------------- #
def _loops(edges):
    """Join undirected residual edges into closed polygonal loops."""
    adjacency = {}
    remaining = set(edges)
    for a, b in remaining:
        adjacency.setdefault(a, []).append(b)
        adjacency.setdefault(b, []).append(a)
    if any(len(neighbors) != 2 for neighbors in adjacency.values()):
        raise RuntimeError("Residual boundary must form closed, nonbranching loops.")
    loops = []
    while remaining:
        a, b = min(remaining)
        loop = [a]
        previous, current = a, b
        remaining.remove((a, b))
        while current != loop[0]:
            loop.append(current)
            following = next(v for v in adjacency[current] if v != previous)
            remaining.remove(tuple(sorted((current, following))))
            previous, current = current, following
        loops.append(np.asarray(loop, dtype=np.int64))
    return loops

# -------------------------------------------------------------------------------- #
def _inside(point, polygon):
    """Determine polygon containment by ray crossing (disjoint simple loops)."""
    x, y = point
    inside = False
    for a, b in zip(polygon, np.roll(polygon, -1, axis=0)):
        if (a[1] > y) != (b[1] > y):
            crossing = a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1])
            if x < crossing:
                inside = not inside
    return inside

# -------------------------------------------------------------------------------- #
def generate_remaining(mesh, cells, fronts=None, mesh_size=None, refinements=None):
    """Fill residual planar regions, preserving all interface segments.

    Physical boundaries must describe the complete fluid boundary. Subtract
    covered physical segments, then use layer interfaces (or supplied fronts)
    to form residual loops. Containment separates outer loops and holes.
    Boundary discretization is fixed; only residual interiors are meshed.
    Returns independent 2D points and cells including the original layers.
    """
    # ------------------------------------------------------------------------ #
    # Assemble residual interfaces and uncovered physical boundaries
    physical = {tuple(sorted((int(a), int(b))))
                for indices in mesh.boundaries.values()
                for a, b in zip(indices[:-1], indices[1:])}
    layer_boundary = set(boundary_edges(cells))
    interface = layer_boundary - physical
    if fronts is not None:
        supplied = {tuple(sorted((int(a), int(b))))
                    for front in fronts for a, b in front.entities.edge}
        if supplied != interface:
            raise RuntimeError("Supplied fronts do not match the exposed layer interfaces.")
    loops = _loops((physical - layer_boundary) | interface)
    points = mesh.points.astype(np.float64).copy()
    if not loops:
        return points, cells

    # ------------------------------------------------------------------------ #
    # Build separate curve loops and freeze every existing segment
    point_tags = {}
    loop_tags = []
    for loop in loops:
        lines = []
        for index in loop:
            if int(index) not in point_tags:
                x, y = points[index]
                point_tags[int(index)] = gmsh.model.geo.addPoint(x, y, 0.0)
        for a, b in zip(loop, np.roll(loop, -1)):
            line = gmsh.model.geo.addLine(point_tags[int(a)], point_tags[int(b)])
            lines.append(line)
            gmsh.model.geo.mesh.setTransfiniteCurve(line, 2)
        loop_tags.append(gmsh.model.geo.addCurveLoop(lines))
    contains = [[_inside(points[child[0]], points[parent]) if i != j else False
                 for j, parent in enumerate(loops)] for i, child in enumerate(loops)]
    depth = np.sum(contains, axis=1)
    for i, tag in enumerate(loop_tags):
        if depth[i] % 2 == 0:
            holes = [loop_tags[j] for j in range(len(loops))
                     if depth[j] == depth[i] + 1 and contains[j][i]]
            gmsh.model.geo.addPlaneSurface([tag] + holes)
    gmsh.model.geo.synchronize()
    if mesh_size is not None:
        gmsh.option.setNumber("Mesh.MeshSizeMax", mesh_size)
        gmsh.option.setNumber("Mesh.MeshSizeMin", mesh_size)
    # Apply local sizes only while filling the residual planar region
    if refinements:
        minimum = gmsh.option.getNumber("Mesh.MeshSizeMin")
        maximum = gmsh.option.getNumber("Mesh.MeshSizeMax")
        callback = build_size_callback(refinements, minimum, maximum)
        # Gmsh's Python wrapper holds one global callback reference across models.
        previous_callback = getattr(gmsh, "api_callback_", None)
        try:
            gmsh.option.setNumber("Mesh.MeshSizeMin",
                                  min(minimum, *(r.size for r in refinements)))
            gmsh.model.mesh.setSizeCallback(callback)
            gmsh.model.mesh.generate(2)
        finally:
            gmsh.model.mesh.removeSizeCallback()
            gmsh.option.setNumber("Mesh.MeshSizeMin", minimum)
            if previous_callback is not None:
                gmsh.api_callback_ = previous_callback
    else:
        gmsh.model.mesh.generate(2)

    # ------------------------------------------------------------------------ #
    # Map boundary nodes back to existing indices and append interior nodes
    mapping = {}
    for index, tag in point_tags.items():
        nodes, _, _ = gmsh.model.mesh.getNodes(0, tag)
        mapping[int(nodes[0])] = index
    tags, coordinates, _ = gmsh.model.mesh.getNodes()
    coordinates = coordinates.reshape(-1, 3)
    added = []
    for tag, coordinate in zip(tags, coordinates):
        if int(tag) not in mapping:
            mapping[int(tag)] = len(points) + len(added)
            added.append(coordinate[:2])
    types, _, connectivities = gmsh.model.mesh.getElements(2)
    result = list(cells)
    for kind, connectivity in zip(types, connectivities):
        width = {2: 3, 3: 4}[int(kind)]
        for row in connectivity.reshape(-1, width):
            cell = np.asarray([mapping[int(tag)] for tag in row], dtype=np.int64)
            result.append(cell)
    if added:
        points = np.vstack((points, added))
    # Orient all cells counterclockwise before the common extrusion stage.
    for i, cell in enumerate(result):
        polygon = points[cell]
        area = np.sum(polygon[:, 0] * np.roll(polygon[:, 1], -1)
                      - polygon[:, 1] * np.roll(polygon[:, 0], -1))
        if area < 0:
            result[i] = cell[::-1].copy()
    return points, result

# -------------------------------------------------------------------------------- #
