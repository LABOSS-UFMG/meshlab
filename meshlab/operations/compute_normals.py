# -------------------------------------------------------------------------------- #
import numpy as np

from meshlab.data.mesh import Mesh
from meshlab.data.contour import Contour

# -------------------------------------------------------------------------------- #
def compute_normals(
        mesh: Mesh,
        front: Contour,
        method: str = "central",
    ) -> np.ndarray:
    """
    Compute outward unit normals at the vertices of a closed contour.

    Parameters
    ----------
    mesh : Mesh
        Mesh containing the vertex coordinates.

    front : Contour
        Closed contour defined by ordered vertex indices in counter-clockwise
        orientation.

    method : str
        Method used to compute the vertex tangent direction:

        - ``"central"``: computes the tangent using the vector connecting the
          previous and next vertices.
        - ``"bisector"``: computes the tangent as the angle bisector between
          the two adjacent edges.

        Default: ``"central"``.

    Returns
    -------
    np.ndarray
        Array of shape (N, 2) containing one unit normal per vertex.
    """
    # ------------------------------------------------------------------------ #
    # Allocate memory for normal vectors
    num_vertices = front.num_indices

    normals = np.empty((num_vertices, 2), dtype=np.float64)

    # ------------------------------------------------------------------------ #
    # Compute normals
    for i in range(num_vertices):

        i_prev = (i - 1) % num_vertices
        i_next = (i + 1) % num_vertices

        p_prev = mesh.vertices[front.indices[i_prev]]
        p_curr = mesh.vertices[front.indices[i]]
        p_next = mesh.vertices[front.indices[i_next]]

        # Compute tangent direction
        if method == "central":

            tangent = p_next - p_prev
            tangent /= np.linalg.norm(tangent)

        elif method == "bisector":

            t_prev = p_curr - p_prev
            t_prev /= np.linalg.norm(t_prev)

            t_next = p_next - p_curr
            t_next /= np.linalg.norm(t_next)

            tangent = t_prev + t_next
            tangent /= np.linalg.norm(tangent)

        else:
            raise ValueError(
                f"Unknown normal computation method: '{method}'."
            )

        # Rotate tangent by 90 degrees to obtain outward normal
        normals[i, 0] = tangent[1]
        normals[i, 1] = -tangent[0]

    # ------------------------------------------------------------------------ #
    return normals

# -------------------------------------------------------------------------------- #
