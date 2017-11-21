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


def read_product(f, meta=''):
    prd_meta = os.getcwd() \
               + '/%s/%s' %(f, meta)
    print prd_meta
    return ProductIO.readProduct(prd_meta)


    
	
def save_array(band):
    print(band.getName() + ' called')
    w = band.getRasterWidth()
    h = band.getRasterHeight()
    band_data = np.zeros(w * h, np.float32)
    band.readPixels(0, 0, w, h, band_data)
    band_data.shape = h, w
    width = 12
    height = 12
    fig = plt.figure(figsize=(width, height))
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    #plt.ion()
    im = plt.imshow(band_data)
    pos = fig.add_axes([0.93, 0.1, 0.02, 0.35])  # Set colorbar position in fig
    fig.colorbar(im, cax=pos)  # Create the colorbar
    fig.savefig(band.getName() + '.jpg')
    plt.close()


def _processes(bands):
    process = []
    for b in bands:
        process.append(Process(target=save_array,
                          args=(b, )))
        process[-1].start()
    for p in process:
        p.join()


def _pool(bands):
    pool = ThreadPool(processes=len(bands))
    pool.map(save_array, bands)
    #pool.map(test_plot, bands)


def _seq(bands):
    for b in bands:
	save_array(b)


def main(): 
    product = read_product(sys.argv[1])
    indices = ['ndvi', 'ndi45', 'gndvi']
    bands = [product.getBand('B1'),
             product.getBand('B2'),
             product.getBand('B3')]    
    #t0 = time.time()   
    #_processes(bands)
    #print ("|| processes time: " + str(time.time() - t0))
    #t0 = time.time()
    #_seq(bands)
    #print ("seq processes time: " + str(time.time() - t0))
    #t0 = time.time()
    #_pool(bands)
    #map(save_array, bands)
    #print ("|| map process time: " + str(time.time() - t0))

if __name__ == '__main__':
    main()
