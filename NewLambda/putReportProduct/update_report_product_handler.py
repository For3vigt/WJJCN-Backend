from http.client import ImproperConnectionState
from bson.objectid import ObjectId
import json
import jwt
import os
import pymongo
import datetime
import bson.json_util as json_util
import hashlib

myclient = pymongo.MongoClient(os.environ.get('db_host'))
mydb = myclient[os.environ.get("db")]
productcol = mydb["products"]

def lambda_handler(event, context):
    if event.get('product', None) == None:
        return {
            'statuscode': 400,
            'body': json.dumps('product is not defined!')
        }
    
    product = event["product"]

    new_values = {"reported": True}
    productcol.find_one_and_update(
        {'_id' : ObjectId(product["_id"]["$oid"])},
        {'$set': new_values},
        upsert=True
    )

    return {
        'statuscode': 200,
        'body': json.dumps('Product reported!')
    }    

#lambda_handler()