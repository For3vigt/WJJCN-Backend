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
    if event.get('brand', None) == None:
        return {
            'statuscode': 400,
            'body': json.dumps('brand is not defined!')
        }

    if event.get('retailer', None) == None:
        return {
            'statuscode': 400,
            'body': json.dumps('retailer is not defined!')
        }
        
    brand = '{}'.format(event['brand'])
    retailer = '{}'.format(event['retailer'])
    
    brandsql = { "name": brand }
    branddoc = brandcol.find(brandsql)
    brand_json_result = json.loads(json_util.dumps(branddoc))
    
    retailersql = {"name": retailer}
    retailerdoc = retailercol.find(retailersql)
    retailer_json_result = json.loads(json_util.dumps(retailerdoc))
    
    productsql = {"brand": ObjectId(brand_json_result[0]["_id"]["$oid"]), "retailer": ObjectId(retailer_json_result[0]["_id"]["$oid"])}
    productdoc = productcol.find(productsql)
    product_json_result = json.loads(json_util.dumps(productdoc))

    returnarray = []
    for index, product in enumerate(product_json_result):
        tempproduct = {"_id": product["_id"],"brand": brand_json_result[0]["name"], "retailer": retailer_json_result[0]["name"], "scrape_date": product["scrape_date"], "score": product["score"], "product": product["product"], "product_brand": product["product_brand"], "product_scraped": product["product_scraped"]}
        returnarray.append(tempproduct)
   
    return (returnarray)

#lambda_handler()