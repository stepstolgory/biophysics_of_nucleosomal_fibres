#!/bin/bash
# Usage: ./make_ics.sh N [seed_file]
#   N          number of initial conditions to make
#   seed_file  optional: one seed per line. If given, these seeds are used
#              instead of generating new ones (line 1 -> id 1, and so on).

N=$1
SEED_FILE=$2

if [[ -z "$N" ]]; then

  echo "Usage: $0 N [seed_file]" >&2

  exit 1
fi

if [[ -n "$SEED_FILE" ]]; then

  if [[ ! -f "$SEED_FILE" ]]; then
    echo "Error: seed file '$SEED_FILE' not found" >&2
    exit 1

  fi
  # Read seeds into an array, skipping blank lines and lines starting with #
  mapfile -t SEEDS < <(grep -v -e '^[[:space:]]*$' -e '^[[:space:]]*#' "$SEED_FILE")
  if ((${#SEEDS[@]} < N)); then
    echo "Error: asked for $N runs but '$SEED_FILE' only has ${#SEEDS[@]} seeds" >&2
    exit 1
  fi
fi

for ((a = 1; a <= N; a++)); do
  if [[ -n "$SEED_FILE" ]]; then
    SEED=${SEEDS[$((a - 1))]}
  else
    SEED=$(python scripts/python/random_seed.py)
    echo "$SEED" >>seeds.txt
  fi
  id=$a
  ./initial_condition_builder/generate_ic -f initial_positions/data_${id}.lammps -s "${SEED}" &>/dev/null
done
