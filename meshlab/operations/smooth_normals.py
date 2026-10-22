# -------------------------------------------------------------------------------- #
import numpy as np

from numbers import Number

# -------------------------------------------------------------------------------- #
def smooth_normals(
        normals: np.ndarray,
        relaxation: float | np.ndarray = 0.5,
    ) -> tuple[np.ndarray, np.ndarray]:
    """
    Apply Laplacian smoothing to a set of unit normals.

    Parameters
    ----------
    normals
        Array of shape (N, 2) containing unit normals.
    relaxation
        Relaxation parameter. It may be either a scalar or an array with one
        value per normal. Values should lie in the interval [0, 1].

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        Smoothed unit normals and the rotation angle (radians) applied to each
        normal. Positive angles correspond to counter-clockwise rotation.
    """
    # ------------------------------------------------------------------------ #
    # Allocate memory to new normals and rotation
    num_normals = normals.shape[0]

    if isinstance(relaxation, Number):
        relaxation = np.full(num_normals, relaxation, dtype=np.float64)

    new_normals = np.empty_like(normals)
    rotation = np.empty(num_normals, dtype=np.float64)

    # ------------------------------------------------------------------------ #
    # Smooth normals
    for i in range(num_normals):

        i_prev = (i - 1) % num_normals
        i_next = (i + 1) % num_normals

        alpha = relaxation[i]

        normal = (
            (1.0 - alpha) * normals[i]
            + 0.5 * alpha * (normals[i_prev] + normals[i_next])
        )

        normal /= np.linalg.norm(normal)

        new_normals[i] = normal

        # Signed rotation angle
        cross = (
            normals[i, 0] * normal[1]
            - normals[i, 1] * normal[0]
        )
        dot = np.dot(normals[i], normal)

        rotation[i] = np.arctan2(cross, dot)

    # ------------------------------------------------------------------------ #
    return new_normals, rotation

# -------------------------------------------------------------------------------- #
