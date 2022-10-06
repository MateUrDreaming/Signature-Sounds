from datetime import date
from typing import List

from sqlalchemy import desc, asc
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from sqlalchemy.orm import scoped_session

import os
from pathlib import Path


from music.domainmodel.artist import Artist
from music.domainmodel.playlist import PlayList
from music.domainmodel.track import Track
from music.domainmodel.genre import Genre
from music.domainmodel.review import Review
from music.domainmodel.album import Album
from music.domainmodel.user import User

from music.adapters.repository import  AbstractRepository
from music.adapters.csvdatareader import TrackCSVReader


class SessionContextManager:
    def __init__(self, session_factory):
        self.__session_factory = session_factory
        self.__session = scoped_session(self.__session_factory)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    @property
    def session(self):
        return self.__session

    def commit(self):
        self.__session.commit()

    def rollback(self):
        self.__session.rollback()

    def reset_session(self):
        # this method can be used e.g. to allow Flask to start a new session for each http request,
        # via the 'before_request' callback
        self.close_current_session()
        self.__session = scoped_session(self.__session_factory)

    def close_current_session(self):
        if not self.__session is None:
            self.__session.close()

class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session_factory):
        self._session_cm = SessionContextManager(session_factory)

    def close_session(self):
        self._session_cm.close_current_session()

    def reset_session(self):
        self._session_cm.reset_session()

    def add_user(self, user: User):
        pass

    def get_user(self, user_name) -> User:
        pass

    def get_number_of_users(self) -> int:
        pass

    def add_track(self, track: Track):
        with self._session_cm as scm:
            scm.session.merge(track)
            scm.commit()
    
    def get_track(self, id: int) -> Track:
        pass
    
    def get_tracks_by_artist(self, target_artist: Artist) -> List[Track]:
        pass
    
    def get_number_of_tracks(self) -> int:
        pass

    def get_all_track_ids(self): 
        pass

    def get_tracks_by_id(self, id_list):
        pass
    
    def get_track_ids_for_titles(self, key: str):
        pass

    def get_track_ids_for_artist(self, artist_name: str):
        pass
    
    def get_track_ids_for_genre(self, genre_name: str):
        pass
    
    def get_track_ids_for_album(self, album_name: str):
        pass

    def get_tracks_by_genre(self, target_genre: Genre) -> List[Track]:
        pass
    
    def get_tracks_by_album(self, target_album: Album) -> List[Track]:
        pass

    def add_genre(self, genre: Genre):
        with self._session_cm as scm:
            scm.session.add(genre)
            scm.commit()
    
    def get_genres(self) -> List[Genre]:
        pass
    
    def add_artist(self, artist: Artist):
        with self._session_cm as scm:
            scm.session.add(artist)
            scm.commit()
    
    def get_artists(self) -> List[Artist]:
        pass
    
    def add_album(self, album: Album):
        with self._session_cm as scm:
            scm.session.add(album)
            scm.commit()
    
    def get_albums(self) -> List[Album]:
        pass
    
    def get_tracks(self) -> List[Track]:
        pass
    
    def add_review(self, track, review):
        pass

    def get_reviews(self, track):
        pass
        
    def add_track_to_likes(self, user: User, track: Track): 
        pass
    
    def remove_track_from_likes(self, user: User, track: Track): 
        pass

    def get_all_reviews(self): 
        pass
    
    def get_all_liked_tracks(self, user):
        pass

    def add_playlist_to_lists(self, user: User, playlist: PlayList): 
        pass
    
    def remove_playlist_from_lists(self, user, playlist: PlayList): 
        pass
    
    def get_user_playlists(self, user):
        pass

    def get_playlist_id(self):
        pass
    
    def get_all_playlist(self): 
        pass
    
    def get_playlist_by_id(self, id: int): 
        pass
    
    def get_user_reviews(self, user): 
        pass
    
    def get_visible_playlists(self): 
        pass

def populate_two(data_path: Path, repo: SqlAlchemyRepository, database_mode=False):
    """ Populates the given repository using data at the given path. """
    dirname = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    albums_file_name = os.path.join(dirname, 'adapters/data/raw_albums_excerpt.csv')
    tracks_file_name = os.path.join(dirname, 'adapters/data/raw_tracks_excerpt.csv')
    reader = TrackCSVReader(albums_file_name, tracks_file_name, database_mode)
    reader.read_csv_files()

    for artist in reader.dataset_of_artists:
        repo.add_artist(artist)

    for genre in reader.dataset_of_genres:
        repo.add_genre(genre)
    
    for album in reader.dataset_of_albums:
        repo.add_album(album)
    
    for track in reader.dataset_of_tracks:
        repo.add_track(track)