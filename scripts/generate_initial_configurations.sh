#!/bin/bash

# Usage: ./run_all.sh N [seed_file]
#   N          number of runs
#   seed_file  optional, defaults to seeds.txt (one seed per line)

N=$1

SEED_FILE=${2:-seeds.txt}

if [[ -z "$N" ]]; then
  echo "Usage: $0 N [seed_file]" >&2
  exit 1
fi

if [[ ! -f "$SEED_FILE" ]]; then
  echo "Error: seed file '$SEED_FILE' not found" >&2
  exit 1
fi

# Read seeds, skipping blank lines and lines starting with #
mapfile -t ALL_SEEDS < <(grep -v -e '^[[:space:]]*$' -e '^[[:space:]]*#' "$SEED_FILE")

if ((${#ALL_SEEDS[@]} < N)); then
  echo "Error: asked for $N runs but '$SEED_FILE' only has ${#ALL_SEEDS[@]} seeds" >&2
  exit 1

fi

# Keep only the first N seeds
SEEDS=("${ALL_SEEDS[@]:0:N}")

for ((i = 0; i < N; i++)); do
  id=$((i + 1))
  SEED=${SEEDS[$i]}

  # Put the commands that need a seed here.
  # For now this just prints what would run.
  echo "id=${id} seed=${SEED}"

  # echo lmp -in production.lam -var id ${id} -var seed ${SEED}
done
