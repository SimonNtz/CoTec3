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


''' Read resample, subset, and compute the vegetation indices of SENTINEL-2
    products'''

indices_expr = {'ndvi': '(B7 + B4) != 0 ? (B7 - B4) / (B7 + B4) : -2',
                'ndi45': '(B5 + B4) != 0 ? (B5 - B4) / (B5 + B4) : -2',
                'gndvi': '(B7 + B3) != 0 ? (B7 - B3) / (B7 + B3) : -2'}


def read_product(f, meta=None):
    print(os.getcwd() + '/' + f)
    product = ProductIO.readProduct(os.getcwd() + '/' + f)
    width = product.getSceneRasterWidth()
    height = product.getSceneRasterHeight()
    name = product.getName()
    description = product.getDescription()
    band_names = product.getBandNames()
    print("Product: %s, %d x %d pixels") % (name, width, height)
    print("Bands:   %s") % (list(band_names))

    return product


def resample(product, params):
    #    product = read_product(product)
    width = product.getSceneRasterWidth()
    height = product.getSceneRasterHeight()
    name = product.getName()
    description = product.getDescription()
    band_names = product.getBandNames()

    print("Product: %s, %d x %d pixels" % (name, width, height))

    print("Bands:   %s" % (list(band_names)))

    HashMap = jpy.get_type('java.util.HashMap')
    parameters = HashMap()
    parameters.put('targetResolution', params)
    result = GPF.createProduct('Resample', parameters, product)
    return result


def compute_vegeation_index(product, index):
    index = ''.join(index)
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


def main(product, params):
    product = read_product(product)
    product = resample(product, 60)
    compute_vegeation_index(product, params)


if __name__ == '__main__':
    products = ['S2A_OPER_PRD_MSIL1C_PDMC_20151230T202002_R008_V20151230T105153_20151230T105153.SAFE',
                'S2A_MSIL1C_20170202T090201_N0204_R007_T35SNA_20170202T090155.SAFE',
                'S2A_MSIL1C_20170617T012701_N0205_R074_T54SUF_20170617T013216.SAFE']

    meta = 'S2A_OPER_MTD_SAFL1C_PDMC_20151230T202002_R008_V20151230T105153_20151230T105153.xml'
    main(products[0] + '/' + meta, 'ndvi')
