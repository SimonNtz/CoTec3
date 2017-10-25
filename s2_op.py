import sys
sys.path.append('/root/.snap/snap-python')
import snappy
from snappy import ProductIO
from snappy import jpy
from snappy import GPF
from snappy import HashMap
import numpy as np
import os
import time
from snappy import Rectangle
from multiprocessing.pool import ThreadPool
from multiprocessing import Process


indices_expr = {'ndvi': '(B7 + B4) != 0 ? (B7 - B4) / (B7 + B4) : -2',
                'ndi45': '(B5 + B4) != 0 ? (B5 - B4) / (B5 + B4) : -2',
                'gndvi': '(B7 + B3) != 0 ? (B7 - B3) / (B7 + B3) : -2'}


def compute_vegeation_index(product, index):
    GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()
    HashMap = jpy.get_type('java.util.HashMap')
    BandDescriptor = jpy.get_type(
        'org.esa.snap.core.gpf.common.BandMathsOp$BandDescriptor')
    targetBand = BandDescriptor()
    targetBand.name = index
    targetBand.type = 'float32'
    targetBand.expression = indices_expr[index]
    targetBands = jpy.array(
        'org.esa.snap.core.gpf.common.BandMathsOp$BandDescriptor', 1)
    targetBands[0] = targetBand
    parameters = HashMap()
    parameters.put('targetBands', targetBands)
    print("Start to compute:" + indices_expr[index])
    result = GPF.createProduct('BandMaths', parameters, product)
    print('Expression computed: ' + indices_expr[index])
    print result.getBand(index)
    return result.getBand(index)


def main():
    pass


if __name__ == '__main__':
    main()
