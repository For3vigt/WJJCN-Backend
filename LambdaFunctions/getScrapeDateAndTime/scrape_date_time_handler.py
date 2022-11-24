from http.client import ImproperConnectionState
from bson.objectid import ObjectId
import json
import jwt
import os
import pymongo
import bson.json_util as json_util
import datetime

myclient = pymongo.MongoClient(os.environ.get('db_host'))
mydb = myclient[os.environ.get("db")]
usercol = mydb["user"]
admincol = mydb["admin_page_settings"]

def lambda_handler(event, context):
    if event.get('token', None) == None:
        return {
            'statuscode': 400,
            'body': json.dumps('token is not defined!')
        }

    userdoc = usercol.find()
    user_json_result = json.loads(json_util.dumps(userdoc))
    hashed_password_from_database = user_json_result[0]["password_hashed"]

    token = jwt.encode({
        'id': '1',
        'date': datetime.datetime.now().strftime("%m-%d-%Y"), 
        'hashed_password': hashed_password_from_database
    }, 
    os.environ.get("JWT_SECRET"), 
    algorithm='HS256')
    
    token_from_website = event["token"]

    if (token == token_from_website):
        mydoc = admincol.find()
        admin_json_result = json.loads(json_util.dumps(mydoc))
        
        return(admin_json_result)
    
    return {
        'statuscode': 401,
        'body': json.dumps('Token incorrect!')
    }   



#lambda_handler()