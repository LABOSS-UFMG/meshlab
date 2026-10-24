"""Basic angle and smoothing behavior with connectivity-based neighbors."""
import numpy as np

from meshlab.core import Mesh, Curve, Contour, Front, FrontEntities
from meshlab.operations import insert_contour, initialize_front, compute_angles, smooth_normals


def test_l_angles_include_straight_and_reflex_vertices():
    points = [[0, 0], [0, 1], [-0.5, 1], [-0.5, 0], [-0.5, -1], [1, -1], [1, 0], [0, 0]]
    mesh = Mesh(float_dtype=np.float32)
    insert_contour(mesh, Contour('body', [Curve('wall', points)]))
    front = Front()
    initialize_front(mesh, front, curves=['wall'])
    front.entities.edge = front.entities.edge[::-1].copy()
    angles = compute_angles(mesh, front)
    np.testing.assert_allclose(angles, np.array([1, 1, 1, 2, 1, 1, 1]) * np.pi / 2, atol=1e-6)
    assert angles.dtype == np.float32


def test_smoothing_uses_edges_and_returns_signed_rotation():
    mesh = Mesh(float_dtype=np.float32)
    for point in [[0, 0], [2, 0], [1, 0]]:
        mesh.add_vertex(point)
    front = Front(entities=FrontEntities(edge=[[0, 2], [2, 1]]))
    normals = np.array([[1, 0], [1, 0], [0, 1]], dtype=np.float32)
    original = normals.copy()
    smoothed, rotation = smooth_normals(mesh, front, normals, np.array([0.5, 0, 0.5]))
    expected = np.array([[2**-0.5, 2**-0.5], [1, 0], [2**-0.5, 2**-0.5]])
    np.testing.assert_allclose(smoothed, expected, atol=1e-6)
    np.testing.assert_allclose(rotation, [np.pi / 4, 0, -np.pi / 4], atol=1e-6)
    np.testing.assert_array_equal(normals, original)
    assert smoothed.dtype == rotation.dtype == np.float32


def test_open_front_angles_use_neutral_endpoints():
    mesh = Mesh(float_dtype=np.float32)
    for point in [[1, 1], [0, 0], [1, 0]]:
        mesh.add_vertex(point)
    front = Front(entities=FrontEntities(edge=[[2, 0], [1, 2]]))
    angles = compute_angles(mesh, front)
    np.testing.assert_allclose(angles, [np.pi, np.pi, np.pi / 2], atol=1e-6)
    assert angles.dtype == mesh.float_dtype
