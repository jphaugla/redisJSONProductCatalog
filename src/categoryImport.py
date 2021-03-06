#!/bin/python
import xml.etree.ElementTree as ET
import redis
import json

from redis.commands.json.path import Path
from os import environ

from Category import Category

REDIS_HOST = 'redis'


def main():
    redis_password = ""
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

    if environ.get('CATEGORY_FILE_LOCATION') is not None:
        category_file_location = environ.get('CATEGORY_FILE_LOCATION')
        print("passed in category file location " + category_file_location)
    else:
        category_file_location = "../data/CategoriesList.xml"
        print("no passed in category file location ")
    # conn = redis.StrictRedis(redis_server, redis_port)
    if redis_password is not None:
        conn = redis.StrictRedis(redis_server, redis_port, password=redis_password, charset="utf-8", decode_responses=True)
    else:
        conn = redis.StrictRedis(redis_server, redis_port, charset="utf-8", decode_responses=True)
    with open(category_file_location) as xml_file:
        # create element tree object
        tree = ET.parse(xml_file)

        # get root element
        root = tree.getroot()
        print("root.tag is ", root.tag)
        cat_cntr = 0
        for child in root:
            print("child tag is " + child.tag)
            print("child attribute is " + str(child.attrib))
        for cat in root.findall('Response/CategoriesList/Category'):
            # print("starting in xml file")
            # print("cat.tag is " + str(cat.tag))
            # print("cat.attribute is " + str(cat.attrib))
            next_category = Category()
            cat_cntr += 1
            cat_id = cat.attrib['ID']
            # print("ID is ", str(cat_id))
            next_category.ID = str(cat_id)
            # print("ID is " + next_category.ID)
            next_category.Score = str(cat.attrib['Score'])
            # category_id = 'categ:' + cat_id
            # conn.hset(category_id, "ID", cat_id)
            if cat.attrib['LowPic']:
                #     conn.hset(category_id, "lowpic", cat.attrib['LowPic'])
                next_category.LowPic = str(cat.attrib['LowPic'])
                # print("lowpic is " + next_category.LowPic)
            if cat.attrib['ThumbPic']:
                #     conn.hset(category_id, "thumbpic", cat.attrib['ThumbPic'])
                next_category.ThumbPic = str(cat.attrib['ThumbPic'])
                # print("thumbpic is " + next_category.ThumbPic)
            for cat_child in cat:
                # category_id is
                # print("cat_child.tag is " + str(cat_child.tag))
                # print("cat_child.attribute is " + str(cat_child.attrib))
                if cat_child.tag == 'Name' and cat_child.attrib['langid'] == '1':
                    cat_name = cat_child.attrib['Value']
                    # print("category name is " + cat_name)
                    next_category.set_category_name(str(cat_name))
                    # print("category name is " + next_category.Name)
                elif cat_child.tag == 'ParentCategory' and cat_id != "1":
                    parent_cat_id = cat_child.attrib['ID']
                    next_category.ParentCategoryID = str(parent_cat_id)
                    # print("parent_cat_id is " + parent_cat_id)
                    for parent_child in cat_child:
                        # print("parent_child is " + str(parent_child))
                        for name in parent_child:
                            # print("name under parent child is " + str(name))
                            if name.tag == 'Name' and name.attrib['langid'] == '1':
                                next_category.ParentCategoryName = str(name.attrib['Value'])
                    if environ.get('WRITE_JSON') is not None and environ.get('WRITE_JSON') == "true":
                        conn.json().set(next_category.get_key(), Path.root_path(), next_category.__dict__)
                    else:
                        conn.hset(next_category.get_key(), mapping=next_category.__dict__)
            if cat_cntr % 1000 == 0:
                print(str(cat_cntr) + " categories loaded")

    xml_file.close()
    print(str(cat_cntr) + " categories loaded")


if '__main__' == __name__:
    main()
