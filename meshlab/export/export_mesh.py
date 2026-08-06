# -------------------------------------------------------------------------------- #
import gmsh
import numpy as np

from typing import Sequence

from meshlab.data.mesh import Mesh
from meshlab.data.contour import Contour
from meshlab.utils import validation

# -------------------------------------------------------------------------------- #
def _partition_boundary_layer(
        mesh: Mesh,
    ) -> list[np.ndarray]:
    """
    Partition the boundary-layer cells into connected bodies.

    Two cells belong to the same body if they share a vertex. Each body is
    later imported into its own discrete Gmsh surface: extruding a single
    discrete surface spanning multiple disconnected bodies silently drops
    boundary faces for all but one body, so bodies must be kept apart.

    Parameters
    ----------
    mesh : Mesh
        Mesh containing the boundary-layer cells.

    Returns
    -------
    list[ndarray]
        Cell indices of each connected body.
    """
    # ------------------------------------------------------------------------ #
    # Union-Find over cells, merging cells that share a vertex
    parent = list(range(mesh.num_cells))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i: int, j: int) -> None:
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[ri] = rj

    # ------------------------------------------------------------------------ #
    vertex_to_cell = {}

    for i in range(mesh.num_cells):
        for vertex in mesh.cells[i]:
            if vertex == -1:
                continue

            vertex = int(vertex)

            if vertex in vertex_to_cell:
                union(i, vertex_to_cell[vertex])
            else:
                vertex_to_cell[vertex] = i

    # ------------------------------------------------------------------------ #
    bodies = {}

    for i in range(mesh.num_cells):
        bodies.setdefault(find(i), []).append(i)

    # ------------------------------------------------------------------------ #
    return [np.array(cells) for cells in bodies.values()]

# -------------------------------------------------------------------------------- #
def _export_body(
        mesh: Mesh,
        cells: np.ndarray,
        element_offset: int,
    ) -> int:
    """
    Export one connected body of boundary-layer cells to a discrete surface.

    Parameters
    ----------
    mesh : Mesh
        Mesh containing the vertex coordinates and cell connectivity.
    cells : ndarray
        Indices of the cells composing the body.
    element_offset : int
        Number of quadrilateral elements already exported by other bodies.
        Element tags are global in Gmsh, so every body must continue
        numbering from where the previous one left off.

    Returns
    -------
    int
        Tag of the created discrete surface.
    """
    # ------------------------------------------------------------------------ #
    surface_tag = gmsh.model.addDiscreteEntity(2)

    # ------------------------------------------------------------------------ #
    # Export the vertices referenced by the body
    vertices = sorted({
        int(vertex)
        for cell in mesh.cells[cells]
        for vertex in cell
        if vertex != -1
    })

    node_tags = [vertex + 1 for vertex in vertices]

    coordinates = []

    for vertex in vertices:
        coordinates.extend([
            mesh.vertices[vertex, 0],
            mesh.vertices[vertex, 1],
            0.0,
        ])

    gmsh.model.mesh.addNodes(
        dim=2,
        tag=surface_tag,
        nodeTags=node_tags,
        coord=coordinates,
    )

    # ------------------------------------------------------------------------ #
    # Export the quadrilateral cells composing the body
    element_tags = []
    connectivity = []

    for i, cell_index in enumerate(cells):

        element_tags.append(element_offset + i + 1)

        cell = mesh.cells[cell_index]

        connectivity.extend([
            cell[0] + 1,
            cell[1] + 1,
            cell[2] + 1,
            cell[3] + 1,
        ])

    # ------------------------------------------------------------------------ #
    # Gmsh element type:
    #   3 -> 4-node quadrilateral
    gmsh.model.mesh.addElementsByType(
        tag=surface_tag,
        elementType=3,
        elementTags=element_tags,
        nodeTags=connectivity,
    )

    # ------------------------------------------------------------------------ #
    return surface_tag

# -------------------------------------------------------------------------------- #
def _export_boundary_layer(
        mesh: Mesh,
    ) -> list[int]:
    """
    Export the boundary-layer mesh, one discrete surface per connected body.

    Parameters
    ----------
    mesh : Mesh
        Mesh containing the generated boundary-layer elements.

    Returns
    -------
    list[int]
        Tags of the created discrete surfaces.
    """
    # ------------------------------------------------------------------------ #
    bodies = _partition_boundary_layer(mesh)

    # ------------------------------------------------------------------------ #
    surface_tags = []
    element_offset = 0

    for cells in bodies:
        surface_tags.append(_export_body(mesh, cells, element_offset))
        element_offset += len(cells)

    # ------------------------------------------------------------------------ #
    return surface_tags

# -------------------------------------------------------------------------------- #
def _identify_wall_curves(
        walls: Sequence[Contour],
    ) -> dict[int, int]:
    """
    Match each wall contour to the discrete curve created by Gmsh.

    ``gmsh.model.mesh.createTopology`` automatically classifies the boundary
    of each discrete surface into curves, without knowledge of which curve is
    a wall and which is a front. Curves are matched to contours by comparing
    node tags exactly, which is robust even when several walls and fronts
    have a similar shape or length.

    Parameters
    ----------
    walls : Sequence[Contour]
        Wall contours.

    Returns
    -------
    dict[int, int]
        Maps ``id(wall)`` to the tag of its matching Gmsh curve.
    """
    # ------------------------------------------------------------------------ #
    wall_node_sets = {
        id(wall): set((wall.indices[:wall.num_indices] + 1).tolist())
        for wall in walls
    }

    # ------------------------------------------------------------------------ #
    wall_curves = {}

    for dim, tag in gmsh.model.getEntities(1):

        node_tags, _, _ = gmsh.model.mesh.getNodes(1, tag, includeBoundary=True)
        node_set = set(int(node_tag) for node_tag in node_tags)

        for wall in walls:
            if wall_node_sets[id(wall)] == node_set:
                wall_curves[id(wall)] = tag

    # ------------------------------------------------------------------------ #
    for wall in walls:
        if id(wall) not in wall_curves:
            raise RuntimeError(
                f"Could not match wall contour '{wall.name}' to a Gmsh curve."
            )

    # ------------------------------------------------------------------------ #
    return wall_curves

# -------------------------------------------------------------------------------- #
def _build_boundary_lines(
        mesh: Mesh,
        contour: Contour,
    ) -> list[int]:
    """
    Build a closed polygon of Gmsh built-in-kernel lines matching a contour.

    Unlike a discrete curve reused from the boundary-layer mesh, a polygon
    built from ``geo`` points and lines is not resampled by Gmsh: each line
    is pinned to its two endpoints with ``setTransfiniteCurve(line, 2)``,
    which prevents ``gmsh.model.mesh.generate`` from inserting extra nodes
    along it. This guarantees that the outer mesh generated from these
    curves conforms exactly to the contour's original vertices; any
    duplicate nodes left where this polygon touches the boundary-layer mesh
    are merged later by ``gmsh.model.mesh.removeDuplicateNodes``.

    Parameters
    ----------
    mesh : Mesh
        Mesh containing the vertex coordinates referenced by the contour.
    contour : Contour
        Contour whose vertices define the polygon.

    Returns
    -------
    list[int]
        Tags of the created Gmsh lines, ordered and oriented like the
        contour.
    """
    # ------------------------------------------------------------------------ #
    point_tags = [
        gmsh.model.geo.addPoint(
            mesh.vertices[index, 0], mesh.vertices[index, 1], 0.0
        )
        for index in contour.indices[:contour.num_indices]
    ]

    # ------------------------------------------------------------------------ #
    line_tags = [
        gmsh.model.geo.addLine(
            point_tags[i], point_tags[(i + 1) % contour.num_indices]
        )
        for i in range(contour.num_indices)
    ]

    # ------------------------------------------------------------------------ #
    return line_tags

# -------------------------------------------------------------------------------- #
def _generate_outer_surface(
        mesh: Mesh,
        fronts: Sequence[Contour],
        farfield: Contour,
    ) -> tuple[int, list[int]]:
    """
    Generate the outer mesh bounded by the front and farfield contours.

    The farfield polygon is used as the outer boundary of the region, and
    the front polygons are used as inner boundaries (holes). Since contours
    are ordered counter-clockwise, the front lines must be reversed so that
    the curve loop is correctly oriented.

    Parameters
    ----------
    mesh : Mesh
        Mesh containing the vertex coordinates referenced by the contours.
    fronts : Sequence[Contour]
        Contours delimiting the already-generated boundary-layer mesh.
    farfield : Contour
        Contour enclosing the computational domain.
    near_body_size, near_body_distance, wake_start, wake_end, wake_radius,
    wake_size, background_size, sigmoid
        Refinement parameters, see ``export_mesh``.

    Returns
    -------
    tuple[int, list[int]]
        Tag of the newly generated outer surface, and the tags of the Gmsh
        lines composing the farfield boundary.
    """
    # ------------------------------------------------------------------------ #
    front_lines = [_build_boundary_lines(mesh, front) for front in fronts]
    farfield_lines = _build_boundary_lines(mesh, farfield)

    # ------------------------------------------------------------------------ #
    # Build the curve loop bounding the outer region
    hole_lines = [-line for lines in front_lines for line in lines]

    curve_loop = gmsh.model.geo.addCurveLoop(farfield_lines + hole_lines)

    surface_tag = gmsh.model.geo.addPlaneSurface([curve_loop])

    gmsh.model.geo.synchronize()

    # ------------------------------------------------------------------------ #
    # Pin every boundary line to its two endpoints, preventing Gmsh from
    # resampling the front and farfield contours
    for lines in front_lines + [farfield_lines]:
        for line in lines:
            gmsh.model.mesh.setTransfiniteCurve(line, 2)

    # ------------------------------------------------------------------------ #
    # Generate the outer mesh
    gmsh.model.mesh.generate(2)

    # ------------------------------------------------------------------------ #
    return surface_tag, farfield_lines

# -------------------------------------------------------------------------------- #
def _extrude_surfaces(
        surface_tags: Sequence[int],
        thickness: float,
    ) -> tuple[list[int], list[int]]:
    """
    Extrude a set of surfaces into a single layer of 3D elements.

    Solvers such as OpenFOAM require a 3D volume mesh. A single-cell
    extrusion along the z-axis produces a "flat" 3D mesh suitable for
    pseudo-2D simulations, with the extruded top and bottom surfaces later
    exported as the ``frontAndBack`` empty-boundary patch.

    Parameters
    ----------
    surface_tags : Sequence[int]
        Tags of the surfaces to extrude.
    thickness : float
        Extrusion length along the z-axis.

    Returns
    -------
    tuple[list[int], list[int]]
        Tags of the resulting volumes, and tags of the extruded top surfaces
        (translated copies of ``surface_tags``).
    """
    # ------------------------------------------------------------------------ #
    volume_tags = []
    top_tags = []

    for surface_tag in surface_tags:

        extrusion = gmsh.model.geo.extrude(
            [(2, surface_tag)], 0.0, 0.0, thickness,
            numElements=[1], heights=[1.0], recombine=True,
        )

        gmsh.model.geo.synchronize()

        volume_tags.append(next(tag for dim, tag in extrusion if dim == 3))
        top_tags.append(extrusion[0][1])

    # ------------------------------------------------------------------------ #
    return volume_tags, top_tags

# -------------------------------------------------------------------------------- #
def _classify_side_surfaces(
        volume_tags: Sequence[int],
        excluded_surfaces: set[int],
        walls: Sequence[Contour],
        wall_curves: dict[int, int],
        farfield_lines: Sequence[int],
    ) -> tuple[dict[int, list[int]], list[int]]:
    """
    Classify the side surfaces of the extruded volumes into physical groups.

    Each side surface is identified by the curve it was extruded from: if
    that curve matches a wall contour, the surface is a wall patch; if it
    belongs to the farfield polygon, it is a farfield patch. Side surfaces
    extruded from a front contour are internal interfaces between the
    boundary-layer and outer volumes and are intentionally left unassigned,
    so Gmsh treats them as internal faces.

    Parameters
    ----------
    volume_tags : Sequence[int]
        Tags of the extruded volumes.
    excluded_surfaces : set[int]
        Tags of the top and bottom (``frontAndBack``) surfaces, excluded
        from classification.
    walls : Sequence[Contour]
        Wall contours.
    wall_curves : dict[int, int]
        Maps ``id(wall)`` to the tag of its matching Gmsh curve.
    farfield_lines : Sequence[int]
        Tags of the Gmsh lines composing the farfield boundary.

    Returns
    -------
    tuple[dict[int, list[int]], list[int]]
        Maps ``id(wall)`` to the tags of its side surfaces, and the tags of
        the farfield side surfaces.
    """
    # ------------------------------------------------------------------------ #
    side_surfaces = set()

    for volume_tag in volume_tags:
        boundary = gmsh.model.getBoundary(
            [(3, volume_tag)], oriented=False, recursive=False
        )
        side_surfaces |= {tag for dim, tag in boundary if dim == 2}

    side_surfaces -= excluded_surfaces

    # ------------------------------------------------------------------------ #
    farfield_line_set = set(farfield_lines)

    wall_surfaces = {id(wall): [] for wall in walls}
    farfield_surfaces = []

    for surface_tag in side_surfaces:

        _, curves = gmsh.model.getAdjacencies(2, surface_tag)
        curves = set(curves)

        wall = next(
            (wall for wall in walls if wall_curves[id(wall)] in curves), None
        )

        if wall is not None:
            wall_surfaces[id(wall)].append(surface_tag)
        elif curves & farfield_line_set:
            farfield_surfaces.append(surface_tag)

    # ------------------------------------------------------------------------ #
    for wall in walls:
        if not wall_surfaces[id(wall)]:
            raise RuntimeError(
                f"Could not find any side surface for wall '{wall.name}'."
            )

    if not farfield_surfaces:
        raise RuntimeError("Could not find any side surface for the farfield.")

    # ------------------------------------------------------------------------ #
    return wall_surfaces, farfield_surfaces

# -------------------------------------------------------------------------------- #
def _create_physical_groups(
        walls: Sequence[Contour],
        wall_surfaces: dict[int, list[int]],
        farfield: Contour,
        farfield_surfaces: Sequence[int],
        frontback_surfaces: Sequence[int],
        volume_tags: Sequence[int],
    ) -> None:
    """
    Create the Gmsh physical groups exported to the mesh file.

    Each group is assigned to the faces bounding the fluid volume, so the
    mesh can be converted directly to OpenFOAM patches: each wall contour
    becomes its own physical surface named after the contour, the farfield
    becomes a physical surface as well, and the top and bottom faces left by
    the extrusion are grouped into a single ``frontAndBack`` surface, meant
    to be set to the ``empty`` patch type for pseudo-2D simulations. The
    boundary-layer and outer volumes are combined into a single physical
    volume representing the fluid domain.

    Parameters
    ----------
    walls : Sequence[Contour]
        Wall contours.
    wall_surfaces : dict[int, list[int]]
        Maps ``id(wall)`` to the tags of its side surfaces.
    farfield : Contour
        Contour enclosing the computational domain.
    farfield_surfaces : Sequence[int]
        Tags of the farfield side surfaces.
    frontback_surfaces : Sequence[int]
        Tags of the top and bottom surfaces left by the extrusion.
    volume_tags : Sequence[int]
        Tags of the extruded volumes composing the fluid domain.
    """
    # ------------------------------------------------------------------------ #
    for wall in walls:
        gmsh.model.addPhysicalGroup(2, wall_surfaces[id(wall)], name=wall.name)

    gmsh.model.addPhysicalGroup(2, list(farfield_surfaces), name=farfield.name)

    gmsh.model.addPhysicalGroup(2, list(frontback_surfaces), name="frontAndBack")

    gmsh.model.addPhysicalGroup(3, list(volume_tags), name="fluid")

    # ------------------------------------------------------------------------ #
    return None

# -------------------------------------------------------------------------------- #
def export_mesh(
        mesh: Mesh,
        walls: Sequence[Contour],
        fronts: Sequence[Contour],
        farfield: Contour,
        filename: str = "output.msh",
        show: bool = False,
    ) -> None:
    """
    Export a MeshLab mesh to Gmsh, ready for conversion to OpenFOAM.

    The boundary-layer elements are imported into Gmsh as discrete surfaces
    (one per connected body). The region between the fronts and the farfield
    is then meshed by Gmsh, producing a hybrid mesh combining the
    boundary-layer quadrilaterals with an unstructured outer mesh that
    conforms exactly to the fronts. Since OpenFOAM requires a 3D volume
    mesh, the whole domain is extruded by a single cell along the z-axis,
    ready to be converted with ``gmshToFoam`` (the resulting
    ``frontAndBack`` patch still needs to be set to the ``empty`` type by
    hand, as ``gmshToFoam`` does not infer patch types).

    The outer mesh can optionally be refined in two regions: a band that
    follows the fronts, and a capsule-shaped region along the wake.

    Parameters
    ----------
    mesh : Mesh
        Mesh containing the generated boundary-layer elements.
    walls : Sequence[Contour]
        Wall contours. Each contour is exported as its own physical surface.
    fronts : Sequence[Contour]
        Front contours delimiting the already-generated mesh.
    farfield : Contour
        External contour enclosing the computational domain.
    filename : str, default="airfoil.msh"
        Name of the output Gmsh mesh file.
    show : bool, default=False
        If True, display the Gmsh GUI before saving the mesh file.
    """
    # ------------------------------------------------------------------------ #
    # Validate input arguments
    validation.is_object(mesh, Mesh)
    validation.is_sequence(walls, None, Contour)
    validation.is_sequence(fronts, None, Contour)
    validation.is_object(farfield, Contour)

    # ------------------------------------------------------------------------ #
    # Initialize Gmsh
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.option.setNumber("General.Verbosity", 0)

    try:

        # -------------------------------------------------------------------- #
        # Create a new Gmsh model
        gmsh.model.add("MeshLab")
        gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
        gmsh.option.setNumber("General.Terminal", 0)

        # -------------------------------------------------------------------- #
        # Export the boundary-layer mesh and identify its wall curves
        boundary_layer_tags = _export_boundary_layer(mesh)

        gmsh.model.mesh.createTopology()
        gmsh.model.geo.synchronize()

        wall_curves = _identify_wall_curves(walls)

        # -------------------------------------------------------------------- #
        # Mesh the outer region, bounded by the fronts and the farfield
        outer_tag, farfield_lines = _generate_outer_surface(mesh, fronts, farfield)

        # -------------------------------------------------------------------- #
        # Extrude the whole domain into a single layer of 3D elements
        bottom_tags = boundary_layer_tags + [outer_tag]

        volume_tags, top_tags = _extrude_surfaces(bottom_tags, 1.0)

        gmsh.model.mesh.generate(3)

        # Merge the outer mesh's boundary nodes with the coincident
        # boundary-layer mesh nodes
        gmsh.model.mesh.removeDuplicateNodes()

        # gmsh.model.mesh.optimize("Laplace2D")
        gmsh.model.mesh.optimize("Netgen")

        # -------------------------------------------------------------------- #
        # Classify the extruded side surfaces and create physical groups
        frontback_surfaces = bottom_tags + top_tags

        wall_surfaces, farfield_surfaces = _classify_side_surfaces(
            volume_tags, set(frontback_surfaces), walls, wall_curves, farfield_lines
        )

        _create_physical_groups(
            walls, wall_surfaces, farfield, farfield_surfaces,
            frontback_surfaces, volume_tags,
        )

        # -------------------------------------------------------------------- #
        # Show the model before saving
        if show:
            gmsh.fltk.run()

        # Write mesh file
        gmsh.write(filename)

    finally:

        # -------------------------------------------------------------------- #
        # Finalize Gmsh even if an exception is raised
        gmsh.finalize()

    # ------------------------------------------------------------------------ #
    return None

# -------------------------------------------------------------------------------- #
