from multiprocessing.pool import ThreadPool, Pool
from multiprocessing import Process, Manager
import multiprocessing
import product_downloader as prdl
import time, os
import Shared
''' Library  of communicating processes over a shared object
    index:  list of objects
'''
	
manager = Manager()
index_state = manager.dict()

class NoDaemonProcess(multiprocessing.Process):
    # make 'daemon' attribute always return False
    def _get_daemon(self):
        return False
    def _set_daemon(self, value):
        pass
    daemon = property(_get_daemon, _set_daemon)

# We sub-class multiprocessing.pool.Pool instead of multiprocessing.Pool
# because the latter is only a wrapper function, not a proper class.
class MyPool(multiprocessing.pool.Pool):
    Process = NoDaemonProcess

class download_decorator(object):

    def __init__(self, target):
        self.target = target

    def __call__(self, *args):
        self.index = args
        self.register()
        while not all(Shared.shared.data_dict[k] for k in self.index):
            print("keys found :" +
                  ', '.join(k for k in self.index if Shared.shared.data_dict[k]))
            time.sleep(2)
        return self.target(args)

    def run_download_manager(self):

        def update_shared_object(band):
	    print "state at current time is: "+str(Shared.shared.data_dict.keys())
	    Shared.shared.data_dict.keys[band] = True

        def download_manager():
            bands_dict = prdl.init(bucket_id, product, meta)
	    print "Bands found in %s: %s" % (bucket_id, str(bands_dict.keys()))
	    object_list = [k for k in Shared.shared.data_dict.keys() if k in bands_dict.keys()]
	    print("Bands selected: "+ str(object_list))
	    prdl.get_product_data(bands_dict, bucket_id, object_list)
	    

        downlad_manager_daemon = Process(target=download_manager)
        downlad_manager_daemon.daemon = True
        downlad_manager_daemon.start()
        downlad_manager_daemon.join()

    def register(self):
	time.sleep(0.1)
        if not len(Shared.shared.data_dict.keys()) > 1:
	    print len(Shared.shared.data_dict.keys())
	    Shared.shared.data_dict['init'] = False
            print "Am I a daemon"
            self.run_download_manager()
        valid_index = [key for key in self.index if key not in Shared.shared.data_dict.keys()]
	print("valid index %s" %(valid_index))
        for v in valid_index:
            Shared.shared.data_dict[v] = False
        print "Objects: %s registered to the index" % ','.join(self.index)


def proc(index):
    index_str = ','.join(index)
    print "processor start on index %s" % index_str
    return("processed_" + index_str)

    if not index_state:
        run_download_manager()
    valid_index = [key for key in index if key not in index_state.keys()]
    for v in valid_index:
        index_state[v] = False
    print "Objects: %s registered to the index" % ','.join(index)


def run_download_manager():
    def download_manager():
        for i in range(10):
            obj = str(i)
            index_state[obj] = True
            print "Object %s released from index" % str(obj)
            time.sleep(1)
        return "Done."

    downlad_manager_daemon = Process(target=download_manager)
    #downlad_manager_daemon.daemon = True
    downlad_manager_daemon.start()


def cb(str):
    print "str"


def proc_runner(funk, index):
    pool = MyPool(processes=len(index))
    processes = []
    for band_index in index:
	p = pool.apply_async(
            download_decorator(proc), band_index, callback=cb)
#        print p.daemon
	processes.append(p)
	#processes.append(pool.apply_async(
            #download_decorator(proc), band_index, callback=cb))
    for p in processes:
        p.get()

bucket_id = 'sixsq.eoproc'
product = 'S2A_MSIL1C_20170202T090201_N0204_R007_T35SNA_20170202T090155.SAFE'
meta = 'MTD_MSIL1C.xml'
bands = [["B02", "B03", "B06"], ["B04", "B05", "B08"], ["B01", "B02"]]
proc_runner(proc, bands)

