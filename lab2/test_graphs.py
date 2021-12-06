# -*- coding: utf-8 -*-
from hypothesis import given,assume,strategies as st
from graphs import *


' generate small integers, 0...10 '
smallints = st.integers(min_value=0, max_value=10)

' generate pairs of small integers '
twoints = st.tuples(smallints, smallints)

' generate lists of pairs of small integers '
' where x != y for each pair (x, y) '
st_edge_list = st.lists(twoints,min_size=3,unique_by=(lambda x: x[0], lambda x: x[1]))

@given(st_edge_list)
def test_edges_in_vertices(eds):
    
    G = Graph()
    for (a,b) in eds:
        G.add_edge(a,b)
     # if (a, b) is in edges(), both a and b are in vertices()
        
            
        assert a in G.vertices()
        assert b in G.vertices()

@given(st_edge_list)
def test_neighbour(eds):
    G = Graph()
    for (a,b) in eds:
        G.add_edge(a,b)
    # if a has b as its neighbour, then b has a as its neighbour
        
        assert a in G.neighbors(b)
            
        assert b in G.neighbors(a)

@given(st_edge_list)
def test_shortestpath(eds):
    G = WeightedGraph()
    rw = []  #randomweight
    for i in range(1,21):
        rw.append(i)
        
    for (a,b) in eds:
        G.add_edge(a,b)
        for i,j in enumerate(G.edges()):
            G.set_weight(j[0], j[1], rw[i] )
 
    assume( b in dijkstra(G, a, cost=lambda u,v: 1) and a!=b)
        
    b_a_shortest = dijkstra(G,b)[a]
    b_a_shortest.reverse()
    assert dijkstra(G,a)[b] == b_a_shortest

if __name__ == '__main__':
    test_edges_in_vertices()
    test_neighbour()
    test_shortestpath()