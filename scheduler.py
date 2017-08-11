''' Scheduler.py '''
from abc import ABC, abstractmethod
from math import ceil
from disk import Disk
import networkx as nx

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

    def split_cv(self, graph):
        ''' Split nodes into d.cv subnodes with identical edges '''
        for d in graph.nodes():
            if d.cv > 1:
                edges = graph.edges(d)
                print(edges)
                for i in range(1,d.cv):
                    new_d = Disk(1,0)
                    new_edges = [(new_d, e[1]) for e in edges]

                    graph.add_node(new_d)
                    graph.add_edges_from(new_edges)


class InOrder(Scheduler):
    ''' Perform transmission between disk in order present in list '''
    def gen_edges(self, graph):
        return [e for e in graph.edges()]

    def do_work(self, graph, queue):
        working = []
        for e in queue:
            if e[0].avail > 0 and e[1].avail > 0:

                # Aqcuire cv resources
                e[0].acquire()
                e[1].acquire()

                # Remove work
                graph.remove_edge(e[0],e[1])

                # Assign disk to active pool
                working.append(e[0])
                working.append(e[1])

                print("Disk" + str(e[0]) + " transferring to Disk" + str(e[1]))

        # Free resources
        for w in working:
            w.free()

class Greedy(InOrder):
    ''' Performs transmission between disks using greedy alg to generate list of edges for InOrder '''
    def gen_edges(self, graph):
        degrees = self.dv_cv(graph) 
        
        # Compute dvcv weight of each edge
        weighted = [(degrees[edge[0]] + degrees[edge[1]], edge) for edge in graph.edges()]

        # Return list of edges of descending accumlative dvcv score
        return [edge for weight, edge in sorted(weighted, key=lambda value: value[0])]

    def dv_cv(self, graph):
        ''' Return degree/cv of disks for current round '''
        degrees = graph.degree()

        return {d:ceil(degrees[d]/d.cv) for d in degrees}

class Color(InOrder):
    ''' Temp scheduler to test coloring '''
    def gen_edges(self, graph):
        self.split_cv(graph)
        d = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_largest_first)
        
        # Use node coloring alg to deduce edge color or import external vizings?

        print(d)
        graph.clear()

    def do_work(self, graph, queue):
        pass