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
mycol = mydb["user"]

def lambda_handler(event, context):
    if event.get('password', None) == None:
        return {
            'statuscode': 400,
            'body': json.dumps('password is not defined!')
        }
        
    if event.get('token', None) == None:
        return {
            'statuscode': 400,
            'body': json.dumps('token is not defined!')
        }
        
    mydoc = mycol.find()
    json_result = json.loads(json_util.dumps(mydoc))
    hashed_password_from_database = json_result[0]["password_hashed"]
    
    token = jwt.encode({
        'id': '1',
        'date': datetime.datetime.now().strftime("%m-%d-%Y"),
        'hashed_password': hashed_password_from_database
    }, 
    os.environ.get("JWT_SECRET"), 
    algorithm='HS256')
    
    token_from_website = event["token"]

    # Check JWT token
    if (token == token_from_website):
        passwd = event['password']
        salt = os.environ.get("salt")
        salted_pass = passwd+salt
        hashed_password_from_website = hashlib.sha256(salted_pass.encode()).hexdigest()
        
        new_values = {"password_hashed": hashed_password_from_website}
        mycol.find_one_and_update(
            {'_id' : ObjectId('636cc5dd6be34c12a045e089')},
            {'$set': new_values},
            upsert=True
        )

        return {
            'statuscode': 200,
            'body': json.dumps('Password changed!')
        }   
    
    return {
        'statuscode': 401,
        'body': json.dumps('Token incorrect!')
    }   

#lambda_handler()