import graphs
import json
import sys
sys.path.append( '.' )
sys.path.append('../lab1/')
from tramdata import * 

TRAM_FILE = '../lab1/tramnetwork.json'

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


class TramNetwork(graphs.WeightedGraph):
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


def readTramNetwork(tramfile=TRAM_FILE):
    with open(tramfile) as trams:
        tramdict = json.loads(trams.read())
        linedict = tramdict['lines']
        stopdict = tramdict['stops']
        timesdict = tramdict['times']
    return TramNetwork(linedict, stopdict, timesdict)


def demo():
    G = readTramNetwork()
    a, b = input('from,to ').split(',')
    graphs.view_shortest(G, a, b)
    #graphs.view_shortest(G, a, b, cost=lambda u,v: G.get_weight(u,v))


if __name__ == '__main__':
    demo()
