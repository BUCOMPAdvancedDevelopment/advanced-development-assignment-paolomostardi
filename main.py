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
def index():
    return redirect('/home')


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/store')
def store():
    return render_template('store.html',listOfgame = getListOfGames())


@app.route('/my_games')
def my_games():
    helper.authenticateUser(request.cookies.get("token"))

    return render_template('my_games.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/addGame')
def add_game():
    return "gameAdded"


@app.route('/getListOfGames', methods=['GET'])
def getListOfGames():
    return helper.sql_request('select * from VIDEOGAME')


@app.route('/sqlRequestUser')
def sql_request_user():
    return helper.sql_request('select * from VIDEOGAME')

@app.route('/createUser')
def sql_create_user():
    return helper.sql_request('user')


@app.route('/callfunction')
def call(whatever):
    url = "https://europe-west2-adassigment.cloudfunctions.net/helloworld"
    req = requests.post(url, json={
        "source": "select * ",
    }, headers={"Content-type": "application/json", "Accept": "text/plain"})
    return (req.content)


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.

    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)