import numpy as np
import matplotlib.pyplot as plt

from typing import Sequence

from mesh import Mesh
from group import Group

# -------------------------------------------------------------------------------- #
def insert_surface(
        mesh: Mesh,
        group: Group,
        vertices: Sequence[Sequence[float]],
    ) -> None:
    """
    Insert a closed surface into the mesh.

    Parameters
    ----------
    mesh
        Mesh where the vertices will be inserted.
    group
        Group that stores the ordered indices of the surface vertices.
    vertices
        Ordered coordinates of the surface vertices. The contour is assumed to
        be closed, i.e., the last vertex is implicitly connected to the first.
    """
    # ------------------------------------------------------------------------ #
    for vertex in vertices:

        index = mesh.add_vertex(vertex)

        group.add_index(index)

    # ------------------------------------------------------------------------ #
    return None

# -------------------------------------------------------------------------------- #
def compute_normals(
        mesh: Mesh,
        front: Group,
    ) -> np.ndarray:
    """
    Compute outward unit normals at the vertices of a closed contour.

    Parameters
    ----------
    mesh
        Mesh containing the vertex coordinates.
    front
        Closed contour defined by ordered vertex indices in counter-clockwise
        orientation.

    Returns
    -------
    np.ndarray
        Array of shape (N, 2) containing one unit normal per vertex.
    """
    # ------------------------------------------------------------------------ #
    num_vertices = front.num_indices

    normals = np.empty((num_vertices, 2), dtype=np.float64)

    # ------------------------------------------------------------------------ #
    for i in range(num_vertices):

        i_prev = (i - 1) % num_vertices
        i_next = (i + 1) % num_vertices

        p_prev = mesh.vertices[front.indices[i_prev]]
        p_next = mesh.vertices[front.indices[i_next]]

        tangent = p_next - p_prev
        tangent /= np.linalg.norm(tangent)

        normals[i, 0] = tangent[1]
        normals[i, 1] = -tangent[0]

    # ------------------------------------------------------------------------ #
    return normals

# -------------------------------------------------------------------------------- #
def advance_front(
        mesh: Mesh,
        front: Group,
        normals: np.ndarray,
        height: float,
    ) -> Group:
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
    height
        Layer thickness.

    Returns
    -------
    Group
        New front.
    """
    # ------------------------------------------------------------------------ #
    num_vertices = front.num_indices

    new_front = Group(
        name=front.name,
        capacity=num_vertices,
    )

    # ------------------------------------------------------------------------ #
    # Create new vertices
    for i in range(num_vertices):

        vertex_index = front.indices[i]

        vertex = mesh.vertices[vertex_index]

        new_vertex = vertex + height * normals[i]

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
# -------------------------------------------------------------------------------- #
import matplotlib.pyplot as plt

from mesh import Mesh
from group import Group

# -------------------------------------------------------------------------------- #
def plot_mesh(
        mesh: Mesh,
        groups: list[Group] | None = None,
    ) -> None:
    """
    Plot the mesh and groups.

    Parameters
    ----------
    mesh
        Mesh to be plotted.
    groups
        List of groups to be highlighted.
    """

    # ------------------------------------------------------------------------ #
    fig, ax = plt.subplots()

    # fig.subplots_adjust(
    #     left=0,
    #     right=1,
    #     bottom=0,
    #     top=1,
    # )

    # ax.set_position([0, 0, 1, 1])
    
    # ------------------------------------------------------------------------ #
    # Plot cells
    for i in range(mesh.num_cells):

        cell = mesh.cells[i]
        cell = cell[cell >= 0]

        vertices = mesh.vertices[cell]

        x = list(vertices[:, 0]) + [vertices[0, 0]]
        y = list(vertices[:, 1]) + [vertices[0, 1]]

        ax.plot(
            x,
            y,
            color="black",
            linewidth=0.8,
        )

    # ------------------------------------------------------------------------ #
    # Plot groups
    if groups is not None:

        for group in groups:

            vertices = mesh.vertices[group.indices[:group.num_indices]]

            x = list(vertices[:, 0]) + [vertices[0, 0]]
            y = list(vertices[:, 1]) + [vertices[0, 1]]

            ax.plot(
                x,
                y,
                linewidth=2.5,
                label=group.name,
            )

    # ------------------------------------------------------------------------ #
    ax.set_aspect("equal", adjustable="datalim")
    ax.autoscale_view()

    if groups:
        ax.legend()

    plt.show()

    # ------------------------------------------------------------------------ #
    return None

# -------------------------------------------------------------------------------- #
