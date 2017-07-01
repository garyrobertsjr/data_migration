''' Simulator.py '''
from scheduler import InOrder
from disk import Disk
import argparse

def main():
    ''' Parse CLI args and invoke simulator '''
    #parser = argparse.ArgumentParser()
    #args = parser.parse_args()

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
