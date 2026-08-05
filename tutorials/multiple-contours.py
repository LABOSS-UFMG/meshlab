# ==============================================================================
# MeshLab Tutorial
#
# Generate a boundary-layer mesh around a square contour.
# ==============================================================================

# ------------------------------------------------------------------------------
# Packages
import numpy as np

from copy import deepcopy

from meshlab.data import Mesh, Contour
from meshlab.operations import insert_contour, compute_normals, advance_front, smooth_normals
from meshlab.visualization import plot_mesh

from tutorials.helpers.create_polygon import create_polygon

# ------------------------------------------------------------------------------
# Parameters
num_layers = 10
first_layer_height = 0.05
growth_rate = 1.10
points_per_edge = 25

# ------------------------------------------------------------------------------
# Create square contour
vertices = np.array([
    [-1.0, -1.0],
    [ 1.0, -1.0],
    [ 1.0,  1.0],
    [-1.0,  1.0],
])
points_square = create_polygon(vertices, [points_per_edge] * len(vertices))

alpha = np.linspace(0.0, 2.0 * np.pi, 50, endpoint=False)
points_circle = np.column_stack([np.cos(alpha), np.sin(alpha)]) + np.array([4, 2])

# ------------------------------------------------------------------------------
# Initialize mesh and contour
mesh = Mesh( vertices_capacity=5000, cells_capacity=5000)
square = Contour(name="Square", capacity=points_square.shape[0])
circle = Contour(name="Circle", capacity=points_circle.shape[0])

# ------------------------------------------------------------------------------
# Generate boundary-layer mesh

# Insert contour
insert_contour(mesh, square, points_square)
insert_contour(mesh, circle, points_circle)

# Initialize front
front_square = deepcopy(square)
front_square.name = "Front [Square]"

front_circle = deepcopy(circle)
front_circle.name = "Front [Circle]"

# Main loop
height = first_layer_height

for _ in range(num_layers):
    # Square
    normals = compute_normals(mesh, front_square)
    for _ in range(10):
        normals, _ = smooth_normals(normals, 0.5)
    front_square = advance_front(mesh, front_square, normals, height)

    # Circle
    normals = compute_normals(mesh, front_circle)
    front_circle = advance_front(mesh, front_circle, normals, height)

    height *= growth_rate

# ------------------------------------------------------------------------------
# Plot mesh
plot_mesh(mesh, contours=[square, front_square, circle, front_circle])

# ------------------------------------------------------------------------------