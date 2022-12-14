
import os
import google.oauth2.id_token
import pymysql
import requests

from google.cloud import datastore
from google.auth.transport import requests as googleRequests



firebase_request_adapter = googleRequests.Request()
db_user = os.environ.get('CLOUD_SQL_USERNAME')
db_password = os.environ.get('CLOUD_SQL_PASSWORD')
db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')


def authenticateUser(id_token):
    error_message = None
    claims = None
    times = None
    valid_token = False
    if id_token:
        try:
            # Verify the token against the Firebase Auth API.
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)
            valid_token = True

        except ValueError as exc:
            # This will be raised if the token is expired or any other
            # verification checks fail.
            error_message = str(exc)
    return (claims, error_message,valid_token)


def sql_request(query):
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
        cursor.execute(query)
        result = cursor.fetchall()
        current_msg = result[0][0]
    cnx.close()

    return str(result)
    # [END gae_python37_cloudsql_mysql]


def cloud_sql_query(query):
        url = "https://europe-west2-adassigment.cloudfunctions.net/helloworld"
        req = requests.post(url, json={
            "query": query,
        }, headers={"Content-type": "application/json", "Accept": "text/plain"})
        return (req.content)


def find_sql_user(name):
    query = 'select * from user WHERE VIDEOGAME_NAME = \'Tetris\''