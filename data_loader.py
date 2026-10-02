# Helper functions for loading large data dump files (named by default as dump_main.nucleosomes)
# The key aim is to ensure efficient memory usage as to not store the large files in memory
from pathlib import Path
import numpy as np

def _check_valid_cols(cols : list, available_cols : list):
    if not all(col in available_cols for col in cols):
        missing_cols = [col for col in cols if col not in header_titles]
        missing_cols = " ".join(missing_cols) 
        raise KeyError(
                    f"The following columns don't exist in the dump file: {missing_cols}")

def _chunk_generator(source : Path, groupby : str):
    data = []
    for row in source:
        if row.startswith(groupby):
            if data:
                yield data
                data = []
        data.append(row)
    if data:
        yield data

def load_dump_timestep(filepath: Path, cols: list | None = None, skip : int = 0):
    """
    Generator that reads a LAMMPS dump file one timestep at a time.

    Yields a tuple of (chunk_params, data) for each timestep, where
    chunk_params is a dict of metadata and data is a 2D array of shape
    (n_atoms, n_selected_columns).
    """
    TIMESTEP_LINE_START = "ITEM: TIMESTEP"


    with open(filepath, "r") as dump_file:
        # Use a generator function to iterate per timestep chunk
        for i, chunk in enumerate(_chunk_generator(dump_file, TIMESTEP_LINE_START)):
            if i < skip:
                continue
            # Drop "ITEM:" and "ATOMS" to leave only the column headings
            atom_headings = chunk[8].split()[2:]

            if cols is not None:
                # Check that all requested columns are present in the file
                _check_valid_cols(cols, atom_headings)
                used_titles = [title for title in atom_headings if title in cols]
                used_title_ids = [atom_headings.index(title) for title in used_titles]
            else:
                # Use all the columns
                used_titles = atom_headings
                used_title_ids = list(range(len(atom_headings)))

            chunk_params = {
                "timestep": int(chunk[1]),
                "n_atoms": int(chunk[3]),
                "atom_headings": atom_headings,
                "used_titles": used_titles,
            }

            # Parse all atom lines for this chunk in one go
            data = np.loadtxt(chunk[9:], usecols=used_title_ids, ndmin=2)

            yield chunk_params, data           



if __name__ == "__main__":
    filepath = "/home/s2289431/MPhys_Project/Shared/initial_condition_builder/dump_main.nucleosomes"
    params, data = next(load_dump_timestep(filepath))
    print(params["timestep"], params["used_titles"], data.shape)
    print(data[0])
