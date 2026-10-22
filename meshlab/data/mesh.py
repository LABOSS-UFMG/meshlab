# -------------------------------------------------------------------------------- #
import numpy as np

from typing import Sequence

from meshlab.utils import validation

# -------------------------------------------------------------------------------- #
class Mesh():
    """
    Data structure used to store a two-dimensional mesh.

    The mesh is represented by two arrays:

    - ``vertices`` stores the coordinates of the mesh vertices;
    - ``cells`` stores the connectivity of the mesh cells.

    The arrays are preallocated during construction to avoid repeated memory
    allocations when new vertices and cells are inserted. The attributes
    ``num_vertices`` and ``num_cells`` keep track of the number of valid
    entries currently stored.

    Cells may have different numbers of vertices (e.g., triangles and
    quadrilaterals). Unused positions in the connectivity array are filled
    with ``-1``.
    """

    def __init__(
            self,
            vertices_capacity: int = 1000,
            cells_capacity: int = 1000,
            cells_max_dim: int = 4,
            increase_ratio: float = 1.5,
        ) -> None:
        """
        Create an empty mesh.

        Parameters
        ----------
        vertices_capacity : int
            Maximum number of vertices that can be stored.
        cells_capacity : int
            Maximum number of cells that can be stored.
        cells_max_dim : int, default=4
            Maximum number of vertices per cell.
        increase_ratio : float, default=1.5
            Ratio used to increase the capacity of the arrays when they are full.
        """
        # ------------------------------------------------------------------------ #
        # Validate input arguments
        validation.is_int(vertices_capacity)
        validation.is_int(cells_capacity)
        validation.is_int(cells_max_dim)

        # ------------------------------------------------------------------------ #
        # Store constructor arguments
        self.vertices_capacity = vertices_capacity
        self.cells_capacity = cells_capacity
        self.cells_max_dim = cells_max_dim
        self.increase_ratio = increase_ratio

        # ------------------------------------------------------------------------ #
        # Allocate memory for the mesh data
        self.vertices = np.empty([self.vertices_capacity, 2], dtype=np.float64)
        self.cells = np.full([self.cells_capacity, self.cells_max_dim], -1, dtype=np.int32)

        self.num_vertices: int = 0
        self.num_cells: int = 0

        # ------------------------------------------------------------------------ #
        return None

    def add_vertex(self, vertex: Sequence[float] | np.ndarray) -> int:
        """
        Insert a new vertex into the mesh.

        Parameters
        ----------
        vertex : Sequence[float] | np.ndarray
            Coordinates of the new vertex.

        Returns
        -------
        int
            Index of the inserted vertex.
        """
        # ------------------------------------------------------------------------ #
        # Check maximum capacity
        if self.num_vertices == self.vertices_capacity - 1:
            self.vertices_capacity = int(self.vertices_capacity * self.increase_ratio)
            vertices = np.empty([self.vertices_capacity, 2], dtype=np.float64)
            vertices[:self.num_vertices, :] = self.vertices[:self.num_vertices, :]
            self.vertices = vertices

        # ------------------------------------------------------------------------ #
        # Add vertex
        self.vertices[self.num_vertices, 0] = vertex[0]
        self.vertices[self.num_vertices, 1] = vertex[1]

        self.num_vertices += 1

        # ------------------------------------------------------------------------ #
        return self.num_vertices - 1

    def replace_vertex(self, index: int, vertex: Sequence[float] | np.ndarray) -> None:
        """
        Replace the coordinates of an existing vertex.

        Parameters
        ----------
        index : int
            Vertex index.
        vertex : Sequence[float] | np.ndarray
            New vertex coordinates.
        """
        # ------------------------------------------------------------------------ #
        # Validate input arguments
        if index > self.num_vertices - 1:
            raise ValueError(
                f"Vertex index {index} is out of bounds. "
                f"Valid range is [0, {self.num_vertices - 1}]."
            )
                
        # ------------------------------------------------------------------------ #
        # Replace vertex
        self.vertices[index, 0] = vertex[0]
        self.vertices[index, 1] = vertex[1]

        # ------------------------------------------------------------------------ #
        return None

    def translate_vertex(self, index: int, displacement: Sequence[float] | np.ndarray) -> None:
        """
        Translate a vertex by a given displacement.

        Parameters
        ----------
        index : int
            Vertex index.
        displacement : Sequence[float] | np.ndarray
            Translation vector.
        """
        # ------------------------------------------------------------------------ #
        # Validate input arguments
        if index > self.num_vertices - 1:
            raise ValueError(
                f"Vertex index {index} is out of bounds. "
                f"Valid range is [0, {self.num_vertices - 1}]."
            )

        # ------------------------------------------------------------------------ #
        # Translate vertex
        self.vertices[index, 0] += displacement[0]
        self.vertices[index, 1] += displacement[1]
    
        # ------------------------------------------------------------------------ #
        return None

    def remove_vertex(self, index: int) -> None:
        """
        Remove a vertex from the mesh.

        All cells connected to the vertex are removed. The remaining vertices are
        shifted to keep the vertex array contiguous, and the connectivity of the
        remaining cells is updated accordingly.

        Parameters
        ----------
        index : int
            Vertex index.
        """
        # ------------------------------------------------------------------------ #
        # Validate input arguments
        if index > self.num_vertices - 1:
            raise ValueError(
                f"Vertex index {index} is out of bounds. "
                f"Valid range is [0, {self.num_vertices - 1}]."
            )

        # ------------------------------------------------------------------------ #
        # Remove cells that contain the vertex
        cells_to_remove = np.where(
            np.any(self.cells[:self.num_cells] == index, axis=1)
        )[0]

        for i in reversed(cells_to_remove):
            self.remove_cell(i)

        # ------------------------------------------------------------------------ #
        # Move vertices after the removed vertex
        if index < self.num_vertices - 1:
            self.vertices[index:self.num_vertices - 1] = (
                self.vertices[index + 1:self.num_vertices]
            )

        self.num_vertices -= 1

        # ------------------------------------------------------------------------ #
        # Update the connectivity after removing the vertex
        self.cells[:self.num_cells][self.cells[:self.num_cells] > index] -= 1

        # ------------------------------------------------------------------------ #
        return None

    def add_cell(self, cell: Sequence[int] | np.ndarray) -> int:
        """
        Insert a new cell into the mesh.

        Parameters
        ----------
        cell : Sequence[int] | np.ndarray
            Sequence containing the indices of the cell vertices.

        Returns
        -------
        int
            Index of the inserted cell.
        """
        # ------------------------------------------------------------------------ #
        # Check maximum capacity
        if self.num_cells == self.cells_capacity - 1:
            self.cells_capacity = int(self.cells_capacity * self.increase_ratio)
            cells = np.full([self.cells_capacity, self.cells_max_dim], -1, dtype=np.int32)
            cells[:self.num_cells, :] = self.cells[:self.num_cells, :]
            self.cells = cells
        
        # ------------------------------------------------------------------------ #
        # Add cell
        for i in range(len(cell)):
            self.cells[self.num_cells, i] = cell[i]
        
        self.num_cells += 1
    
        # ------------------------------------------------------------------------ #
        return self.num_cells - 1

    def remove_cell(self, index: int) -> None:
        """
        Remove a cell from the mesh.

        The remaining cells are shifted to keep the connectivity array contiguous.

        Parameters
        ----------
        index : int
            Cell index.
        """
        # ------------------------------------------------------------------------ #
        # Validate input arguments
        if index > self.num_cells - 1:
            raise ValueError(
                f"Cell index {index} is out of bounds. "
                f"Valid range is [0, {self.num_cells - 1}]."
            )

        # ------------------------------------------------------------------------ #
        # Remove cell
        if index < self.num_cells - 1:
            self.cells[index:self.num_cells-1] = self.cells[index+1:self.num_cells]

        self.num_cells -= 1

        # ------------------------------------------------------------------------ #
        return None

# -------------------------------------------------------------------------------- #
