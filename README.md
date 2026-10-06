# biophysics_of_nucleosomal_fibres

This repository is the code base for the MPhys dissertation project of the same name. The code is intended to measure the behaviour of nucleosomes using a new coarse grained model simulated in LAMMPS.

Make sure to push changes to the repository after finishing a session.
# Initial setup 
Make sure to enter a supported python environment
``` console
conda activate daml
```
> [!NOTE]
> The `daml` environment was designed for the Data Analysis and Machine Learning in Physics course, so likely has many unnecessary libraries. Creating a dedicated environment is on the TODO list.

# Calculate radius of gyration

``` console
python calculate_rg.py
```
Currently no CLI inputs, takes in default dump file.

# vmd commands

To run the dump file straight from the terminal adding the dump file as a lammps trajectory molecule and updating the colours in one go
``` console
vmd -lammpstrj <path_to_dump_file>/dump_main.nucleosomes -e <path_to>/colours.tcl
```
