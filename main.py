import datetime
import json
import os

from pymongo import MongoClient
from bson.json_util import dumps


from flask import Flask, render_template, request, jsonify

from google.auth.transport import requests
from google.cloud import datastore
import google.oauth2.id_token
import pymysql

db_user = os.environ.get('CLOUD_SQL_USERNAME')
db_password = os.environ.get('CLOUD_SQL_PASSWORD')
db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')


firebase_request_adapter = requests.Request()

# [START gae_python38_datastore_store_and_fetch_user_times]
# [START gae_python3_datastore_store_and_fetch_user_times]
datastore_client = datastore.Client()

# [END gae_python3_datastore_store_and_fetch_user_times]
# [END gae_python38_datastore_store_and_fetch_user_times]
app = Flask(__name__)


cluster = MongoClient("mongodb+srv://paolomostardi:tMfWyN51mysRllox@cluster0.aoiwmkj."
                      + "mongodb.net/?retryWrites=true&w=majority")
db = cluster["ADunit"]
collection = db["Students"]


def get_mongodb_items():
    # Search data from Mongodb
    # create queries

    myCursor = collection.find({ "Gender": "0" })
    list_cur = list(myCursor)
    print(list_cur)
    json_data = dumps(list_cur)
    return json_data

def store_mongodb(Unittitle, Unitleader, content, dateCreated, thumbnail):
  # Write to MongoDB
  json_data = {"Unit title": Unittitle, "Unit leader": Unitleader, "dateCreated": dateCreated, "thumbnail": thumbnail, "content": content}
  collection.insert_one(json_data)

# [START gae_python38_datastore_store_and_fetch_user_times]
# [START gae_python3_datastore_store_and_fetch_user_times]
def store_time(email, dt):
    entity = datastore.Entity(key=datastore_client.key('User', email, 'visit'))
    entity.update({
        'timestamp': dt
    })

    datastore_client.put(entity)


def fetch_times(email, limit):
    ancestor = datastore_client.key('User', email)
    query = datastore_client.query(kind='visit', ancestor=ancestor)
    query.order = ['-timestamp']

    times = query.fetch(limit=limit)

    return times


@app.route('/')
def root():
    # Verify Firebase auth.
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None

    if id_token:
        try:
            # Verify the token against the Firebase Auth API. This example
            # verifies the token on each page load. For improved performance,
            # some applications may wish to cache results in an encrypted
            # session store (see for instance
            # http://flask.pocoo.org/docs/1.0/quickstart/#sessions).
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)

            store_time(claims['email'], datetime.datetime.now())
            times = fetch_times(claims['email'], 10)

        except ValueError as exc:
            # This will be raised if the token is expired or any other
            # verification checks fail.
            error_message = str(exc)

    return render_template(
        'index.html',
        user_data=claims, error_message=error_message, times=times,games=sql())



@app.route('/yee')
def yee():
    return "you did it paolo"

@app.route('/display')
def display():
    jResponse = get_mongodb_items()
    data= json.loads(jResponse)
    print(jsonify(data))
    print("success")
    return jsonify(data)

@app.route('/sql')
def sql():
    # When deployed to App Engine, the `GAE_ENV` environment variable will be
    # set to `standard`
    if os.environ.get('GAE_ENV') == 'standard':
        # If deployed, use the local socket interface for accessing Cloud SQL
        unix_socket = '/cloudsql/{}'.format(db_connection_name)
        cnx = pymysql.connect(user=db_user, password=db_password,
                              unix_socket=unix_socket, db=db_name)
    else:
        # If running locally, use the TCP connections instead
        # Set up Cloud SQL Proxy (cloud.google.com/sql/docs/mysql/sql-proxy)
        # so that your application can use 127.0.0.1:3306 to connect to your
        # Cloud SQL instance
        host = '127.0.0.1'
        cnx = pymysql.connect(user=db_user, password=db_password,
                              host=host, db=db_name)

    with cnx.cursor() as cursor:
        cursor.execute('select * from VIDEOGAME;')
        result = cursor.fetchall()
        current_msg = result[0][0]
    cnx.close()

    return str(result)
# [END gae_python37_cloudsql_mysql]

@app.route('/uploadfile')
def uploadfile():
    # Verify Firebase auth.
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None

    if id_token:
        try:
            # Verify the token against the Firebase Auth API. This example
            # verifies the token on each page load. For improved performance,
            # some applications may wish to cache results in an encrypted
            # session store (see for instance
            # http://flask.pocoo.org/docs/1.0/quickstart/#sessions).
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)

            store_time(claims['email'], datetime.datetime.now())
            times = fetch_times(claims['email'], 5)

        except ValueError as exc:
            # This will be raised if the token is expired or any other
            # verification checks fail.
            error_message = str(exc)

    return render_template('uploadfile.html',user_data=claims, error_message=error_message, times=times)


def local_root_helper(request):
    return root()


def sql_helper(request):
    print("hello")
    return sql()


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.

    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)