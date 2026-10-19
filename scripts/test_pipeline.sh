#!/bin/bash
# Test pipeline for ONE id, from scratch:
#   seeds -> starting structure -> set-up -> untangle -> sweep (1 job) -> production
#
# Usage (from the repo root, with the python environment active):
#   scripts/test_pipeline.sh
#   nohup scripts/test_pipeline.sh > pipeline_test.out 2>&1 &     # keeps going after you log out
#
# Settings you can change with environment variables, for example:
#   NSTEPS=10000000 scripts/test_pipeline.sh
#   LMP=/path/to/lmp_mpi SWEEP=sweep_test scripts/test_pipeline.sh
#
#   NNUC    number of nucleosomes (default 20)
#   NSTEPS  length of the production run (default 200000, a short test)
#   SWEEP   name of the sweep folder (default untangled_test)
#   LMP     LAMMPS executable (default LAMMPS/lmp_mpi)
#
# It stops at the first stage that fails. It will not run if files for this id
# already exist, so clear them first (see the clear commands).

set -euo pipefail

ID=1 # the sweep stage always uses repeat 1, so this test is for id 1 only
NNUC=${NNUC:-20}
NSTEPS=${NSTEPS:-200000}
SWEEP=${SWEEP:-untangled_test}
LMP=${LMP:-LAMMPS/lmp_mpi}

stage() { echo; echo "=== $(date '+%H:%M:%S')  $*"; }
fail() { echo "Error: $*" >&2; exit 1; }

# Needs to be run from the repo root
[[ -f scripts/lammps/setup.lammps ]] || fail "run this from the repo root"

# Checks before anything is made
[[ -x $LMP ]] || fail "LAMMPS not found at $LMP (set LMP=...)"
python -c "import numpy" 2>/dev/null || fail "numpy not found, run 'conda activate daml' first"

# Stop if an old copy is there, as the generators would quietly keep it
for f in initial_positions/data_${ID}.lammps seeds/seed_${ID}.lammps \
  init_configs/init_config_${ID}.init init_configs/untangled/init_config_${ID}.init \
  sweeps/${SWEEP}; do
  [[ -e $f ]] && fail "$f already exists, clear the old files first"
done

# LAMMPS does not make folders, and stops with a poor error if one is missing
mkdir -p init_configs/untangled init_configs/logs

stage "Build the structure builder, if needed"
[[ -x initial_condition_builder/generate_ic ]] || make -C initial_condition_builder

stage "Seeds and starting structure for id $ID"
scripts/generate_random_thermal_seeds.sh "$ID"
scripts/generate_random_IC.sh "$ID" "$NNUC"
[[ -f initial_positions/data_${ID}.lammps ]] || fail "no starting structure was made"
[[ -f seeds/seed_${ID}.lammps ]] || fail "no seed file was made"

stage "Set-up (equilibration)"
"$LMP" -in scripts/lammps/setup.lammps -var id "$ID" -log none -screen none
[[ -f init_configs/init_config_${ID}.init ]] || fail "set-up did not write init_configs/init_config_${ID}.init"

stage "Untangle"
"$LMP" -in scripts/lammps/untangle.lammps -var id "$ID" -log none -screen none
[[ -f init_configs/untangled/init_config_${ID}.init ]] || fail "untangle did not write init_configs/untangled/init_config_${ID}.init"

stage "Make the sweep (one job)"
scripts/make_sweep.sh -n "$SWEEP" -E "9.0" -I "0.3" -W "10.0" -r 1 -s init_configs/untangled

stage "Production (job 1, $NSTEPS steps)"
"$LMP" -in scripts/lammps/production.lammps -var sweep "sweeps/$SWEEP" -var job 1 -var nsteps "$NSTEPS" -log none -screen none
run_dir=$(awk '!/^#/ && $1 == 1 {print $7}' "sweeps/$SWEEP/jobs.txt")
[[ -f $run_dir/final.data ]] || fail "production did not write $run_dir/final.data"

stage "Done"
echo "Production output: $run_dir"
echo "Look at the movies:"
echo "  vmd -lammpstrj init_configs/dump_initial_${ID}.nucleosomes -e scripts/vmd/colours.tcl"
echo "  vmd -lammpstrj init_configs/untangled/dump_initial_${ID}.nucleosomes -e scripts/vmd/colours.tcl"
echo "  vmd -lammpstrj $run_dir/dump.nucleosomes -e scripts/vmd/colours.tcl"
