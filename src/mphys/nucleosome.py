"""
This file contains the dataclass for a nucleosome in terms of its central bead.
The data class stores information such as the position, quaternion values, normal vector
The nucleosome consists of atom types: 2 - the alway stuck DNA, 3 - the outer layer of the core, 4 - the inner layer of the core, 23 - the single core sphere.
NOTE: There are also patches but they are not important for now.

I think that it is enough to store the information only about ATOM TYPE = 23 and then maybe a list of atoms part of the same nucleosome (I think I can do this by atom IDs)

From the looks of the IC generator program, the nucleosome consists of 1 core atom, 6 type 4 atoms, 12 type 3 atoms. (There is also one type 2 DNA placed at the same time as the type 3 and 4 atoms and I don't know why.
The highest atoms ID is for the core. Then the next 6 down are type 4, then skip one (the weird type 2), then the next 12 are type 3

"""

import numpy as np
from dataclasses import dataclass


@dataclass
class Nucleosome:

    pos: np.ndarray
    norm: np.ndarray
    quat: np.ndarray

    atoms: np.ndarray
