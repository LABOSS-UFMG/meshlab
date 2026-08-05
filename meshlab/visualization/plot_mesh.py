# -------------------------------------------------------------------------------- #
import matplotlib.pyplot as plt

from meshlab.data.mesh import Mesh
from meshlab.data.contour import Contour

from meshlab.utils import validation

# -------------------------------------------------------------------------------- #
def plot_mesh(
        mesh: Mesh,
        contours: list[Contour] | None = None,
    ) -> None:
    """
    Plot the mesh and contours.

    Parameters
    ----------
    mesh : Mesh
        Mesh to be plotted.
    contours : list[Contour] | None, default=None
        List of contours to be highlighted.
    """
    # ------------------------------------------------------------------------ #
    # Validate arguments
    validation.is_object(mesh, Mesh)

    if not (contours is None):
        validation.is_sequence(contours, None, Contour)

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

        for contour in contours:

            vertices = mesh.vertices[contour.indices[:contour.num_indices]]

            x = list(vertices[:, 0]) + [vertices[0, 0]]
            y = list(vertices[:, 1]) + [vertices[0, 1]]

            ax.plot(
                x,
                y,
                linewidth=2.5,
                label=contour.name,
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
