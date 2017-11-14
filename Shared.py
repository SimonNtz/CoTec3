from multiprocessing import Manager

class Shared:

    def __init__(self):
        print("Init shared dict")
        self.data_dict = Manager().dict()
	self.data_dict['Init'] = False

    def write(self, msg):
        self.data_dict[msg] = True
        print("write %s on data")
        print self.data_dict.keys()

shared = Shared()
