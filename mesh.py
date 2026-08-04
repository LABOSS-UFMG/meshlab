# -------------------------------------------------------------------------------- #
import numpy as np

from typing import Sequence

# -------------------------------------------------------------------------------- #
class Mesh():

    def __init__(
            self,
            vertices_capacity: int,
            cells_capacity: int,
            cells_max_dim: int = 4,
        ) -> None:
        # ------------------------------------------------------------------------ #
        self.cells_max_dim = cells_max_dim

        # ------------------------------------------------------------------------ #
        self.vertices = np.empty([vertices_capacity, 2], dtype=np.float64)
        self.cells = np.full([cells_capacity, cells_max_dim], -1, dtype=np.int32)
        
        # ------------------------------------------------------------------------ #
        self.num_vertices: int = 0
        self.num_cells: int = 0

        # ------------------------------------------------------------------------ #
        return None

    def add_vertex(self, vertex: Sequence[float]) -> int:
        # ------------------------------------------------------------------------ #
        self.vertices[self.num_vertices, 0] = vertex[0]
        self.vertices[self.num_vertices, 1] = vertex[1]

        self.num_vertices += 1

        # ------------------------------------------------------------------------ #
        return self.num_vertices - 1

    def replace_vertex(self, index: int, vertex: Sequence[float]) -> None:
        # ------------------------------------------------------------------------ #
        self.vertices[index, 0] = vertex[0]
        self.vertices[index, 1] = vertex[1]

        # ------------------------------------------------------------------------ #
        return None

    def translate_vertex(self, index: int, displacement: Sequence[float]) -> None:
            # ------------------------------------------------------------------------ #
            self.vertices[index, 0] += displacement[0]
            self.vertices[index, 1] += displacement[1]
    
            # ------------------------------------------------------------------------ #
            return None

    def remove_vertex(self, index: int) -> None:
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
        # Update vertex indices in cells
        self.cells[:self.num_cells][self.cells[:self.num_cells] > index] -= 1

        # ------------------------------------------------------------------------ #
        return None

    def add_cell(self, cell: Sequence[int]) -> int:
        # ------------------------------------------------------------------------ #
        for i in range(len(cell)):
            self.cells[self.num_cells, i] = cell[i]
        
        self.num_cells += 1
    
        # ------------------------------------------------------------------------ #
        return self.num_cells - 1

    def remove_cell(self, index: int) -> None:
        # ------------------------------------------------------------------------ #
        if index < self.num_cells - 1:
            self.cells[index:self.num_cells-1] = self.cells[index+1:self.num_cells]

        self.num_cells -= 1

        # ------------------------------------------------------------------------ #
        return None

# -------------------------------------------------------------------------------- #
