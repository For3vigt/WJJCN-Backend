from http.client import ImproperConnectionState
import json
import os
import pymongo
import bson.json_util as json_util
import jwt
import datetime
from bson.objectid import ObjectId
import hashlib


myclient = pymongo.MongoClient(os.environ.get('db_host'))
mydb = myclient[os.environ.get("db")]
brandscol = mydb["brands"]
usercol = mydb["user"]

def lambda_handler(event, context):
    # Check if token is send 
    if event.get('token', None) == None:
        return {
            'statuscode': 400,
            'body': json.dumps('token is not defined!')
        }
    
    # Check if token is send 
    if event.get('name', None) == None:
        return {
            'statuscode': 400,
            'body': json.dumps('name is not defined!')
        }
    
    # Check if token is send 
    if event.get('retailers', None) == None:
        return {
            'statuscode': 400,
            'body': json.dumps('retailers is not defined!')
        }

    # Get hashed user password from DB
    userdoc = usercol.find()
    user_json_result = json.loads(json_util.dumps(userdoc))
    hashed_password_from_database = user_json_result[0]["password_hashed"]

    # Create token with hashed pass from DB
    token = jwt.encode({
        'id': '1',
        'date': datetime.datetime.now().strftime("%m-%d-%Y"), 
        'hashed_password': hashed_password_from_database
    }, 
    os.environ.get("JWT_SECRET"), 
    algorithm='HS256')
    
    token_from_website = event["token"]

    # Check if the 2 tokens are equal
    if (token == token_from_website):
        # Collect the data from event
        brandName = '{}'.format(event['name'])
        brandRetailers = event["retailers"]
        
        # Refactor ids into ObjectIds
        retailerObjectId = []
        for retailerId in brandRetailers:
            retailerObjectId.append(ObjectId(retailerId))
            
        branddict = { "name": brandName, "retailers": retailerObjectId }

        newBrand = brandscol.insert_one(branddict)
        newBrand_json = json.loads(json_util.dumps(newBrand.inserted_id))
        return (newBrand_json)


    # If tokens are not equal return 401
    return {
        'statuscode': 401,
        'body': json.dumps('Token incorrect!')
    }   


    

#lambda_handler()