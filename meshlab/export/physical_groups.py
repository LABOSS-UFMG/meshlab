# -------------------------------------------------------------------------------- #
import gmsh
import numpy as np

from meshlab.export.extrusion import rotate

# -------------------------------------------------------------------------------- #
# Local faces of Gmsh's first-order tetrahedron, hexahedron, prism and pyramid.
_FACES = {
    4: ((0, 2, 1), (0, 1, 3), (1, 2, 3), (2, 0, 3)),
    5: ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)),
    6: ((0, 2, 1), (3, 4, 5), (0, 1, 4, 3), (1, 2, 5, 4), (2, 0, 3, 5)),
    7: ((0, 3, 2, 1), (0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)),
}

# -------------------------------------------------------------------------------- #
def classify_faces(mesh, points, node_tags, coordinates, blocks, frame):
    """Classify exposed volume faces, excluding all internal layer interfaces.

    Face incidence comes from actual volume connectivity. Swept nodes are
    mapped back to section coordinates to preserve each named boundary even
    when Gmsh merges adjacent geometric curves during topology creation.
    """
    # ------------------------------------------------------------------------ #
    # Find the actual exterior shell of the final volume mesh
    faces = {}
    counts = {}
    for kind, (_, cells) in blocks.items():
        for cell in cells:
            for local in _FACES[kind]:
                face = tuple(int(cell[i]) for i in local)
                key = tuple(sorted(face))
                faces[key] = face
                counts[key] = counts.get(key, 0) + 1
    shell = [face for key, face in faces.items() if counts[key] == 1]
    node_rows = {int(tag): i for i, tag in enumerate(node_tags)}
    tolerance = max(float(np.ptp(coordinates, axis=0).max()), 1.0) * 1e-8

    # ------------------------------------------------------------------------ #
    # Recover section coordinates and the two extrusion planes
    if frame["mode"] == "planar":
        section = coordinates[:, :2]
        bottom = np.abs(coordinates[:, 2]) < tolerance
        top = np.abs(coordinates[:, 2] - frame["thickness"]) < tolerance
        plane_names = ("frontAndBack", "frontAndBack")
    else:
        origin, direction, radial = (frame[key] for key in ("origin", "direction", "radial"))
        offset = coordinates - origin
        axial = offset @ direction
        radius = np.hypot(offset @ radial, offset[:, 2])
        section = (origin + np.outer(axial, direction) + np.outer(radius, radial))[:, :2]
        lower = rotate(coordinates, origin, direction, frame["angle"] / 2)
        upper = rotate(coordinates, origin, direction, -frame["angle"] / 2)
        bottom = np.abs(lower[:, 2]) < tolerance
        top = np.abs(upper[:, 2]) < tolerance
        plane_names = ("wedge_front", "wedge_back")

    # ------------------------------------------------------------------------ #
    # Match only exterior nodes to the preserved original section
    source = {}
    for tag in {tag for face in shell for tag in face}:
        point = section[node_rows[tag]]
        distance = np.linalg.norm(points - point, axis=1)
        index = int(np.argmin(distance))
        if distance[index] > tolerance:
            raise RuntimeError("Extrusion changed a boundary node; cannot preserve its name.")
        source[tag] = index
    physical = {tuple(sorted((int(a), int(b)))): name
                for name, indices in mesh.boundaries.items()
                for a, b in zip(indices[:-1], indices[1:])}
    groups = {}
    for face in shell:
        rows = [node_rows[tag] for tag in face]
        if np.all(bottom[rows]):
            name = plane_names[0]
        elif np.all(top[rows]):
            name = plane_names[1]
        else:
            key = tuple(sorted({source[tag] for tag in face}))
            if key not in physical:
                raise RuntimeError("Unclassified exterior face: section interfaces are not conformal.")
            name = physical[key]
        groups.setdefault(name, []).append(face)
    return groups

# -------------------------------------------------------------------------------- #
def write_groups(node_tags, coordinates, blocks, groups):
    """Rebuild discrete output entities with one physical group per patch.

    Numerical coordinates and volume elements are copied unchanged. The
    output contains first-order volumes and only their exterior surface faces.
    The axis produces no surface patch when its swept area is zero.
    """
    volume = gmsh.model.addDiscreteEntity(3)
    gmsh.model.mesh.addNodes(3, volume, node_tags, coordinates.ravel())
    offset = 0
    for kind, (_, cells) in blocks.items():
        ids = np.arange(offset + 1, offset + len(cells) + 1)
        gmsh.model.mesh.addElementsByType(volume, kind, ids, cells.ravel())
        offset += len(cells)
    gmsh.model.addPhysicalGroup(3, [volume], name="fluid")
    for name, faces in groups.items():
        surface = gmsh.model.addDiscreteEntity(2)
        for width, kind in [(3, 2), (4, 3)]:
            selected = [face for face in faces if len(face) == width]
            if selected:
                ids = np.arange(offset + 1, offset + len(selected) + 1)
                gmsh.model.mesh.addElementsByType(surface, kind, ids, np.asarray(selected).ravel())
                offset += len(selected)
        gmsh.model.addPhysicalGroup(2, [surface], name=name)

# -------------------------------------------------------------------------------- #
