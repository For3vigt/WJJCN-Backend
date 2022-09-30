from http.client import ImproperConnectionState
import psycopg2
import psycopg2.extras
import json
import os

conn = psycopg2.connect(
    host = os.environ.get('db_host'),
    database = os.environ.get('db'),
    user = os.environ.get('db_user'),
    password = os.environ.get('db_pass')
)

def lambda_handler(event, context):
    curr = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    curr.execute("select * from product")
    results = curr.fetchall()
    json_result = json.dumps(results)
    print(json_result)
    return json_result

#lambda_handler()