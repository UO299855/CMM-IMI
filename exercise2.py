from graph import Graph
from collections import deque

class Exercise2:

    def exercise2(self, graph: Graph, start : int, firewallN : int):
            self.graph = graph
            n = len(graph.adj)
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
            stack = self._loop_over_queue(queue, visited, reaching_edges)

            ## Assign importance to each edge based on how many times it is used
            self._loop_over_stack(stack, reaching_edges, importance_matrix)

            #TODO 
            self._print_matrix(importance_matrix)

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

    def _print_matrix(self, matrix):
        """
        Prints a matrix in a readable format.
        """
        for row in matrix:
            print(" ".join(f"{val:>5}" for val in row))

    def _loop_over_stack(self,stack,reaching_edges, importance_matrix):
        """
        Assigns importance to each edge based on how many times it is used
        in the shortest paths from the start vertex to all other vertices.
        """
        n = len(self.graph.vertices)
        node_weight = [0 for _ in range(n)]
        while(stack):
            current = stack.pop()
            for edge in reaching_edges[current]:
               if edge is not None:
                parent = edge[0]

                # The parent absorbs the weight of the current node,
                # which represents the number of shortest paths that pass through it
                # in order to propagate it to its own parent in the next iteration of the loop.
                node_weight[parent] += 1 + node_weight[current]

                # The importance of the edge from parent to current is incremented by 1
                # (because of this very edge [parent, current])
                # plus the accumulated weight of the current node.
                importance_matrix[parent][current] += 1 + node_weight[current]
                

    def _loop_over_queue(self, queue, visited, reaching_edges):
        """
        Visits vertices as the fire would
        Keeps looping as long as there are vertices in the queue
        """
        stack = []
        n = len(self.graph.adj)
        while queue:
            current = queue.popleft()
            stack.append(current)
            for i in self.graph.adj[current]:
                # If this is a minimally soon visit
                if visited[i] >= visited[current] + 1:
                    reaching_edges[i].append([current, i])
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

def main():
    start = 0
    firewallN = 2
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