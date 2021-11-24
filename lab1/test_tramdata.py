import unittest
from tramdata import *

TRAM_FILE = './tramnetwork.json'

class TestTramData(unittest.TestCase):

    def setUp(self):
        with open(TRAM_FILE) as trams:
            self.tramdict = json.loads(trams.read())
            self.stopdict = self.tramdict['stops']
            self.linedict = self.tramdict['lines']
            self.timesdict = self.tramdict['times']

    def test_stops_exist(self):
        stopset = {stop for line in self.linedict for stop in self.linedict[line]}
        for stop in stopset:
            self.assertIn(stop, self.stopdict, msg = stop + ' not in stopdict')

    def test_lines_exist(self):
        """tests that all tram lines listed in the original text file tramlines.txt are included in linedict"""
        lines_in_dict = [line for line in self.linedict]
        lines_in_txt = []
        with open(TXT_FILE_INPUT, 'r') as txt:
            data = txt.readlines()  
        data = [r.rstrip() for r in data]
        for row in data:
            if row and row[-1] == ':':
                lines_in_txt.append(row[:-1].strip())
        for line in lines_in_txt:
            self.assertIn(line, lines_in_dict, msg = line + ' not in linedict')
    
    def test_stop_is_same_in_lines(self):
        """tests that the list of stops for each tramline is the same in tramlines.txt and linedict"""
        tramlines = dict({})
        with open(TXT_FILE_INPUT, 'r', encoding='UTF-8') as tramlines_file:
            data = tramlines_file.readlines()
        data = [r.rstrip() for r in data]

        for row in data:
            if row and row[-1] ==':':
                current_line = row.strip(':')
                tramlines[current_line] = []
            else:
                stop = row[:-5].strip()
                if row:
                    tramlines[current_line].append(stop)

        for line in tramlines:
            self.assertEqual(tramlines[line], self.linedict[line], msg = line + ' is not the same in linedict')


    def test_distance_feasible(self):
        """tests that all distances are feasible, meaning less than 20 km"""
        max_distance = 20
        for stop1 in self.stopdict:
            for stop2 in self.stopdict:
                if not stop1 == stop2:
                    distance = distance_between_stops(self.stopdict, stop1, stop2)
                    self.assertLessEqual(distance, max_distance, msg = f'distance between {stop1} and {stop2} is {distance} (not feasible)')

    def test_equal_travel_time(self):
        """tests that the time from a to b is always the same as the time from b to a along the same line"""
        for stop1 in self.stopdict:
            for stop2 in self.stopdict:
                for line in self.linedict:
                    if stop1 in self.linedict[line] and stop2 in self.linedict[line]:
                        t1 = time_between_stops(self.linedict, self.timesdict, line, stop1, stop2)
                        t2 = time_between_stops(self.linedict, self.timesdict, line, stop2, stop1)
                        self.assertEqual(t1, t2, msg = f'times not the same in both ways for {stop1} and {stop2}')

    def test_answer_query(self):
        """tests that queries are parsed and interpreted correctly"""
        #test for lines_via_stop()
        inputs = ['Chalmers', 'Chaldjshd']
        for stop in inputs:
            query = f'via {stop}'
            answer_from_function = lines_via_stop(self.linedict, stop)
            answer_from_query = answer_query(self.tramdict, query)
            self.assertEqual(answer_from_function, answer_from_query, msg = 'dialogue does not give expected answer regarding lines_via_stop()')
        #test for lines_between_stops()
        inputs = [('Chalmers', 'Hjalmar Brantingsplatsen'),
                  ('Chalguf', 'Hjalmar Brantingsplatsen'),
                  ('Chalmers', 'Östra Sjukhuset'),
                  ('Chalmers', 'Chalmers')]
        for stop1, stop2 in inputs:
            query = f'between {stop1} and {stop2}'
            answer_from_function = lines_between_stops(self.linedict, stop1, stop2)
            answer_from_query = answer_query(self.tramdict, query)
            self.assertEqual(answer_from_function, answer_from_query, msg = 'dialogue does not give expected answer regarding lines_between_stops()')
        #test for time_between_stops()
        inputs = [('10', 'Hjalmar Brantingsplatsen', 'Chalmers'),
                  ('13', 'Hjalmar Brantingsplatsen', 'Chalmers'),
                  ('10', 'Chalmers', 'Chalmers'),
                  ('dhbjhdj', 'Hjalmar Brantingsplatsen', 'Chalmers'),
                  ('10', 'Hjalmar Brantiubuddb', 'Chalmers'),
                  ('1', 'Chalmers', 'Östra Sjukhuset')]
        for line, stop1, stop2 in inputs:
            query = f'time with {line} from {stop1} to {stop2}'
            answer_from_function = time_between_stops(self.linedict, self.timesdict, line, stop1, stop2)
            answer_from_query = answer_query(self.tramdict, query)
            self.assertEqual(answer_from_function, answer_from_query, msg = 'dialogue does not give expected answer regarding time_between_stops()')
        #test for distance_between_stops()
        inputs = [('Chalmers', 'Järntorget'),
                  ('Chaldjhcvjsd', 'Järntorget'),
                  ('Chalmers', 'Chalmers')]
        for stop1, stop2 in inputs:
            query = f'distance from {stop1} to {stop2}'
            answer_from_function = distance_between_stops(self.stopdict, stop1, stop2)
            answer_from_query = answer_query(self.tramdict, query)
            self.assertEqual(answer_from_function, answer_from_query, msg = 'dialogue does not give expected answer regarding distance_between_stops()')


if __name__ == '__main__':
    unittest.main()
    