from multiprocessing.pool import Pool
from multiprocessing import Process
import proc_runner
import multiprocessing
import snap_op as snap
import sys
import io
import os
import time


bucket = 'sixsq.eoproc'

products = ['S2A_OPER_PRD_MSIL1C_PDMC_20151230T202002_R008_V20151230T105153_20151230T105153.SAFE',
            'S2A_MSIL1C_20170202T090201_N0204_R007_T35SNA_20170202T090155.SAFE',
            'S2A_MSIL1C_20170617T012701_N0205_R074_T54SUF_20170617T013216.SAFE']


meta_file_dict = {'S2A_MTD': 'MTD_MSIL1C.xml'}


# Import your proces or paste it here
def MyProc(meta, params):
    return("About to process %s with parameters %s" % (str(meta), str(params)))


def main(prods, jobs):
    print "%d cpu available" % multiprocessing.cpu_count()
    sum_tasks = sum([len(job[1]) for job in jobs])
    print "%d jobs, %d tasks" % (len(jobs), sum_tasks)

    for job in jobs:
        proc_func, tasks = job
        proc_runner.main(proc_func, [prods, tasks])


if __name__ == '__main__':

    task1 = {
        'bands': ['B04', 'B07'],
        'params': ['ndvi']
    }
    task2 = {
        'bands': ['B05', 'B04'],
        'params': ['ndi45']
    }
    task3 = {
        'bands': ['B06', 'B07'],
        'params': ['gndvi']
    }
    jobs = [(snap.main, [task1])]
    # jobs = [(MyProc, [task1, task2, task3])]
    main(products[0], jobs)
