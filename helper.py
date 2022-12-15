
import os
import google.oauth2.id_token
import pymysql
import requests

from google.cloud import datastore
from google.auth.transport import requests as googleRequests
from flask import json
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
    return claims, error_message, valid_token


def cloud_sql_insert(query):
    url = "https://us-central1-adassigment.cloudfunctions.net/sql_cloud_insert"
    req = requests.post(url, json={
        "query": query,
    }, headers={"Content-type": "application/json", "Accept": "text/plain"})
    result = req.content
    print(result)
    if result != b'Error: could not handle the request\n':
        return result
    else:
        return None


def cloud_sql_query(query):
    url = "https://europe-west2-adassigment.cloudfunctions.net/helloworld"
    req = requests.post(url, json={
        "query": query,
    }, headers={"Content-type": "application/json", "Accept": "text/plain"})
    result = req.content
    print(result)
    if result != b'Error: could not handle the request\n':
        return json.loads(result)
    else:
        return None


def get_sql_games_from_email(email, name):
    user_id = get_sql_user_id_from_email(email)
    if user_id is None:
        create_sql_user(email, name)
        return None
    print(user_id)
    query = 'SELECT VIDEOGAME_ID from USER_VIDEOGAME WHERE user_id = \'' + str(user_id[0][0]) + '\''
    return cloud_sql_query(query)


def find_sql_game_from_id_list(list_id):
    list_game = []
    for game_id in list_id:
        list_game.append(find_sql_game_from_id(game_id[0]))
    return list_game


def get_sql_user_id_from_email(email):
    query = 'SELECT USER_ID from USER_TABLE WHERE email = \'' + email + '\''
    return cloud_sql_query(query)


def create_sql_user(email, name):
    query = 'INSERT INTO USER_TABLE  ( email, name ) VALUES ( \''+email+'\', \''+name+'\');'
    return cloud_sql_insert(query)


def find_sql_game_from_name(name):
    query = 'select * from VIDEOGAME WHERE VIDEOGAME_NAME =     \''+name+'\''
    return cloud_sql_query(query)


def find_sql_game_from_id(id):

    query = 'select * from VIDEOGAME WHERE VIDEOGAME_ID = '+str(id)
    return cloud_sql_query(query)
