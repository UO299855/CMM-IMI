from graph import Graph
from collections import deque

class Exercise2:

    def exercise2(self, graph: Graph, start : int, firewallN : int):
        cuts = []
        for _ in range(firewallN):
            best = self._best_edge(graph, start)
            if best is None: break
            cuts.append(best)
            graph.set_firewall(best[0], best[1])

        return cuts

    def _best_edge(self, graph: Graph, start : int):
            self.graph = graph
            n = len(graph.vertices)
            # Initialize visited array with a value larger than any possible distance
            visited : list[int] = [n+1 for _ in range(n)]
            visited[start] = 0
    
            # Initial variable setup
            importance_matrix = [[0 for _ in range(n)] for _ in range(n)]
            reaching_edges = [[] for _ in range(n)]
            reaching_edges[start] = [None]
            
            # Initial queue setup
            queue  = deque()
            for i in range(n):
                if graph.adj_matrix[start][i]:
                    queue.append(i)
                    visited[i] = 1
                    reaching_edges[i].append([start, i])

            most_distant_set = set()

            # Keep looping as long as there are vertices in the queue
            # Save the order of the vertices we visit
            stack = self._loop_over_queue(queue, visited, reaching_edges, most_distant_set)

            ## Assign importance to each edge based on how many times it is used
            self._loop_over_stack(stack, reaching_edges, importance_matrix, most_distant_set)

            # TODO
            self._matrix_print(importance_matrix)

            # We flatten the list of reaching edges and sort them by importance,
            # returning the top edge
            return self._get_candidate_edges(reaching_edges, importance_matrix, visited)[0]


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
                -(importance_matrix[edge[0]][edge[1]] +
                importance_matrix[edge[1]][edge[0]]),
                # Second criterion: min(visited[i], visited[j])
                min(visited[edge[0]], visited[edge[1]])
            )
        )
        return candidate_edges

    def _loop_over_stack(self,stack,reaching_edges, importance_matrix, most_distant_set):
        """
        Assigns importance to each edge based on how many times it is used
        in the shortest paths from the start vertex to all other vertices.
        """
        n = len(self.graph.vertices)
        node_weight = [1 if i in most_distant_set else 0 for i in range(n)]
        while(stack):
            current = stack.pop()
            for edge in reaching_edges[current]:
               if edge is not None:
                parent = edge[0]

                # The parent absorbs the weight of the current node,
                # which represents the number of shortest paths that pass through it
                # in order to propagate it to its own parent in the next iteration of the loop.
                node_weight[parent] += node_weight[current]

                # The importance of the edge from parent to current is incremented by 1
                # (because of this very edge [parent, current])
                # plus the accumulated weight of the current node.
                importance_matrix[parent][current] += node_weight[current] * len(reaching_edges[parent])

    def _matrix_print(self, matrix):
        """
        Prints a matrix in a readable format.
        """
        for row in matrix:
            print(" ".join(f"{val:>5}" for val in row))
                

    def _loop_over_queue(self, queue, visited, reaching_edges, most_distant_set):
        """
        Visits vertices as the fire would
        Keeps looping as long as there are vertices in the queue
        """
        stack = []
        n = len(self.graph.vertices)
        while queue:
            current = queue.popleft()
            stack.append(current)
            no_new_visits = True
            for i in range(n):
                # If this is a minimally soon visit
                if self.graph.adj_matrix[current][i] and visited[i] >= visited[current] + 1:
                    no_new_visits = False
                    reaching_edges[i].append([current, i])
                    # If the vertex hasn't been visited yet
                    if visited[i] == n+1:
                        queue.append(i)
                        visited[i] = visited[current] + 1
            if no_new_visits:
                most_distant_set.add(current)
        return stack

    def _recursive_importance_update(self, importance_matrix, reaching_edges, current):
        for edge in reaching_edges[current]:
            if edge is not None:
                importance_matrix[edge[0]][edge[1]] += 1
                self._recursive_importance_update(importance_matrix, reaching_edges, edge[0])

def main():
    start = 0
    firewallN = 1
    filename = "graph_test2.txt"
    # filename = "graph_007_probs.txt"

    graph = Graph(directed=True)
    graph.load_from_file(filename)
    # graph.display()
    exercise2 = Exercise2()
    print(exercise2.exercise2(graph, start, firewallN))
    pass

if __name__ == "__main__":
    main()