#!/bin/python
#  not used curently as genaration the files was too time consuming
import time

import redis
from redis.commands.json.path import Path
import sys
import datetime
from os import environ
import os.path
from multiprocessing import Pool

import xml.etree.ElementTree as ET

from ProductDetail import ProductDetail

maxInt = sys.maxsize


def main():
    # global redis_pool
    # print("PID %d: initializing redis pool..." % os.getpid())
    # redis_pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    print("Starting productDetailImport.py at " + str(datetime.datetime.now()))
    startTime = time.time()
    startTimeChar = str(datetime.datetime.now())
    product_file_location = ""
    if environ.get('PRODUCT_FILE_LOCATION') is not None:
        product_file_location = environ.get('PRODUCT_FILE_LOCATION')
        print("passed in product file location " + product_file_location)
    else:
        product_file_location = "../data/product/"
        print("no passed in product file location ")

    if environ.get('PROCESSES') is not None:
        numberProcesses = int(environ.get('PROCESSES'))
        print("passed in PROCESSES " + str(numberProcesses))
    else:
        numberProcesses = 1
        print("no passed in number of processes ")

    print("process_files_parallel()" + str(startTime))
    for (dirpath, dirnames, filenames) in os.walk(product_file_location):
        # print("dirpath=" + dirpath)
        # print(dirnames)
        # print(filenames)
        process_files_parallel(dirpath, filenames, numberProcesses)
        # process_files(dirpath, filenames)
    # process_file("../data/product/1409.xml")
    endTime = time.time()
    print("processing complete. start was " + startTimeChar + " end was " + str(datetime.datetime.now()) +
           " total time " + str(int(endTime - startTime)) + " seconds")

def process_file(file_name):
    print("starting process_file with file name " + file_name)
    if "xml" not in file_name:
        print("invalid file name")
        return
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
    with open(file_name) as xml_file:
        # create element tree object
        tree = ET.parse(xml_file)

        # get root element
        root = tree.getroot()
        print("root.tag is ", root.tag)
        cat_cntr = 0
        for child in root:
            print("child tag is " + child.tag)
            print("child attribute is " + str(child.attrib))
        for prod in root.findall('Product'):
            print("starting in xml file")
            print("prod.tag is " + str(prod.tag))
            print("prod.attribute is " + str(prod.attrib))

            if int(prod.attrib['Code']) > -1:
                next_product = ProductDetail()
                prod_id = prod.attrib['ID']
                print("ID is ", str(prod_id))
                next_product.ID = str(prod_id)
                # print("ID is " + next_product.ID)
                if prod.attrib['LowPic']:
                    #     conn.hset(category_id, "lowpic", prod.attrib['LowPic'])
                    next_product.LowPic = str(prod.attrib['LowPic'])
                    next_product.LowPicHeight = prod.attrib['LowPicHeight']
                    next_product.LowPicSize = prod.attrib['LowPicSize']
                    next_product.LowPicWidth = prod.attrib['LowPicWidth']
                    print("lowpic is " + next_product.LowPic)
                if prod.attrib['ThumbPic']:
                    #     conn.hset(category_id, "thumbpic", prod.attrib['ThumbPic'])
                    next_product.ThumbPic = str(prod.attrib['ThumbPic'])
                    # next_product.ThumbPicHeight = prod.attrib['ThumbPicHeight']
                    next_product.ThumbPicSize = prod.attrib['ThumbPicSize']
                    # next_product.ThumbPicWidth = prod.attrib['ThumbPicWidth']
                    print("thumbpic is " + next_product.ThumbPic)

                if prod.attrib['HighPic']:
                    next_product.HighPic = prod.attrib['HighPic']
                    print("highpic is " + next_product.HighPic)
                    next_product.HighPicHeight = prod.attrib['HighPicHeight']
                    next_product.HighPicSize = prod.attrib['HighPicSize']
                    next_product.HighPicWidth = prod.attrib['HighPicWidth']
                if prod.attrib['Pic500x500']:

                    next_product.Pic500x500 = prod.attrib['Pic500x500']
                    print("pic500 is " + next_product.Pic500x500)
                    next_product.Pic500x500Size = prod.attrib['Pic500x500Size']
                    next_product.Pic500x500Width = prod.attrib['Pic500x500Width']
                    next_product.Pic500x500Height = prod.attrib['Pic500x500Height']

                next_product.set_key()

                next_product.BrandLocalTitle = prod.attrib['BrandLocalTitle']
                next_product.Code = prod.attrib['Code']
                next_product.GeneratedIntTitle = prod.attrib['GeneratedIntTitle']
                next_product.GeneratedLocalTitle = prod.attrib['GeneratedLocalTitle']
                next_product.IntName = prod.attrib['IntName']
                print("IntName is " + next_product.IntName)
                next_product.LocalName = prod.attrib['LocalName']
                next_product.Name = prod.attrib['Name']
                next_product.Prod_id = prod.attrib['Prod_id']
                next_product.Quality = prod.attrib['Quality']
                print("Quality is " + next_product.Quality)
                next_product.ReleaseDate = prod.attrib['ReleaseDate']
                next_product.Title = prod.attrib['Title']
                conn.json().set(next_product.key_name, Path.rootPath(), next_product.__dict__)

    xml_file.close()
    print("Finished productDetailImport.py at " + str(datetime.datetime.now()))


def process_files_parallel(dirname, names, numProcesses: int):
    # Process each file in parallel via Poll.map()
    print("starting process_files_parallel")
    pool = Pool(processes=numProcesses)
    results = pool.map(process_file, [os.path.join(dirname, name) for name in names])


def process_files(dirname, names):
    # Process each file in via map
    results = map(process_file, [os.path.join(dirname, name) for name in names])


if '__main__' == __name__:
    main()
