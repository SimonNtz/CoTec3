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
import os
import time
from snappy import Rectangle
from multiprocessing.pool import ThreadPool
from multiprocessing import Process
import functools


def read_product(f, meta=''):
    prd_meta = os.getcwd() \
        + '/%s/%s' % (f, meta)
    print prd_meta
    return ProductIO.readProduct(prd_meta)


def save_array(band, output=None):
    w = band.getRasterWidth()
    h = band.getRasterHeight()
    band_data = np.zeros(w * h, np.float32)
    band.readPixels(0, 0, w, h, band_data)
    band_data.shape = h, w
    width = 12
    height = 12
    fig = plt.figure(figsize=(width, height))
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    im = plt.imshow(band_data)
    pos = fig.add_axes([0.93, 0.1, 0.02, 0.35])  # Set colorbar position in fig
    fig.colorbar(im, cax=pos)  # Create the colorbar
    if output:
        name = output
    else:
        name = band.getName()
    fig.savefig(name + '.jpg')
    plt.close()


def resample(product, resolution):
    width = product.getSceneRasterWidth()
    height = product.getSceneRasterHeight()
    name = product.getName()
    description = product.getDescription()
    band_names = product.getBandNames()

    print("Product: %s, %d x %d pixels" % (name, width, height))

    print("Bands:   %s" % (list(band_names)))

    HashMap = jpy.get_type('java.util.HashMap')
    parameters = HashMap()
    parameters.put('targetResolution', resolution)
    result = GPF.createProduct('Resample', parameters, product)
    return result


def subset(product, bands):
    SubsetOp = jpy.get_type('org.esa.snap.core.gpf.common.SubsetOp')
#    WKTReader = jpy.get_type('com.vividsolutions.jts.io.WKTReader')
#    wkt = 'POLYGON ((27.350865857300093 36.824908050376905,
#                    27.76637805803395 36.82295594263548,
#                    27.76444424458719 36.628100558767244,
#                     27.349980428973755 36.63003894847389,
#                    27.350865857300093 36.824908050376905))'
#    geometry = WKTReader().read(wkt)
    op = SubsetOp()
    op.setBandNames(bands)
    op.setSourceProduct(product)
    op.setRegion(Rectangle(0, 500, 500, 500))
    sub_product = op.getTargetProduct()
    print("subset product ready")
    return sub_product


def main(product, meta):
    product = read_product(product, meta)
    product = resample(product, '60')
    subset(product, ['B5', 'B4'])


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
