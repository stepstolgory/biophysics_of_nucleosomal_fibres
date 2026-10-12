#!/bin/bash
# Usage: scripts/generate_random_thermal_seeds.sh N
#   N  make seed files seeds/seed_1.lammps to seeds/seed_N.lammps (ones that already exist are kept)
# Run from the repo root.

N=$1

if [[ -z "$N" ]]; then
  echo "Usage: $0 N" >&2
  exit 1
fi

for ((a = 1; a <= N; a++)); do
  if [[ -f seeds/seed_$a.lammps ]]; then
    echo "seeds/seed_$a.lammps already exists. Skipping."
  else
    SEED1=$(python scripts/python/random_seed.py)
    SEED2=$(python scripts/python/random_seed.py)

    echo "variable seed equal ${SEED1}" >seeds/seed_$a.lammps
    echo "variable seed2 equal ${SEED2}" >>seeds/seed_$a.lammps
  fi
done
