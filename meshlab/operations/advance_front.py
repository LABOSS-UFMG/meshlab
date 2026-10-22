# -------------------------------------------------------------------------------- #
import numpy as np

from numbers import Number

from meshlab.data.mesh import Mesh
from meshlab.data.contour import Contour

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
