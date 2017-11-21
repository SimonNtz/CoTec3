from multiprocessing.pool import Pool
from multiprocessing import Process
from pprint import pprint as pp
import decorate_decorator_object as pr
import multiprocessing
# import MyProc
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


def MyProc(meta):
    return("About to process " + str(meta))


def main(prods, jobs):
    print "%d cpu available" % multiprocessing.cpu_count()
    sum_tasks = sum([len(job[1]) for job in jobs])
    print "%d jobs, %d tasks" % (len(jobs), sum_tasks)

    for job in jobs:
        proc_func, tasks = job
        pr.proc_runner(proc_func, [prods, tasks])


if __name__ == '__main__':

    task1 = {
        'bands': ['B01', 'B02'],
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

    jobs = [(MyProc, [task1, task2, task3])]
    main(products[0], jobs)
