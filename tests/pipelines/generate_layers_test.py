import numpy as np
import pytest

from meshlab.core import Front, FrontEntities, Mesh
from meshlab.pipelines import generate_layers


def make_front(mesh, x):
    ids = [mesh.add_vertex(p) for p in [(x, 0), (x + 2, 0), (x + 2, 1)]]
    return Front(entities=FrontEntities(edge=list(zip(ids, ids[1:]))))


def test_per_front_settings_match_separate_scalar_calls():
    mesh = Mesh()
    fronts = [make_front(mesh, x) for x in (0, 10)]
    settings = dict(num_layers=[1, 3], first_height=[0.1, 0.2], growth_rate=1.2,
                    method=["central", "bisector"], smooth_steps=[0, 2],
                    relaxation=[0.5, 0.8])
    generate_layers(mesh, fronts, **settings)
    assert mesh.num_cells == 8
    assert settings["first_height"] == [0.1, 0.2]
    for i, front in enumerate(fronts):
        single = Mesh()
        reference = make_front(single, 10 * i)
        generate_layers(single, [reference], **{
            key: value[i] if isinstance(value, list) else value
            for key, value in settings.items()
        })
        np.testing.assert_allclose(mesh.points[front.entities.edge],
                                   single.points[reference.entities.edge])


@pytest.mark.parametrize("name", ["num_layers", "first_height", "growth_rate", "method",
                                  "smooth_steps", "relaxation", "min_edge_ratio"])
def test_length_mismatch_is_rejected_before_advancing(name):
    mesh = Mesh()
    fronts = [make_front(mesh, x) for x in (0, 10)]
    settings = dict(num_layers=2, first_height=0.1)
    settings[name] = []
    with pytest.raises(ValueError, match=name):
        generate_layers(mesh, fronts, **settings)
    assert mesh.num_cells == 0
    assert mesh.num_vertices == 6


def test_short_edge_collapse_is_optional_per_front():
    mesh = Mesh()
    fronts = []
    for x in (0, 10):
        ids = [mesh.add_vertex((x + dx, 0)) for dx in (0, 0.04, 1)]
        fronts.append(Front(entities=FrontEntities(edge=list(zip(ids, ids[1:])))))

    generate_layers(mesh, fronts, num_layers=[1, 2], first_height=0.1,
                    min_edge_ratio=[0.0, 0.5])

    assert mesh.cells.triangle.num_cells == 1
    assert [len(front.entities.edge) for front in fronts] == [2, 1]
    for front, y in zip(fronts, [-0.1, -0.2]):
        np.testing.assert_allclose(mesh.points[front.entities.edge, 1], y)
