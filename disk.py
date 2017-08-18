''' Disk.py '''

class Disk():
    ''' Generic disk object '''
    def __init__(self, cv, capacity):
        self.cv = cv
        self.capacity = capacity
        self.avail = cv

    def acquire(self):
        ''' Semaphore for CV: Consume resource '''
        if self.avail > 0:
            self.avail -= 1
            return True
        return False

    def free(self):
        ''' Semaphore for CV: Free resource '''
        self.avail += 1

    def __le__(self, true):
        ''' LE overridden for sorting (nx line_graph compat) '''
        return True
