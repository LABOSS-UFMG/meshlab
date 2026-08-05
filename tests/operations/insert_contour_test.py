# -------------------------------------------------------------------------------- #
import numpy as np

from meshlab.data import Mesh, Contour
from meshlab.operations import insert_contour

# -------------------------------------------------------------------------------- #

def test_insert_contour():
    """
    Test insertion of a contour into a mesh.
    """

    mesh = Mesh(
        vertices_capacity=10,
        cells_capacity=10,
    )

    contour = Contour(
        name="Square",
        capacity=4,
    )

    vertices = np.array([
        [-1.0, -1.0],
        [ 1.0, -1.0],
        [ 1.0,  1.0],
        [-1.0,  1.0],
    ])

    result = insert_contour(
        mesh,
        contour,
        vertices,
    )

    # Function does not return anything
    assert result is None

    # Check number of inserted vertices
    assert mesh.num_vertices == 4

    # Check number of contour indices
    assert contour.num_indices == 4


# -------------------------------------------------------------------------------- #

def test_insert_contour_vertices():
    """
    Test that contour vertices are correctly stored in the mesh.
    """

    mesh = Mesh(10, 10)

    contour = Contour(
        name="Surface",
        capacity=4,
    )

    vertices = np.array([
        [0.0, 0.0],
        [1.0, 0.0],
        [1.0, 1.0],
        [0.0, 1.0],
    ])

    insert_contour(
        mesh,
        contour,
        vertices,
    )

    np.testing.assert_array_equal(
        mesh.vertices[:4],
        vertices,
    )


# -------------------------------------------------------------------------------- #

def test_insert_contour_indices():
    """
    Test that contour indices preserve vertex insertion order.
    """

    mesh = Mesh(10, 10)

    contour = Contour(
        name="Boundary",
        capacity=4,
    )

    vertices = np.array([
        [0.0, 0.0],
        [1.0, 0.0],
        [1.0, 1.0],
        [0.0, 1.0],
    ])

    insert_contour(
        mesh,
        contour,
        vertices,
    )

    np.testing.assert_array_equal(
        contour.indices[:4],
        [0, 1, 2, 3],
    )


# -------------------------------------------------------------------------------- #

def test_insert_contour_with_multiple_calls():
    """
    Test insertion of multiple contours into the same mesh.
    """

    mesh = Mesh(20, 20)

    contour_1 = Contour(
        name="Surface 1",
        capacity=4,
    )

    contour_2 = Contour(
        name="Surface 2",
        capacity=4,
    )

    vertices_1 = np.array([
        [0.0, 0.0],
        [1.0, 0.0],
        [1.0, 1.0],
        [0.0, 1.0],
    ])

    vertices_2 = np.array([
        [2.0, 2.0],
        [3.0, 2.0],
        [3.0, 3.0],
        [2.0, 3.0],
    ])

    insert_contour(mesh, contour_1, vertices_1)
    insert_contour(mesh, contour_2, vertices_2)

    assert mesh.num_vertices == 8

    np.testing.assert_array_equal(
        contour_1.indices[:4],
        [0, 1, 2, 3],
    )

    np.testing.assert_array_equal(
        contour_2.indices[:4],
        [4, 5, 6, 7],
    )

# -------------------------------------------------------------------------------- #
