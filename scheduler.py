''' Scheduler.py '''
from abc import ABC, abstractmethod
from math import ceil

class Scheduler(ABC):
    ''' Abstract class for implementing scheduling algorithms '''

    @abstractmethod
    def do_work(self, nodes, edges):
        ''' Run one round of the algorithm '''
        pass

class InOrder(Scheduler):
    ''' Perform transmission between disk in order present in list '''
    def do_work(self, disks, edges):
        working = []
        for i, e in enumerate(edges):
            if disks[e[0]].avail > 0 and disks[e[1]].avail > 0:

                # Aqcuire cv resources
                disks[e[0]].acquire()
                disks[e[1]].acquire()

                # Remove work
                edges.pop(i)

                # Assign disk to active pool
                working.append(e[0])
                working.append(e[1])

                print("Disk" + str(e[0]) + " transferring to Disk" + str(e[1]))

        # Free resources
        for w in working:
            disks[w].free()

class Greedy(InOrder):
    ''' Performs transmission between disks using greedy alg to generate list of edges for InOrder '''
    def dv_cv(self, disks, graph):
        ''' Return degree/cv of disks for current round '''
        degrees = graph.get_out_degrees(graph.get_vertices())

        for i, d in enumerate(disks):
            degrees[i] = ceil(degrees[i]/d.cv)

        return degrees