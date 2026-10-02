# Loads each data chunk one at a time, unwraps coordinates, calculates radius of gyration for each chunk, plots time evolution of it


import numpy as np
import matplotlib.pyplot as plt
from data_loader import load_dump_timestep


def _unwrap_coords(data : np.ndarray, dims : list = [11, 11, 11]) -> np.ndarray:

    #TODO: Get a way to dynamically detect the dimensions
    real_pos = np.array(data[:, 0:3] + data[:, 3:]*dims)
    return real_pos

def calculate_radius_of_gyration(n_atoms : int, data : np.ndarray) -> float:

    unwrapped_positions = _unwrap_coords(data) 
    mean_r = np.mean(unwrapped_positions, axis = 0)     # This should be mean x, y, z positions in an array of shape (3,)   
    rg_sq = np.sum(np.linalg.norm(unwrapped_positions - mean_r))/n_atoms # This should be the square of the radius of gyration for the given data chunk
    return rg_sq

def plot_rg_over_time(rg_data : np.ndarray, n_bins : int = 50):
    
    time_data = np.arange(0, 10010000, step=10000)
    time_bins = np.array_split(time_data, n_bins)
    rg_data_bins = np.array_split(rg_data, n_bins)

    bin_centres = np.array([t.mean() for t in time_bins])
    mean = np.array([rg.mean() for rg in rg_data_bins])
    std = np.array([rg.std() for rg in rg_data_bins])

    fig, ax = plt.subplots()
    ax.scatter(time_data, rg_data, s = 2, alpha = 0.2, color = "grey", label = "data")
    ax.errorbar(bin_centres, mean, yerr=std, fmt="o-", markersize = 3, capsize = 2, label=r"binned mean $\pm 1 \sigma$") 
    ax.set_title(r"Time evolution of radius of gyration squared, $R_g^2$")
    ax.set_xlabel("Timestep")
    ax.set_ylabel(r"$R_g^2$")
    ax.legend()
    
    fig.savefig("figures/rg_over_time.png") 

if __name__ == "__main__":
    filepath = "/home/s2289431/MPhys_Project/Shared/initial_condition_builder/dump_main.nucleosomes"
    needed_cols = ['x','y','z','ix','iy','iz']
    # Iterate over chunks
    rg_sq_all = []
    for chunk_params, chunk_data in load_dump_timestep(filepath, needed_cols):
        rg_sq_all.append(calculate_radius_of_gyration(chunk_params['n_atoms'], chunk_data))
    plot_rg_over_time(np.asarray(rg_sq_all))
