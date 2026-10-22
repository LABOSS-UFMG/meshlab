# -------------------------------------------------------------------------------- #
import numpy as np
import pytest

from meshlab.data import Mesh, Contour
from meshlab.operations import collapse_edges, find_short_edges


def create_mesh():
    mesh = Mesh()
    for point in [(0, 0), (.1, 0), (1, 0), (0, 1), (.1, 1), (1, 1), (1, 2), (0, 2)]:
        mesh.add_vertex(point)
    mesh.add_cell([0, 1, 4, 3])
    mesh.add_cell([1, 2, 5, 4])
    front = Contour('Front')
    for index in [3, 4, 5, 6, 7]:
        front.add_index(index)
    return mesh, front


def test_detection_only_and_strict_threshold():
    mesh, front = create_mesh()
    vertices = mesh.vertices[:mesh.num_vertices].copy()
    cells = mesh.cells[:mesh.num_cells].copy()
    assert find_short_edges(mesh, front, .2) == [(3, 4)]
    assert find_short_edges(mesh, front, .1) == []
    np.testing.assert_array_equal(mesh.vertices[:mesh.num_vertices], vertices)
    np.testing.assert_array_equal(mesh.cells[:mesh.num_cells], cells)
    np.testing.assert_array_equal(front.indices[:front.num_indices], [3, 4, 5, 6, 7])


def test_detection_includes_closing_edge_and_sorts_lengths():
    mesh, front = create_mesh()
    front.indices[:front.num_indices] = [4, 5, 6, 7, 3]
    edges = find_short_edges(mesh, front, 1.01)
    assert edges[0] == (3, 4)
    lengths = [np.linalg.norm(mesh.vertices[a] - mesh.vertices[b]) for a, b in edges]
    assert lengths == sorted(lengths)


@pytest.mark.parametrize('reverse_front', [False, True])
def test_collapse_uses_mesh_methods_and_returns_mapping(monkeypatch, reverse_front):
    mesh, front = create_mesh()
    if reverse_front:
        front.indices[:front.num_indices] = front.indices[:front.num_indices][::-1]
    original_front = front.indices[:front.num_indices].copy()
    calls = []
    for name in ('replace_vertex', 'remove_vertex', 'remove_cell', 'add_cell'):
        original = getattr(mesh, name)
        def record(*args, _name=name, _method=original):
            calls.append(_name)
            return _method(*args)
        monkeypatch.setattr(mesh, name, record)
    edges = find_short_edges(mesh, front, .2)
    updated, mapping = collapse_edges(mesh, front, edges)
    assert updated.num_indices == 4
    assert mesh.num_vertices == 7 and mesh.num_cells == 2
    assert mapping[3] == mapping[4]
    np.testing.assert_allclose(mesh.vertices[mapping[3]], [.05, 1])
    np.testing.assert_array_equal(mapping, [0, 1, 2, 3, 3, 4, 5, 6])
    np.testing.assert_array_equal(mesh.cells[0], [0, 1, 3, -1])
    np.testing.assert_array_equal(mesh.cells[1], [1, 2, 4, 3])
    np.testing.assert_array_equal(front.indices[:front.num_indices], original_front)
    assert calls == ['remove_cell', 'remove_cell', 'replace_vertex', 'remove_vertex',
                     'add_cell', 'add_cell']


def test_only_supplied_edges_are_collapsed():
    mesh, front = create_mesh()
    updated, mapping = collapse_edges(mesh, front, [])
    assert updated.num_indices == 5 and mesh.num_vertices == 8
    np.testing.assert_array_equal(mapping, np.arange(8))


def test_shared_endpoints_use_original_indices_after_compaction():
    mesh = Mesh()
    front = Contour('Front')
    for point in [(0, 0), (.1, 0), (.2, 0), (1, 1), (0, 1)]:
        front.add_index(mesh.add_vertex(point))
    updated, mapping = collapse_edges(mesh, front, [(0, 1), (1, 2)])
    assert mesh.num_vertices == updated.num_indices == 3
    np.testing.assert_array_equal(mapping, [0, 0, 0, 1, 2])
    np.testing.assert_allclose(mesh.vertices[0], [.1, 0])


def test_degenerate_triangles_are_removed():
    mesh, front = create_mesh()
    mesh.add_cell([0, 4, 3])
    updated, mapping = collapse_edges(mesh, front, [(3, 4)])
    assert mesh.num_cells == 2
    assert updated.num_indices == 4
    assert np.count_nonzero(mesh.cells[0] >= 0) == 3


def test_invalidating_geometry_is_skipped():
    mesh, front = create_mesh()
    mesh.add_cell([3, 6, 4, 7])
    updated, mapping = collapse_edges(mesh, front, [(3, 4)])
    assert updated.num_indices == 5 and mesh.num_vertices == 8
    np.testing.assert_array_equal(mapping, np.arange(8))


def test_invalid_edge_list_is_rejected_before_modification():
    mesh, front = create_mesh()
    with pytest.raises(ValueError):
        collapse_edges(mesh, front, [(3, 4), (999, 1000)])
    assert mesh.num_vertices == 8 and mesh.num_cells == 2



@pytest.mark.parametrize('edges', [
    [(0, 1), (1, 2), (2, 3)],
    [(2, 3), (0, 1), (1, 2)],
    [(1, 2), (2, 3), (0, 1)],
    [(0, 1), (1, 2), (0, 1), (2, 3)],
])
def test_transitive_group_uses_mean_of_distinct_original_vertices(edges):
    mesh = Mesh()
    front = Contour('Front')
    points = [(0, 0), (.1, 0), (.2, .1), (.3, .1), (1, 1), (0, 1)]
    for point in points:
        front.add_index(mesh.add_vertex(point))
    updated, mapping = collapse_edges(mesh, front, edges)
    assert mesh.num_vertices == updated.num_indices == 3
    np.testing.assert_array_equal(mapping, [0, 0, 0, 0, 1, 2])
    np.testing.assert_allclose(mesh.vertices[0], np.mean(points[:4], axis=0))


def test_group_across_closing_edge():
    mesh = Mesh()
    front = Contour('Front')
    points = [(0, 0), (.1, 0), (1, 0), (1, 1), (0, .1)]
    for point in points:
        front.add_index(mesh.add_vertex(point))
    updated, mapping = collapse_edges(mesh, front, [(4, 0), (0, 1)])
    assert updated.num_indices == 3
    assert mapping[0] == mapping[1] == mapping[4]
    np.testing.assert_allclose(mesh.vertices[mapping[0]], np.mean(np.array(points)[[0, 1, 4]], axis=0))


def test_disconnected_groups_survive_global_reindexing():
    mesh = Mesh()
    front = Contour('Front')
    points = [(0, 0), (.1, 0), (.2, 0), (1, 0), (1, 1), (.9, 1), (0, 1)]
    for point in points:
        front.add_index(mesh.add_vertex(point))
    updated, mapping = collapse_edges(mesh, front, [(4, 5), (1, 2), (0, 1)])
    assert mesh.num_vertices == updated.num_indices == 4
    assert mapping[0] == mapping[1] == mapping[2]
    assert mapping[4] == mapping[5] != mapping[0]
    np.testing.assert_allclose(mesh.vertices[mapping[0]], [.1, 0])
    np.testing.assert_allclose(mesh.vertices[mapping[4]], [.95, 1])


def test_group_updates_all_incident_cells_together():
    mesh, front = create_mesh()
    updated, mapping = collapse_edges(mesh, front, [(4, 5), (3, 4)])
    assert updated.num_indices == 3
    assert mesh.num_vertices == 6 and mesh.num_cells == 2
    assert mapping[3] == mapping[4] == mapping[5]
    np.testing.assert_allclose(mesh.vertices[mapping[3]], [1.1 / 3, 1])
    np.testing.assert_array_equal(mesh.cells[0], [0, 1, 3, -1])
    np.testing.assert_array_equal(mesh.cells[1], [1, 2, 3, -1])


def test_invalid_group_is_not_partially_collapsed():
    mesh, front = create_mesh()
    mesh.add_cell([3, 6, 4, 7])
    vertices = mesh.vertices[:mesh.num_vertices].copy()
    cells = mesh.cells[:mesh.num_cells].copy()
    updated, mapping = collapse_edges(mesh, front, [(3, 4), (4, 5)])
    assert updated.num_indices == 5
    np.testing.assert_array_equal(mapping, np.arange(8))
    np.testing.assert_array_equal(mesh.vertices[:mesh.num_vertices], vertices)
    np.testing.assert_array_equal(mesh.cells[:mesh.num_cells], cells)


@pytest.mark.parametrize('edges', [[(0, 1), (1, 2)], [(0, 1), (1, 2), (2, 3), (3, 0)]])
def test_group_leaving_fewer_than_three_vertices_is_skipped_entirely(edges):
    mesh = Mesh()
    front = Contour('Front')
    points = np.array([(0, 0), (.1, 0), (.2, 0), (0, 1)])
    for point in points:
        front.add_index(mesh.add_vertex(point))
    updated, mapping = collapse_edges(mesh, front, edges)
    assert mesh.num_vertices == updated.num_indices == 4
    np.testing.assert_array_equal(mapping, np.arange(4))
    np.testing.assert_array_equal(mesh.vertices[:4], points)
