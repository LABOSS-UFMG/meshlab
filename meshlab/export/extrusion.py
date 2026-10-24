# -------------------------------------------------------------------------------- #
import gmsh
import numpy as np

from meshlab.export.boundary_layer import import_surfaces

# -------------------------------------------------------------------------------- #
def rotate(points, origin, direction, angle):
    """Rotate coordinates about a unit axis using Rodrigues' formula."""
    offset = points - origin
    return (origin + offset * np.cos(angle)
            + np.cross(direction, offset) * np.sin(angle)
            + np.outer(offset @ direction, direction) * (1.0 - np.cos(angle)))

# -------------------------------------------------------------------------------- #
def extrude_mesh(mesh, points, cells, mode, thickness, axis, angle):
    """Sweep the complete hybrid section with Gmsh, using one cell layer.

    Revolutions are symmetric about the original xy plane. The axis is a
    straight named boundary; its direction is chosen so the sweep follows
    the positive section normal. Gmsh handles collapsed nodes on the axis.
    Returns node tags, coordinates, volume blocks and a frame for face naming.
    """
    # ------------------------------------------------------------------------ #
    # Place the section on the first extrusion plane
    coordinates = np.column_stack((points, np.zeros(len(points))))
    frame = {"mode": mode, "thickness": thickness}
    if mode == "axisymmetric":
        axis_points = mesh.points[mesh.boundaries[axis]] if isinstance(axis, str) else axis.points
        origin = np.r_[axis_points[0], 0.0]
        direction = np.r_[axis_points[-1] - axis_points[0], 0.0]
        direction /= np.linalg.norm(direction)
        radial = np.array([-direction[1], direction[0], 0.0])
        if np.mean((coordinates - origin) @ radial) < 0:
            direction = -direction
            radial = -radial
        frame.update(origin=origin, direction=direction, radial=radial, angle=angle)
        coordinates = rotate(coordinates, origin, direction, -angle / 2)
    surfaces = import_surfaces(coordinates, cells)

    # ------------------------------------------------------------------------ #
    # Extrude disconnected components independently, as in the legacy exporter
    for surface in surfaces:
        if mode == "planar":
            gmsh.model.geo.extrude([(2, surface)], 0.0, 0.0, thickness,
                                   numElements=[1], heights=[1.0], recombine=True)
        else:
            gmsh.model.geo.revolve([(2, surface)], *origin, *direction, angle,
                                   numElements=[1], heights=[1.0], recombine=True)
        gmsh.model.geo.synchronize()
    gmsh.model.mesh.generate(3)
    gmsh.model.mesh.removeDuplicateNodes()

    # ------------------------------------------------------------------------ #
    # Capture volume connectivity for explicit physical boundary classification
    node_tags, coordinates, _ = gmsh.model.mesh.getNodes()
    types, tags, connectivity = gmsh.model.mesh.getElements(3)
    blocks = {int(kind): (np.asarray(ids), np.asarray(nodes).reshape(-1, {4: 4, 5: 8, 6: 6, 7: 5}[int(kind)]))
              for kind, ids, nodes in zip(types, tags, connectivity)}
    return node_tags, coordinates.reshape(-1, 3), blocks, frame

# -------------------------------------------------------------------------------- #
