from graph import Graph
import heapq
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
            # Initialize max_prob array with 0.0 (minimum possible probability)
            # This reflects an initial absurdly low value
            max_prob : list[float] = [0.0] * n
            for i in self.burnt_set:
                max_prob[i] = 1.0
    
            # Initial variable setup
            importance_matrix = [[0.0 for _ in range(n)] for _ in range(n)]
            reaching_edges = [[None] if i in self.burnt_set else [] for i in range(n)]
                        
            # Initial priority queue setup (using negative values for max-heap behavior)
            queue = []

            # Accumulates path probabilities to each node from the start node(s)
            # Instead of accumulating the number of paths, we now accumulate the
            # probability of reaching each node
            path_probabilities = [0.0] * n
            for i in newly_burnt:
                path_probabilities[i] = 1.0
                max_prob[i] = 1.0
                heapq.heappush(queue, (-1.0, i))

            # Keep looping as long as there are vertices in the priority queue
            # Save the order of the vertices we visit
            stack = self._loop_over_queue(queue, max_prob, reaching_edges, path_probabilities)

            ## Assign importance to each edge based on the probability ratio
            self._loop_over_stack(stack, reaching_edges, importance_matrix, path_probabilities, max_prob)

            if self.verbose_process:
                self._matrix_print(importance_matrix)
                print()

            # We flatten the list of reaching edges and sort them by importance,
            # returning the top edge
            candidates = self._get_candidate_edges(reaching_edges, importance_matrix, max_prob)
            return candidates[0] if candidates else None

    def _fire_spread(self, last_newly_burnt : set[int]):
        """
        Simulates fire spread probabilistically.
        Neighbors attempt to catch fire only once from the current burning front.
        """
        newly_burnt_next = set()
        for burning in last_newly_burnt:
            for i in self.graph.adj[burning]:
                if i not in self.burnt_set and i not in newly_burnt_next:
                    p_uv = self.graph.adj[burning][i]
                    if random.random() <= p_uv:
                        newly_burnt_next.add(i)
        return newly_burnt_next

    def _get_candidate_edges(self, reaching_edges, importance_matrix, max_prob):
        """
        Flattens the list of reaching edges and returns a set of unique edges.
        Sorts the edges by their importance (most important first)
        and max probability to the fire (highest probability first).
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
                -round(importance_matrix[edge[0]][edge[1]] +
                importance_matrix[edge[1]][edge[0]], 9),
                # Second criterion: max(max_prob[i], max_prob[j]) -> largest prob first
                -max(max_prob[edge[0]], max_prob[edge[1]]),
                # Makes ties not arbitrary, but consistent across runs, as stated by the exercise instructions
                tuple(edge)
            )
        )
        return candidate_edges

    def _loop_over_stack(self, stack, reaching_edges, importance_matrix, path_probabilities, max_prob):
        """
        Assigns importance to each edge based on the proportion of probability 
        that flows through it from the source to the target.
        """
        n = len(path_probabilities)
        delta = [0.0] * n
        while stack:
            current = stack.pop()
            for edge in reaching_edges[current]:
               if edge is not None:
                parent = edge[0]
                p_uv = self.graph.adj[parent][current]

                if path_probabilities[current] > 0:
                    # The parent absorbs the weight of the current node,
                    # which represents the ratio of path probability that passes through it
                    c = (path_probabilities[parent] * p_uv) / path_probabilities[current] * (1 + delta[current])
                    delta[parent] += c

                    # The importance of the edge from parent to current is incremented by
                    # the same ratio
                    importance_matrix[parent][current] += c

    def _matrix_print(self, matrix):
        """
        Prints a matrix in a readable format.
        """
        for row in matrix:
            print(" ".join(f"{val:>6.2f}" for val in row))
                
    def _loop_over_queue(self, queue, max_prob, reaching_edges, path_probabilities):
        """
        Visits vertices applying Dijkstra's algorithm to find paths
        with the maximum propagation probability.
        """
        stack = []
        visited_set = set()
        
        while queue:
            prob_neg, current = heapq.heappop(queue)
            
            # Since heapq can hold duplicate nodes with worse probabilities,
            # we only process a node the first time it is popped (best probability)
            if current in visited_set:
                continue
            
            visited_set.add(current)
            stack.append(current)
            
            for i in self.graph.adj[current]:
                p_uv = self.graph.adj[current][i]
                new_prob = max_prob[current] * p_uv
                
                # If this is a strictly more probable path
                if new_prob > max_prob[i]:
                    reaching_edges[i] = [[current, i]]
                    path_probabilities[i] = path_probabilities[current] * p_uv
                    max_prob[i] = new_prob
                    heapq.heappush(queue, (-new_prob, i))
                
                # If it's an equally probable path
                elif new_prob == max_prob[i] and new_prob > 0:
                    reaching_edges[i].append([current, i])
                    path_probabilities[i] += path_probabilities[current] * p_uv
                    
        return stack

    def try_config(self, graph: Graph, start : int, firewallN : int, firewalls : list[list[tuple[int,int]]]):
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
                for cut_index in range(min(len(cuts), firewallN)):
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
    # Changed to 1 as specified in Challenge 3
    firewallN = 1
    BASE_DIR = Path(__file__).resolve().parent
    for i in [3,4,5,7,8,10]:
        print()
        print(f"\nGraph {i:03d}:")
        filename = BASE_DIR / f"../graph_{i:03d}_probs.txt"
        graph = Graph(directed=True)
        graph.load_from_file(filename)
        exercise3 = Exercise3()
        exercise3.exercise3(graph, start, firewallN)

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
    main()
    # main_try_config()