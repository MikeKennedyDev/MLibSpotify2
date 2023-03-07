import requests
import MLibSpotify2.Utilities as util


class Authorization:
    # region Fields

    __access_token = None
    __client_id = None
    __client_secret = None
    __refresh_token = None

    # endregion Fields

    # region Constructors

    def __init__(self,
                 client_id,
                 client_secret,
                 refresh_token,
                 access_token=None,
                 force_refresh=False):

        self.__client_secret = client_secret
        self.__client_id = client_id
        self.__refresh_token = refresh_token

        if access_token and not force_refresh:
            __access_token = access_token

        if not self.__validate_access_token():
            self.__refresh_access_token()
            if not self.__validate_access_token():
                raise Exception("Invalid auth token.")

    # endregion Constructors

    # region Methods

    def GetAccessToken(self):
        self.__validate_access_token()
        return self.__access_token

    def __validate_access_token(self):

        request_headers = {
            "Authorization": f"Bearer {self.__access_token}",
            "Content-Type": "application/json"
        }

        response = requests.get("https://api.spotify.com/v1/me",
                                headers=request_headers)

        return response.status_code == 200

    def __refresh_access_token(self):

        request_headers = {
            "Authorization": util.EncodeAuthorization(self.__client_id,
                                                      self.__client_secret),
            "Content-Type": "application/x-www-form-urlencoded"
        }

        request_body = {
            "grant_type": "refresh_token",
            "refresh_token": self.__refresh_token
        }

        response = requests.post("https://accounts.spotify.com/api/token",
                                 headers=request_headers,
                                 data=request_body)

        if not response.ok:
            raise Exception(f"Error refreshing access token: {response.json()['error']}")

        self.__access_token = response.json()['access_token']

    # endregion Methods
