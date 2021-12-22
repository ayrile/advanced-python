import json

# imports added in Lab3 version
import math
import os, sys
from .graphs import WeightedGraph, visualize, dijkstra   #.
#sys.path.append('../../mysite/')
#import settings
from django.conf import settings

# path changed from Lab2 version
# TODO: copy your json file from Lab 1 here
TRAM_FILE = os.path.join(settings.BASE_DIR, 'static/tramnetwork.json')


# TODO: use your lab 2 class definition, but add one method
class TramStop:
    def __init__(self, name, lines=None, lat=None, lon=None):
        self._lines = lines
        self._name = name
        self._position = (lat, lon)
        
    def add_line(self, line):
        if not line in self._lines:
            self._lines.append(line)
        
    def get_lines(self):
        return self._lines
    
    def get_name(self):
        return self._name
    
    def get_position(self):
        return self._position
    
    def set_position(self, lat, lon):
        self._position = (lat, lon)


class TramLine:
    def __init__(self, num, stops=None):
        self._number = num
        self._stops = stops
        
    def get_number(self):
        return self._number
    
    def get_stops(self):
        return self._stops


class TramNetwork(WeightedGraph):
    def __init__(self, lines, stops, times, edgelist=None):  
        self._stops = {}
        for stop in stops:
            name = stop 
            lines_serving_stop = lines_via_stop(lines, stop)
            lat, lon = stops[stop]['lat'], stops[stop]['lon']
            ts = TramStop(name, lines_serving_stop, lat, lon)
            self._stops[stop] = ts

        self._lines = {}
        for line in lines:
            num = line
            stops_on_line = lines[line]
            tl = TramLine(num, stops_on_line)
            self._lines[line] = tl

        if not edgelist:
            edgelist = []
        for line in self._lines:
            stops = self._lines[line].get_stops()  
            for i in range(len(stops)-1):
                vertex1, vertex2 = stops[i], stops[i+1]
                if (vertex1,vertex2) not in edgelist and (vertex2, vertex1) not in edgelist:
                    edgelist.append((vertex1, vertex2))

        super().__init__(edgelist)
        
        for stop in self._stops:
            self.set_vertex_value(self._stops[stop].get_name(), self._stops[stop].get_position())
            
        weights = {}
        for edge in self.edges():
            if edge[0] in times and edge[1] in times[edge[0]]:
                weights[edge] = times[edge[0]][edge[1]]
                self.set_weight(edge[0], edge[1], weights[edge])
            elif edge[1] in times and edge[0] in times[edge[1]]:               
                weights[edge] = times[edge[1]][edge[0]]
                self.set_weight(edge[0], edge[1], weights[edge])                

        
    def all_lines(self):
        return list(self._lines.keys())
    
    def all_stops(self):
        return list(self._stops.keys())

    def geo_distance(self, a, b):
        return distance_between_stops(self._stops, a, b, network=True)
    
    def line_stops(self, line):
        if line in self._lines:
            return self._lines[line].get_stops()

    def stop_lines(self, a):
        if a in self._stops:
            return self._stops[a].get_lines()
    
    def stop_position(self, a):    
        if a in self._stops:
            return self._stops[a].get_position()

    def transition_time(self, a, b):
        if (a,b) in self.edges() or (b,a) in self.edges():
            return self.get_weight(a, b)
        
    def extreme_positions(self):
        stops = self._stops.values()
        minlat = float(min([s._position[0] for s in stops]))
        maxlat = float(max([s._position[0] for s in stops]))
        minlon = float(min([s._position[1] for s in stops]))
        maxlon = float(max([s._position[1] for s in stops]))
        return minlon, minlat, maxlon, maxlat



def readTramNetwork(tramfile=TRAM_FILE):
    with open(tramfile) as trams:
        tramdict = json.loads(trams.read())
        linedict = tramdict['lines']
        stopdict = tramdict['stops']
        timesdict = tramdict['times']
    return TramNetwork(linedict, stopdict, timesdict)


def lines_via_stop(line_dict, stop):
    """returns list of lines that go via the given stop, 
    returns None if no lines go via the stop"""
    
    lines = []
    
    for line in line_dict:
        if stop in line_dict[line]:
            lines.append(line)  
    lines.sort(key=int)
    if lines:
        return lines
    return None


def distance_between_stops(stops_dict, stop1, stop2, network=False):
    """returns geographic distance between any two stops,
    returns None if unknown stop is entered,
    returns answer string if same stop is input twice
    """
    
    distance = 0
    
    if stop1 == stop2:
        return 'cannot enter same stop twice'
    
    if stop1 in stops_dict and stop2 in stops_dict:
        if network:
            lat1, lon1 = float(stops_dict[stop1].get_position()[0]) * math.pi/180, float(stops_dict[stop1].get_position()[1]) * math.pi/180
            lat2, lon2 = float(stops_dict[stop2].get_position()[0]) * math.pi/180, float(stops_dict[stop2].get_position()[1]) * math.pi/180
        else:
            lat1, lon1 = float(stops_dict[stop1]['lat']) * math.pi/180, float(stops_dict[stop1]['lon']) * math.pi/180
            lat2, lon2 = float(stops_dict[stop2]['lat']) * math.pi/180, float(stops_dict[stop2]['lon']) * math.pi/180
        R = 6371.009
        delta_phi = lat1-lat2
        phi_m = (lat1+lat2)/2
        delta_lambda = lon1-lon2
        distance = round(R * math.sqrt(delta_phi**2 + (math.cos(phi_m) * delta_lambda)**2), 3)
    else:
        return None
    
    return distance



# Bonus task 1: take changes into account and show used tram lines

def specialize_stops_to_lines(network):
    # TODO: write this function as specified
    stops = network.all_stops()
    lines = network.all_lines()
    
    G = WeightedGraph() 
    
    for stop in stops:
        for line in network.stop_lines(stop):
            G.add_vertex((stop, line))
    
    for edge in network.edges():
        for line in lines:
            if edge[0] in network.line_stops(line) and edge[1] in network.line_stops(line):
                G.add_edge((edge[0], line), (edge[1], line))
                
    for vertex1 in G.vertices():
        for vertex2 in G.vertices():
            if vertex1[0] == vertex2[0] and not vertex1 == vertex2:
                G.add_edge(vertex1, vertex2)
                
    for vertex in G.vertices():
        G.set_vertex_value(vertex, network.stop_position(vertex[0]))
          
    for edge in G.edges():
        if edge[0][0] == edge[1][0]:
            G.set_weight(edge[0], edge[1], dict({'time':0, 'distance':0}))
        else:
            time = network.transition_time(edge[0][0], edge[1][0])
            distance = network.geo_distance(edge[0][0], edge[1][0])
            G.set_weight(edge[0], edge[1], dict({'time':time, 'distance':distance}))
            
    return G


def specialized_transition_time(spec_network, a, b, changetime=10):
    # TODO: write this function as specified  
    options = []
    
    for vertex1 in spec_network.vertices():
        if a in vertex1:
            for vertex2 in spec_network.vertices():
                if b in vertex2:
                    path = dijkstra(spec_network, vertex1, 
                                    cost=lambda u,v: spec_network.get_weight(u,v)['time'], 
                                    give_total=True)[0][vertex2]
                    time = dijkstra(spec_network, vertex1, 
                                    cost=lambda u,v: spec_network.get_weight(u,v)['time'], 
                                    give_total=True)[1][vertex2]
                    options.append([path, time])
                    
    for opt in options:
        path = opt[0]
        line_changes = 0
        for i in range(len(path)-1):
            if path[i][0] == path[i+1][0]:
                line_changes += 1
        opt[1] += changetime * line_changes
        
    options.sort(key=lambda p:p[1])
    quickest = options[0]
    
    quickest_path = quickest[0]
    website_output = []
    for i in range(len(quickest_path)):
        if i == 0:
            website_output.append(f'{quickest_path[i][1]} {quickest_path[i][0]} - ')
        elif not quickest_path[i][1] == quickest_path[i-1][1]:
            website_output.append(f'{quickest_path[i][1]} {quickest_path[i][0]} - ')
        else:
            website_output.append(f'{quickest_path[i][0]} - ')
    website_output.append(f'{str(quickest[1])} minutes')
    
    return 'Quickest: ' + ''.join(website_output)


def specialized_geo_distance(spec_network, a, b, changedistance=0.02):
    # TODO: write this function as specified
    options = []
    
    for vertex1 in spec_network.vertices():
        if a in vertex1:
            for vertex2 in spec_network.vertices():
                if b in vertex2:
                    path = dijkstra(spec_network, vertex1, 
                                    cost=lambda u,v: spec_network.get_weight(u,v)['distance'], 
                                    give_total=True)[0][vertex2]
                    distance = dijkstra(spec_network, vertex1, 
                                    cost=lambda u,v: spec_network.get_weight(u,v)['distance'], 
                                    give_total=True)[1][vertex2]
                    options.append([path, distance])
                    
    for opt in options:
        path = opt[0]
        line_changes = 0
        for i in range(len(path)-1):
            if path[i][0] == path[i+1][0]:
                line_changes += 1
        opt[1] += changedistance * line_changes
        
    options.sort(key=lambda p:p[1])
    shortest = options[0]
    
    shortest_path = shortest[0]
    website_output = []
    for i in range(len(shortest_path)):
        if i == 0:
            website_output.append(f'{shortest_path[i][1]} {shortest_path[i][0]} - ')
        elif not shortest_path[i][1] == shortest_path[i-1][1]:
            website_output.append(f'{shortest_path[i][1]} {shortest_path[i][0]} - ')
        else:
            website_output.append(f'{shortest_path[i][0]} - ')
    website_output.append(f'{str(shortest[1])} km')
    
    return 'Shortest: ' + ''.join(website_output)


#sn = specialize_stops_to_lines(readTramNetwork())
#print(specialized_transition_time(sn, 'Chalmers', 'Komettorget'))
#print(specialized_geo_distance(sn, 'Chalmers', 'Komettorget'))




