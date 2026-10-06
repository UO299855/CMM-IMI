import pulp
from graph import Graph
from pathlib import Path

class Exercise2ILP:

    def __init__(self, verbose : bool = False):
        self.verbose = verbose

    def exact_solve(self,graph : Graph, start, firewall_n):
        # Define the ILP problem
        self._problem_variable_definition(graph)
        self._impose_constraints(graph, start, firewall_n)
        
        # Solve the problem using an ILP solver
        # We disable the solver output messages for cleaner output
        self.problem.solve(pulp.PULP_CBC_CMD(msg=False))

        # Result retreival
        burnt_nodes, saved_nodes, cuts = self._get_results(graph)
        if self.verbose:
            self._print_results(burnt_nodes, saved_nodes, cuts)
        return burnt_nodes, saved_nodes, cuts

    
    def _problem_variable_definition(self, graph : Graph):
        n = len(graph.adj)
        # We declare a problem for our solver (minimization problem)
        self.problem = pulp.LpProblem("Firefighter_Problem", pulp.LpMinimize)

        # We define our decision variables
        self.burnt_nodes = {}
        for i in graph.adj:
            for t in range(n):
                # Binary variable indicating if node i starts to burn at time t or before
                self.burnt_nodes[(i, t)] = pulp.LpVariable(f"x_{i}_{t}", cat='Binary')

        self.firewalls = {}
        for u in graph.adj:
            for v in graph.adj[u]:
                for t in range(n):
                    # Binary variable indicating if edge (u, v) is cut at time t or before
                    self.firewalls[(u, v, t)] = pulp.LpVariable(f"y_{u}_{v}_{t}", cat='Binary')

        # Objective function: minimize the total number of burnt nodes at the end of the time horizon
        self.problem += pulp.lpSum([self.burnt_nodes[(i, n-1)] for i in range(n)]), "burnt_nodes"

    def _impose_constraints(self, graph : Graph, start, firewall_n):
        # The fire starts only at the starting node at time t=0
        self.problem += self.burnt_nodes[(start, 0)] == 1, "fire_starts"        
        for i in graph.adj:
            if i != start:
                self.problem += self.burnt_nodes[(i, 0)] == 0, f"not_starting_in_{i}"
                    
        # No firewalls can be set at time t=0
        for i in graph.adj:
            for j in graph.adj[i]:
                self.problem += self.firewalls[(i, j, 0)] == 0, f"no_firewalls_t0_{i}_{j}"

        # We now model the spread of the fire
        n = len(graph.adj)
        for t in range(1, n):
            # We can set at most 'firewall_n' new firewalls per step
            new_firewalls = pulp.lpSum([
                self.firewalls[(u, v, t)] - self.firewalls[(u, v, t-1)] for u in graph.adj for v in graph.adj[u]
            ])
            self.problem += new_firewalls <= firewall_n, f"limit_firewalls_t{t}"

            for i in graph.adj:
                # Irreversibility: if a node is burnt at time t-1, it remains burnt at time t
                self.problem += self.burnt_nodes[(i, t)] >= self.burnt_nodes[(i, t-1)], f"irreversible_burn_{i}_{t}"
                for j in graph.adj[i]:
                    # Irreversibility of the firewall: a cut remains in time
                    self.problem += self.firewalls[(i, j, t)] >= self.firewalls[(i, j, t-1)], f"irreversible_firewall_{i}_{j}_{t}"

                    # Propagation of the fire: if 'i' is burning at time t-1 and
                    # the edge (i, j) is NOT cut at time t, then 'j' burns at time t
                    self.problem += self.burnt_nodes[(j, t)] >= self.burnt_nodes[(i, t-1)] - self.firewalls[(i, j, t)], f"propagation_{i}_{j}_{t}"

    def _get_results(self, graph : Graph):
        if self.problem.status != pulp.LpStatusOptimal:
            print(f"The solver could not find an optimal solution. Status: {pulp.LpStatus[self.problem.status]}")
            return None, None, None

        n = len(graph.adj)
        are_nodes_burnt = {i: pulp.value(self.burnt_nodes[(i, n-1)]) for i in graph.adj}
        burnt_nodes = sorted({i for i, burnt in are_nodes_burnt.items() if burnt > 0.5})
        saved_nodes = sorted({i for i in graph.adj if i not in burnt_nodes})

        cuts = {}
        for t in range(1, n):
            cuts_at_t = []
            for u in graph.adj:
                for v in graph.adj[u]:
                    # Check if the edge (u, v) was cut ecxactly at time t
                    # It was not cut at time t-1 and it is cut at time t
                    if pulp.value(self.firewalls[(u, v, t)]) > 0.5 and pulp.value(self.firewalls[(u, v, t-1)]) < 0.5:
                        cuts_at_t.append((u, v))
            if len(cuts_at_t) > 0:
                cuts[t] = cuts_at_t

        return burnt_nodes, saved_nodes, cuts

    def _print_results(self, burnt_nodes, saved_nodes, cuts):
        if not burnt_nodes or not saved_nodes:
            print("No results to display.")
            return
        print(f"Burnt nodes ({len(burnt_nodes)}):", burnt_nodes)
        print(f"Saved {len(saved_nodes)} nodes:", saved_nodes)
        print("Firewall cuts made:")
        for t, cuts_at_t in cuts.items():
            print(f"  Step {t}: {cuts_at_t}")



def main():
    BASE_DIR = Path(__file__).resolve().parent
    for i in [3,4,5,7,8,10]:
        filename = BASE_DIR / f"../graph_{i:03d}_probs.txt"
        print()
        print(f"\n Graph {i:03d}:")
        graph = Graph(directed=True)
        graph.load_from_file(filename)

        solver = Exercise2ILP(verbose=True)
        solver.exact_solve(graph, start=1, firewall_n=2)


if __name__ == "__main__":
    main()