# -------------------------------------------------------------------------------- #
import numpy as np
import pytest

from meshlab.data import Mesh

# -------------------------------------------------------------------------------- #

def test_create_empty_mesh():
    """
    Test mesh initialization.
    """

    mesh = Mesh(
        vertices_capacity=10,
        cells_capacity=10,
    )

    assert mesh.num_vertices == 0
    assert mesh.num_cells == 0

    assert mesh.vertices.shape == (10, 2)
    assert mesh.cells.shape == (10, 4)


# -------------------------------------------------------------------------------- #

def test_add_vertex():
    """
    Test vertex insertion.
    """

    mesh = Mesh(10, 10)

    index = mesh.add_vertex([1.0, 2.0])

    assert index == 0
    assert mesh.num_vertices == 1

    np.testing.assert_array_equal(
        mesh.vertices[0],
        [1.0, 2.0],
    )


# -------------------------------------------------------------------------------- #

def test_add_multiple_vertices():
    """
    Test insertion of multiple vertices.
    """

    mesh = Mesh(10, 10)

    vertices = np.array([
        [0.0, 0.0],
        [1.0, 0.0],
        [1.0, 1.0],
    ])

    for vertex in vertices:
        mesh.add_vertex(vertex)

    assert mesh.num_vertices == 3

    np.testing.assert_array_equal(
        mesh.vertices[:3],
        vertices,
    )


# -------------------------------------------------------------------------------- #

def test_replace_vertex():
    """
    Test replacement of an existing vertex.
    """

    mesh = Mesh(10, 10)

    mesh.add_vertex([0.0, 0.0])

    mesh.replace_vertex(
        0,
        [1.0, 2.0],
    )

    np.testing.assert_array_equal(
        mesh.vertices[0],
        [1.0, 2.0],
    )


# -------------------------------------------------------------------------------- #

def test_replace_invalid_vertex():
    """
    Test replacement with an invalid index.
    """

    mesh = Mesh(10, 10)

    with pytest.raises(ValueError):
        mesh.replace_vertex(
            0,
            [1.0, 2.0],
        )


# -------------------------------------------------------------------------------- #

def test_translate_vertex():
    """
    Test vertex translation.
    """

    mesh = Mesh(10, 10)

    mesh.add_vertex([1.0, 2.0])

    mesh.translate_vertex(
        0,
        [0.5, -1.0],
    )

    np.testing.assert_array_equal(
        mesh.vertices[0],
        [1.5, 1.0],
    )


# -------------------------------------------------------------------------------- #

def test_add_cell():
    """
    Test cell insertion.
    """

    mesh = Mesh(10, 10)

    mesh.add_vertex([0.0, 0.0])
    mesh.add_vertex([1.0, 0.0])
    mesh.add_vertex([0.0, 1.0])

    index = mesh.add_cell([0, 1, 2])

    assert index == 0
    assert mesh.num_cells == 1

    np.testing.assert_array_equal(
        mesh.cells[0, :3],
        [0, 1, 2],
    )


# -------------------------------------------------------------------------------- #

def test_remove_cell():
    """
    Test cell removal.
    """

    mesh = Mesh(10, 10)

    mesh.add_cell([0, 1, 2])
    mesh.add_cell([0, 2, 3])

    mesh.remove_cell(0)

    assert mesh.num_cells == 1

    np.testing.assert_array_equal(
        mesh.cells[0, :4],
        [0, 2, 3, -1],
    )


# -------------------------------------------------------------------------------- #

def test_remove_vertex_without_cells():
    """
    Test vertex removal without connected cells.
    """

    mesh = Mesh(10, 10)

    mesh.add_vertex([0.0, 0.0])
    mesh.add_vertex([1.0, 0.0])
    mesh.add_vertex([2.0, 0.0])

    mesh.remove_vertex(1)

    assert mesh.num_vertices == 2

    np.testing.assert_array_equal(
        mesh.vertices[:2],
        [
            [0.0, 0.0],
            [2.0, 0.0],
        ],
    )


# -------------------------------------------------------------------------------- #

def test_remove_vertex_with_cells():
    """
    Test vertex removal and connectivity update.
    """

    mesh = Mesh(10, 10)

    mesh.add_vertex([0.0, 0.0])
    mesh.add_vertex([1.0, 0.0])
    mesh.add_vertex([0.0, 1.0])
    mesh.add_vertex([1.0, 1.0])

    mesh.add_cell([0, 1, 2])
    mesh.add_cell([1, 3, 2])

    mesh.remove_vertex(1)

    assert mesh.num_vertices == 3

    # Both cells containing vertex 1 must be removed
    assert mesh.num_cells == 0


# -------------------------------------------------------------------------------- #
