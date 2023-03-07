import base64
import os
import re
import webbrowser
from urllib.parse import urlencode

import requests

TrackApiBase = 'https://api.spotify.com/v1/tracks/'


def GetAllPlaylistsEndpoint(limit=20, offset=0):
    return f'https://api.spotify.com/v1/me/playlists?limit={limit}&offset={offset}'


def GetPlaylistTracksEndpoint(playlist_id, limit=100, offset=0):
    return f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks?limit={limit}&offset={offset}'


def GetPlaylistEndpoint(playlist_id):
    return f'https://api.spotify.com/v1/playlists/{playlist_id}'


def GetAddTracksEndpoint(playlist_id, tracks):
    uris = '%2C'.join([f'spotify%3Atrack%3A{track}' for track in tracks])
    return f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks?uris={uris}'


def chunker(lst, size):
    return [lst[i:i + size] for i in range(0, len(lst), size)]


def GetRemoveTracksEndpoint(playlist_id):
    return f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'


def EncodeAuthorization(client_id, client_secret):
    encoded_id = client_id.encode()
    encoded_secret = client_secret.encode()

    encoded_creds = base64.b64encode(encoded_id + b':' + encoded_secret).decode("utf-8")

    return f'Basic {encoded_creds}'


def GetAccessToken(client_id, client_secret, RefreshToken=None):
    request_headers = {
        "Authorization": EncodeAuthorization(client_id, client_secret),
        "Content-Type": "application/x-www-form-urlencoded"
    }

    request_body = {
        "grant_type": "authorization_code",
        "code": os.getenv("AUTHORIZATION_CODE"),
        "redirect_uri": os.getenv("REDIRECT_URI")
    }

    response = requests.post("https://accounts.spotify.com/api/token",
                             headers=request_headers,
                             data=request_body)
    print(response)
    print(response.content)
    return response.json()['access_token']


def RefreshAccessToken(client_id, client_secret):
    request_headers = {
        "Authorization": EncodeAuthorization(client_id, client_secret),
        "Content-Type": "application/x-www-form-urlencoded"
    }

    request_body = {
        "grant_type": "refresh_token",
        "refresh_token": os.getenv("REFRESH_TOKEN")
    }

    response = requests.post("https://accounts.spotify.com/api/token",
                             headers=request_headers,
                             data=request_body)
    print(response)
    print(response.content)
    return response.json()['access_token']


def GetAuthorizationCode():
    # Send get request to /authorize
    client_id = os.getenv("CLIENT_ID")
    redirect_uri = os.getenv("REDIRECT_URI")
    scope = 'playlist-read-collaborative playlist-modify-public'

    auth_url = 'https://accounts.spotify.com/authorize?'
    headers = {"client_id": client_id,
               "response_type": "code",
               "redirect_uri": redirect_uri,
               "scope": scope
               }

    # Code is returned in web browser here
    webbrowser.open(auth_url + urlencode(headers))

    return
