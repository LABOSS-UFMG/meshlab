# -------------------------------------------------------------------------------- #
import numpy as np

from meshlab.data import Contour

# -------------------------------------------------------------------------------- #

def test_create_empty_contour():
    """
    Test contour initialization.
    """

    contour = Contour(
        name="Surface",
        capacity=10,
    )

    assert contour.name == "Surface"
    assert contour.num_indices == 0

    assert contour.indices.shape == (10,)


# -------------------------------------------------------------------------------- #

def test_add_index():
    """
    Test insertion of a vertex index.
    """

    contour = Contour(
        name="Surface",
        capacity=10,
    )

    contour.add_index(5)

    assert contour.num_indices == 1
    assert contour.indices[0] == 5


# -------------------------------------------------------------------------------- #

def test_add_multiple_indices():
    """
    Test insertion of multiple vertex indices.
    """

    contour = Contour(
        name="Boundary",
        capacity=10,
    )

    indices = [3, 7, 2, 1]

    for index in indices:
        contour.add_index(index)

    assert contour.num_indices == 4

    np.testing.assert_array_equal(
        contour.indices[:4],
        indices,
    )


# -------------------------------------------------------------------------------- #

def test_contour_preserves_order():
    """
    Test that indices are stored in insertion order.
    """

    contour = Contour(
        name="Front",
        capacity=5,
    )

    contour.add_index(10)
    contour.add_index(4)
    contour.add_index(8)

    np.testing.assert_array_equal(
        contour.indices[:3],
        [10, 4, 8],
    )

# -------------------------------------------------------------------------------- #
