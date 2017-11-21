from multiprocessing.pool import ThreadPool, Pool
from multiprocessing import Process, Manager
import multiprocessing
import product_downloader as prdl
from pprint import pprint as pp
import time
import os
import Shared
from random import randint
import NoDaemonProcess as ndp

''' Library  of communicating processes over a shared object
    index:  list of objects
'''


class download_decorator(object):

    def __init__(self, target):
        self.target = target

    def __call__(self, *args):
        self.product = args[0]
        self.index, self.params = (args[1].values())
        whoaim("a proc assigned to object %s" % self.index)
        rdm_sleep()
        self.register()
        while not all(Shared.shared.dict[k] for k in self.index):
            print("keys found :" +
                  ', '.join(k for k in self.index if Shared.shared.dict[k]))
            rdm_sleep(1)
        return self.target(self.index)

    def run_download_manager(self):

        def create_process(self):
            whoaim("the download manager process.")
            object_list = [
                k for k in Shared.shared.dict.keys() if k in self.bands_loc.keys()]
            print("Bands selected: " + str(object_list))
            threadpool = ThreadPool(2)
            meta = threadpool.apply_async(prdl.get_product_data,
                                          args=(self.bands_loc,
                                                bucket_id,
                                                object_list))
            bands = threadpool.apply_async(prdl.get_product_metadata,
                                           args=(self.metadata_loc,
                                                 bucket_id))
            meta.get()
            bands.get()
            return meta, bands

        def download_manager():
            bucket_id = 'sixsq.eoproc'
            self.bands_loc, self.metadata_loc = prdl.init(
                bucket_id, self.product)
            proc_meta, proc_bands = create_process(self)
            # proc_meta.start()
            # proc_bands.start()
            # proc_meta.join()
            # proc_bands.join()

        downlad_manager_daemon = Process(target=download_manager)
        downlad_manager_daemon.daemon = False
        downlad_manager_daemon.start()
        downlad_manager_daemon.join()

    def register(self):
        valid_index = [
            key for key in self.index if key not in Shared.shared.dict.keys()]
        for v in valid_index:
            Shared.shared.write(v, False)
        print "Objects: %s registered in shared object" % ','.join(self.index)
        Shared.shared.dict["nbproc"] += -1
        print Shared.shared.dict.keys()
        if Shared.shared.dict["nbproc"] == 0:
            Shared.shared.write('Init', False)
            self.run_download_manager()


def rdm_sleep(offset=0):
    time.sleep(.001 * randint(10, 100) + offset)


def whoaim(id):
    print "I'm running on CPU #%s and I am %s" % (multiprocessing.current_process().name, id)


def proc_runner(funk, index):
    nbproc = len(index[1])
    Shared.shared.write("nbproc", nbproc)
    pool = ndp.MyPool(nbproc)

    def printer(msg):
        print msg
    for task in index[1]:
        pool.apply_async(
            download_decorator(funk),
            args=(index[0], task),
            callback=printer)
    pool.close()
    pool.join()


bucket_id = 'sixsq.eoproc'
# product = 'S2A_MSIL1C_20170202T090201_N0204_R007_T35SNA_20170202T090155.SAFE'
# # meta = 'MTD_MSIL1C.xml'
# bands = [["B02", "B03", "B06"], ["B04", "B05", "B08"], ["B01", "B02"]]
# proc_runner(MyProc, [product, bands])
