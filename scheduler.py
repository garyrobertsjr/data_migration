''' Scheduler.py '''
from abc import ABC, abstractmethod
from math import ceil

class Scheduler(ABC):
    ''' Abstract class for implementing scheduling algorithms '''

    @abstractmethod
    def do_work(self, nodes, edges):
        ''' Run one round of the algorithm '''
        pass

    @abstractmethod
    def gen_edges(self, disks, graph):
        ''' Create list of edges '''
        pass

class InOrder(Scheduler):
    ''' Perform transmission between disk in order present in list '''
    def gen_edges(self, disks, graph):
        edges = []

        for e in g.edges():
            edges.append((int(e.source()), int(e.target())))

        return edges

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
    def gen_edges(self, disks, graph):
        degrees = self.dv_cv(disks, graph)
        edges = []

        for e in graph.edges():
            edges.append((int(e.source()), int(e.target())))

        edges = [edge for dvcv, edge in sorted(zip(degrees, edges))]

        return edges

    def dv_cv(self, disks, graph):
        ''' Return degree/cv of disks for current round '''
        degrees = graph.get_out_degrees(graph.get_vertices())

        for i, d in enumerate(disks):
            degrees[i] = ceil(degrees[i]/d.cv)

        return degrees