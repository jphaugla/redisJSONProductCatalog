#!/bin/python

import csv
import time
# import shlex, subprocess

import redis
from redis.commands.json.path import Path
import sys
import datetime
from os import environ
import os.path
from multiprocessing import Pool

from ProductTitle import ProductTitle
from Category import Category

maxInt = sys.maxsize


def main():
    # global redis_pool
    # print("PID %d: initializing redis pool..." % os.getpid())
    # redis_pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    print("Starting productimport.py at " + str(datetime.datetime.now()))
    startTime = time.time()
    startTimeChar = str(datetime.datetime.now())
    if environ.get('PRODID_FILE_LOCATION') is not None:
        prodid_file_location = (environ.get('PRODID_FILE_LOCATION'))
        print("passed in prodid file location " + prodid_file_location)
    else:
        prodid_file_location = "../data/prodid"
        print("no passed in index file location ")
    if environ.get('PROCESSES') is not None:
        numberProcesses = int(environ.get('PROCESSES'))
        print("passed in PROCESSES " + str(numberProcesses))
    else:
        numberProcesses = 1
        print("no passed in number of processes ")

    print("process_files_parallel()" + str(startTime))
    for (dirpath, dirnames, filenames) in os.walk(prodid_file_location):
        # print("dirpath=" + dirpath)
        # print(dirnames)
        # print(filenames)
        process_files_parallel(dirpath, filenames, numberProcesses)
    # process_file("../data/prodid_d100.txt")
    endTime = time.time()
    print("processing complete. start was " + startTimeChar + " end was " + str(datetime.datetime.now()) +
           " total time " + str(int(endTime - startTime)) + " seconds")

def process_file(file_name):
    print("starting process_file with file name " + file_name)
    if environ.get('REDIS_SERVER') is not None:
        redis_server = environ.get('REDIS_SERVER')
        print("passed in redis server is " + redis_server)
    else:
        redis_server = 'localhost'
        print("no passed in redis server variable ")

    if environ.get('REDIS_PORT') is not None:
        redis_port = int(environ.get('REDIS_PORT'))
        print("passed in redis port is " + str(redis_port))
    else:
        redis_port = 6379
        print("no passed in redis port variable ")

    conn = redis.StrictRedis(host=redis_server, port=redis_port, db=0, charset="utf-8", decode_responses=True)
    with open(file_name) as csv_file:
        # file is tab delimited
        csv_reader = csv.DictReader(csv_file, delimiter='\t', quoting=csv.QUOTE_NONE)
        prod_idx = 0
        prod_loaded = 0
        #  go through all rows in the file

        for row in csv_reader:
            #  increment prod_idx and use as incremental part of the key
            # print(row)
            prod_idx += 1
            nextProduct = ProductTitle(**row)
            # print(nextProduct)
            if nextProduct.Title and nextProduct.Quality == "ICECAT":
                prod_loaded += 1
                subset = {k: nextProduct.__dict__[k] for k in ('Partnumber', 'Title')}
                # print(subset)
                if environ.get('WRITE_JSON') is not None and environ.get('WRITE_JSON') == "true":
                    conn.json().set("PRODID:" + nextProduct.Partnumber, Path.rootPath(), subset)
                else:
                    conn.hset("PRODID:" + nextProduct.Partnumber, mapping=subset)
                # this write is for debug to know what line failed on
                conn.set("prod_highest_idx" + file_name, prod_idx)
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
            if prod_idx % 50000 == 0:
                print(str(prod_idx) + " rows from file " + file_name + " " + str(prod_loaded) + " rows added to redis")
        csv_file.close()
        print(str(prod_idx) + " rows loaded " + str(prod_loaded) + " rows added to redis")
        conn.set("prod_highest_idx", prod_idx)
    print("Finished productTitleimport.py at " + str(datetime.datetime.now()))


def process_files_parallel(dirname, names, numProcesses: int):
    # Process each file in parallel via Poll.map()
    print("starting process_files_parallel")
    pool = Pool(processes=numProcesses)
    results = pool.map(process_file, [os.path.join(dirname, name) for name in names if name.find("csv")])


def process_files(dirname, names):
    ''' Process each file in via map() '''
    results = map(process_file, [os.path.join(dirname, name) for name in names])


if '__main__' == __name__:
    main()
