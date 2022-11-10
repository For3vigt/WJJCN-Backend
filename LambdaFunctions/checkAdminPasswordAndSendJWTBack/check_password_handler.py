from http.client import ImproperConnectionState
import json
import jwt
import os
import pymongo
import bson.json_util as json_util
import hashlib


myclient = pymongo.MongoClient(os.environ.get('db_host'))
mydb = myclient[os.environ.get("db")]
mycol = mydb["user"]

def lambda_handler(event, context):
    mydoc = mycol.find()
    json_result = json.loads(json_util.dumps(mydoc))

    passwd = event['password']
    salt = os.environ.get("salt")
    salted_pass = passwd+salt
    
    hashed_password_from_website = hashlib.sha256(salted_pass.encode()).hexdigest()
    hashed_password_from_database = json_result[0]["password_hashed"]

    # get hashed password from json_result. 
    # check if database password is same password from website
    if (hashed_password_from_website == hashed_password_from_database):
        # make JWT with secret in os.environ.get("SECRET_KEY") return JWT
        token = jwt.encode({
            'ID': '1'
        }, 
        os.environ.get("JWT_SECRET"), 
        algorithm='HS256')
        
        return {
        'statuscode': 200,
        'token': token
        }   

    return {
        'statuscode': 401,
        'body': json.dumps('Password is not correct!')
    }

#lambda_handler()