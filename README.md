# biophysics_of_nucleosomal_fibres

This repository is the code base for the MPhys dissertation project of the same name. The code is intended to measure the behaviour of nucleosomes using a new coarse grained model simulated in LAMMPS.

Make sure to push changes to the repository after finishing a session.

# Initial setup
Make sure to enter a supported python environment
``` console
conda activate mphys
```

Build the initial condition builder (once on each machine, it is not kept in git)
``` console
make -C initial_condition_builder
```
LAMMPS itself goes in `LAMMPS/` (also not in git), so the commands below use `LAMMPS/lmp_mpi`. Run every command from the repo root.

# Folder structure

```
.
├── initial_condition_builder/   C++ code that builds the straight starting chain
│   ├── generate_IC_unwrapableNuclesomes.cpp
│   ├── nucleosome.h
│   └── Makefile                 run `make` here to build generate_ic
├── initial_positions/           structures from the builder (data_<id>.lammps)
│   └── ic_seeds.txt             builder seed for each structure
├── seeds/                       LAMMPS seed files (seed_<rep>.lammps)
├── init_configs/                starting configurations from the set-up script
├── scripts/
│   ├── lammps/                  set-up and production LAMMPS scripts
│   ├── python/                  analysis and plotting scripts
│   ├── vmd/                     VMD scripts for viewing runs ?
│   ├── generate_random_IC.sh    makes structures with random seeds
│   ├── generate_random_thermal_seeds.sh   makes the LAMMPS seed files
│   ├── make_sweep.sh            makes a sweep folder
│   ├── run_sweep.sh             runs a sweep as separate processes
├── src/mphys/                   shared Python code (reading files, plotting)
├── tests/                       tests for src/mphys and the analysis scripts
├── sweeps/                      one folder per sweep: jobs.txt, job files, runs
├── data_files/                  analysis output (.dat), one folder per sweep
├── figures/                     plots, same layout as data_files/
├── pyproject.toml               Python package set-up (`pip install -e .`)
├── README.md
└── RUNS.md                      log of test runs (T1, T2, ...)
```

`sweeps/` is a link to `/storage/teaching/MPhysProject/s2289431/sweeps`, as the
dump files are too big for the home directory. Dumps and data files are not
tracked by git.

`init_configs` contains multiple sub-folders.
```
.
├── 20_nuc_IC                   eight 20 nucleosomes initial conditions that have been manually confirmed as GOOD. These are tracked in Git.
├── logs                        all logs
├── sweep02                     initial conditions that were used for sweep02
├── tangled                     initial conditions that only went through setup.lammps so are likely still untangled
└── untangled                   initial conditions that have gone through both the setup.lammps and the untangle.lammps script
```

# Make starting structures and seeds
``` console
scripts/generate_random_IC.sh 10            # structures 1 to 10 (a second number sets the nucleosomes, default 20)
scripts/generate_random_thermal_seeds.sh 10 # seed files 1 to 10
```
Both keep files that already exist, so they can be run again with a bigger number to add more.

`generate_ic` always writes a box of -50 to 50, but many fibres grow past that. With `boundary s s s` LAMMPS throws away every atom outside the box in the data file and stops with `Did not assign all atoms correctly`. So `generate_random_IC.sh` runs `scripts/fit_box.sh`, which widens the box lines of a file when atoms are outside (atom positions are never changed). To check or fix structures made another way:
``` console
scripts/fit_box.sh initial_positions/data_*.lammps
```

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
