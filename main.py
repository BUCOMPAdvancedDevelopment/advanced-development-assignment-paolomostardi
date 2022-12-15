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
    return render_template('home.html')


@app.route('/store')
def store():
    return render_template('store.html', listOfgame=getListOfGames())


@app.route('/my_games')
def my_games():
    infos, error, valid_token = helper.authenticateUser(request.cookies.get("token"))
    helper.get_sql_games_from_email(infos['email'], infos['name'])
    if valid_token:
        return render_template('my_games.html', user_data=infos)
    return redirect('/login')


@app.route('/login')
def login():
    return render_template('login.html')


# used to get the list of games in javascript files and others
@app.route('/getListOfGames', methods=['GET'])
def getListOfGames():
    return helper.cloud_sql_query('select * from VIDEOGAME')

@app.route('/test')
def tester(sdfsdf):
    return str(helper.create_sql_user('fake@fake.com','test test'))


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
