"""Basic storage of an independent edge front."""
import numpy as np

from meshlab.core import Front, FrontEntities


def test_empty_front():
    front = Front()

    assert front.entities.edge.shape == (0, 2)
    assert front.entities.edge.dtype == front.int_dtype == np.int32
    assert front.constraints == {}


def test_front_preserves_edges_and_copies_input():
    source = np.array([[0, 1], [1, 2]])
    front = Front('active', FrontEntities(edge=source), int_dtype=np.int64)
    source[:] = 0

    assert front.name == 'active'
    assert front.entities.edge.dtype == front.int_dtype == np.int64
    np.testing.assert_array_equal(front.entities.edge, [[0, 1], [1, 2]])
    front.constraints['guide'] = 'inlet'
    assert front.constraints['guide'] == 'inlet'
