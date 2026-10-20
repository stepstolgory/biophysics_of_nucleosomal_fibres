#!/bin/bash

# Run every job of a sweep as its own single-core LAMMPS process, a few at a time.
#
# Usage (from the repo root):
#   scripts/run_sweep.sh SWEEP_DIR MAX_AT_ONCE
# Example:
#   nohup scripts/run_sweep.sh sweeps/sweep01 25 > sweeps/sweep01/launcher.out 2>&1 &
#
# A job counts as finished when its run folder has final.data, so running this again
# only does the jobs that never finished. The screen output of each job goes to
# stdout.out in its run folder, next to log.out.
#
# Settings from the environment:
#   LMP     LAMMPS executable (default LAMMPS/lmp_mpi)
#   NSTEPS  production steps for every job (default: whatever production.lammps says)
#
# To stop it, kill this script first (or it starts new jobs), then the LAMMPS processes:
#   pkill -f run_sweep.sh; pkill -f "sweep sweeps/sweep01"

SWEEP_DIR=${1%/}
MAXPAR=$2
LMP=${LMP:-LAMMPS/lmp_mpi}
NSTEPS=${NSTEPS:-}

say() { echo "$(date '+%H:%M:%S')  $*"; }
fail() {
  echo "Error: $*" >&2
  exit 1
}

if [[ -z $SWEEP_DIR || -z $MAXPAR ]]; then
  echo "Usage: $0 SWEEP_DIR MAX_AT_ONCE   (for example: $0 sweeps/sweep01 25)" >&2
  exit 1
fi

[[ $MAXPAR =~ ^[1-9][0-9]*$ ]] || fail "MAX_AT_ONCE must be a whole number above 0 (it is '$MAXPAR')"
[[ -f scripts/lammps/production.lammps ]] || fail "run this from the repo root"
[[ -f $SWEEP_DIR/jobs.txt ]] || fail "$SWEEP_DIR/jobs.txt not found. Make the sweep with scripts/make_sweep.sh first"
command -v "$LMP" >/dev/null || fail "LAMMPS not found at $LMP (set LMP=...)"

# --all, because plain nproc also obeys OMP_NUM_THREADS, which is set to 1 below
cores=$(nproc --all 2>/dev/null || echo 0)
if ((cores > 0 && MAXPAR > cores)); then
  echo "Warning: MAX_AT_ONCE ($MAXPAR) is more than the $cores cores on this machine" >&2
fi

# One core per run. This stops a LAMMPS build with OpenMP from starting extra threads.
export OMP_NUM_THREADS=1

# The same command for every job, only -var job changes
cmd=("$LMP" -in scripts/lammps/production.lammps -var sweep "$SWEEP_DIR" -log none)
[[ -n $NSTEPS ]] && cmd+=(-var nsteps "$NSTEPS")

total=$(awk '!/^#/ && NF {n++} END {print n + 0}' "$SWEEP_DIR/jobs.txt")
say "$SWEEP_DIR: $total jobs, at most $MAXPAR at once"

# jobs.txt columns: job E I wrapEuniform rep start run_dir
while read -r job _ _ _ _ start run_dir; do
  [[ -z $job || $job == \#* ]] && continue

  if [[ -f $run_dir/final.data ]]; then
    say "job $job already finished, skipping"
    continue
  fi
  if [[ ! -f $start ]]; then
    say "job $job: starting configuration $start is missing, skipping"
    continue
  fi

  # Wait for a free slot
  while (($(jobs -rp | wc -l) >= MAXPAR)); do sleep 5; done

  mkdir -p "$run_dir"
  say "job $job started: $run_dir"
  (
    # /dev/null as input, or anything that reads standard input could eat the rest of jobs.txt
    "${cmd[@]}" -var job "$job" </dev/null >"$run_dir/stdout.out" 2>&1
    rc=$? # saved straight away, before anything else can change $?
    say "job $job ended with exit code $rc"
  ) &
done <"$SWEEP_DIR/jobs.txt"

wait

# Final count: a job is finished if it wrote final.data
finished=0
unfinished=()
while read -r job _ _ _ _ _ run_dir; do
  [[ -z $job || $job == \#* ]] && continue
  if [[ -f $run_dir/final.data ]]; then
    finished=$((finished + 1))
  else
    unfinished+=("$job")
  fi
done <"$SWEEP_DIR/jobs.txt"

say "$finished of $total jobs finished"
if ((${#unfinished[@]} > 0)); then
  echo "Not finished: ${unfinished[*]}"
  echo "The reason is at the end of log.out and stdout.out in each run folder."
  echo "Run this script again to redo only these jobs."
  exit 1
fi
