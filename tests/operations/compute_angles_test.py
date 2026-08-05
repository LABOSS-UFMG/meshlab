# -------------------------------------------------------------------------------- #
import numpy as np

from meshlab.data import Mesh, Contour
from meshlab.operations import compute_angles

# -------------------------------------------------------------------------------- #

def create_square():
    """
    Create a square mesh and contour.
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

    for vertex in vertices:
        contour.add_index(
            mesh.add_vertex(vertex)
        )

    return mesh, contour


# -------------------------------------------------------------------------------- #

def create_equilateral_triangle():
    """
    Create an equilateral triangle mesh and contour.
    """

    mesh = Mesh(
        vertices_capacity=10,
        cells_capacity=10,
    )

    contour = Contour(
        name="Triangle",
        capacity=3,
    )

    vertices = np.array([
        [0.0, np.sqrt(3.0) / 2.0],
        [-0.5, 0.0],
        [0.5, 0.0],
    ])

    for vertex in vertices:
        contour.add_index(
            mesh.add_vertex(vertex)
        )

    return mesh, contour


# -------------------------------------------------------------------------------- #

def test_compute_angles_shape():
    """
    Test output size.
    """

    mesh, contour = create_square()

    angles = compute_angles(
        mesh,
        contour,
    )

    assert angles.shape == (4,)


# -------------------------------------------------------------------------------- #

def test_compute_angles_square():
    """
    Test interior angles of a square.

    All angles must be 90 degrees.
    """

    mesh, contour = create_square()

    angles = compute_angles(
        mesh,
        contour,
    )

    np.testing.assert_allclose(
        angles,
        np.pi / 2.0,
    )


# -------------------------------------------------------------------------------- #

def test_compute_angles_equilateral_triangle():
    """
    Test interior angles of an equilateral triangle.

    All angles must be 60 degrees.
    """

    mesh, contour = create_equilateral_triangle()

    angles = compute_angles(
        mesh,
        contour,
    )

    np.testing.assert_allclose(
        angles,
        np.pi / 3.0,
    )


# -------------------------------------------------------------------------------- #

def test_compute_angles_are_positive():
    """
    Test that all angles are positive.
    """

    mesh, contour = create_square()

    angles = compute_angles(
        mesh,
        contour,
    )

    assert np.all(
        angles > 0.0
    )


# -------------------------------------------------------------------------------- #

def test_compute_angles_sum_square():
    """
    Test the sum of interior angles of a polygon.

    For a quadrilateral:
        sum(theta) = 2*pi
    """

    mesh, contour = create_square()

    angles = compute_angles(
        mesh,
        contour,
    )

    np.testing.assert_allclose(
        np.sum(angles),
        2.0 * np.pi,
    )

# -------------------------------------------------------------------------------- #
