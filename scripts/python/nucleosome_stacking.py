"""This file is responsible for calculating the stacking fraction of nucleosomes over the simulation time"""

import argparse
import numpy as np
from mphys.data_loader import load_dump_timestep
from mphys.nucleosome import Nucleosome
from mphys.constants import ATOMS_PER_NUC, TYPE_2_ATOM_NUC, FF_INTERACTION_RANGE


def reconstruct_nucleosomes(data: np.ndarray):
    """
    Construct a list of nucleosomes for a given frame of data.
    Since the data list is already sorted by atom ID the nucleosome IDs should also be sorted wrt initial conditions.

    data : np.ndarray  Atom data for a single frame. Must contain all columns in the file (9 total)

    return list[Nucleosome]
    """
    nucs: list[Nucleosome] = []
    nuc_count = 0
    for i, atom in enumerate(data):
        if (
            atom.size != 12
        ):  # Change this to 9 once I remove ix, iy, iz from dump command and run new sweep
            raise IndexError(
                f"Atom with ID {i} does not have the expected number of columns. Expected 9, got {atom.size}."
            )

        if atom[1] == 23:
            nuc = Nucleosome(
                id=nuc_count,
                centre_id=int(atom[0]),
                pos=np.array(atom[2:5]),
                quat=np.array(atom[-4:]),
                atoms=np.asarray(
                    [
                        int(atom[0]) - j
                        for j in range(0, ATOMS_PER_NUC)
                        if j != TYPE_2_ATOM_NUC
                    ]
                ),
            )
            nucs.append(nuc)
            nuc_count += 1
            continue

    return nucs


def find_stackings(nucs: list[Nucleosome]):
    nucs = np.asarray(nucs)

    for i in range(nucs.size):
        if nucs[i].stacks >= 2:
            # Maximum of two face to face stackings, so if a nucleosome already has two, can drop it and no longer check.
            np.delete(nucs, i)
            continue
        for j in range(i + 1, nucs.size):
            distance = nucs[i].distance_to_nuc(nucs[j])
            if distance <= FF_INTERACTION_RANGE:
                print(f"Possibly stacked nucleosome {i} with nucleosome {j}")
            # Now I need to check for distance between nucleosome 1 and all other nucleosomes
            continue


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("filepath", type=str, help="Path to dump file")
    args = parser.parse_args()

    for chunk_params, chunk_data in load_dump_timestep(args.filepath, skip=999):
        nucs = reconstruct_nucleosomes(chunk_data)
        find_stackings(nucs)


if __name__ == "__main__":
    main()
