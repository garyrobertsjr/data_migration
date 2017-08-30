''' Scheduler.py '''
from abc import ABC, abstractmethod
from math import ceil
from disk import Disk, Alias
import networkx as nx
import matplotlib.pyplot as plt

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
    def gen_edges(self, graph):
        return [e for e in graph.edges()]

    def do_work(self, graph, queue):
        working = []
        for e in queue:
            if e[0].avail > 0 and e[1].avail > 0 and graph.has_edge(e[0], e[1]):

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
        return [edge for _, edge in sorted(weighted, key=lambda value: value[0])]

    def dv_cv(self, graph):
        ''' Return degree/cv of disks for current round '''
        degrees = graph.degree()

        return {d:ceil(degrees[d]/d.cv) for d in degrees}

class SplitCV(InOrder):
    ''' Temp scheduler to test coloring '''
    def __init__(self):
        self.a_graph = None
        self.l_graph = None
        self.d = None

    def gen_edges(self, graph):
        if not self.a_graph:
            # Generate alias graph
            a_graph = self.split(graph)

            # Generate Line Graph
            self.l_graph = nx.line_graph(a_graph)

            # Find edge coloring of line graph (nonoptimal, greedy)
            self.d = nx.coloring.greedy_color(self.l_graph, strategy=nx.coloring.strategy_largest_first)

        # Return edges for round
        return [(e[0].org, e[1].org) for e in self.d.keys()]

    def alias_graph(self, graph):
        a = nx.MultiGraph()

        for d in graph.nodes():
            # Create alias disk
            disk_alias = Alias(d)

            # Copy edges from original
            edges = graph.edges(d)
            alias_edges =[(disk_alias, Alias(e[1])) for e in edges]
            
            # Add to alias graph
            a.add_node(disk_alias)
            a.add_edges_from(alias_edges)

        return a

    def split(self, graph):
        ''' Split nodes into d.cv alias nodes with identical edges '''
        self.a_graph = self.alias_graph(graph)

        for d in self.a_graph.nodes():
            if d.org.cv > 1:
                edges = self.a_graph.edges(d)
                
                # Create d.cv number of clones with  a cv of 1
                for i in range(1,d.org.cv-1):
                    new_d = Alias(d.org)
                    new_edges = [(new_d, e[1]) for e in edges]

                    # Append cv clones
                    self.a_graph.add_node(new_d)
                    self.a_graph.add_edges_from(new_edges)

        
        return self.a_graph


class Bipartite(Scheduler):
    ''' Chadi algorithm scheduler '''
    def do_work(self, graph, queue):
        graph.clear()

    def gen_edges(self, graph):
        ''' Build bipartite graph '''
        # normalize
        self.normalize(graph)

        # euler cycle
        ec = nx.eulerian_circuit(graph)
        print('EC: ' + str(ec))

        # bipartite graph set 1 = in; set 2 = out
        b = nx.Graph()


        # TODO: Remap edges to disk alias for second nodes for bipartite functionality
        
        # v_in nodes
        b.add_nodes_from(graph.nodes(), bipartite=0)

        # v_out nodes 
        b.add_nodes_from(graph.nodes(), bipartite=1)

        # Edges
        for e in graph.edges():
            b.add_edge(e[0], e[1])

        # OUTPUT FOR TESTING
        plt.clf()
        nx.draw_networkx(b)
        plt.savefig("bipartite.png")

    def max_d(self, graph):
        ''' Return max cv d prime '''
        degree = graph.degree()
        degrees = [(d,ceil(degree[d]/d.cv)) for d in degree]
        
        return max(degrees, key=lambda item:item[1])[1]

    def normalize(self, graph):
        ''' Add self loops to normalize cv d prime '''
        cvd = self.max_d(graph)
        print('CVD: ' + str(cvd))

        for d in graph.nodes():
            while graph.degree(d) < cvd:
                graph.add_edge(d, d)