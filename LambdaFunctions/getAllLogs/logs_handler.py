from http.client import ImproperConnectionState
import json
import os
import pymongo
import jwt
import datetime
import bson.json_util as json_util
from bson.objectid import ObjectId

myclient = pymongo.MongoClient(os.environ.get('db_host'))
mydb = myclient[os.environ.get("db")]
logscol = mydb["logs"]
usercol = mydb["user"]
retailercol = mydb["retailers"]

def lambda_handler(event, context):
    #token checken 
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
        logsdoc = logscol.find()
        logs_json_result = json.loads(json_util.dumps(logsdoc))
        
        returnarray = []
        for index, log in enumerate(logs_json_result):
            retailersql = {"_id": ObjectId(log["retailer"]["$oid"])}
            retailerdoc = retailercol.find(retailersql)
            retailer_json_result = json.loads(json_util.dumps(retailerdoc))
            
            templog = {"_id": log["_id"], "date_run": log["date_run"], "steps": log["steps"], "retailer": retailer_json_result[0]["name"]} 
            returnarray.append(templog)
        return(returnarray)
        
    return {
        'statuscode': 401,
        'body': json.dumps('Token incorrect!')
    }   

    

#lambda_handler()