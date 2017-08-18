#!/bin/env python
''' Simulator.py '''
from scheduler import InOrder, Greedy, Split_CV
from disk import Disk
import networkx as nx
import matplotlib.pyplot as plt
from numpy.random import randint
import random
import argparse

def main():
    ''' Parse CLI args and invoke simulator '''
    parser = argparse.ArgumentParser()
    parser.add_argument('scheduler', help='Specifiy scheduler algorithm', choices=['inorder', 'random', 'greedy', 'split'])
    cv_g = parser.add_mutually_exclusive_group()
    cv_g.add_argument('--static_cv', help='Specifiy cv', type=int)
    cv_g.add_argument('--rand_cv', help='Specifiy max value for random cv', type=int)
    graph_g = parser.add_mutually_exclusive_group()
    graph_g.add_argument('--random', help='Random graph generation', type=int)
    graph_g.add_argument('--file', metavar='F', help='Import graph from pickle', type=argparse.FileType('rb'))
    args = parser.parse_args()

    if args.scheduler == 'inorder':
        sched = InOrder()
    elif args.scheduler == 'random':
        print("Not yet implemented.")
        return
    elif args.scheduler == 'greedy':
        sched = Greedy()
    elif args.scheduler == 'split':
        sched = Split_CV()

    disks = []

    g = nx.MultiGraph()

    if(args.random):
        ''' Populate disk list '''
        for i in range(args.random):
            if args.rand_cv:
                disks.append(Disk(random.randint(1,args.rand_cv),0))
            elif args.static_cv:
                disks.append(Disk(args.static_cv,0))
            else:
                disks.append(Disk(1,0))

        g.add_nodes_from(disks)

        ''' Random graph generation '''
        for s,t in zip(randint(0,args.random,args.random*5), \
		                randint(0,args.random,args.random)):
            g.add_edge(disks[s],disks[t])

        # Write graph pickle to file. 
        # TODO: Naming schema
        nx.write_gpickle(g, "output.gpickle")

    elif(args.file):
        # Import graph pickle
        g = nx.read_gpickle(args.file)
    
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
