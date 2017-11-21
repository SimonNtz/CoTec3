from multiprocessing import Manager


class Shared:

    def __init__(self):
        self.dict = Manager().dict()
        self.dict['Init'] = True
        self.dict['meta'] = False

    def write(self, index, msg):
        self.dict[index] = msg


shared = Shared()
