# biophysics_of_nucleosomal_fibres

This repository is the code base for the MPhys dissertation project of the same name. The code is intended to measure the behaviour of nucleosomes using a new coarse grained model simulated in LAMMPS.

Make sure to push changes to the repository after finishing a session.

# Initial setup
Make sure to enter a supported python environment
``` console
conda activate daml
```
> [!NOTE]
> The `daml` environment was designed for the Data Analysis and Machine Learning in Physics course, so likely has many unnecessary libraries. Creating a dedicated environment is on the TODO list.

Build the initial condition builder (once on each machine, it is not kept in git)
``` console
make -C initial_condition_builder
```
LAMMPS itself goes in `LAMMPS/` (also not in git), so the commands below use `LAMMPS/lmp_mpi`. Run every command from the repo root.

# Folder layout

| Folder | What is in it | In git? |
|---|---|---|
| `initial_condition_builder/` | C++ code that builds a random starting structure | source only |
| `initial_positions/` | starting structures `data_<id>.lammps`, and `ic_seeds.txt` with the seed used for each | yes |
| `seeds/` | thermostat seeds `seed_<id>.lammps` | yes |
| `init_configs/` | set-up output for each id: `init_config_<id>.init`, its dump and its log | no (only `.gitkeep`, so the folder exists) |
| `sweeps/` | one folder per sweep, made by `scripts/make_sweep.sh` | `jobs.txt`, `sweep.lammps` and `jobs/` only |
| `scripts/` | LAMMPS scripts, bash scripts, Python analysis and VMD colours | yes |
| `data_files/`, `figures/` | output of `calculate_rg.py` | yes |
| `LAMMPS/` | your LAMMPS build | no |

# Make starting structures and seeds
``` console
scripts/generate_random_IC.sh 10            # structures 1 to 10 (a second number sets the nucleosomes, default 20)
scripts/generate_random_thermal_seeds.sh 10 # seed files 1 to 10
```
Both keep files that already exist, so they can be run again with a bigger number to add more.

# Run LAMMPS sim
> [!NOTE]
> For the runs that have been done so far, refer to the `RUNS.md` file.

## Set-up (equilibration): `scripts/lammps/setup.lammps`
One id
``` console
LAMMPS/lmp_mpi -in scripts/lammps/setup.lammps -var id 3 -log none
```
All 10 at once (partition mode)
``` console
mpirun -np 10 LAMMPS/lmp_mpi -partition 10x1 -plog none -pscreen none -in scripts/lammps/setup.lammps
```
Each id writes `init_config_<id>.init`, `dump_initial_<id>.nucleosomes` and `log_initial_<id>.out` into `init_configs/`.

## Production: `scripts/lammps/production.lammps`
Make a sweep, then run its jobs
``` console
scripts/make_sweep.sh -n sweep01 -E "2.0 4.0 6.0 8.0 10.0" -I "0.3" -r 5

# one job
LAMMPS/lmp_mpi -in scripts/lammps/production.lammps -var sweep sweeps/sweep01 -var job 7 -log none
# every job, one after another
LAMMPS/lmp_mpi -in scripts/lammps/production.lammps -var sweep sweeps/sweep01 -log none
# many at once (partition mode)
mpirun -np 10 LAMMPS/lmp_mpi -partition 10x1 -plog none -pscreen none -in scripts/lammps/production.lammps -var sweep sweeps/sweep01
```
Each job writes `log.out`, `dump.nucleosomes` and `final.data` into its own folder in `sweeps/sweep01/runs/`. Jobs that already have `final.data` are skipped.

## Arguments taken by the LAMMPS scripts
Set with `-var name value`.

| Script | Variable | Default | Meaning |
|---|---|---|---|
| `setup.lammps` | `id` | 1 to 10, one per partition | which starting structure and seed file to use |
| | `nsoft`, `nrelax`, `nwrap`, `nstack` | 50000, 250000, 500000, 150000 | steps in each set-up stage |
| | `E`, `I`, `wrapEuniform` | 9.0, 0.3, 10.0 | face-to-face energy, face-to-side energy, wrapping energy |
| `production.lammps` | `sweep` | none, must be given | sweep folder, e.g. `sweeps/sweep01` |
| | `job` | every job in the sweep | which job to run |
| | `nsteps` | 10000000 | length of the production run |

In production, `E`, `I` and `wrapEuniform` come from the sweep's job files.

> [!WARNING]
> Don't use `-var id` or `-var job` in partition mode: every partition would get the same value. Don't start two partition-mode batches from the same folder at once: they share the job counter file `tmp.lammps.variable`.

# Calculate radius of gyration

``` console
python scripts/python/calculate_rg.py
```
Currently no CLI inputs, takes in default dump file. Writes `figures/rg_over_time.png` and `data_files/rg_sq_data.dat`.

# vmd commands

To run the dump file straight from the terminal adding the dump file as a lammps trajectory molecule and updating the colours in one go
``` console
vmd -lammpstrj <path_to_dump_file> -e scripts/vmd/colours.tcl
```
For example `init_configs/dump_initial_1.nucleosomes`, or `sweeps/sweep01/runs/<run>/dump.nucleosomes`.
