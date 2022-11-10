from http.client import ImproperConnectionState
import json
import os
import pymongo
import bson.json_util as json_util
myclient = pymongo.MongoClient(os.environ.get('db_host'))
mydb = myclient[os.environ.get("db")]
mycol = mydb["brand_retailer_product"]

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
    
    mysql = { "brand": brand, "retailer": retailer}
    mydoc = mycol.find(mysql)
    json_result = json.loads(json_util.dumps(mydoc))
    
    return(json_result)
#lambda_handler()