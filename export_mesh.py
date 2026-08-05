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
    Export quadrilateral cells to a Gmsh discrete surface.

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
    #
    # Gmsh uses 1-based indexing, whereas MeshLab stores vertex indices using
    # 0-based indexing.
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
def _export_contour(
        contour: Contour,
    ) -> int:
    """
    Export a contour as a Gmsh discrete curve.

    Parameters
    ----------
    contour : Contour
        Contour to be exported.

    Returns
    -------
    int
        Tag of the created Gmsh curve.
    """
    # ------------------------------------------------------------------------ #
    # Create a discrete curve
    curve_tag = gmsh.model.addDiscreteEntity(1)

    # ------------------------------------------------------------------------ #
    # Allocate memory
    element_tags = []
    connectivity = []

    # ------------------------------------------------------------------------ #
    # Create line elements
    for i in range(contour.num_indices):

        i_next = (i + 1) % contour.num_indices

        element_tags.append(i + 1)

        connectivity.extend([
            contour.indices[i] + 1,
            contour.indices[i_next] + 1,
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
def _export_walls(walls: Sequence[Contour]) -> None:
    """
    Export wall contours.

    Returns
    -------
    list[int]
        Tags of the created Gmsh curves.
    """
    # ------------------------------------------------------------------------ #
    curve_tags = []

    for wall in walls:
        curve_tags.append(_export_contour(wall))

    # ------------------------------------------------------------------------ #
    return curve_tags

# -------------------------------------------------------------------------------- #
def _export_fronts(fronts: Sequence[Contour]) -> list[int]:
    """
    Export front contours.

    Returns
    -------
    list[int]
        Tags of the created Gmsh curves.
    """
    # ------------------------------------------------------------------------ #
    curve_tags = []

    for front in fronts:
        curve_tags.append(_export_contour(front))

    # ------------------------------------------------------------------------ #
    return curve_tags

# -------------------------------------------------------------------------------- #
def _export_farfield(
        farfield: Contour,
    ) -> int:
    """
    Export the farfield contour as a Gmsh discrete curve.

    Parameters
    ----------
    farfield : Contour
        Contour defining the outer boundary of the computational domain.

    Returns
    -------
    int
        Tag of the created Gmsh curve.
    """
    # ------------------------------------------------------------------------ #
    curve_tag = _export_contour(farfield)

    # ------------------------------------------------------------------------ #
    return curve_tag

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

        # Create a discrete surface to store the imported mesh
        surface_tag = gmsh.model.addDiscreteEntity(2)

        # Export mesh
        _export_vertices(mesh, surface_tag)
        _export_cells(mesh, surface_tag)
        _export_walls(walls)
        _export_fronts(fronts)
        _export_farfield(farfield)

        gmsh.model.mesh.reclassifyNodes()
        gmsh.model.mesh.createGeometry()

        for entity in gmsh.model.getEntities():
            print(entity)

        # -------------------------------------------------------------------- #
        # Future implementation:
        
        # 1. Export mesh vertices.
        # 2. Export quadrilateral boundary-layer cells.
        # 3. Export wall contours.
        # 4. Export front contours.
        # 5. Export farfield contour.
        # 6. Generate the outer mesh.
        # 7. Create physical groups.
        
        # -------------------------------------------------------------------- #

        # Show the model before saving
        if show:
            gmsh.fltk.run()

        # Write mesh file
        # gmsh.write(filename)

    finally:

        # -------------------------------------------------------------------- #
        # Finalize Gmsh even if an exception is raised
        gmsh.finalize()

    # ------------------------------------------------------------------------ #
    return None

# -------------------------------------------------------------------------------- #