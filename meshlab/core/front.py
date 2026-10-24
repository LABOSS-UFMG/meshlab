# -------------------------------------------------------------------------------- #
import numpy as np

from numpy.typing import DTypeLike
from dataclasses import dataclass

from meshlab.utils import validation

# -------------------------------------------------------------------------------- #
@dataclass(slots=True, repr=False, eq=False)
class FrontEntities():
    """Store edge connectivity for attribute access"""
    edge: np.ndarray | None = None

# -------------------------------------------------------------------------------- #
class Front():
    """Store oriented front entities referencing mesh vertices.

    Attributes
    ----------
    name : str
        Front identifier.
    entities : FrontEntities
        Edge connectivity accessed as entities.edge, copied using int_dtype.
    constraints : dict
        Named guide or endpoint constraints interpreted by operations.
    int_dtype : numpy.dtype
        Integer type used for edge connectivity.

    Notes
    -----
    Front stores no mesh reference or spatial dimension. Operations receive
    mesh and front separately and consult mesh.dim when necessary.
    """

    # ---------------------------------------------------------------------------- #
    def __init__(
            self,
            name: str = "front",
            entities: FrontEntities | None = None,
            int_dtype: DTypeLike = np.int32,
        ) -> None:
        """
        Parameters
        ----------
        name : str, default="front"
            Nonempty front identifier.
        entities : FrontEntities, optional
            Edge connectivity with shape (N, 2). Omit for an empty front.
            Edges reference vertex indices, but their existence in a mesh
            is not checked by this independent data container.
        int_dtype : numpy dtype-like, default=numpy.int32
            Connectivity storage type: int32 or int64.
        """
        # ------------------------------------------------------------------------ #
        # Validate constructor arguments
        validation.is_int_dtype(int_dtype)

        # ------------------------------------------------------------------------ #
        # Store constructor arguments
        self._name = name
        self._int_dtype = np.dtype(int_dtype)

        # ------------------------------------------------------------------------ #
        # Copy connectivity and initialize constraints
        edge = (np.empty((0, 2), dtype=int_dtype)
               if entities is None else np.asarray(entities.edge))
        self._entities = FrontEntities(edge=edge.astype(self._int_dtype, copy=True))
        self._constraints = {}

        # ------------------------------------------------------------------------ #
        return None

    # ---------------------------------------------------------------------------- #
    @property
    def name(self) -> str:
        """Identifier associated with this front."""
        return self._name

    @property
    def entities(self) -> FrontEntities:
        """Connectivity container; edits are not validated automatically."""
        return self._entities

    @property
    def constraints(self) -> dict:
        """Writable mapping of constraints interpreted by operations."""
        return self._constraints

    @property
    def int_dtype(self) -> np.dtype:
        """Integer dtype used for connectivity storage."""
        return self._int_dtype

# -------------------------------------------------------------------------------- #
