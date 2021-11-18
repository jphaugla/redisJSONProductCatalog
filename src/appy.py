#!/bin/python
from flask import Flask, jsonify
from flask_bootstrap import Bootstrap
from flask import request
from flask_nav import Nav
from flask_nav.elements import Navbar, View
import redis
import time
from redis import ResponseError

from os import environ

from redis.commands.search.field import TextField, TagField, NumericField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search import Search

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
    TextField("$.lowpic", as_name='lowpic'),
    TextField("$.thumbpic", as_name='thumbpic'),
    TextField("$.name", as_name='name')
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
    TextField("$.category_name", as_name='category_name')
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

nav = Nav()
topbar = Navbar('',
                View('Home', 'index'),
                View('Aggregations', 'show_agg'),
                )
nav.register_element('top', topbar)

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
        if path == 'NEW':
            prod_idx = str(db.incr("prod_highest_idx"))
            path = "prod:" + str(prod_idx)
            print("insert-new index is " + path)
        else:
            db.delete(path)  # remove old keys
            print("prod_idx exists so is a replace")
        event['updated'] = int(time.time())
        event['prod_idx'] = path
        # db.hmset(path, event)
        db.json().set(path, event)
        return_string = jsonify(event, 201)

    elif request.method == 'DELETE':
        return_status = db.delete(path)
        print("delete with path = " + path + " and status of " + str(return_status))
        return_string = jsonify(str(return_status), 201)

    elif request.method == 'GET':
        print("GET Method with path " + path)
        if path == 'search':
            search_str = request.args.get("search_string")
            print("search string is ", search_str)
            product_list = db.smembers("ProductModel:" + search_str)
            product_results = []
            for prod in product_list:
                print("prod is " + prod)
                product_record = db.hgetall(prod)
                product_results.append(product_record)
            return_string = jsonify(product_results, 200)

        # category passed in will be Category name, need to get the category index and pull products with category index
        elif path == 'category':
            get_category = request.args.get("show_category")
            print("reporting category is ", get_category)
            #  retrieve the category index using the passed in category name
            #  pull this from the zCategoryName sorted set holding category name and category id separated by colon
            category_key = "CategIDX:" + get_category
            product_list = db.smembers(category_key)
            product_results = []
            # print("product list is\n")
            # print(product_list)
            for prod in product_list:
                # print("prod is " + prod)
                # product_name = db.hget(prod, "model_name")
                product_record = db.hgetall(prod)
                product_results.append(product_record)
            return_string = jsonify(product_results, 200)

        elif not db.exists(path):
            return_string = "Error: thing doesn't exist"

        else:
            event = db.hgetall(path)
            print("got event back" + str(event))
            # put path in as product index
            event["prod_idx"] = path
            # cast integers accordingly, nested arrays, dicts not supported for now  :(
            dict_with_ints = dict((k,int(v) if isInt(v) else v) for k, v in event.items())
            # return json.dumps(dict_with_ints), 200
            return_string = jsonify(dict_with_ints, 200)

    return return_string


if __name__ == "__main__":
    app.run(host='0.0.0.0')
