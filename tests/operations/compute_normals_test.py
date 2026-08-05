# -------------------------------------------------------------------------------- #
import numpy as np
import pytest

from meshlab.data import Mesh, Contour
from meshlab.operations import compute_normals

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

def test_compute_normals_shape():
    """
    Test output size.
    """

    mesh, contour = create_square()

    normals = compute_normals(
        mesh,
        contour,
    )

    assert normals.shape == (4, 2)


# -------------------------------------------------------------------------------- #

def test_compute_normals_are_unit_vectors():
    """
    Test that all normals are normalized.
    """

    mesh, contour = create_square()

    normals = compute_normals(
        mesh,
        contour,
    )

    lengths = np.linalg.norm(
        normals,
        axis=1,
    )

    np.testing.assert_allclose(
        lengths,
        1.0,
    )


# -------------------------------------------------------------------------------- #

def test_compute_normals_square_direction():
    """
    Test outward normal direction for a square.

    The contour is counter-clockwise, therefore normals must point outward.
    """

    mesh, contour = create_square()

    normals = compute_normals(
        mesh,
        contour,
        method="bisector",
    )

    expected = np.array([
        [-1.0, -1.0],
        [ 1.0, -1.0],
        [ 1.0,  1.0],
        [-1.0,  1.0],
    ])

    expected /= np.linalg.norm(
        expected,
        axis=1,
    )[:, None]

    np.testing.assert_allclose(
        normals,
        expected,
    )


# -------------------------------------------------------------------------------- #

def test_compute_normals_methods():
    """
    Test that both normal computation methods are available.
    """

    mesh, contour = create_square()

    normals_central = compute_normals(
        mesh,
        contour,
        method="central",
    )

    normals_bisector = compute_normals(
        mesh,
        contour,
        method="bisector",
    )

    assert normals_central.shape == normals_bisector.shape

    np.testing.assert_allclose(
        np.linalg.norm(normals_central, axis=1),
        1.0,
    )

    np.testing.assert_allclose(
        np.linalg.norm(normals_bisector, axis=1),
        1.0,
    )


# -------------------------------------------------------------------------------- #

def test_compute_normals_invalid_method():
    """
    Test invalid normal computation method.
    """

    mesh, contour = create_square()

    with pytest.raises(ValueError):

        compute_normals(
            mesh,
            contour,
            method="invalid",
        )

# -------------------------------------------------------------------------------- #
