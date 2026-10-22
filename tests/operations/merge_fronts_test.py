# -------------------------------------------------------------------------------- #
import numpy as np
import pytest

from meshlab.data import Mesh, Contour
from meshlab.operations.find_close_edges import find_close_edges
from meshlab.operations.merge_fronts import merge_fronts


def create_fronts():
    mesh = Mesh()
    front_a, front_b = Contour('a'), Contour('b')
    for front, points in (
        (front_a, [(0, 0), (1, 0), (1, .5), (1, 1), (0, 1)]),
        (front_b, [(1.1, 0), (2.1, 0), (2.1, 1), (1.1, 1), (1.1, .5)]),
    ):
        for point in points:
            front.add_index(mesh.add_vertex(point))
    return mesh, front_a, front_b


@pytest.mark.parametrize('reverse_pairs', [False, True])
@pytest.mark.parametrize('rotate_fronts', [False, True])
def test_merge_creates_one_quad_per_pair(reverse_pairs, rotate_fronts):
    mesh, a, b = create_fronts()
    if rotate_fronts:
        a.indices[:a.num_indices] = np.roll(a.indices[:a.num_indices], 3)
        b.indices[:b.num_indices] = np.roll(b.indices[:b.num_indices], 1)
    pairs = find_close_edges(mesh, a, b, .15)
    assert len(pairs) == 2
    if reverse_pairs:
        pairs.reverse()
    original_vertices = mesh.vertices[:mesh.num_vertices].copy()
    original_a = a.indices[:a.num_indices].copy()
    original_b = b.indices[:b.num_indices].copy()
    merged = merge_fronts(mesh, a, b, pairs)

    assert mesh.num_cells == len(pairs)
    assert np.all(np.sum(mesh.cells[:mesh.num_cells] >= 0, axis=1) == 4)
    assert {tuple(cell) for cell in mesh.cells[:mesh.num_cells]} == {
        (1, 5, 9, 2), (2, 9, 8, 3),
    }
    np.testing.assert_array_equal(mesh.vertices[:mesh.num_vertices], original_vertices)
    np.testing.assert_array_equal(a.indices[:a.num_indices], original_a)
    np.testing.assert_array_equal(b.indices[:b.num_indices], original_b)
    indices = merged.indices[:merged.num_indices]
    assert len(indices) == len(set(indices)) == 8
    boundary = set(zip(indices, np.roll(indices, -1)))
    for pair in pairs:
        assert all(edge not in boundary for edge in pair)
    assert (1, 5) in boundary and (8, 3) in boundary


def test_single_pair_creates_only_one_quad():
    mesh, a, b = create_fronts()
    pairs = [((1, 2), (9, 5))]
    merged = merge_fronts(mesh, a, b, pairs)
    assert merged.num_indices == a.num_indices + b.num_indices
    assert mesh.num_cells == 1
    np.testing.assert_array_equal(mesh.cells[0], [1, 5, 9, 2])


@pytest.mark.parametrize('pairs', [
    [],
    [((1, 2), (9, 5)), ((1, 2), (8, 9))],  # Reused edge.
    [((999, 1000), (9, 5))],               # Unknown edge.
    [((1, 2), (8, 9)), ((2, 3), (9, 5))], # Crossed correspondence.
    [((1, 2), (9, 5)), ((3, 4), (6, 7))], # Invalid bridge.
])
def test_invalid_pairs_leave_mesh_unchanged(pairs):
    mesh, a, b = create_fronts()
    vertices = mesh.vertices[:mesh.num_vertices].copy()
    with pytest.raises(ValueError):
        merge_fronts(mesh, a, b, pairs)
    assert mesh.num_cells == 0
    np.testing.assert_array_equal(mesh.vertices[:mesh.num_vertices], vertices)
