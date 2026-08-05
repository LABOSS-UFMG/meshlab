# -------------------------------------------------------------------------------- #
import numpy as np

from numbers import Number

from meshlab.data.mesh import Mesh
from meshlab.data.contour import Contour
from meshlab.utils import validation

# -------------------------------------------------------------------------------- #
def insert_contour(
        mesh: Mesh,
        contour: Contour,
        vertices: np.ndarray,
    ) -> None:
    """
    Insert a closed surface into the mesh.

    Parameters
    ----------
    mesh : Mesh
        Mesh where the vertices will be inserted.
    contour : Contour
        Contour that stores the ordered indices of the surface vertices.
    vertices: np.ndarray
        Ordered coordinates of the surface vertices. The contour is assumed to
        be closed, i.e., the last vertex is implicitly connected to the first.
    """
    # ------------------------------------------------------------------------ #
    # Validate arguments
    validation.is_object(mesh, Mesh)
    validation.is_object(contour, Contour)
    validation.is_object(vertices, np.ndarray)
    
    for vertex in vertices:
        validation.is_sequence(vertex.tolist(), 2, Number)
    
    # ------------------------------------------------------------------------ #
    # Add vertices at mesh and contour
    for vertex in vertices:
        index = mesh.add_vertex(vertex)
        contour.add_index(index)

    # ------------------------------------------------------------------------ #
    return None

# -------------------------------------------------------------------------------- #
