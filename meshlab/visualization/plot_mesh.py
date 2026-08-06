# -------------------------------------------------------------------------------- #
import numpy as np
import matplotlib.pyplot as plt

from meshlab.data.mesh import Mesh
from meshlab.data.contour import Contour

from meshlab.utils import validation

# -------------------------------------------------------------------------------- #
def plot_mesh(
        mesh: Mesh,
        contours: list[Contour] | None = None,
        normals: list[tuple[str, np.ndarray]] | None = None,
    ) -> None:
    """
    Plot the mesh and contours.

    Parameters
    ----------
    mesh : Mesh
        Mesh to be plotted.
    contours : list[Contour] | None, default=None
        List of contours to be highlighted.
    normals : list[np.ndarray] | None, default=None
        List of normals to be plotted. Must be of the same size as contours.
    """
    # ------------------------------------------------------------------------ #
    # Validate arguments
    validation.is_object(mesh, Mesh)

    if not (contours is None):
        validation.is_sequence(contours, None, Contour)

    if not (normals is None):
        if contours is None:
            raise "In order to plot the normals, contours cannot be None."

    # ------------------------------------------------------------------------ #
    _, ax = plt.subplots()

    # ------------------------------------------------------------------------ #
    # Plot cells
    for i in range(mesh.num_cells):

        cell = mesh.cells[i]
        cell = cell[cell >= 0]

        vertices = mesh.vertices[cell]

        x = list(vertices[:, 0]) + [vertices[0, 0]]
        y = list(vertices[:, 1]) + [vertices[0, 1]]

        ax.plot(
            x,
            y,
            color="black",
            linewidth=0.8,
        )

    # ------------------------------------------------------------------------ #
    # Plot contours
    if contours is not None:

        for i, contour in enumerate(contours):

            vertices = mesh.vertices[contour.indices[:contour.num_indices]]

            x = list(vertices[:, 0]) + [vertices[0, 0]]
            y = list(vertices[:, 1]) + [vertices[0, 1]]

            ax.plot(
                x,
                y,
                linewidth=2.5,
                label=contour.name,
            )

            if normals is not None:

                index = None
                for i, (name, _) in enumerate(normals):
                    if name == contour.name:
                        index = i
                        break

                if index is not None:
                    normal = normals[index][1]
                    u = list(normal[:, 0]) + [normal[0, 0]]
                    v = list(normal[:, 1]) + [normal[0, 1]]

                    ax.quiver(
                        x, y,
                        u, v,
                    )
    
    # ------------------------------------------------------------------------ #
    ax.set_aspect("equal", adjustable="datalim")
    ax.autoscale_view()

    if contours:
        ax.legend()

    plt.show()

    # ------------------------------------------------------------------------ #
    return None

# -------------------------------------------------------------------------------- #
