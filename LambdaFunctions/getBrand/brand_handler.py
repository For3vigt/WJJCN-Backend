from http.client import ImproperConnectionState
import json
import os
import pymongo
import bson.json_util as json_util
myclient = pymongo.MongoClient(os.environ.get('db_host'))
mydb = myclient[os.environ.get("db")]
mycol = mydb["brands"]

def lambda_handler(event, context):
    mydoc = mycol.find()
    json_result = json.loads(json_util.dumps(mydoc))
    
    return(json_result[0]["Brands"])
#lambda_handler()