''' Scheduler.py '''
from abc import ABC, abstractmethod
from collections import Counter
from math import ceil

import matplotlib.pyplot as plt

import networkx as nx
from disk import Alias, Disk, Bypass


class Scheduler(ABC):
    ''' Abstract class for implementing scheduling algorithms '''
    def __init__(self, bypass):
        self.bypass = bypass
        self.num_bypass = 0
        self.cycles = []
        self.inactive_bypass_edges = []
        self.active_bypass_edges = []

    @abstractmethod
    def do_work(self, nodes, edges, verbose):
        ''' Run one round of the algorithm '''
        pass

    @abstractmethod
    def gen_edges(self, disks, graph):
        ''' Create list of edges '''
        pass
        
    def max_d(self, graph):
        ''' Return max cv d prime '''
        degrees = graph.degree()
        degrees = [ceil(d[1]/d[0].cv) for d in degrees]

        return max(degrees)

    def cycle3(self, graph):
        ''' Returns list of disk sets w/ 3-cycles '''
        self.cycles = []

        for d1 in graph.nodes():
            for d2 in graph.neighbors(d1):
                for d3 in graph.neighbors(d2):
                    if graph.has_edge(d1,d3) and d3 is not d1:
                        cycle = {d1, d2, d3}
                        
                        if cycle not in self.cycles:
                            self.cycles.append(cycle)
class InOrder(Scheduler):
    ''' Perform transmission between disk in order present in list '''
    def __init__(self, bypass):
        Scheduler.__init__(self, bypass)
        self.init = False

    def gen_edges(self, graph):
        if not self.init:
            for c in self.cycles:

                cycle_list = list(c)
                bypass_node = Bypass(1,1)

                self.inactive_bypass_edges.append((cycle_list[0], bypass_node))
                self.inactive_bypass_edges.append((cycle_list[1], bypass_node))

            self.init = True
            self.num_bypass = len(self.inactive_bypass_edges)
        return [e for e in graph.edges()]

    def do_work(self, graph, queue, verbose):
        working = []

        # Off-load data on bypass nodes
        for e in self.active_bypass_edges:

            if e[0][0].avail and e[1].avail:
                # Aqcuire cv resources
                e[0][1].acquire()
                e[1].acquire()

                # Remove work
                graph.remove_edge(e[0][0],e[1])

                # Assign disk to active pool
                working.append(e[0][1])
                working.append(e[1])

                if verbose:
                    print("Bypass " + str(e[0]) + " transferring to Disk" + str(e[1]))

            self.active_bypass_edges.clear()
        for e in queue:
            if e[0].avail and e[1].avail and graph.has_edge(e[0], e[1]):
                if e[0] != e[1]:
                    # Aqcuire cv resources
                    e[0].acquire()
                    e[1].acquire()

                    # Remove work
                    graph.remove_edge(e[0],e[1])

                    # Assign disk to active pool
                    working.append(e[0])
                    working.append(e[1])

                else:
                    e[0].acquire()
                    graph.remove_edge(e[0],e[1])
                    working.append(e[0])

                if verbose:
                    print("Disk" + str(e[0]) + " transferring to Disk" + str(e[1]))

        # Load data onto free bypass nodes if edge in cycle
        if self.bypass:
            # Get set of disk-disk edges not active
            for e in self.inactive_bypass_edges:
                for d in [d for d in graph.nodes() if d is not e[0]]:
                    if graph.has_edge(e[0], d) and (d, e[1]) in self.inactive_bypass_edges:
                        if e[0].avail and e[1].avail:
                            # Aqcuire cv resources
                            e[0].acquire()
                            e[1].acquire()

                            # Assign disk to active pool
                            working.append(e[0])
                            working.append(e[1])

                            # Move active bypass edge to active pool
                            self.active_bypass_edges.append((e, d))
                            self.inactive_bypass_edges.remove(e)

                            if verbose:
                                print("Disk" + str(e[0]) + " transferring to Bypass" + str(d))
        # Free resources
        for w in working:
            w.free()

class EdgeRanking(InOrder):
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

class FlattenAndColor(InOrder):
    ''' Temp scheduler to test coloring '''
    def __init__(self):
        self.a_graph = None
        self.e_colors = None

    def gen_edges(self, graph):
        if not self.a_graph:
            # Generate alias graph
            self.a_graph = self.split(graph)
            self.e_colors = [e for e in self.greedy_color(self.a_graph).items()]

        # Return edges for round
        return [(e[0].org, e[1].org) for e, _ in sorted(self.e_colors, key=lambda item: item[1])]

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
        originals = []

        for d in self.a_graph.nodes():
            if d.org.cv > 1:
                edges = self.a_graph.edges(d)
                originals += self.a_graph.edges(d)
                
                # Create d.cv number of clones
                clones = [Alias(d.org) for i in range(1,d.org.cv)]

                # Distribute edges round-robin
                for i, e in enumerate(edges):
                    new_edges.append((clones[i%len(clones)],e[1]))

        # Append cv clones
        self.a_graph.add_nodes_from(new_disks)
        self.a_graph.add_edges_from(new_edges)

        # Remove original edges for disks w/ cv > 1
        self.a_graph.remove_edges_from(originals)
  
        return self.a_graph

    def greedy_color(self, graph):
        e_colors = {}
        d_colors = {}
        for d in graph.nodes():
            adj = []

            color = 0
            for e in graph.edges(d):
                if e not in e_colors:
                    e_colors[e] = color
                    color += 1

        return e_colors

class Bipartite(InOrder):
    ''' Chadi algorithm scheduler '''
    def __init__(self):
        self.normalized = False
        self.b = None

    def gen_edges(self, graph):
        ''' Build bipartite graph '''
        # Normalize
        if not self.normalized:
            # Relax CV
            for d in graph:
                if d.cv%2:
                    d.cv -= 1
                    d.avail -= 1

            #self.mg_split(graph)
            self.normalize(graph)
            self.normalized = True

            # Euler cycle
            ec = nx.eulerian_circuit(graph)

            # Remove self-loops on graph
            loops = []
            for e in graph.edges():
                if e[0].org is e[1].org:
                    loops.append(e)

            graph.remove_edges_from(loops)

            # Bipartite graph for flow problem, NOTE: cannot express MG characteristics
            self.b = nx.DiGraph()

            # v-in aliases and edge mapping
            v_out = [d for d in graph.nodes()]
            v_in = {d:Alias(d) for d in graph.nodes()}

            # Added edges in euler cycle with capacity of 1
            c=0
            for e in ec:
                self.b.add_edge(e[0], v_in[e[1]], capacity=1)

                if e[0].org is not e[1].org:
                    c +=1 

            # Create s-node
            self.b.add_node('t')
            for d in v_in.items():
                self.b.add_edge(d[1], 't', capacity=ceil(d[1].org.cv/2))

            # Create t-node
            self.b.add_node('s')
            for d in v_out:
                self.b.add_edge('s', d, capacity=ceil(d.cv/2))

        # Ford-Fulkerson flow Returns: (flow_val, flow_dict)
        _, flow_dict = nx.maximum_flow(self.b, 's', 't')

        # Extract active edges and cull self loops and s/t nodes
        flow = [(d[0], d2[0]) for d in flow_dict.items() for d2 in d[1].items() \
                if d2[1] > 0 and d[0] not in ['s','t'] and d2[0] not in ['s','t']]
        
        self.b.remove_edges_from(flow)

        # Reassociate aliases and return queue
        return [(e[0].org, e[1].org) for e in flow if e[0].org is not e[1].org]

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

class Greedy(FlattenAndColor):
    ''' Split disk Cv and return maximal matching each round '''
    def __init__(self):
        self.a_graph = None

    def do_work(self, graph, queue, verbose):
        if not queue:
            graph.clear()
        else:
            if verbose:
                for e in queue:
                    print("Disk" + str(e[0]) + " transferring to Disk" + str(e[1]))

    def gen_edges(self, graph):
        # Split Cv and generate alias graph
        if not self.a_graph:
            self.a_graph = self.split(graph)

        # Solve max matching to obtain round
        queue = nx.maximal_matching(self.a_graph)

        # Cull active edges
        self.a_graph.remove_edges_from(queue)

        # Reassociate aliases
        return [(e[0].org, e[1].org) for e in queue]