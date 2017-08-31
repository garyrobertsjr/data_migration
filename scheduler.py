''' Scheduler.py '''
from abc import ABC, abstractmethod
from math import ceil
from disk import Disk, Alias
from networkx.algorithms.flow import edmonds_karp
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

                if e[0] != e[1]:
                    # Aqcuire cv resources
                    e[0].acquire()
                    e[1].acquire()

                    # Remove work
                    graph.remove_edge(e[0],e[1])

                    # Assign disk to active pool
                    working.append(e[0])
                    working.append(e[1])

                    print("Disk" + str(e[0]) + " transferring to Disk" + str(e[1]))
                else:
                    e[0].acquire()
                    graph.remove_edge(e[0],e[1])
                    working.append(e[0])
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

        return {d[0]:ceil(d[1]/d[0].cv) for d in degrees}

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

        new_disks = []
        new_edges = []
        for d in self.a_graph.nodes():
            if d.org.cv > 1:
                edges = self.a_graph.edges(d)
                
                # Create d.cv number of clones with  a cv of 1
                for i in range(1,d.org.cv-1):
                    new_d = Alias(d.org)
                    new_edges = [(new_d, e[1]) for e in edges]

        # Append cv clones
        self.a_graph.add_nodes_from(new_disks)
        self.a_graph.add_edges_from(new_edges)

        
        return self.a_graph


class Bipartite(InOrder):
    ''' Chadi algorithm scheduler '''
    def __init__(self):
        self.normalized = False

    def gen_edges(self, graph):
        ''' Build bipartite graph '''
        
        # normalize
        if not self.normalize:
            self.normalize(graph)
            self.normalized = True

        # euler cycle
        ec = nx.eulerian_circuit(graph)

        # Remove loops on graph
        loops = []
        for e in graph.edges():
            if e[0] == e[1]:
                loops.append(e)

        graph.remove_edges_from(loops)

        # bipartite graph set 1 = in; set 2 = out
        b = nx.Graph()  

        # v-in aliases and edge mapping
        v_out = [e[0] for e in graph.edges()]
        v_in = {e[1]:Alias(e[1]) for e in graph.edges()}

        for e in graph.edges():
            b.add_edge(e[0], v_in[e[1]], capacity=1)

        # Create s-node
        b.add_node('s')
        for d in v_in.items():
            b.add_edge('s', d[1], capacity=ceil(d[1].org.cv/2))

        # Create t-node
        b.add_node('t')
        for d in v_out:
            b.add_edge('t', d, capacity=ceil(d.cv/2))

        flow_value, flow_dict = nx.maximum_flow(b, 's', 't')
        
        flow = [(d[0],d2[0]) for d in flow_dict.items() for d2 in d[1].items() if d2[1] > 0 and d[0] != 's' and d2[0] != 't' and d[0] != 't' and d2[0] != 's']
        b.remove_edges_from(flow)

        # Reassociate aliases

        active = []
        for e in flow:
            if e[0] != 's' and e[1] != 't' and e[0] != 't' and e[1] != 's':
                if e[0].avail == None:
                    active.append((e[0].org, e[1]))
                elif e[1].avail == None:
                    active.append((e[0],e[1].org))
                elif e[0].avail == None and e[1].avail == None:
                    active.append((e[0].org,e[1].org))
                else:
                    active.append(e)

        return active


    def max_d(self, graph):
        ''' Return max cv d prime '''
        degrees = graph.degree()
        
        return max(degrees, key=lambda item:item[1])[1]

    def normalize(self, graph):
        ''' Add self loops to normalize cv d prime '''
        delta_prime = self.max_d(graph)

        spares = []
        for d in graph.nodes():            
            while graph.degree(d) < (delta_prime*d.cv)-1:
                graph.add_edge(d, d)

            # Identify nodes with odd degree
            if graph.degree(d) == delta_prime*d.cv-1:
                spares.append(d)

        # Pair nodes with delta*cv - 1
        while spares:
            new_edge = spares[:2]
            spares = spares[2:]

            graph.add_edge(new_edge[0], new_edge[1])
