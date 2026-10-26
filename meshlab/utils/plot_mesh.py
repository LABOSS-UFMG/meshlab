# -------------------------------------------------------------------------------- #
from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

from collections.abc import Sequence
from collections import Counter
from dataclasses import fields
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from meshlab.core.mesh import Mesh
    from meshlab.core.front import Front

# -------------------------------------------------------------------------------- #
def plot_mesh(
        mesh: Mesh,
        boundaries: Sequence[str] | None = None,
        show_points: bool = True,
        ax=None,
        show: bool = True,
        normals: Sequence[tuple[Front, np.ndarray]] | None = None,
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
        the supplied arrays. A unit normal is drawn with this length. In 2D,
        shaft width is fixed at 0.8 points and head width is three times the
        shaft width. Automatic limits include the arrows.

    Returns
    -------
    figure, axes
        Matplotlib objects for customization or saving.

    Notes
    -----
    Reads valid coordinate and connectivity views without changing the mesh.
    Cell outlines are gray. Singly incident edges outside the registered
    physical boundaries are drawn in black as the exposed layer front.
    Named boundaries retain their independent colors. No Front is required
    for this topological outline; it does not identify active/inactive edges.
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
    # Plot gray cell outlines and count undirected edge incidences
    edge_counts = Counter()
    for field in fields(mesh.cells):
        block = getattr(mesh.cells, field.name)
        for indices in block.connectivity:
            points = mesh.points[np.append(indices, indices[0])]
            ax.plot(*points.T, color="dimgrey", linewidth=0.8, zorder=1)
            edge_counts.update(tuple(sorted((int(a), int(b))))
                               for a, b in zip(indices, np.roll(indices, -1)))

    # ------------------------------------------------------------------------ #
    # Highlight exposed layer edges without recoloring physical boundaries
    physical_edges = {tuple(sorted((int(a), int(b))))
                      for indices in mesh.boundaries.values()
                      for a, b in zip(indices[:-1], indices[1:])}
    for edge, count in edge_counts.items():
        if count == 1 and edge not in physical_edges:
            points = mesh.points[list(edge)]
            ax.plot(*points.T, color="black", linewidth=0.8, zorder=2)

    # ------------------------------------------------------------------------ #
    # Plot named boundaries in their stored traversal order
    names = mesh.boundaries if boundaries is None else boundaries
    for name in names:
        points = mesh.points[mesh.boundaries[name]]
        ax.plot(*points.T, linewidth=1.8, label=name, zorder=3)

    # ------------------------------------------------------------------------ #
    # Plot vectors only on the selected fronts using their current vertex IDs
    if normals is not None:
        for front, vectors in normals:
            points = mesh.points[np.unique(front.entities.edge)]
            directions = normal_scale * np.asarray(vectors)
            if not len(points):
                continue
            length = np.max(np.linalg.norm(directions, axis=1))
            if length == 0:
                continue
            tips = points + directions
            if mesh.dim == 3:
                ax.quiver(*points.T, *directions.T, normalize=False, linewidth=0.8,
                          label=f"{front.name} normals")
                # Bound the tips and the default 30%-length arrow heads.
                bounds = np.vstack((points, tips))
                bounds = np.vstack((bounds.min(axis=0) - 0.3 * length,
                                    bounds.max(axis=0) + 0.3 * length))
                ax.auto_scale_xyz(*bounds.T, had_data=True)
            else:
                # Match the mesh lines: 0.8 typographic points, independent of length.
                width = 0.8 / 72.0
                ax.quiver(*points.T, *directions.T, angles="xy",
                          scale_units="xy", units="inches", scale=1.0,
                          width=width, headwidth=3, headlength=4,
                          headaxislength=3.5, minlength=0,
                          label=f"{front.name} normals")
                # Quiver's automatic bounds otherwise include only origins.
                bounds = np.vstack((points, tips))
                padding = 0.03 * length
                ax.update_datalim(np.vstack((bounds.min(axis=0) - padding,
                                            bounds.max(axis=0) + padding)))

    # ------------------------------------------------------------------------ #
    # Show vertices and configure spatial axes
    if show_points and mesh.num_vertices:
        ax.plot(*mesh.points.T, linestyle="none", marker=".",
                markersize=3, color="0.65", zorder=1)

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
