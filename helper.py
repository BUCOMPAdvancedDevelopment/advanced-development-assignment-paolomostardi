import json
import google.oauth2.id_token
from google.auth.transport import requests as googleRequests
import requests


firebase_request_adapter = googleRequests.Request()


def authenticateUser(token):
    """ Authenticates the user and returns the user's information"""

    # Verify Firebase auth.
    id_token = token
    error_message = None
    claims = None
    user_data = None
    if id_token:
        try:
            # Verify the token against the Firebase Auth API.
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)

            # Get the users' account (and make it if it doesn't exist)
            user_data = getUserData(
                claims['user_id'], claims['email'], claims['name'])

        except ValueError as exc:
            # Expired tokens etc
            error_message = str(exc)
            user_data = None
    return {
        "user_data": user_data,
        "error_message": error_message
    }

def getUserData(userId, email="", name=""):


    url = "https://europe-west2-synthetic-cargo-328708.cloudfunctions.net/read_mongodb_users"
    data = {
        'userId': userId,
        'email': email,
        'name': name
    }
    response = requests.get(url, data)
    user_data = json.loads(response.content.decode("utf-8"))

    return user_data



def sql_request():
    return