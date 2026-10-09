# Tests ran

This file describes various tests that were run in many areas of the program.

### LAMMPS tests


| ID | Date | Test | Status |
|---|---|---|---|
| T1 | 2026-10-08 16:03 | Split set-up script | Passed |
| T2 | 2026-10-08 16:25 | Split main script | Passed |
| T3 | 2026-10-08 18:36 | MPI main version | Completed|
| T4 | 2026-10-08 19:24 | 32 process MPI main | Completed|

---

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
