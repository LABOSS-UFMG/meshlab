# -------------------------------------------------------------------------------- #
import numpy as np

from numbers import Number

from meshlab.data.mesh import Mesh
from meshlab.data.contour import Contour
from meshlab.utils import validation

# -------------------------------------------------------------------------------- #
def advance_front(
        mesh: Mesh,
        front: Contour,
        normals: np.ndarray,
        height: float | np.ndarray,
    ) -> Contour:
    """
    Advance a closed front by one layer.

    Parameters
    ----------
    mesh
        Mesh to be modified.
    front
        Current front.
    normals
        Unit outward normals computed at the front vertices.
    height | np.ndarray
        Layer thickness.

    Returns
    -------
    Group
        New front.
    """
    # ------------------------------------------------------------------------ #
    # Validate arguments
    validation.is_object(mesh, Mesh)
    validation.is_object(front, Contour)
    validation.is_object(normals, np.ndarray)

    for normal in normals:
        validation.is_sequence(normal.tolist(), 2, Number)

    validation.is_union(height, [float, np.ndarray])
    if isinstance(height, np.ndarray):
        validation.is_sequence(height.tolist(), None, Number)

    # ------------------------------------------------------------------------ #
    # Create new front
    num_vertices = front.num_indices

    new_front = Contour(
        name=front.name,
        capacity=num_vertices,
    )

    # ------------------------------------------------------------------------ #
    # Verify height
    if isinstance(height, Number):
        height = [height for _ in range(len(normals))]

    # ------------------------------------------------------------------------ #
    # Create new vertices
    for i in range(num_vertices):

        vertex_index = front.indices[i]
        vertex = mesh.vertices[vertex_index]
        new_vertex = vertex + height[i] * normals[i]

        new_index = mesh.add_vertex(new_vertex)
        new_front.add_index(new_index)

    # ------------------------------------------------------------------------ #
    # Create quadrilateral cells
    for i in range(num_vertices):
        
        i_next = (i + 1) % num_vertices

        cell = [
            front.indices[i],
            front.indices[i_next],
            new_front.indices[i_next],
            new_front.indices[i],
        ]

        mesh.add_cell(cell)

    # ------------------------------------------------------------------------ #
    return new_front

# -------------------------------------------------------------------------------- #
