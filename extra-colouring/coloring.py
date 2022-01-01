import sys
import graphviz
sys.path.append('../lab2/')
import graphs as gr


def simplify(graph, n=4):
    "returning the stack of removed vertices, when n colours are available"
    stack = []
    num_of_nodes = len(graph)
    
    while len(graph) > 0:
        if not num_of_nodes == len(graph):
            print(f'graph cannot be simplified with {n} degrees')
            return 
        for vertex in graph.vertices():
            if len(graph.neighbors(vertex)) < n:
                stack.append(vertex)
                graph.remove_vertex(vertex)
                break
        num_of_nodes -= 1
    stack.reverse()
    
    return stack
        

def rebuild(graph, stack, colors):
    """returning a dictionary that for each vertex assigns a color from the
    list colors (e.g. ['red', 'green', 'blue'])"""
    c_dict = dict()
    
    for vertex in stack:
        neighbors = graph.neighbors(vertex)
        colors_taken = []
        for neigh in neighbors:
            if str(neigh) in c_dict:
                colors_taken.append(c_dict[str(neigh)])
        
        if set(colors) == set(colors_taken):
            print(f'no color left for {vertex}')
        
        for col in colors:
            if not col in colors_taken:
                c_dict[str(vertex)] = col
                break

    return c_dict


def viz_color_graph(graph, colors):
    """combines the two functions simplify() and rebuild() and shows a GraphViz
    image of graph coloured with colours from the list colors, whose length is
    passed as n to simplify()"""
    graph_copy = gr.Graph(graph.edges())
    stack = simplify(graph, len(colors))
    if not stack:
        return
    color_dict = rebuild(graph_copy, stack, colors)
    gr.visualize(graph_copy, nodecolors=color_dict)
    
    
def demo():
    G = gr.Graph([(1,2),(1,3),(1,4),(3,4),(3,5),(3,6), (3,7), (6,7)])
    viz_color_graph(G,['red', 'green', 'blue'])
    
    
if __name__ == '__main__':
    demo()
    