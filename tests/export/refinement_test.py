"""Basic local sizing and export integration checks."""
import gmsh
import numpy as np
import pytest

from meshlab.core import Mesh, Point, Curve, Contour, Refinement
from meshlab.operations import insert_contour
from meshlab.export import export_mesh
from meshlab.export.refinement import build_size_callback


def test_geometry_sizes_and_point_storage():
    coordinates = np.array([0., 0.])
    point = Point('point', coordinates, float_dtype=np.float32)
    coordinates[:] = 10
    np.testing.assert_array_equal(point.coordinates, [0, 0])
    assert point.coordinates.dtype == np.float32
    curve = Curve('line', [[0, 0], [1, 0]])
    contour = Contour('concave', [Curve('outline', [
        [0, 0], [2, 0], [2, 1], [1, 1], [1, 2], [0, 2], [0, 0],
    ])])
    for geometry in [point, curve, contour]:
        callback = build_size_callback([Refinement(geometry, .1, .2, .8)], 0, 1)
        assert callback(2, 1, 0, 0, 0, 1) == pytest.approx(.1)
        assert callback(2, 1, 10, 10, 0, 1) == pytest.approx(1)
    callback = build_size_callback([Refinement(contour, .1, 0, .1)], 0, 1)
    assert callback(2, 1, .5, 1.5, 0, 1) == pytest.approx(.1)
    assert callback(2, 1, 1.5, 1.5, 0, 1) == pytest.approx(1)
    callback = build_size_callback([Refinement(point, .1, .2, .8)], 0, 1)
    assert callback(2, 1, .6, 0, 0, 1) == pytest.approx(.55)
    with pytest.raises(ValueError):
        Refinement(point, .1, transition=0)


@pytest.mark.parametrize('mode', ['planar', 'axisymmetric'])
def test_refined_export_preserves_inputs_and_physical_names(tmp_path, mode):
    mesh = Mesh()
    corners = np.array([[0, 1], [2, 1], [2, 3], [0, 3], [0, 1]])
    curves = [Curve(name, np.linspace(a, b, 9))
              for name, a, b in zip(['lower', 'outlet', 'upper', 'inlet'],
                                    corners[:-1], corners[1:])]
    insert_contour(mesh, Contour('domain', curves))
    original = mesh.points.copy()
    refinement = Refinement(Point('center', [1, 2]), .08, .3, .5)
    axis = Curve('axis', [[0, 0], [2, 0]])
    gmsh.initialize()
    try:
        gmsh.option.setNumber('General.Terminal', 0)
        gmsh.model.add('caller')
        previous_callback = lambda dim, tag, x, y, z, lc: lc
        gmsh.model.mesh.setSizeCallback(previous_callback)
        handle = gmsh.api_callback_
        counts = []
        for name, refinements in [('base', None), ('refined', [refinement])]:
            filename = tmp_path / f'{mode}_{name}.msh'
            export_mesh(mesh, filename=filename, mode=mode, thickness=.1,
                        axis=axis, mesh_size=.3, refinements=refinements)
            assert gmsh.model.getCurrent() == 'caller'
            assert gmsh.api_callback_ is handle
            gmsh.model.add("inspection")
            gmsh.merge(str(filename))
            groups = {gmsh.model.getPhysicalName(dim, tag)
                      for dim, tag in gmsh.model.getPhysicalGroups()}
            caps = {'frontAndBack'} if mode == 'planar' else {'wedge_front', 'wedge_back'}
            assert groups == {'lower', 'outlet', 'upper', 'inlet', 'fluid'} | caps
            _, tags, _ = gmsh.model.mesh.getElements(3)
            counts.append(sum(len(t) for t in tags))
            assert np.min(gmsh.model.mesh.getElementQualities(
                np.concatenate(tags), 'minDetJac')) > 0
            gmsh.model.remove()
            gmsh.model.setCurrent('caller')
        assert counts[1] > 1.5 * counts[0]
        np.testing.assert_array_equal(mesh.points, original)
        assert mesh.num_cells == 0
    finally:
        gmsh.finalize()
