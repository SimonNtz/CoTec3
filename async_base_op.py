from multiprocessing.pool import ThreadPool
from multiprocessing import Process
from pprint import pprint as pp
import Queue as Q
import product_downloader
# import snap_base_op as snap
# import s2_op as s2
import sys
import io
import os
import time


bucket = 'sixsq.eoproc'
filenames = ['S2A_MSIL1C_20170202T090201_N0204_R007_T35SNA_20170202T090155.SAFE',
             'S2A_MSIL1C_20170617T012701_N0205_R074_T54SUF_20170617T013216.SAFE']

meta_file = 'MTD_MSIL1C.xml'


def main():
    product_size = len(filenames)
    process = [None] * product_size
    t0 = time.time()
    for i in range(product_size):
        process[i] = Process(target=product_downloader.main,
                             args=(bucket, filenames[i], meta_file))
        process[i].start()
    for j in range(product_size):
        process[j].join()
    print time.time() - t0


if __name__ == '__main__':
    main()
