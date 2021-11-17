import json
import math
import sys

JSON_FILE_INPUT = './tramstops.json'
TXT_FILE_INPUT = './tramlines.txt'
JSON_FILE_OUTPUT = 'tramnetwork.json'


## dictionary building functions ##
def build_tram_stops(tramstops_json):
    tramstops = dict({})
    
    with open(tramstops_json, "r", encoding='utf-8') as tramstops_file:
        tramstops_info = json.loads(tramstops_file.read())
    
    for stop in tramstops_info:
        lat = tramstops_info[stop]['position'][0]
        lon = tramstops_info[stop]['position'][1]    
        tramstops[stop] = dict({'lat': str(lat), 'lon': str(lon)})
        
    return tramstops


def build_tram_lines(tramlines_txt):
    tramlines = dict({})
    times = dict({})
    times_list = []
    
    with open(tramlines_txt, "r", encoding='utf-8') as tramlines_file:
        tramlines_info = tramlines_file.readlines()
    
    tramlines_info = [r.rstrip() for r in tramlines_info]
    
    for row in tramlines_info:
        if row and row[-1] == ':':
            current_line = row[:-1].strip()
            tramlines[current_line] = []
        else:
            stop = row[:-5].strip()
            time = row[-2:]
            if row:
                time = int(time)
                tramlines[current_line].append(stop)
            times_list.append((stop, time))
                
    for i in range(len(times_list)-1):
        current_stop_name, current_stop_time = times_list[i]
        next_stop_name, next_stop_time = times_list[i+1]
        if current_stop_name != '' and next_stop_name != '':
            if current_stop_name in times:
                if next_stop_name in times[current_stop_name]:
                    continue
                if next_stop_name in times and current_stop_name in times[next_stop_name]:
                    continue
                times[current_stop_name].update({next_stop_name:next_stop_time-current_stop_time})
            else:
                if next_stop_name in times and current_stop_name in times[next_stop_name]:
                    continue
                times[current_stop_name] = {next_stop_name:next_stop_time-current_stop_time}
            
    '''
    #test if all stop-combinations are included in dictionary times
    missing = []
    tl2 = [(times_list[i][0], times_list[i+1][0]) for i in range(len(times_list)-1) if times_list[i][0] and times_list[i+1][0]]
    for first, second in tl2:
        if first in times and second in times[first]:
            continue
        if second in times and first in times[second]:
            continue
        else:
            missing.append((first, second))
            print(f'The following stop-combination is missing: {first} and {second}')
    print(f'{len(missing)} stop-combinations are missing')
    
    #test for redundancy in dictionary times
    count = 0 
    for s in times:
        pairs = times[s]
        for pair in pairs:
            if pair in times:
                if s in times[pair]:
                    count+=1
                    print(s, pair, 'redundant!')
    print(f'{count} redundant stop-combinations')
    '''
    return tramlines, times


def build_tram_network(files):
    tramstops = build_tram_stops(files[0])
    tramlines, times = build_tram_lines(files[1])
    master_dict = {"stops":tramstops, "lines":tramlines, "times":times}
    with open(JSON_FILE_OUTPUT, 'w') as file:
        json.dump(master_dict, file, indent=4)


## query functions ## 
def lines_via_stop(line_dict, stop):
    lines = []
    
    for line in line_dict:
        if stop in line_dict[line]:
            lines.append(line)  
    lines.sort(key=int)
    
    return lines
    '''
    if lines:
        print(lines)
        return
    print('There are no lines going through this stop.')
    '''
    

def lines_between_stops(line_dict, stop1, stop2):
    lines = []
    
    for line in line_dict:
        if stop1 in line_dict[line] and stop2 in line_dict[line]:
            lines.append(line)  
    lines.sort(key=int)
    
    return lines
    
    '''
    if lines:
        print(lines)
        return
    print('There is no line directly connecting these two stops.')
    '''


def time_between_stops(line_dict, times_dict, line, stop1, stop2):
    time = 0
    
    if line in line_dict and stop1 in line_dict[line] and stop2 in line_dict[line]:
        pos1 = line_dict[line].index(stop1)
        pos2 = line_dict[line].index(stop2)
        stops = line_dict[line][min(pos1, pos2):max(pos1, pos2)+1]
        stops_adj = [(stops[i], stops[i+1]) for i in range(len(stops)-1)]
        
        for s1, s2 in stops_adj:
            if s2 in times_dict and s1 in times_dict[s2]:
                time += times_dict[s2][s1]
            elif s1 in times_dict and s2 in times_dict[s1]:
                time += times_dict[s1][s2]
            else:
                print(f'Information for travel time between stops {s1} and {s2} missing.')
    
    return time
    '''
        print(time)
        
    else:
        print('The two stops are not directly connected via the specified line.')
        return 
    '''
    

def distance_between_stops(stops_dict, stop1, stop2):
    distance = 0
    
    if stop1 in stops_dict and stop2 in stops_dict:
        lat1, lon1 = float(stops_dict[stop1]['lat']) * math.pi/180, float(stops_dict[stop1]['lon']) * math.pi/180
        lat2, lon2 = float(stops_dict[stop2]['lat']) * math.pi/180, float(stops_dict[stop2]['lon']) * math.pi/180
        R = 6371.009
        delta_phi = lat1-lat2
        phi_m = (lat1+lat2)/2
        delta_lambda = lon1-lon2
        distance = round(R * math.sqrt(delta_phi**2 + (math.cos(phi_m) * delta_lambda)**2), 3)
    
    return distance
    '''
    else:
        print('At least one of the specified stops could not be found.')
    '''


## dialogue function ##
def answer_query(tramdict, query):
    
    words = query.split(' ')
    
    if query == 'quit':
        return 1
    
    if query.startswith('via'):
        stop = ' '.join(words[1:])
        lines = lines_via_stop(tramdict['lines'], stop)
        if lines:
            return lines
        return 2
    
    if query.startswith('between'):
        if not ' and ' in query:
            return 2 
        pos_of_and = words.index('and') 
        stop1 = ' '.join(words[1:pos_of_and])
        stop2 = ' '.join(words[pos_of_and+1:])
        if stop1 == stop2:
            return 2
        lines = lines_between_stops(tramdict['lines'], stop1, stop2)
        if lines:
            return lines
        return 2
    
    if query.startswith('time'):
        if not ' with ' in query or not ' from ' in query or not ' to ' in query:
            return 2 
        pos_of_with = words.index('with')
        pos_of_from = words.index('from')
        pos_of_to = words.index('to')
        line = ''.join(words[pos_of_with+1:pos_of_from])
        stop1 = ' '.join(words[pos_of_from+1:pos_of_to])
        stop2 = ' '.join(words[pos_of_to+1:])  
        if stop1 == stop2:
            return 2
        time = time_between_stops(tramdict['lines'], tramdict['times'], line, stop1, stop2)
        if time:
            return time
        return 2
    
    if query.startswith('distance'):
        if not ' from ' in query or not ' to ' in query:
            return 2 
        pos_of_from = words.index('from')
        pos_of_to = words.index('to')
        stop1 = ' '.join(words[pos_of_from+1:pos_of_to])
        stop2 = ' '.join(words[pos_of_to+1:])    
        if stop1 == stop2:
            return 2
        distance = distance_between_stops(tramdict['stops'], stop1, stop2)
        if distance:
            return distance
        return 2
    
    else:
        return 0


def dialogue(jsonfile):
    try:
        with open(jsonfile, 'r') as file:
            tramnetwork = json.load(file)
    except FileNotFoundError:
        print('The file tramnetwork.json could not be found.')
        return
    
    while True:
        query = input('>')
        answer = answer_query(tramnetwork, query)
        
        if answer == 1:
            return
        if answer == 2:
            print('unknown arguments')
        elif not answer:
            print('sorry, try again')
        else:
            print(answer)
    

## main function ##
if __name__ == '__main__':
    #print(sys.argv[1])
    if len(sys.argv) == 2 and sys.argv[1] == 'init':
        build_tram_network((JSON_FILE_INPUT, TXT_FILE_INPUT))
    else:
        dialogue(JSON_FILE_OUTPUT)                             



## trying query functions ##
#print(lines_via_stop(build_tram_lines(TXT_FILE_INPUT)[0], 'Chalmers'))
#print(lines_between_stops(build_tram_lines(TXT_FILE_INPUT)[0], 'Chalmers', 'Valand'))
#print(time_between_stops(build_tram_lines(TXT_FILE_INPUT)[0], build_tram_lines(TXT_FILE_INPUT)[1], '6', 'Chalmers', 'Järntorget'))
#print(distance_between_stops(build_tram_stops(JSON_FILE_INPUT), 'Chalmers', 'Järntorget'))
