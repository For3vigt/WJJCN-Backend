from http.client import ImproperConnectionState
import json
import os
from bson.objectid import ObjectId
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

    # Chech if retailer is sent
    if event.get('retailer', None) == None:
        return {
            'statuscode': 400,
            'body': json.dumps('retailer is not defined!')
        }
        
    brand = '{}'.format(event['brand'])
    retailer = '{}'.format(event['retailer'])
    
    # Find brand by name
    brandsql = { "name": brand }
    branddoc = brandcol.find(brandsql)
    brand_json_result = json.loads(json_util.dumps(branddoc))
    
    # Find retailer by name
    retailersql = {"name": retailer}
    retailerdoc = retailercol.find(retailersql)
    retailer_json_result = json.loads(json_util.dumps(retailerdoc))
    
    # Find products with brand ID and retailer ID
    productsql = {"brand": ObjectId(brand_json_result[0]["_id"]["$oid"]), "retailer": ObjectId(retailer_json_result[0]["_id"]["$oid"])}
    productdoc = productcol.find(productsql)
    product_json_result = json.loads(json_util.dumps(productdoc))

    returnarray = []
    # Loop products and Append product with brand and retailer name
    for product in product_json_result:
        tempproduct = {"_id": product["_id"], "brand": brand_json_result[0]["name"], "retailer": retailer_json_result[0]["name"], "product": product["name"], "product_url": product["product_url"], "history": product["history"]}
        returnarray.append(tempproduct)
   
    return (returnarray)

#lambda_handler()