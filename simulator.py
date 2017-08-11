#!/bin/env python
''' Simulator.py '''
from scheduler import InOrder, Greedy
from disk import Disk
import networkx as nx
import matplotlib.pyplot as plt
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
    graph_g.add_argument('--random_edges', help='Random graph generation', type=int)
    graph_g.add_argument('--demo', metavar='S', help='Use demo graph', choices=['331', '391'])
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

    g = nx.MultiGraph()

    if(args.random_edges):
        ''' Populate disk list '''
        for i in range(args.random_edges):
            if args.rand_cv:
                disks.append(Disk(random.randint(1,args.rand_cv),0))
            elif args.static_cv:
                disks.append(Disk(args.static_cv,0))
            else:
                disks.append(Disk(1,0))

        g.add_nodes_from(disks)

        ''' Random graph generation '''
        for s,t in zip(randint(0,args.random_edges,args.random_edges*5), \
		                randint(0,args.random_edges,args.random_edges*5)):
            g.add_edge(disks[s],disks[t])

    elif(args.static):
        pass


    nx.draw_random(g)
    plt.savefig("graph.png")

    rounds = 0
    while g.edges():
        print("ROUND " + str(rounds + 1))
        q = sched.gen_edges(g)
        sched.do_work(g, q)
        rounds += 1 

if __name__ == "__main__":
    main()
