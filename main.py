import datetime
import json
import os
import helper
from pymongo import MongoClient
from bson.json_util import dumps

from flask import Flask, render_template, request, jsonify, redirect

from google.auth.transport import requests
from google.cloud import datastore
import google.oauth2.id_token
import pymysql
import requests

firebase_request_adapter = requests.Request()

# [START gae_python38_datastore_store_and_fetch_user_times]
# [START gae_python3_datastore_store_and_fetch_user_times]
datastore_client = datastore.Client()

# [END gae_python3_datastore_store_and_fetch_user_times]
# [END gae_python38_datastore_store_and_fetch_user_times]
app = Flask(__name__)


@app.route('/')
def index():
    return redirect('/home')


@app.route('/home')
def home():
    user_data, error, valid_token = helper.authenticateUser(request.cookies.get("token"))
    return render_template('home.html', user_data=user_data)


@app.route('/store')
def store():
    user_data, error, valid_token = helper.authenticateUser(request.cookies.get("token"))
    print(user_data)
    if valid_token:
        user_id = helper.get_sql_user_id_from_email(user_data['email'])
        return render_template('store.html', list_game_info=get_list_of_all_games(),user_data=user_data,user_id=user_id)
    return render_template('login.html')

@app.route('/my_games')
def my_games():
    user_data, error, valid_token = helper.authenticateUser(request.cookies.get("token"))
    if valid_token:
        list_game_info = []
        id_game_list = helper.get_sql_games_from_email(user_data['email'], user_data['name'])
        if id_game_list:
            list_game_info = helper.find_sql_game_from_id_list(id_game_list)
            print("list of game_info:",list_game_info)
        return render_template('my_games.html', user_data=user_data, list_game_info=list_game_info)
    return redirect('/home')



@app.route('/login')
def login():
    user_data, error, valid_token = helper.authenticateUser(request.cookies.get("token"))
    if valid_token:
        return redirect('/my_games')
    return render_template('login.html')



@app.route('/logout')
def logout():
    user_data, error, valid_token = helper.authenticateUser(request.cookies.get("token"))
    if valid_token:
        return render_template('logout.html')
    return redirect('/home')


# used to get the list of all the games available to the store
@app.route('/getListOfGames', methods=['GET'])
def get_list_of_all_games():
    return helper.cloud_sql_query('select * from VIDEOGAME')


@app.route('/hello/<name>/<age>')
def hello(name, age):
    return f'Hello, {name}! You are {age} years old.'

def tester(asd):
    return store()


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
