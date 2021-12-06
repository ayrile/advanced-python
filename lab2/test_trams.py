# -*- coding: utf-8 -*-

from hypothesis import given, strategies as st
from trams import *
from graphs import *
import unittest
from collections import *
import sys

sys.path.append( '.' )
sys.path.append('../lab1/')
TRAM_FILE = 'tramnetwork.json'


def BFS(G, node, goal=lambda n: False):
     
      Q = deque()
      explored = [node]
      Q.append(node)
      while Q:
          v = Q.popleft()
          if goal(v):
              return v
          for w in G.neighbors(v):
              if w not in explored:
                  explored.append(w)
                  Q.append(w)
      return explored

class TestTramNetWork(unittest.TestCase):

    def setUp(self):
        with open(TRAM_FILE) as trams:
            self.tramdict = json.loads(trams.read())
            self.stopdict = self.tramdict['stops']
            self.linedict = self.tramdict['lines']
            self.timesdict = self.tramdict['times']
    
    def test_connectedness(self):
        G = TramNetwork(self.linedict, self.stopdict, self.timesdict)
        stopset = G.all_stops()
        root = G.all_stops()[0]
        for stop in stopset:
            self.assertIn(stop,BFS(G,root))
            
    def test_stops_exist(self):
        "tests that all tram stops listed in the original dictionary are included in the TramNetwork"
        G = TramNetwork(self.linedict, self.stopdict, self.timesdict)
        stops = [s for s in self.stopdict]
        for stop in G.all_stops():
            self.assertIn(stop, stops, msg = stop + ' not in Graph')
        
    def test_lines_exist(self):
        "tests that all tram lines listed in the original dictionary are included in the TramNetwork"
        G = TramNetwork(self.linedict, self.stopdict, self.timesdict)
        lines = [l for l in self.linedict]
        for line in G.all_lines():
            self.assertIn(line, lines, msg = line + ' not in Graph')
   
        
    def test_stop_is_same_in_lines(self):
        "tests that the list of stops for each tram line is the same in TramNetwork and original file"
        G = TramNetwork(self.linedict, self.stopdict, self.timesdict)
        for line in self.linedict:
            stops_on_line_file = self.linedict[line]
            stops_on_line_network = G._lines[line].get_stops()
            self.assertEqual(stops_on_line_file, stops_on_line_network, msg = line + ' is not the same in network')
            
    def test_distance_feasible(self):
        "tests that all distances are feasible, meaning less than 20 km"
        G = TramNetwork(self.linedict, self.stopdict, self.timesdict)
        max_distance = 20
        for stop1 in G.all_stops():
            for stop2 in G.all_stops():
                if not stop1 == stop2:
                    distance = G.geo_distance(stop1, stop2)
                    self.assertLessEqual(distance, max_distance, msg = f'distance between {stop1} and {stop2} is {distance} (not feasible)')

    def test_equal_travel_time(self):
        "tests that the transition time from a to b is always the same as the transition time from b to a"
        G = TramNetwork(self.linedict, self.stopdict, self.timesdict)
        for stop1 in self.stopdict:
            for stop2 in self.stopdict:
                t1 = G.transition_time(stop1, stop2)
                t2 = G.transition_time(stop2, stop1)
                self.assertEqual(t1, t2, msg = f'times not the same in both ways for {stop1} and {stop2}')
                        


if __name__ == '__main__':
    unittest.main()
