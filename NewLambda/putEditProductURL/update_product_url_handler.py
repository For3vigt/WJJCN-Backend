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
usercol = mydb["user"]
productcol = mydb["products"]

def lambda_handler(event, context):
    # Check if token is sent
    if event.get('token', None) == None:
        return {
            'statuscode': 400,
            'body': json.dumps('token is not defined!')
        }

    # Check if product is sent
    if event.get('product', None) == None:
        return {
            'statuscode': 400,
            'body': json.dumps('product is not defined!')
        }
        
    # Get the hashed password from the DB
    mydoc = usercol.find()
    json_result = json.loads(json_util.dumps(mydoc))
    hashed_password_from_database = json_result[0]["password_hashed"]
    
    # create token with the password from the database. 
    token = jwt.encode({
        'id': '1',
        'date': datetime.datetime.now().strftime("%m-%d-%Y"),
        'hashed_password': hashed_password_from_database
    }, 
    os.environ.get("JWT_SECRET"), 
    algorithm='HS256')
    
    token_from_website = event["token"]

    # Check JWT token from DB and Website
    if (token == token_from_website):
        product = event["product"]
        # Update product url 
        productcol.find_one_and_update(
            { "_id": ObjectId(product["_id"]["$oid"])},
            {'$set': {"product_url": product["product_url"]}},
            upsert=True
        )

        return {
            'statuscode': 200,
            'body': json.dumps('All values changend!')
        } 
    
    return {
        'statuscode': 401,
        'body': json.dumps('Token incorrect!')
    }   

#lambda_handler()