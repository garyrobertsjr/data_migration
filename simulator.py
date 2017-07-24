#!/bin/env python
''' Simulator.py '''
from scheduler import InOrder, Greedy
from disk import Disk
from graph_tool.all import *
from numpy.random import randint
import random
import argparse

def main():
    ''' Parse CLI args and invoke simulator '''
    parser = argparse.ArgumentParser()
    parser.add_argument('scheduler', help='Specifiy scheduler algorithm', choices=['inorder', 'random', 'greedy'])
    cv_g = parser.add_mutually_exclusive_group()
    cv_g.add_argument('--static_cv', help='Specifiy cv', type=int)
    cv_g.add_argument('--rand_cv', help='Specifiy max value for random cv', type=int)
    graph_g = parser.add_mutually_exclusive_group()
    graph_g.add_argument('--random', help='Random graph generation', type=int)
    graph_g.add_argument('--static', metavar='S', help='Use static graph', choices=['331', '391'])
    args = parser.parse_args()

    if args.scheduler == 'inorder':
        sched = InOrder()
    elif args.scheduler == 'random':
        print("Not yet implemented.")
        return
    elif args.scheduler == 'greedy':
        sched = Greedy()

    disks = []
    edges = []
    g = Graph(directed=False)

    if(args.random):
        ''' Random graph generation '''
        g.add_vertex(args.random)
        for s,t in zip(randint(0,args.random,args.random*5), \
		randint(0,args.random,args.random*5)):
            g.add_edge(g.vertex(s),g.vertex(t))

        ''' Populate disk list '''
        for i in range(args.random):
            if args.rand_cv:
                disks.append(Disk(random.randint(1,args.rand_cv),0))
            elif args.static_cv:
                disks.append(Disk(args.static_cv,0))
            else:
                disks.append(Disk(1,0))

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
 
    ''' Greedy: arrange edges according to dv_cv(refactor to func in sched)'''
    if args.scheduler == 'greedy':
        degrees = sched.dv_cv(disks, g)
        edges = [edge for dvcv, edge in sorted(zip(degrees, edges))]

    rounds = 0
    while edges != []:
        print("ROUND " + str(rounds + 1))
        sched.do_work(disks, edges)
        rounds += 1

if __name__ == "__main__":
    main()
