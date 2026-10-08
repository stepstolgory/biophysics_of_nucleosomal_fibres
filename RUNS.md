# Tests ran

This file describes various tests that were run in many areas of the program.

### LAMMPS tests


| ID | Date | Test | Status |
|---|---|---|---|
| T1 | 2026-10-08 16:03 | Split set-up script | Passed |
| T2 | 2026-10-08 | Split main script | In progress |

---

#### T1: Split set-up script (2026-10-08 14:30)

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

#### T2: MPI timing (2026-10-08 16:00)

**Aim:** Check that the new main simulation script runs on its own and writes correct data files.

**Setup**:
- Script: `scripts/lammps/main.lammps_twistable_nucInteractions`
- Parameters: E = 9.0, I = 0.3, 10 nucleosomes
- Seeds: 54654651, 84575451
- Git commit: `79397dd` 

Command:
```bash
nohup LAMMPS/lmp_mpi -in scripts/main.lammps_twistable_nucInteractions -var in initial_condition_test1 -var dump_out main_test1 -var data_out main_test1 -log tests.outputs/main_test1.lammps -screen none > /dev/null 2>&1 &
```

