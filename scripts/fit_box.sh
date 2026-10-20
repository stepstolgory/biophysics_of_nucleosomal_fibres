#!/bin/bash
# Make sure every atom of a LAMMPS data file is inside the box given in its header.
# Usage: scripts/fit_box.sh [-q] FILE...
#   -q  only say something about files that were changed or have a problem
#
# Why: with "boundary s s s", read_data throws away every atom that is outside the box in the
# header and then stops with "Did not assign all atoms correctly". generate_ic always writes a
# box of -50 to 50, but a fibre can grow past that (to z = 78 in one of the first ten structures).
# With the old periodic box such atoms were wrapped back in, so nobody saw the problem.
#
# What it does: if every atom is inside, the file is not touched. If not, the box lines of the
# header (xlo xhi, ylo yhi, zlo zhi) are widened, only where needed, until every atom is inside
# with 10 to spare. The box is never made smaller. Atom positions and everything else in the file
# stay exactly as they were. Shrink-wrapped boundaries resize the box to fit the atoms as soon as
# the file is read, so the size in the header does not change the simulation.

export LC_ALL=C # so awk always reads 50.5 and never 50,5

MARGIN=10

QUIET=0
if [[ $1 == -q ]]; then
  QUIET=1
  shift
fi

if (($# == 0)); then
  echo "Usage: $0 [-q] FILE..." >&2
  exit 1
fi

# Reads a data file and prints one line:
#   atoms found, atoms the header promises, box lines found, atoms outside the header box,
#   then the box the file needs: xlo xhi ylo yhi zlo zhi
needed_box() {
  awk -v margin="$MARGIN" '
    BEGIN { OFMT = "%.10g" }
    function floor(x) { return (x == int(x) || x > 0) ? int(x) : int(x) - 1 }
    function ceil(x)  { return (x == int(x) || x < 0) ? int(x) : int(x) + 1 }

    $3 == "xlo" && $4 == "xhi" { lo[1] = $1 + 0; hi[1] = $2 + 0; boxlines++ }
    $3 == "ylo" && $4 == "yhi" { lo[2] = $1 + 0; hi[2] = $2 + 0; boxlines++ }
    $3 == "zlo" && $4 == "zhi" { lo[3] = $1 + 0; hi[3] = $2 + 0; boxlines++ }
    NF == 2 && $2 == "atoms"   { expected = $1 + 0 }

    # The Atoms section runs from the heading to the next blank line. Each line is: id type x y z ...
    $1 == "Atoms" { inatoms = 1; next }
    inatoms && NF == 0 { if (found > 0) inatoms = 0; next }
    inatoms {
      if ($1 !~ /^[0-9]+$/) { inatoms = 0; next }
      found++
      isout = 0
      for (d = 1; d <= 3; d++) {
        c = $(2 + d) + 0
        if (found == 1 || c < mn[d]) mn[d] = c
        if (found == 1 || c > mx[d]) mx[d] = c
        if (c < lo[d] || c >= hi[d]) isout = 1 # LAMMPS keeps an atom only if lo <= c < hi
      }
      outside += isout
    }

    END {
      for (d = 1; d <= 3; d++) {
        if (found > 0 && mn[d] < lo[d])  lo[d] = floor(mn[d] - margin)
        if (found > 0 && mx[d] >= hi[d]) hi[d] = ceil(mx[d] + margin)
      }
      print found + 0, expected + 0, boxlines + 0, outside + 0, lo[1], hi[1], lo[2], hi[2], lo[3], hi[3]
    }
  ' "$1"
}

status=0
for f in "$@"; do
  if [[ ! -f $f ]]; then
    echo "Error: $f not found" >&2
    status=1
    continue
  fi

  read -r found expected boxlines outside xlo xhi ylo yhi zlo zhi < <(needed_box "$f")
  if ((boxlines != 3 || expected == 0 || found != expected)); then
    echo "Error: $f does not read as a LAMMPS data file (atoms found: $found, header says: $expected, box lines found: $boxlines of 3)" >&2
    status=1
    continue
  fi

  if ((outside == 0)); then
    ((QUIET)) || echo "$f: all $found atoms are inside the box, nothing to change"
    continue
  fi

  # Make the widened copy first, so the real file is only touched once the copy has passed the checks
  tmp=$(mktemp) || {
    echo "Error: could not make a temporary file" >&2
    status=1
    continue
  }
  awk -v xlo="$xlo" -v xhi="$xhi" -v ylo="$ylo" -v yhi="$yhi" -v zlo="$zlo" -v zhi="$zhi" '
    $3 == "xlo" && $4 == "xhi" { print xlo, xhi, "xlo xhi"; next }
    $3 == "ylo" && $4 == "yhi" { print ylo, yhi, "ylo yhi"; next }
    $3 == "zlo" && $4 == "zhi" { print zlo, zhi, "zlo zhi"; next }
    { print }
  ' "$f" >"$tmp"

  # The copy must read the same, have no atom outside, and differ from the original in the box lines only
  read -r new_found _ new_boxlines new_outside _ < <(needed_box "$tmp")
  changed=$(diff "$f" "$tmp" | grep -c '^<')
  if ((new_found != found || new_boxlines != 3 || new_outside != 0 || changed < 1 || changed > 3)); then
    echo "Error: $f: the widened copy failed its checks, so the file was left as it was" >&2
    rm -f "$tmp"
    status=1
    continue
  fi

  # cat and not mv, so the file keeps its permissions
  if ! cat "$tmp" >"$f"; then
    echo "Error: could not write to $f" >&2
    rm -f "$tmp"
    status=1
    continue
  fi
  rm -f "$tmp"
  echo "$f: $outside of $found atoms were outside the box. The box is now x $xlo $xhi, y $ylo $yhi, z $zlo $zhi"
done

exit $status
