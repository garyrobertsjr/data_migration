''' Simulator.py '''
from scheduler import InOrder
from disk import Disk
from graph_tool.all import *
import argparse

def main():
    ''' Parse CLI args and invoke simulator '''
    parser = argparse.ArgumentParser()
    graph_g = parser.add_mutually_exclusive_group()
    graph_g.add_argument('--random', help='Random graph generation', action='store_true')
    graph_g.add_argument('--static', metavar='S', help='Use static graph', choices=['331', 391])
    args = parser.parse_args()

    s = InOrder()

    ''' Static graph for testing [3 Disks, 3 Edges, CV 1] '''
    #disks = [Disk(1, 0), Disk(1, 0), Disk(1, 0)]
    #edges = [(0, 1), (0, 2), (1, 2)]

    ''' Static graph for testing [3 Disks, 9 Edges, CV 1] '''
    disks = [Disk(3, 0), Disk(1, 0), Disk(1, 0)]
    edges = [(0, 1), (0, 2), (1, 2), (0, 1), (0, 2), (1, 2), (0, 1), (0, 2), (1, 2)]

    rounds = 0
    while edges != []:
        print("ROUND " + str(rounds + 1))
        s.do_work(disks, edges)
        print(edges)

        rounds += 1

if __name__ == "__main__":
    main()
