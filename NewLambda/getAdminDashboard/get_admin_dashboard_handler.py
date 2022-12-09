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
brandscol = mydb["brands"]
logscol = mydb["logs"]
usercol = mydb["user"]
admincol = mydb["admin_page_settings"]

def lambda_handler(event, context):
    # Check if token is sent
    if event.get('token', None) == None:
        return {
            'statuscode': 400,
            'body': json.dumps('token is not defined!')
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

    returnarray = {}
    # Check if the 2 tokens are equal
    if (token == token_from_website):
        # Get all brands with their retailer name
        brandsdoc = brandscol.find()
        brands_json = json.loads(json_util.dumps(brandsdoc))

        # Loop brands 
        allBrandArray = []
        for brand in brands_json:
            retailers = []
            # Loop brands retailer
            for retailerId in brand["retailers"]:
                singleretailersql = {"_id": ObjectId(retailerId["$oid"])}
                singleretailerdoc = retailerscol.find(singleretailersql)
                single_retailer_json = json.loads(json_util.dumps(singleretailerdoc))
                
                # Get retailer name and append it in the array
                tempSingleRetailer = {"name": single_retailer_json[0]["name"]}
                retailers.append(tempSingleRetailer)

            # Append brand with retailers names
            tempBrand = {"_id": brand["_id"], "name": brand["name"], "retailers": retailers}
            allBrandArray.append(tempBrand)
        


        # Get all retailers 
        retailersdoc = retailerscol.find()
        retailers_json = json.loads(json_util.dumps(retailersdoc))
        

        # Get all logs
        logsdoc = logscol.find()
        logs_json_result = json.loads(json_util.dumps(logsdoc))
        
        # Loop logs
        allLogsArray = []
        for log in logs_json_result:
            retailersql = {"_id": ObjectId(log["retailer"]["$oid"])}
            retailersdoc = retailerscol.find(retailersql)
            retailer_json_result = json.loads(json_util.dumps(retailersdoc))
            
            # Append the return with the retailer name
            templog = {"_id": log["_id"], "date_run": log["date_run"], "steps": log["steps"], "retailer": retailer_json_result[0]["name"]} 
            allLogsArray.append(templog)

        # Get All admin setting 
        admindoc = admincol.find()
        admin_json_result = json.loads(json_util.dumps(admindoc))

        returnarray = {"allBrands": allBrandArray, "allRetailers": retailers_json, "allLogs": allLogsArray, "allAdminSettings": admin_json_result}
        return (returnarray)

    # If tokens are not equal return 401
    return {
        'statuscode': 401,
        'body': json.dumps('Token incorrect!')
    }   

#lambda_handler()