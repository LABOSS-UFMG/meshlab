"""Basic assembly of a closed contour from ordered curves."""
from meshlab.core import Contour, Curve


def test_contour_preserves_curve_order():
    first = Curve('bottom', [[0, 0], [1, 0]])
    second = Curve('remaining', [[1, 0], [0, 1], [0, 0]])
    contour = Contour('body', [first, second], tolerance=1e-8)

    assert contour.name == 'body'
    assert contour.curves == (first, second)
    assert contour.tolerance == 1e-8
