import numpy as np

# Prints one random seed. LAMMPS only accepts seeds from 1 to 900,000,000,
# so the range here stays well inside that.
if __name__ == "__main__":
    very_fancy_generated_random_seed = np.random.randint(1, 100_000_000)
    print(very_fancy_generated_random_seed)
