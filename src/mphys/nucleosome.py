"""
This file contains the dataclass for a nucleosome in terms of its central bead.
The data class stores information such as the position, quaternion values, normal vector
The nucleosome consists of atom types: 2 - the alway stuck DNA, 3 - the outer layer of the core, 4 - the inner layer of the core, 23 - the single core sphere.
NOTE: There are also patches but they are not important for now.

I think that it is enough to store the information only about ATOM TYPE = 23 and then maybe a list of atoms part of the same nucleosome (I think I can do this by atom IDs)

From the looks of the IC generator program, the nucleosome consists of 1 core atom, 6 type 4 atoms, 12 type 3 atoms. (There is also one type 2 DNA placed at the same time as the type 3 and 4 atoms and I don't know why.
The highest atoms ID is for the core. Then the next 6 down are type 4, then skip one (the weird type 2), then the next 12 are type 3

"""

from __future__ import annotations
import numpy as np
from dataclasses import dataclass, field
from mphys.funcs import quat2uaxis, quat2vaxis, quat2faxis


@dataclass
class Nucleosome:

    id: int = 0

    pos: np.ndarray = field(default_factory=lambda: np.zeros(3))
    norm: np.ndarray = field(default_factory=lambda: np.zeros(3))
    quat: np.ndarray = field(default_factory=lambda: np.zeros(4))

    centre_id: int = 0
    atoms: np.ndarray = field(default_factory=lambda: np.zeros(19))

    stacks: int = 0

    stacked_with: np.ndarray = field(default_factory=lambda: np.zeros(2))

    @property
    def uaxis(self):
        """Unit vector corresponding to z-axis of the centre bead"""
        return quat2uaxis(self.quat)

    @property
    def vaxis(self):
        """Unit vector corresponding to y-axis of the centre bead"""
        return quat2vaxis(self.quat)

    @property
    def faxis(self):
        """Unit vector corresponding to y-axis of the centre bead"""
        return quat2faxis(self.quat)

    def __post_init__(self):
        if not isinstance(self.centre_id, int):
            raise ValueError("Atom IDs must be of type int")
        if not all(i.is_integer() for i in self.atoms):
            raise ValueError("Atom IDs must be of type int")
        if self.pos.size != 3:
            raise ValueError(f"Position must have 3 coordinates, has {self.pos.size}")
        if self.quat.size != 4:
            raise ValueError(
                f"Quaternion must have 4 coordinates, has {self.quat.size}"
            )
        if self.stacks > 2:
            raise NotImplementedError(
                "Currently only supporting face to face stacking which has a maximum number of 2."
            )
        if self.stacked_with.size > 2:
            raise NotImplementedError(
                "Currently only supporting face to face stacking which has a maximum number of 2."
            )

    def distance_to_nuc(self, nuc: Nucleosome) -> float:
        if not isinstance(nuc, Nucleosome):
            raise TypeError("The second object must be of type Nucleosome.")
        return np.linalg.norm(self.pos - nuc.pos)
