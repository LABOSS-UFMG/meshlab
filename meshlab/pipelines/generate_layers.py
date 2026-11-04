# -------------------------------------------------------------------------------- #
from collections.abc import Sequence

from meshlab.core import Front, Mesh
from meshlab.operations import advance_front, collapse_edges, compute_normals, find_short_edges, smooth_normals

# -------------------------------------------------------------------------------- #
def generate_layers(
    mesh: Mesh,
    fronts: Sequence[Front],
    *,
    num_layers: int | list[int],
    first_height: float | list[float],
    growth_rate: float | list[float] = 1.0,
    method: str | list[str] = "central",
    smooth_steps: int | list[int] = 0,
    relaxation: float | list[float] = 0.5,
    min_edge_ratio: float | list[float] = 0.0,
) -> None:
    """Grow quadrilateral layers on initialized planar fronts in place.

    Parameters
    ----------
    mesh : Mesh
        Planar mesh containing the vertices of all supplied fronts.
    fronts : sequence of Front
        Distinct fronts initialized on this mesh, including any endpoint guides.
    num_layers : int or list of int
        Number of layers to add to each front.
    first_height : float or list of float
        Positive displacement along each normal in the first layer.
    growth_rate : float or list of float, default=1.0
        Positive multiplier applied to the height after every layer.
    method : str or list of str, default="central"
        Normal method for each front: "central" or "bisector".
    smooth_steps : int or list of int, default=0
        Number of normal smoothing passes before each advance.
    relaxation : float or list of float, default=0.5
        Smoothing weight in [0, 1].
    min_edge_ratio : float or list of float, default=0.0
        After each advance, attempt to collapse edges shorter than this factor
        times the current layer height. Zero disables the check.

    Notes
    -----
    Each keyword accepts a shared value or a list in the same order and of
    the same length as fronts. Each front stops after its own layer count.
    The caller chooses heights that avoid collisions and preserve cell quality.
    Height is uniform along each front during an advance.

    Raises
    ------
    ValueError
        If a list length differs from the number of fronts or a ratio is invalid.
    """
    # ---------------------------------------------------------------------------- #
    # Helper to convert a shared value or list to a per-front list
    def per_front(value, name):
        if isinstance(value, list):
            if len(value) != len(fronts):
                raise ValueError(f"{name} must have {len(fronts)} entries, got {len(value)}")
            return value.copy()
        return [value] * len(fronts)

    # ---------------------------------------------------------------------------- #
    # Convert all parameters to per-front lists
    counts = per_front(num_layers, "num_layers")
    heights = per_front(first_height, "first_height")
    rates = per_front(growth_rate, "growth_rate")
    methods = per_front(method, "method")
    steps = per_front(smooth_steps, "smooth_steps")
    weights = per_front(relaxation, "relaxation")
    ratios = per_front(min_edge_ratio, "min_edge_ratio")
    
    if any(not 0 <= ratio < float("inf") for ratio in ratios):
        raise ValueError("min_edge_ratio must be finite and nonnegative")

    # ---------------------------------------------------------------------------- #
    # Grow each front in turn, layer by layer
    for layer in range(max(counts, default=0)):
        for i, front in enumerate(fronts):
            if layer >= counts[i]:
                continue
            normals = compute_normals(mesh, front, method=methods[i])
            for _ in range(steps[i]):
                normals, _ = smooth_normals(mesh, front, normals, weights[i])
            advance_front(mesh, front, normals, heights[i])
            if ratios[i] > 0:
                short_edges = find_short_edges(mesh, front, ratios[i] * heights[i])
                if short_edges:
                    # Only the vertices just appended by advance_front can be
                    # merged, so indices on all other fronts remain valid.
                    collapse_edges(mesh, front, short_edges)
            heights[i] *= rates[i]

    # ---------------------------------------------------------------------------- #
    return
