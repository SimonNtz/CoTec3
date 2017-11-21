import sys
sys.path.append('/root/.snap/snap-python')
import snappy
from snappy import ProductIO
from snappy import jpy
from snappy import GPF
from snappy import HashMap
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from snappy import Rectangle
from skimage import exposure
import os
import time


def read_product(object):
    return ProductIO.readProduct(object)


def crop(product):
    SubsetOp = jpy.get_type('org.esa.snap.core.gpf.common.SubsetOp')
    op = SubsetOp()
    op.setSourceProduct(product)
    op.setRegion(Rectangle(0, 500, 500, 500))
    return op.getTargetProduct()


def resample(input, resolution_target):
    HashMap = jpy.get_type('java.util.HashMap')
    parameters = HashMap()
    parameters.put('targetResolution', 60)
    output = GPF.createProduct('Resample', parameters, input)
    return output


def main(object):
    product = read_product(object)
    resolution_target = 60
    resampled_product = resample(product,
                                 resolution_target)
    crop_dim = [0, 500, 500, 500]
    cropped_product = crop(resampled_product,
                           crop_dim)
    ProductIO.writeProduct(cropped_product, 'subset_output.dim', 'BEAM-DIMAP')


if __name__ == '__main__':
    main(sys.argv[1])
