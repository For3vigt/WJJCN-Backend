from http.client import ImproperConnectionState
import jwt
import os


def lambda_handler(event, context):
    token_from_website = event['token']
    token = jwt.encode({
        'ID': '1'
    }, 
    os.environ.get("JWT_SECRET"), 
    algorithm='HS256')

    if (token == token_from_website):
            return {
        'statuscode': 200,
        'body': True
        }
    
    return {
        'statuscode': 401,
        'body': False
    }

#lambda_handler()