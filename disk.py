''' Disk.py '''

class Disk():
    ''' Generic disk object '''
    def __init__(self, cv, capacity):
        self.cv = cv
        self.capacity = capacity
        self.avail = cv
        self.org = self
        self.bypass = False

    def acquire(self):
        ''' Semaphore for CV: Consume resource '''
        if self.avail:
            self.avail -= 1
            return True
        return False

    def free(self):
        ''' Semaphore for CV: Free resource '''
        self.avail += 1

    def __le__(self, item):
        ''' LE overridden for sorting (nx line_graph compat) '''
        return True

class Alias():
    ''' Disk alias object '''
    def __init__(self, org):
        self.org = org
    def __le__(self, item):
        ''' LE overridden for sorting (nx line_graph compat) '''
        return True

class Bypass():
    ''' Bypass disk object '''
    def __init__(self, cv, capacity):
        self.cv = cv
        self.capacity = capacity
        self.avail = cv
        self.bypass = True

    def acquire(self):
        ''' Semaphore for CV: Consume resource '''
        if self.avail:
            self.avail -= 1
            return True
        return False

    def free(self):
        ''' Semaphore for CV: Free resource '''
        self.avail += 1
    def __le__(self, item):
        ''' LE overridden for sorting (nx line_graph compat) '''
        return True