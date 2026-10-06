class Graph:
    def __init__(self, directed=False):
        """
        Initializes an empty graph using matrices.
        :param directed: If True, edges are one-way. If False, they are bidirectional.
        """
        self.directed = directed
        self.adj : dict[int,dict[int, float]] = {}             # Adjacency list representation

    def add_vertex(self, vertex : int):
        """Adds a vertex to the graph if it doesn't already exist."""
        if vertex not in self.adj:
            self.adj[vertex] = {}

    def add_edge(self, u, v, weight=1.0):
        """Adds an edge between vertex u and vertex v with a given weight."""
        self.add_vertex(u)
        self.add_vertex(v)

        self.adj[u][v] = weight
        # If undirected, do the same for the reverse direction
        if not self.directed:
            self.adj[v][u] = weight

    def set_firewall(self, u : int, v : int):
        """
        Sets a firewall between two given nodes
        """
        # Remove the edge from u to v and from v to u
        if u in self.adj and v in self.adj:
            self.adj[u].pop(v, None)
            self.adj[v].pop(u, None)
        else:
            raise ValueError("Invalid firewall")

    def clone(self):
            new_graph = Graph(directed=self.directed)
            new_graph.directed = self.directed
            # Shallow copy of the adjacency list to ensure we don't modify the original graph
            new_graph.adj = {k: v.copy() for k, v in self.adj.items()}
            return new_graph

    def load_from_file(self, filename):
        """
        Loads graph data from a text file.
        Expected format per line: source target weight (separated by whitespace)
        """
        vertices_set = set()
        edges = []
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue  # Skip empty lines
                
                parts = line.split()
                if len(parts) >= 2:
                    # Keep as integer if numeric, or parse accordingly
                    u = int(parts[0])
                    v = int(parts[1])
                    
                    weight = float(parts[2]) if len(parts) > 2 else 1.0
                    
                    edges.append((u, v, weight))
                    vertices_set.add(u)
                    vertices_set.add(v)
                    
        # Add all vertices to the graph
        for vertex in vertices_set:
            self.add_vertex(vertex)
        # Add all edges to the graph
        for u, v, weight in edges:
            self.add_edge(u, v, weight)