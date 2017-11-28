from boto3.s3.transfer import TransferConfig
from functools import partial
from multiprocessing.pool import ThreadPool
from boto3.s3.transfer import TransferConfig
from multiprocessing import Process
import multiprocessing
from pprint import pprint as pp
import xml.etree.ElementTree as ET
import product_meta as pm
import botocore
import boto3
import Queue as Q
import threading
import errno
import time
import Queue as Q
import Shared
import sys
import io
import os

GB = 1024 ** 3
config = TransferConfig(multipart_threshold=0.03 * GB,
                        max_concurrency=20,
                        use_threads=True)  # max_concurency
formats_file_extension = {'JPEG2000': '.jp2'}
meta_lock = False


def create_dir(abs_path):
    path = ('/').join(abs_path.split("/")[:-1])
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def get_obj(obj, bucket_id):
    create_dir(obj)
    s3 = boto3.resource('s3')
    try:
        rep = s3.Bucket(bucket_id).download_file(obj, obj, Config=config)
    except OSError:
        print("Failled to download "
              + key
              + " from "
              + bucket_id)
    return obj


def filter_data_order(inv_data_key, key):
    foo = list(filter(lambda x: not inv_data_key, key))
    return foo


def get_product_keys(bucket_id, f):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_id)
    objects = list(bucket.objects.filter(Prefix=f + '/'))
    return map(lambda x: x.Object().key, list(objects))


def _extract_img_format(root):
    temp = root[0][0][-1][0][0].attrib['imageFormat']
    return formats_file_extension[temp]


def locate_bands(product, meta, file_keys, bucket_id):
    #metadata_file = "%s/%s" % (product, meta)
    metadata_file = meta
    print "Determine bands' location from " + metadata_file
    s3 = boto3.resource('s3')
    obj = s3.Object(bucket_id, metadata_file)
    data = io.BytesIO()
    obj.download_fileobj(data)
    data.seek(0)
    root = ET.parse(data).getroot()
    try:
        img_format = _extract_img_format(root)
    except KeyError as er:
        print("Unknown format " + er)

    bands = {}
    pp(file_keys)
    for child in root[0][0][-1][0][0]:
        band = child.text
        print band
        bands[band.split(
            '_')[-1]] = ''.join([f for f in file_keys if f.find(band) != -1])
    # obj.download_fileobj(data)
    # print obj.get()["Body"].read().decode('utf-8')
    # tree = ET.fromstring(data.getvalue().decode("utf-8"))
    # data.read()
    return bands


def get_product_metadata(keys, bucket_id):
    pool = ThreadPool(processes=len(keys))
    _get_obj = partial(get_obj, bucket_id=bucket_id)
    pool.map(_get_obj, keys)
    Shared.shared.write('meta', True)
    print "Metadata ready."


def get_product_data(bands_dict, bucket_id, targets=None):
    def value2key(value):
        return bands_dict.keys()[bands_dict.values().index(value)]

    def cb(band):
        band_key = value2key(band)
        print("%s downloaded." % band_key)
        Shared.shared.write(band_key, True)

    if targets:
        bands = [bands_dict[i] for i in targets]
    else:
        bands = bands_dict.values()

    pool = ThreadPool(processes=len(bands))
    print "Download of %s is starting" % str(bands)
    res = [pool.apply_async(get_obj,
                            args=(band, bucket_id),
                            callback=cb) for band in bands]
    pool.close()
    pool.join()


def locate_metadata(files, bands):
    return [f for f in files if f not in bands]


def init(bucket_id, product):
    product_file_list = get_product_keys(bucket_id, product)
    bands_index = locate_bands(
        product, pm.get_meta_from_prod(product), product_file_list, bucket_id)
    metadata_loc = locate_metadata(
        product_file_list, bands_index.values())
    return bands_index, metadata_loc


def main(bucket_id, product, meta, target_bands=None):
    bands_index = init(bucket_id, product, meta)
    bands = ["B02", "B03", "B06"]  # , ["B04", "B05", "B08"]]
    get_product_data(bands_index, bucket_id, bands)


if __name__ == '__main__':
    BUCKET_NAME = 'sixsq.eoproc'
    p = 'S2A_MSIL1C_20170202T090201_N0204_R007_T35SNA_20170202T090155.SAFE'
    meta_file = 'MTD_MSIL1C.xml'
    q = Q.Queue()
    main(BUCKET_NAME, p, meta_file, ['B01', 'B02', 'B03'])
