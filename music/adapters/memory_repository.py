import csv
import os
from pathlib import Path
import re
from typing import List

from bisect import bisect, bisect_left, insort_left

from werkzeug.security import generate_password_hash

from music.adapters.repository import AbstractRepository, RepositoryException
from music.domainmodel.artist import Artist
from music.domainmodel.playlist import PlayList
from music.domainmodel.track import Track
from music.domainmodel.genre import Genre
from music.domainmodel.review import Review
from music.domainmodel.album import Album
from music.domainmodel.user import User
from music.adapters.csvdatareader import TrackCSVReader

class MemoryRepository(AbstractRepository):
    # Tracks ordered by id which is assumed unique.

    def __init__(self):
        self.__tracks = list()
        self.__tracks_index = dict()
        self.__artists = list()
        self.__genres = list()
        self.__albums = list()
        self.__reviews = dict()
        self.__users = list()
        self.__reviews_list = list()
        self.__playlist_list = []
        self.__playlist_ids = 0
    
    def add_user(self, user: User):
        self.__users.append(user)

    def get_user(self, user_name) -> User:
        return next((user for user in self.__users if user.user_name == user_name), None)

    def get_number_of_users(self) -> int:
        return len(self.__users)

    def add_track(self, track: Track):
        insort_left(self.__tracks, track)
        self.__tracks_index[track.track_id] = track
        self.__reviews[track] = []
    
    def get_track(self, id: int) -> Track:
        track = None
        try:
            track = self.__tracks_index[id]
        except KeyError:
            raise ValueError(f"no track with the id '{id}'")
            
        return track
    
    def get_tracks_by_artist(self, target_artist: Artist) -> List[Track]:
        matching_tracks = list()

        try:
            for track in self.__tracks:
                if track.artist == target_artist:
                    matching_tracks.append(track)
        except ValueError:
            # No tracks for specified artist. Simply return an empty list.
            pass

        return matching_tracks
    
    def get_number_of_tracks(self) -> int:
        return len(self.__tracks)

    def get_all_track_ids(self): 
        return self.__tracks_index.keys()

    def get_tracks_by_id(self, id_list):
        # Strip out any ids in id_list that don't respresent Track ids in the repository.

        existing_ids = [id for id in id_list if id in self.__tracks_index]

        # Fetch the tracks.
        tracks = [self.__tracks_index[id] for id in existing_ids]
        return tracks
    
    def get_track_ids_for_titles(self, key: str):
        # Linear search, to find the first occurence of an artist with the name artist_name.
        check_track = next((c_track for c_track in self.__tracks if c_track.title.lower().find(key.lower()) != -1), None)
        # Retrieve the ids of tracks associated with the artist.
        if check_track is not None:
            track_ids = list()
            for track in self.__tracks:
                title = (track.title).lower()
                if title.find(key.lower()) != -1:
                    track_ids.append(track.track_id)
        else:
            # No artist with name artist_name, so return an empty list.
            track_ids = list()
        
        return track_ids

    def get_track_ids_for_artist(self, artist_name: str):
        # Linear search, to find the first occurence of an artist with the name artist_name.
        artist = next((artist for artist in self.__artists if (artist.full_name).lower().find(artist_name.lower()) != -1), None)

        # Retrieve the ids of tracks associated with the artist.
        if artist is not None:
            track_ids = list()
            for track in self.__tracks:
                if (track.artist.full_name).lower().find(artist_name.lower()) != -1:
                    track_ids.append(track.track_id)
        else:
            # No artist with name artist_name, so return an empty list.
            track_ids = list()
        
        return track_ids
    
    def get_track_ids_for_genre(self, genre_name: str):
        # Linear search, to find the first occurence of a Genre with the name genre_name.
        genre = next((genre for genre in self.__genres if (genre.name).lower() == genre_name.lower()), None)

        # Retrieve the ids of tracks associated with the Genre.
        if genre is not None:
            track_ids = list()
            for track in self.__tracks:
                for genre in track.genres:
                    if (genre.name).lower() == genre_name.lower():
                        track_ids.append(track.track_id)
        else:
            # No Genre with name genre_name, so return an empty list.
            track_ids = list()
        
        return track_ids
    
    def get_track_ids_for_album(self, album_name: str):
        # Linear search, to find the first occurence of an Album with the name album_name.
        album = next((album for album in self.__albums if (album.title).lower().find(album_name.lower()) != -1), None)

        # Retrieve the ids of tracks associated with the Album.
        if album is not None:
            track_ids = list()
            for track in self.__tracks:
                if track.album:
                    if (track.album.title).lower().find(album_name.lower()) != -1:
                        track_ids.append(track.track_id)
                    else: 
                        pass
        else:
            # No Album with name album_name, so return an empty list.
            track_ids = list()
        
        return track_ids

    def get_tracks_by_genre(self, target_genre: Genre) -> List[Track]:
        matching_tracks = list()

        try:
            for track in self.__tracks:
                for genre in track.genres:
                    if genre == target_genre:
                        matching_tracks.append(track)
        except ValueError:
            # No tracks for specified genre. Simply return an empty list.
            pass

        return matching_tracks
    
    def get_tracks_by_album(self, target_album: Album) -> List[Track]:
        matching_tracks = list()

        try:
            for track in self.__tracks:
                if track.album == target_album:
                        matching_tracks.append(track)
        except ValueError:
            # No tracks for specified album. Simply return an empty list.
            pass

        return matching_tracks

    def add_genre(self, genre: Genre):
        self.__genres.append(genre)
    
    def get_genres(self) -> List[Genre]:
        return self.__genres
    
    def add_artist(self, artist: Artist):
        self.__artists.append(artist)
    
    def get_artists(self) -> List[Artist]:
        return self.__artists
    
    def add_album(self, album: Album):
        self.__albums.append(album)
    
    def get_albums(self) -> List[Album]:
        return self.__albums
    
    def get_tracks(self) -> List[Track]:
        return self.__tracks
    
    def add_review(self, track, review):
        if not isinstance(review, Review): return
        if review in self.__reviews_list:
            return

        self.__reviews[track].append(review)
        
        self.__reviews_list.append(review)

    def get_reviews(self, track):
        try:
            return self.__reviews[track]
        except KeyError:
            return []
        
    def add_track_to_likes(self, user: User, track: Track): 
        if isinstance(track, Track):
            user.add_liked_track(track)
    
    def remove_track_from_likes(self, user: User, track: Track): 
        user.remove_liked_track(track)

    def get_all_reviews(self): 
        return self.__reviews_list 
    
    def get_all_liked_tracks(self, user):
        return user.liked_tracks

    def add_playlist_to_lists(self, user: User, playlist: PlayList): 
        if isinstance(playlist, PlayList):
            user.add_playlist(playlist)
            if playlist not in self.__playlist_list:
                self.__playlist_list.append(playlist)
    
    def remove_playlist_from_lists(self, user, playlist: PlayList): 
        if isinstance(playlist, PlayList):
            for user in self.__users: 
                if playlist in user.playlist: user.remove_playlist(playlist)
            self.__playlist_list.remove(playlist)
    
    def get_user_playlists(self, user):
        return user.playlist

    def get_playlist_id(self):
        self.__playlist_ids += 1
        return self.__playlist_ids
    
    def get_all_playlist(self): 
        return self.__playlist_list
    
    def get_playlist_by_id(self, id: int): 
        playlist = next((playlist for playlist in self.__playlist_list if playlist.list_id == id), None)
        return playlist
    
    def get_user_reviews(self, user): 
        return user.reviews
    
    def get_visible_playlists(self): 
        return [playlist for playlist in self.__playlist_list if playlist.is_public == True]

def populate(data_path: Path, repo: MemoryRepository, database_mode=False):
    """ Populates the given repository using data at the given path. """
    dirname = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    albums_file_name = os.path.join(dirname, 'adapters/data/raw_albums_excerpt.csv')
    tracks_file_name = os.path.join(dirname, 'adapters/data/raw_tracks_excerpt.csv')
    reader = TrackCSVReader(albums_file_name, tracks_file_name, database_mode)
    reader.read_csv_files()

    for track in reader.dataset_of_tracks:
        repo.add_track(track)

    for artist in reader.dataset_of_artists:
        repo.add_artist(artist)

    for genre in reader.dataset_of_genres:
        repo.add_genre(genre)
    
    for album in reader.dataset_of_albums:
        repo.add_album(album)
    
    #repo.add_tracks(reader.dataset_of_tracks)
    #repo.add_artists(reader.dataset_of_artists)
    #repo.add_genres(reader.dataset_of_genres)
    #repo.add_albums(reader.dataset_of_albums)