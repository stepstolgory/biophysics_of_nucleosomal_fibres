# Tests ran

This file describes various tests that were run in many areas of the program.

### LAMMPS tests


#### T1: Split set-up script (2026-10-08 16:03)

**Aim:** Check that the new set-up (equilibration) script runs on its own and writes a data file.

**Setup:**
- Script: `scripts/lammps/in.lammps_twistable_nucInteractions`
- Parameters: E = 9.0, I = 0.3, 10 nucleosomes
- Seeds: 54654651, 84575451
- Git commit: `79397dd`

**Command:**
```bash
nohup LAMMPS/lmp_mpi -in scripts/lammps/in.lammps_twistable_nucInteractions -var out initial_condition_test1 -log tests/outputs/initial_condition_test1.lammps -screen none > /dev/null 2>&1 &
```

**Outputs:**
- `init_configs/initial_condition_test1.init`
- `sim_outputs/initial/initial_condition_test1.nucleosomes`
- `tests/outputs/initial_condition_test1.lammps`

**Wall time:** 03:13

**Result:** Data file written. Fibre looked fine in VMD, no stuck crossings.

**Problems and fixes:** Forgot to add `-var dump_out` into command. So moved the default dump file manually into output.

**Next:** Use this file as the starting point for the main script.

---

#### T2: Split main script (2026-10-08 16:25)

**Aim:** Check that the new main simulation script runs on its own and writes correct data files.

**Setup:**
- Script: `scripts/lammps/main.lammps_twistable_nucInteractions`
- Parameters: E = 9.0, I = 0.3, 10 nucleosomes
- Seeds: 54654651, 84575451
- Git commit: `cca5058` 

**Command:**
```bash
nohup LAMMPS/lmp_mpi -in scripts/main.lammps_twistable_nucInteractions -var in initial_condition_test1 -var dump_out main_test1 -var data_out main_test1 -log tests.outputs/main_test1.lammps -screen none > /dev/null 2>&1 &
```

**Outputs:**
- `sim_outputs/main_test1.nucleosomes`
- `tests/outputs/main_test1.lammps`
- `data_files/main_test1.data`

**Wall time:** 38:25 

**Result:** Data files were all written. In VMD the fibre looks to behave well. 

**Next:** Test whether MPI run of this is faster.

#### T3: Test main script MPI (2026-10-08 18:25)

**Aim:** Check whether using MPI will improve the simulation speed.

**Setup:** 
  - Script: `scripts/lammps/main.lammps_twistable_nucInteractions`
  - Parameters: E = 9.0, I = 0.3, 10 nucleosomes, 4 MPI processes
  - Seeds: 54654651, 84575451
  - Git commit: `52329d8`

**Command:**
``` bash
nohup mpirun -np 4 LAMMPS/lmp_mpi -in scripts/lammps/main.lammps_twistable_nucInteractions -var in initial_condition_test1 -var dump_out main_test2 -var data_out main_test2 -log tests/outputs/main_test2.lammps -screen none > /dev/null 2>&1 &
```

**Outputs:**
 - `sim_outputs/main_test2.nucleosomes`
 - `tests/outputs/main_test2.lammps`
 - `data_files/main_test2.data`

**Wall time:** 39:50

**Result:** The MPI run with 4 processes was slower.

**Next:** Try with 16 MPI processes

#### T4: Test MPI with 16 processes (2026-10-08 19:24)

**Aim:** Check if it was too few MPI processes that made the previous test slower

**Setup:**
  - Script: `scripts/lammps/main.lammps_twistable_nucInteractions`
  - Parameters: E = 9.0, I = 0.3, 10 nucleosomes, 32 MPI processes
  - Seeds: 54654651, 84575451
  - Git commit: `52329d8`

**Command:** 
``` bash
nohup mpirun -np 32 LAMMPS/lmp_mpi -in scripts/lammps/main.lammps_twistable_nucInteractions -var in initial_condition_test1 -var dump_out main_test3 -var data_out main_test3 -log tests/outputs/main_test3.lammps -screen none > /dev/null 2>&1 &
```

**Outputs:**
 - `sim_outputs/main_test3.nucleosomes`
 - `tests/outputs/main_test3.lammps`
 - `data_files/main_test3.data`

**Wall time:** 47:38

**Result:** Even slower suggesting more processes is worse (going to keep the single core runs)

**Next:** Carry on with the todo list

#### T5: Generate initial configuration using set seeds and ID.

**Aim:** Test whether my changes to the random seed scripts and the in.lammps_twistable_nucInteractions script work. The goal is to generate an initial condig (equilibration) using nothing but an ID as the input variable.

**Setup:** 
 - Generate 5 ICs with `scripts/generate_random_IC.sh 5`
 - Generate 5 random pairs of seeds with `scripts/generate_random_thermal_seeds.sh 5`
 - Script: `scripts/lammps/in.lammps_twistable_nucInteractions`
 - Parameters: E = 9.0, I = 0.3, 10 nucleosomes, ID = 1
 - Seeds given in seeds/seed_1.lammps
 - Git commit: `b5cd198`

**Command:**
```bash
nohup LAMMPS/lmp_mpi -in scripts/in.lammps_twistable_nucInteractions -var id 1 -log tests/outputs/testing_id_functionality_1.out -screen none > /dev/null 2>&1 &
```

**Outputs:** 
  - `tests/outputs/testing_id_functionality_1.out`

**Wall time:** N/A

**Result:** *ERROR: Incorrect atom format in data file:* 

**Next:** Need to change the shell script to include correct parameters for IC generation.

#### T6: Generate initial configuration using set seeds and ID (with correct atom format).

**Aim:** Re-run T5 with now the correct atom formats for initial conditions.

**Setup:** 
 - Generate 5 ICs with `scripts/generate_random_IC.sh 5`
 - Generate 5 random pairs of seeds with `scripts/generate_random_thermal_seeds.sh 5`
 - Script: `scripts/lammps/in.lammps_twistable_nucInteractions`
 - Parameters: E = 9.0, I = 0.3, 10 nucleosomes, ID = 1
 - Seeds given in seeds/seed_1.lammps
 - Git commit: `3da41ab`

**Command:**
```bash
nohup LAMMPS/lmp_mpi -in scripts/in.lammps_twistable_nucInteractions -var id 1 -log tests/outputs/testing_id_functionality_3.out -screen none > /dev/null 2>&1 &
```

**Outputs:** 
  - `tests/outputs/testing_id_functionality_3.out`
  - `init_configs/'init_config_${id}.init'`
  - `sim_outputs/initial/'dump_initial${id}.nucleosomes'`

**Wall time:** 03:16

**Result:** The program ran well but the output file names were incorrect.

**Next:** Fix the output file names and run again

#### T7: Test if the file names for in.lammps_twistable_nucInteractions outputs are fixed

**Aim:** Re-run T6 with now the correct file names. 

**Setup:** 
 - Script: `scripts/lammps/in.lammps_twistable_nucInteractions`
 - Parameters: E = 9.0, I = 0.3, 10 nucleosomes, ID = 1
 - Seeds given in seeds/seed_1.lammps
 - Git commit: `3d14239`

**Command:**
```bash
nohup LAMMPS/lmp_mpi -in scripts/in.lammps_twistable_nucInteractions -var id 1 -log tests/outputs/testing_id_functionality_4.out -screen none > /dev/null 2>&1 &
```

**Outputs:** 
  - `tests/outputs/testing_id_functionality_4.out`
  - `init_configs/init_config_1.init'`
  - `sim_outputs/initial/dump_initial_1.nucleosomes'`

**Wall time:** 03:13

**Result:** Correct file names.

**Next:** Create a new shell script for running the main simulations

#### T8: Test changes brought about by using shrink-wrapped box

**Aim:** See what happens to the dump file, the movie, and the plots when changing the boundary conditions from p p p to s s s  

**Setup:**
  - Script: `scripts/lammps/setup.lammps`
  - Parameters: E = 9.0, I = 0.3, 20 nucleosomes, id = 3, nsoft = 25000, nrelax = 12500, nwrap = 250000, nstack = 75000
  - Git commit: `8477920`. Branch: `shrink_wrapped_box`

**Command:**
```bash
LAMMPS/lmp_mpi -in scripts/lammps/setup.lammps -var id 3 -var out shrink_test_1 -var dump_out shrink_test_1 -var nsoft 25000 -var nrelax 125000 -var nwrap 250000 -var nstack 75000
```

**Outputs:**
  - `init_configs/shrink_test_1.nucleosomes`
  - `init_configs/shrink_test_1.init`

**Result:** The data dump file contains valid looking data. Importantly the columns ix, iy, iz are now obsolete since they are always 0. The box dimensions change every time step (unsurprisingly) so will need to change the quantity computation scripts to take that into account. (Most likely just not unwrapping the coordinates). Movie looks fine at first glance.

#### T9: Test shrink-wrapped box for full run time 2026-10-17

**Aim:** Running this setup for `id = 3` should produce the identical (unwrapped) positions of the periodic box of the same id, as long as they are ran for the same number of iterations.

**Setup:** 
  - Run the setup script on the `shrink_wrapped_box` branch with default run times
  - Pass the output of this script and the periodic box counterpart to `compare_positions.py`
  - Parameters: E = 9.0, I = 0.3, 20 nucleosomes, id = 3, box = shrink wrapped
  - Git commit: `8477921`. Branch: `shrink_wrapped_box`

**Command:**
```bash
nohup LAMMPS/lmp_mpi -in scripts/lammps/setup.lammps -var id 3 -var out shrink_test_2 -var dump_out shrink_test_2 -screen none > /dev/null 2>&1
```

**Outputs:**
  - `init_configs/shrink_test_2.nucleosomes`
  - `init_configs/shrink_test_2.init`
  - `init_configs/log_shrink_test2.out`

**Result:** Even with the same seeds the atom positions start differing considerably staring from the first (non initial) frame. To me this suggests that the atoms in the periodic box interact across the boundary at all times because I don't otherwise see what should be different between the two.

**Next:** Try the shrink-wrapped box with minimum value mode by setting the minimum value to be -50 to 50 for all 3 dimensions. This will take longer as the box will be at least the same at all steps but it should more decisively determine what the cause of the difference is. 

#### T10: Test shrink-wrapped box with minimum size 2026-10-17 10:58

**Aim:** Check if setting boundary conditions to `m` with minimum size given in the initial conditions file (should be -50 to 50 for each dimension) results in the same output as `s` or as `p` or neither. This should determine the effect periodicity had on the simulation.

**Setup:**
 - Changed boundary conditions in `setup.lammps`
 - Run it with the same parameters as in T9 but box = shrink wrapped with minimum
 - Compare all three of the files to eachother with `scripts/python/tests/compare_positions.py`
 - Compare calculated values of R_g as well using  `scripts/python/calculate_rg.py` and `scripts/python/plotter.py`
 - Git commit: `6406fe0`. Branch: `shrink_wrapped_box`

**Command:**
``` bash
nohup LAMMPS/lmp_mpi -in scripts/lammps/setup.lammps -var id 3 -var out min_shrink_test_1 -var dump_out min_shrink_test_1 -log init_configs/min_shrink_test_1.out -screen none > /dev/null 2>&1 &
```

**Outputs:**
  - `init_configs/min_shrink_test_1.nucleosomes`
  - `init_configs/min_shrink_test_1.init`
  - `init_configs/log_min_shrink_test_1.out`
  - `figures/min_shrink_rg.png`
  - `figures/min_shrink_rgh.png`
  - And other plots of similar names for shrink wrapped and periodic boxes
    These plots will most likely be deleted at a later date.

**Result:** All three files are different and end up in completely different configurations once again starting from frame 1. The radius of gyration values are also all different and the histograms don't match at all -> the behaviour is not the same. This is an interesting result I should discuss with Chris because I expected at least `m` and `s` to be the same for the same seeds. The minimum box for `m` was correctly of size 100 in each dimension.

**Next:** Importantly, this is not necessarily a bad thing since the extra atomic interactions due to periodicity shouldn't be there (as per previous discussion with Chris) so now it's more of a decision of whether doing `m` or `s`. This is something to discuss in the Tuesday meeting. Next test is to run one of the box styles, take `s`, for a longer equilibration since I saw that the nucleosomes don't get stuck all the way and the nucleosomes don't fully stuck.

#### T11: Equilibrate shrink wrapped box for more timesteps



**Aim:** See how double the equilibration steps affect the initial conditions and have a better initial conditions file to start implementing the untangling code. Also focus on the wrapping and stacking time steps since that is what isn't happening in the vmd movie

**Setup:** 
  - Run the `setup.lammps` script with all time steps doubled
  - Non-default parameters: nsoft = 100000, nrelax = 500000, nwrap = 1000000, nstack = 300000 (Exactly doubled step counts), id = 3, boundary = s s s 
  - Git commit: `a81edda`. Branch: `shrink_wrapped_box`

**Command:**
``` bash
nohup LAMMPS/lmp_mpi -in scripts/lammps/setup.lammps -var id 3 -var nsoft 100000 -var nrelax 500000 -var nwrap 1000000 -var nstack 300000 -screen none > /dev/null 2>&1 &
```

**Outputs:**
  - `init_configs/init_config_3.init`
  - `sim_outputs/initial/dump_initial_3.nucleosomes`
  - `init_configs/log_initial_3.out`

  
