# Module that allows the user to load its data from Spotify.
# This package can be used as library if placed in the same repository of the files that
# will use this module.

# For example, to import this class as a module, you will just have to type :
# from SpotifyData import SpotifyData

# Then, if you want to specifically use a method inside of the class, let's say, create_dataframe, you'll have to :
# load_data = SpotifyData(client_id, client_secret, username, data_location)
# df_spotify = load_data.create_dataframe(spotify_data, offset)

### Import libraries

import pandas as pd
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials

### Contents of the class

class SpotifyData(object):
    """
    Class that contains all the methods to load your Spotify Data (the tracks that you liked).
    """
    
    def __init__(
        self, client_id, client_secret, 
        username, data_location):
        """
        Initializing our constructors.
        
        The three parameters in the function inputs are available in the user's Spotify for Developers dashboard.
        ------
        Parameters:
            - client_id: the user's Spotify client ID 
            - client_secret: the user's Spotify secret ID
            - username: the user's Spotify username
            - data_location: the data that the user wants to load from its Spotify logs (ex: gathering data from playlists, from saved tracks, etc ...)
        """
        
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.data_location = data_location

    def connect_spotify(self):
        """
        Method allowing the user to connect to its Spotify database, thus according him access to his songs data.
        """

        ### Creating a Spotify object with the user logs

        self.client_credentials_manager = SpotifyClientCredentials(
            client_id=self.client_id, 
            client_secret=self.client_secret
        )

        self.sp = spotipy.Spotify(
            client_credentials_manager=self.client_credentials_manager
        )

        ### Choosing specific user data (scope allows to choose from which Spotify section to load the data, 
        ### token allows to connect the user credentials).

        self.scope = self.data_location # Location from where we want to load the data on Spotify (playlist, library, etc ...)
        self.token = util.prompt_for_user_token(self.username, self.scope) # Generate an authentication token

        ## Get read access to your library

        if self.token:
            self.sp = spotipy.Spotify(auth=self.token)
        else:
            print("No token available.", self.username)

        return self.sp
    
    def create_dataframe(self, spotify_data, offset):
        """
        Method that allows the user to create a DataFrame containing the data related to the songs in its library
        ------
        Parameters:
            - spotify_data:  the user data on Spotify.
            - offset : number of tracks to select in the playlist.
        """

        self.df_saved_tracks = pd.DataFrame()
        self.track_list = ''
        self.added_time_list = []
        self.artist_list = []
        self.title_list = []
        self.more_songs = True

        # As the limit of tracks' storage in the JSON file is 20, we need to set an offset to determine 
        # from which track we start to collect the data.
        # An offset of 0 means that we will collect data from track 0 to track 20.
        # So, if you have 220 songs in your playlist, you will have to use 11 offsets to load your data entirely.

        self.offset_index = offset

        while self.more_songs:
            self.songs = spotify_data.current_user_saved_tracks(offset=self.offset_index)

            # A playlist on Spotify data is actually represented in a JSON file form,
            # so we need to use list comprehension to collect all the necessary data
            # for our study.

            for song in self.songs['items']:
                self.track_list += song['track']['id'] + ','         # ID of the song
                self.added_time_list.append(song['added_at'])        # Time at which the song got added
                self.title_list.append(song['track']['name'])        # Name of the song  

                # As a song can have multiple artists, we need to add all of them inside
                # of the list, so we need to use another list comprehension inside of
                # the initial one.  

                self.artists = song['track']['artists']
                self.artists_name = ''

                for artist in self.artists:
                    self.artists_name += artist['name']  + ','

                self.artist_list.append(self.artists_name[:-1])

            ### Collecting the audio features for each song and put them into a DataFrame

            self.track_features = spotify_data.audio_features(self.track_list[:-1])
            self.df_temp = pd.DataFrame(self.track_features)
            self.df_saved_tracks = self.df_saved_tracks.append(self.df_temp)

            self.track_list = ''

            if self.songs['next'] == None:
                self.more_songs = False    # There are no more songs in the playlist
            else:
                self.offset_index += self.songs['limit']    # Index of the playlist

            ### Adding timestamp, title and artists of a song as features in the DataFrame

            self.df_saved_tracks['added_at'] = self.added_time_list
            self.df_saved_tracks['song_title'] = self.title_list
            self.df_saved_tracks['artists'] = self.artist_list 

            return self.df_saved_tracks