import pulp
import numpy as np
from pathlib import Path
from graph import Graph

class Exercise3ILP:

    def __init__(self, n_samples: int = 50, verbose: bool = False):
        self.n_samples = n_samples
        self.verbose = verbose

    def exact_solve(self, graph: Graph, start: int, firewall_n: int):
        # Generate random scenarios based on edge probabilities
        self._generate_scenarios(graph)
        
        # Define the ILP problem
        self._problem_variable_definition(graph)
        self._impose_constraints(graph, start, firewall_n)
        
        # Solve the problem using an ILP solver with multithreading
        self.problem.solve(pulp.PULP_CBC_CMD(msg=False, threads=8))

        # Result retrieval
        avg_saved_nodes, cuts = self._get_results(graph)
        if self.verbose:
            self._print_results(avg_saved_nodes, cuts)
        return avg_saved_nodes, cuts

    def _generate_scenarios(self, graph: Graph):
        self.active_edges = {}
        for ite in range(self.n_samples):
            for u in graph.adj:
                for v, weight in graph.adj[u].items():
                    # An edge is active if a random value is less than or equal to its weight
                    self.active_edges[(u, v, ite)] = (np.random.rand() <= weight)

    def _problem_variable_definition(self, graph: Graph):
        n = len(graph.adj)
        self.problem = pulp.LpProblem("Stochastic_Firefighter_Problem", pulp.LpMinimize)

        self.burnt_nodes = {}
        for ite in range(self.n_samples):
            for i in graph.adj:
                for t in range(n):
                    # Binary variable indicating if node i starts to burn at time t or before in a given scenario
                    self.burnt_nodes[(i, t, ite)] = pulp.LpVariable(f"x_{i}_{t}_{ite}", cat='Binary')

        self.firewalls = {}
        for u in graph.adj:
            for v in graph.adj[u]:
                for t in range(n):
                    # Binary variable indicating if edge (u, v) is cut at time t or before
                    self.firewalls[(u, v, t)] = pulp.LpVariable(f"y_{u}_{v}_{t}", cat='Binary')

        # Objective function: minimize the average total number of burnt nodes
        self.problem += pulp.lpSum([
            self.burnt_nodes[(i, n-1, ite)] 
            for i in graph.adj for ite in range(self.n_samples)
        ]) / self.n_samples, "avg_burnt_nodes"

    def _impose_constraints(self, graph: Graph, start: int, firewall_n: int):
        n = len(graph.adj)
        
        # The fire starts only at the starting node at time t=0
        for ite in range(self.n_samples):
            self.problem += self.burnt_nodes[(start, 0, ite)] == 1, f"fire_starts_{ite}"        
            for i in graph.adj:
                if i != start:
                    self.problem += self.burnt_nodes[(i, 0, ite)] == 0, f"not_starting_in_{i}_{ite}"
                    
        # No firewalls can be set at time t=0
        for u in graph.adj:
            for v in graph.adj[u]:
                self.problem += self.firewalls[(u, v, 0)] == 0, f"no_firewalls_t0_{u}_{v}"

        # Model the spread of the fire
        for t in range(1, n):
            # We can set at most 'firewall_n' new firewalls per step
            new_firewalls = pulp.lpSum([
                self.firewalls[(u, v, t)] - self.firewalls[(u, v, t-1)] 
                for u in graph.adj for v in graph.adj[u]
            ])
            self.problem += new_firewalls <= firewall_n, f"limit_firewalls_t{t}"

            for i in graph.adj:
                for ite in range(self.n_samples):
                    # Irreversibility: if a node is burnt at time t-1, it remains burnt at time t
                    self.problem += self.burnt_nodes[(i, t, ite)] >= self.burnt_nodes[(i, t-1, ite)], f"irreversible_burn_{i}_{t}_{ite}"
                
                for j in graph.adj[i]:
                    # Irreversibility of the firewall: a cut remains in time
                    self.problem += self.firewalls[(i, j, t)] >= self.firewalls[(i, j, t-1)], f"irreversible_firewall_{i}_{j}_{t}"

                    for ite in range(self.n_samples):
                        # Propagation: if edge (i, j) is active in this scenario, 
                        # and 'i' is burning at t-1 while (i, j) is NOT cut at t, then 'j' burns at t
                        if self.active_edges[(i, j, ite)]:
                            self.problem += self.burnt_nodes[(j, t, ite)] >= self.burnt_nodes[(i, t-1, ite)] - self.firewalls[(i, j, t)], f"propagation_{i}_{j}_{t}_{ite}"

    def _get_results(self, graph: Graph):
        if self.problem.status != pulp.LpStatusOptimal:
            print(f"The solver could not find an optimal solution. Status: {pulp.LpStatus[self.problem.status]}")
            return None, None

        n = len(graph.adj)
        
        # Calculate the average number of burnt and saved nodes across all samples
        avg_burnt_nodes = sum(
            1 for i in graph.adj for ite in range(self.n_samples) 
            if pulp.value(self.burnt_nodes[(i, n-1, ite)]) > 0.5
        ) / self.n_samples
        
        avg_saved_nodes = n - avg_burnt_nodes

        cuts = {}
        for t in range(1, n):
            cuts_at_t = []
            for u in graph.adj:
                for v in graph.adj[u]:
                    # Check if the edge (u, v) was cut exactly at time t
                    if pulp.value(self.firewalls[(u, v, t)]) > 0.5 and pulp.value(self.firewalls[(u, v, t-1)]) < 0.5:
                        cuts_at_t.append((u, v))
            if len(cuts_at_t) > 0:
                cuts[t] = cuts_at_t

        return avg_saved_nodes, cuts

    def _print_results(self, avg_saved_nodes, cuts):
        if avg_saved_nodes is None:
            print("No results to display.")
            return
        print(f"Average saved nodes: {avg_saved_nodes:.2f}")
        print("Firewall cuts made:")
        for t, cuts_at_t in cuts.items():
            print(f"  Step {t}: {cuts_at_t}")


def main():
    BASE_DIR = Path(__file__).resolve().parent
    np.random.seed(1926)
    
    for i in [3, 4, 5, 10]:
        filename = BASE_DIR / f"../graph_{i:03d}_probs.txt"
        print()
        print(f"\n Graph {i:03d}:")
        
        graph = Graph(directed=True)
        graph.load_from_file(filename)

        solver = Exercise3ILP(n_samples=50, verbose=True)
        solver.exact_solve(graph, start=1, firewall_n=1)


if __name__ == "__main__":
    main()