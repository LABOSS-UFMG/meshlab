# ==============================================================================
# MeshLab Tutorial
#
# Generate a boundary-layer mesh around a circular contour.
# ==============================================================================

# ------------------------------------------------------------------------------
# Packages
import numpy as np

from copy import deepcopy

from meshlab.data import Mesh, Contour
from meshlab.operations import insert_contour, compute_normals, advance_front
from meshlab.visualization import plot_mesh

# ------------------------------------------------------------------------------
# Parameters
num_points = 100
num_layers = 10
first_layer_height = 0.02
growth_rate = 1.1

# ------------------------------------------------------------------------------
# Create circular surface
alpha = np.linspace(0.0, 2.0 * np.pi, num_points, endpoint=False)
points = np.column_stack([np.cos(alpha), np.sin(alpha)])

# Initialize mesh and surface
mesh = Mesh(vertices_capacity=5000, cells_capacity=5000)
surface = Contour(name="Surface", capacity=num_points)

# ------------------------------------------------------------------------------
# Generate boundary-layer mesh

# Insert contour
insert_contour(mesh, surface, points)

# Initialize front
front = deepcopy(surface)
front.name = "Front"

# Main loop
height = first_layer_height
for _ in range(num_layers):
    normals = compute_normals(mesh, front)
    front = advance_front(mesh, front, normals, height)
    height *= growth_rate

# Plot mesh
plot_mesh(mesh, contours=[surface, front])

# ------------------------------------------------------------------------------
