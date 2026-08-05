# -------------------------------------------------------------------------------- #
import gmsh

from typing import Sequence

from meshlab.data.mesh import Mesh
from meshlab.data.contour import Contour
from meshlab.utils import validation

# -------------------------------------------------------------------------------- #
def _export_vertices(
        mesh: Mesh,
        surface_tag: int,
    ) -> None:
    """
    Export mesh vertices to a Gmsh discrete surface.

    Parameters
    ----------
    mesh : Mesh
        Mesh containing the vertex coordinates.
    surface_tag : int
        Tag of the discrete Gmsh surface that will store the vertices.
    """
    # ------------------------------------------------------------------------ #
    # Allocate memory
    node_tags = []
    coordinates = []

    # ------------------------------------------------------------------------ #
    # Convert MeshLab vertices to the Gmsh format
    #
    # Gmsh uses 1-based indexing, whereas MeshLab stores vertex indices using
    # 0-based indexing.
    for i in range(mesh.num_vertices):

        node_tags.append(i + 1)

        coordinates.extend([
            mesh.vertices[i, 0],
            mesh.vertices[i, 1],
            0.0,
        ])

    # ------------------------------------------------------------------------ #
    # Add nodes to the discrete surface
    gmsh.model.mesh.addNodes(
        dim=2,
        tag=surface_tag,
        nodeTags=node_tags,
        coord=coordinates,
    )

    # ------------------------------------------------------------------------ #
    return None

# -------------------------------------------------------------------------------- #
def _export_cells(
        mesh: Mesh,
        surface_tag: int,
    ) -> None:
    """
    Export quadrilateral boundary-layer cells to a Gmsh discrete surface.

    Parameters
    ----------
    mesh : Mesh
        Mesh containing the quadrilateral connectivity.
    surface_tag : int
        Tag of the discrete Gmsh surface that will store the cells.
    """
    # ------------------------------------------------------------------------ #
    # Allocate memory
    element_tags = []
    connectivity = []

    # ------------------------------------------------------------------------ #
    # Convert MeshLab connectivity to the Gmsh format
    for i in range(mesh.num_cells):

        element_tags.append(i + 1)

        cell = mesh.cells[i]

        connectivity.extend([
            cell[0] + 1,
            cell[1] + 1,
            cell[2] + 1,
            cell[3] + 1,
        ])

    # ------------------------------------------------------------------------ #
    # Add quadrilateral elements
    #
    # Gmsh element type:
    #   3 -> 4-node quadrilateral
    gmsh.model.mesh.addElementsByType(
        tag=surface_tag,
        elementType=3,
        elementTags=element_tags,
        nodeTags=connectivity,
    )

    # ------------------------------------------------------------------------ #
    return None

# -------------------------------------------------------------------------------- #
def _export_wall(
        wall: Contour,
    ) -> int:
    """
    Export a wall contour as a Gmsh discrete curve.

    The wall curve only labels a physical group; it never bounds a newly
    generated surface, so Gmsh does not remesh it.

    Parameters
    ----------
    wall : Contour
        Wall contour to be exported.

    Returns
    -------
    int
        Tag of the created Gmsh curve.
    """
    # ------------------------------------------------------------------------ #
    curve_tag = gmsh.model.addDiscreteEntity(1)

    # ------------------------------------------------------------------------ #
    # Allocate memory
    element_tags = []
    connectivity = []

    # ------------------------------------------------------------------------ #
    # Create line elements
    for i in range(wall.num_indices):

        i_next = (i + 1) % wall.num_indices

        element_tags.append(i + 1)

        connectivity.extend([
            wall.indices[i] + 1,
            wall.indices[i_next] + 1,
        ])

    # ------------------------------------------------------------------------ #
    # Add line elements to the curve
    #
    # Gmsh element type:
    #   1 -> 2-node line
    gmsh.model.mesh.addElementsByType(
        tag=curve_tag,
        elementType=1,
        elementTags=element_tags,
        nodeTags=connectivity,
    )

    # ------------------------------------------------------------------------ #
    return curve_tag

# -------------------------------------------------------------------------------- #
def _export_walls(
        walls: Sequence[Contour],
    ) -> list[int]:
    """
    Export wall contours.

    Returns
    -------
    list[int]
        Tags of the created Gmsh curves.
    """
    # ------------------------------------------------------------------------ #
    curve_tags = [_export_wall(wall) for wall in walls]

    # ------------------------------------------------------------------------ #
    return curve_tags

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
def _generate_outer_mesh(
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

    Returns
    -------
    tuple[int, list[int]]
        Tag of the newly generated outer surface, and the tags of the Gmsh
        lines composing the farfield boundary.
    """
    # ------------------------------------------------------------------------ #
    # Build the polygons bounding the outer region
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
    # Merge the outer mesh's boundary nodes with the coincident boundary-layer
    # mesh nodes
    gmsh.model.mesh.removeDuplicateNodes()

    # ------------------------------------------------------------------------ #
    return surface_tag, farfield_lines

# -------------------------------------------------------------------------------- #
def _create_physical_groups(
        walls: Sequence[Contour],
        wall_tags: Sequence[int],
        farfield: Contour,
        farfield_tags: Sequence[int],
        surface_tags: Sequence[int],
    ) -> None:
    """
    Create the Gmsh physical groups exported to the mesh file.

    Each wall contour is exported as its own physical curve, named after the
    contour. The farfield contour is exported as a physical curve as well.
    The boundary-layer surface and the outer surface are combined into a
    single physical surface representing the fluid domain.

    Parameters
    ----------
    walls : Sequence[Contour]
        Wall contours.
    wall_tags : Sequence[int]
        Tags of the Gmsh curves associated with the wall contours.
    farfield : Contour
        Contour enclosing the computational domain.
    farfield_tags : Sequence[int]
        Tags of the Gmsh lines associated with the farfield contour.
    surface_tags : Sequence[int]
        Tags of the Gmsh surfaces composing the fluid domain.
    """
    # ------------------------------------------------------------------------ #
    for wall, wall_tag in zip(walls, wall_tags):
        gmsh.model.addPhysicalGroup(1, [wall_tag], name=wall.name)

    gmsh.model.addPhysicalGroup(1, list(farfield_tags), name=farfield.name)

    gmsh.model.addPhysicalGroup(2, list(surface_tags), name="fluid")

    # ------------------------------------------------------------------------ #
    return None

# -------------------------------------------------------------------------------- #
def export_mesh(
        mesh: Mesh,
        walls: Sequence[Contour],
        fronts: Sequence[Contour],
        farfield: Contour,
        filename: str = "airfoil.msh",
        show: bool = False,
    ) -> None:
    """
    Export a MeshLab mesh to Gmsh.

    The boundary-layer elements are imported into Gmsh as a discrete surface.
    The region between the fronts and the farfield is then meshed by Gmsh,
    producing a hybrid mesh combining the boundary-layer quadrilaterals with
    an unstructured outer mesh that conforms exactly to the fronts.

    Parameters
    ----------
    mesh : Mesh
        Mesh containing the generated boundary-layer elements.
    walls : Sequence[Contour]
        Wall contours. Each contour is exported as a physical group.
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

    try:

        # -------------------------------------------------------------------- #
        # Create a new Gmsh model
        gmsh.model.add("MeshLab")

        # Create a discrete surface to store the imported boundary-layer mesh
        surface_tag = gmsh.model.addDiscreteEntity(2)

        # -------------------------------------------------------------------- #
        # Export the boundary-layer mesh and the wall contours
        _export_vertices(mesh, surface_tag)
        _export_cells(mesh, surface_tag)

        wall_tags = _export_walls(walls)

        # -------------------------------------------------------------------- #
        # Mesh the outer region, bounded by the fronts and the farfield
        outer_tag, farfield_tags = _generate_outer_mesh(mesh, fronts, farfield)

        # -------------------------------------------------------------------- #
        # Create physical groups
        _create_physical_groups(
            walls, wall_tags, farfield, farfield_tags, [surface_tag, outer_tag]
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
