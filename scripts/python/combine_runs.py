#!/usr/bin/env python3
"""
Combine the per-run data files of a sweep into one summary per kind of file.

Reads every file in DIR named
    E<E>_I<I>_W<W>_r<rep>_<kind>.dat
for example E8.0_I0.2_W10.0_r1_rg.dat, with a timestep column and one or more
quantity columns (names from the file's header).

For each run it takes the mean of the last N rows of every quantity column. Runs with
the same E, I and W but a different rep are repeats, so for each (E, I, W) it then
gives the mean, SD and SE of those per-run means across the repeats. The per-run means
are independent of each other, so this SE is valid (unlike an SE over frames).

Output, one file per kind:
    summary_<kind>.dat   columns: E I W n, then <col>_mean <col>_sd <col>_se for each column

Usage:
    python combine_runs.py DIR
    python combine_runs.py DIR --last 100              # mean of the last 100 rows of each run
    python combine_runs.py DIR --kinds rg              # only the rg files
    python combine_runs.py DIR --outdir somewhere/else
"""

import argparse
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np

from mphys.funcs import parse_run_name, read_table


def warn(message: str) -> None:
    print(f"warning: {message}", file=sys.stderr)


def collect(directory: Path, kinds: list[str], last: int) -> dict:
    """
    Read every matching file and take the mean of its last rows.
        directory : Path - Folder holding the per-run files
        kinds : list[str] - Kinds of file to read (the part after _r<rep>_)
        last : int - Number of rows at the end of each file to average

    Returns: dict kind -> {"names": column names, "groups": {(E, I, W): list of runs}},
             where each run is a dict with rep, final timestep and the per-run means
    """
    found = {}
    skipped = []
    for path in sorted(directory.glob("*.dat")):
        params = parse_run_name(path)
        if params is None:
            if not path.name.startswith("summary_"):
                skipped.append(path.name)
            continue
        kind = params["kind"]
        if kind not in kinds:
            continue

        try:
            names, data = read_table(path)
        except ValueError as e:
            warn(f"{e}, skipped")
            continue
        if "timestep" not in names:
            warn(f"{path.name} has no 'timestep' column, skipped")
            continue

        t_col = names.index("timestep")
        value_cols = [i for i, name in enumerate(names) if name != "timestep"]
        value_names = [names[i] for i in value_cols]

        # Every file of one kind must have the same columns, or they can't be combined
        entry = found.setdefault(
            kind, {"names": value_names, "groups": defaultdict(list)}
        )
        if value_names != entry["names"]:
            warn(
                f"{path.name} has columns {' '.join(value_names)}, but other {kind} files "
                f"have {' '.join(entry['names'])}, skipped"
            )
            continue

        if len(data) < last:
            warn(f"{path.name} has only {len(data)} rows (asked for --last {last})")
        tail = data[-last:]

        key = (params["E"], params["I"], params["W"])
        entry["groups"][key].append(
            {
                "rep": params["rep"],
                "final_step": data[-1, t_col],
                "means": tail[:, value_cols].mean(axis=0),
            }
        )

    if skipped:
        warn(
            f"{len(skipped)} .dat file(s) don't match E<E>_I<I>_W<W>_r<rep>_<kind>.dat "
            f"and were ignored, e.g. {skipped[0]}"
        )
    return found


def summarise(runs: list[dict]) -> tuple[np.ndarray, np.ndarray, np.ndarray, int]:
    """
    Mean, SD and SE across repeats, for every column.
        runs : list[dict] - Runs of one (E, I, W), each with its per-run means

    Returns: mean, SD, SE (arrays with one value per column) and n.
             SD and SE are NaN if there is only one repeat.
    """
    values = np.array([run["means"] for run in runs])  # Shape (n, columns)
    n = len(values)
    mean = values.mean(axis=0)
    if n > 1:
        sd = values.std(axis=0, ddof=1)
        se = sd / np.sqrt(n)
    else:
        sd = np.full_like(mean, np.nan)
        se = np.full_like(mean, np.nan)
    return mean, sd, se, n


def check_final_steps(kind: str, key: tuple, runs: list[dict]) -> None:
    """Warn if the repeats of one (E, I, W) end at different timesteps (a crashed run?)"""
    steps = {run["final_step"] for run in runs}
    if len(steps) > 1:
        E, I, W = key
        detail = ", ".join(
            f"r{run['rep']}: {run['final_step']:g}"
            for run in sorted(runs, key=lambda run: run["rep"])
        )
        warn(
            f"{kind} at E={E:g} I={I:g} W={W:g}: repeats end at different timesteps "
            f"(crashed run?) {detail}"
        )


def write_summary(
    out_file: Path,
    kind: str,
    names: list[str],
    groups: dict,
    directory: Path,
    last: int,
) -> None:
    """Write one summary file: a row per (E, I, W) with n and the mean, SD and SE of each column"""
    columns = ["E", "I", "W", "n"]
    for name in names:
        columns += [f"{name}_mean", f"{name}_sd", f"{name}_se"]

    rows = []
    for key in sorted(groups):
        runs = groups[key]
        check_final_steps(kind, key, runs)
        mean, sd, se, n = summarise(runs)
        E, I, W = key
        row = [f"{E:g}", f"{I:g}", f"{W:g}", str(n)]
        for m, s, e in zip(mean, sd, se):
            row += [f"{m:.6g}", f"{s:.6g}", f"{e:.6g}"]
        rows.append(" ".join(row))

    with open(out_file, "w") as f:
        f.write(
            f"# {kind}: mean of the last {last} rows of each run, "
            "then mean, SD and SE across repeats\n"
        )
        f.write(f"# source: {directory.resolve()}\n")
        f.write(f"# made: {datetime.now():%Y-%m-%d %H:%M}\n")
        f.write("# " + " ".join(columns) + "\n")
        f.write("\n".join(rows) + "\n")


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "directory", type=Path, help="Folder holding the per-run .dat files"
    )
    parser.add_argument(
        "--kinds",
        nargs="+",
        default=["rg", "ee", "stacking"],
        help="Kinds of file to combine. Default rg ee stacking",
    )
    parser.add_argument(
        "--last",
        type=int,
        default=50,
        help="Average the last N rows of each run. Default 50",
    )
    parser.add_argument(
        "--outdir",
        type=Path,
        default=None,
        help="Where to write the summaries. Default: the input folder",
    )
    args = parser.parse_args()

    if not args.directory.is_dir():
        parser.error(f"{args.directory} is not a folder")
    if args.last < 1:
        parser.error("--last must be at least 1")
    if "faces" in args.kinds:
        parser.error("faces files hold partner indices, which can't be averaged")

    outdir = args.outdir or args.directory
    outdir.mkdir(parents=True, exist_ok=True)

    found = collect(args.directory, args.kinds, args.last)
    if not found:
        parser.error(
            f"no files of kind {' '.join(args.kinds)} matching "
            f"E<E>_I<I>_W<W>_r<rep>_<kind>.dat in {args.directory}"
        )

    for kind in args.kinds:
        if kind not in found:
            warn(f"no {kind} files found")
            continue
        names = found[kind]["names"]
        groups = found[kind]["groups"]
        out_file = outdir / f"summary_{kind}.dat"
        write_summary(out_file, kind, names, groups, args.directory, args.last)
        n_runs = sum(len(runs) for runs in groups.values())
        print(f"{out_file}: {len(groups)} parameter sets, {n_runs} runs")


if __name__ == "__main__":
    main()
