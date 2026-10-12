#!/bin/bash
# Usage: scripts/generate_random_IC.sh N [NNUC]
#   N     make starting structures 1 to N (ones that already exist are kept)

#   NNUC  number of nucleosomes (default 20)
# Run from the repo root.

N=$1
NNUC=${2:-20}

# Linker lengths, in beads (5 bp each)
L1=5 # before the first nucleosome
L=8  # between nucleosomes
LF=5 # after the last nucleosome

if [[ -z "$N" ]]; then
  echo "Usage: $0 N [NNUC]" >&2
  exit 1
fi

# Start the seed list with a header saying how the structures were made
if [[ ! -f ic_seeds.txt ]]; then
  echo "# id seed   made with: generate_ic -e 1 -N $NNUC -L1 $L1 -L $L -LF $LF" >ic_seeds.txt
fi

for ((id = 1; id <= N; id++)); do
  out=initial_positions/data_${id}.lammps

  # Never touch a structure that already exists
  if [[ -f $out ]]; then
    echo "$out already exists, keeping it"
    continue
  fi

  SEED=$(python scripts/python/random_seed.py)

  # Only the seed is in quotes. Each flag and value is its own word.
  if ./initial_condition_builder/generate_ic -f "$out" -s "$SEED" -e 1 -N "$NNUC" -L1 "$L1" -L "$L" -LF "$LF" \
    >initial_positions/generate_ic_${id}.log 2>&1; then
    echo "$id $SEED" >>ic_seeds.txt
    echo "made $out (seed $SEED)"
  else
    echo "Error: generate_ic failed for id $id, see initial_positions/generate_ic_${id}.log" >&2
  fi
done
