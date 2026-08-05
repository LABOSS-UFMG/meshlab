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
from meshlab.operations import insert_contour, compute_normals, advance_front, smooth_normals, compute_angles
from meshlab.visualization import plot_mesh

from tutorials.helpers.create_polygon import create_polygon

# ------------------------------------------------------------------------------
# Parameters
num_layers = 3
first_layer_height = 0.05
growth_rate = 1.10
points_per_edge = 5

# Modifythe parameters below and verify the results!
normal_method = "bisector"  # Change: "central" or "bisector"
correct_height = True       # Change: True or False
smooth = False              # Change: True or False
smooth_steps = 5
relaxation = 0.5

# ------------------------------------------------------------------------------
# Create square contour
vertices = np.array([
        [ 0, 0],
        [ 0, 1],
        [-1, 1],
        [-1,-1],
        [ 1,-1],
        [ 1, 0],
])

points = create_polygon(
    vertices,
    points_per_edge=[points_per_edge] * len(vertices),
)

# ------------------------------------------------------------------------------
# Initialize mesh and contour
mesh = Mesh( vertices_capacity=5000, cells_capacity=5000)
surface = Contour(name="Surface", capacity=points.shape[0])

# ------------------------------------------------------------------------------
# Generate boundary-layer mesh

# Insert contour
insert_contour(mesh, surface, points)

# Initialize front
front = deepcopy(surface)
front.name = "Front"

# Main loop
height = first_layer_height

for layer in range(num_layers):
    normals = compute_normals(mesh, front, method=normal_method)

    if smooth:
        for _ in range(smooth_steps):
            normals, _ = smooth_normals(normals, relaxation)

    if correct_height:
        angles = compute_angles(mesh, front)
        height_array = height / np.sin(angles / 2)
    else:
        height_array = np.full([front.num_indices], height)
    
    front = advance_front(mesh, front, normals, height_array)

    height *= growth_rate

# ------------------------------------------------------------------------------
# Plot mesh
plot_mesh(mesh, contours=[surface, front])

# ------------------------------------------------------------------------------