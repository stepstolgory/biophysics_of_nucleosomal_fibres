# Load the set-up, untangle and production dumps into ONE molecule, so they play as a single movie.
#
# Usage (from the repo root):
#   vmd -e scripts/vmd/stitch.tcl
#   RUN_DIR=sweeps/NAME/runs/RUN_FOLDER vmd -e scripts/vmd/stitch.tcl    # a different production run
#
# Then in the VMD Tk Console, "animate goto N" jumps to frame N (the start frames are printed below).

set id 1
if {[info exists env(RUN_DIR)]} {
  set run_dir $env(RUN_DIR)
} else {
  set run_dir sweeps/untangled_test/runs/E9.0_I0.3_W10.0_r1
}

# Each stage is: name, dump file, stride (1 = every frame, 5 = every fifth frame)
# The dump intervals differ (set-up 5000 steps, untangle 1000, production 10000), so
# playback speed changes at each join. A stride of 5 for untangle would match the set-up.
set stages [list \
  [list setup      init_configs/dump_initial_$id.nucleosomes           1] \
  [list untangle   init_configs/untangled/dump_initial_$id.nucleosomes 1] \
  [list production $run_dir/dump.nucleosomes                           1]]

set mol -1
foreach stage $stages {
  lassign $stage name file stride
  if {![file exists $file]} {
    puts "stitch: $file not found, skipping $name"
    continue
  }
  if {$mol < 0} {
    set mol [mol new $file type lammpstrj first 0 last -1 step $stride waitfor all]
    puts "stitch: $name starts at frame 0"
  } else {
    set first_frame [molinfo $mol get numframes]
    mol addfile $file type lammpstrj first 0 last -1 step $stride waitfor all molid $mol
    puts "stitch: $name starts at frame $first_frame"
  }
}
puts "stitch: [molinfo $mol get numframes] frames in total"

# colours.tcl works on molecule 0, which is the one loaded above in a fresh VMD
source scripts/vmd/colours.tcl
animate goto 0
