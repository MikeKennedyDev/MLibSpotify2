import logging
import os
from datetime import date
from logging.handlers import TimedRotatingFileHandler

import requests

import MLibSpotify2.Links as links
import MLibSpotify2.Utilities as util

# region Fields

base_spotify_api = 'https://api.spotify.com/v1/'
__refresh_token = None
__access_token = None
__client_id = None
__client_secret = None

# endregion

logger = logging.getLogger('standard')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = TimedRotatingFileHandler('DiscordBot.log', when="midnight", interval=1)
handler.suffix = "%Y%m%d"
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
log_dir = os.path.join(os.getcwd(), 'Logs')
if not os.path.exists(log_dir):
    os.mkdir(log_dir)
logging.basicConfig(filename=f'Logs\\log_{date.today().strftime("%d_%m_%Y")}.txt', format='%(asctime)s - %(message)s',
                    level=logging.INFO)


class SpotifyPlaylist:
    # region Fields

    PlaylistId = None
    PlaylistName = None
    __all_tracks = []
    __authorization = None

    # endregion

    # region Constructors

    def __init__(self,
                 playlist_id,
                 auth):

        # Initialize playlist values
        self.PlaylistId = playlist_id

        # Populate playlist data
        self.__authorization = auth
        self.PlaylistName = self.GetPlaylistName()
        self.PlaylistUrl = links.GetSpotifyPlaylistUrl(self.PlaylistId)
        self.__all_tracks = self.GetAllTracks(force_refresh=True)

        logging.info(f'Playlist object created for playlist {self.PlaylistName} and populated with {len(self.__all_tracks)} tracks.')

    # endregion

    # region Methods

    def GetPlaylistName(self):
        client_id = os.getenv("CLIENT_ID")
        client_secret = os.getenv("CLIENT_SECRET")
        endpoint = util.GetPlaylistEndpoint(self.PlaylistId)
        headers = {"Authorization": f"Bearer {self.__authorization.GetAccessToken()}"}
        response = requests.get(endpoint, headers=headers)

        if not response.ok:
            logging.error(f"Failed to retrieve playlist name: {response.json()['error']}")
            raise Exception(f"Failed to retrieve playlist name: {response.json()['error']}")

        return response.json()["name"]

    def GetAllTracks(self, force_refresh=False):
        if not force_refresh and self.__all_tracks:
            return self.__all_tracks

        limit = 100
        offset = 0
        self.__all_tracks = []

        while True:
            endpoint = util.GetPlaylistTracksEndpoint(playlist_id=self.PlaylistId,
                                                           limit=limit,
                                                           offset=offset)
            headers = {"Authorization": f"Bearer {self.__authorization.GetAccessToken()}"}
            response = requests.get(endpoint, headers=headers)

            # Error handling
            if not response.ok:
                logging.error(f"Error getting playlist tracks: {response.json()['error']}")
                raise Exception(f"Error getting playlist tracks: {response.json()['error']}")

            tracks = [item['track'] for item in response.json()['items']]
            self.__all_tracks += tracks

            if len(tracks) < limit:
                break

            offset += limit

        return self.__all_tracks

    def AddTracks(self, track_ids):

        # Refresh tracks before add
        self.__all_tracks = self.GetAllTracks(force_refresh=True)

        playlist_track_ids = [track['id'] for track in self.__all_tracks]
        tracks_to_add = list(set(track_ids) - set(playlist_track_ids))

        if len(tracks_to_add) == 0:
            logging.debug('Specified tracks already in playlist.')
            raise Exception('Specified tracks already in playlist.')

        logging.info(f'Adding {len(tracks_to_add)} track(s) to playlist {self.PlaylistId}')

        headers = {"Authorization": f"Bearer {self.__authorization.GetAccessToken()}"}
        playlist_chunks = util.chunker(tracks_to_add, 10)

        for chunk in playlist_chunks:
            endpoint = util.GetAddTracksEndpoint(self.PlaylistId, tracks=chunk)
            response = requests.post(endpoint, headers=headers)

            if not response.ok:
                logging.error(f"Error adding tracks to playlist: {response.json()['error']}")
                raise Exception(f"Error adding tracks to playlist: {response.json()['error']}")

        # Update internal track list
        self.__all_tracks = self.GetAllTracks(force_refresh=True)

    def RemoveTracks(self, track_ids):

        # Refresh tracks
        self.__all_tracks = self.GetAllTracks(force_refresh=True)

        playlist_track_ids = [track['id'] for track in self.__all_tracks]
        tracks_to_remove = [value for value in track_ids if value in playlist_track_ids]
        if len(tracks_to_remove) == 0:
            logging.debug("Error thrown in RemoveTracks: Tracks not found in playlist.")
            raise Exception('Tracks not found in playlist.')

        logging.info(f'Removing {len(tracks_to_remove)} track(s) from playlist {self.PlaylistId}')

        playlist_chunks = util.chunker(tracks_to_remove, 10)
        endpoint = util.GetRemoveTracksEndpoint(self.PlaylistId)
        headers = {"Authorization": f"Bearer {self.__authorization.GetAccessToken()}"}

        for chunk in playlist_chunks:
            track_uris = [{"uri": f"spotify:track:{track_id}"} for track_id in chunk]

            # I don't know why, but spotify complains unless this format is used here
            body = str({"tracks": track_uris}).replace("'", '\"')

            response = requests.delete(endpoint, headers=headers, data=body)
            if not response.ok:
                logging.error(f"Not response.ok returned from RemoveTrack api call: {response.json()['error']}")
                raise Exception(f"Error removing tracks: {response.json()['error']}")

        # Update internal track list
        self.__all_tracks = self.GetAllTracks(force_refresh=True)

    # endregion


def GetAllUserPlaylists(authorization):
    user_playlists = []
    offset = 0
    limit = 10

    while True:
        endpoint = util.GetAllPlaylistsEndpoint(limit=10, offset=offset)
        headers = {"Authorization": f"Bearer {authorization.GetAccessToken()}"}
        response = requests.get(endpoint, headers=headers)

        playlist_ids = [item['id'] for item in response.json()['items']]

        for playlist_id in playlist_ids:
            user_playlists.append(SpotifyPlaylist(playlist_id=playlist_id, auth=authorization))

        if len(playlist_ids) < 10:
            break
        offset += limit

    logging.info(f'GetAllUserPlaylists: {len(user_playlists)} playlists found.')
    return
