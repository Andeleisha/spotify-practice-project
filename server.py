import json
from flask import Flask, request, redirect, g, render_template
import requests
from urllib.parse import quote
import os

# Authentication Steps, paramaters, and responses are defined at https://developer.spotify.com/web-api/authorization-guide/
# Visit this url to see all the steps, parameters, and expected response.


app = Flask(__name__)

#  Client Keys
CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

# Server-side Parameters
CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 8080
REDIRECT_URI = "{}:{}/callback/q".format(CLIENT_SIDE_URL, PORT)
SCOPE = "playlist-modify-public playlist-modify-private"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()

auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    # "state": STATE,
    # "show_dialog": SHOW_DIALOG_str,
    "client_id": CLIENT_ID
}


@app.route("/")
def index():
    # Auth Step 1: Authorization
    url_args = "&".join(["{}={}".format(key, quote(val)) for key, val in auth_query_parameters.items()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    return redirect(auth_url)


@app.route("/callback/q")
def callback():
    # Auth Step 4: Requests refresh and access tokens
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload)

    # Auth Step 5: Tokens are Returned to Application
    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]

    # Auth Step 6: Use the access token to access Spotify API
    authorization_header = {"Authorization": "Bearer {}".format(access_token)}

    # Get profile data
    user_profile_api_endpoint = "{}/me".format(SPOTIFY_API_URL)
    profile_response = requests.get(user_profile_api_endpoint, headers=authorization_header)
    profile_data = json.loads(profile_response.text)

    # Get user playlist data
    playlist_api_endpoint = "{}/playlists".format(profile_data["href"])
    playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
    playlist_data = json.loads(playlists_response.text)

    # Combine profile and playlist data to display
    display_arr = [profile_data] + playlist_data["items"]

    #Test
    search_api_endpoint = "{}/search".format(SPOTIFY_API_URL)
    search_args = "?q=romantic&type=playlist"
    romantic_playlists_request = requests.get(search_api_endpoint + search_args, headers=authorization_header)
    romantic_playlists = json.loads(romantic_playlists_request.text)

    return render_template("index.html", sorted_array=display_arr, romantic_playlists=romantic_playlists)

@app.route("/books")
def book_search():
    """Play with GoodReads API and search results"""
    
    #UnrelatedGoodReadsStuff
    gr_search_endpoint = "https://www.goodreads.com/search.json"
    gr_search_key = os.environ["GOODREADS_DEV_KEY"]
    gr_search_args = "&q=Ender%27s+Game"
    gr_search_request = requests.get(gr_search_endpoint + gr_search_key + gr_search_args)
    gr_search_result = gr_search_request.text 

    gr_reviews_for_book_endpoint = "https://www.goodreads.com/book/show/"
    book_id = "50"
    format_arg = ".json?"
    reviews_request = requests.get(gr_reviews_for_book_endpoint + book_id + format_arg + "key=" + gr_search_key)
    reviews_result = reviews_request.text

    return render_template("book_tests.html", books=reviews_result)



if __name__ == "__main__":
    app.run(debug=True, port=PORT)