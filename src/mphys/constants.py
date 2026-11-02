"""
This file contains useful global constants that are used throughout the project.
"""

from math import pi

ATOMS_PER_NUC = 19  # Atoms in each nucleosome core.  Not counting any DNA or patches
TYPE_2_ATOM_NUC = 7  # Possibly spurious DNA type atom in nucleosome core list in the given initial conditions generator
TIMESTEP_LINE_START = "ITEM: TIMESTEP"  # Identifier for the line in the dump file marking the start of a frame
LJ_TO_M = 2.5e-9  # From the meetings with Chris 1LJ unit of distance is 2.5 nm
FF_INTERACTION_RANGE = (
    75e-10 / LJ_TO_M
)  # Taking the approximate value from the Moller et al. paper. About half way up from the well minimum.
FF_ANGLE_THRESHOLD = (
    pi / 4
)  # FIXME: Add the real thershold. Ask Chris for the actual value.
