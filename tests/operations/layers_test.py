"""Basic planar normals and quadrilateral layer generation."""
import numpy as np
import pytest

from meshlab.core import Mesh, Curve, Contour, Front, FrontEntities
from meshlab.operations import insert_contour, initialize_front, compute_normals, advance_front


@pytest.mark.parametrize('method', ['central', 'bisector'])
def test_circle_layers(method):
    mesh = Mesh(vertices_capacity=1, cells_capacity=1, float_dtype=np.float32)
    angles = np.linspace(0, 2 * np.pi, 16, endpoint=False)
    points = np.column_stack((np.cos(angles), np.sin(angles)))
    insert_contour(mesh, Contour('body', [Curve('wall', np.vstack((points, points[0])))]))
    front = Front()
    initialize_front(mesh, front, curves=['wall'])
    boundary = mesh.boundaries['wall'].copy()
    for layer in range(2):
        normals = compute_normals(mesh, front, method=method)
        np.testing.assert_allclose(normals, points, atol=1e-6)
        assert normals.dtype == mesh.float_dtype
        assert advance_front(mesh, front, normals, 0.1) is None
        radii = np.linalg.norm(mesh.points[np.unique(front.entities.edge)], axis=1)
        np.testing.assert_allclose(radii, 1 + 0.1 * (layer + 1), atol=1e-6)
    assert mesh.num_vertices == 48
    assert mesh.num_cells == 32
    np.testing.assert_array_equal(mesh.boundaries['wall'], boundary)
    quads = mesh.points[mesh.cells.quadrilateral.connectivity]
    following = np.roll(quads, -1, axis=1)
    area = np.sum(quads[:, :, 0] * following[:, :, 1] - quads[:, :, 1] * following[:, :, 0], axis=1)
    assert np.all(area > 0)


def test_open_front_uses_connectivity_and_per_vertex_heights():
    mesh = Mesh(int_dtype=np.int64)
    for point in [[2, 0], [0, 0], [1, 0]]:
        mesh.add_vertex(point)
    front = Front(entities=FrontEntities(edge=[[2, 0], [1, 2]]), int_dtype=mesh.int_dtype)
    normals = compute_normals(mesh, front)
    np.testing.assert_array_equal(normals, [[0, -1]] * 3)
    advance_front(mesh, front, normals, np.array([0.1, 0.2, 0.3]))
    np.testing.assert_allclose(mesh.points[3:], [[2, -0.1], [0, -0.2], [1, -0.3]])
    np.testing.assert_array_equal(front.entities.edge, [[5, 3], [4, 5]])
    assert front.entities.edge.dtype == np.int64
