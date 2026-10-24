"""Straight guides keep open layer endpoints on physical boundaries."""
import numpy as np

from meshlab.core import Mesh, Curve, Contour, Front
from meshlab.operations import insert_contour, initialize_front, compute_normals, advance_front


def test_two_wall_fronts_follow_shared_guides():
    mesh = Mesh(vertices_capacity=1, cells_capacity=1)
    channel = Contour('channel', [
        Curve('inlet', [[0, 0], [0, 1]]),
        Curve('upper', [[0, 1], [1, 1], [2, 1]]),
        Curve('outlet', [[2, 1], [2, 0]]),
        Curve('lower', [[2, 0], [1, 0], [0, 0]]),
    ])
    insert_contour(mesh, channel)
    walls = {name: mesh.boundaries[name].copy() for name in ['upper', 'lower']}
    fronts = [Front('upper'), Front('lower')]
    for front, name in zip(fronts, walls):
        initialize_front(mesh, front, curves=[name], guides=['inlet', 'outlet'])
        assert len(front.constraints['guides']) == 2
    for _ in range(3):
        for front in fronts:
            normals = compute_normals(mesh, front)
            # Deliberately tilt directions away from the straight guide.
            normals[:, 0] += 0.2
            normals /= np.linalg.norm(normals, axis=1)[:, None]
            advance_front(mesh, front, normals, 0.05)
            for index, name in front.constraints['guides'].items():
                assert index in front.entities.edge
                assert index in mesh.boundaries[name]
                assert mesh.points[index, 0] == (0 if name == 'inlet' else 2)
    assert mesh.num_cells == 12
    for name, expected in walls.items():
        np.testing.assert_array_equal(mesh.boundaries[name], expected)
    for name in ['inlet', 'outlet']:
        indices = mesh.boundaries[name]
        assert len(indices) == len(np.unique(indices)) == 8
        y = mesh.points[indices, 1]
        assert np.all(np.diff(y) > 0) if name == 'inlet' else np.all(np.diff(y) < 0)
    initialize_front(mesh, fronts[0], curves=['upper'])
    assert fronts[0].constraints['guides'] == {}
