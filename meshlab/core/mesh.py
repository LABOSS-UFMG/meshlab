# -------------------------------------------------------------------------------- #
import math
import numpy as np

from collections.abc import Sequence
from numpy.typing import DTypeLike
from dataclasses import dataclass, fields

from meshlab.utils import validation

# -------------------------------------------------------------------------------- #
class CellBlock():
    """Store fixed-width connectivity with reserved capacity.

    Atributes
    ---------
    connectivity : ndarray
        Writable view of valid rows; reacquire it after storage growth.
    num_cells : int
        Number of populated rows.
    """

    # ---------------------------------------------------------------------------- #
    def __init__(
            self,
            vertices_per_cell: int,
            capacity: int = 1000,
            increase_ratio: float = 1.5,
            int_dtype: DTypeLike = np.int32,
        ) -> None:
        """
        Parameters
        ----------
        vertices_per_cell : int
            Number of vertex indices per cell, not the spatial dimension.
        capacity : int, default=1000
            Initial number of reserved rows.
        increase_ratio : float, default=1.5
            Capacity growth factor, finite and greater than one.
        int_dtype : numpy dtype-like, default=numpy.int32
            Connectivity type: int32 or int64.
        """
        # ------------------------------------------------------------------------ #
        # Validate input arguments
        validation.is_positive_int(vertices_per_cell, "vertices_per_cell")
        validation.is_positive_int(capacity, "capacity")
        validation.is_positive_float(increase_ratio, "increase_ratio")
        validation.is_int_dtype(int_dtype)

        # ------------------------------------------------------------------------ #
        # Store constructor arguments
        self._vertices_per_cell = vertices_per_cell
        self._capacity = capacity
        self._increase_ratio = increase_ratio
        self._int_dtype = np.dtype(int_dtype)

        # ------------------------------------------------------------------------ #
        # Allocate memory and initialize the valid-cell count
        self._connectivity = np.empty(
            shape=(self._capacity, self._vertices_per_cell),
            dtype=self._int_dtype,
        )
        self._num_cells = 0

        # ------------------------------------------------------------------------ #
        return None

    # ---------------------------------------------------------------------------- #
    @property
    def int_dtype(self) -> np.dtype:
        """Integer dtype used for connectivity storage."""
        return self._int_dtype

    @property
    def vertices_per_cell(self) -> int:
        """Number of indices in each connectivity row."""
        return self._vertices_per_cell

    @property
    def capacity(self) -> int:
        """Number of reserved rows, including unused storage."""
        return self._capacity

    @property
    def num_cells(self) -> int:
        """Number of populated rows."""
        return self._num_cells

    @property
    def connectivity(self) -> np.ndarray:
        """Writable view of valid rows; reacquire it after storage growth."""
        return self._connectivity[:self._num_cells]

    # ---------------------------------------------------------------------------- #
    def add_cell(self, indexes: Sequence[int]) -> int:
        """Append connectivity supplied by the caller without validation.

        Parameters
        ----------
        indexes : sequence of int
            Connectivity supplied by the caller in element order.

        Returns
        -------
        int
            Cell index local to this block.
        """
        # ------------------------------------------------------------------------ #
        # Increase capacity when necessary
        if self._num_cells == self._capacity:
            capacity = max(self._capacity + 1,
                           math.ceil(self._capacity * self._increase_ratio))
            connectivity = np.empty((capacity, self.vertices_per_cell), dtype=self._int_dtype)
            connectivity[:self._num_cells] = self.connectivity
            self._connectivity = connectivity
            self._capacity = capacity

        # ------------------------------------------------------------------------ #
        # Insert the cell and return its local index
        index = self._num_cells
        self._connectivity[index] = np.array(indexes, dtype=self._int_dtype)
        self._num_cells += 1

        # ------------------------------------------------------------------------ #
        return index

# -------------------------------------------------------------------------------- #
@dataclass(slots=True, repr=False, eq=False)
class Cells():
    """
    Group independently allocated cell blocks by element name.
    """
    triangle: CellBlock
    quadrilateral: CellBlock

# -------------------------------------------------------------------------------- #
class Mesh():
    """Store mesh data through the same interface in 2D and 3D.

    Attributes
    ----------
    dim : int
        Read-only spatial dimension, either 2 or 3.
    points : ndarray
        Writable view of valid coordinates, with shape (num_vertices, dim).
    cells : Cells
        Cell blocks accessible by attributes, such as cells.triangle.
        A cell is identified by its type and block-local index.
    boundaries : dict[str, ndarray]
        Ordered vertex indices by globally unique curve name.
    """

    # ---------------------------------------------------------------------------- #
    def __init__(
            self,
            dim: int = 2,
            vertices_capacity: int = 1000,
            cells_capacity: int = 1000,
            increase_ratio: float = 1.5,
            float_dtype: DTypeLike = np.float64,
            int_dtype: DTypeLike = np.int32,
        ) -> None:
        """
        Parameters
        ----------
        dim : {2, 3}, default=2
            Spatial dimension used by geometric operations.
        vertices_capacity : int, default=1000
            Initial number of reserved vertices.
        cells_capacity : int, default=1000
            Initial capacity of each cell block.
        increase_ratio : float, default=1.5
            Finite capacity growth factor greater than one.
        float_dtype : numpy dtype-like, default=numpy.float64
            Coordinate storage type: float32 or float64.
        int_dtype : numpy dtype-like, default=numpy.int32
            Connectivity storage type: int32 or int64, shared by all blocks.
        """
        # ------------------------------------------------------------------------ #
        # Validate input arguments
        if not (dim in (2, 3)):
            raise ValueError(f"dim must be 2 or 3, got {dim}.")
        
        validation.is_positive_int(vertices_capacity, "vertices_capacity")
        validation.is_positive_int(cells_capacity, "cells_capacity")
        validation.is_positive_float(increase_ratio, "increase_ratio")
        validation.is_float_dtype(float_dtype)
        validation.is_int_dtype(int_dtype)

        # ------------------------------------------------------------------------ #
        # Store constructor arguments
        self._dim = dim
        self._vertices_capacity = vertices_capacity
        self._increase_ratio = increase_ratio
        self._float_dtype = np.dtype(float_dtype)
        self._int_dtype = np.dtype(int_dtype)

        # ------------------------------------------------------------------------ #
        # Allocate independent blocks and coordinate storage
        self._cells = Cells(
            triangle=CellBlock(3, cells_capacity, increase_ratio, int_dtype=self._int_dtype),
            quadrilateral=CellBlock(4, cells_capacity, increase_ratio, int_dtype=self._int_dtype),
        )
        self._points = np.empty((self._vertices_capacity, self._dim), dtype=self._float_dtype)
        self._num_vertices = 0
        self._boundaries = {}

        # ------------------------------------------------------------------------ #
        return None

    # ---------------------------------------------------------------------------- #
    @property
    def float_dtype(self) -> np.dtype:
        """Floating-point dtype used for coordinates."""
        return self._float_dtype

    @property
    def int_dtype(self) -> np.dtype:
        """Integer dtype used by all cell blocks."""
        return self._int_dtype

    @property
    def dim(self) -> int:
        """Spatial dimension used to dispatch dimension-specific algorithms."""
        return self._dim

    @property
    def points(self) -> np.ndarray:
        """Writable view of valid coordinates; reacquire after storage growth."""
        return self._points[:self._num_vertices]

    @property
    def cells(self) -> Cells:
        """Container holding this mesh's independently allocated cell blocks."""
        return self._cells

    @property
    def boundaries(self) -> dict[str, np.ndarray]:
        """Writable boundary indices by curve name, independent of fronts."""
        return self._boundaries

    @property
    def vertices_capacity(self) -> int:
        """Number of reserved vertex rows."""
        return self._vertices_capacity

    @property
    def num_vertices(self) -> int:
        """Number of populated vertex rows."""
        return self._num_vertices

    @property
    def num_cells(self) -> int:
        """Total populated cells across all blocks."""
        return sum(getattr(self.cells, field.name).num_cells for field in fields(Cells))

    # ---------------------------------------------------------------------------- #
    def add_vertex(self, vertex: Sequence[float] | np.ndarray) -> int:
        """Append coordinates without validation and return the vertex index."""
        # ------------------------------------------------------------------------ #
        # Increase capacity when necessary
        if self._num_vertices == self._vertices_capacity:
            capacity = max(self._vertices_capacity + 1,
                           math.ceil(self._vertices_capacity * self._increase_ratio))
            points = np.empty((capacity, self.dim), dtype=self._float_dtype)
            points[:self._num_vertices] = self.points
            self._points = points
            self._vertices_capacity = capacity

        # ------------------------------------------------------------------------ #
        # Insert the vertex and return its global index
        index = self._num_vertices
        self._points[index] = np.asarray(vertex, dtype=self._float_dtype)
        self._num_vertices += 1

        # ------------------------------------------------------------------------ #
        return index

    # ---------------------------------------------------------------------------- #
    def add_cell(self, cell_type: str, vertices: Sequence[int] | np.ndarray) -> int:
        """Append a cell without validation and return its block-local index.

        Parameters
        ----------
        cell_type : str
            Exact Cells attribute name, such as triangle or quadrilateral.
        vertices : sequence of int
            Connectivity supplied by the caller in element order.

        Notes
        -----
        The caller ensures correct arity, references compatible with int_dtype,
        element dimension and geometry. Unknown attributes raise AttributeError
        naturally; no aliases or explicit input checks are provided.
        """
        # ------------------------------------------------------------------------ #
        # Insert into the corresponding block
        return getattr(self.cells, cell_type).add_cell(np.asarray(vertices, dtype=self._int_dtype))

# -------------------------------------------------------------------------------- #
