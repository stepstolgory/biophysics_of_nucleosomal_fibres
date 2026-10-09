#!/bin/bash

N=$1

if [[ -z "$N" ]]; then

  echo "Usage $0 N " >&2

  exit 1
fi

for ((a = 1; a <= N; a++)); do
  SEED1=$(python scripts/python/random_seed.py)
  SEED2=$(python scripts/python/random_seed.py)

  echo "variable seed equal ${SEED1}" >>seeds/seed_$a.lammps
  echo "variable seed2 equal ${SEED2}" >>seeds/seed_$a.lammps

done
