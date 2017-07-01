''' Scheduler.py '''
from abc import ABC, abstractmethod

class Scheduler(ABC):
    ''' Abstract class for implementing scheduling algorithms '''

    @abstractmethod
    def do_work(self, nodes, edges):
        ''' Run one round of the algorithm '''
        pass

class InOrder(Scheduler):
    ''' Perform transmission between disk randomly '''
    def do_work(self, nodes, edges):
        working = []
        for i, e in enumerate(edges):
            if nodes[e[0]].avail > 0 and nodes[e[1]].avail > 0:

                # Aqcuire cv resources
                nodes[e[0]].acquire()
                nodes[e[1]].acquire()

                # Remove work
                edges.pop(i)

                # Assign disk to active pool
                working.append(e[0])
                working.append(e[1])

                print("Disk" + str(e[0]) + " transferring to Disk" + str(e[1]))

        # Free resources
        for w in working:
            nodes[w].free()

