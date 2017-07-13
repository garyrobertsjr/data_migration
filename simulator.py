''' Simulator.py '''
from scheduler import InOrder
from disk import Disk
from graph_tool.all import *
from numpy.random import randint
import argparse

def main():
    ''' Parse CLI args and invoke simulator '''
    parser = argparse.ArgumentParser()
    graph_g = parser.add_mutually_exclusive_group()
    graph_g.add_argument('--random', help='Random graph generation', type=int)
    graph_g.add_argument('--static', metavar='S', help='Use static graph', choices=['331', '391'])
    args = parser.parse_args()

    sched = InOrder()
    disks = []
    edges = []
    g = Graph(directed=False)

    if(args.random):
        ''' Random graph generation '''
        g.add_vertex(args.random)
        for s,t in zip(randint(0,args.random,args.random), \
		randint(0,args.random,args.random)):
            g.add_edge(g.vertex(s),g.vertex(t))

        ''' Populate disk list '''
        for i in range(args.random):
            disks.append(Disk(2,2))

    elif(args.static):
        disks = [Disk(1,0), Disk(1,0), Disk(1,0)]

        if args.static == '331':
            v1 = g.add_vertex()
            v2 = g.add_vertex()
            v3 = g.add_vertex()
    
            g.add_edge(v1, v2)
            g.add_edge(v1, v3)
            g.add_edge(v2, v3)

        elif args.static == '391':
            v1 = g.add_vertex()
            v2 = g.add_vertex()
            v3 = g.add_vertex() 
            g.add_edge(v1, v2)
            g.add_edge(v1, v2)
            g.add_edge(v1, v2)
            g.add_edge(v1, v3)
            g.add_edge(v1, v3)
            g.add_edge(v1, v3)
            g.add_edge(v2, v3)
            g.add_edge(v2, v3)
            g.add_edge(v2, v3)
           

    graph_draw(g, vertex_text=g.vertex_index, vertex_font_size=18,
               output_size=(1000,1000), output="test.png")


    ''' Convert Graph edges to list format '''
    for e in g.edges():
        edges.append((int(e.source()), int(e.target())))
 
    rounds = 0
    while edges != []:
        print("ROUND " + str(rounds + 1))
        sched.do_work(disks, edges)
        print(edges)

        rounds += 1

if __name__ == "__main__":
    main()
