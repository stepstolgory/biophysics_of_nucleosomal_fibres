# Tests ran

This file describes various tests that were run in many areas of the program.

### LAMMPS tests


| ID | Date | Test | Status |
|---|---|---|---|
| T1 | 2026-10-08 16:03 | Split set-up script | Passed |
| T2 | 2026-10-08 16:25 | Split main script | Passed |
| T3 | 2026-10-08 18:36 | MPI main version | Completed|
| T4 | 2026-10-08 19:24 | 32 process MPI main | In Progress |

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

**Wall time:** 47:38

**Result:** Even slower suggesting more processes is worse (going to keep the single core runs)

**Next:** Carry on with the todo list

**Outputs:**
 - `sim_outputs/main_test3.nucleosomes`
 - `tests/outputs/main_test3.lammps`
 - `data_files/main_test3.data`
