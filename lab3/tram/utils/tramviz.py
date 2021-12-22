# baseline tram visualization for Lab 3, modified to work with Django

from .trams import readTramNetwork     #.
from .graphs import dijkstra           #.
import graphviz
import json
import os, sys
#sys.path.append('../../mysite/')
#import settings
from django.conf import settings

# to be defined in Bonus task 1, but already included as mock-up
from .trams import specialize_stops_to_lines, specialized_geo_distance, specialized_transition_time   #.

SHORTEST_PATH_SVG = os.path.join(settings.BASE_DIR,
                        'tram/templates/tram/images/shortest_path.svg')

# assign colors to lines, indexed by line number; not quite accurate
gbg_linecolors = {
    1: 'gray', 2: 'yellow', 3: 'blue', 4: 'green', 5: 'red',
    6: 'orange', 7: 'brown', 8: 'purple', 9: 'blue',
    10: 'lightgreen', 11: 'black', 13: 'pink'}


def scaled_position(network):
    # compute the scale of the map
    minlat, minlon, maxlat, maxlon = network.extreme_positions()
    size_x = maxlon - minlon
    scalefactor = len(network)/4  # heuristic
    x_factor = scalefactor/size_x
    size_y = maxlat - minlat
    y_factor = scalefactor/size_y
    return lambda xy: (x_factor*(xy[0]-minlon), y_factor*(xy[1]-minlat))

# Bonus task 2: redefine this so that it returns the actual traffic information
import urllib.parse
from bs4 import BeautifulSoup
def find_all_links(url='https://www.vasttrafik.se/reseplanering/hallplatslista/'):
    # finds all <a> tags on the given website
    html_doc = urllib.request.urlopen(url)
    soup = BeautifulSoup(html_doc, 'html.parser')
    return soup.find_all('a')

def stop_url(links, stop):
    # identifies GID and creates URL for given stop
    for link in links:
        if stop in link.getText() and 'Göteborg' in link.getText():
            if 'hallplatser' in link.get('href').split('/'):
                GID = link.get('href').split('/')[3]
                return f'https://avgangstavla.vasttrafik.se/?source=vasttrafikse-stopareadetailspage&stopAreaGid={GID}'


# You don't probably need to change this
def network_graphviz(network, outfile, colors=None, positions=scaled_position):
    dot = graphviz.Graph(engine='fdp', graph_attr={'size': '13,13'})
    
    for stop in network.all_stops():
        
        y, x = network.stop_position(stop)
        x, y = float(x), float(y)
        if positions:
            x, y = positions(network)((x, y))
        pos_x, pos_y = str(x), str(y)
        
        if colors and stop in colors:
            col = colors[stop] # set this to white to create gbg_tramnet.svg
        else:
            col = 'white'
        
        dot.node(stop, label=stop, shape='rectangle', pos=pos_x + ',' + pos_y,
            fontsize='8pt', width='0.4', height='0.05',
            URL=stop_url(links, stop),
            fillcolor=col, style='filled')
        
    for line in network.all_lines():
        stops = network.line_stops(line)
        for i in range(len(stops)-1):
            dot.edge(stops[i], stops[i+1],
                         color=gbg_linecolors[int(line)], penwidth=str(2))

    dot.format = 'svg'
    s = dot.pipe().decode('utf-8')
    with open(outfile, 'w', encoding='utf-8') as file:
        file.write(s)


def show_shortest(dep, dest):
    # TODO: uncomment this when it works with your own code
    network = readTramNetwork()

    # TODO: replace this mock-up with actual computation using dijkstra
    spec_network = specialize_stops_to_lines(network)
    time = specialized_transition_time(spec_network, dep, dest)
    geo = specialized_geo_distance(spec_network, dep, dest)
    timestops = list(set([s[0] for s in time[0]]))
    geostops = list(set([s[0] for s in geo[0]]))
    timepath = time[1]
    geopath = geo[1]
    #print(timepath)
    #print('')
    #print(geopath)
    
    colors = {}
    for stop in (timestops+geostops):
        if stop in timestops and not stop in geostops:
            colors[stop] = 'orange'
        if stop in geostops and not stop in timestops:
            colors[stop] = 'green'
        if stop in timestops and stop in geostops:
            colors[stop] = 'cyan'

    # TODO: run this with the shortest-path colors to update the svg image
    network_graphviz(network, SHORTEST_PATH_SVG, colors=colors)
    
    return timepath, geopath

#gather links at the start so it does not have to be repeated for every search#
links = find_all_links()

#show_shortest('Opaltorget', 'Komettorget')
