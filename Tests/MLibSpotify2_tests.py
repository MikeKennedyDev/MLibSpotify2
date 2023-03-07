import os

import MLibSpotify2.Authorization as Auth
import MLibSpotify2.SpotifyPlaylist as sp

from dotenv import load_dotenv

load_dotenv()

# region Fields

TestAuth = None
TestPlaylist = None
TestPlaylistId = '2UmDYQxgIDaKikeG53Ffd5'
TestTrackIds = ['56rgqDNRIqKq0qIMdu7r4r', '1rWzYSHyZ5BiI4DnDRCwy7']
TestTrackUri = 'https://api.spotify.com/v1/tracks/0irYSFrgXf2OH1F5NAdK6I'

# endregion


# region test methods

def AddRemoveTrackTest(verbose=False):
    global TestPlaylist

    original_num_tracks = len(TestPlaylist.GetAllTracks())

    if verbose:
        print(f'Playlist has {original_num_tracks} tracks.')

    try:
        TestPlaylist.RemoveTracks(TestTrackIds)
        if verbose:
            print('Tracks removed')
        new_num_tracks = len(TestPlaylist.GetAllTracks(force_refresh=True))
        if verbose:
            print(f'new track num: {new_num_tracks}')
        assert new_num_tracks == (original_num_tracks - len(TestTrackIds))

        TestPlaylist.AddTracks(TestTrackIds)
        new_num_tracks = len(TestPlaylist.GetAllTracks(force_refresh=True))
        assert new_num_tracks == original_num_tracks

    except:
        print('excepting')

        tracks = TestPlaylist.GetAllTracks(force_refresh=True)
        TestPlaylist.AddTracks(TestTrackIds)
        new_num_tracks = len(TestPlaylist.GetAllTracks(force_refresh=True))
        assert new_num_tracks == (original_num_tracks + len(TestTrackIds))

        TestPlaylist.RemoveTracks(TestTrackIds)
        new_num_tracks = len(TestPlaylist.GetAllTracks(force_refresh=True))
        assert new_num_tracks == original_num_tracks

    print(f'{len(TestTrackIds)} tracks added/removed successfully')


def AuthorizationTest(verbose=False):
    global TestPlaylist, TestAuth

    if verbose:
        print('Creating TestAuth')

    TestAuth = Auth.Authorization(client_id=os.getenv("CLIENT_ID"),
                                  client_secret=os.getenv("CLIENT_SECRET"),
                                  refresh_token=os.getenv("REFRESH_TOKEN"))

    if verbose:
        print('TestAuth created successfully')

    if verbose:
        print('Creating TestPlaylist')

    TestPlaylist = sp.SpotifyPlaylist(playlist_id=TestPlaylistId,
                                      auth=TestAuth)

    if verbose:
        print('TestPlaylist created successfully')

    assert TestPlaylist is not None

    if verbose:
        print('AuthorizationTest success')


def GetTracksTest(verbose=False):
    global TestPlaylist
    all_tracks = TestPlaylist.GetAllTracks(force_refresh=True)

    assert all_tracks is not None

    if verbose:
        print('GetTracks test success')


# endregion

if __name__ == '__main__':
    verbose = False

    if verbose:
        print('Starting tests')

    if verbose:
        print('Running AuthorizationTest()')
    AuthorizationTest(verbose)
    if verbose:
        print('AuthorizationTest() run success')

    if verbose:
        print('Running GetTracksTest()')
    GetTracksTest(verbose)
    if verbose:
        print('GetTracksTest() run success')

    if verbose:
        print('Running AddRemoveTrackTest()')
    AddRemoveTrackTest(verbose)
    if verbose:
        print('AddRemoveTrackTest() run success')
