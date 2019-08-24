"""
In this Python script, we will use Spotify API to get the data needed for analysis.

First, we will aim to answer the following questions using data based on my Spotify playlist :
    1. What are currently my favorite music types ?
    2. Who are my favorite artists ?

Then, we will try to build a playlist recommandation tool through the use of Machine Learning.
"""

### 1. Importing libraries

import pandas as pd 
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials

### 2. Creating an object to collect the data

class CollectData(object):
    """
    Class that will contains several methods allowing the user to :
        - load its Spotify's data
        - create a DataFrame containing all the data
    """

    def __init__(
        self, client_id, client_secret, username, 
        client_credentials, sp, scope, token):
        """
        Constructor allowing the initialization of all the variables used in the methods below.
        ------
        Parameters :
            - client_id : your Spotify Client ID 
            - client_secret : your Spotify Client Secret ID
            - username : your Spotify Username
            - client_credentials : authentication to Spotify Web API request
        """

        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.client_credentials = client_credentials
        self.sp = sp

    def spotify_data_collect(self):
        """
        Method that will allow the user to connect to the Spotify API with
        its credentials in order to access to its library of music.
        """

        self.scope = 'user-library-read' # Access to the user's private playlists
        self.token = util.prompt_for_user_token(self.username, self.scope)

        if self.token:
            self.sp = spotipy.Spotify(auth=self.token) # Creating a Spotify object with the user logs
        else:
            print("Token not available for : ", self.username)

        return self.sp

    def create_dataframe(self, spotify_data):
        """
        Method that will allow to create a DataFrame containing all the data
        related to the songs from the user playlist.
        """

        self.df_songs = pd.DataFrame()
        self.song_list = ''
        self.added_time_list = []
        self.artist_list = []
        self.title_list = []

        self.more_songs = True
        self.offset_index = 0

        while self.more_songs:
            songs = spotify_data.current_user_saved_tracks(offset=self.offset_index)

            ## A playlist on Spotify data is actually represented in a JSON file form
            ## So we need to use list comprehension to collect all the necessary data
            ## for our study.

            for song in songs['items']:
                self.song_list += song['track']['id'] + ','    # ID of the song
                self.added_time_list.append(song['added_at'])   # Time at which the song got added
                self.title_list.append(song['track']['name'])   # Name of the song
                
                # As a song can have multiple artists, we need to add all of them inside
                # of the list, so we need to use another list comprehension inside of
                # the initial one.  

                artists = song['track']['artists']
                artists_name = ''

                for artist in artists:
                    artists_name += artist['name'] + ','

                self.artist_list.append(artists_name[:-1])

            ## Collecting the audio features for each song and put them into a DataFrame

            songs_features = spotify_data.audio_features(self.song_list[:-1])
            df_song_feats = pd.DataFrame(songs_features)
            df_saved_songs = self.df_songs.append(df_song_feats)
            self.song_list = ''

            if songs['next'] == None:
                self.more_songs = False # There are no more songs in the playlist
            else:
                self.offset_index += songs['limit'] # Index of the playlists

        ### Adding timestamp, title and artists of a song as features in the DataFrame

        df_saved_songs['added_at'] = self.added_time_list
        df_saved_songs['song_title'] = self.title_list
        df_saved_songs['artists'] = self.artist_list 
