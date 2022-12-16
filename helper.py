
import os
import google.oauth2.id_token
import pymysql
import requests
from datetime import datetime

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
    print("running sql query: ",result)
    if result != b'Error: could not handle the request\n':
        return json.loads(result)
    else:
        return None


def get_sql_games_from_email(email, name):
    user_id = get_sql_user_id_from_email(email)
    print("user id :",user_id)
    if user_id:
        query = 'SELECT VIDEOGAME_ID from USER_VIDEOGAME WHERE user_id = \'' + str(user_id[0][0]) + '\''
        return cloud_sql_query(query)
    create_sql_user(email, name)
    return None


def find_sql_game_from_id_list(list_id):
    list_game = []
    for game_id in list_id:
        game = find_sql_game_from_id(game_id[0])
        list_game.append(game[0])
    return list_game


def buy_game(user_id,game_id):
    user_credit = get_user_credit(user_id)
    print('user credit: ',user_credit)
    game_price = get_game_price(game_id)
    insert_success = insert_game_user_table(user_id, game_id)
    if user_credit >= game_price and insert_success:
        credit_update = update_user_credit(user_credit - game_price,user_id)
        print('stats after buying: ',user_credit,game_price,user_id,game_id,credit_update,insert_success)
        return True
    return False


def insert_game_user_table(user_id,game_id):
    date = datetime.today().strftime('%Y-%m-%d')
    query = 'INSERT INTO USER_VIDEOGAME  ( user_id, videogame_id,date_purchased ) VALUES ( \''+str(user_id)+'\', \''+str(game_id)+'\',\''+date+'\');'
    return cloud_sql_insert(query)


def game_already_bought(user_id, game_id):
    query = 'SELECT * FROM USER_VIDEOGAME'
    return cloud_sql_query(query)


def update_user_credit(user_credit,user_id):
    query = 'UPDATE USER_TABLE SET credit = '+str(user_credit)+' WHERE user_id = '+str(user_id)+';'
    return cloud_sql_insert(query)


def get_user_credit(user_id):
    query = 'SELECT credit from USER_TABLE WHERE user_id = ' + str(user_id)
    return cloud_sql_query(query)[0][0]


def get_game_price(game_id):
    query = 'SELECT PRICE from VIDEOGAME WHERE VIDEOGAME_ID = ' + str(game_id)
    return cloud_sql_query(query)[0][0]


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
