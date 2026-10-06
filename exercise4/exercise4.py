from graph import Graph
from exercise3_montecarlo import MonteCarloSimulation
import random
from pathlib import Path

class Pyromaniac:
    def __init__(self, n_simulations: int = 10_000):
        self.n_simulations = n_simulations

    def find_best_start(self, graph: Graph, firewall_n: int):
        best_node = None
        highest_mean = -float("inf")
        std_of_highest_mean = float("inf")

        for node in graph.adj:
            simulation = MonteCarloSimulation()

            mean, std = simulation.simulate_fire(
                graph,
                self.n_simulations,
                fire_start=node,
                firewall_n=firewall_n
            )

            if mean > highest_mean or (
                mean == highest_mean and std < std_of_highest_mean
            ):
                highest_mean = mean
                std_of_highest_mean = std
                best_node = node

        return best_node, highest_mean, std_of_highest_mean

def main():
    seed = 1926
    random.seed(seed)
    n_simulations = 1_000
    print(f"Running Pyromaniac simulation with {n_simulations} iterations and seed {seed}...")
    BASE_DIR = Path(__file__).resolve().parent
    for i in [3, 4, 5, 7, 8, 10]:
        filename = BASE_DIR / f"../graph_{i:03d}_probs.txt"
        print()
        print(f"\nGraph {i:03d}:")
        graph = Graph(directed=True)
        graph.load_from_file(filename)
        pyromaniac = Pyromaniac(n_simulations)
        best_node, highest_mean, std = pyromaniac.find_best_start(graph, firewall_n=2)
        print(f"Best starting node: {best_node}")
        print(f"Mean burnt nodes: {highest_mean:.2f}")
        print(f"Std: {std:.2f}")

if __name__ == "__main__":
    main()