from multiprocessing.pool import ThreadPool, Pool 
from multiprocessing import Process, Manager
import time

''' 
    index:  list of objects
'''

manager = Manager()
index_state = manager.dict()

def global_state(index_state):
    def download_block(func):
        def func_wrapper(index):
            register(index)
            while not all(index_state[key] for key in index):
                print("proc see "+', '.join(k for k in index_state.keys() if index_state[k]))
                print("keys found :"+', '.join(k for k in index if index_state[k]))
                time.sleep(2)
            return func(index)
        return func_wrapper
    return download_block


@global_state(index_state)
def proc(index):
    index_str = ','.join(index)
    print "processor start on index %s" % index_str
    return("processed_"+index_str)


def index_coordinator():    
    for i in range(10):
        obj = str(i)
        index_state[obj] = True
        print "Object %s released from index" % str(obj)
        time.sleep(1)   


def register(index):
    valid_index = [key for key in index if key not in index_state.keys()]
    for v in valid_index:
        index_state[v] = False
    print "Objects: %s registered to the index" % ','.join(index)   


if __name__ == '__main__':
    p1 = Process(target=proc, args=(["5", "6", "7"], ))
    p2 = Process(target=index_coordinator)
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    p2.join()
