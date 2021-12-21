import graphviz

class Graph:
    """
    A class of undirected graphs.
    """
    def __init__(self, edgelist=None):
        "A graph can be initialized from None or from a list of edges."
        self._adjlist = {}
        self._valuelist = {}
        if edgelist:
            for node1,node2 in edgelist:
                for node in node1, node2:
                    if not node in self._adjlist.keys():
                        if node == node1:
                            self._adjlist[node] = set([node2])
                        elif node == node2:
                            self._adjlist[node] = set([node1])
                    else:
                        if node == node1:
                            self._adjlist[node].add(node2)
                        elif node == node2:
                            self._adjlist[node].add(node1)
                            
    def __str__(self):
        "Gives object representation as string (as adjacency list)."
        return str(self._adjlist)
    
    def __len__(self):
        "Gives number of vertices."
        return len(self._adjlist)
    
    def neighbors(self, vertex):
        "Gives the neighbours of vertex."
        return self._adjlist[vertex]
    
    def vertices(self):
        "Lists all vertices."
        return list(self._adjlist.keys())
    
    def edges(self):
        "Lists all edges in one direction, vertex1 <= vertex2"
        edges = []
        for vertex1 in self._adjlist.keys():
            for vertex2 in self._adjlist[vertex1]:
                if vertex1 <= vertex2:
                    edges.append((vertex1, vertex2))
        return edges
    
    def add_vertex(self, vertex):
        "Adds a vertex."
        if not vertex in self._adjlist:
            self._adjlist[vertex] = set()
        else:
            print(f'Vertex {vertex} is already part of the graph')
            
    def add_edge(self, vertex1, vertex2):
        "Adds an edge, and the vertices if needed."
        if vertex1 not in self._adjlist:
            self._adjlist[vertex1] = set()
        self._adjlist[vertex1].add(vertex2)
        if vertex2 not in self._adjlist:
            self._adjlist[vertex2] = set()
        self._adjlist[vertex2].add(vertex1)
        
    def remove_vertex(self, vertex):
        "Removes vertex and all edges including the vertex"
        if vertex in self._adjlist:
            del self._adjlist[vertex]
            for v in self._adjlist:
                if vertex in self._adjlist[v]:
                    self._adjlist[v].remove(vertex)
        else:
            print('Vertex not in Graph.')
                
    def remove_edge(self, vertex1, vertex2):
        "Removes an edge."
        for vertex in self._adjlist:
            if vertex == vertex1 and vertex2 in self._adjlist[vertex1]:
                self._adjlist[vertex1].remove(vertex2)
            elif vertex == vertex2 and vertex1 in self._adjlist[vertex2]:
                self._adjlist[vertex2].remove(vertex1)
                
    def get_vertex_value(self, vertex):
        "Gives the value of vertex, default None."
        if vertex in self.vertices():
            return self._valuelist.get(vertex, None)
        else:
            print('Cannot get value of an unknown vertex.')
    
    def set_vertex_value(self, vertex, value):
        "Destructive update of value of vertex."
        if vertex in self.vertices():
            self._valuelist[vertex] = value
        else:
            print('Cannot set value of an unknown vertex.')
            
            
class WeightedGraph(Graph):
    """
    A subclass of Graph, which stores edge weights.
    """
    def __init__(self, edgelist=None):
        "Initialize with empty graph and no edge weights."
        super().__init__(edgelist)
        self._weightlist = {}
        
    def get_weight(self, vertex1, vertex2):
        "Gives the weight of an edge consisting of the two given vertices"
        if (vertex1, vertex2) in self.edges():
            return self._weightlist.get((vertex1, vertex2), None)
        elif (vertex2, vertex1) in self.edges():
            return self._weightlist.get((vertex2, vertex1), None)
        else:
            print('Cannot get weight of an unknown edge.')

    def set_weight(self, vertex1, vertex2, weight):
        "Destructive update of weight of edge."
        if (vertex1, vertex2) in self.edges():
            self._weightlist[(vertex1, vertex2)] = weight
        elif (vertex2, vertex1) in self.edges():
            self._weightlist[(vertex2, vertex1)] = weight
        else:
            print('Cannot set weight of an unknown edge.')
    

def dijkstra(graph, source, cost=lambda u,v: 1):
    """Returns a dictionary, where the keys are all target vertices reachable from the source, 
    and their values are paths from the source to the target 
    (i.e. lists of vertices in the order that the shortest path traverses them)."""
    if not source in graph.vertices():
        print('Source node is not in graph.')
        return

    Q = []
    dist = {}
    prev = {}
    for vertex in graph.vertices():
        dist[vertex] = float('inf')
        prev[vertex] = None
        Q.append(vertex)   
    dist[source] = 0

    while Q:
        u = sorted([(vertex, dist[vertex]) for vertex in Q], key=lambda v:v[1])[0][0]
        Q.remove(u)
        for vertex in graph.neighbors(u):
            if vertex in Q:
                alt = dist[u] + cost (u, vertex)
                if alt < dist[vertex]:
                    dist[vertex] = alt
                    prev[vertex] = u


    paths = {}
    
    for vertex in graph.vertices():
        if vertex !=source:
            possible = True
            prev_vertex = vertex
            path = []
            
            while prev_vertex != source:
                if prev_vertex in prev:
                    path.append(prev_vertex)
                    prev_vertex = prev[prev_vertex]
                else:
                    possible = False
                    break
            if possible:
                path.append(source)
                path.reverse()
                paths[vertex] = path
    
    return paths
                
    
    # for vertex in dist:
    #     if prev[vertex]:
    #         paths[vertex] = [vertex]
    #         prev_vertex = prev[vertex]
    #         while not prev_vertex == source:
    #             paths[vertex].append(prev_vertex)
    #             prev_vertex = prev[prev_vertex]
    #         paths[vertex].append(source)
    #         paths[vertex].reverse()
            
    # return paths

        
            
        
        
   



def visualize(graph, view='dot', name='mygraph', nodecolors={}, engine='dot'):
    "Visualize undirected graphs with the dot method of Graphviz."
    dot = graphviz.Graph(engine=engine)
    for v in graph.vertices():
        if nodecolors and str(v) in nodecolors:
            dot.node(str(v), fillcolor=nodecolors[str(v)], style='filled')
        else:
            dot.node(str(v))
    for (a,b) in graph.edges():
        dot.edge(str(a),str(b))
    dot.render(f'{name}.gv', view=view)
     

def view_shortest(G, source, target, cost=lambda u,v: 1):
    "Visualizes undirected graphs, shortest path between source and target is highlighted by color."
    if source not in G.vertices() or target not in G.vertices():
        print('Cannot view shortest path. Source and target have to be part of the graph.')
        return
    if source == target:
        path = [source]
    
    # elif (source,target) not in G.():
    #     if (target,source) not in G.edges():
    #         print("There is no way between {} and {}".format(source, target))
    #     else:
    #         path = dijkstra(G, source, cost)[target]
    #         print(path)
    #         colormap = {str(v): 'orange' for v in path}
    #         print(colormap)
    #         visualize(G, view='dot', nodecolors=colormap)
            
    if target not in dijkstra(G, source, cost):
        
        print("There is no way between {} and {}".format(source, target))
    
    else:
        path = dijkstra(G, source, cost)[target]
        print(path)
        colormap = {str(v): 'orange' for v in path}
        print(colormap)
        visualize(G, view='dot', nodecolors=colormap)


def demo():
    G = Graph([(1,2),(1,3),(1,4),(3,4),(3,5),(3,6), (3,7), (6,7)])
    #visualize(G)
    view_shortest(G, 2, 6)
    
    #eds=[(0, 1), (1, 0), (2, 2)]
    #edges_test = [(0,1), (0,2), (0,3), (2,4), (2,5)]
    #T = WeightedGraph(edges_test)
    # T.add_edge(1, 11)
    # T.add_edge(1, 12)
    # T.add_edge(11, 111)
    # T.add_edge(111, 11)
    # T.add_edge(11, 112)
    # T.add_edge(1, 4)
    # T.add_edge(3, 4)
    # T.add_edge(11, 112)
    # T.add_vertex(7)
    # T.add_edge(3, 7)
    # T.add_edge(12, 112)
    # T.add_vertex(113)
    # T.add_edge(112,113)
    #for e in T.edges():
    #    T.set_weight(e[0], e[1], 1)
    # T.set_weight(1, 11, 15)

    # visualize(T)
    #view_shortest(T,0,5)
    # print(dijkstra(T, 1)[2])
    #view_shortest(T, 11, 7, cost=lambda u,v: T.get_weight(u,v))


if __name__ == '__main__':
    demo()

