from exercise3_bis import Exercise3
from graph import Graph

from pathlib import Path
import random
import numpy as np

import concurrent.futures


# In order to use multiprocessing, we need to define
# this function outside of the class
def _run_single_sim(args):
    base_graph, fire_start, firewall_n = args
    graph = base_graph.clone()
    exercise3 = Exercise3(verbose_output=False)
    _, burnt_set = exercise3.exercise3(graph, fire_start, firewall_n)
    return len(burnt_set)

class MonteCarloSimulation:
    def simulate_fire(self, file_name, n_simulations: int, fire_start: int, firewall_n: int):
        base_graph = Graph(directed=True)

        # Only read from disk once for better performance
        base_graph.load_from_file(file_name)
        
        # preparing arguments for each simulation
        args = [(base_graph, fire_start, firewall_n) for _ in range(n_simulations)]
        
        # Using all available cores
        with concurrent.futures.ProcessPoolExecutor() as executor:
            # chunksize=100 is a value to reduce overhead
            # that seems to work well according to our testing (tune if needed)
            results = list(executor.map(_run_single_sim, args, chunksize=100))
            
        burnt_nodes = np.array(results)
        return burnt_nodes.mean(), burnt_nodes.std()
            

def main():
    seed = 1926
    random.seed(seed)
    simulation_n = 10_000
    print(f"Running Monte Carlo simulation with {simulation_n} iterations and seed {seed}...")

    BASE_DIR = Path(__file__).resolve().parent
    for i in [3,4,5,7,8,10]:
        filename = BASE_DIR / f"../graph_{i:03d}_probs.txt"
        print()
        print(f"\nGraph {i:03d}:")
        montecarlo = MonteCarloSimulation()
        mean, std = montecarlo.simulate_fire(filename, simulation_n, fire_start=1, firewall_n=2)
        print(f"Mean burnt nodes: {mean:.2f}\nStd: {std:.2f}")

if __name__ == "__main__":
    main()