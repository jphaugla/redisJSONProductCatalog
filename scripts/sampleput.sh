# curl -X PUT -H "Content-Type: application/json" -d '{"status":"great"}' http://localhost:5000/key1
# this does not work as went away from product index
# curl -X GET -H "Content-Type: application/json"  http://localhost:5000/prod:57106
# curl -X GET -H "Content-Type: application/json"  http://localhost:5000/search?search_string=iPhone
# curl -X GET -H "Content-Type: application/json"  http://localhost:5000/search?search_string=iPhone%20XS:1200983
#  valid below here
#  gets all the information about a category
# curl -X GET -H "Content-Type: application/json"  http://localhost:5000/category?show_category="Ink%20Cartridges"
# curl -X GET -H "Content-Type: application/json"  http://localhost:5000/parent_category?parent_category="Printing%20Supplies"
# curl -X GET -H "Content-Type: application/json"  'http://localhost:5000/search?search_column=m_supplier_name&search_string=Lexmark'
# curl -X PUT -H "Content-Type: application/json" -d '{ "Date_Added": 20080203000000, "Limited": "No", "catid": 2927, "country_market": "US", "ean_upc": 999992942972, "ean_upc_is_approved": 0, "high_pic": "http://images.icecat.biz/img/norm/high/1397513-9531.jpg", "high_pic_height": 460, "high_pic_size": 72523, "high_pic_width": 460, "m_prod_id": "BNB-24", "model_name": "24 Capacity Nylon CD / DVD Super Binder", "on_market": 1, "path": "export/freexml.int/NL/1397513.xml", "prod_id": "BNB-24", "product_id": 1397513, "product_view": 6175, "quality": "ICECAT", "supplier_id": 148, "ttl": -1, "updated": 20190506005832 }' http://localhost:5000/
curl -X DELETE http://localhost:5000/mprodid:BNB-24:prodid:1397513:supplyid:148
