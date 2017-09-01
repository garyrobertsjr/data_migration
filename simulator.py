#!/bin/env python
''' Simulator.py '''
from scheduler import InOrder, Greedy, SplitCV, Bipartite
from disk import Disk
from numpy.random import randint
from math import floor
import networkx as nx
import matplotlib.pyplot as plt
import datetime, random, argparse, os


def generate_disks(n, rand_cv, static_cv, even_cv):
    ''' Populate disk list '''
    disks = []
    for i in range(n):
        if rand_cv:
            # Generate random cv and ensure it is even
            disks.append(Disk(random.randint(1,rand_cv),0))
        elif static_cv:
            disks.append(Disk(static_cv,0))
        elif even_cv:
            disks.append(Disk(random.randint(1,floor(even_cv/2))*2,0))
        else:
            disks.append(Disk(1,0))

    return disks

def main():
    ''' Parse CLI args and invoke simulator '''
    parser = argparse.ArgumentParser()
    parser.add_argument('scheduler', help='Specifiy scheduler algorithm', choices=['inorder', 'random', 'greedy', 'split', 'bipartite'])
    cv_g = parser.add_mutually_exclusive_group()
    cv_g.add_argument('--static_cv', help='Specifiy cv', type=int)
    cv_g.add_argument('--rand_cv', help='Specify max value for a random cv', type=int)
    cv_g.add_argument('--even_cv', help='Specify max value for a random but even cv', type=int)
    graph_g = parser.add_mutually_exclusive_group()
    graph_g.add_argument('--random', help='Random graph generation', type=int)
    graph_g.add_argument('--regular', help='Regular graph generation', type=int)
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
        sched = SplitCV()
    elif args.scheduler == 'bipartite':
        sched = Bipartite()

    disks = []
    timestamp = datetime.datetime.now().isoformat()
    os.makedirs(timestamp)
    g = nx.MultiGraph()

    if args.random:
        ''' Populate disk list '''
        disks = generate_disks(args.random, args.rand_cv, args.static_cv, args.even_cv)

        g.add_nodes_from(disks)

        ''' Random graph generation '''
        # TODO: Change to nx call w/ remap?
        t = nx.dense_gnm_random_graph(args.random,random.randint(args.random,args.random**2))

        # Remap nodes to disks
        disk_map = {i:d for i,d in enumerate(disks)}
        t = nx.relabel_nodes(t, disk_map)

        g = nx.MultiGraph(t)
        t.clear()

        # Write graph pickle to file. 
        # TODO: Naming schema
        nx.write_gpickle(g, timestamp+"/network.gpickle")

        nx.write_gpickle(g, "network.gpickle")


    elif args.regular:
        ''' Populate disk list '''
        disks = generate_disks(args.regular, args.rand_cv, args.static_cv, args.even_cv)

        # Generate random graph skeleton
        r = nx.random_regular_graph(args.regular-1, args.regular)

        # Remap nodes to disks
        disk_map = {i:d for i,d in enumerate(disks)}
        r = nx.relabel_nodes(r, disk_map)

        g = nx.MultiGraph(r)
        r.clear()
        
        # Write graph pickle to file. 
        # TODO: Naming schema
        nx.write_gpickle(g, timestamp+"/network.gpickle")

        nx.write_gpickle(g, "network.gpickle")
    
    elif args.file:
        # Import graph pickle
        g = nx.read_gpickle(args.file)
    
    rounds = 1
    while g.edges():
        print("ROUND " + str(rounds))
        
        plt.clf()
        nx.draw_networkx(g)
        plt.savefig(timestamp+"/round" + str(rounds) + ".png")

        q = sched.gen_edges(g)
        sched.do_work(g, q)
        rounds += 1

    print(rounds-1)
    
if __name__ == "__main__":
    main()
