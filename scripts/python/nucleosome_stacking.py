"""This file is responsible for calculating the stacking fraction of nucleosomes over the simulation time"""

import argparse
from pathlib import Path

import numpy as np

from mphys.constants import (
    ATOMS_PER_NUC,
    FF_ANGLE_THRESHOLD,
    FF_INTERACTION_RANGE,
    TYPE_2_ATOM_NUC,
)
from mphys.data_loader import load_dump_timestep
from mphys.funcs import partner_gaps, store_data_to_csv
from mphys.nucleosome import Nucleosome

MAX_GAP = 4


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
        ):  # FIXME: Change this to 9 once I remove ix, iy, iz from dump command and run new sweep
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


def partner_table(frames: list[list[Nucleosome]]) -> np.ndarray:
    """
    Partner on each face of each nucleosome, for every frame.
        frames : list[list[Nucleosome]] - Nucleosomes of every frame, after find_stackings

    Returns: numpy.ndarray of shape (F, 2N). Column 2i is nucleosome i's plus face,
             column 2i + 1 its minus face. -1 marks a free face.

        Note: "partner or -1" would turn partner 0 into -1, so None is tested for directly.
    """
    F, N = len(frames), len(frames[0])
    partners = np.full((F, 2 * N), -1, dtype=int)
    for f, nucs in enumerate(frames):
        for nuc in nucs:
            if nuc.plus_partner is not None:
                partners[f, 2 * nuc.id] = nuc.plus_partner
            if nuc.minus_partner is not None:
                partners[f, 2 * nuc.id + 1] = nuc.minus_partner
    return partners


def stacking_columns(partners: np.ndarray) -> tuple[list[str], np.ndarray]:
    """
    Stacked fraction, split by how far along the chain the partner is.
        partners : numpy.ndarray - Partner table of shape (F, 2N), from partner_table

    Returns: Column names and values of shape (F, MAX_GAP + 1):
             fraction, then gap1 ... gap<MAX_GAP - 1>, then gap<MAX_GAP>plus.
             Each is a number of faces divided by 2N, so the gap columns add up to fraction.
    """
    gaps = partner_gaps(partners)
    n_faces = partners.shape[1]  # 2N

    names = ["fraction"]
    columns = [(partners >= 0).sum(axis=1) / n_faces]
    for gap in range(1, MAX_GAP):
        names.append(f"gap{gap}")
        columns.append((gaps == gap).sum(axis=1) / n_faces)
    names.append(f"gap{MAX_GAP}plus")
    columns.append((gaps >= MAX_GAP).sum(axis=1) / n_faces)

    return names, np.column_stack(columns)


def write_outputs(
    prefix: Path,
    times: list,
    partners: np.ndarray,
    r_cut: float,
    angle_cut: float,
    source: str,
) -> None:
    """
    Write <prefix>_faces.dat (partner on every face) and <prefix>_stacking.dat
    (stacked fraction and its split by gap), one row per frame.
        prefix : Path - Output path without the ending, e.g. data_files/sweep04/E8.0_I0.2_W10.0_r1
        times : list - Timestep of each frame
        partners : numpy.ndarray - Partner table of shape (F, 2N)
        r_cut : float - Distance cut-off used, in sigma_LJ
        angle_cut : float - Angle cut-off used, in radians
        source : str - Dump file the stackings were found in
    """
    prefix.parent.mkdir(parents=True, exist_ok=True)
    times = np.asarray(times, dtype=int)
    N = partners.shape[1] // 2

    comments = [
        f"source: {source}",
        f"N = {N}, r_cut = {r_cut:g} sigma_LJ, angle_cut = {angle_cut:g} rad",
    ]

    # Partner on every face: n0_plus n0_minus n1_plus n1_minus ...
    face_names = [f"n{i}_{face}" for i in range(N) for face in ("plus", "minus")]
    store_data_to_csv(
        np.column_stack((times, partners)),
        f"{prefix}_faces.dat",
        ["#", "timestep", *face_names],
        comments=comments + ["partner index on each face, -1 if free"],
    )

    # Stacked fraction and its split by gap along the chain
    names, values = stacking_columns(partners)
    store_data_to_csv(
        [[t, *(f"{v:.6g}" for v in row)] for t, row in zip(times, values)],
        f"{prefix}_stacking.dat",
        ["#", "timestep", *names],
        comments=comments + ["stacked faces / 2N, in total and by gap along the chain"],
    )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("filepath", type=str, help="Path to dump file")
    parser.add_argument(
        "--skip", type=int, default=0, help="Skip this many frames from the dump file."
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        default=False,
        help="Print out what stackings have been found.",
    )
    parser.add_argument(
        "-o",
        "--out",
        type=str,
        default=None,
        help="Output prefix, e.g. data_files/sweep04/E8.0_I0.2_W10.0_r1 "
        "Writes <prefix>_faces.dat and <prefix>_stacking.dat",
    )
    args = parser.parse_args()

    times = []
    pos_list = []
    u_list = []
    frames = []

    for chunk_params, chunk_data in load_dump_timestep(args.filepath, skip=args.skip):
        nucs: list[Nucleosome] = reconstruct_nucleosomes(chunk_data)
        frames.append(nucs)
        times.append(chunk_params["timestep"])
        pos_list.append([nuc.pos for nuc in nucs])
        u_list.append([nuc.u for nuc in nucs])

    _, fraction, _, _, _ = find_stackings(
        times, pos_list, u_list, frames, verbose=args.verbose
    )
    print(f"Mean stacking fraction: {np.mean(fraction):.3g}")

    if args.out is not None:
        partners = partner_table(frames)
        write_outputs(
            Path(args.out),
            times,
            partners,
            FF_INTERACTION_RANGE,
            FF_ANGLE_THRESHOLD,
            args.filepath,
        )
        print(f"Saved {args.out}_faces.dat and {args.out}_stacking.dat")


if __name__ == "__main__":
    main()
