"""
This file contains the dataclass for a nucleosome in terms of its central bead.
The data class stores information such as the position, quaternion values, normal vector
The nucleosome consists of atom types: 2 - the alway stuck DNA, 3 - the outer layer of the core, 4 - the inner layer of the core, 23 - the single core sphere.
NOTE: There are also patches but they are not important for now.


I think that it is enough to store the information only about ATOM TYPE = 23 and then maybe a list of atoms part of the same nucleosome (I think I can do this by atom IDs)


From the looks of the IC generator program, the nucleosome consists of 1 core atom, 6 type 4 atoms, 12 type 3 atoms. (There is also one type 2 DNA placed at the same time as the type 3 and 4 atoms and I don't know why.
The highest atoms ID is for the core. Then the next 6 down are type 4, then skip one (the weird type 2), then the next 12 are type 3

Faces of the disc:

    The "plus" face is the one the u axis (bead z axis) points out of, the "minus" face is
    the opposite one. u is fixed to the bead, so each face keeps its label for the whole run.
"""

from __future__ import annotations
import warnings
import numpy as np

from dataclasses import dataclass, field
from mphys.funcs import quat2uaxis, quat2vaxis, quat2faxis

PLUS = 1
MINUS = -1


@dataclass
class Nucleosome:

    id: int = 0

    pos: np.ndarray = field(default_factory=lambda: np.zeros(3))
    norm: np.ndarray = field(default_factory=lambda: np.zeros(3))
    quat: np.ndarray = field(default_factory=lambda: np.zeros(4))

    centre_id: int = 0
    atoms: np.ndarray = field(default_factory=lambda: np.zeros(19))

    # Index of the nucleosome stacked on each face, or None if that face is free
    plus_partner: int | None = None
    minus_partner: int | None = None

    @property
    def u(self):
        """Unit vector corresponding to z-axis of the centre bead (the disc normal)"""
        return quat2uaxis(self.quat)

    @property
    def v(self):
        """Unit vector corresponding to y-axis of the centre bead"""
        return quat2vaxis(self.quat)

    @property
    def f(self):
        """Unit vector corresponding to x-axis of the centre bead"""
        return quat2faxis(self.quat)

    @property
    def stacks(self) -> int:
        """Number of occupied faces (0, 1 or 2)"""
        return (self.plus_partner is not None) + (self.minus_partner is not None)

    @property
    def stacked_with(self) -> list[int]:
        """Indices of the stacking partners, plus face first"""
        return [p for p in (self.plus_partner, self.minus_partner) if p is not None]

    @property
    def faces(self) -> tuple[bool, bool]:
        """(plus face occupied, minus face occupied)"""
        return self.plus_partner is not None, self.minus_partner is not None

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

    def distance_to_nuc(self, nuc: Nucleosome) -> float:
        """
        Returns the straight line distance between two nucleosome cores
        """
        if not isinstance(nuc, Nucleosome):
            raise TypeError("Both objects must be of type Nucleosome.")
        return np.linalg.norm(self.pos - nuc.pos)

    def relative_orientation(self, nuc: Nucleosome) -> float:
        """
        Returns the angle in radians between the u axis vector (z) of this nucleosome and one other. Using only the central code bead for reference.
        cos(a) = (self.uaxis * nuc.uaxis) (vector is already normalised).

        np.arccos takes in values in the range [-1,1], without doing anything extra nucleosomes who's u-axis vectors are antiparallet (or close to) will not count as stacked though they visually are so taking the absolute value of cos(a) places us in [0, 1]
        which leaves arccos always between [0, pi/2].

        Final equation: a = arccos(|self.uaxis * nuc.uaxis|)


        return : float
        Symmetrical angle offset between two nucleosomes in radians
        """
        if not isinstance(nuc, Nucleosome):
            raise TypeError("Both objects must be of type Nucleosome.")
        return np.arccos(abs(np.inner(self.u, nuc.u)))

    def face_towards(self, nuc: Nucleosome) -> int:
        """
        Which face of this disc points towards another nucleosome.

        The sign of u . (r_other - r_self) says which side of the disc the other centre is on.

        return : int
        PLUS (+1) or MINUS (-1)
        """
        return PLUS if np.dot(self.u, nuc.pos - self.pos) >= 0 else MINUS

    def add_stack(self, partner: int, face: int, frame: int | None = None) -> bool:
        """
        Record a stacking partner on the given face (PLUS or MINUS).
        If that face already has a different partner, warn and keep the first one.

        return : bool
        True if the partner was recorded

        """
        attr = "plus_partner" if face > 0 else "minus_partner"
        current = getattr(self, attr)
        if current is not None and current != partner:
            where = f"frame {frame}, " if frame is not None else ""
            warnings.warn(
                f"{where}nucleosome {self.id}: {attr.split('_')[0]} face already has "
                f"partner {current}, ignoring {partner}"
            )
            return False
        setattr(self, attr, partner)
        return True
