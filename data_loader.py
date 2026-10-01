# Helper functions for loading large data dump files (named by default as dump_main.nucleosomes)
# The key aim is to ensure efficient memory usage as to not store the large files in memory
from pathlib import Path


def load_dump_timestep(filepath: Path, cols: list | None = None):
    # Load in a dump chunk, optionally with only the selected columns
    HEADER_LINE_START = "ITEM: ATOMS"
    header_line = None
    # First need to check if all columns are present in the file
    with open(filepath, "r") as dump_file:
        for line in dump_file:
            if line.startswith(HEADER_LINE_START):
                header_line = line.strip()
                break
    dump_file.close()
    header_titles = set(header_line.split(" "))
    print(header_titles)
    if cols is not None:
        if not all(cols in header_titles):
            raise KeyError(
                "Some of the specified columns don't exist in the dump file."
            )


if __name__ == "__main__":
    filepath = "~/MPhys_Project/Shared/initial_conditions_builder/dump_main.nucleosomes"
    print("Testing the file loader with all columns")
    load_dump_timestep(filepath)
    print("Testing the file loader with existing columns")
    load_dump_timestep(filepath, ["x", "y"])
    print("Testing the file loader with non-existing columns")
    load_dump_timestep(filepath, ["x", "fake_name"])
