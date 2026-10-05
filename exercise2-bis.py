from graph import Graph
from collections import deque

class Exercise2:

    def __init__(self, verbose_process = False, verbose_output = True):
        self.verbose_process = verbose_process
        self.verbose_output = verbose_output

    def exercise2(self, graph: Graph, start : int, firewallN : int):
        self.graph = graph
        self.burnt_set = set()
            
        total_cuts = []
        newly_burnt = set([start])
        while newly_burnt:
            cuts = []
            self.burnt_set.update(newly_burnt)
            for _ in range(firewallN):
                best = self._best_edge(newly_burnt)
                if best is None: break
                cuts.append(best)
                self.graph.set_firewall(best[0], best[1])
            newly_burnt = self._fire_spread()
            total_cuts.append(cuts)

        if self.verbose_output:
            self._print_results(total_cuts, self.burnt_set)

        return total_cuts, self.burnt_set

    def _print_results(self, total_cuts, burnt_set):
        print(f"Burnt vertices ({len(burnt_set)}):", sorted(burnt_set))
        print(f"Saved {len(self.graph.vertices) - len(burnt_set)} vertices")
        print("Firewall cuts made:")
        for i, cuts in enumerate(total_cuts):
            print(f"  Step {i+1}: {cuts}")

    def _best_edge(self, newly_burnt : set[int]):
            n = len(self.graph.vertices)
            # Initialize visited array with a value larger than any possible distance
            visited : list[int] = [n+1] * n
            for i in self.burnt_set:
                visited[i] = 0
    
            # Initial variable setup
            importance_matrix = [[0 for _ in range(n)] for _ in range(n)]
            reaching_edges = [[None] if i in self.burnt_set else [] for i in range(n)]
                        
            # Initial queue setup
            queue  = deque(newly_burnt)
            # Counts the number of shortest paths to each node from the start node(s)
            num_paths_to_node = [0] * n
            for i in newly_burnt:
                num_paths_to_node[i] = 1

            # Keep looping as long as there are vertices in the queue
            # Save the order of the vertices we visit
            stack = self._loop_over_queue(queue, visited, reaching_edges, num_paths_to_node)

            ## Assign importance to each edge based on how many times it is used
            self._loop_over_stack(stack, reaching_edges, importance_matrix, num_paths_to_node)


            if self.verbose_process:
                self._matrix_print(importance_matrix)
                print()

            # We flatten the list of reaching edges and sort them by importance,
            # returning the top edge
            candidates = self._get_candidate_edges(reaching_edges, importance_matrix, visited)
            return candidates[0] if candidates else None

    def _fire_spread(self):
        newly_burnt = set()
        for burning in self.burnt_set:
            for i in range(len(self.graph.vertices)):
                if self.graph.adj_matrix[burning][i] and i not in self.burnt_set:
                    newly_burnt.add(i)
        return newly_burnt


    def _get_candidate_edges(self, reaching_edges, importance_matrix, visited):
        """
        Flattens the list of reaching edges and returns a set of unique edges.
        Sorts the edges by their importance (most important first)
        and distance to the fire (least distant first).
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
                # Second criterion: min(visited[i], visited[j])
                min(visited[edge[0]], visited[edge[1]])
            )
        )
        return candidate_edges

    def _loop_over_stack(self,stack,reaching_edges, importance_matrix, num_paths_to_node):
        """
        Assigns importance to each edge based on how many times it is used
        in the shortest paths from the start vertex to all other vertices.
        """
        n = len(num_paths_to_node)
        delta = [0.0] * n
        while(stack):
            current = stack.pop()
            for edge in reaching_edges[current]:
               if edge is not None:
                parent = edge[0]

                # The parent absorbs the weight of the current node,
                # which represents the ratio of shortest paths that pass through it
                # in order to propagate it to its own parent in the next iteration of the loop.
                c = num_paths_to_node[parent] / num_paths_to_node[current] * (1 + delta[current])
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
                

    def _loop_over_queue(self, queue, visited, reaching_edges, num_paths_to_node):
        """
        Visits vertices as the fire would
        Keeps looping as long as there are vertices in the queue
        """
        stack = []
        n = len(self.graph.vertices)
        while queue:
            current = queue.popleft()
            stack.append(current)
            for i in range(n):
                # If this is a minimally soon visit
                if self.graph.adj_matrix[current][i] and visited[i] >= visited[current] + 1:
                    reaching_edges[i].append([current, i])
                    num_paths_to_node[i] += num_paths_to_node[current]
                    # If the vertex hasn't been visited yet
                    if visited[i] == n+1:
                        queue.append(i)
                        visited[i] = visited[current] + 1
        return stack

    def _recursive_importance_update(self, importance_matrix, reaching_edges, current):
        for edge in reaching_edges[current]:
            if edge is not None:
                importance_matrix[edge[0]][edge[1]] += 1
                self._recursive_importance_update(importance_matrix, reaching_edges, edge[0])

    def try_config(self, graph: Graph, start : int, firewallN : int, firewalls : list[list[list[int]]]):
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
            newly_burnt = self._fire_spread()
            iter = iter + 1

        if self.verbose_output:
            self._print_results(actual_firewalls, self.burnt_set)

        return len(self.burnt_set)

def main(filename, start, firewallN):    

    graph = Graph(directed=True)
    graph.load_from_file(filename)
    # graph.display()
    exercise2 = Exercise2()
    exercise2.exercise2(graph, start, firewallN)
    pass

def main_try_config(filename, start, firewallN, firewalls):
    graph = Graph(directed=True)
    graph.load_from_file(filename)
    # graph.display()
    exercise2 = Exercise2()
    exercise2.try_config(graph, start, firewallN, firewalls)

if __name__ == "__main__":
    start = 1
    firewallN = 2
    filename = "graph_007_probs.txt"
    firewalls = [
        [(1, 19), (15, 12)],
        [(14, 0), (15, 4)],
        [(19, 12), (19, 18)],
        [(9, 8), (9, 18)],
        [(11, 8)],
        [(1, 15), (12, 4)],
        [(13, 18)]
    ]
    main_try_config(filename, start, firewallN, firewalls)
    # for i in [3,4,5,7,8,10]:
    #     print(f"\nGraph {i:03d}:")
    #     main(f"graph_{i:03d}_probs.txt", start, firewallN)
    #     print()