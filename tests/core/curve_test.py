"""Basic storage of ordered curve points."""
import numpy as np

from meshlab.core import Curve


def test_curve_preserves_points_and_copies_input():
    source = np.array([[0., 0.], [1., 0.], [1., 1.]])
    curve = Curve('wall', source, float_dtype=np.float32)
    source[:] = -1

    assert curve.name == 'wall'
    assert curve.points.dtype == curve.float_dtype == np.float32
    np.testing.assert_array_equal(curve.points, [[0, 0], [1, 0], [1, 1]])
