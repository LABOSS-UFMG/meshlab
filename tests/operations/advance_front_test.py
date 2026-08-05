# -------------------------------------------------------------------------------- #
import numpy as np

from meshlab.data import Mesh, Contour
from meshlab.operations import advance_front

# -------------------------------------------------------------------------------- #

def create_square_front():
    """
    Create a square mesh and contour.
    """

    mesh = Mesh(
        vertices_capacity=100,
        cells_capacity=100,
    )

    front = Contour(
        name="Front",
        capacity=4,
    )

    vertices = np.array([
        [-1.0, -1.0],
        [ 1.0, -1.0],
        [ 1.0,  1.0],
        [-1.0,  1.0],
    ])

    for vertex in vertices:
        index = mesh.add_vertex(vertex)
        front.add_index(index)

    return mesh, front


# -------------------------------------------------------------------------------- #

def create_square_normals():
    """
    Create outward normals for a square contour.
    """

    normals = np.array([
        [-1.0, -1.0],
        [ 1.0, -1.0],
        [ 1.0,  1.0],
        [-1.0,  1.0],
    ])

    normals /= np.linalg.norm(
        normals,
        axis=1,
    )[:, None]

    return normals


# -------------------------------------------------------------------------------- #

def test_advance_front_returns_contour():
    """
    Test returned object type.
    """

    mesh, front = create_square_front()

    normals = create_square_normals()

    new_front = advance_front(
        mesh,
        front,
        normals,
        0.1,
    )

    assert isinstance(
        new_front,
        Contour,
    )


# -------------------------------------------------------------------------------- #

def test_advance_front_number_of_vertices():
    """
    Test that the new front has the same number of vertices.
    """

    mesh, front = create_square_front()

    normals = create_square_normals()

    new_front = advance_front(
        mesh,
        front,
        normals,
        0.1,
    )

    assert new_front.num_indices == front.num_indices

    assert mesh.num_vertices == 8


# -------------------------------------------------------------------------------- #

def test_advance_front_vertex_position():
    """
    Test new vertex positions.
    """

    mesh, front = create_square_front()

    normals = create_square_normals()

    height = 0.5

    new_front = advance_front(
        mesh,
        front,
        normals,
        height,
    )

    for i in range(front.num_indices):

        old_vertex = mesh.vertices[front.indices[i]]
        new_vertex = mesh.vertices[new_front.indices[i]]

        expected = old_vertex + height * normals[i]

        np.testing.assert_allclose(
            new_vertex,
            expected,
        )


# -------------------------------------------------------------------------------- #

def test_advance_front_creates_cells():
    """
    Test quadrilateral cell generation.
    """

    mesh, front = create_square_front()

    normals = create_square_normals()

    advance_front(
        mesh,
        front,
        normals,
        0.1,
    )

    assert mesh.num_cells == 4

    expected = np.array([
        [
            0, 1, 5, 4
        ],
        [
            1, 2, 6, 5
        ],
        [
            2, 3, 7, 6
        ],
        [
            3, 0, 4, 7
        ],
    ])

    np.testing.assert_array_equal(
        mesh.cells[:4, :4],
        expected,
    )


# -------------------------------------------------------------------------------- #

def test_advance_front_variable_height():
    """
    Test advancing the front with different layer heights.
    """

    mesh, front = create_square_front()

    normals = create_square_normals()

    heights = np.array([
        0.1,
        0.2,
        0.3,
        0.4,
    ])

    new_front = advance_front(
        mesh,
        front,
        normals,
        heights,
    )

    for i in range(front.num_indices):

        old_vertex = mesh.vertices[front.indices[i]]
        new_vertex = mesh.vertices[new_front.indices[i]]

        expected = old_vertex + heights[i] * normals[i]

        np.testing.assert_allclose(
            new_vertex,
            expected,
        )

# -------------------------------------------------------------------------------- #
