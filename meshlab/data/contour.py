# -------------------------------------------------------------------------------- #
import numpy as np

from meshlab.utils import validation

# -------------------------------------------------------------------------------- #
class Contour():
    """
    Data structure used to store a group of vertex indices.

    A contour represents an ordered closed contour of the mesh. The stored
    indices refer to vertices in a ``Mesh`` object and are assumed to be
    ordered in the counter-clockwise direction.

    The array is preallocated during construction to avoid repeated memory
    allocations when new indices are inserted. The attribute ``num_indices``
    keeps track of the number of valid indices currently stored.
    """

    def __init__(
            self,
            name: str,
            capacity: int = 1000,
            increase_ratio: float = 1.5,
        ) -> None:
        """
        Create an empty contour.

        Parameters
        ----------
        name : str
            Name of the contour.
        capacity : int
            Maximum number of indices that can be stored.
        """
        # ------------------------------------------------------------------------ #
        # Validate input arguments
        validation.is_int(capacity)

        # ------------------------------------------------------------------------ #
        # Store constructor arguments
        self.name = name
        self.capacity = capacity
        self.increase_ratio = increase_ratio

        # ------------------------------------------------------------------------ #
        # Allocate memory for the vertex indices
        self.indices = np.empty(self.capacity, dtype=np.int32)

        self.num_indices: int = 0

        # ------------------------------------------------------------------------ #
        return None

    def add_index(self, index: int) -> None:
        """
        Insert a new vertex index into the contour.

        Parameters
        ----------
        index : int
            Vertex index.
        """
        # ------------------------------------------------------------------------ #
        # Check maximum capacity
        if self.num_indices == self.capacity - 1:
            self.capacity = int(self.capacity * self.increase_ratio)
            indices = np.empty(self.capacity, dtype=np.int32)
            indices[:self.num_indices] = self.indices[:self.num_indices]
            self.indices = indices

        # ------------------------------------------------------------------------ #
        # Store the new index
        self.indices[self.num_indices] = index

        self.num_indices += 1

        # ------------------------------------------------------------------------ #
        return None

# -------------------------------------------------------------------------------- #
