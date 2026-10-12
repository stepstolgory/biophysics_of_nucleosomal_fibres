#!/bin/bash

# Make a sweep folder: a table of jobs (jobs.txt) and one small LAMMPS file per job.
#
# Usage (from the repo root):
#   scripts/make_sweep.sh -n NAME -E "E values" [-I "I values"] [-W "wrap values"] [-r REPS] [-s START_DIR]
# Example: 5 values of E at I = 0.3, 5 repeats each (25 jobs)
#   scripts/make_sweep.sh -n sweep01 -E "2.0 4.0 6.0 8.0 10.0" -I "0.3" -r 5
#
# Repeat r always starts from START_DIR/init_config_r.init and uses seeds/seed_r.lammps.

# Defaults, changed by the options below
NAME=""
E_LIST=""
I_LIST="0.3"
W_LIST="10.0"
REPS=5
START_DIR="init_configs"

# Read the options. "n:" means -n must be followed by a value, which lands in $OPTARG.
while getopts "n:E:I:W:r:s:" opt; do
  case $opt in
  n) NAME=$OPTARG ;;
  E) E_LIST=$OPTARG ;;
  I) I_LIST=$OPTARG ;;
  W) W_LIST=$OPTARG ;;

  r) REPS=$OPTARG ;;
  s) START_DIR=$OPTARG ;;
  *) exit 1 ;;
  esac
done

if [[ -z $NAME || -z $E_LIST ]]; then
  echo "Usage: $0 -n NAME -E \"E values\" [-I \"I values\"] [-W \"wrap values\"] [-r REPS] [-s START_DIR]" >&2
  exit 1
fi

DIR="sweeps/$NAME"

if [[ -e $DIR ]]; then
  echo "Error: $DIR already exists. Pick a new name so old results are never overwritten." >&2
  exit 1
fi

# Warn now about missing files, rather than halfway through a sweep
for ((rep = 1; rep <= REPS; rep++)); do
  [[ -f $START_DIR/init_config_${rep}.init ]] || echo "Warning: $START_DIR/init_config_${rep}.init does not exist yet" >&2
  [[ -f seeds/seed_${rep}.lammps ]] || echo "Warning: seeds/seed_${rep}.lammps does not exist yet" >&2
done

mkdir -p "$DIR/jobs" "$DIR/runs"

# Header lines for jobs.txt
{
  echo "# Made $(date '+%Y-%m-%d %H:%M') at commit $(git rev-parse --short HEAD)"
  echo "# Command: $0 -n \"$NAME\" -E \"$E_LIST\" -I \"$I_LIST\" -W \"$W_LIST\" -r $REPS -s \"$START_DIR\""

  echo "# job E I wrapEuniform rep start run_dir"
} >"$DIR/jobs.txt"

job=0
for ((rep = 1; rep <= REPS; rep++)); do # rep is the outer loop
  for I in $I_LIST; do

    for E in $E_LIST; do
      for W in $W_LIST; do
        job=$((job + 1))
        start="$START_DIR/init_config_${rep}.init"
        run_dir="$DIR/runs/E${E}_I${I}_W${W}_r${rep}"
        mkdir -p "$run_dir"

        # string variables, so the next job in the same LAMMPS process can replace them

        cat >"$DIR/jobs/job_${job}.lammps" <<END
variable E            string $E
variable I            string $I
variable wrapEuniform string $W
variable rep          string $rep
variable start        string $start
variable run_dir      string $run_dir
END
        echo "$job $E $I $W $rep $start $run_dir" >>"$DIR/jobs.txt"
      done
    done
  done
done

echo "variable njobs index $job" >"$DIR/sweep.lammps"
echo "Made $job jobs in $DIR"
