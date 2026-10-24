"""Local collapse, rejection and continuation with the current core."""
from copy import deepcopy

import numpy as np

from meshlab.core import Mesh, Front, FrontEntities, Curve, Contour
from meshlab.operations import (
    find_short_edges, collapse_edges, insert_contour, initialize_front,
    compute_normals, compute_angles, advance_front,
)


def test_short_edges_and_quad_to_triangle():
    mesh = Mesh(int_dtype=np.int64)
    for point in [[0, 0], [.2, 0], [1, 1], [0, 1], [4, 0], [4, 1]]:
        mesh.add_vertex(point)
    mesh.add_cell('quadrilateral', [0, 1, 2, 3])
    mesh.boundaries['other'] = np.array([4, 5], dtype=mesh.int_dtype)
    front = Front(entities=FrontEntities(np.array([[0, 1], [1, 2], [2, 3], [3, 0]])))
    assert find_short_edges(mesh, front, .2) == []
    assert find_short_edges(mesh, front, 1.01) == [(0, 1), (2, 3), (3, 0)]
    mapping = collapse_edges(mesh, front, [(0, 1)])
    np.testing.assert_array_equal(mapping, [0, 0, 1, 2, 3, 4])
    assert mapping.dtype == np.int64
    np.testing.assert_allclose(mesh.points[0], [.1, 0])
    np.testing.assert_array_equal(mesh.boundaries['other'], [3, 4])
    assert mesh.cells.quadrilateral.num_cells == 0
    assert mesh.cells.triangle.num_cells == 1
    assert len(front.entities.edge) == 3
    # A closed front must retain at least three vertices.
    np.testing.assert_array_equal(collapse_edges(mesh, front, [(0, 1)]), np.arange(5))


def test_inversion_and_protected_vertices_are_not_collapsed():
    mesh = Mesh()
    for point in [[0, 0], [.2, 0], [1, 1], [0, 1], [.05, -.1], [.05, .1]]:
        mesh.add_vertex(point)
    mesh.add_cell('quadrilateral', [0, 1, 2, 3])
    mesh.add_cell('triangle', [0, 4, 5])
    front = Front(entities=FrontEntities(np.array([[0, 1], [1, 2], [2, 3], [3, 0]])))
    before = mesh.points.copy()
    np.testing.assert_array_equal(collapse_edges(mesh, front, [(0, 1)]), np.arange(6))
    np.testing.assert_array_equal(mesh.points, before)
    mesh.boundaries['wall'] = np.array([2, 3])
    np.testing.assert_array_equal(collapse_edges(mesh, front, [(2, 3)]), np.arange(6))


def test_connected_group_across_closing_edge_is_order_independent():
    mesh = Mesh()
    for angle in np.linspace(0, 2*np.pi, 5, endpoint=False):
        mesh.add_vertex([np.cos(angle), np.sin(angle)])
    front = Front(entities=FrontEntities(np.column_stack((np.arange(5), np.roll(np.arange(5), -1)))))
    other_mesh, other_front = deepcopy(mesh), deepcopy(front)
    original = mesh.points.copy()
    mapping = collapse_edges(mesh, front, [(4, 0), (0, 1)])
    other_map = collapse_edges(other_mesh, other_front, [(0, 1), (4, 0)])
    np.testing.assert_array_equal(mapping, other_map)
    np.testing.assert_allclose(mesh.points, other_mesh.points)
    np.testing.assert_allclose(mesh.points[mapping[0]], original[[4, 0, 1]].mean(axis=0))
    assert len(front.entities.edge) == 3


def test_legacy_l_geometry_continues_after_collapses():
    corners = np.array([[0, 0], [0, 1], [-.5, 1], [-.5, -1], [1, -1], [1, 0]])
    points = np.vstack([np.linspace(a, b, 5, endpoint=False)
                        for a, b in zip(corners, np.roll(corners, -1, axis=0))])
    mesh = Mesh()
    insert_contour(mesh, Contour('body', [Curve('wall', np.vstack((points, points[0])))]))
    front = Front()
    initialize_front(mesh, front, ['wall'])
    wall = mesh.points[mesh.boundaries['wall']].copy()
    collapsed = 0
    h = .04
    for _ in range(10):
        normals = compute_normals(mesh, front, method='bisector')
        advance_front(mesh, front, normals, h / np.sin(compute_angles(mesh, front) / 2))
        previous = mesh.num_vertices
        collapse_edges(mesh, front, find_short_edges(mesh, front, 1.5*h))
        collapsed += previous - mesh.num_vertices
        h *= 1.1
    assert collapsed > 0
    assert mesh.cells.triangle.num_cells > 0
    np.testing.assert_array_equal(mesh.points[mesh.boundaries['wall']], wall)
    for block in (mesh.cells.triangle, mesh.cells.quadrilateral):
        polygon = mesh.points[block.connectivity]
        directions = np.roll(polygon, -1, axis=1) - polygon
        following = np.roll(directions, -1, axis=1)
        cross = directions[:, :, 0]*following[:, :, 1] - directions[:, :, 1]*following[:, :, 0]
        assert np.all(cross > 0)


def test_open_front_remaps_guides_and_removes_reduced_triangles():
    mesh = Mesh()
    for point in [[0, 0], [.1, 0], [.2, 0], [1, 0], [.15, -.1]]:
        mesh.add_vertex(point)
    mesh.add_cell('triangle', [1, 4, 2])
    mesh.boundaries['guide'] = np.array([3, 4])
    front = Front(entities=FrontEntities(np.array([[0, 1], [1, 2], [2, 3]])))
    front.constraints['guides'] = {3: 'guide'}
    assert find_short_edges(mesh, front, .15) == [(0, 1), (1, 2)]
    mapping = collapse_edges(mesh, front, [(1, 2)])
    np.testing.assert_array_equal(mapping, [0, 1, 1, 2, 3])
    np.testing.assert_array_equal(front.entities.edge, [[0, 1], [1, 2]])
    assert front.constraints['guides'] == {2: 'guide'}
    assert mesh.num_cells == 0
