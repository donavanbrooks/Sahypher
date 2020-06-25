from __future__ import print_function  # (at top of module)
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException
import json
import spotipy
import time
import sys
import argparse
import os


class SpotifyClient():

    def __init__(self):
        self.name = "Donavan"
        self.client_credentials_manager = SpotifyClientCredentials()
        self.sp = spotipy.Spotify(client_credentials_manager = self.client_credentials_manager)

    def get_args(self):
        parser = argparse.ArgumentParser(description='Creates a playlist for user')
        parser.add_argument('-u', '--username', required=False,
                            default=os.environ.get('SPOTIPY_CLIENT_USERNAME'),
                            help='Username id. Defaults to environment var')
        parser.add_argument('-p', '--playlist', required=True,
                            help='Name of Playlist')
        parser.add_argument('-d', '--description', required=False, default='',
                            help='Description of Playlist')
        return parser.parse_args()

    def get_track_analysis(self, track_id):
        if len(sys.argv) > 1:
            track_id = sys.argv[1]

        start = time.time()

        try:
            analysis = self.sp.audio_analysis(track_id)
            delta = time.time() - start
            analysis_json = json.dumps(analysis, indent=4)

            # Writing to JSON file
            filename = '{}.json'.format(track_id)
            with open(filename, "w") as outfile:
                outfile.write(analysis_json)

            print(analysis_json)
            print("analysis retrieved in %.2f seconds" % (delta))
            return analysis
        except SpotifyException as e:
            error_msg = 'Error occurred fetching track analysis for track id: {}' \
                        ',\n Exception: {}'.format(track_id, e)
            print(error_msg)

    def get_track_id_search(self, track_name, limit):
        start = time.time()

        try:
            search_results = self.sp.search(q=track_name, limit=limit, type='track')
            delta = time.time() - start
            print(json.dumps(search_results, indent=4))
            print("analysis retrieved in %.2f seconds" % (delta))

            for idx, track in enumerate(search_results['tracks']['items']):
                artist = track['artists'][0]['name']
                track_name = track['name']
                id = track['id']

                print(idx, 'Artist: {}, Name: {}, ID: {}'.format(artist, track_name, id))

            return search_results
        except SpotifyException as e:
            print('Error occurred searching for track{}'.format(track_name))

    # TODO: Add functionality to pull back new releases
    def get_new_releases(self):
        try:
            raise NotImplementedError("get_new_releases() not yet implemented!")
        except SpotifyException as e:
            print('Error occurred searching for new releases')

if __name__ == '__main__':
    client = SpotifyClient()
    # client.get_track_id_search('ex-factor', 10)
    client.get_track_analysis('2VjXGuPVVxyhMgER3Uz2Fe')
