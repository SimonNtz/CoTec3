
from boto3.s3.transfer import TransferConfig
from functools import partial
from multiprocessing.pool import ThreadPool
from boto3.s3.transfer import TransferConfig
from multiprocessing import Process
import multiprocessing
from pprint import pprint as pp
import xml.etree.ElementTree as ET
import botocore
import boto3
import Queue as Q
import threading
import errno
import time
import Queue as Q
import sys
import io
import os

GB = 1024 ** 3
config = TransferConfig(multipart_threshold=0.03 * GB,
                        max_concurrency=20,
                        use_threads=True)  # max_concurency
formats_file_extension = {'JPEG2000': '.jp2'}


def create_dir(abs_path):
    path = ('/').join(abs_path.split("/")[:-1])
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def get_obj(obj, bucket_id):
    s3 = boto3.resource('s3')
    print("!!!" + obj)
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


def locate_bands(product, meta, bucket_id):
    metadata_file = "%s/%s" % (product, meta)
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
    for child in root[0][0][-1][0][0]:
        band = product + '/' + child.text
        bands[band.split('_')[-1]] = band + img_format
    # obj.download_fileobj(data)
    # print obj.get()["Body"].read().decode('utf-8')
    # tree = ET.fromstring(data.getvalue().decode("utf-8"))
    # data.read()
    return bands


def get_product_metadata(keys, bucket_id):
    pp(keys)
    pool = ThreadPool(processes=len(keys))
    # pool.map(get_obj, keys)
    _get_obj = partial(get_obj, bucket_id=bucket_id)
    pool.map(_get_obj, keys)
    # pool.map(lambda x: get_obj(x, bucket_id), keys)


def get_product_data(bands_dict, targets=None):

    def cb(band):
        print "%s downloaded." % band
        return "ok"

    if targets:
        bands = [bands_dict[i] for i in targets]
    else:
        bands = bands_dict.values()
    pool = ThreadPool(processes=len(bands))
    res = [pool.apply_async(get_obj,
                            args=(band, ),
                            callback=cb) for band in bands]
    for r in res:
        r.wait()


def locate_metadata(files, bands):
    return list(filter(lambda x: '.'.join(
        x.split('.')[:-1]) not in bands, files))


def init(bucket_id, product, meta):
    product_file_list = get_product_keys(bucket_id, product)
    bands_index = locate_bands(product, meta, bucket_id)
    metadata_loc = locate_metadata(
        product_file_list, bands_index.values())
    get_product_metadata(metadata_loc, bucket_id)


def main(bucket_id, product, meta, target_bands=None):
    # global BUCKET_NAME
    init(bucket_id, product, meta)
    # global BUCKET_NAME
    # global q
    # BUCKET_NAME = bucket_id
    # product_file_list = get_product_keys(bucket_id, product)
    # bands_index = locate_bands(product, meta)
    # # get_data_imap(bands_index)
    # metadata_loc = locate_metadata(product_file_list, bands_index.values())
    # get_product_metadata(metadata_loc)
    # get_product_data(bands_index, target_bands)
    # print list(q.queue)


if __name__ == '__main__':
    BUCKET_NAME = 'sixsq.eoproc'
    p = 'S2A_MSIL1C_20170202T090201_N0204_R007_T35SNA_20170202T090155.SAFE'
    meta_file = 'MTD_MSIL1C.xml'
    q = Q.Queue()
    main(BUCKET_NAME, p, meta_file, ['B01', 'B02', 'B03'])
# run_proc(filenames[0])
# run_async_get(filenames[0])
# process = [None] * 2
# for i in range(2):
#    #process[i] = Process(target=run_async_get, args=(filenames[i], ))
#    process[i] = Process(target=run_proc, args=(filenames[i], ))
#    process[i].start()
# for j in range(2):
#    process[j].join()
##
# time_0 = time.time()
# pool = Pool(processes=2)
# pool.map(run_proc, filenames)
# print(time.time() - time_0)
# print(time.time() - time_0)
