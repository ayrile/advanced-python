import csv
import haversine
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import sys
from sklearn.cluster import KMeans


AIRPORTS_FILE = './airports.dat'    #input for mk_airportdict()
ROUTES_FILE = './routes.dat'     #input for mk_routeset()


def mk_airportdict(FILE):
    """reads airport data from FILE and constructs a dictionary where the 
    location (and possible other information) about airports can be looked up"""
    airports = dict()
    
    with open(FILE, 'r', encoding='utf-8') as f:
        data = csv.reader(f)
        for line in data:
            try:
                airports[line[0]] = dict({'Name':line[1],
                                          'City':line[2],
                                          'Country':line[3],
                                          'IATA':line[4],
                                          'ICAO':line[5],
                                          'Latitude':line[6],
                                          'Longitude':line[7],
                                          'Altitude':line[8],
                                          'Timezone':line[9],
                                          'DST':line[10],
                                          'Tz database time zone':line[11],
                                          'Type':line[12],
                                          'Source':line[13]})
            except:
                pass
         
    return airports
            

def mk_routeset(FILE):
    "builds a set of routes that consist of pairs of keys to the airport dictionary"
    routes = set()
    
    with open(FILE, 'r', encoding='utf-8') as f:
        data = csv.reader(f)
        for line in data:
            try:
                if not line[3] == '\\N' and not line[5] == '\\N' and not line[3] == line[5]:
                    routes.add((line[3], line[5]))
            except:
                pass
    
    return routes


def mk_routegraph(routeset, airportdict):
    "builds an undirected graph from the routes"
    graph = nx.Graph()
    
    for node in airportdict:
        graph.add_node(node)
        graph.nodes[node]['position'] = (float(airportdict[node]['Latitude']), float(airportdict[node]['Longitude']))
        
    for route in routeset:
        lat1, lon1 = float(airportdict[route[0]]['Latitude']), float(airportdict[route[0]]['Longitude'])
        lat2, lon2 = float(airportdict[route[1]]['Latitude']), float(airportdict[route[1]]['Longitude'])
        distance = int(haversine.haversine((lat1, lon1), (lat2, lon2)))
        graph.add_edge(route[0], route[1])
        graph[route[0]][route[1]]['distance'] = distance

    return graph


def k_spanning_tree(G, airportdict, k = 1000):
    "returns a graph that consists of disconnected subtrees"
    min_edges = list(nx.algorithms.tree.mst.minimum_spanning_edges(G, algorithm='prim', weight='distance'))
    min_edges.sort(key=lambda x:x[2]['distance'])
    tree = min_edges[:-(k-1)]    #remove k-1 longest edges
    
    graph = nx.Graph()
    for edge in tree:
        if not edge[0] in graph.nodes:
            graph.add_node(edge[0])
            graph.nodes[edge[0]]['position'] = (float(airportdict[edge[0]]['Latitude']), float(airportdict[edge[0]]['Longitude']))
        if not edge[1] in graph.nodes:
            graph.add_node(edge[1])
            graph.nodes[edge[1]]['position'] = (float(airportdict[edge[1]]['Latitude']), float(airportdict[edge[1]]['Longitude']))
        graph.add_edge(edge[0], edge[1])
    
    return graph


def k_means(data, k=7):
    "returning a mapping from each point in the data to an integer in range(k)"
    X = np.array(data)
    kmeans = KMeans(n_clusters=k, random_state=0).fit_predict(X)
    clusters = dict(zip(data, kmeans))
    return clusters


def plot_airports(lats, lons, saveresult=False):
    "plots airports"
    fig = plt.figure(figsize=(16,10))
    plt.scatter(lons, lats, s=0.15)
    if saveresult:
        fig.savefig('airports_scatter.png')  
    plt.show()

    
def plot_routes(G, lats, lons, saveresult=False):
    "plots routes"
    fig = plt.figure(figsize=(16,10))
    plt.scatter(lons, lats, s=0.15)
    for edge in G.edges:
        lat1, lon1 = G.nodes[edge[0]]['position'][0], G.nodes[edge[0]]['position'][1]
        lat2, lon2 = G.nodes[edge[1]]['position'][0], G.nodes[edge[1]]['position'][1]
        plt.plot([lon1,lon2], [lat1,lat2], linewidth=0.15)
    if saveresult:
        fig.savefig('airports_routes.png')
    plt.show()


def plot_kspan(G_kspan, lats, lons, saveresult=False):
    "plots result of k-span clustering"
    fig = plt.figure(figsize=(16,10))
    plt.scatter(lons, lats, s=0.1)
    for edge in G_kspan.edges:
        lat1, lon1 = G_kspan.nodes[edge[0]]['position'][0], G_kspan.nodes[edge[0]]['position'][1]
        lat2, lon2 = G_kspan.nodes[edge[1]]['position'][0], G_kspan.nodes[edge[1]]['position'][1]
        plt.plot([lon1,lon2], [lat1,lat2], linewidth=1)
    if saveresult:
        fig.savefig('airports_kspan.png')
    plt.show()


def plot_kmeans(points, saveresult=False):
    "plots result of k-means clustering"
    clusters = dict()
    for p in points:
        if not points[p] in clusters:
            clusters[points[p]] = [p]
        else:
            clusters[points[p]].append(p)

    fig = plt.figure(figsize=(16,10))
    for cluster in clusters:
        lats = [clusters[cluster][i][0] for i in range(len(clusters[cluster]))]
        lons = [clusters[cluster][i][1] for i in range(len(clusters[cluster]))]            
        plt.scatter(lons, lats, s=0.25)
    if saveresult:
        fig.savefig('airports_kmeans.png')
    plt.show()
    

def demo():
    if len(sys.argv) == 1:
        print('Missing input.')
        return
    
    airport_dict = mk_airportdict(AIRPORTS_FILE)
    routes_set = mk_routeset(ROUTES_FILE)
    for route in routes_set.copy():
        if route[0] not in airport_dict or route[1] not in airport_dict:
            routes_set.remove(route)
    G = mk_routegraph(routes_set, airport_dict)
    lats = [G.nodes[node]['position'][0] for node in G.nodes]
    lons = [G.nodes[node]['position'][1] for node in G.nodes]
    
    if sys.argv[1:] == ['airports']:
        plot_airports(lats, lons)
    
    elif sys.argv[1:] == ['routes']:
        plot_routes(G, lats, lons)
    
    elif sys.argv[1] == 'span':
        try:
            k = int(sys.argv[2])
        except:
            print("Input could not be interpreted. Use format 'span <int>' please.")
            return
        G_kspan = k_spanning_tree(G, airport_dict, k)
        plot_kspan(G_kspan, lats, lons)
    
    elif sys.argv[1] == 'means':
        try: 
            k = int(sys.argv[2])
        except:
            print("Input could not be interpreted. Use format 'means <int>' please.")
            return
        Kmeans_cluster = k_means([G.nodes[node]['position'] for node in G.nodes], k)
        plot_kmeans(Kmeans_cluster)
            
    else:
        print('Input could not be interpreted.')
    
    
if __name__ == '__main__':
    demo()
