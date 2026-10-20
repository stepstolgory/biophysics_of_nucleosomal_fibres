#!/bin/bash

# Full sweep from scratch:
#   seeds and starting structures -> set-up -> untangle -> make the sweep -> run every job
# This is scripts/test_pipeline.sh done for every id and every parameter value at once.
#
# Usage (from the repo root, with the python environment active):
#   scripts/run_full_sweep.sh [all | prepare | sweep]
#     all       everything (the default)
#     prepare   only seeds, structures, set-up and untangle. Stop here to look at the
#               untangled fibres in VMD before spending hours on production.
#     sweep     only make the sweep and run it, using untangled configurations that already exist
#
# To keep going after you log out (put "nice -n 10" in front on a shared machine):
#   nohup scripts/run_full_sweep.sh > full_sweep_sweep01.out 2>&1 &
#   tail -f full_sweep_sweep01.out
#
# Settings are environment variables. Example:
#   SWEEP=sweep02 E_LIST="4.0 8.0" MAXPAR=10 scripts/run_full_sweep.sh
#
#   SWEEP          name of the new sweep folder, never reused           sweep01
#   E_LIST         face-to-face energies (E in the LAMMPS scripts)      "2.0 4.0 6.0 8.0 10.0"
#   I_LIST         face-to-side energies (I)                            "0.3"
#   W_LIST         wrapping energies (wrapEuniform)                     "10.0"
#   REPS           repeats of every parameter set. Repeat r starts      5
#                  from configuration r and uses seeds/seed_r.lammps
#   NIDS           how many starting configurations to make             10
#   NNUC           nucleosomes, only for structures not made yet        20
#   MAXPAR         most LAMMPS processes running at once                25
#   NSTEPS         production steps, empty = production.lammps          (empty)
#   SETUP_ARGS     extra LAMMPS arguments for setup.lammps              (empty)
#   UNTANGLE_ARGS  extra LAMMPS arguments for untangle.lammps,          (empty)
#                  for example UNTANGLE_ARGS="-var nuntangle 50000"
#   LMP            LAMMPS executable                                    LAMMPS/lmp_mpi
#   RESUME         1 = keep set-up and untangle files, and a sweep      0
#                  folder, that already exist, so a stopped run carries on
#   MB_PER_ID, MB_PER_JOB   guesses of the dump size, for the disk check    300, 150
#
# E_LIST and I_LIST follow the README example and the 3 low plus 2 high split in the meeting
# notes. Check them against the phase diagram before a real run.

SWEEP=${SWEEP:-sweep01}
E_LIST=${E_LIST:-"2.0 4.0 6.0 8.0 10.0"}
I_LIST=${I_LIST:-"0.3"}
W_LIST=${W_LIST:-"10.0"}
REPS=${REPS:-5}
NIDS=${NIDS:-10}
NNUC=${NNUC:-20}
MAXPAR=${MAXPAR:-25}
NSTEPS=${NSTEPS:-}
SETUP_ARGS=${SETUP_ARGS:-}
UNTANGLE_ARGS=${UNTANGLE_ARGS:-}
LMP=${LMP:-LAMMPS/lmp_mpi}
RESUME=${RESUME:-0}
MB_PER_ID=${MB_PER_ID:-300}
MB_PER_JOB=${MB_PER_JOB:-150}
PHASE=${1:-all}

say() { echo "$(date '+%H:%M:%S')  $*"; }
stage() {
  echo
  say "=== $*"
}
fail() {
  echo "Error: $*" >&2
  exit 1
}

###############################################
# Checks, before anything is made
###############################################

case $PHASE in
all | prepare | sweep) ;;
*) fail "unknown stage '$PHASE'. Use all, prepare or sweep" ;;
esac

[[ -f scripts/lammps/setup.lammps ]] || fail "run this from the repo root"
command -v "$LMP" >/dev/null || fail "LAMMPS not found at $LMP (set LMP=...)"

for v in REPS NIDS MAXPAR; do
  [[ ${!v} =~ ^[1-9][0-9]*$ ]] || fail "$v must be a whole number above 0 (it is '${!v}')"
done
((REPS <= NIDS)) || fail "REPS ($REPS) cannot be more than NIDS ($NIDS), as repeat r starts from configuration r"
[[ $SWEEP =~ ^[A-Za-z0-9_.-]+$ ]] || fail "SWEEP should be a plain folder name, like sweep01 (it is '$SWEEP')"

read -ra e_vals <<<"$E_LIST"
read -ra i_vals <<<"$I_LIST"
read -ra w_vals <<<"$W_LIST"
read -ra setup_args <<<"$SETUP_ARGS"
read -ra untangle_args <<<"$UNTANGLE_ARGS"
NJOBS=$((${#e_vals[@]} * ${#i_vals[@]} * ${#w_vals[@]} * REPS))
((NJOBS > 0)) || fail "E_LIST, I_LIST and W_LIST each need at least one value"
for v in "${e_vals[@]}" "${i_vals[@]}" "${w_vals[@]}"; do
  [[ $v =~ ^[0-9]+(\.[0-9]+)?$ ]] || fail "energies must be plain numbers like 4.0 (got '$v')"
done

# Old set-up files may be from before your latest fixes, and the later stages would quietly use them
if [[ $PHASE != sweep && $RESUME != 1 ]]; then
  old=()
  for ((id = 1; id <= NIDS; id++)); do
    for f in init_configs/init_config_${id}.init init_configs/untangled/init_config_${id}.init; do
      [[ -e $f ]] && old+=("$f")
    done
  done
  if ((${#old[@]} > 0)); then
    echo "Error: files from an earlier run already exist:" >&2
    printf '  %s\n' "${old[@]}" >&2
    echo "They may be older than your latest fixes. Move or delete them, or use RESUME=1 to keep and use them." >&2
    exit 1
  fi
fi

if [[ $PHASE != prepare && $RESUME != 1 && -e sweeps/$SWEEP ]]; then
  fail "sweeps/$SWEEP already exists. Pick a new name with SWEEP=..., or use RESUME=1 to carry on with it"
fi

need_mb=0
[[ $PHASE != sweep ]] && need_mb=$((need_mb + NIDS * MB_PER_ID))
[[ $PHASE != prepare ]] && need_mb=$((need_mb + NJOBS * MB_PER_JOB))
free_mb=$(df -Pk . | awk 'NR == 2 {print int($4 / 1024)}')
((free_mb >= need_mb)) || fail "about $need_mb MB of dumps expected but only $free_mb MB is free here"

cores=$(nproc --all 2>/dev/null || echo "?")
[[ -n $(git status --porcelain --untracked-files=no) ]] &&
  echo "Warning: uncommitted changes, so the commit recorded in jobs.txt will not match exactly what ran" >&2

steps_text="${NSTEPS:-$(awk '$1 == "variable" && $2 == "nsteps" {print $4; exit}' scripts/lammps/production.lammps)} steps per job"
[[ -z $NSTEPS ]] && steps_text="$steps_text (the production.lammps default)"
echo "Plan (stage: $PHASE)"
echo "  git:            $(git rev-parse --abbrev-ref HEAD) at $(git rev-parse --short HEAD)"
echo "  start configs:  1 to $NIDS (set-up, then untangle)"
echo "  sweep:          sweeps/$SWEEP, $NJOBS jobs = ${#e_vals[@]} E x ${#i_vals[@]} I x ${#w_vals[@]} wrapping x $REPS repeats"
echo "  E:              $E_LIST"
echo "  I:              $I_LIST"
echo "  wrapEuniform:   $W_LIST"
echo "  production:     $steps_text"
echo "  set-up args:    ${SETUP_ARGS:-none, script defaults}"
echo "  untangle args:  ${UNTANGLE_ARGS:-none, script defaults}"
echo "  at most:        $MAXPAR processes at once ($cores cores here)"
echo "  disk:           about $need_mb MB needed, $free_mb MB free"
echo "  machine load:   $(uptime | sed 's/.*load average: *//')"

# One core per run. This stops a LAMMPS build with OpenMP from starting extra threads.
export OMP_NUM_THREADS=1

###############################################
# Seeds and starting structures
###############################################

if [[ $PHASE != sweep ]]; then
  stage "Seeds and starting structures (ids 1 to $NIDS)"

  # Python and the builder are only needed if something has to be made
  make_needed=0
  for ((id = 1; id <= NIDS; id++)); do
    [[ -f seeds/seed_${id}.lammps && -f initial_positions/data_${id}.lammps ]] || make_needed=1
  done
  if ((make_needed)); then
    python -c "import numpy" 2>/dev/null || fail "numpy not found. Activate the python environment first (the README uses 'conda activate mphy')"
    if [[ ! -x initial_condition_builder/generate_ic ]]; then
      # The compiler warnings are only shown if the build fails
      make -C initial_condition_builder >initial_condition_builder/make.log 2>&1 || {
        grep -i "error" initial_condition_builder/make.log | head -10 >&2
        fail "could not build initial_condition_builder (full output in initial_condition_builder/make.log)"
      }
    fi
  fi

  # Both scripts keep files that already exist
  scripts/generate_random_thermal_seeds.sh "$NIDS" | grep -v "already exists"
  scripts/generate_random_IC.sh "$NIDS" "$NNUC" | grep -v "already exists"

  data_files=()
  for ((id = 1; id <= NIDS; id++)); do
    [[ -f initial_positions/data_${id}.lammps ]] || fail "initial_positions/data_${id}.lammps was not made (see initial_positions/generate_ic_${id}.log)"
    [[ -f seeds/seed_${id}.lammps ]] || fail "seeds/seed_${id}.lammps was not made"
    # LAMMPS only accepts seeds from 1 to 900,000,000
    awk '$1 == "variable" && ($2 == "seed" || $2 == "seed2") && $3 == "equal" && $4 ~ /^[0-9]+$/ && $4 >= 1 && $4 <= 900000000 {n++} END {exit n != 2}' "seeds/seed_${id}.lammps" ||
      fail "seeds/seed_${id}.lammps should hold a seed and a seed2, each from 1 to 900000000. Delete it and run again"
    data_files+=("initial_positions/data_${id}.lammps")
  done

  # The old seed bug made every structure the same, so check they differ
  dupes=$(md5sum "${data_files[@]}" | sort | uniq -w32 -D)
  [[ -z $dupes ]] || fail "some starting structures are identical:
$dupes
Delete the copies and run again to make new ones"

  sizes=$(for f in "${data_files[@]}"; do awk '/ atoms$/ {print $1; exit}' "$f"; done | sort -u)
  [[ $(echo "$sizes" | wc -l) -eq 1 ]] || fail "the starting structures do not all have the same number of atoms: $(echo "$sizes" | tr '\n' ' ')"
  say "$NIDS starting structures, all different, $sizes atoms each"

  # With boundary s s s, LAMMPS drops every atom that is outside the box in the data file header
  # and stops with "Did not assign all atoms correctly". generate_ic writes a box of -50 to 50,
  # which most fibres outgrow. This only edits the box lines of a file, and only if needed.
  fitted=$(scripts/fit_box.sh -q "${data_files[@]}")
  fit_rc=$?
  [[ -n $fitted ]] && echo "$fitted"
  ((fit_rc == 0)) || fail "scripts/fit_box.sh could not fix the box of a starting structure (see above)"
  [[ -n $fitted ]] && echo "Only the box lines of the files above changed, not the atom positions. Commit them so the repository matches what was run."

  ###############################################
  # Set-up, then untangle, one single-core process per id
  ###############################################

  stage "Set-up and untangle (ids 1 to $NIDS, at most $MAXPAR at once)"

  # LAMMPS does not make folders, and stops with a poor error if one is missing
  mkdir -p init_configs/untangled init_configs/logs

  # Set-up, then untangle, for one id. A stage is skipped if its output is already there.
  prepare_id() {
    local id=$1 rc
    local setup_out=init_configs/init_config_${id}.init
    local untangle_out=init_configs/untangled/init_config_${id}.init

    if [[ -f $untangle_out ]]; then
      say "id $id: already prepared, keeping $untangle_out"
      return 0
    fi

    if [[ ! -f $setup_out ]]; then
      say "id $id: set-up started"
      "$LMP" -in scripts/lammps/setup.lammps -var id "$id" -log none "${setup_args[@]}" \
        </dev/null >"init_configs/logs/stdout_setup_${id}.out" 2>&1
      rc=$?
      if [[ ! -f $setup_out ]]; then
        say "id $id: set-up FAILED (exit code $rc). See init_configs/logs/stdout_setup_${id}.out and init_configs/log_initial_${id}.out"
        return 1
      fi
      say "id $id: set-up finished"
    fi

    say "id $id: untangle started"
    "$LMP" -in scripts/lammps/untangle.lammps -var id "$id" -log none "${untangle_args[@]}" \
      </dev/null >"init_configs/logs/stdout_untangle_${id}.out" 2>&1
    rc=$?
    if [[ ! -f $untangle_out ]]; then
      say "id $id: untangle FAILED (exit code $rc). See init_configs/logs/stdout_untangle_${id}.out and init_configs/logs/log_untangle_${id}.out"
      return 1
    fi
    say "id $id: untangle finished"
  }

  for ((id = 1; id <= NIDS; id++)); do
    while (($(jobs -rp | wc -l) >= MAXPAR)); do sleep 5; done
    prepare_id "$id" &
  done
  wait

  # Only the first REPS ids are needed for the sweep, the others are spares
  missing_needed=()
  missing_spare=()
  for ((id = 1; id <= NIDS; id++)); do
    [[ -f init_configs/untangled/init_config_${id}.init ]] && continue
    if ((id <= REPS)); then missing_needed+=("$id"); else missing_spare+=("$id"); fi
  done
  ((${#missing_spare[@]} > 0)) && echo "Warning: no untangled configuration for id ${missing_spare[*]}. Not needed for this sweep." >&2
  ((${#missing_needed[@]} > 0)) && fail "no untangled configuration for id ${missing_needed[*]}. Fix the problem, then run again with RESUME=1"

  say "untangled configurations ready: init_configs/untangled/init_config_<id>.init"
fi

if [[ $PHASE == prepare ]]; then
  echo
  echo "Check the untangled fibres before the sweep (movie, not just the last frame), for example:"
  echo "  vmd -lammpstrj init_configs/untangled/dump_initial_1.nucleosomes -e scripts/vmd/colours.tcl"
  echo "Then run the rest with the same settings:  scripts/run_full_sweep.sh sweep"
  exit 0
fi

###############################################
# Make the sweep and run every job
###############################################

stage "Make the sweep: sweeps/$SWEEP"

for ((rep = 1; rep <= REPS; rep++)); do
  [[ -f init_configs/untangled/init_config_${rep}.init ]] || fail "init_configs/untangled/init_config_${rep}.init is missing. Run 'scripts/run_full_sweep.sh prepare' first"
  [[ -f seeds/seed_${rep}.lammps ]] || fail "seeds/seed_${rep}.lammps is missing"
done

if [[ -d sweeps/$SWEEP ]]; then
  say "sweeps/$SWEEP already exists, using it (RESUME=1). It was made with:"
  grep '^#' "sweeps/$SWEEP/jobs.txt" | sed 's/^/    /'
else
  scripts/make_sweep.sh -n "$SWEEP" -E "$E_LIST" -I "$I_LIST" -W "$W_LIST" -r "$REPS" -s init_configs/untangled ||
    fail "make_sweep.sh failed"
  made=$(awk '!/^#/ && NF {n++} END {print n + 0}' "sweeps/$SWEEP/jobs.txt")
  ((made == NJOBS)) || fail "sweeps/$SWEEP has $made jobs, expected $NJOBS"
fi

stage "Production: $NJOBS jobs, at most $MAXPAR at once"

export LMP NSTEPS
scripts/run_sweep.sh "sweeps/$SWEEP" "$MAXPAR" || {
  # Repeat any non-default setting, or the redone jobs would not match the rest of the sweep
  redo="scripts/run_sweep.sh sweeps/$SWEEP $MAXPAR"
  [[ -n $NSTEPS ]] && redo="NSTEPS=$NSTEPS $redo"
  [[ $LMP != LAMMPS/lmp_mpi ]] && redo="LMP=$LMP $redo"
  echo
  echo "Some jobs did not finish. After fixing the cause, redo only those with:" >&2
  echo "  $redo" >&2
  exit 1
}

stage "Done in $((SECONDS / 3600)) h $((SECONDS % 3600 / 60)) min"
echo "Run folders:  sweeps/$SWEEP/runs/"
echo "To keep a record of this sweep in git:  git add sweeps/$SWEEP"
