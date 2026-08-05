# -------------------------------------------------------------------------------- #
import numpy as np

from meshlab.operations import smooth_normals

# -------------------------------------------------------------------------------- #

def create_normals():
    """
    Create a simple set of unit normals.
    """

    return np.array([
        [1.0, 0.0],
        [1.0, 0.0],
        [0.0, 1.0],
        [1.0, 0.0],
    ])


# -------------------------------------------------------------------------------- #

def test_smooth_normals_shape():
    """
    Test output dimensions.
    """

    normals = create_normals()

    new_normals, rotation = smooth_normals(
        normals,
    )

    assert new_normals.shape == normals.shape
    assert rotation.shape == (4,)


# -------------------------------------------------------------------------------- #

def test_smooth_normals_are_unit_vectors():
    """
    Test that smoothed normals remain normalized.
    """

    normals = create_normals()

    new_normals, _ = smooth_normals(
        normals,
    )

    lengths = np.linalg.norm(
        new_normals,
        axis=1,
    )

    np.testing.assert_allclose(
        lengths,
        1.0,
    )


# -------------------------------------------------------------------------------- #

def test_smooth_normals_zero_relaxation():
    """
    Test that zero relaxation does not modify the normals.
    """

    normals = create_normals()

    new_normals, rotation = smooth_normals(
        normals,
        relaxation=0.0,
    )

    np.testing.assert_allclose(
        new_normals,
        normals,
    )

    np.testing.assert_allclose(
        rotation,
        0.0,
    )


# -------------------------------------------------------------------------------- #

def test_smooth_normals_scalar_relaxation():
    """
    Test smoothing using a scalar relaxation parameter.
    """

    normals = np.array([
        [1.0, 0.0],
        [0.0, 1.0],
        [1.0, 0.0],
    ])

    new_normals, rotation = smooth_normals(
        normals,
        relaxation=0.5,
    )

    # The central normal should be modified
    assert not np.allclose(
        new_normals[1],
        normals[1],
    )

    # All normals must remain unitary
    np.testing.assert_allclose(
        np.linalg.norm(new_normals, axis=1),
        1.0,
    )


# -------------------------------------------------------------------------------- #

def test_smooth_normals_array_relaxation():
    """
    Test smoothing using one relaxation value per normal.
    """

    normals = create_normals()

    relaxation = np.array([
        0.0,
        0.2,
        0.5,
        1.0,
    ])

    new_normals, _ = smooth_normals(
        normals,
        relaxation=relaxation,
    )

    # First normal is unchanged
    np.testing.assert_allclose(
        new_normals[0],
        normals[0],
    )

    # Other normals are allowed to change
    assert not np.allclose(
        new_normals[2],
        normals[2],
    )


# -------------------------------------------------------------------------------- #

def test_smooth_normals_rotation_angle():
    """
    Test rotation angle consistency.
    """

    normals = np.array([
        [1.0, 0.0],
        [0.0, 1.0],
        [-1.0, 0.0],
    ])

    new_normals, rotation = smooth_normals(
        normals,
        relaxation=0.5,
    )

    for i in range(len(normals)):

        expected = np.arctan2(
            normals[i, 0] * new_normals[i, 1]
            - normals[i, 1] * new_normals[i, 0],

            np.dot(
                normals[i],
                new_normals[i],
            ),
        )

        np.testing.assert_allclose(
            rotation[i],
            expected,
        )

# -------------------------------------------------------------------------------- #
