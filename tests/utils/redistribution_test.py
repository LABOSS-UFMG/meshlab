import numpy as np

from meshlab.utils import (
    redistribute_points, monitor_start, monitor_end, monitor_curvature, monitor_corners,
)


def test_uniform_and_exact_linear_density():
    points = np.array([[0, 0, 0], [1, 0, 0]], dtype=np.float32)
    uniform = redistribute_points(points, 11, kind="linear")
    assert uniform.dtype == np.float32
    np.testing.assert_allclose(uniform[:, 0], np.linspace(0, 1, 11))
    refined = redistribute_points(points, 11, lambda p: 1 + p[:, 0], kind="linear")
    # Integral of 1+x is x+x²/2; equal monitor mass is 1.5*i/10.
    np.testing.assert_allclose(refined[:, 0], np.sqrt(1 + 3*np.linspace(0, 1, 11)) - 1,
                               atol=1e-7)
    np.testing.assert_array_equal(points, [[0, 0, 0], [1, 0, 0]])


def test_integer_coordinates_preserve_fractional_spacing():
    result = redistribute_points([[0, 0], [1, 0]], 5, kind="linear")
    assert result.dtype == np.float64
    np.testing.assert_array_equal(result[:, 0], [0, 0.25, 0.5, 0.75, 1])


def test_combined_endpoint_monitors_and_smoothing():
    points = np.column_stack((np.linspace(0, 1, 101), np.zeros(101)))
    combined = lambda p: monitor_start(p) + monitor_end(p)
    refined = redistribute_points(points, 31, combined, steps=3)
    lengths = np.diff(refined[:, 0])
    assert lengths[0] < lengths[15] and lengths[-1] < lengths[15]
    np.testing.assert_allclose(lengths, lengths[::-1], atol=1e-14)
    spike = lambda p: np.where(np.arange(len(p)) == 50, 100.0, 1.0)
    raw = redistribute_points(points, 101, spike)
    smooth = redistribute_points(points, 101, spike, steps=10)
    assert np.diff(smooth[:, 0]).min() > np.diff(raw[:, 0]).min()
    np.testing.assert_array_equal(refined[[0, -1]], points[[0, -1]])


def test_curvature_and_periodic_closed_curve():
    straight = np.column_stack((np.linspace(0, 1, 10), np.zeros(10)))
    np.testing.assert_array_equal(monitor_curvature(straight), np.ones(10))
    corner = np.array([[0., 0.], [1., 0.], [2., 0.], [2., 1.], [2., 2.]])
    assert np.argmax(monitor_curvature(corner)) == 2
    polygon = np.array([[0., 0.], [2., 0.], [2., 1.], [0., 1.], [0., 0.]])
    weights = monitor_curvature(polygon)
    assert weights[0] == weights[-1]
    refined = redistribute_points(polygon, 21, monitor_curvature, steps=3)
    assert np.all(np.isfinite(refined))
    assert np.all(np.linalg.norm(np.diff(refined, axis=0), axis=1) > 0)
    np.testing.assert_array_equal(refined[[0, -1]], polygon[[0, -1]])


def test_corner_monitor_threshold_and_periodic_neighbors():
    points = np.array([[0., 0., 0.], [2., 0., 0.], [2., 1., 0.], [2., 3., 0.]])
    # A 90-degree turn with a 30-degree threshold gives 1 + 10*(60/150).
    np.testing.assert_allclose(monitor_corners(points), [1, 5, 1, 1])
    np.testing.assert_allclose(monitor_corners(points, min_angle=np.pi/2), 1)
    np.testing.assert_allclose(monitor_corners(points[:2]), [1, 1])
    np.testing.assert_allclose(monitor_corners(points * 7), monitor_corners(points))
    polygon = np.array([[0., 0.], [2., 0.], [2., 1.], [0., 1.], [0., 0.]])
    np.testing.assert_allclose(monitor_corners(polygon), np.full(5, 5.0))
    refined = redistribute_points(points, 31,
                                  lambda p: monitor_corners(p) + monitor_start(p), steps=2)
    assert np.all(np.isfinite(refined))
    np.testing.assert_array_equal(refined[[0, -1]], points[[0, -1]])
