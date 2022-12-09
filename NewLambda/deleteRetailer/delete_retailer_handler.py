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
retailerscol = mydb["retailers"]
usercol = mydb["user"]

def lambda_handler(event, context):
    # Check if token is sent
    if event.get('token', None) == None:
        return {
            'statuscode': 400,
            'body': json.dumps('token is not defined!')
        }
    
    # Check if id is sent 
    if event.get('id', None) == None:
        return {
            'statuscode': 400,
            'body': json.dumps('id is not defined!')
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
        # Collect the data 
        retailerId = event['name']
        
        retailerquery = {"_id": retailerId}
        retailerscol.delete_one(retailerquery) 

        return {
            'statuscode': 200,
            'body': json.dumps('Retailer deleted!')
        }  


    # If tokens are not equal return 401
    return {
        'statuscode': 401,
        'body': json.dumps('Token incorrect!')
    }   


    

#lambda_handler()