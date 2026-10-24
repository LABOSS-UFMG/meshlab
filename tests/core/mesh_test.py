"""Basic mesh storage and capacity growth in 2D and 3D."""
import numpy as np
import pytest

from meshlab.core import Mesh


@pytest.mark.parametrize('dim, float_dtype, int_dtype', [
    (2, np.float64, np.int32),
    (3, np.float32, np.int64),
])
def test_mesh_storage_and_growth(dim, float_dtype, int_dtype):
    mesh = Mesh(dim=dim, vertices_capacity=1, cells_capacity=1,
                float_dtype=float_dtype, int_dtype=int_dtype)
    points = np.zeros((4, dim))
    points[:, :2] = [[0, 0], [1, 0], [1, 1], [0, 1]]

    assert [mesh.add_vertex(point) for point in points] == [0, 1, 2, 3]
    assert mesh.add_cell('triangle', [0, 1, 2]) == 0
    assert mesh.add_cell('triangle', [0, 2, 3]) == 1
    assert mesh.add_cell('quadrilateral', [0, 1, 2, 3]) == 0

    assert mesh.dim == dim
    assert mesh.num_vertices == 4
    assert mesh.num_cells == 3
    assert mesh.points.dtype == mesh.float_dtype == float_dtype
    assert mesh.cells.triangle.connectivity.dtype == mesh.int_dtype == int_dtype
    assert mesh.cells.quadrilateral.connectivity.dtype == int_dtype
    np.testing.assert_array_equal(mesh.points, points)
    np.testing.assert_array_equal(mesh.cells.triangle.connectivity,
                                  [[0, 1, 2], [0, 2, 3]])
    np.testing.assert_array_equal(mesh.cells.quadrilateral.connectivity,
                                  [[0, 1, 2, 3]])
