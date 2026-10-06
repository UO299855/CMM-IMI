from graph import Graph
from exercise3_montecarlo import MonteCarloSimulation
import random
from pathlib import Path
from collections import deque

class Pyromaniac:
    def __init__(self, n_simulations: int = 10_000):
        self.n_simulations = n_simulations

    def _brandes_betweenness(self, graph: Graph):
        """
        Computes the betweenness centrality for all nodes using Brandes' algorithm.
        """
        centrality_scores = {node: 0.0 for node in graph.adj}
        
        for source_node in graph.adj:
            visited_nodes_stack = []
            predecessors = {node: [] for node in graph.adj}
            
            shortest_path_counts = {node: 0 for node in graph.adj}
            shortest_path_counts[source_node] = 1
            
            distances = {node: -1 for node in graph.adj}
            distances[source_node] = 0
            
            bfs_queue = deque([source_node])

            # Perform BFS to compute shortest paths and predecessors
            while bfs_queue:
                current_node = bfs_queue.popleft()
                visited_nodes_stack.append(current_node)
                
                for neighbor_node in graph.adj[current_node]:
                    # If neighbor_node is found for the first time
                    if distances[neighbor_node] < 0:
                        bfs_queue.append(neighbor_node)
                        distances[neighbor_node] = distances[current_node] + 1
                    
                    # If the shortest path to neighbor_node goes via current_node
                    if distances[neighbor_node] == distances[current_node] + 1:
                        shortest_path_counts[neighbor_node] += shortest_path_counts[current_node]
                        predecessors[neighbor_node].append(current_node)
            
            # Accumulation phase to calculate dependencies
            dependency_scores = {node: 0.0 for node in graph.adj}
            while visited_nodes_stack:
                target_node = visited_nodes_stack.pop()
                for predecessor_node in predecessors[target_node]:
                    dependency_scores[predecessor_node] += (
                        shortest_path_counts[predecessor_node] / shortest_path_counts[target_node]
                    ) * (1 + dependency_scores[target_node])
                
                if target_node != source_node:
                    centrality_scores[target_node] += dependency_scores[target_node]
                    
        return centrality_scores

    def find_best_start(self, graph: Graph, firewall_n: int, n_brandes: int = 10):
        """
        Finds the best starting node by pre-filtering with Brandes' algorithm 
        and then running Monte Carlo simulations.
        """
        # Compute betweenness centrality
        centrality = self._brandes_betweenness(graph)
        
        # Sort nodes by centrality (descending) and get the top candidates
        sorted_nodes = sorted(centrality.keys(), key=lambda k: centrality[k], reverse=True)
        
        # Use slices to ensure we don't exceed the number of available nodes
        candidate_nodes = sorted_nodes[:n_brandes]

        best_node = None
        highest_mean = -float("inf")
        std_of_highest_mean = float("inf")

        # Brute force only over the top n_brandes nodes
        for node in candidate_nodes:
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
    n_brandes = 5
    print(f"Running Pyromaniac simulation with {n_simulations} iterations and seed {seed}...")
    print(f"Using top {n_brandes} nodes based on Brandes' betweenness centrality")
    
    BASE_DIR = Path(__file__).resolve().parent
    for i in [3, 4, 5, 7, 8, 10]:
        filename = BASE_DIR / f"../graph_{i:03d}_probs.txt"
        print()
        print(f"\nGraph {i:03d}:")
        
        graph = Graph(directed=True)
        graph.load_from_file(filename)
            
        pyromaniac = Pyromaniac(n_simulations)
        best_node, highest_mean, std = pyromaniac.find_best_start(
            graph, firewall_n=2, n_brandes=n_brandes
        )
        
        print(f"Best starting node: {best_node}")
        print(f"Mean burnt nodes: {highest_mean:.2f}")
        print(f"Std: {std:.2f}")

if __name__ == "__main__":
    main()