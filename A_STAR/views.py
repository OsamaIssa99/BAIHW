import sys
from django.shortcuts import render
from collections import defaultdict
import math
import csv

#define list of nodes and edges and the graph
nodes = []
edges = []
graph = defaultdict(list)

sys.setrecursionlimit(1500)
def home(request):
    #read data from dataset and select the required data only for countries
    ddl_countries = [""]
    with open('worldcities.csv','rt')as f:
        data = csv.reader(f)
        for row in data:
            ddl_countries.append(row[11])

    #remove the fieldname from country list      
    ddl_countries.remove('countries')

    #add countries to ddl_countries in HTML page
    cont_countries = {'countries': ddl_countries}
    return render(request,'A_STAR/home.html',cont_countries)

def add_cities(request):
    #get the selected country from HTML page
    country = request.GET.get('ddl_country')
    
    #prepare the cities belonging to the country 
    ddl_cities = []
    cities = []
    with open('worldcities.csv','rt')as f:
        data = csv.reader(f)
        for row in data:
            if row[4] == country:
                ddl_cities.append(row[1])
                cities.append((row[1], row[2], row[3], row[4]))

    #fill the nodes with appropriate cities
    for city in cities:
        h = 100000000
        d = 100000000
        nodes.append((city[0], city[1], city[2], h, d))


    #add cities to ddl_cities in HTML page
    cont_cities = {'cities': ddl_cities}

    return render(request,'A_STAR/cities.html',cont_cities)
    

#recursive function to build graph
def build_edges(start, end, nodes, edges):
    #condition to stop
    if start[0] == end[0]: return None

    #if node is already visited
    for edge in edges:
        if start[0] == edge[0]: return None
    
    #temp nodes lists for storing changes
    temp=[]
    temp2 = []
    temp3 = []

    #scoping to a smaller area to reduce excution time
    for node in nodes:
        if node[1] >= min(start[1],end[1]) and node[1] <= max(start[1],end[1]) and node[2] >= min(start[2],end[2]) and node[2] <= max(start[2],end[2]) and node[0] != start[0]:
            temp.append(node)

    #get heuristic depending on [lat,lng] coords
    for c in temp:
        c3 = math.sqrt(math.pow(float(c[1]) - float(end[2]), 2) + math.pow(float(c[2]) - float(end[2]), 2))
        temp2.append((c[0], c[1], c[2], c3, c[4]))

    #get nodes distance from parent
    for c in temp2:
        c4 = math.sqrt(math.pow(float(c[2]) - float(start[2]), 2) + math.pow(float(c[2]) - float(start[2]), 2))
        temp3.append((c[0], c[1], c[2], c[3], c4))
    def sortkey(e):
        return e[4]
    temp3.sort(key = sortkey)

    #create edges and add them
    i = 0
    for c in temp3:
        if i == 5: break
        i += 1
        edges.append((start,c,c[4]))
        
    
    #recursive
    i = 0
    for c in temp3:
        if i == 5: break
        i += 1
        return build_edges(c, end, nodes, edges)
        

def get_neighbors(v):
    if v in graph:
        return graph[v]
    else:
        return None

#gets the city node from city_name
def get_node(q):
    for node in nodes:
            if node[0] == q:
                return node
    return None

def result(request):
    
    #get start/end coords
    city1_name = request.GET.get('ddl_city1')
    city2_name = request.GET.get('ddl_city2')
    startpoint = []
    endpoint = []
    for node in nodes:
        if node[0] == city1_name:
            startpoint = node
        elif node[0] == city2_name:
            endpoint = node
    

    #build the edges between nodes
    build_edges(startpoint, endpoint, nodes, edges)

    #build the graph in the desired area
    
    for edge in edges:
        graph[(edge[0][0])].append((edge[1][0],edge[2]))
        graph[(edge[1][0])].append((edge[0][0],edge[2]))
    
    
    #Apply A-Star algorithm on the graph
    path = [""]
    open_list = []
    open_list.append(startpoint[0])
    closed_list = set()
    g = {}
    parents = {}
    g[startpoint[0]] = 0
    parents[startpoint[0]] = startpoint[0]
    while len(open_list) > 0:
        n = None
        n1 = get_node(n)
        # find the node with lowest f
        for v in open_list:
            v1 = get_node(v)
            #n1 = get_node(n)
            if n == None or g[v] + v1[3] < g[n] + n1[3]:
                n = v
                n1 = get_node(n)
        if n1[0] == endpoint[0] or graph[n1[0]] == None: 
            pass
        else:
            for (m, weight) in get_neighbors(n1[0]):
                if m not in open_list and m not in closed_list:
                    open_list.append(m)
                    parents[m] = n1[0]
                    g[m] = g[n1[0]] + weight

                else:
                    if g[m] > g[n1[0]] + weight:
                        g[m] = g[n1[0]] + weight
                        parents[m] = n1[0]
                        if m in closed_list:
                            closed_list.remove(m)
                            open_list.append(m)
        if n == None: path.append('F')
        #when done, reconsrtuct path
        if n == endpoint[0]:
            while parents[n] != n:
                path.append(n)
                n = parents[n]

            path.append(startpoint[0])
            path.reverse()
            break
        open_list.remove(n)
        closed_list.add(n)

    #send path to be sent to HTML page
    contresult = {'l_path': path}
    return render(request,'A_STAR/result.html',contresult)
