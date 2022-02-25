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

from Product import Product
from Category import Category

maxInt = sys.maxsize


def main():
    # global redis_pool
    # print("PID %d: initializing redis pool..." % os.getpid())
    # redis_pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    print("Starting productimport.py at " + str(datetime.datetime.now()))
    startTime = time.time()
    startTimeChar = str(datetime.datetime.now())
    if environ.get('INDEX_FILE_LOCATION') is not None:
        index_file_location = (environ.get('INDEX_FILE_LOCATION'))
        print("passed in index file location " + index_file_location)
    else:
        index_file_location = "../data/index/"
        print("no passed in index file location ")
    if environ.get('PROCESSES') is not None:
        numberProcesses = int(environ.get('PROCESSES'))
        print("passed in PROCESSES " + str(numberProcesses))
    else:
        numberProcesses = 1
        print("no passed in number of processes ")

    print("process_files_parallel()" + str(startTime))
    for (dirpath, dirnames, filenames) in os.walk(index_file_location):
        # print("dirpath=" + dirpath)
        # print(dirnames)
        # print(filenames)
        process_files_parallel(dirpath, filenames, numberProcesses)
    # process_file("../data/files19.csv")
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
    if environ.get('REDIS_PASSWORD') is not None:
        redis_password = environ.get('REDIS_PASSWORD')
        print("passed in redis password is " + redis_password)
    iceCatUser = ""
    iceCatPw = ""
    if environ.get('ICECAT_USER') is not None:
        iceCatUser = environ.get('ICECAT_USER')
        print("passed in iceCatUser " + iceCatUser)
    else:
        print("no passed in icecat_user ")
        exit(1)
    if environ.get('ICECAT_PW') is not None:
        iceCatPw = environ.get('ICECAT_PW')
        print("passed in iceCatUPw " + iceCatPw)
    else:
        print("no passed in icecat_password ")
        exit(1)

    if redis_password is not None:
        conn = redis.StrictRedis(redis_server, redis_port, password=redis_password, charset="utf-8",
                                 decode_responses=True)
    else:
        conn = redis.StrictRedis(redis_server, redis_port, charset="utf-8", decode_responses=True)
    with open(file_name) as csv_file:
        # file is tab delimited
        csv_reader = csv.DictReader(csv_file, delimiter='\t', quoting=csv.QUOTE_NONE)
        prod_idx = 0
        prod_loaded = 0
        #  go through all rows in the file
        previousCatID = "juststarting"
        previousCatName = "juststarting"
        previousParentCatName = "juststarting"
        categ_name = ""
        parent_category_name = ""

        # this was not practical.  Way too slow
        # CURL_PREFIX = "curl -u " + iceCatUser + ":" + iceCatPw + " https://data.Icecat.biz/"
        # print(CURL_PREFIX)

        for row in csv_reader:
            #  increment prod_idx and use as incremental part of the key
            prod_idx += 1
            nextProduct = Product(**row)
            if nextProduct.catid and nextProduct.quality == "ICECAT":
                category_id = 'Category:' + nextProduct.catid
                # print(row)
                # print(category_id)
                # categ_name = conn.json().get(category_id, "Name")
                # parent_categ_name = conn.json().get(category_id,"ParentCategoryName")
                # the input file is loosely in category id order so no need to re-lookup same category over and over
                if previousCatID == nextProduct.catid:
                    categ_name = previousCatName
                    parent_category_name = previousParentCatName
                    nextProduct.set_category_name(categ_name)
                    nextProduct.set_parent_category_name(parent_category_name)
                    # print("previous matched prev was " + previousCatName + " prev parent " + previousParentCatName)
                else:
                    # print("in categ else")
                    getAll = None;
                    if environ.get('WRITE_JSON') is not None and environ.get('WRITE_JSON') == "true":
                        getAll = conn.json().get(category_id)
                        # print("got from json ")
                    else:
                        getAll = conn.hgetall(category_id)
                        # print("got from hash ")
                    if(getAll):
                        # print(getAll)
                        thisCategory = Category(**getAll)
                        categ_name = thisCategory.Name
                        parent_category_name = thisCategory.ParentCategoryName
                        nextProduct.set_category_name(categ_name)
                        nextProduct.set_parent_category_name(parent_category_name)
                        previousCatID = nextProduct.catid
                        previousCatName = categ_name
                        previousParentCatName = parent_category_name
                        # print("writing categ_name " + categ_name + " parent category " + parent_category_name)
            if nextProduct.quality == "ICECAT":
                nextProduct.set_key()
                prod_loaded += 1
                # print("prodkey " + nextProduct.key_name)
            # if nextProduct.product_id:
            #     productDetailFile = nextProduct.path.replace("/INT/", "/EN/")
            #     cmd = CURL_PREFIX + productDetailFile + " -o " + nextProduct.product_id + ".xml"
            #     print(cmd)
            #     args = shlex.split(cmd)
            #     process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd="../data/product/")
            #     stdout, stderr = process.communicate()
            #     conn.sadd("prodToKey", nextProduct.product_id + ":" + nextProduct.key_name)
            # print("before write of product " + str(nextProduct.product_id) + " " + nextProduct.key_name)
                if nextProduct.m_prod_id:
                    if environ.get('WRITE_JSON') is not None and environ.get('WRITE_JSON') == "true":
                        title = conn.json().get("PRODID:" + nextProduct.m_prod_id, "Title")
                        # print("json found " + nextProduct.m_prod_id)
                    else:
                        title = conn.hget("PRODID:" + nextProduct.m_prod_id, "Title")
                        # print("hash found " + nextProduct.m_prod_id)
                    if title:
                        # print("title found " + title)
                        nextProduct.title = title
                elif nextProduct.model_name:
                    nextProduct.title = nextProduct.model_name
                if environ.get('WRITE_JSON') is not None and environ.get('WRITE_JSON') == "true":
                    conn.json().set(nextProduct.key_name, Path.rootPath(), nextProduct.__dict__)
                else:
                    conn.hset(nextProduct.key_name, mapping=nextProduct.__dict__)
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
                print(str(prod_idx) + " rows loaded from file " + file_name + " " + str(prod_loaded) + " loaded to redis")
        csv_file.close()
        print(str(prod_idx) + " rows loaded " + str(prod_loaded) + " loaded to redis")
        conn.set("prod_highest_idx", prod_idx)
    print("Finished productimport.py at " + str(datetime.datetime.now()))


def process_files_parallel(dirname, names, numProcesses: int):
    # Process each file in parallel via Poll.map()
    print("starting process_files_parallel")
    pool = Pool(processes=numProcesses)
    results = pool.map(process_file, [os.path.join(dirname, name) for name in names])


def process_files(dirname, names):
    ''' Process each file in via map() '''
    results = map(process_file, [os.path.join(dirname, name) for name in names])


if '__main__' == __name__:
    main()
