#!/bin/python

import csv
import time

import redis
from redis.commands.json.path import Path
import sys
import datetime
from os import environ
import os.path
from multiprocessing import Pool

from Product import Product
from Category import Category

maxInt = sys.maxsize


def main():
    # global redis_pool
    # print("PID %d: initializing redis pool..." % os.getpid())
    # redis_pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    print("Starting productimport.py at " + str(datetime.datetime.now()))
    startTime = time.time()
    if environ.get('INDEX_FILE_LOCATION') is not None:
        index_file_location = (environ.get('INDEX_FILE_LOCATION'))
        print("passed in index file location " + index_file_location)
    else:
        index_file_location = "../data/index/"
        print("no passed in index file location ")

    print("process_files_parallel()" + str(startTime))
    # for (dirpath, dirnames, filenames) in os.walk(index_file_location):
    #     print("dirpath=" + dirpath)
    #     print(dirnames)
    #     print(filenames)
    #     process_files_parallel("start", dirpath, filenames)
    process_file("../data/files100.csv")

def process_file(file_name):

    print("starting process_file with file name " + file_name)
    if environ.get('REDIS_SERVER') is not None:
        redis_server = environ.get('REDIS_SERVER')
        print("passed in redis server is " + redis_server)
    else:
        redis_server = '10.0.1.35'
        print("no passed in redis server variable ")

    if environ.get('REDIS_PORT') is not None:
        redis_port = int(environ.get('REDIS_PORT'))
        print("passed in redis port is " + str(redis_port))
    else:
        redis_port = 13000
        print("no passed in redis port variable ")
    conn = redis.StrictRedis(host = redis_server, port=redis_port, db=0, charset="utf-8", decode_responses=True)
    with open(file_name) as csv_file:
        # file is tab delimited
        csv_reader = csv.DictReader(csv_file, delimiter='\t', quoting=csv.QUOTE_NONE)
        prod_idx = 0
        #  go through all rows in the file
        for row in csv_reader:
            #  increment prod_idx and use as incremental part of the key
            prod_idx += 1
            nextProduct = Product(**row)
            if nextProduct.catid:
                category_id = 'Category:' + nextProduct.catid
                # print(row)
                # print(category_id)
                # categ_name = conn.json().get(category_id, "Name")
                # parent_categ_name = conn.json().get(category_id,"ParentCategoryName")
                getAll = conn.json().get(category_id)
                print(getAll)
                thisCategory = Category(**getAll)
                categ_name = thisCategory.Name
                parent_category_name = thisCategory.ParentCategoryName
                nextProduct.set_category_name(categ_name)
                nextProduct.set_parent_category_name(parent_category_name)
            nextProduct.set_key()
            # print("before write of product " + str(nextProduct.product_id) + " " + nextProduct.key_name)
            conn.json().set(nextProduct.key_name, Path.rootPath(), nextProduct.__dict__)
            # 0)path 1)product_id 2)updated 3)quality 4)supplier_id 5)prod_id 6)catid 7)m_prod_id 8)ean_upc 9)on_market
            # 10)country_market 11)model_name 12)product_view 13)high_pic 14)high_pic_size
            # 15)high_pic_width 16)high_pic_height 17)m_supplier_id 18)m_supplier_name 19)ean_upc_is_approved
            # 20)Limited Date_Added
            # index will be model name and hold value of prod_idx
            # comment this out for now-might now need with JSON search
            # if categ_name and not categ_name.isspace():
            #     conn.sadd("CategIDX:" + categ_name, nextProduct.key_name)
            # if nextProduct.model_name and not nextProduct.model_name.isspace():
            #     model_key: str = "ProductModel:" + nextProduct.model_name
            #     # print("model key is " + model_key)
            #     conn.sadd(model_key, nextProduct.key_name)
            if prod_idx % 10000 == 0:
                print(str(prod_idx) + " rows loaded from file ")
        csv_file.close()
        print(str(prod_idx) + " rows loaded")
        conn.set("prod_highest_idx", prod_idx)
    print("Finished productimport.py at " + str(datetime.datetime.now()))


def process_files_parallel(arg, dirname, names):
    # Process each file in parallel via Poll.map()
    print("starting process_files_parallel")
    pool = Pool()
    results = pool.map(process_file, [os.path.join(dirname, name) for name in names])

def process_files(arg, dirname, names):
    ''' Process each file in via map() '''
    results = map(process_file, [os.path.join(dirname, name) for name in names])

if '__main__' == __name__:
    main()
