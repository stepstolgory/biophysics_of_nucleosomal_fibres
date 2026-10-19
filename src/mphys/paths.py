from pathlib import Path

# src/mphys/paths.py -> parents[0] = mphys, [1] = src, [2] = repo root
REPO = Path(__file__).resolve().parents[2]

DATA = REPO / "data_files"
FIGURES = REPO / "figures"
INIT_CONFIGS = REPO / "init_configs"
SEEDS = REPO / "seeds"
SWEEPS = REPO / "sweeps"
SIM_OUTPUTS = REPO / "sim_outputs"


# Inside the package, so it moves with the code
STYLE = Path(__file__).resolve().parent / "style"
FONTS = STYLE / "fonts"
