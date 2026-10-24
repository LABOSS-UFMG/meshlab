"""Basic contour assembly and independent front initialization."""
import numpy as np

from meshlab.core import Mesh, Curve, Contour, Front
from meshlab.operations import insert_contour, initialize_front


def test_channel_with_two_independent_fronts():
    channel = Contour('channel', [
        Curve('inlet', [[0, 0], [0, 1]]),
        Curve('upper', [[0, 1], [1, 1], [2, 1]]),
        Curve('outlet', [[2, 1], [2, 0]]),
        Curve('lower', [[2, 0], [0, 0]]),
    ])
    mesh = Mesh(vertices_capacity=1, int_dtype=np.int64)
    insert_contour(mesh, channel)
    assert mesh.num_vertices == 5
    assert mesh.num_cells == 0
    np.testing.assert_array_equal(mesh.points, [[0, 0], [0, 1], [1, 1], [2, 1], [2, 0]])
    for name, expected in [('inlet', [0, 1]), ('upper', [1, 2, 3]),
                           ('outlet', [3, 4]), ('lower', [4, 0])]:
        np.testing.assert_array_equal(mesh.boundaries[name], expected)
        assert mesh.boundaries[name].dtype == mesh.int_dtype

    upper, lower = Front('upper', int_dtype=mesh.int_dtype), Front('lower')
    initialize_front(mesh, upper, curves=['upper'])
    initialize_front(mesh, lower, curves=['lower'])
    np.testing.assert_array_equal(upper.entities.edge, [[1, 2], [2, 3]])
    np.testing.assert_array_equal(lower.entities.edge, [[4, 0]])
    assert upper.entities.edge.dtype == mesh.int_dtype
    assert mesh.num_vertices == 5
    upper.entities.edge[0, 0] = 0
    np.testing.assert_array_equal(mesh.boundaries['upper'], [1, 2, 3])
    np.testing.assert_array_equal(lower.entities.edge, [[4, 0]])

    initialize_front(mesh, upper, curves=['lower', 'inlet'])
    np.testing.assert_array_equal(upper.entities.edge, [[4, 0], [0, 1]])


def test_successive_closed_contours_in_3d():
    mesh = Mesh(dim=3)
    points = [[0, 0, 1], [1, 0, 1], [0, 1, 1], [0, 0, 1]]
    for name in ['first', 'second']:
        insert_contour(mesh, Contour(name, [Curve(name, points)]))
    assert mesh.num_vertices == 6
    assert mesh.num_cells == 0
    np.testing.assert_array_equal(mesh.boundaries['first'], [0, 1, 2, 0])
    np.testing.assert_array_equal(mesh.boundaries['second'], [3, 4, 5, 3])
    assert Mesh().boundaries == {}
    front = Front()
    initialize_front(mesh, front, curves=['second'])
    np.testing.assert_array_equal(front.entities.edge, [[3, 4], [4, 5], [5, 3]])
