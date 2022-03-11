#!/bin/python
from flask import Flask, jsonify, request, render_template, Response, json
from flask_bootstrap import Bootstrap
import redis
from redis.commands.json.path import Path
from redis import ResponseError
from Product import Product

from os import environ

from redis.commands.search.field import TextField, TagField, NumericField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType


app = Flask(__name__)
app.debug = True
bootstrap = Bootstrap()
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
#  if environment is set to write to
#  jason change the index type and the field prefix
#  for JSON the field prefix is $.   for hash there is none
if environ.get('WRITE_JSON') is not None and environ.get('WRITE_JSON') == "true":
    useIndexType = IndexType.JSON
    fieldPrefix = "$."
else:
    useIndexType = IndexType.HASH
    fieldPrefix = ""

db = redis.StrictRedis(redis_server, redis_port, charset="utf-8", decode_responses=True)  # connect to server
print("beginning of appy.py now")

categoryDefinition = IndexDefinition(prefix=['Category:'], index_type=useIndexType)
categorySCHEMA = (
    # TextField(fieldPrefix + "LowPic", as_name='LowPic', no_stem=True, no_index=True),
    # TextField(fieldPrefix + "ThumbPic", as_name='ThumbPic', no_stem=True, no_index=True),
    TextField(fieldPrefix + "Name", as_name='Name'),
    TextField(fieldPrefix + "ParentCategoryName", as_name='ParentCategoryName')
)

productDefinition = IndexDefinition(prefix=['mprodid:', 'prodid:'], index_type=useIndexType)
productSCHEMA = (
    TextField(fieldPrefix + "product_id", as_name='product_id', no_stem=True),
    # path and updated not needed
    # TextField(fieldPrefix + "path", as_name='path', no_stem=True),
    # TextField(fieldPrefix + "updated", as_name='updated', no_stem=True),
    TextField(fieldPrefix + "quality", as_name='quality', no_stem=True),
    TextField(fieldPrefix + "supplier_id", as_name='supplier_id', no_stem=True),
    TextField(fieldPrefix + "prod_id", as_name='prod_id', no_stem=True),
    TextField(fieldPrefix + "catid", as_name='catid', no_stem=True),
    TextField(fieldPrefix + "m_prod_id", as_name='m_prod_id', no_stem=True),
    TextField(fieldPrefix + "ean_upc", as_name='ean_upc', no_stem=True),
    TagField(fieldPrefix + "country_market", separator=";", as_name='country_market'),
    TextField(fieldPrefix + "model_name", as_name='model_name', no_stem=True),
    TextField(fieldPrefix + "product_view", as_name='product_view', no_stem=True),
    TextField(fieldPrefix + "m_supplier_id", as_name='m_supplier_id', no_stem=True),
    TextField(fieldPrefix + "m_supplier_name", as_name='m_supplier_name'),
    # TextField(fieldPrefix + "high_pic", as_name='high_pic', no_stem=True, no_index=True),
    # NumericField(fieldPrefix + "high_pic_width", as_name='high_pic_width'),
    # NumericField(fieldPrefix + "high_pic_height", as_name='high_pic_height'),
    # NumericField(fieldPrefix + "high_pic_size", as_name='high_pic_size'),
    TagField(fieldPrefix + "ean_upc_is_approved", separator=";", as_name='ean_upc_is_approved'),
    # TextField(fieldPrefix + "Date_Added", as_name='date_added', no_stem=True),
    TextField(fieldPrefix + "category_name", as_name='category_name'),
    TextField(fieldPrefix + "parent_category_name", as_name='parent_category_name')
)

print("before try on product")
try:
    print("creating Product index")
    db.ft(index_name="Product").create_index(productSCHEMA, definition=productDefinition)
except ResponseError:
    db.ft(index_name="Product").info()




print("before try on category")
try:
    print("creating Category index")
    db.ft(index_name="Category").create_index(categorySCHEMA, definition=categoryDefinition)

except ResponseError:
    db.ft(index_name="Category").info()


def isInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


@app.route('/', defaults={'path': ''}, methods=['PUT', 'GET'])
@app.route('/<path:path>', methods=['PUT', 'GET', 'DELETE'])
def home(path):
    print("the request method is " + request.method + " path is " + path)
    if request.method == 'PUT':
        # if prod_idx is set it is a replace
        # if proc_idx is not set, is insert
        print('in PUT')
        event = request.json
        print('event is %s ' % event)
        nextProduct = Product(**event)
        nextProduct.set_key()
        # event['updated'] = int(time.time())
        # db.hmset(path, event)
        if environ.get('WRITE_JSON') is not None and environ.get('WRITE_JSON') == "true":
            db.json().set(nextProduct.key_name, Path.rootPath(), nextProduct.__dict__)
        else:
            db.hset(nextProduct.key_name, mapping=nextProduct.__dict__)
        return_string = jsonify(nextProduct.__dict__, 201)

    elif request.method == 'DELETE':
        return_status = db.delete(path)
        print("delete with path = " + path + " and status of " + str(return_status))
        return_string = jsonify(str(return_status), 201)

    elif request.method == 'GET':
        print("GET Method with path " + path)
        if path == 'search':
            search_column = request.args.get("search_column")
            print("search column is " + search_column)
            search_str = request.args.get("search_string")
            print("search string is " + search_str)
            productSearch = "@" + str(search_column) + ":" + str(search_str)
            print("productSearch is " + productSearch)
            productReturn = db.ft(index_name="Product").search(productSearch)
            print("number returned is " + str(productReturn.total))
            productResults =[]
            for i in range(min(productReturn.total-1, 9)):
                results = productReturn.docs[i].json
                final_results = json.loads(results)
                # productResults.append(productReturn.docs[i].json)
                productResults.append(final_results)
            return_string = jsonify(productResults, 200)
        # category passed in will be Category name, return Category attributes
        elif path == 'category':
            get_category = request.args.get("show_category")
            print("reporting category is ", get_category)
            #  retrieve the category index using the passed in category name
            #  pull this from the zCategoryName sorted set holding category name and category id separated by colon
            catSearch = "@Name:" + get_category
            catReturn = db.ft(index_name="Category").search(catSearch)
            print("number returned is " + str(catReturn.total))
            return_string = catReturn.docs[0].json
        elif path == 'parent_category':
            get_parent = request.args.get("parent_category")
            print("reporting category is ", get_parent)
            #  retrieve the category index using the passed in category name
            #  pull this from the zCategoryName sorted set holding category name and category id separated by colon
            catSearch = "@ParentCategoryName:" + get_parent
            catReturn = db.ft(index_name="Category").search(catSearch)
            print("number returned is " + str(catReturn.total))
            catResults = []
            for i in range(min(catReturn.total - 1, 9)):
                results = catReturn.docs[i].json
                final_results = json.loads(results)
                # catResults.append(productReturn.docs[i].json)
                catResults.append(final_results)
            return_string = jsonify(catResults, 200)
        elif path == 'prod':
            get_prod = request.args.get("prodkey")
            if environ.get('WRITE_JSON') is not None and environ.get('WRITE_JSON') == "true":
                return_value = db.json().get(get_prod)
            else:
                return_value = db.get(get_prod)
            return_string = jsonify(return_value,200)
        else:
             print("in the GET before call to index.html")
             response=app.send_static_file('index.html')
             response.headers['Content-Type']='text/html'
             return_string = response

    return return_string


if __name__ == "__main__":
    app.run(host='0.0.0.0')
