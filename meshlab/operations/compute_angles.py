# -------------------------------------------------------------------------------- #
import numpy as np

from meshlab.data.mesh import Mesh
from meshlab.data.contour import Contour
from meshlab.utils import validation

# -------------------------------------------------------------------------------- #
def compute_angles(
        mesh: Mesh,
        contour: Contour,
    ) -> np.ndarray:
    """
    Compute the interior angle at each vertex of a closed contour.

    Parameters
    ----------
    mesh : Mesh
        Mesh containing the vertex coordinates.
    contour : Contour
        Closed contour defined by ordered vertex indices.

    Returns
    -------
    np.ndarray
        Interior angles (radians) at each vertex.
    """
    # ------------------------------------------------------------------------ #
    # Validate arguments
    validation.is_object(mesh, Mesh)
    validation.is_object(contour, Contour)

    # ------------------------------------------------------------------------ #
    # Allocate memory to angles
    num_vertices = contour.num_indices

    angles = np.empty(num_vertices, dtype=np.float64)

    # ------------------------------------------------------------------------ #
    # Compute angles
    for i in range(num_vertices):

        i_prev = (i - 1) % num_vertices
        i_next = (i + 1) % num_vertices

        p_prev = mesh.vertices[contour.indices[i_prev]]
        p_curr = mesh.vertices[contour.indices[i]]
        p_next = mesh.vertices[contour.indices[i_next]]

        u = p_prev - p_curr
        v = p_next - p_curr

        u /= np.linalg.norm(u)
        v /= np.linalg.norm(v)

        cos_theta = np.dot(u, v)

        # Evita erros numéricos
        cos_theta = np.clip(cos_theta, -1.0, 1.0)

        angles[i] = np.arccos(cos_theta)

    # ------------------------------------------------------------------------ #
    return angles

# -------------------------------------------------------------------------------- #
