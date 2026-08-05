# -------------------------------------------------------------------------------- #
import numpy as np

from typing import Sequence

# -------------------------------------------------------------------------------- #
def create_polygon(
        vertices: Sequence[Sequence[float]],
        points_per_edge: Sequence[int],
    ) -> np.ndarray:
    """
    Create a polygon contour with a specified number of points per edge.

    Parameters
    ----------
    vertices : sequence of sequence of float
        Polygon vertices ordered counter-clockwise.

    points_per_edge : sequence of int
        Number of points generated along each edge.

    Returns
    -------
    ndarray
        Coordinates of the polygon points.
    """

    # ------------------------------------------------------------------------ #
    # Convert input vertices to numpy array
    vertices = np.asarray(vertices, dtype=np.float64)

    # ------------------------------------------------------------------------ #
    # Create list to store generated points
    points = []

    # ------------------------------------------------------------------------ #
    # Generate points along each edge
    num_vertices = len(vertices)

    for i in range(num_vertices):

        # Define edge vertices
        start = vertices[i]
        end = vertices[(i + 1) % num_vertices]

        # Generate points excluding the final vertex to avoid duplication
        alpha = np.linspace(
            0.0,
            1.0,
            points_per_edge[i],
            endpoint=False,
        )

        edge_points = (
            (1.0 - alpha[:, None]) * start
            + alpha[:, None] * end
        )

        points.append(edge_points)

    # ------------------------------------------------------------------------ #
    # Combine all edge points into a single array
    return np.vstack(points)

# -------------------------------------------------------------------------------- #
