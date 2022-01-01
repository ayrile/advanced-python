import json
import sys
import xml.etree.ElementTree as et
import coloring
sys.path.append('../lab2/')
import graphs as gr

COUNTRY_CODES_FILE = './files/country_codes.json'
NEIGHBOR_FILE = './files/neighbors.json'
WHITEMAP_FILE = './files/whitemap.svg'
COLORMAP_FILE = './files/colormap.svg'


def get_neighbors(codefile=COUNTRY_CODES_FILE, neighborfile=NEIGHBOR_FILE):
    "returning dictionaries of country codes and country-neighbour lists"
    code_dict = dict()
    
    with open(codefile, "r", encoding='utf-8') as cfile:
        country_codes = json.loads(cfile.read())
    with open(neighborfile, "r", encoding='utf-8') as nfile:
        neighbor_dict = json.loads(nfile.read())
    
    for code in country_codes:
        code_dict[code['Code']] = code['Name']
        
    return code_dict, neighbor_dict
        

def get_map_colors(neighbordict):
    """returning a dictionary of colours for the countries in neighbordict, 
    using your algorithm from Part 1 of this lab with four colours"""
    G = gr.Graph()
    
    for country in neighbordict:
        country1 = country['countryLabel']
        country2 = country['neighborLabel']
        G.add_edge(country1, country2)
     
    G_copy = gr.Graph(G.edges())
    
    stack = coloring.simplify(G)  
    
    return coloring.rebuild(G_copy, stack, ['red', 'green', 'blue', 'yellow'])
    

def color_svg_map(colordict, infile=WHITEMAP_FILE, outfile=COLORMAP_FILE):
    "putting everything together and writing a coloured version of the white map"
    
    tree = et.parse(infile)
    root = tree.getroot()
    
    for elem in root.iter('{http://www.w3.org/2000/svg}path'):
        if elem.attrib['id'] in colordict:
            elem.attrib['style'] = f"fill:{colordict[elem.attrib['id']]};stroke:#000000;stroke-width:7.63942308000000030;fill-opacity:1;stroke-opacity:1;stroke-miterlimit:4;stroke-dasharray:none;stroke-linejoin:round;stroke-linecap:round;marker-start:none"

    tree.write(outfile)
    

def main():
    codes, neighbors = get_neighbors()
    country_colors = get_map_colors(neighbors)
    colorcodes = dict()

    for code in codes:
        if codes[code] in country_colors:
            colorcodes[code.lower()] = country_colors[codes[code]]

    color_svg_map(colorcodes)   
    
    
if __name__ == '__main__':
    main()
