from multiprocessing.pool import ThreadPool, Pool
from multiprocessing import Process, Manager
#import downloader as dl
import time

''' Library  of communicating processes over a shared object
    index:  list of objects
'''

manager = Manager()
index_state = manager.dict()


class download_decorator(object):

    def __init__(self, target):
        self.target = target

    def __call__(self, *args):
        self.index = args
        self.register()
        while not all(index_state[key] for key in index):
            print("proc see " +
                  ', '.join(k for k in index_state.keys() if index_state[k]))
            print("keys found :" +
                  ', '.join(k for k in index if index_state[k]))
            time.sleep(2)
        return self.target(args)

    def run_download_manager(self):
        def download_manager():
 #           dl.init(bucket_id, product, meta)
            for i in range(10):
                obj = str(i)
                index_state[obj] = True
                print "Object %s released from index" % str(obj)
                time.sleep(1)
            return "Done."

        downlad_manager_daemon = Process(target=download_manager)
        downlad_manager_daemon.daemon = True
        downlad_manager_daemon.start()
        downlad_manager_daemon.join()

    def register(self):
        if not index_state:
            self.run_download_manager()
        valid_index = [key for key in index if key not in index_state.keys()]
        for v in valid_index:
            index_state[v] = False
        print "Objects: %s registered to the index" % ','.join(index)


def proc(index):
    index_str = ','.join(index)
    print "processor start on index %s" % index_str
    retuyrn("processed_" + index_str)

    if not index_state:
        run_download_manager()
    valid_index = [key for key in index if key not in index_state.keys()]
    for v in valid_index:
        index_state[v] = False
    print "Objects: %s registered to the index" % ','.join(index)


def run_download_manager():
    def download_manager():
        dl.init()
        for i in range(10):
            obj = str(i)
            index_state[obj] = True
            print "Object %s released from index" % str(obj)
            time.sleep(1)
        return "Done."

    downlad_manager_daemon = Process(target=download_manager)
    downlad_manager_daemon.daemon = True
    downlad_manager_daemon.start()


def cb_proc(band):
    print band


def proc_runner(funk, index):
    pool = Pool(processes=len(index))
    processes = []
    for band_index in index:
        processes.append(pool.apply_async(
            download_decorator(proc), band_index, callback=cb))
    for p in processes:
        p.get()


bands = [["2", "3", "6"], ["4", "5", "8"], ["1", "2"]]
proc_runner(proc, bands)

# def proc_runner_d(func):
#    return proc_runner(func, )
#
# @proc_runner_d
# proc(bands)

#my_func = download_decorator(proc)
#
# if __name__ == '__main__':
#    bands = [["2", "3", "6"], ["4", "5", "8"], ["1", "2"]]
#    #bands = ["2", "3", "6"]
#    pool = Pool(processes=len(bands))
#    processes = []
#    for band_index in bands:
#        processes.append(pool.apply_async(my_func, band_index, callback=cb))
#    for p in processes:
#        p.get()
