"""Geometry and failure contracts for the rounded cut."""
import numpy as np
import pytest

from meshlab.core import Curve
from meshlab.operations import split_curve


def area(points):
    return .5 * np.sum(points[:-1, 0]*points[1:, 1] - points[:-1, 1]*points[1:, 0])


@pytest.mark.parametrize('reverse', [False, True])
def test_split_preserves_surface_orientation_and_shared_arc(reverse):
    points = np.array([[0, 0], [1, 0], [2, 0], [2, 1], [2, 2], [0, 2], [0, 0]], dtype=float)
    if reverse:
        points = points[::-1]
    curve = Curve('body', points)
    a = np.flatnonzero(np.all(points[:-1] == [2, 1], axis=1))[0]
    b = np.flatnonzero(np.all(points[:-1] == [1, 0], axis=1))[0]
    first, second = split_curve(curve, a, b, [-3, 0], [0, 2], .2)
    np.testing.assert_array_equal(curve.points, points)
    assert first.name == 'body_1' and second.name == 'body_2'
    assert area(first.points)*area(points) > 0 and area(second.points)*area(points) > 0
    assert area(first.points)+area(second.points) == pytest.approx(area(points))
    for result in (first, second):
        np.testing.assert_array_equal(result.points[0], result.points[-1])
        assert np.all(np.linalg.norm(np.diff(result.points, axis=0), axis=1) > 0)
    center = np.array([1.2, .8])
    for tangent in ([1.2, 1], [1, .8]):
        assert np.min(np.linalg.norm(first.points-tangent, axis=1)) < 1e-12
    cut = np.array([p for p in first.points[:-1] if not np.any(np.all(points[:-1] == p, axis=1))])
    assert np.allclose(np.linalg.norm(cut-center, axis=1), .2)
    for point in cut:
        assert np.min(np.linalg.norm(second.points-point, axis=1)) < 1e-12


def test_rejects_nonfitting_or_parallel_rays():
    curve = Curve('body', [[0, 0], [1, 0], [2, 0], [2, 1], [2, 2], [0, 2], [0, 0]])
    for start, end, radius in [([-1, 0], [0, 1], 2), ([1, 0], [0, 1], .2), ([-1, 0], [-1, 0], .2)]:
        with pytest.raises(ValueError):
            split_curve(curve, 3, 1, start, end, radius)
