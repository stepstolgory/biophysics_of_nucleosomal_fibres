"""This file is responsible for calculating the stacking fraction of nucleosomes over the simulation time"""

import argparse
import numpy as np
from mphys.data_loader import load_dump_timestep
from mphys.nucleosome import Nucleosome
from mphys.constants import (
    ATOMS_PER_NUC,
    TYPE_2_ATOM_NUC,
    FF_INTERACTION_RANGE,
    FF_ANGLE_THRESHOLD,
)


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
            # print(nuc.id, nuc.centre_id)
            continue

    return nucs


def find_stackings(
    times,
    pos_list,
    u_list,
    frames,
    r_cut=FF_INTERACTION_RANGE,
    angle_cut=FF_ANGLE_THRESHOLD,
    verbose=False,
):
    """Find face-to-face stacked nucleosome pairs in every frame.

    times     : list of timesteps, one per frame
    pos_list  : list of (N, 3) centre positions, one per frame
    u_list    : list of (N, 3) unit normals, one per frame
    frames    : list of nucleosome objects per frame; their .plus_partner and
                .minus_partner are filled in (must start as None)
    r_cut     : distance cut-off
    angle_cut : angle cut-off in radians
    verbose   : flag to print all stacked pairs

    Returns stacked (F, n_pairs) True/False, fraction (F,),
    occ (F, N, 2) with [..., 0] the plus face and [..., 1] the minus face
    (1 occupied, 0 free, 2 two partners on one face), and the pair indices
    I_IDX, J_IDX.
    """
    # Where F is the number of frames and N is the number of nucleosomes
    times = np.array(times)  # Shape (F,)
    pos = np.array(pos_list)  # Shape (F, N, 3)
    u = np.array(u_list)  # Shape (F, N, 3)
    F, N = pos.shape[:2]

    # All unique nucleosome pairs, k=1 stops pairing with itself
    I_IDX, J_IDX = np.triu_indices(N, k=1)
    r2_cut = r_cut**2
    cos_cut = np.cos(angle_cut)

    # Vector from i to j, and squared distance, for every pair in every frame
    d = pos[:, J_IDX] - pos[:, I_IDX]
    dist2 = (d * d).sum(axis=2)

    # Normals of the two nucleosomes in each pair
    u_i = u[:, I_IDX]
    u_j = u[:, J_IDX]
    cos = np.abs((u_i * u_j).sum(axis=2))

    close = dist2 <= r2_cut
    # Want cos bigger than cos_cut since cos increases as angles get closer to 0
    aligned = cos >= cos_cut
    stacked = close & aligned

    # Which face of each nucleosome its partner is on: +1 plus, -1 minus
    proj_i = (u_i * d).sum(axis=2)  # u_i . (r_j - r_i)
    proj_j = -(u_j * d).sum(axis=2)  # u_j . (r_i - r_j)
    face_i = np.where(proj_i >= 0, 1, -1)
    face_j = np.where(proj_j >= 0, 1, -1)
    face_name = {1: "plus", -1: "minus"}

    # Go through every stacked pair, fill the faces and print
    f_idx, p_idx = np.nonzero(stacked)
    for f, p in zip(f_idx, p_idx):
        i, j = int(I_IDX[p]), int(J_IDX[p])
        fi, fj = int(face_i[f, p]), int(face_j[f, p])
        nucs = frames[f]
        nucs[i].add_stack(j, fi, frame=f)
        nucs[j].add_stack(i, fj, frame=f)
        if verbose:
            print(
                f"Frame {f} (time {times[f]}): stacking found between "
                f"nucleosome {nucs[i].id} ({face_name[fi]} face) and "
                f"nucleosome {nucs[j].id} ({face_name[fj]} face)"
            )

    # Occupied faces: column 0 is the plus face, column 1 the minus face
    occ = np.zeros((F, N, 2), dtype=int)
    np.add.at(occ, (f_idx, I_IDX[p_idx], (face_i[f_idx, p_idx] < 0).astype(int)), 1)
    np.add.at(occ, (f_idx, J_IDX[p_idx], (face_j[f_idx, p_idx] < 0).astype(int)), 1)

    # Stacked fraction = occupied faces / 2N
    fraction = (occ > 0).sum(axis=(1, 2)) / (2 * N)

    return stacked, fraction, occ, I_IDX, J_IDX


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("filepath", type=str, help="Path to dump file")
    args = parser.parse_args()

    times = []
    pos_list = []
    u_list = []
    frames = []

    for chunk_params, chunk_data in load_dump_timestep(
        args.filepath,
    ):
        nucs: list[Nucleosome] = reconstruct_nucleosomes(chunk_data)
        frames.append(nucs)
        times.append(chunk_params["timestep"])
        pos_list.append([nuc.pos for nuc in nucs])
        u_list.append([nuc.u for nuc in nucs])

    _, fraction, _, _, _ = find_stackings(
        times, pos_list, u_list, frames, verbose=False
    )
    print(np.mean(fraction))


if __name__ == "__main__":
    main()
