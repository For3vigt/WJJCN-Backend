from http.client import ImproperConnectionState
import json
from bson.objectid import ObjectId
import os
import pymongo
import bson.json_util as json_util

myclient = pymongo.MongoClient(os.environ.get('db_host'))
mydb = myclient[os.environ.get("db")]
brandcol = mydb["brands"]
retailercol = mydb["retailers"]
productcol = mydb["products"]

def lambda_handler(event, context):
    # Chech if brand is sent
    if event.get('brand', None) == None:
        return {
            'statuscode': 400,
            'body': json.dumps('brand is not defined!')
        }
    
    # Get brand by brand name
    brandname = '{}'.format(event['brand'])
    brandsql = { "name": brandname }
    branddoc = brandcol.find(brandsql)
    brand_json_result = json.loads(json_util.dumps(branddoc))
    
    returnarray = []
    
    # Loop retailers form brand
    for index, retailer in enumerate(brand_json_result[0]["retailers"]):
        # Get retailer by ID
        retailersql = {"_id": ObjectId(retailer["$oid"])}
        retailerdoc = retailercol.find(retailersql)
        retailer_json_result = json.loads(json_util.dumps(retailerdoc))
        
        tempBrandAndRetailer = {"brand": brand_json_result[0]["name"], "retailer": retailer_json_result[0]["name"], "products": []}
        returnarray.append(tempBrandAndRetailer)
        
        productsql = {"brand": ObjectId(brand_json_result[0]["_id"]["$oid"]), "retailer": ObjectId(retailer["$oid"])}
        productdoc = productcol.find(productsql)
        product_json_result = json.loads(json_util.dumps(productdoc))
        
        products = []
        for product in product_json_result:
            tempProduct = {"name": product["name"], "score": product["history"][-1]["score"]}
            products.append(tempProduct)
        
        returnarray[index]["products"] = products
        
    return(returnarray)
    
#lambda_handler()