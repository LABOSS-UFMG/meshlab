# -------------------------------------------------------------------------------- #
import numpy as np
import matplotlib.pyplot as plt

from collections.abc import Sequence
from dataclasses import fields
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from meshlab.core.mesh import Mesh
    from meshlab.core.front import Front

# -------------------------------------------------------------------------------- #
def plot_mesh(
        mesh: "Mesh",
        boundaries: Sequence[str] | None = None,
        show_points: bool = True,
        ax=None,
        show: bool = True,
        normals: Sequence[tuple["Front", np.ndarray]] | None = None,
        normal_scale: float = 0.1,
    ):
    """Plot valid cells and named boundaries in two or three dimensions.

    Parameters
    ----------
    mesh : Mesh
        Mesh containing coordinates, cell blocks and boundary indices.
    boundaries : sequence of str | None, default=None
        Boundary names to display. None selects all registered boundaries;
        an empty sequence displays none. Curves are not closed implicitly.
    show_points : bool, default=True
        Display all mesh vertices as small dots.
    ax : matplotlib axes, optional
        Existing axes compatible with mesh.dim. Omit to create a figure.
    show : bool, default=True
        Call matplotlib.pyplot.show after drawing.
    normals : sequence of (Front, ndarray) | None, default=None
        Fronts and vectors to display. Vector rows follow the ascending unique
        vertex indices of each current front, as returned by compute_normals.
        Recompute vectors after advancing a front. Shape is (N, mesh.dim).
    normal_scale : float, default=0.1
        Multiplier of vector lengths in mesh coordinate units; does not change
        the supplied arrays. A unit normal is drawn with this length.

    Returns
    -------
    figure, axes
        Matplotlib objects for customization or saving.

    Notes
    -----
    Reads valid coordinate and connectivity views without changing the mesh.
    No input checks are performed. In 3D, plots surface cell outlines only.
    """
    # ------------------------------------------------------------------------ #
    # Create axes according to the spatial dimension
    if ax is None:
        figure = plt.figure()
        ax = figure.add_subplot(projection="3d" if mesh.dim == 3 else None)
    else:
        figure = ax.figure

    # ------------------------------------------------------------------------ #
    # Plot the closed outline of each valid cell
    for field in fields(mesh.cells):
        block = getattr(mesh.cells, field.name)
        for indices in block.connectivity:
            points = mesh.points[np.append(indices, indices[0])]
            ax.plot(*points.T, color="black", linewidth=0.8)

    # ------------------------------------------------------------------------ #
    # Plot named boundaries in their stored traversal order
    names = mesh.boundaries if boundaries is None else boundaries
    for name in names:
        points = mesh.points[mesh.boundaries[name]]
        ax.plot(*points.T, linewidth=1.8, label=name)

    # ------------------------------------------------------------------------ #
    # Plot vectors only on the selected fronts using their current vertex IDs
    if normals is not None:
        for front, vectors in normals:
            points = mesh.points[np.unique(front.entities.edge)]
            directions = normal_scale * np.asarray(vectors)
            if mesh.dim == 3:
                ax.quiver(*points.T, *directions.T, normalize=False,
                          label=f"{front.name} normals")
            else:
                ax.quiver(*points.T, *directions.T, angles="xy",
                          scale_units="xy", scale=1.0,
                          label=f"{front.name} normals")

    # ------------------------------------------------------------------------ #
    # Show vertices and configure spatial axes
    if show_points and mesh.num_vertices:
        ax.plot(*mesh.points.T, linestyle="none", marker=".",
                markersize=3, color="black")

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    if mesh.dim == 3:
        ax.set_zlabel("z")
        ax.set_aspect("equal")
    else:
        ax.set_aspect("equal", adjustable="box")
    ax.autoscale_view()
    if len(names) or (normals is not None and len(normals)):
        ax.legend()

    # ------------------------------------------------------------------------ #
    # Display and return the plotting objects
    if show:
        plt.show()

    return figure, ax

# -------------------------------------------------------------------------------- #
