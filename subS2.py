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



indices_expr = { 'ndvi': '(B7 + B4) != 0 ? (B7 - B4) / (B7 + B4) : -2',
    		 'ndi45': '(B5 + B4) != 0 ? (B5 - B4) / (B5 + B4) : -2',
                  'gndvi': '(B7 + B3) != 0 ? (B7 - B3) / (B7 + B3) : -2'} 
    


def read_product(f, meta=None): 
    product = ProductIO.readProduct(f)
#    width = product.getSceneRasterWidth()
#    height = product.getSceneRasterHeight()
#    name = product.getName()
#    description = product.getDescription()
#    band_names = product.getBandNames()
#    print("Product: %s, %d x %d pixels" % (name, width, height))
#    print("Bands:   %s" % (list(band_names)))    
    return product
 
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

def subset():
    SubsetOp = jpy.get_type('org.esa.snap.core.gpf.common.SubsetOp')
#    WKTReader = jpy.get_type('com.vividsolutions.jts.io.WKTReader')
#    wkt = 'POLYGON ((27.350865857300093 36.824908050376905,
#		     27.76637805803395 36.82295594263548,
#	 	     27.76444424458719 36.628100558767244,
#                     27.349980428973755 36.63003894847389,
#                    27.350865857300093 36.824908050376905))'
#    geometry = WKTReader().read(wkt)
    op = SubsetOp()
    op.setSourceProduct(result)
    op.setRegion(Rectangle(0, 500, 500, 500))
    sub_product = op.getTargetProduct()
    print("subset product ready")
    return sub_product

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
    result = GPF.createProduct('BandMaths', parameters, product)	
    print('Expression computed: ' + indices_expr[index])
    #save_array(result.getBand(index))
    product.dispose()
    result.dispose()
    return result.getBand(index)

def save_array(band):
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
    plt.savefig(band.getName() + '.jpg') 
#    save_array_plot(result.getBand(index))
#    return result.getBand(index)

def write_product(p):
    return ProductIO.writeProduct(p, p + '.dim', 'BEAM-DIMAP')    


def run_worker(index):
    #product = read_product(f)
    compute_vegeation_index(product, index)
    

def main():
    indices = ['ndvi', 'ndi45']#, 'gndvi'] 
    #run_worker('ndi45')
    pool = ThreadPool(processes=2)
    pool.map(run_worker, indices)
   #pool.map(lambda x: run_worker(f, x), indices)

    #pool.map(lambda x: compute_vegeation_index(product, x), indices)

#    compute_vegeation_index(product, 'ndvi') 
   

if __name__ == '__main__':
    f = sys.argv[1]
    product = read_product(f)
    main()

    
# width = sub_product.getSceneRasterWidth()
# height = sub_product.getSceneRasterHeight()
# name = sub_product.getName()
# description = sub_product.getDescription()
# band_names = sub_product.getBandNames()
# print("Product: %s, %d x %d pixels" % (name, width, height))
# print("Bands:   %s" % (list(band_names)))
# ndvi_expr = '(B7 + B4) != 0 ? (B7 - B4) / (B7 + B4) : -2'
# ndi45_expr = '(B5 + B4) != 0 ? (B5 - B4) / (B5 + B4) : -2'
# gndvi_expr = '(B7 + B3) != 0 ? (B7 - B3) / (B7 + B3) : -2'
#
# GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()
#
# HashMap = jpy.get_type('java.util.HashMap')
# BandDescriptor = jpy.get_type(
#     'org.esa.snap.core.gpf.common.BandMathsOp$BandDescriptor')
#
# print '1'
# targetBand1 = BandDescriptor()
# targetBand1.name = 'ndvi'
# targetBand1.type = 'float32'
# targetBand1.expression = ndvi_expr
#
# targetBand2 = BandDescriptor()
# targetBand2.name = 'ndi45'
# targetBand2.type = 'float32'
# targetBand2.expression = ndi45_expr
#
# targetBand3 = BandDescriptor()
# targetBand3.name = 'gndvi'
# targetBand3.type = 'float32'
# targetBand3.expression = gndvi_expr
#
# targetBands = jpy.array(
#     'org.esa.snap.core.gpf.common.BandMathsOp$BandDescriptor', 3)
# targetBands[0] = targetBand1
# targetBands[1] = targetBand2
# targetBands[2] = targetBand3
#
# parameters = HashMap()
# parameters.put('targetBands', targetBands)
#
# print '2'
#
# result = GPF.createProduct('BandMaths', parameters, sub_product)
# band1 = result.getBand('ndvi')
# band2 = result.getBand('ndi45')
# band3 = result.getBand('gndvi')
#
# w = band1.getRasterWidth()
# h = band1.getRasterHeight()
#
# band1_data = np.zeros(w * h, np.float32)
# band1.readPixels(0, 0, w, h, band1_data)
#
# band2_data = np.zeros(w * h, np.float32)
# band2.readPixels(0, 0, w, h, band2_data)
#
# band3_data = np.zeros(w * h, np.float32)
# band3.readPixels(0, 0, w, h, band3_data)
#
# print '3'
# sub_product.dispose()
# result.dispose()
#
# band1_data.shape = h, w
# band2_data.shape = h, w
# band3_data.shape = h, w
#
# print '4'
#
# width = 12
# height = 12
# fig = plt.figure(figsize=(width, height))
# plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
#
# im = plt.imshow(band1_data)
# pos = fig.add_axes([0.93, 0.1, 0.02, 0.35])  # Set colorbar position in fig
# fig.colorbar(im, cax=pos)  # Create the colorbar
# plt.savefig('ndvi.jpg')
#
# im = plt.imshow(band2_data)
# pos = fig.add_axes([0.93, 0.1, 0.02, 0.35])  # Set colorbar position in fig
# fig.colorbar(im, cax=pos)  # Create the colorbar
# plt.savefig('ndi45.jpg')
#
# im = plt.imshow(band3_data)
# pos = fig.add_axes([0.93, 0.1, 0.02, 0.35])  # Set colorbar position in fig
# fig.colorbar(im, cax=pos)  # Create the colorbar
# plt.savefig('gndvi.jpg')
#
# print(time.time() - t0)
#fig = plt.figure(figsize=(width, height))
#ax = plt.Axes(fig, [0., 0., 1., 1.])
# ax.set_axis_off()
# fig.add_axes(ax)
# ax.imshow(band1_data)
# plt.colorbar()
#plt.savefig('sub_b6_data.png', transparent=True)
#


