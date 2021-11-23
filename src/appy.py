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
    redis_server = '10.0.1.35'
    print("no passed in redis server variable ")

if environ.get('REDIS_PORT') is not None:
    redis_port = int(environ.get('REDIS_PORT'))
    print("passed in redis port is " + str(redis_port))
else:
    redis_port = 13000
    print("no passed in redis port variable ")

db = redis.StrictRedis(redis_server, redis_port, charset="utf-8", decode_responses=True)  # connect to server
print("beginning of appy.py now")

categoryDefinition = IndexDefinition(prefix=['Category:'], index_type=IndexType.JSON)
categorySCHEMA = (
    TextField("$.LowPic", as_name='LowPic'),
    TextField("$.ThumbPic", as_name='ThumbPic'),
    TextField("$.Name", as_name='Name'),
    TextField("$.ParentCategoryName", as_name='ParentCategoryName')
)

productDefinition = IndexDefinition(prefix=['mprodid:', 'prodid:'], index_type=IndexType.JSON)
productSCHEMA = (
    TextField("$.product_id", as_name='product_id'),
    TextField("$.path", as_name='path'),
    TextField("$.updated", as_name='updated'),
    TextField("$.quality", as_name='quality'),
    TextField("$.supplier_id", as_name='supplier_id'),
    TextField("$.prod_id", as_name='prod_id'),
    TextField("$.catid", as_name='catid'),
    TextField("$.m_prod_id", as_name='m_prod_id'),
    TextField("$.ean_upc", as_name='ean_upc'),
    TagField("$.country_market", separator=";", as_name='country_market'),
    TextField("$.model_name", as_name='model_name'),
    TextField("$.product_view", as_name='product_view'),
    TextField("$.m_supplier_id", as_name='m_supplier_id'),
    TextField("$.m_supplier_name", as_name='m_supplier_name'),
    TextField("$.high_pic", as_name='high_pic'),
    # NumericField("$.high_pic_width", as_name='high_pic_width'),
    # NumericField("$.high_pic_height", as_name='high_pic_height'),
    # NumericField("$.high_pic_size", as_name='high_pic_size'),
    TagField("$.ean_upc_is_approved", separator=";", as_name='ean_upc_is_approved'),
    TextField("$.Date_Added", as_name='date_added'),
    TextField("$.category_name", as_name='category_name'),
    TextField("$.parent_category_name", as_name='parent_category_name')
)

print("before try on product")
try:
    db.ft(index_name="Product").info()
    print("checking for Product index")
except ResponseError:
    print("creating Product index")
    db.ft(index_name="Product").create_index(productSCHEMA, definition=productDefinition)

print("before try on category")
try:
    db.ft(index_name="Category").info()
    print("checking for Category index")
except ResponseError:
    print("creating Category index")
    db.ft(index_name="Category").create_index(categorySCHEMA, definition=categoryDefinition)

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
        db.json().set(nextProduct.key_name, Path.rootPath(), nextProduct.__dict__)
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

        elif not db.exists(path):
            return_string = "Error: thing doesn't exist"

    return return_string


if __name__ == "__main__":
    app.run(host='0.0.0.0')
