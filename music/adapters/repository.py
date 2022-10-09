import abc
from typing import List

from music.domainmodel.artist import Artist
from music.domainmodel.track import Track
from music.domainmodel.genre import Genre
from music.domainmodel.review import Review
from music.domainmodel.album import Album
from music.domainmodel.user import User
from music.domainmodel.playlist import PlayList
from music.adapters.csvdatareader import TrackCSVReader

repo_instance = None

class RepositoryException(Exception):

    def __init__(self, message=None):
        pass

class AbstractRepository(abc.ABC):

    @abc.abstractmethod
    def add_user(self, user: User):
        """" Adds a User to the repository. (Register)"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_user(self, user_name) -> User:
        """ Returns the User named user_name from the repository.
        If there is no User with the given user_name, this method returns None. (Login)
        """
        raise NotImplementedError

    @abc.abstractmethod
    def add_track(self, track: Track):
        """ Adds a track to the repository. """
        raise NotImplementedError
    
    @abc.abstractmethod
    def get_track(self, id: int) -> Track:
        """ Returns Track with id from the repository.
        If there is no Track with the given id, this method returns None.
         """
        raise NotImplementedError
    
    @abc.abstractmethod
    def get_tracks_by_artist(self, target_artist: Artist) -> List[Track]:
        """ Returns a list of tracks that were made by the target_artist. 
        If there are no tracks by the given artist, this method returns an empty list.
        """
        raise NotImplementedError
    
    @abc.abstractmethod
    def get_number_of_tracks(self) -> int:
        """ Returns the number of Tracks in the repository. """
        raise NotImplementedError
    
    @abc.abstractmethod
    def get_all_track_ids(self):
        """ Returns a list of all ids of tracks stored in the repository.
        """
        raise NotImplementedError
    
    @abc.abstractmethod
    def get_tracks_by_id(self, id_list):
        """ Returns a list of Tracks, whose id matches those in id_list, from the repository.
        If there are no matches, this method returns an empty list.
        """
        raise NotImplementedError
    
    @abc.abstractclassmethod
    def get_track_ids_for_titles(self, title: str):
        """ Returns a list of ids representing tracks that are tagged by title.
        If there are no Tracks that are tagged by title, this method returns an empty list.
        """
        raise NotImplementedError
    
    @abc.abstractclassmethod
    def get_track_ids_for_artist(self, artist_name: str):
        """ Returns a list of ids representing tracks that are tagged by artist_name.
        If there are no Tracks that are tagged by artist_name, this method returns an empty list.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_track_ids_for_genre(self, genre_name: str):
        """ Returns a list of ids representing tracks that are tagged by genre_name. 
        If there are no Tracks that are tagged by genre_name, this method returns an empty list.
        """
        raise NotImplementedError
    
    @abc.abstractmethod
    def get_track_ids_for_album(self, album_name: str):
        """ Returns a list of ids representing tracks that are tagged by album_name.
        If there are no Tracks that are tagged by album_name, this method returns an empty list.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_tracks_by_genre(self, target_genre: Genre) -> List[Track]:
        """ Returns a list of tracks that have the target_genre. 
        If there are no tracks with the given genre, this method returns an empty list.
        """
        raise NotImplementedError
    
    @abc.abstractmethod
    def get_tracks_by_album(self, target_album: Album) -> List[Track]:
        """ Returns a list of tracks that were made by the target_album. 
        If there are no tracks associated with the given album, this method returns an empty list.
        """
        raise NotImplementedError
    
    @abc.abstractmethod
    def add_genre(self, genre: Genre):
        """ Adds a Genre to the repository. """
        raise NotImplementedError
    
    @abc.abstractmethod
    def get_genres(self) -> List[Genre]:
        """ Returns the Genres stored in the repository. """
        raise NotImplementedError
    
    @abc.abstractmethod
    def add_artist(self, artist: Artist):
        """ Adds an Artist to the repository. """
        raise NotImplementedError
    
    @abc.abstractmethod
    def get_artists(self) -> List[Artist]:
        """ Returns the Artists stored in the repository. """
        raise NotImplementedError
    
    @abc.abstractmethod
    def add_album(self, album: Album):
        """ Adds an Album to the repository. """
        raise NotImplementedError
    
    @abc.abstractmethod
    def get_albums(self) -> List[Album]:
        """ Returns the Albums stored in the repository. """
        raise NotImplementedError
    
    @abc.abstractmethod
    def add_review(self, review: Review, user: User):
        """ Adds a Review to the repository.
        
        If the Review doesn't have bidirectional links with a Track and User, this method raises a 
        RepositoryException and doesn't update the repository.
        """
        raise NotImplementedError
    
    @abc.abstractmethod
    def get_reviews(self):
        """ Returns the Reviews stored in the repository for a specified track."""
        raise NotImplementedError
    
    @abc.abstractmethod
    def get_all_reviews(self): 
        """ Returns the Reviews stored in the repository."""
        raise NotImplementedError

    @abc.abstractmethod
    def add_track_to_likes(self, user, track ):
        """ Adds track to users liked tracks."""
        raise NotImplementedError

    @abc.abstractmethod
    def remove_track_from_likes(self, user, track ):
        """ Remove track to users liked tracks."""
        raise NotImplementedError

    @abc.abstractmethod
    def get_all_liked_tracks(self, user):
        """ Returns all liked tracks of a specified user."""
        raise NotImplementedError
    
    @abc.abstractmethod
    def add_playlist_to_lists(self, user: User, playlist: PlayList):
        """ Returns all liked tracks of a specified user."""
        raise NotImplementedError

    @abc.abstractmethod
    def remove_playlist_from_lists(self, user: User, playlist: PlayList):
        """ Returns all liked tracks of a specified user."""
        raise NotImplementedError

    @abc.abstractmethod
    def get_user_playlists(self, user):
        """ Returns all liked tracks of a specified user."""
        raise NotImplementedError

    @abc.abstractmethod
    def get_playlist_id(self):
        """ Returns all liked tracks of a specified user."""
        raise NotImplementedError

    @abc.abstractmethod
    def get_all_playlist(self): 
        """ Returns all liked tracks of a specified user."""
        raise NotImplementedError

    @abc.abstractmethod
    def get_playlist_by_id(self, id: int): 
        """ Returns the playlist specified by the id."""
        raise NotImplementedError

    @abc.abstractmethod
    def get_user_reviews(self, user: User): 
        """ Returns all reviews made by a user"""
        raise NotImplementedError
        
    @abc.abstractmethod
    def get_visible_playlists(self): 
        """ Returns all visible playlists"""
        raise NotImplementedError
    
    @abc.abstractmethod
    def add_track_to_playlist(self, track: Track, playlist: PlayList):
        """Returns adds track to a playlist."""
        raise NotImplementedError
    
    @abc.abstractmethod
    def remove_track_from_playlist(self, track: Track, playlist: PlayList):
        """ removes a track from playlist."""
        raise NotImplementedError
