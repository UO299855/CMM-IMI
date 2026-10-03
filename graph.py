class Graph:
    def __init__(self, directed=False):
        """
        Initializes an empty graph using matrices.
        :param directed: If True, edges are one-way. If False, they are bidirectional.
        """
        self.directed = directed
        self.vertices = []        # List of vertex names
        self.vertex_map = {}      # Maps vertex name to its matrix index
        self.adj_matrix = []      # 2D list for adjacency (False or True)
        self.weight_matrix = []   # 2D list for edge weights

    def add_vertex(self, vertex):
        """Adds a vertex to the graph if it doesn't already exist."""
        if vertex not in self.vertex_map:
            self.vertices.append(vertex)
            new_index = len(self.vertices) - 1
            self.vertex_map[vertex] = new_index

            # Expand existing rows with False (adjacency) and infinity (weight)
            for row in self.adj_matrix:
                row.append(False)
            for row in self.weight_matrix:
                row.append(float('inf'))

            # Add a new row for the new vertex
            new_adj_row = [False] * len(self.vertices)
            new_weight_row = [float('inf')] * len(self.vertices)
            
            # Distance to itself is usually 0
            new_weight_row[new_index] = 0 

            self.adj_matrix.append(new_adj_row)
            self.weight_matrix.append(new_weight_row)

    def add_edge(self, u, v, weight=1.0):
        """Adds an edge between vertex u and vertex v with a given weight."""
        self.add_vertex(u)
        self.add_vertex(v)

        i = self.vertex_map[u]
        j = self.vertex_map[v]

        # Set adjacency and weight
        self.adj_matrix[i][j] = True
        self.weight_matrix[i][j] = weight

        # If undirected, do the same for the reverse direction
        if not self.directed:
            self.adj_matrix[j][i] = True
            self.weight_matrix[j][i] = weight

    def display(self):
        """Prints the vertices, adjacency matrix, and weight matrix clearly labeled."""
        print("Vertices and their matrix indices:")
        for v, idx in self.vertex_map.items():
            print(f"  Vertex {v} -> Index {idx}")
        
        header = "      " + " ".join([f"{str(v):>5}" for v in self.vertices])
        
        print("\nAdjacency Matrix:")
        print(header)
        for idx, row in enumerate(self.adj_matrix):
            v_label = self.vertices[idx]
            row_str = " ".join([f"{str(int(val)):>5}" for val in row])
            print(f"{str(v_label):>5}: {row_str}")
            
        print("\nWeight Matrix:")
        print(header)
        for idx, row in enumerate(self.weight_matrix):
            v_label = self.vertices[idx]
            formatted_row = [str(w) if w != float('inf') else 'INF' for w in row]
            row_str = " ".join([f"{w:>5}" for w in formatted_row])
            print(f"{str(v_label):>5}: {row_str}")

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