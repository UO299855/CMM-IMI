from graph import Graph
from collections import deque

class Exercise2:

    def exercise2(self, graph: Graph, start : int, firewallN : int):
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
                    importance_matrix[start][i] += 1
    
            # Keep looping as long as there are vertices in the queue
            # Save the order of the vertices we visit
            stack = self._loop_over_queue(queue, visited, importance_matrix, reaching_edges)
            

            # We flatten the list of reaching edges and sort them by importance,
            # returning the top firewallN edges
            return self._get_candidate_edges(reaching_edges, importance_matrix)[:firewallN]


    def _get_candidate_edges(self, reaching_edges, importance_matrix):
        """
        Flattens the list of reaching edges and returns a set of unique edges.
        """
        unique_edges = set()
        for edge_list in reaching_edges:
            for edge in edge_list:
                if edge is not None:
                    unique_edges.add(tuple(sorted(edge)))
        candidate_edges = [list(edge) for edge in unique_edges]
        candidate_edges.sort(key=lambda edge:
            importance_matrix[edge[0]][edge[1]] + importance_matrix[edge[1]][edge[0]],
            reverse=True)
        return candidate_edges

    def _loop_over_stack(self,stack):
        pass

    def _loop_over_queue(self, queue, visited, importance_matrix, reaching_edges):
        """
        Keep looping as long as there are vertices in the queue
        """
        n = len(self.graph.vertices)
        while queue:
            current = queue.popleft()
            for i in range(n):
                # If this is a minimally soon visit
                if self.graph.adj_matrix[current][i] and visited[i] >= visited[current] + 1:
                    # If the vertex hasn't been visited yet
                    if visited[i] == n+1:
                        queue.append(i)
                        visited[i] = visited[current] + 1
                    # Add importance to this new edge
                    importance_matrix[current][i] += 1
                    reaching_edges[i].append([current, i])
                    # Recursively add importance to all edges leading to the current vertex
                    self._recursive_importance_update(importance_matrix, reaching_edges, current)

    def _recursive_importance_update(self, importance_matrix, reaching_edges, current):
        for edge in reaching_edges[current]:
            if edge is not None:
                importance_matrix[edge[0]][edge[1]] += 1
                self._recursive_importance_update(importance_matrix, reaching_edges, edge[0])

def main():
    start = 0
    firewallN = 2
    filename = "graph_test.txt"
    # filename = "graph_007_probs.txt"

    graph = Graph(directed=True)
    graph.load_from_file(filename)
    graph.display()
    exercise2 = Exercise2()
    print(exercise2.exercise2(graph, start, firewallN))
    pass

if __name__ == "__main__":
    main()