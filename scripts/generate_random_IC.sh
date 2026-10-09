#!/bin/bash
# Usage: ./generate_random_IC.sh N
#   N          number of initial conditions to make

N=$1

if [[ -z "$N" ]]; then

  echo "Usage: $0 N [seed_file]" >&2

  exit 1
fi

for ((a = 1; a <= N; a++)); do
  SEED=$(python scripts/python/random_seed.py)
  echo "$a $SEED" >>seeds.txt
  id=$a
  ./initial_condition_builder/generate_ic -f initial_positions/data_${id}.lammps -s "${SEED}" &>/dev/null
done
