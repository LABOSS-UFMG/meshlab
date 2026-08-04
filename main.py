import numpy as np

from copy import deepcopy

from mesh import Mesh
from group import Group

from functions import insert_surface, compute_normals, advance_front, plot_mesh

def rotate(angle, vertices):

    angle = np.deg2rad(angle)

    c = np.cos(angle)
    s = np.sin(angle)

    R = np.array([
        [ c, -s],
        [ s,  c],
    ])

    return vertices @ R.T

if __name__ == "__main__":

    mesh = Mesh(100, 100)
    surface_1 = Group("Surface 1", 100)
    surface_2 = Group("Surface 2", 100)

    vertices_1 = [
        [ 1, 1],
        [ 0, 1],
        [-1, 1],
        [-1, 0],
        [-1,-1],
        [ 0,-1],
        [ 1,-1],
        [ 1, 0],
    ]

    vertices_2 = np.array([
        [ 1, 1],
        [ 0, 1],
        [-1, 1],
        [-1, 0],
        [-1,-1],
        [ 0,-1],
        [ 1,-1],
        [ 1, 0],
    ])
    vertices_2 = rotate(45, vertices_2) + np.array([4, 3])
    vertices_2 = vertices_2.tolist()

    insert_surface(mesh, surface_1, vertices_1)
    insert_surface(mesh, surface_2, vertices_2)

    front_1 = deepcopy(surface_1)
    front_1.name = "Front 1"

    front_2 = deepcopy(surface_2)
    front_2.name = "Front 2"

    for i in range(5):
        normals = compute_normals(mesh, front_1)
        front_1 = advance_front(mesh, front_1, normals, 0.1 + 0.05 * i)

        normals = compute_normals(mesh, front_2)
        front_2 = advance_front(mesh, front_2, normals, 0.1 + 0.05 * i)
    
    plot_mesh(mesh, [surface_1, front_1, surface_2, front_2])