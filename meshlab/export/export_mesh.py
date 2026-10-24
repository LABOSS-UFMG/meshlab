# -------------------------------------------------------------------------------- #
from collections.abc import Sequence
from pathlib import Path
from uuid import uuid4

import gmsh
import numpy as np

from meshlab.core import Mesh, Front, Curve, Refinement
from meshlab.export.boundary_layer import collect_cells
from meshlab.export.remaining_domain import generate_remaining
from meshlab.export.extrusion import extrude_mesh
from meshlab.export.physical_groups import classify_faces, write_groups

# -------------------------------------------------------------------------------- #
def export_mesh(
        mesh: Mesh,
        fronts: Sequence[Front] | None = None,
        filename: str | Path = "output.msh",
        mode: str = "planar",
        thickness: float = 1.0,
        axis: str | Curve | None = None,
        angle: float = np.pi / 36,
        mesh_size: float | None = None,
        show: bool = False,
        refinements: Sequence[Refinement] | None = None,
    ) -> None:
    """Complete a 2D section and export one volume layer for OpenFOAM.

    Parameters
    ----------
    mesh : Mesh
        Planar dim=2 mesh with valid triangles/quadrilaterals and all physical
        boundaries registered by unique names. Not modified by export.
    fronts : sequence of Front | None, default=None
        All residual layer interfaces. If omitted, derive them from cell
        incidence and physical boundaries. Supplied fronts must match them.
    filename : str | Path, default="output.msh"
        Output MSH 2.2 ASCII file; the parent directory must exist.
    mode : {"planar", "axisymmetric"}, default="planar"
        Translation along z or symmetric revolution about a named straight axis.
    thickness : float, default=1.0
        Positive planar extrusion length, with one element through thickness.
    axis : str | Curve | None, default=None
        Straight revolution axis in the xy plane. A string selects a registered
        boundary; a Curve supplies an independent geometric axis outside the
        domain if necessary. Required for axisymmetric mode; not an active wall.
    angle : float, default=pi/36
        Positive total wedge angle in radians, less than pi. Five degrees by
        default. The section is rotated to -angle/2 then swept by angle.
    mesh_size : float | None, default=None
        Positive target size for residual interior triangles. Existing boundary
        segments remain fixed regardless of this value.
    show : bool, default=False
        Display the resulting Gmsh model before writing the file.

    refinements : sequence of Refinement | None, default=None
        Local size controls for the residual 2D region, before either sweep.
        Points and curves refine their neighborhoods; contours refine their
        interiors. Existing layer cells and boundary segments remain fixed.
        Overlapping controls use the smallest requested size. Geometries do
        not create physical groups or fixed nodes.

    Notes
    -----
    Physical names are preserved, with fluid as the volume group. Planar
    faces use frontAndBack; revolution uses wedge_front and wedge_back.
    These names must not be used for input curves. gmshToFoam and checkMesh
    are separate commands; patch types must be set to empty or wedge in the
    OpenFOAM case (including fields). No OpenFOAM case files are overwritten.

    Inputs must form a conformal, non-overlapping planar section. Axisymmetric
    coordinates must lie on one side of a nondegenerate straight axis. Nodes
    on the axis are shared, not duplicated into zero-volume cells. Curved
    axes, crossing the axis and general 3D inputs are outside this contract.
    Existing Gmsh sessions/models are preserved; only temporary models owned
    by this call are removed. No optimization moves the original layer nodes.
    """
    # ------------------------------------------------------------------------ #
    # Own a temporary model and preserve options of an existing Gmsh session
    owned_session = not gmsh.isInitialized()
    if owned_session:
        gmsh.initialize()
    previous_model = gmsh.model.getCurrent()
    options = {name: gmsh.option.getNumber(name) for name in (
        "General.Terminal", "Mesh.MshFileVersion", "Mesh.Binary", "Mesh.SaveAll",
        "Mesh.MeshSizeMin", "Mesh.MeshSizeMax", "Mesh.ElementOrder", "Mesh.RecombineAll",
    )}
    model = "meshlab_" + uuid4().hex
    gmsh.model.add(model)
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
        gmsh.option.setNumber("Mesh.Binary", 0)
        gmsh.option.setNumber("Mesh.SaveAll", 0)
        gmsh.option.setNumber("Mesh.ElementOrder", 1)
        gmsh.option.setNumber("Mesh.RecombineAll", 0)

        # -------------------------------------------------------------------- #
        # Complete the section without remeshing the supplied layer cells
        points, cells = generate_remaining(
            mesh, collect_cells(mesh), fronts, mesh_size, refinements,
        )
        gmsh.model.remove()
        gmsh.model.add(model)

        # -------------------------------------------------------------------- #
        # Sweep the hybrid section and identify the exterior physical faces
        tags, coordinates, blocks, frame = extrude_mesh(
            mesh, points, cells, mode, thickness, axis, angle,
        )
        element_tags = np.concatenate([ids for ids, _ in blocks.values()])
        quality = gmsh.model.mesh.getElementQualities(element_tags, "minDetJac")
        if not len(quality) or np.any(np.asarray(quality) <= 0):
            raise RuntimeError("Extrusion generated degenerate or inverted volume cells.")
        groups = classify_faces(mesh, points, tags, coordinates, blocks, frame)
        gmsh.model.remove()
        gmsh.model.add(model)
        write_groups(tags, coordinates, blocks, groups)

        # -------------------------------------------------------------------- #
        # Show optionally and write the OpenFOAM conversion input
        if show:
            gmsh.fltk.run()
        gmsh.write(str(filename))
    finally:
        # -------------------------------------------------------------------- #
        # Restore the caller's Gmsh state even when generation fails
        if model in gmsh.model.list():
            gmsh.model.setCurrent(model)
            gmsh.model.remove()
        for name, value in options.items():
            gmsh.option.setNumber(name, value)
        if previous_model in gmsh.model.list():
            gmsh.model.setCurrent(previous_model)
        if owned_session:
            gmsh.finalize()

# -------------------------------------------------------------------------------- #
