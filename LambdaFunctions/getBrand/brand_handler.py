from http.client import ImproperConnectionState
import psycopg2
import psycopg2.extras
import json

host = "woc.cdtpo0oxyy5p.eu-central-1.rds.amazonaws.com"
username = "postgres"
password = "CgnB!#HSrhKqG8&K"
database = "woc"

conn = psycopg2.connect(
    host = host,
    database = database,
    user = username,
    password = password
)

def lambda_handler(event, context):
    curr = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    curr.execute("select * from brand")
    results = curr.fetchall()
    json_result = json.dumps(results)
    print(json_result)
    return json_result

#lambda_handler()