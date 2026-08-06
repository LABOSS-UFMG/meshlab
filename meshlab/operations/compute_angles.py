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
    Compute the exterior angle at each vertex of a closed contour.

    Parameters
    ----------
    mesh : Mesh
        Mesh containing the vertex coordinates.

    contour : Contour
        Closed contour defined by ordered vertex indices in counter-clockwise
        orientation.

    Returns
    -------
    np.ndarray
        Exterior angles (radians) in the interval [0, 2*pi].
    """
    # ------------------------------------------------------------------------ #
    # Validate arguments
    validation.is_object(mesh, Mesh)
    validation.is_object(contour, Contour)

    # ------------------------------------------------------------------------ #
    # Allocate memory
    num_vertices = contour.num_indices

    angles = np.empty(num_vertices, dtype=np.float64)

    # ------------------------------------------------------------------------ #
    # Compute exterior angles
    for i in range(num_vertices):

        i_prev = (i - 1) % num_vertices
        i_next = (i + 1) % num_vertices

        p_prev = mesh.vertices[contour.indices[i_prev]]
        p_curr = mesh.vertices[contour.indices[i]]
        p_next = mesh.vertices[contour.indices[i_next]]

        # Compute the two contour edges
        e_prev = p_prev - p_curr
        e_next = p_next - p_curr

        e_prev /= np.linalg.norm(e_prev)
        e_next /= np.linalg.norm(e_next)

        # Compute the angle
        dot = np.dot(e_prev, e_next)
        angle = np.arccos(dot)
        
        angles[i] = angle

    # ------------------------------------------------------------------------ #
    return angles

# -------------------------------------------------------------------------------- #
