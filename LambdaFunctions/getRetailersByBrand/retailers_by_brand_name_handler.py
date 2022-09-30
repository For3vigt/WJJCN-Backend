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
    # curr1 = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    # curr1.execute("SELECT id FROM brand WHERE brand.name = " + parameter)
    # results1 = curr1.fetchall()
    # json_result1 = json.dumps(results1)

    # curr2 = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    # curr2.execute("SELECT * FROM retailer JOIN brand_retailer ON brand_retailer.brand_id = " + json_result1)
    # results2 = curr2.fetchall()
    # json_result2 = json.dumps(results2)
    # print(json_result2)
    # return json_result2

    # curr3 = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    # curr3.execute("    select retailer.* from retailer INNER JOIN brand_retailer ON retailer.id=brand_retailer.retailer_id INNER JOIN brand ON brand_retailer.brand_id=brand.id WHERE brand.name=" + parameter)
    # results3 = curr3.fetchall()
    # json_result3 = json.dumps(results3)
    # print(json_result3)

    return event['pathParameters']['param1']



#lambda_handler()