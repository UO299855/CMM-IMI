
from graph import Graph
import heapq
import math
import random
from pathlib import Path


class Exercise3:

    def __init__(self, verbose_process = False, verbose_output = True):
        self.verbose_process = verbose_process
        self.verbose_output = verbose_output

    def exercise3(self, graph: Graph, start : int, firewall_n : int):
        """
        Adaptation of exercise2's heuristic for a probabilistic environment
        """
        self.graph = graph
        self.burnt_set = set()
            
        total_cuts = []
        newly_burnt = set([start])
        while newly_burnt:
            cuts = []
            self.burnt_set.update(newly_burnt)
            for cuts_done in range(firewall_n):
                self.remaining_firewalls = firewall_n - cuts_done
                best = self._best_edge(newly_burnt)
                if best is None: break
                cuts.append(best)
                self.graph.set_firewall(best[0], best[1])
            newly_burnt = self._fire_spread(newly_burnt)
            total_cuts.append(cuts)

        if self.verbose_output:
            self._print_results(total_cuts, self.burnt_set)

        return total_cuts, self.burnt_set

    def _print_results(self, total_cuts, burnt_set):
        print(f"Burnt vertices ({len(burnt_set)}):", sorted(burnt_set))
        print(f"Saved {len(self.graph.adj) - len(burnt_set)} vertices")
        print("Firewall cuts made:")
        for i, cuts in enumerate(total_cuts):
            print(f"  Step {i+1}: {cuts}")

    def _best_edge(self, newly_burnt : set[int]):
            n = len(self.graph.adj)

            # CHANGE FROM EXERCISE 2:
            # Instead of BFS distances, Dijkstra uses -log(probability) as the edge weight.
            # Minimizing the sum of these weights is equivalent to maximizing the probability of a path.
            minus_log_prob : list[float] = [float("inf")] * n
            for i in self.burnt_set:
                minus_log_prob[i] = 0.0

            # CHANGE FROM EXERCISE 2:
            # Keep the number of edges in the path as a secondary criterion.
            # This makes paths with p=1 behave like shortest paths in BFS.
            # It also helps to break ties in a consistent and useful way.
            n_steps_to_node : list[int] = [n+1] * n
            for i in self.burnt_set:            
                n_steps_to_node[i] = 0

            # Initial variable setup
            importance_matrix = [[0.0 for _ in range(n)] for _ in range(n)]
            reaching_edges = [[None] if i in self.burnt_set else [] for i in range(n)]

            # CHANGE FROM EXERCISE 2:
            # accumulated probability of the maximum-probability paths to each node.
            path_probabilities = [0.0] * n


            # Initial priority heap setup
            # The heap is ordered first by log probability and then by the number of steps.
            heap = []
            for i in newly_burnt:
                path_probabilities[i] = 1.0
                heapq.heappush(heap, (0.0, 0, i))

            # Keep looping as long as there are vertices in the priority heap
            # Save the order of the vertices we visit
            stack = self._loop_over_heap(heap, minus_log_prob, n_steps_to_node,
                reaching_edges,path_probabilities)

            # Assign importance to each edge based on how much probability
            # flows through it from the source to the target
            self._loop_over_stack(stack, reaching_edges, importance_matrix,
                path_probabilities)

            if self.verbose_process:
                self._matrix_print(importance_matrix)
                print()

            # We flatten the list of reaching edges and sort them by importance,
            # returning the top edge
            candidates = self._get_candidate_edges(
                reaching_edges,
                importance_matrix,
                minus_log_prob,
                n_steps_to_node
            )
            return candidates[0] if candidates else None

    def _fire_spread(self, last_new_burnt):
        """
        Simulates fire spread probabilistically.
        Neighbors attempt to catch fire only once from the current burning front.
        """
        newly_burnt_next = set()

        for burning in last_new_burnt:
            for i in self.graph.adj[burning]:
                if i not in self.burnt_set and i not in newly_burnt_next:
                    p_uv = self.graph.adj[burning][i]

                    # CHANGE FROM EXERCISE 2:
                    # The edge only propagates the fire with probability p_uv.
                    if random.random() <= p_uv:
                        newly_burnt_next.add(i)

        return newly_burnt_next

    def _get_candidate_edges(self, reaching_edges, importance_matrix, minus_log_prob, n_steps_to_node):
        """
        Flattens the list of reaching edges and returns a set of unique edges.
        Sorts the edges by their importance (most important first)
        and probability distance to the fire (least distant first).
        """
        # Collapse (i,j) and (j,i) into a single edge by using a set of tuples
        unique_edges = set()

        for edge_list in reaching_edges:
            for edge in edge_list:
                if edge is not None:
                    unique_edges.add(tuple(sorted(edge)))

        # Flatten the set of unique edges into a list
        candidate_edges = [list(edge) for edge in unique_edges]

        candidate_edges.sort(
            key=lambda edge: (
                # First criterion: importance[i][j] + importance[j][i]
                # (the sum of the importance of both directions)
                -round(
                    importance_matrix[edge[0]][edge[1]] +
                    importance_matrix[edge[1]][edge[0]],
                    9
                ),

                # Second criterion: min distance to the fire
                min(minus_log_prob[edge[0]], minus_log_prob[edge[1]]),

                # Tie breaker based on steps
                min(n_steps_to_node[edge[0]], n_steps_to_node[edge[1]]),

                # Makes ties not arbitrary, but consistent across runs
                tuple(edge)
            )
        )

        return candidate_edges

    def _loop_over_stack(self, stack, reaching_edges, importance_matrix,
        path_probabilities):
        """
        Assigns importance to each edge based on the probability
        of the paths that use it.
        """
        n = len(path_probabilities)
        delta = [0.0] * n

        while stack:
            current = stack.pop()

            for edge in reaching_edges[current]:
                if edge is not None:
                    parent = edge[0]
                    p_uv = self.graph.adj[parent][current]

                    # CHANGE FROM EXERCISE 2:
                    # The contribution of an edge is weighted by its
                    # propagation probability.
                    if path_probabilities[current] > 0:
                        c = (
                            path_probabilities[parent] * p_uv
                        ) / path_probabilities[current] * (1 + delta[current])

                        delta[parent] += c

                        # The importance of the edge from parent to current
                        # is incremented by the same ratio
                        importance_matrix[parent][current] += c

    def _matrix_print(self, matrix):
        """
        Prints a matrix in a readable format.
        """
        for row in matrix:
            print(" ".join(f"{val:>6.2f}" for val in row))

    def _loop_over_heap(self, heap, minus_log_prob, steps, reaching_edges,path_probabilities):
        """
        Visits vertices applying Dijkstra's algorithm to find paths
        with the maximum propagation probability.

        Edge weights are -log(p), so maximizing path probability
        is equivalent to minimizing the total distance.
        """
        stack = []
        visited_set = set()

        while heap:
            current_m_log_prob, current_steps, current = heapq.heappop(heap)

            # Since heapq can hold duplicate nodes with worse distances,
            # we only process a node the first time it is popped
            # with its best distance and hop count.
            if current in visited_set:
                continue

            visited_set.add(current)
            stack.append(current)

            for i in self.graph.adj[current]:
                p_uv = self.graph.adj[current][i]

                # A zero-probability edge can never belong to a
                # maximum-probability path.
                if p_uv <= 0:
                    continue

                # CHANGE FROM EXERCISE 2:
                # Dijkstra's edge weight is -log(p_uv).
                new_m_log_prob = current_m_log_prob - math.log(p_uv)
                new_steps = current_steps + 1

                new_probability = (
                    path_probabilities[current] * p_uv
                )
                
                # More likely path (smaller -log(probability))
                if new_m_log_prob < minus_log_prob[i]:
                     # Keep track of only the best path to each node. Reset the values.
                    minus_log_prob[i] = new_m_log_prob
                    steps[i] = new_steps
                    reaching_edges[i] = [[current, i]]
                    path_probabilities[i] = new_probability
                    heapq.heappush(
                        heap,
                        (new_m_log_prob, new_steps, i)
                    )

                # If it's an equally probable path
                elif (
                    new_m_log_prob == minus_log_prob[i]
                    and new_steps == steps[i]
                    and new_probability > 0
                ):  #Update what we had before
                    reaching_edges[i].append([current, i])
                    path_probabilities[i] += new_probability

        return stack

    def try_config(self, graph: Graph, start : int, firewall_n : int,
        firewalls : list[list[tuple[int,int]]]):
        """
        Tries a configuration of firewalls and returns the number of burnt vertices.
        Checks if the given configuration of firewalls is valid and applies them in order, simulating the fire spread.
        """
        self.graph = graph
        self.burnt_set = set()
        newly_burnt = set([start])
        iter = 0
        actual_firewalls = []

        while newly_burnt:
            self.burnt_set.update(newly_burnt)
            actual_this_iter = []

            if iter < len(firewalls):
                cuts = firewalls[iter]

                for cut_index in range(min(len(cuts), firewall_n)):
                    cut = cuts[cut_index]
                    self.graph.set_firewall(cut[0], cut[1])
                    actual_this_iter.append(cut)

            actual_firewalls.append(actual_this_iter)
            newly_burnt = self._fire_spread(newly_burnt)
            iter = iter + 1

        if self.verbose_output:
            self._print_results(actual_firewalls, self.burnt_set)

        return len(self.burnt_set)


def main():
    start = 1
    firewall_n = 1
    BASE_DIR = Path(__file__).resolve().parent

    for i in [3, 4, 5, 7, 8, 10]:
        print()
        print(f"\nGraph {i:03d}:")
        filename = BASE_DIR / f"../graph_{i:03d}_probs.txt"

        graph = Graph(directed=True)
        graph.load_from_file(filename)

        exercise3 = Exercise3()
        exercise3.exercise3(graph, start, firewall_n)


def main_try_config():
    BASE_DIR = Path(__file__).resolve().parent
    filename = BASE_DIR / "../graph_007_probs.txt"

    start = 1
    firewallN = 1

    firewalls = [
        [(1, 19)],
        [(14, 0)],
        [(19, 12)],
        [(9, 8)],
        [(11, 8)],
        [(1, 15)],
        [(13, 18)]
    ]

    graph = Graph(directed=True)
    graph.load_from_file(filename)

    exercise3 = Exercise3()
    exercise3.try_config(graph, start, firewallN, firewalls)


if __name__ == "__main__":
    random.seed(42)  # Set a fixed seed for reproducibility
    main()
    # main_try_config()
